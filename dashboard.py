import streamlit as st
import pandas as pd
import plotly.express as px
import io
from datetime import datetime

st.set_page_config(page_title="Sales Performance Dashboard", layout="wide")
st.title("📊 Sales Performance Dashboard")

# Sidebar - Dataset Selection
st.sidebar.header("📁 Select Dataset")
dataset_option = st.sidebar.radio("Choose Dataset:", ("Default Superstore Data", "Upload Your Own"))

if dataset_option == "Upload Your Own":
    uploaded_file = st.sidebar.file_uploader("Upload your Excel file", type=["xlsx"])
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    else:
        st.warning("Please upload a valid Excel file to proceed.")
        st.stop()
else:
    df = pd.read_excel("sales_data.xlsx", engine="openpyxl")

# --- Sidebar Filters ---
st.sidebar.header("🎯 Filter Sales Data")
region = st.sidebar.multiselect("Select Region", options=df["Region"].unique(), default=df["Region"].unique())
category = st.sidebar.multiselect("Select Category", options=df["Category"].unique(), default=df["Category"].unique())

# Convert Order Date to datetime format
df["Order Date"] = pd.to_datetime(df["Order Date"])
min_date = df["Order Date"].min()
max_date = df["Order Date"].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])

# --- Filter Data ---
df_filtered = df[
    (df["Region"].isin(region)) &
    (df["Category"].isin(category)) &
    (df["Order Date"] >= pd.to_datetime(date_range[0])) &
    (df["Order Date"] <= pd.to_datetime(date_range[1]))
]

# --- Main Dashboard KPIs ---
total_sales = int(df_filtered["Sales"].sum())
total_profit = int(df_filtered["Profit"].sum())
total_orders = df_filtered["Order ID"].nunique()

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Sales", f"${total_sales:,}")
col2.metric("📦 Total Orders", f"{total_orders:,}")
col3.metric("📈 Total Profit", f"${total_profit:,}")

st.markdown("---")

# --- Visualizations ---

# Sales by Region
fig_region = px.bar(df_filtered.groupby("Region")["Sales"].sum().reset_index(),
                    x="Region", y="Sales", color="Region",
                    title="Sales by Region")
st.plotly_chart(fig_region, use_container_width=True)

# Sales Over Time
fig_time = px.line(df_filtered.groupby("Order Date")["Sales"].sum().reset_index(),
                   x="Order Date", y="Sales",
                   title="Sales Over Time")
st.plotly_chart(fig_time, use_container_width=True)

# Category-wise Sales
fig_category = px.pie(df_filtered, values="Sales", names="Category",
                      title="Category-wise Sales Distribution")
st.plotly_chart(fig_category, use_container_width=True)

# --- Download Filtered Data ---

@st.cache_data
def convert_df(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    return processed_data

data = convert_df(df_filtered)

st.download_button(
    label="📥 Download Filtered Data",
    data=data,
    file_name="filtered_sales_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# --- Display Filtered Table ---
st.markdown("---")
st.subheader("📄 Filtered Sales Data Table")
st.dataframe(df_filtered, use_container_width=True)
