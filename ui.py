import streamlit as st
import pandas as pd
import json

# Page config
st.set_page_config(
    page_title="n8n Workflow Popularity Dashboard",
    layout="wide"
)

st.title("📊 n8n Workflow Popularity Dashboard")
st.markdown(
    "Analyze popular **n8n workflows** across YouTube, Google Trends, and Community Forum."
)

# Load JSON data
@st.cache_data
def load_data():
    with open("workflows.json", "r", encoding="utf-8") as f:
        return json.load(f)

try:
    data = load_data()
except Exception as e:
    st.error(f"❌ Failed to load workflows.json: {e}")
    st.stop()

if not data:
    st.warning("⚠️ No data available. Please run fetch_data.py locally first.")
    st.stop()

df = pd.DataFrame(data)

# Sidebar filters
st.sidebar.header("🔍 Filters")

platforms = ["All"] + sorted(df["platform"].unique().tolist())
countries = ["All"] + sorted(df["country"].unique().tolist())

platform = st.sidebar.selectbox("Select Platform", platforms)
country = st.sidebar.selectbox("Select Country", countries)

limit = st.sidebar.slider(
    "Number of workflows to display",
    min_value=10,
    max_value=100,
    value=30
)

# Apply filters
filtered_df = df.copy()

if platform != "All":
    filtered_df = filtered_df[filtered_df["platform"] == platform]

if country != "All":
    filtered_df = filtered_df[filtered_df["country"] == country]

# Expand popularity metrics
metrics_df = pd.json_normalize(filtered_df["popularity_metrics"])
filtered_df = filtered_df.drop(columns=["popularity_metrics"]).join(metrics_df)

# Sort by any available metric
numeric_cols = filtered_df.select_dtypes(include="number").columns.tolist()
sort_col = numeric_cols[0] if numeric_cols else None

if sort_col:
    filtered_df = filtered_df.sort_values(by=sort_col, ascending=False)

filtered_df = filtered_df.head(limit)

# Display table
st.subheader(f"📌 Showing {len(filtered_df)} workflows")
st.dataframe(filtered_df, use_container_width=True)

# Popularity comparison chart
if numeric_cols:
    st.subheader("📈 Popularity Comparison")

    metric = st.selectbox("Choose metric", numeric_cols)

    chart_df = (
        filtered_df[["workflow", metric]]
        .dropna()
        .sort_values(by=metric, ascending=False)
        .head(10)
        .set_index("workflow")
    )

    st.bar_chart(chart_df)
