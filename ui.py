import streamlit as st
import pandas as pd
import json

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="n8n Workflow Popularity Dashboard",
    layout="wide"
)

st.title("📊 n8n Workflow Popularity Dashboard")
st.caption(
    "Professional analytics dashboard to identify popular n8n workflows "
    "across platforms and countries."
)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    with open("workflows.json", "r", encoding="utf-8") as f:
        return json.load(f)

try:
    data = load_data()
except Exception as e:
    st.error(f"❌ Could not load workflows.json: {e}")
    st.stop()

df = pd.DataFrame(data)

# Expand popularity metrics
metrics_df = pd.json_normalize(df["popularity_metrics"])
df = df.drop(columns=["popularity_metrics"]).join(metrics_df)

# Choose main popularity metric automatically
numeric_cols = df.select_dtypes(include="number").columns.tolist()
MAIN_METRIC = numeric_cols[0] if numeric_cols else None

if MAIN_METRIC:
    df = df.sort_values(by=MAIN_METRIC, ascending=False)

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🔍 Filters")

platform = st.sidebar.selectbox(
    "Platform",
    ["All"] + sorted(df["platform"].unique())
)

country = st.sidebar.selectbox(
    "Country",
    ["All"] + sorted(df["country"].unique())
)

rows_limit = st.sidebar.slider(
    "Rows to display",
    min_value=5,
    max_value=100,
    value=30
)

filtered_df = df.copy()

if platform != "All":
    filtered_df = filtered_df[filtered_df["platform"] == platform]

if country != "All":
    filtered_df = filtered_df[filtered_df["country"] == country]

# ---------------- KPI CARDS ----------------
st.markdown("### 📌 Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Workflows", len(filtered_df))
c2.metric("Platforms", filtered_df["platform"].nunique())
c3.metric("Countries", filtered_df["country"].nunique())
c4.metric(
    "Top Platform",
    filtered_df["platform"].value_counts().idxmax()
    if not filtered_df.empty else "-"
)

st.divider()

# ---------------- TOP POPULAR WORKFLOWS ----------------
st.markdown("### ⭐ Top Popular Workflows")

top_workflows = filtered_df.head(5)

for i, row in top_workflows.iterrows():
    st.markdown(
        f"**{row['workflow']}**  \n"
        f"Platform: `{row['platform']}` | Country: `{row['country']}`  \n"
        f"[🔗 Open Link]({row['url']})"
    )

st.divider()

# ---------------- FULL WORKFLOW TABLE ----------------
st.markdown("### 📋 Popular Workflows List")

search = st.text_input("🔎 Search workflow by name")

table_df = filtered_df.copy()

if search:
    table_df = table_df[
        table_df["workflow"].str.contains(search, case=False, na=False)
    ]

table_df = table_df.head(rows_limit)

st.dataframe(table_df, use_container_width=True)

st.divider()

# ---------------- POPULARITY COMPARISON ----------------


# ---------------- INSIGHTS SECTION ----------------
st.markdown("### 🧠 Key Insights")

if not filtered_df.empty and MAIN_METRIC:
    st.info(
        f"• **{filtered_df.iloc[0]['workflow']}** is the most popular workflow "
        f"based on **{MAIN_METRIC}**.\n\n"
        f"• **{filtered_df['platform'].value_counts().idxmax()}** is the most active platform.\n\n"
        f"• Highest engagement comes from **{filtered_df['country'].value_counts().idxmax()}**."
    )
