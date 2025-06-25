import streamlit as st
import pandas as pd
import plotly.express as px
import io

# Set Streamlit page config
st.set_page_config(page_title="📊 Sales Performance Dashboard", layout="wide")
st.title("📈 Sales Performance Dashboard")

# Sidebar - Upload or Use Default Dataset
st.sidebar.header("📂 Select Dataset")
dataset_option = st.sidebar.radio("Choose Dataset:", ("Default Superstore Data", "Upload Your Own"))

# Load Default or Uploaded Data
def load_default_data():
    return pd.read_excel("sales_data.xlsx", engine='openpyxl')

def load_user_data(uploaded_file):
    try:
        if uploaded_file.name.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            return pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            st.warning("Unsupported file type. Please upload .csv or .xlsx")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return pd.DataFrame()

if dataset_option == "Upload Your Own":
    uploaded_file = st.sidebar.file_uploader("Upload your dataset (.csv or .xlsx)", type=["csv", "xlsx"])
    if uploaded_file:
        df = load_user_data(uploaded_file)
    else:
        df = pd.DataFrame()
else:
    df = load_default_data()

# If data is loaded
if not df.empty:

    st.sidebar.header("🎯 Filter Your Data")

    # Filters
    if 'Region' in df.columns:
        regions = st.sidebar.multiselect("Region", sorted(df['Region'].dropna().unique()))
        if regions:
            df = df[df['Region'].isin(regions)]

    if 'Category' in df.columns:
        categories = st.sidebar.multiselect("Category", sorted(df['Category'].dropna().unique()))
        if categories:
            df = df[df['Category'].isin(categories)]

    if 'Segment' in df.columns:
        segments = st.sidebar.multiselect("Segment", sorted(df['Segment'].dropna().unique()))
        if segments:
            df = df[df['Segment'].isin(segments)]

    if 'Order Date' in df.columns:
        df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
        min_date = df['Order Date'].min()
        max_date = df['Order Date'].max()
        date_range = st.sidebar.date_input("Order Date Range", [min_date, max_date])
        if len(date_range) == 2:
            start_date, end_date = date_range
            df = df[(df['Order Date'] >= pd.to_datetime(start_date)) & (df['Order Date'] <= pd.to_datetime(end_date))]

    # Sorting
    st.sidebar.header("⬇️ Sort Data")
    sort_columns = st.sidebar.multiselect("Sort By", df.columns.tolist())
    sort_order = st.sidebar.radio("Sort Order", ["Ascending", "Descending"])
    if sort_columns:
        df = df.sort_values(by=sort_columns, ascending=(sort_order == "Ascending"))

    # Show Data
    st.subheader("📄 Filtered Data Table")
    st.dataframe(df, use_container_width=True)

    # Visualizations
    st.markdown("---")
    st.subheader("📊 Data Visualizations")

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col5, col6 = st.columns(2)

    with col1:
        if 'Category' in df.columns and 'Sales' in df.columns:
            fig1 = px.bar(df.groupby('Category')['Sales'].sum().reset_index(), x='Category', y='Sales',
                         title='Sales by Category', color='Category')
            st.plotly_chart(fig1, use_container_width=True)

    with col2:
        if 'Order Date' in df.columns and 'Sales' in df.columns:
            fig2 = px.line(df.groupby('Order Date')['Sales'].sum().reset_index(),
                          x='Order Date', y='Sales', title='Sales Over Time')
            st.plotly_chart(fig2, use_container_width=True)

    with col3:
        if 'Region' in df.columns and 'Sales' in df.columns:
            fig3 = px.pie(df, values='Sales', names='Region', title='Sales by Region')
            st.plotly_chart(fig3, use_container_width=True)

    with col4:
        if 'Sub-Category' in df.columns and 'Profit' in df.columns:
            fig4 = px.bar(df.groupby('Sub-Category')['Profit'].sum().reset_index(),
                         x='Sub-Category', y='Profit', title='Profit by Sub-Category', color='Profit')
            st.plotly_chart(fig4, use_container_width=True)

    with col5:
        if 'Ship Mode' in df.columns and 'Sales' in df.columns:
            fig5 = px.pie(df, values='Sales', names='Ship Mode', title='Sales by Ship Mode')
            st.plotly_chart(fig5, use_container_width=True)

    with col6:
        if 'Discount' in df.columns and 'Sales' in df.columns:
            fig6 = px.scatter(df, x='Discount', y='Sales', size=df['Profit'].abs(), color='Category',
                  title='Sales vs Discount with Absolute Profit Size')

            st.plotly_chart(fig6, use_container_width=True)

    # Download Filtered Data
    st.subheader("📥 Download Filtered Data")
    @st.cache_data
    def convert_df(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        processed_data = output.getvalue()
        return processed_data

    data = convert_df(df)
    st.download_button("⬇️ Download Excel File", data, "filtered_data.xlsx")

else:
    st.warning("Please upload a dataset or select a valid file.")
