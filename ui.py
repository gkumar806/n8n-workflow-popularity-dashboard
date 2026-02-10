import streamlit as st
import requests
import pandas as pd

# Page config
st.set_page_config(
    page_title="n8n Workflow Popularity Dashboard",
    layout="wide"
)

st.title("📊 n8n Workflow Popularity Dashboard")
st.markdown(
    "Analyze popular **n8n workflows** across **YouTube, Google Trends, and Community Forum**."
)

# Sidebar filters
st.sidebar.header("🔍 Filters")

platform = st.sidebar.selectbox(
    "Select Platform",
    ["All", "YouTube", "Google", "Discourse"]
)

country = st.sidebar.selectbox(
    "Select Country",
    ["All", "IN", "US"]
)

limit = st.sidebar.slider(
    "Number of workflows to display",
    min_value=10,
    max_value=100,
    value=20
)

# API URL
API_URL = st.secrets.get(
    "API_URL",
    "http://127.0.0.1:8000/workflows"
)

params = {}
if platform != "All":
    params["platform"] = platform
if country != "All":
    params["country"] = country
params["limit"] = limit

# Fetch data
try:
    response = requests.get(API_URL, params=params)
    data = response.json()

    if "workflows" not in data or len(data["workflows"]) == 0:
        st.warning("⚠️ No data found. Run fetch_data.py first.")
    else:
        workflows = data["workflows"]

        df = pd.DataFrame(workflows)

        # Expand popularity metrics
        metrics_df = pd.json_normalize(df["popularity_metrics"])
        df = df.drop(columns=["popularity_metrics"]).join(metrics_df)

        st.subheader(f"📌 Showing {len(df)} workflows")

        st.dataframe(df, use_container_width=True)

        # Chart section
        numeric_cols = df.select_dtypes(include="number").columns.tolist()

        if numeric_cols:
            st.subheader("📈 Popularity Comparison")
            metric = st.selectbox("Choose metric", numeric_cols)

            chart_df = df[["workflow", metric]].dropna().sort_values(
                by=metric, ascending=False
            ).head(10)

            st.bar_chart(chart_df.set_index("workflow"))

except Exception as e:
    st.error(f"❌ Failed to connect to API: {e}")
