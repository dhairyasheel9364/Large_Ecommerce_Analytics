import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------------
st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="🛒",
    layout="wide"
)

# ------------------------------------------------------------
# DASHBOARD HEADER
# ------------------------------------------------------------
st.title("🛒 E-Commerce Product & Conversion Analytics")

st.markdown(
    "**October 2019** | E-Commerce Behavior Dataset"
)

st.caption(
    "Interactive analytics dashboard powered by Apache Spark and Streamlit"
)

# ------------------------------------------------------------
# DATA PATHS
# ------------------------------------------------------------
FUNNEL_FILE = "/app/data/curated/daily_funnel.parquet"
BRAND_FILE = "/app/data/curated/brand_metrics.parquet"
HOURLY_FILE = "/app/data/curated/hourly_dynamics.parquet"

# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------
@st.cache_data
def load_data():
    required_files = [FUNNEL_FILE, BRAND_FILE, HOURLY_FILE]
    if not all(os.path.exists(f) for f in required_files):
        return None, None, None

    funnel = pd.read_parquet(FUNNEL_FILE)
    brand = pd.read_parquet(BRAND_FILE)
    hourly = pd.read_parquet(HOURLY_FILE)
    return funnel, brand, hourly

funnel_df, brand_df, hourly_df = load_data()

# ------------------------------------------------------------
# HANDLE MISSING DATA
# ------------------------------------------------------------
if funnel_df is None:
    st.warning("Processed Parquet data was not detected. Please run the PySpark ETL job first.")
    st.stop()

# ------------------------------------------------------------
# SIDEBAR FILTER
# ------------------------------------------------------------
st.sidebar.header("Dashboard Filters")

categories = sorted(
    funnel_df["main_category"]
    .dropna()
    .unique()
    .tolist()
)

selected_cat = st.sidebar.selectbox(
    "Product Category",
    ["All Categories"] + categories
)

if selected_cat == "All Categories":
    df_f = funnel_df
else:
    df_f = funnel_df[
        funnel_df["main_category"] == selected_cat
    ]

st.sidebar.caption(
    "The category filter affects KPI, funnel, and brand metrics."
)

# ------------------------------------------------------------
# HEADLINE METRICS (here is KPI)
# ------------------------------------------------------------
total_views = int(df_f["views"].sum())
total_carts = int(df_f["carts"].sum())
total_buys = int(df_f["purchases"].sum())
total_gmv = float(df_f["total_revenue"].sum())

# Purchase events divided by product view events.
purchase_rate = (
    total_buys / total_views * 100
    if total_views > 0
    else 0
)

# Purchase events divided by add-to-cart events.
cart_to_purchase_rate = (
    total_buys / total_carts * 100
    if total_carts > 0
    else 0
)

# Average revenue generated per purchase event.
avg_revenue_per_purchase = (
    total_gmv / total_buys
    if total_buys > 0
    else 0
)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Product Views",
    f"{total_views:,}"
)

c2.metric(
    "Add-to-Cart Events",
    f"{total_carts:,}"
)

c3.metric(
    "Purchase Events",
    f"{total_buys:,}"
)

c4.metric(
    "Purchase Rate",
    f"{purchase_rate:.2f}%"
)

c5.metric(
    "Avg Revenue / Purchase",
    f"${avg_revenue_per_purchase:,.2f}"
)

st.markdown("---")

with st.expander("ℹ️ Metric Definitions & Methodology"):

    st.markdown("""
    **Purchase Rate** = Purchase events ÷ Product view events

    **Cart-to-Purchase Rate** = Purchase events ÷ Add-to-cart events

    **Avg Revenue / Purchase** = GMV ÷ Purchase events

    **GMV** = Sum of product prices associated with purchase events

    **Data scope:** October 2019

    **Processing:** Records with non-positive prices are excluded from the
    analytics. Missing brands and category codes are handled during the
    Spark ETL process.

    **Important:** The source dataset does not provide a conventional order ID,
    so purchase-event metrics should not be interpreted as unique orders or
    unique-customer conversion rates.
    """)


# ------------------------------------------------------------
# VISUALIZATIONS
# ------------------------------------------------------------
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Conversion Funnel")
    fig_funnel = go.Figure(
        go.Funnel(
    y=[
        "Product Views",
        "Add-to-Cart Events",
        "Purchase Events"
    ],
    x=[
        total_views,
        total_carts,
        total_buys
    ],
    textinfo="value+percent initial"
)
    )
    fig_funnel.update_layout(margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_funnel, use_container_width=True)

with col_right:
    st.subheader("Hourly Traffic Dynamics")

    hourly_plot = hourly_df.copy()

    hourly_plot["hour"] = pd.to_numeric(
        hourly_plot["hour"],
        errors="coerce"
    )

    hourly_plot = hourly_plot.dropna(
        subset=["hour"]
    )

    hourly_plot = hourly_plot.sort_values(
        "hour"
    )

    # Create a cleaner hourly traffic visualization.
    fig_hourly = px.line(
        hourly_plot,
        x="hour",
        y="event_count",
        color="event_type",
        markers=True,
        labels={
            "hour": "Hour of Day (UTC)",
            "event_count": "Number of Events",
            "event_type": "Event Type"
        }
    )

    fig_hourly.update_xaxes(
        dtick=1,
        tickmode="linear"
    )

    fig_hourly.update_yaxes(
        separatethousands=True
    )

    fig_hourly.update_layout(
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),
        legend_title_text="Event Type",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_hourly,
        use_container_width=True
    )

# ------------------------------------------------------------
# CATEGORY PERFORMANCE
# ------------------------------------------------------------
st.subheader("Category Performance")

category_summary = (
    df_f
    .groupby("main_category", as_index=False)
    .agg(
        views=("views", "sum"),
        purchases=("purchases", "sum"),
        gmv=("total_revenue", "sum")
    )
)

# Calculate purchase rate for each category.
category_summary["purchase_rate"] = (
    category_summary["purchases"]
    / category_summary["views"]
    * 100
).fillna(0)

# Rank categories by GMV.
category_summary = (
    category_summary
    .sort_values(
        "gmv",
        ascending=False
    )
)

st.dataframe(
    category_summary[
        [
            "main_category",
            "views",
            "purchases",
            "purchase_rate",
            "gmv"
        ]
    ],
    use_container_width=True,
    hide_index=True,
    column_config={

        "main_category": "Category",

        "views": st.column_config.NumberColumn(
            "Views",
            format="%d"
        ),

        "purchases": st.column_config.NumberColumn(
            "Purchases",
            format="%d"
        ),

        "purchase_rate": st.column_config.NumberColumn(
            "Purchase Rate",
            format="%.2f%%"
        ),

        "gmv": st.column_config.NumberColumn(
            "GMV ($)",
            format="$%.2f"
        )
    }
)

# ------------------------------------------------------------
# REVENUE & BRANDS TABLE
# ------------------------------------------------------------
st.subheader("Revenue Summary")

revenue_col1, revenue_col2, revenue_col3 = st.columns(3)

revenue_col1.metric(
    "Total GMV",
    f"${total_gmv:,.2f}"
)

revenue_col2.metric(
    "Avg Revenue / Purchase",
    f"${avg_revenue_per_purchase:,.2f}"
)

revenue_col3.metric(
    "Cart-to-Purchase Rate",
    f"{cart_to_purchase_rate:.2f}%"
)

st.subheader("Top Revenue-Generating Brands")
df_b = (
    brand_df
    if selected_cat == "All Categories"
    else brand_df[
        brand_df["main_category"] == selected_cat
    ]
)
# Calculate brand-level purchase rate.
top_brands = df_b.copy()

top_brands["purchase_rate"] = (
    top_brands["total_purchases"]
    / top_brands["total_views"]
    * 100
).fillna(0)

# Keep the top 10 brands by GMV.
top_brands = (
    top_brands
    .sort_values(
        by="gmv",
        ascending=False
    )
    .head(10)
)

st.dataframe(
    top_brands[
        [
            "brand",
            "main_category",
            "total_views",
            "total_purchases",
            "purchase_rate",
            "gmv"
        ]
    ],
    use_container_width=True,
    hide_index=True,
    column_config={

        "brand": "Brand",

        "main_category": "Category",

        "total_views": st.column_config.NumberColumn(
            "Views",
            format="%d"
        ),

        "total_purchases": st.column_config.NumberColumn(
            "Purchases",
            format="%d"
        ),

        "purchase_rate": st.column_config.NumberColumn(
            "Purchase Rate",
            format="%.2f%%"
        ),

        "gmv": st.column_config.NumberColumn(
            "GMV ($)",
            format="$%.2f"
        )
    }
)

st.markdown("---")
st.caption("Data source: E-Commerce Behavior Data | Processing: Apache Spark | Dashboard: Streamlit")