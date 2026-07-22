from flask import Flask, render_template, request
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
import os

# ----------------------------
# Load Environment Variables
# ----------------------------
load_dotenv()

app = Flask(__name__)

# ----------------------------
# MySQL Connection
# ----------------------------
engine = create_engine(
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)

# ----------------------------
# Load Data
# ----------------------------
df = pd.read_sql("SELECT * FROM ecommerce_data", engine)

# Convert columns once
df["visit_date"] = pd.to_datetime(df["visit_date"], errors="coerce")
df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")

# Remove invalid rows
df = df.dropna(subset=["visit_date"])

# ----------------------------
# Home Page
# ----------------------------
@app.route("/")
def home():
    return render_template("home.html")


# ----------------------------
# Dashboard
# ----------------------------
@app.route("/dashboard")
def dashboard():

    filtered_df = df.copy()

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df["visit_date"] >= pd.to_datetime(start_date))
            &
            (filtered_df["visit_date"] <= pd.to_datetime(end_date))
        ]

    # ---------------- KPI ----------------

    total_revenue = round(filtered_df["revenue"].sum(), 2)

    total_customers = int(filtered_df["customer_id"].nunique())

    total_products = int(filtered_df["product_id"].nunique())

    total_orders = int(len(filtered_df))

    avg_rating = round(filtered_df["rating"].mean(), 2)

    avg_order_value = round(filtered_df["revenue"].mean(), 2)

    repeat_customers = int(
        filtered_df.groupby("customer_id")
        .size()
        .gt(1)
        .sum()
    )

    monthly_growth = 12.8

    # ---------------- Category Mapping ----------------

    category_names = {
        0: "Electronics",
        1: "Fashion",
        2: "Home & Kitchen",
        3: "Beauty",
        4: "Sports",
        5: "Books",
        6: "Grocery",
        7: "Toys"
    }

    category_df = (
        filtered_df.groupby("product_category")["revenue"]
        .sum()
        .reset_index()
    )

    category_df["product_category"] = (
        category_df["product_category"]
        .map(category_names)
        .fillna(category_df["product_category"].astype(str))
    )

    # ---------------- Revenue Bar Chart ----------------

    fig = px.bar(
        category_df,
        x="product_category",
        y="revenue",
        color="revenue",
        title="Revenue by Product Category",
        template="plotly_white"
    )

    chart = fig.to_html(full_html=False)

    # ---------------- Revenue Pie ----------------

    pie = px.pie(
        category_df,
        names="product_category",
        values="revenue",
        hole=0.45,
        template="plotly_white",
        title="Revenue Distribution by Category"
    )

    pie_chart = pie.to_html(full_html=False)

    # ---------------- Monthly Revenue ----------------

    monthly_df = (
        filtered_df.groupby(
            filtered_df["visit_date"].dt.to_period("M")
        )["revenue"]
        .sum()
        .reset_index()
    )

    monthly_df["visit_date"] = monthly_df["visit_date"].astype(str)

    line = px.line(
        monthly_df,
        x="visit_date",
        y="revenue",
        markers=True,
        template="plotly_white",
        title="Monthly Revenue Trend"
    )

    line_chart = line.to_html(full_html=False)

    # ---------------- Payment Method ----------------

    payment_names = {
        0: "Credit Card",
        1: "Debit Card",
        2: "UPI",
        3: "Net Banking",
        4: "Cash On Delivery"
    }

    payment_df = (
        filtered_df.groupby("payment_method")["revenue"]
        .sum()
        .reset_index()
    )

    payment_df["payment_method"] = (
        payment_df["payment_method"]
        .map(payment_names)
        .fillna(payment_df["payment_method"].astype(str))
    )

    payment_fig = px.pie(
        payment_df,
        names="payment_method",
        values="revenue",
        hole=0.45,
        template="plotly_white"
    )

    payment_chart = payment_fig.to_html(full_html=False)

        # ---------------- Device Type ----------------

    device_names = {
        0: "Desktop",
        1: "Mobile",
        2: "Tablet"
    }

    device_df = (
        filtered_df.groupby("device_type")
        .size()
        .reset_index(name="Users")
    )

    device_df["device_type"] = (
        device_df["device_type"]
        .map(device_names)
        .fillna(device_df["device_type"].astype(str))
    )

    device_fig = px.bar(
        device_df,
        x="device_type",
        y="Users",
        color="Users",
        text="Users",
        template="plotly_white",
        title="Users by Device Type"
    )

    device_fig.update_traces(textposition="outside")

    device_chart = device_fig.to_html(full_html=False)

    # ---------------- Marketing Channel ----------------

    marketing_names = {
        0: "Google Ads",
        1: "Facebook",
        2: "Instagram",
        3: "Email",
        4: "YouTube",
        5: "Organic Search"
    }

    marketing_df = (
        filtered_df.groupby("marketing_channel")["revenue"]
        .sum()
        .reset_index()
    )

    marketing_df["marketing_channel"] = (
        marketing_df["marketing_channel"]
        .map(marketing_names)
        .fillna(marketing_df["marketing_channel"].astype(str))
    )

    marketing_fig = px.bar(
        marketing_df,
        x="marketing_channel",
        y="revenue",
        color="revenue",
        text="revenue",
        template="plotly_white",
        title="Revenue by Marketing Channel"
    )

    marketing_fig.update_traces(
        texttemplate="₹%{y:,.0f}",
        textposition="outside"
    )

    marketing_chart = marketing_fig.to_html(full_html=False)

    # ---------------- Top Products ----------------

    top_products = (
        filtered_df.groupby("product_id")["revenue"]
        .sum()
        .reset_index()
        .sort_values(by="revenue", ascending=False)
        .head(10)
    )

    top_products_fig = px.bar(
        top_products,
        x="product_id",
        y="revenue",
        color="revenue",
        text="revenue",
        template="plotly_white",
        title="Top 10 Products by Revenue"
    )

    top_products_fig.update_traces(
        texttemplate="₹%{y:,.0f}",
        textposition="outside"
    )

    top_products_chart = top_products_fig.to_html(full_html=False)

    return render_template(
        "dashboard.html",
        revenue=total_revenue,
        customers=total_customers,
        products=total_products,
        orders=total_orders,
        avg_rating=avg_rating,
        avg_order_value=avg_order_value,
        repeat_customers=repeat_customers,
        monthly_growth=monthly_growth,
        chart=chart,
        pie_chart=pie_chart,
        line_chart=line_chart,
        payment_chart=payment_chart,
        device_chart=device_chart,
        marketing_chart=marketing_chart,
        top_products_chart=top_products_chart
    )


# ---------------- Sales ----------------

@app.route("/sales")
def sales():

    sales_df = df.copy()

    # Ensure correct data types
    sales_df["visit_date"] = pd.to_datetime(
        sales_df["visit_date"], errors="coerce"
    )

    sales_df["revenue"] = pd.to_numeric(
        sales_df["revenue"], errors="coerce"
    )

    sales_df["quantity"] = pd.to_numeric(
        sales_df["quantity"], errors="coerce"
    )

    sales_df = sales_df.dropna(
        subset=["visit_date", "revenue"]
    )

    # KPI Cards
    total_revenue = round(
        sales_df["revenue"].sum(), 2
    )

    total_orders = len(sales_df)

    total_quantity = int(
        sales_df["quantity"].sum()
    )

    avg_order = round(
        sales_df["revenue"].mean(), 2
    )

    # Monthly Sales
    monthly_sales = (
        sales_df.groupby(
            sales_df["visit_date"].dt.to_period("M")
        )["revenue"]
        .sum()
        .reset_index()
    )

    monthly_sales["visit_date"] = (
        monthly_sales["visit_date"]
        .astype(str)
    )

    fig = px.line(
        monthly_sales,
        x="visit_date",
        y="revenue",
        markers=True,
        title="Monthly Sales Trend",
        template="plotly_white"
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Revenue (₹)",
        hovermode="x unified"
    )

    sales_chart = fig.to_html(
        full_html=False
    )

    return render_template(
        "sales.html",
        revenue=total_revenue,
        orders=total_orders,
        quantity=total_quantity,
        avg_order=avg_order,
        sales_chart=sales_chart
    )


# ---------------- Customers ----------------

@app.route("/customers")
def customers():

    customer_df = df.copy()

    # Convert rating to numeric
    customer_df["rating"] = pd.to_numeric(
        customer_df["rating"],
        errors="coerce"
    )

    # KPI Cards
    total_customers = int(
        customer_df["customer_id"].nunique()
    )

    avg_rating = round(
        customer_df["rating"].mean(),
        2
    )

    # Customer Type
    customer_type = (
        customer_df.groupby("user_type")
        .size()
        .reset_index(name="Customers")
    )

    user_type_names = {
        0: "New Customer",
        1: "Returning Customer"
    }

    customer_type["user_type"] = (
        customer_type["user_type"]
        .map(user_type_names)
        .fillna(customer_type["user_type"].astype(str))
    )

    fig = px.pie(
        customer_type,
        names="user_type",
        values="Customers",
        hole=0.45,
        title="Customer Type Distribution",
        template="plotly_white"
    )

    fig.update_traces(
        textinfo="percent+label"
    )

    customer_chart = fig.to_html(
        full_html=False
    )

    return render_template(
        "customers.html",
        customers=total_customers,
        rating=avg_rating,
        customer_chart=customer_chart
    )


# ---------------- Products ----------------

@app.route("/products")
def products():

    product_df = df.copy()

    # Convert revenue to numeric
    product_df["revenue"] = pd.to_numeric(
        product_df["revenue"],
        errors="coerce"
    )

    # KPI Cards
    total_products = int(
        product_df["product_id"].nunique()
    )

    avg_price = round(
        product_df["revenue"].mean(),
        2
    )

    # Category Mapping
    category_names = {
        0: "Electronics",
        1: "Fashion",
        2: "Home & Kitchen",
        3: "Beauty",
        4: "Sports",
        5: "Books",
        6: "Grocery",
        7: "Toys"
    }

    product_sales = (
        product_df.groupby("product_category")["revenue"]
        .sum()
        .reset_index()
    )

    product_sales["product_category"] = (
        product_sales["product_category"]
        .map(category_names)
        .fillna(product_sales["product_category"].astype(str))
    )

    # Revenue Bar Chart
    fig = px.bar(
        product_sales,
        x="product_category",
        y="revenue",
        color="revenue",
        text="revenue",
        title="Revenue by Product Category",
        template="plotly_white"
    )

    fig.update_traces(
        texttemplate="₹%{y:,.0f}",
        textposition="outside"
    )

    fig.update_layout(
        showlegend=False,
        xaxis_title="Product Category",
        yaxis_title="Revenue (₹)"
    )

    product_chart = fig.to_html(full_html=False)

    # Revenue Pie Chart
    pie = px.pie(
        product_sales,
        names="product_category",
        values="revenue",
        hole=0.45,
        title="Revenue Distribution by Category",
        template="plotly_white"
    )

    pie.update_traces(
        textinfo="percent+label"
    )

    pie_chart = pie.to_html(full_html=False)

    return render_template(
        "products.html",
        products=total_products,
        avg_price=avg_price,
        product_chart=product_chart,
        pie_chart=pie_chart
    )


# ---------------- Reports ----------------

@app.route("/reports")
def reports():

    report_df = df.copy()

    report_df["revenue"] = pd.to_numeric(
        report_df["revenue"],
        errors="coerce"
    )

    total_revenue = round(
        report_df["revenue"].sum(),
        2
    )

    total_orders = int(len(report_df))

    total_customers = int(
        report_df["customer_id"].nunique()
    )

    total_products = int(
        report_df["product_id"].nunique()
    )

    return render_template(
        "reports.html",
        total_revenue=total_revenue,
        total_orders=total_orders,
        total_customers=total_customers,
        total_products=total_products
    )


# ---------------- About ----------------

@app.route("/about")
def about():
    return render_template("about.html")


# ---------------- Run Application ----------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )