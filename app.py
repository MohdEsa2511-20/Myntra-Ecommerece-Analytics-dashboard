from flask import Flask, render_template, request
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px

app = Flask(__name__)

# MySQL Connection
engine = create_engine(
    "mysql+pymysql://root:sidd2025@localhost:3305/ecommerce_db"
)

# Load Data
df = pd.read_sql("SELECT * FROM ecommerce_data", engine)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/dashboard")
def dashboard():

    # ---------------- Filter Values ----------------

    quick_filter = request.args.get("quick_filter")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    filtered_df = df.copy()
    filtered_df["visit_date"] = pd.to_datetime(filtered_df["visit_date"])

    # Date Filter
    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df["visit_date"] >= start_date)
            &
            (filtered_df["visit_date"] <= end_date)
        ]

    # ---------------- KPI Cards ----------------

    total_revenue = round(filtered_df["revenue"].sum(), 2)
    total_customers = filtered_df["customer_id"].nunique()
    total_products = filtered_df["product_id"].nunique()
    total_orders = len(filtered_df)

    # Additional KPIs

    avg_rating = round(filtered_df["rating"].mean(), 2)
    avg_order_value = round(filtered_df["revenue"].mean(), 2)

    repeat_customers = (
        filtered_df.groupby("customer_id")
        .size()
        .gt(1)
        .sum()
    )

    monthly_growth = 12.8

    # ---------------- Product Category ----------------

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

    # ---------------- Bar Chart ----------------

    fig = px.bar(
        category_df,
        x="product_category",
        y="revenue",
        color="revenue",
        title="Revenue by Product Category"
    )

    chart = fig.to_html(full_html=False)

    # ---------------- Pie Chart ----------------

    pie = px.pie(
        category_df,
        names="product_category",
        values="revenue",
        hole=0.4,
        title="Revenue Distribution by Category"
    )

    pie_chart = pie.to_html(full_html=False)

        # ---------------- Monthly Revenue ----------------

    df_copy = filtered_df.copy()
    df_copy["visit_date"] = pd.to_datetime(df_copy["visit_date"])

    monthly_df = (
        df_copy.groupby(
            df_copy["visit_date"].dt.to_period("M")
        )["revenue"]
        .sum()
        .reset_index()
    )

    monthly_df["visit_date"] = monthly_df["visit_date"].astype(str)

    fig2 = px.line(
        monthly_df,
        x="visit_date",
        y="revenue",
        markers=True,
        title="Monthly Revenue Trend",
        template="plotly_white"
    )

    fig2.update_layout(
        xaxis_title="Month",
        yaxis_title="Revenue (₹)",
        hovermode="x unified"
    )

    line_chart = fig2.to_html(full_html=False)

    # ---------------- Payment Method ----------------

    payment_names = {
        0: "Credit Card",
        1: "Debit Card",
        2: "UPI",
        3: "Net Banking",
        4: "Cash on Delivery"
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
        title="Revenue by Payment Method",
        template="plotly_white"
    )

    payment_fig.update_traces(
        textposition="inside",
        textinfo="percent+label"
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
        title="Users by Device Type",
        template="plotly_white",
        color_continuous_scale="Blues"
    )

    device_fig.update_traces(
        textposition="outside"
    )

    device_fig.update_layout(
        showlegend=False,
        xaxis_title="Device",
        yaxis_title="Number of Users"
    )

    device_chart = device_fig.to_html(full_html=False)

               # ---------------- Marketing Channel Analysis ----------------

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
        title="Revenue by Marketing Channel",
        template="plotly_white",
        color_continuous_scale="Blues"
    )

    marketing_fig.update_traces(
        texttemplate="₹%{y:,.0f}",
        textposition="outside"
    )

    marketing_fig.update_layout(
        showlegend=False,
        xaxis_title="Marketing Channel",
        yaxis_title="Revenue (₹)",
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=20, r=20, t=60, b=20)
    )

    marketing_chart = marketing_fig.to_html(full_html=False)

    # ---------------- Top 10 Products ----------------

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
        title="Top 10 Products by Revenue",
        template="plotly_white",
        color_continuous_scale="Viridis"
    )

    top_products_fig.update_traces(
        texttemplate="₹%{y:,.0f}",
        textposition="outside"
    )

    top_products_fig.update_layout(
        showlegend=False,
        xaxis_title="Product ID",
        yaxis_title="Revenue (₹)",
        margin=dict(l=20, r=20, t=60, b=20)
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
        top_products_chart=top_products_chart,
    )


@app.route("/sales")
def sales():

    total_revenue = round(df["revenue"].sum(), 2)
    total_orders = len(df)
    total_quantity = int(df["quantity"].sum())
    avg_order = round(df["revenue"].mean(), 2)

    sales_df = df.copy()
    sales_df["visit_date"] = pd.to_datetime(sales_df["visit_date"])

    monthly_sales = (
        sales_df.groupby(
            sales_df["visit_date"].dt.to_period("M")
        )["revenue"]
        .sum()
        .reset_index()
    )

    monthly_sales["visit_date"] = monthly_sales["visit_date"].astype(str)

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
        hovermode="x unified",
        margin=dict(l=20, r=20, t=60, b=20)
    )

    sales_chart = fig.to_html(full_html=False)

    return render_template(
        "sales.html",
        revenue=total_revenue,
        orders=total_orders,
        quantity=total_quantity,
        avg_order=avg_order,
        sales_chart=sales_chart
    )


@app.route("/customers")
def customers():

    total_customers = df["customer_id"].nunique()
    avg_rating = round(df["rating"].mean(), 2)

    customer_type = (
        df.groupby("user_type")
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

    fig.update_traces(textinfo="percent+label")

    customer_chart = fig.to_html(full_html=False)

    return render_template(
        "customers.html",
        customers=total_customers,
        rating=avg_rating,
        customer_chart=customer_chart
    )


@app.route("/products")
def products():

    total_products = df["product_id"].nunique()
    avg_price = round(df["revenue"].mean(), 2)

    product_sales = (
        df.groupby("product_category")["revenue"]
        .sum()
        .reset_index()
    )

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

    product_sales["product_category"] = (
        product_sales["product_category"]
        .map(category_names)
        .fillna(product_sales["product_category"].astype(str))
    )

    fig = px.bar(
        product_sales,
        x="product_category",
        y="revenue",
        color="revenue",
        text="revenue",
        title="Revenue by Product Category",
        template="plotly_white",
        color_continuous_scale="Blues"
    )

    fig.update_traces(
        texttemplate="₹%{y:,.0f}",
        textposition="outside"
    )

    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=False,
        xaxis_title="Product Category",
        yaxis_title="Revenue (₹)"
    )

    product_chart = fig.to_html(full_html=False)
        # ---------------- Revenue Pie Chart ----------------

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

    pie.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=20, r=20, t=60, b=20)
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
    return render_template(
        "reports.html",
        total_revenue=round(df["revenue"].sum(), 2),
        total_orders=len(df),
        total_customers=df["customer_id"].nunique(),
        total_products=df["product_id"].nunique()
    )


# ---------------- About ----------------

@app.route("/about")
def about():
    return render_template("about.html")


# ---------------- Run App ----------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )