import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="Myntra E-Commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 Myntra E-Commerce Analytics Dashboard")

# Load Dataset
df = pd.read_csv("Ecommerce.csv")

# Show Data
st.subheader("Dataset Preview")
st.dataframe(df.head())

# Basic KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Revenue", f"₹{df['revenue'].sum():,.0f}")

with col2:
    st.metric("Total Orders", len(df))

with col3:
    st.metric("Customers", df["customer_id"].nunique())

with col4:
    st.metric("Products", df["product_id"].nunique())