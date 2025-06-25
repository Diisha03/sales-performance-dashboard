import pandas as pd
import streamlit as st
import plotly.express as px
import io  # for download

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(page_title="📊 Sales Dashboard", layout="wide")

# ---------------------- LOAD DATA ----------------------
df = pd.read_excel("sales_data.xlsx")
df.columns = [col.strip() for col in df.columns]
df["Order Date"] = pd.to_datetime(df["Order Date"])

# ---------------------- SIDEBAR ----------------------
with st.sidebar:
    st.title("🔍 Filter Sales Data")

    region = st.multiselect("📍 Select Region", df["Region"].unique(), default=df["Region"].unique())
    category = st.multiselect("🧩 Select Category", df["Category"].unique(), default=df["Category"].unique())

    min_date = df["Order Date"].min()
    max_date = df["Order Date"].max()

    st.markdown("## 🗓️ Select Date Range")
    start_date, end_date = st.date_input(
        "Order Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

# ---------------------- DATA FILTERING ----------------------
df_filtered = df[
    (df["Region"].isin(region)) &
    (df["Category"].isin(category)) &
    (df["Order Date"] >= pd.to_datetime(start_date)) &
    (df["Order Date"] <= pd.to_datetime(end_date))
]

# ---------------------- METRICS ----------------------
total_sales = round(df_filtered["Sales"].sum(), 2)
total_profit = round(df_filtered["Profit"].sum(), 2)
total_quantity = int(df_filtered["Quantity"].sum())
profit_margin = round((total_profit / total_sales) * 100, 2) if total_sales else 0

# ---------------------- CUSTOM STYLES ----------------------
st.markdown("""
    <style>
    .kpi-card {
        background-color: #f0f9ff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
        text-align: center;
        transition: transform 0.2s;
    }
    .kpi-card:hover {
        transform: scale(1.02);
    }
    .kpi-title {
        font-size: 18px;
        color: #555;
    }
    .kpi-value {
        font-size: 26px;
        font-weight: bold;
        color: #007bff;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------- DASHBOARD TITLE ----------------------
st.markdown("<h1 style='text-align: center; color: #1f77b4;'>✨ Real-Time Sales Performance Dashboard</h1>", unsafe_allow_html=True)
st.markdown("---")

# ---------------------- KPI CARDS ----------------------
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-title'>💰 Total Sales</div>
            <div class='kpi-value'>₹{total_sales:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-title'>📈 Total Profit</div>
            <div class='kpi-value'>₹{total_profit:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-title'>📦 Total Quantity</div>
            <div class='kpi-value'>{total_quantity}</div>
        </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-title'>📊 Profit Margin</div>
            <div class='kpi-value'>{profit_margin}%</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("## ")

# ---------------------- CHART 1: Monthly Sales Trend ----------------------
df_filtered["Month"] = df_filtered["Order Date"].dt.to_period("M").dt.to_timestamp()
monthly_sales = df_filtered.groupby("Month")["Sales"].sum().reset_index()

fig_line = px.line(
    monthly_sales,
    x="Month", y="Sales",
    title="📅 Monthly Sales Trend",
    markers=True,
    template="plotly_white",
    color_discrete_sequence=["#1f77b4"]
)
fig_line.update_layout(title_x=0.4)

# ---------------------- CHART 2: Top 10 Products ----------------------
top_products = df_filtered.groupby("Product Name")["Sales"].sum().nlargest(10).sort_values()
fig_bar = px.bar(
    x=top_products.values,
    y=top_products.index,
    orientation="h",
    title="🏆 Top 10 Products by Sales",
    template="plotly_white",
    color_discrete_sequence=["#ff7f0e"]
)
fig_bar.update_layout(title_x=0.4)

# ---------------------- DISPLAY CHARTS ----------------------
left, right = st.columns(2)
with left:
    st.plotly_chart(fig_line, use_container_width=True)
with right:
    st.plotly_chart(fig_bar, use_container_width=True)

# ---------------------- CHART 3: Category Pie Chart ----------------------
category_sales = df_filtered.groupby("Category")["Sales"].sum().reset_index()
fig_pie = px.pie(
    category_sales,
    names="Category",
    values="Sales",
    title="🧩 Category-Wise Sales Share",
    color_discrete_sequence=px.colors.sequential.RdBu
)
fig_pie.update_traces(textposition='inside', textinfo='percent+label')
fig_pie.update_layout(title_x=0.4)

st.plotly_chart(fig_pie, use_container_width=True)

# ---------------------- DOWNLOAD EXCEL BUTTON ----------------------
st.markdown("### 📥 Download Filtered Data")
@st.cache_data
def convert_df(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Filtered Data')
    return output.getvalue()

excel_data = convert_df(df_filtered)

st.download_button(
    label="Download as Excel",
    data=excel_data,
    file_name="filtered_sales_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ---------------------- FOOTER ----------------------
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>🚀 Built with ❤️ using Streamlit | Data: Superstore Sales</p>", unsafe_allow_html=True)
