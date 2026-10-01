from pyspark import StorageLevel
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    to_timestamp,
    date_format,
    when,
    count,
    sum as spark_sum,
    round as spark_round,
    split
)
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    LongType
)


def main():
    print(">>> Initializing Spark Session...")

    spark = (
        SparkSession.builder
        .appName("ECommerceProductAnalytics")

        # Prevent very large collect() results from overwhelming the driver.
        .config("spark.driver.maxResultSize", "1g")

        # 12 partitions is a reasonable starting point for 6 Docker CPUs.
        .config("spark.sql.shuffle.partitions", "12")

        # Provides parallelism without creating excessive task overhead.
        .config("spark.default.parallelism", "12")

        # Leaves a reasonable portion of Spark memory for execution/storage.
        .config("spark.memory.fraction", "0.7")
        .config("spark.memory.storageFraction", "0.3")

        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    raw_path = "/app/data/raw/2019-Oct.csv"

    print(f">>> Reading raw CSV from {raw_path}...")

    # Explicit schema avoids Spark scanning the entire CSV to infer data types.
    raw_schema = StructType([
        StructField("event_time", StringType(), True),
        StructField("event_type", StringType(), True),
        StructField("product_id", LongType(), True),
        StructField("category_id", LongType(), True),
        StructField("category_code", StringType(), True),
        StructField("brand", StringType(), True),
        StructField("price", DoubleType(), True),
        StructField("user_id", LongType(), True),
        StructField("user_session", StringType(), True)
    ])

    raw_df = (
        spark.read
        .option("header", "true")
        .schema(raw_schema)
        .csv(raw_path)
    )

    print(">>> Cleaning data and extracting dimensions...")

    cleaned_df = (
        raw_df

        # Remove invalid/non-positive prices before calculations.
        .filter(col("price") > 0)

        # Replace missing dimensions so records remain usable.
        .fillna({
            "brand": "Unknown",
            "category_code": "unknown.unknown"
        })

        # Convert event_time into a Spark timestamp.
        .withColumn(
            "timestamp",
            to_timestamp(
                col("event_time"),
                "yyyy-MM-dd HH:mm:ss 'UTC'"
            )
        )

        # Extract date for daily analysis.
        .withColumn(
            "date",
            date_format(col("timestamp"), "yyyy-MM-dd")
        )

        # Extract hour for traffic analysis.
        .withColumn(
            "hour",
            date_format(col("timestamp"), "HH")
        )

        # Extract the top-level category.
        # Example: electronics.smartphone -> electronics
        .withColumn(
            "main_category",
            split(col("category_code"), "\\.").getItem(0)
        )

        # Keep only columns required by our three analytical tables.
        # This substantially reduces the amount of data Spark must carry
        # through the aggregations and cache.
        .select(
            "date",
            "hour",
            "main_category",
            "brand",
            "event_type",
            "price"
        )
    )

    # Cache the smaller, projected dataset instead of the original 9-column CSV.
    # MEMORY_AND_DISK allows cached partitions to spill to Spark's local disk
    # instead of requiring the entire dataset to fit in RAM.
    cleaned_df.persist(StorageLevel.MEMORY_AND_DISK)

    # ============================================================
    # 1. DAILY FUNNEL METRICS
    # ============================================================

    print(">>> Computing Daily Conversion Funnel...")

    funnel_df = (
        cleaned_df
        .groupBy("date", "main_category")
        .agg(
            count(
                when(col("event_type") == "view", 1)
            ).alias("views"),

            count(
                when(col("event_type") == "cart", 1)
            ).alias("carts"),

            count(
                when(col("event_type") == "purchase", 1)
            ).alias("purchases"),

            spark_round(
                spark_sum(
                    when(
                        col("event_type") == "purchase",
                        col("price")
                    )
                ),
                2
            ).alias("total_revenue")
        )
    )

    funnel_df.write \
        .mode("overwrite") \
        .parquet("/app/data/curated/daily_funnel.parquet")

    # ============================================================
    # 2. BRAND PERFORMANCE
    # ============================================================

    print(">>> Computing Brand Performance...")

    brand_df = (
        cleaned_df
        .filter(col("brand") != "Unknown")

        # Aggregate brand performance by main category.
        .groupBy("brand", "main_category")

        .agg(
            count(
                when(col("event_type") == "view", 1)
            ).alias("total_views"),

            count(
                when(col("event_type") == "purchase", 1)
            ).alias("total_purchases"),

            spark_round(
                spark_sum(
                    when(
                        col("event_type") == "purchase",
                        col("price")
                    )
                ),
                2
            ).alias("gmv")
        )

        # Remove extremely low-volume brands from the dashboard table.
        .filter(col("total_purchases") > 5)
    )

    brand_df.write \
        .mode("overwrite") \
        .parquet("/app/data/curated/brand_metrics.parquet")

    # ============================================================
    # 3. HOURLY TRAFFIC DYNAMICS
    # ============================================================

    print(">>> Computing Hourly Dynamics...")

    hourly_df = (
        cleaned_df
        .groupBy("hour", "event_type")
        .agg(
            count("*").alias("event_count")
        )
    )

    hourly_df.write \
        .mode("overwrite") \
        .parquet("/app/data/curated/hourly_dynamics.parquet")

    # Release the cached dataset before Spark shuts down.
    cleaned_df.unpersist()

    print(">>> PySpark ETL completed successfully!")
    print(">>> Parquet files written to /app/data/curated/")

    spark.stop()


if __name__ == "__main__":
    main()