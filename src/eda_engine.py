import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set plotting styles
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

# Create output directories
os.makedirs("static/charts", exist_ok=True)

def generate_sales_charts(df):
    """Generates all sales-related visualizations."""
    print("Generating Sales Analysis Charts...")
    
    # Pre-parse date
    df["order_date"] = pd.to_datetime(df["order_date"])
    
    # 1. Monthly Sales Trend
    df_monthly = df.set_index("order_date").resample("ME")["revenue"].sum().reset_index()
    fig, ax = plt.subplots()
    sns.lineplot(data=df_monthly, x="order_date", y="revenue", marker="o", color="#1a5276", linewidth=2.5, ax=ax)
    ax.set_title("Monthly Revenue Trend", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Order Date", fontweight="bold")
    ax.set_ylabel("Revenue ($)", fontweight="bold")
    plt.tight_layout()
    plt.savefig("static/charts/sales_monthly_trend.png", dpi=150)
    plt.close()
    
    # Plotly interactive version
    fig_plotly = px.line(df_monthly, x="order_date", y="revenue", title="Monthly Revenue Trend",
                         labels={"revenue": "Revenue ($)", "order_date": "Date"},
                         template="plotly_dark")
    fig_plotly.update_traces(line=dict(color="#1f77b4", width=3), marker=dict(size=6))
    fig_plotly.write_html("static/charts/sales_monthly_trend.html")

    # 2. Quarterly Growth
    df_quarterly = df.set_index("order_date").resample("QE")["revenue"].sum().reset_index()
    df_quarterly["quarter"] = df_quarterly["order_date"].dt.to_period("Q").astype(str)
    df_quarterly["growth_pct"] = df_quarterly["revenue"].pct_change() * 100
    
    fig, ax1 = plt.subplots()
    sns.barplot(data=df_quarterly, x="quarter", y="revenue", color="#2e86c1", ax=ax1, alpha=0.8)
    ax2 = ax1.twinx()
    sns.lineplot(data=df_quarterly, x="quarter", y="growth_pct", marker="s", color="#e74c3c", linewidth=2, ax=ax2)
    ax1.set_title("Quarterly Sales & Growth %", fontsize=14, fontweight="bold", pad=15)
    ax1.set_xlabel("Quarter", fontweight="bold")
    ax1.set_ylabel("Revenue ($)", fontweight="bold")
    ax2.set_ylabel("Growth Rate (%)", color="#e74c3c", fontweight="bold")
    plt.tight_layout()
    plt.savefig("static/charts/sales_quarterly_growth.png", dpi=150)
    plt.close()

    # 3. Revenue by Region
    df_region = df.groupby("region")["revenue"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(8, 8))
    colors = ["#2471a3", "#229954", "#d35400", "#7d3c98"]
    ax.pie(df_region["revenue"], labels=df_region["region"], autopct="%1.1f%%", startangle=90, 
           colors=colors, textprops={'fontweight': 'bold'})
    ax.set_title("Revenue Distribution by Region", fontsize=14, fontweight="bold", pad=15)
    plt.savefig("static/charts/sales_by_region.png", dpi=150)
    plt.close()

    # 4. Revenue by Top Cities
    df_city = df.groupby("city")["revenue"].sum().reset_index().sort_values("revenue", ascending=False).head(15)
    fig, ax = plt.subplots()
    sns.barplot(data=df_city, x="revenue", y="city", palette="viridis", ax=ax)
    ax.set_title("Top 15 Cities by Revenue", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Revenue ($)", fontweight="bold")
    ax.set_ylabel("City", fontweight="bold")
    plt.tight_layout()
    plt.savefig("static/charts/sales_by_city.png", dpi=150)
    plt.close()

    # 5. Revenue by Category and Sub-category
    df_cat = df.groupby(["category", "sub_category"])["revenue"].sum().reset_index().sort_values("revenue", ascending=False)
    fig = px.treemap(df_cat, path=["category", "sub_category"], values="revenue",
                     title="Revenue Breakdown by Category & Sub-Category",
                     color="revenue", color_continuous_scale="RdBu")
    fig.write_html("static/charts/sales_category_treemap.html")
    
    # Save static category comparison
    df_cat_summary = df.groupby("category")["revenue"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=df_cat_summary, x="category", y="revenue", palette="Blues_r", ax=ax)
    ax.set_title("Revenue by Product Category", fontsize=14, fontweight="bold")
    ax.set_xlabel("Category")
    ax.set_ylabel("Revenue ($)")
    plt.savefig("static/charts/sales_by_category.png")
    plt.close()

    # 6. Top 20 & Bottom 20 Products
    df_prod_sales = df.groupby("product_name")["revenue"].sum().reset_index()
    top_20 = df_prod_sales.sort_values("revenue", ascending=False).head(20)
    bottom_20 = df_prod_sales.sort_values("revenue", ascending=True).head(20)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(data=top_20, x="revenue", y="product_name", palette="GnBu_r", ax=ax)
    ax.set_title("Top 20 Products by Revenue", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig("static/charts/products_top_20.png")
    plt.close()
    
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(data=bottom_20, x="revenue", y="product_name", palette="OrRd", ax=ax)
    ax.set_title("Bottom 20 Products by Revenue", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig("static/charts/products_bottom_20.png")
    plt.close()

    # 7. Discount Impact on Profit
    # Segment discount levels
    df["discount_bin"] = pd.cut(df["discount"], bins=[-0.01, 0.0, 0.2, 0.5, 1.0], 
                                labels=["No Discount (0%)", "Low Discount (0.1-20%)", "Medium Discount (20.1-50%)", "High Discount (>50%)"])
    df_disc_impact = df.groupby("discount_bin", observed=False).agg(
        avg_profit=("profit", "mean"),
        total_revenue=("revenue", "sum"),
        total_profit=("profit", "sum")
    ).reset_index()
    
    fig, ax = plt.subplots()
    sns.barplot(data=df_disc_impact, x="discount_bin", y="avg_profit", palette="coolwarm", ax=ax)
    ax.set_title("Average Profit by Discount Tier", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Discount Tier", fontweight="bold")
    ax.set_ylabel("Average Profit ($)", fontweight="bold")
    plt.tight_layout()
    plt.savefig("static/charts/discount_impact_on_profit.png", dpi=150)
    plt.close()


def generate_customer_charts(df):
    """Generates all customer-related visualizations (cohort, retention, RFM)."""
    print("Generating Customer Analysis Charts & RFM Segmentation...")
    
    # 1. New vs Repeat Customer Analysis
    # A customer's first order date is their registration date
    first_orders = df.groupby("customer_id")["order_date"].transform("min")
    df["customer_type"] = np.where(df["order_date"] == first_orders, "New", "Repeat")
    
    df_cust_type = df.groupby("customer_type")["revenue"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(df_cust_type["revenue"], labels=df_cust_type["customer_type"], autopct="%1.1f%%", startangle=90, 
           colors=["#58d68d", "#2e86c1"], textprops={'fontweight': 'bold'})
    ax.set_title("Revenue Contribution: New vs Repeat Customers", fontsize=14, fontweight="bold")
    plt.savefig("static/charts/customer_new_vs_repeat.png")
    plt.close()

    # 2. RFM Analysis & Segmentation
    # Recency: days since last purchase (relative to max date in dataset)
    # Frequency: number of unique orders
    # Monetary: total spending
    max_date = df["order_date"].max()
    
    rfm = df.groupby("customer_id").agg(
        recency=("order_date", lambda x: (max_date - x.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("revenue", "sum")
    ).reset_index()
    
    # Scoring 1-5 (5 is best)
    # Recency: lower is better -> assign 5 to lowest recency
    rfm["r_score"] = pd.qcut(rfm["recency"], q=5, labels=[5, 4, 3, 2, 1], duplicates="drop")
    # Frequency and Monetary: higher is better -> assign 5 to highest
    rfm["f_score"] = pd.qcut(rfm["frequency"], q=5, labels=[1, 2, 3, 4, 5], duplicates="drop")
    rfm["m_score"] = pd.qcut(rfm["monetary"], q=5, labels=[1, 2, 3, 4, 5], duplicates="drop")
    
    # Cast to integer scores
    rfm["r_score"] = rfm["r_score"].astype(int)
    rfm["f_score"] = rfm["f_score"].astype(int)
    rfm["m_score"] = rfm["m_score"].astype(int)
    
    # Segment definition function
    def define_segment(row):
        r, f, m = row["r_score"], row["f_score"], row["m_score"]
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
        elif r >= 3 and f >= 3 and m >= 3:
            return "Loyal Customers"
        elif r >= 3 and f <= 3 and m >= 2:
            return "Potential Loyalists"
        elif r <= 2 and (f >= 3 or m >= 3):
            return "At Risk"
        else:
            return "Lost Customers"
            
    rfm["rfm_segment"] = rfm.apply(define_segment, axis=1)
    
    # Save RFM segmentation results to static/charts
    rfm.to_csv("data/rfm_customer_segments.csv", index=False)
    
    # Plot RFM Segment Distribution
    segment_counts = rfm["rfm_segment"].value_counts().reset_index()
    segment_counts.columns = ["Segment", "Count"]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=segment_counts, x="Count", y="Segment", palette="Set2", ax=ax)
    ax.set_title("Customer Segmentation via RFM Analysis", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Number of Customers", fontweight="bold")
    ax.set_ylabel("Segment", fontweight="bold")
    plt.tight_layout()
    plt.savefig("static/charts/customer_rfm_segments.png", dpi=150)
    plt.close()
    
    # Highlight lists
    high_value_custs = rfm[rfm["m_score"] == 5]["customer_id"].tolist()
    frequent_buyers = rfm[rfm["f_score"] == 5]["customer_id"].tolist()
    churn_risks = rfm[rfm["rfm_segment"] == "At Risk"]["customer_id"].tolist()
    
    print(f"  Champions count: {len(rfm[rfm['rfm_segment'] == 'Champions'])}")
    print(f"  At Risk count: {len(churn_risks)}")
    print(f"  High Value Customers (Monetary=5): {len(high_value_custs)}")
    
    # Write segment info back to master file inside Streamlit or scripts
    return rfm


def generate_product_charts(df):
    """Generates all product performance visualizations."""
    print("Generating Product Analysis Charts...")
    
    # 1. Fast-Moving vs Dead Stock
    # We define Dead Stock as products with cumulative quantity sold < 10 AND last sold date older than 365 days
    # (or simply lowest velocity scores)
    df_prod_stats = df.groupby(["product_id", "product_name", "category", "sub_category"]).agg(
        total_quantity=("quantity", "sum"),
        total_revenue=("revenue", "sum"),
        avg_margin=("profit_margin_pct", "mean"),
        last_sold_date=("order_date", "max"),
        velocity_score=("product_velocity_score", "first")
    ).reset_index()
    
    # Sort by velocity
    fast_moving = df_prod_stats.sort_values("velocity_score", ascending=False).head(20)
    dead_stock = df_prod_stats.sort_values("velocity_score", ascending=True).head(20)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=fast_moving, x="velocity_score", y="product_name", palette="summer", ax=ax)
    ax.set_title("Top 20 Fast-Moving Products (Velocity Score)", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig("static/charts/products_fast_moving.png")
    plt.close()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=dead_stock, x="velocity_score", y="product_name", palette="copper", ax=ax)
    ax.set_title("Bottom 20 Slowest-Moving Products (Velocity Score)", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig("static/charts/products_dead_stock.png")
    plt.close()

    # 2. High Return Products (Products with highest return rates)
    df_prod_returns = df.groupby(["product_id", "product_name"])["return_flag"].agg(["count", "mean"]).reset_index()
    # Filter products with at least 5 transactions to avoid low-sample bias
    high_returns = df_prod_returns[df_prod_returns["count"] >= 5].sort_values("mean", ascending=False).head(15)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=high_returns, x="mean", y="product_name", palette="Reds_r", ax=ax)
    ax.set_title("Top 15 High Return Rate Products (Min 5 purchases)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Return Probability", fontweight="bold")
    plt.tight_layout()
    plt.savefig("static/charts/products_high_returns.png")
    plt.close()

    # 3. High Margin vs Low Margin Products
    # Group by Sub-category for profitability
    df_subcat_profit = df.groupby("sub_category")["profit_margin_pct"].mean().reset_index().sort_values("profit_margin_pct", ascending=False)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=df_subcat_profit, x="profit_margin_pct", y="sub_category", palette="Spectral", ax=ax)
    ax.set_title("Average Profit Margin % by Sub-Category", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Average Margin Rate", fontweight="bold")
    ax.set_ylabel("Sub-Category", fontweight="bold")
    plt.tight_layout()
    plt.savefig("static/charts/products_margin_by_subcategory.png", dpi=150)
    plt.close()


def main():
    print("--- Starting Phase 3: Exploratory Data Analysis ---")
    
    if not os.path.exists("data/master_dataset.csv"):
        print("Error: data/master_dataset.csv not found. Running data_cleaning.py first...")
        os.system("python src/data_cleaning.py")
        
    df_master = pd.read_csv("data/master_dataset.csv")
    
    # Run visualization pipelines
    generate_sales_charts(df_master)
    rfm_df = generate_customer_charts(df_master)
    generate_product_charts(df_master)
    
    # Save a master table with customer segments joined back for ML modeling later
    df_master_rfm = pd.merge(df_master, rfm_df[["customer_id", "rfm_segment"]], on="customer_id", how="left")
    df_master_rfm.to_csv("data/master_dataset.csv", index=False)
    
    print("\n--- Phase 3 Completed: Visualizations saved to static/charts/ ---")

if __name__ == "__main__":
    main()
