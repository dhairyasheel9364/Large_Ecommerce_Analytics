FROM apache/spark-py:v3.4.0

USER root

WORKDIR /app

# Create directories used by the ETL job.
RUN mkdir -p /app/data/raw /app/data/curated && \
    chmod -R 777 /app/data

# Copy the Spark ETL script into the image.
COPY etl_job.py .

# Spark driver gets 4 GB heap.
# Docker Compose limits the whole container to 5.5 GB.
CMD ["/opt/spark/bin/spark-submit", \
     "--master", "local[*]", \
     "--driver-memory", "4g", \
     "etl_job.py"]