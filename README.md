E-Commerce Product & Conversion Analytics



An end-to-end Interactive e-commerce analytics project built with PySpark, Python, Pandas, Plotly, Docker, and Streamlit.


The project processes large-scale e-commerce behavioral data, transforms raw event data into analytics-ready datasets using PySpark, and presents the results through an interactive web dashboard.



## Live Dashboard --->

 [Open the Live Streamlit Dashboard](https://large-ecommerce-analytics-proj.streamlit.app/)





📊 Project Overview


This project analyzes e-commerce user behavior across product views, cart events, and purchase events.

The goal is to demonstrate a complete analytics workflow:

*Raw Data → Distributed Processing → Curated Data → Interactive Dashboard*

The pipeline uses Apache Spark for large-scale processing while keeping the final dashboard lightweight by consuming only the aggregated Parquet datasets.



🎯 Business Questions

The dashboard is designed to answer questions such as:

1* How much product traffic is generated?

2* How many users/events progress from viewing to cart and purchase?

3* What is the purchase-event rate?

4* Which product categories generate the most GMV?

5* Which brands generate the most revenue?

6* How does customer activity change throughout the day?

7* How do category-level metrics compare?



---


🏗️ Architecture


```

&#x20;                Kaggle E-Commerce Dataset

&#x20;                        │

&#x20;                        │

&#x20;                        ▼

&#x20;                 Raw CSV Files

&#x20;                        │

&#x20;                        │

&#x20;                        ▼

&#x20;             ┌─────────────────────┐

&#x20;             │      Apache Spark   │

&#x20;             │                     │

&#x20;             │  Data Cleaning      │

&#x20;             │  Transformation     │

&#x20;             │  Aggregation        │

&#x20;             └──────────┬──────────┘

&#x20;                        │

&#x20;                        ▼

&#x20;                Curated Parquet

&#x20;                        │

&#x20;            ┌───────────┼───────────┐

&#x20;            │           │           │

&#x20;            ▼           ▼           ▼

&#x20;         Funnel       Brand      Hourly

&#x20;         Metrics      Metrics    Dynamics

&#x20;            │           │           │

&#x20;            └───────────┼───────────┘

&#x20;                        │

&#x20;                        ▼

&#x20;                 Streamlit Dashboard

&#x20;                        │

&#x20;                        ▼

&#x20;                   Interactive

&#x20;                    Analytics

```


---



⚙️ Data Engineering


The raw dataset contains millions of e-commerce behavioral events.


The PySpark ETL pipeline performs:


1. Explicit schema definition

2. Data cleaning

3. Positive-price filtering

4. Missing brand/category handling

5. Timestamp parsing

6. Date and hour extraction

7. Main-category extraction

8. Daily funnel aggregation

9. Brand-level performance aggregation

10. Hourly event aggregation

11. Parquet output generation


*Curated datasets



| Dataset                   | Purpose                                              |

| ------------------------- | ---------------------------------------------------- |

| `daily\_funnel.parquet`    | Views, carts, purchases, and GMV by date/category    |

| `brand\_metrics.parquet`   | Brand-level views, purchases, purchase rate, and GMV |

| `hourly\_dynamics.parquet` | Event activity by hour and event type                |



The raw CSV files are intentionally excluded from Git because of their large size.



---



\## 📈 Dashboard Features

*KPI Overview

The dashboard displays:


1* Product Views

2* Add-to-Cart Events

3* Purchase Events

4* Purchase Rate

5* Average Revenue per Purchase



### Conversion Funnel

The interactive funnel visualizes:



*Product Views → Add-to-Cart Events → Purchase Events



### Category Analysis

Users can filter the dashboard by product category and inspect:


* Views
* Purchases
* Purchase rate
* GMV



# Brand Performance

The dashboard displays the top brands by GMV along with:



* Views

* Purchases

* Purchase rate

* GMV



# Hourly Traffic Dynamics

An interactive Plotly visualization shows event activity throughout the day.

# Revenue Summary

The dashboard provides:

* Total GMV

* Average Revenue per Purchase

* Cart-to-Purchase Rate



---



📊 October 2019 Dataset Metrics


For the October 2019 processed dataset:


| Metric                     |           Value |

| -------------------------- | --------------: |

| Product Views              |      40,710,876 |

| Add-to-Cart Events         |         926,366 |

| Purchase Events            |         742,849 |

| Purchase Rate              |           1.82% |

| GMV                        | $229,957,502.27 |

| Average Revenue / Purchase |         $309.56 |

| Cart-to-Purchase Rate      |          80.19% |



---



The source dataset records behavioral events rather than conventional orders.



Therefore:



* Purchase events should not automatically be interpreted as unique orders.

* Purchase-event metrics should not be interpreted as unique-customer conversion rates.

* The current purchase rate is based on event counts.

* Average revenue per purchase is calculated from purchase events rather than an order-level identifier.

* The dashboard currently focuses on October 2019.

* Raw data is processed locally and is not stored in the Git repository.

These definitions are documented directly in the dashboard.



---



🛠️ Tech Stack



| Technology     | Purpose                                     |

| -------------- | ------------------------------------------- |

| Python         | Data processing and application development |

| Apache Spark   | Large-scale ETL                             |

| PySpark        | Spark-based data transformations            |

| Pandas         | Dashboard-side data handling                |

| PyArrow        | Parquet data access                         |

| Plotly         | Interactive visualizations                  |

| Streamlit      | Interactive dashboard                       |

| Docker         | Containerized execution                     |

| Docker Compose | Local multi-container orchestration         |

| WSL2           | Linux environment for Docker Desktop        |

| Git \& GitHub   | Version control and portfolio hosting       |






💻 Run Locally
 *Prerequisites

* Docker Desktop
* WSL2
* Git
* Kaggle dataset



# Start the project

Clone the repository:



```bash

git clone https://github.com/dhairyasheel9364/Large\_Ecommerce\_Analytics.git



cd Large\_Ecommerce\_Analytics

```

Place the raw dataset inside:


```text

data/raw/

```

The expected files are:

```text
2019-Oct.csv

2019-Nov.csv

```

Then start the pipeline:

```bash

docker compose up --build

```


The Spark container processes the raw data and writes the curated Parquet datasets.



The Streamlit dashboard is available at:



```text

http://localhost:8501

```



---



🔮 Future Improvements

Potential extensions include:


* Processing November 2019 data

* Adding customer-level behavioral analysis

* Adding category-specific hourly analysis

* Adding repeat-purchase analysis where appropriate identifiers permit

* Expanding time-series analytics

* Adding automated data-quality checks

* Adding additional business KPIs

* Improving dashboard interactions and drill-down capabilities



---


📚 Dataset
Source:

\[Kaggle Dataset](https://www.kaggle.com/datasets/mkechinov/ecommerce-behavior-data-from-multi-category-store)


The dataset contains behavioral events from an e-commerce platform, including product views, cart events, and purchases.

---


👤 Author

Dhairyasheel Wangdare


GitHub:

https://github.com/dhairyasheel9364



