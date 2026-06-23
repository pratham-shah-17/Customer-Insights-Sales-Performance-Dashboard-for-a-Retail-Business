import os
import subprocess
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pickle
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Retail Customer Insights & Sales Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling via CSS
st.markdown("""
<style>
    .reportview-container {
        background: #0f172a;
    }
    .metric-card {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        text-align: center;
    }
    .metric-title {
        font-size: 0.875rem;
        color: #94a3b8;
        font-weight: 600;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.875rem;
        color: #f8fafc;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .metric-delta {
        font-size: 0.875rem;
        font-weight: 600;
    }
    .delta-up {
        color: #10b981;
    }
    .delta-down {
        color: #ef4444;
    }
</style>
""", unsafe_markdown=True)

# Helper function to run backend pipelines
def run_pipeline():
    with st.spinner("Executing Data Ingestion Pipeline..."):
        subprocess.run(["python", "src/data_ingestion.py"], check=True)
    with st.spinner("Executing Preprocessing & KPI Calculations..."):
        subprocess.run(["python", "src/data_cleaning.py"], check=True)
    with st.spinner("Executing Exploratory Analysis & Segmentations..."):
        subprocess.run(["python", "src/eda_engine.py"], check=True)
    with st.spinner("Executing Predictive Model Training..."):
        subprocess.run(["python", "src/ml_pipeline.py"], check=True)
    with st.spinner("Executing Strategic Analysis Engine..."):
        subprocess.run(["python", "src/insights_engine.py"], check=True)
    st.success("End-to-End Analytics Pipeline executed successfully! Refreshing dashboard data...")
    st.rerun()

# Check dataset presence
data_files = [
    "data/master_dataset.csv",
    "data/rfm_customer_segments.csv",
    "data/customer_risk_predictions.csv",
    "data/sales_future_forecast.csv",
    "data/inventory_recommendations.csv"
]
pipeline_needed = any(not os.path.exists(f) for f in data_files)

# Sidebar
st.sidebar.image("https://img.icons8.com/color/96/000000/dashboard.png", width=80)
st.sidebar.title("Retail Insights Engine")
st.sidebar.markdown("*Decision Support & Analytics Suite*")
st.sidebar.divider()

if pipeline_needed:
    st.sidebar.warning("Pipeline files missing. Ingesting baseline dataset is required.")
    if st.sidebar.button("Run Analytics Pipeline", use_container_width=True):
        run_pipeline()
    st.stop()

# Load Datasets
@st.cache_data
def load_data():
    df_master = pd.read_csv("data/master_dataset.csv")
    df_rfm = pd.read_csv("data/rfm_customer_segments.csv")
    df_risk = pd.read_csv("data/customer_risk_predictions.csv")
    df_forecast = pd.read_csv("data/sales_future_forecast.csv")
    df_inventory = pd.read_csv("data/inventory_recommendations.csv")
    
    # Ensure dates are datetime objects
    df_master["order_date"] = pd.to_datetime(df_master["order_date"])
    
    return df_master, df_rfm, df_risk, df_forecast, df_inventory

df_master, df_rfm, df_risk, df_forecast, df_inventory = load_data()

# Navigation Tabs
tabs = ["📊 Executive Overview", "👥 Customer Insights", "📦 Product & Inventory", "🔮 Predictive Analytics", "📤 Data Pipeline & Reports"]
selected_tab = st.sidebar.radio("Navigation", tabs)

# Add filters in the sidebar
st.sidebar.divider()
st.sidebar.markdown("### Dashboard Slicers")

# Date Slicer
min_date = df_master["order_date"].min().to_pydatetime()
max_date = df_master["order_date"].max().to_pydatetime()
start_date, end_date = st.sidebar.slider(
    "Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)

# Region Slicer
all_regions = sorted(df_master["region"].unique())
selected_regions = st.sidebar.multiselect("Regions", all_regions, default=all_regions)

# Category Slicer
all_categories = sorted(df_master["category"].unique())
selected_categories = st.sidebar.multiselect("Product Categories", all_categories, default=all_categories)

# Apply filters
df_filtered = df_master[
    (df_master["order_date"] >= pd.to_datetime(start_date)) &
    (df_master["order_date"] <= pd.to_datetime(end_date)) &
    (df_master["region"].isin(selected_regions)) &
    (df_master["category"].isin(selected_categories))
]

# Tab 1: Executive Overview
if selected_tab == "📊 Executive Overview":
    st.title("Executive Dashboard Overview")
    st.markdown("---")
    
    # 1. Calculated KPI Cards
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    
    total_revenue = df_filtered["revenue"].sum()
    total_profit = df_filtered["profit"].sum()
    total_orders = df_filtered["order_id"].nunique()
    total_customers = df_filtered["customer_id"].nunique()
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    margin_pct = (total_profit / total_revenue) * 100 if total_revenue > 0 else 0
    
    with kpi1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Revenue</div>
            <div class="metric-value">${total_revenue:,.2f}</div>
            <div class="metric-delta delta-up">▲ 100% (Active Filters)</div>
        </div>
        """, unsafe_markdown=True)
        
    with kpi2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Profit</div>
            <div class="metric-value">${total_profit:,.2f}</div>
            <div class="metric-delta delta-up" style="color: {'#ef4444' if total_profit < 0 else '#10b981'}">
                {'▼' if total_profit < 0 else '▲'} Margin: {margin_pct:.1f}%
            </div>
        </div>
        """, unsafe_markdown=True)
        
    with kpi3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Orders</div>
            <div class="metric-value">{total_orders:,}</div>
            <div class="metric-delta delta-up">▲ Sales Volume</div>
        </div>
        """, unsafe_markdown=True)
        
    with kpi4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Active Customers</div>
            <div class="metric-value">{total_customers:,}</div>
            <div class="metric-delta delta-up">▲ Unique Profiles</div>
        </div>
        """, unsafe_markdown=True)
        
    with kpi5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Avg Order Value</div>
            <div class="metric-value">${avg_order_value:,.2f}</div>
            <div class="metric-delta delta-up">▲ Spent / Order</div>
        </div>
        """, unsafe_markdown=True)
        
    st.markdown("### Sales Trend & Distribution Analyses")
    col_left, col_right = st.columns([2, 1])
    
    # Left: Monthly Revenue Trend
    with col_left:
        df_monthly = df_filtered.set_index("order_date").resample("ME")["revenue"].sum().reset_index()
        fig_trend = px.line(
            df_monthly, x="order_date", y="revenue", 
            title="Monthly Sales Trend (Gross Revenue)", 
            labels={"revenue": "Revenue ($)", "order_date": "Order Date"},
            template="plotly_dark"
        )
        fig_trend.update_traces(line=dict(color="#38bdf8", width=3), marker=dict(size=6))
        st.plotly_chart(fig_trend, use_container_width=True)
        
    # Right: Sales by Region Map/Bar
    with col_right:
        df_region = df_filtered.groupby("region")["revenue"].sum().reset_index()
        fig_region = px.pie(
            df_region, values="revenue", names="region", 
            title="Revenue Distribution by Region",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            template="plotly_dark"
        )
        st.plotly_chart(fig_region, use_container_width=True)
        
    st.divider()
    col_bottom_l, col_bottom_r = st.columns(2)
    
    # Bottom Left: Category & Sub-category Breakdown
    with col_bottom_l:
        df_cat = df_filtered.groupby("category")["revenue"].sum().reset_index()
        fig_cat = px.bar(
            df_cat, x="category", y="revenue", 
            title="Sales Contribution by Product Category",
            labels={"revenue": "Revenue ($)", "category": "Product Category"},
            template="plotly_dark",
            color="category",
            color_discrete_sequence=["#38bdf8", "#10b981", "#fbbf24"]
        )
        st.plotly_chart(fig_cat, use_container_width=True)
        
    # Bottom Right: Discount vs Profitability Analysis
    with col_bottom_r:
        df_filtered["discount_pct"] = df_filtered["discount"] * 100
        fig_scatter = px.scatter(
            df_filtered, x="discount_pct", y="profit", 
            color="category",
            title="Discount Rate Impact on Transactional Profit",
            labels={"discount_pct": "Discount Rate (%)", "profit": "Profit ($)"},
            template="plotly_dark"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

# Tab 2: Customer Insights
elif selected_tab == "👥 Customer Insights":
    st.title("Customer Demographics & Retention Analysis")
    st.markdown("---")
    
    col_cust_l, col_cust_r = st.columns([1, 1])
    
    # Left: RFM Bins
    with col_cust_l:
        segment_counts = df_rfm["rfm_segment"].value_counts().reset_index()
        segment_counts.columns = ["RFM Segment", "Count"]
        
        fig_segments = px.bar(
            segment_counts, x="Count", y="RFM Segment", 
            orientation="h",
            title="Customer Cohorts via RFM Analysis",
            template="plotly_dark",
            color="RFM Segment",
            color_discrete_sequence=px.colors.qualitative.Dark24
        )
        st.plotly_chart(fig_segments, use_container_width=True)
        
    # Right: Churn Risk Category distribution
    with col_cust_r:
        risk_counts = df_risk["risk_category"].value_counts().reset_index()
        risk_counts.columns = ["Risk Category", "Count"]
        
        fig_risk = px.pie(
            risk_counts, values="Count", names="Risk Category", 
            title="Customer Retention & Churn Risk Segmentation",
            template="plotly_dark",
            color="Risk Category",
            color_discrete_map={"Low Risk": "#10b981", "Medium Risk": "#fbbf24", "High Risk": "#ef4444"}
        )
        st.plotly_chart(fig_risk, use_container_width=True)
        
    st.divider()
    st.markdown("### Customer Demographic Insights")
    
    col_demo1, col_demo2 = st.columns(2)
    
    # Demo 1: Age vs Spending
    with col_demo1:
        fig_age = px.histogram(
            df_master, x="age", y="revenue", 
            color="gender", 
            title="Revenue Contribution by Customer Age & Gender",
            labels={"age": "Customer Age", "revenue": "Cumulative Sales ($)"},
            template="plotly_dark",
            nbins=15
        )
        st.plotly_chart(fig_age, use_container_width=True)
        
    # Demo 2: Customer Lifetime Value (CLV)
    with col_demo2:
        df_clv_bins = df_risk.sort_values("total_revenue", ascending=False).head(100)
        fig_clv = px.bar(
            df_clv_bins, x="customer_id", y="total_revenue",
            color="risk_category",
            title="Top 100 High-Value Customers by Cumulative Spend",
            labels={"customer_id": "Customer Code", "total_revenue": "Lifetime Spend ($)"},
            template="plotly_dark"
        )
        st.plotly_chart(fig_clv, use_container_width=True)

# Tab 3: Product & Inventory
elif selected_tab == "📦 Product & Inventory":
    st.title("Product Performance & Inventory Analytics")
    st.markdown("---")
    
    col_prod_l, col_prod_r = st.columns(2)
    
    with col_prod_l:
        st.markdown("### Top Selling Products (By Revenue)")
        df_top_prod = df_master.groupby("product_name")["revenue"].sum().reset_index()
        df_top_prod = df_top_prod.sort_values("revenue", ascending=False).head(10)
        
        fig_top = px.bar(
            df_top_prod, x="revenue", y="product_name", 
            orientation="h",
            labels={"revenue": "Revenue ($)", "product_name": "Product Name"},
            template="plotly_dark",
            color="revenue",
            color_continuous_scale="Viridis"
        )
        fig_top.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_top, use_container_width=True)
        
    with col_prod_r:
        st.markdown("### Product Return Rates by Sub-Category")
        df_sub_returns = df_master.groupby("sub_category")["return_flag"].mean().reset_index()
        df_sub_returns["return_rate_pct"] = df_sub_returns["return_flag"] * 100
        df_sub_returns = df_sub_returns.sort_values("return_rate_pct", ascending=False)
        
        fig_ret = px.bar(
            df_sub_returns, x="return_rate_pct", y="sub_category",
            orientation="h",
            labels={"return_rate_pct": "Return Rate (%)", "sub_category": "Sub-Category"},
            template="plotly_dark",
            color="return_rate_pct",
            color_continuous_scale="Reds"
        )
        fig_ret.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_ret, use_container_width=True)
        
    st.divider()
    st.markdown("### 📋 Predictive Inventory Optimization (Safety Stock & Reorder Points)")
    st.markdown("This module calculates the optimal safety stock thresholds based on daily transaction volumes and supplier lead-times (10 days average, 15 days max).")
    
    # Display table of recommendations
    st.dataframe(
        df_inventory.style.format({
            "Avg Daily Demand": "{:.2f}",
            "Standard Deviation": "{:.2f}",
            "Forecasted Monthly Demand": "{:,}",
            "Safety Stock Limit": "{:,}",
            "Reorder Point": "{:,}"
        }),
        use_container_width=True
    )

# Tab 4: Predictive Analytics
elif selected_tab == "🔮 Predictive Analytics":
    st.title("Machine Learning Predictive Analytics Portal")
    st.markdown("---")
    
    ml_page = st.selectbox("Select ML Subsystem", ["📈 Time-Series Sales Forecasting", "👥 Individual Customer Churn Predictor"])
    
    if ml_page == "📈 Time-Series Sales Forecasting":
        st.subheader("12-Month Rolling Revenue Forecast")
        st.markdown("Ensemble models (Random Forest, XGBoost, and Seasonal regression models) trained on historical monthly aggregates.")
        
        # Load forecast metrics
        df_fore_metrics = pd.read_csv("data/sales_forecasting_metrics.csv")
        st.markdown("#### Model Performance Evaluation Table")
        st.table(df_fore_metrics)
        
        # Line chart of historical + forecast
        # Agg historical
        df_master["year_month"] = df_master["order_date"].dt.to_period("M")
        df_hist_monthly = df_master.groupby("year_month")["revenue"].sum().reset_index()
        df_hist_monthly["year_month"] = df_hist_monthly["year_month"].astype(str)
        df_hist_monthly["Type"] = "Historical"
        df_hist_monthly = df_hist_monthly.rename(columns={"year_month": "Date", "revenue": "Sales Amount"})
        
        # Forecast
        df_fore = df_forecast.copy()
        df_fore["Date"] = pd.to_datetime(df_fore["Date"]).dt.to_period("M").astype(str)
        df_fore["Type"] = "ML Forecast"
        df_fore = df_fore.rename(columns={"Forecasted Sales": "Sales Amount"})
        
        # Merge
        df_combined_forecast = pd.concat([df_hist_monthly, df_fore], axis=0).reset_index(drop=True)
        
        fig_fore = px.line(
            df_combined_forecast, x="Date", y="Sales Amount", 
            color="Type",
            title="12-Month Sales Projections & Seasonal Target Cycles",
            labels={"Sales Amount": "Monthly Sales ($)", "Date": "Year-Month"},
            template="plotly_dark",
            color_discrete_map={"Historical": "#38bdf8", "ML Forecast": "#10b981"}
        )
        st.plotly_chart(fig_fore, use_container_width=True)
        
        st.divider()
        st.markdown("### 🎛️ Interactive Forecast Scenario Simulator")
        st.markdown("Adjust macro parameters to forecast how promotions and marketing budget boosts will affect projected revenues.")
        
        sim_col1, sim_col2 = st.columns(2)
        with sim_col1:
            promo_boost = st.slider("Additional Marketing Budget Allocation ($)", 0, 50000, 10000, step=5000)
        with sim_col2:
            discount_cap_effect = st.checkbox("Cap Maximum Customer Discounts to 20%", value=True)
            
        # Simulated boost calculation
        multiplier = 1.0 + (promo_boost / 150000.0)
        if discount_cap_effect:
            multiplier += 0.03 # 3% margin/revenue recovery
            
        simulated_sales = df_forecast["Forecasted Sales"].sum() * multiplier
        baseline_forecast = df_forecast["Forecasted Sales"].sum()
        
        st.metric(
            label="Projected Simulated Cumulative Revenue (Next 12 Months)",
            value=f"${simulated_sales:,.2f}",
            delta=f"${simulated_sales - baseline_forecast:,.2f} increase vs baseline forecast"
        )
        
    elif ml_page == "👥 Individual Customer Churn Predictor":
        st.subheader("Customer Retention Risk Profiler")
        st.markdown("Evaluate any customer's churn risk score in real-time. The classifier utilizes Recency, AOV, spend frequency, and regional modifiers.")
        
        # Load Classifier metrics
        df_churn_metrics = pd.read_csv("data/customer_churn_metrics.csv")
        st.markdown("#### Classifier Performance Evaluation Table")
        st.table(df_churn_metrics)
        
        # Select customer
        customer_list = df_risk["customer_id"].tolist()
        selected_cust = st.selectbox("Select Customer ID", customer_list)
        
        cust_profile = df_risk[df_risk["customer_id"] == selected_cust].iloc[0]
        
        # Load classifier model
        with open("models/customer_churn_model.pkl", "rb") as f:
            model_pack = pickle.load(f)
            
        # Draw metric stats
        st.divider()
        st.markdown(f"### Profile Analysis for Customer: **{selected_cust}**")
        
        stat1, stat2, stat3, stat4 = st.columns(4)
        stat1.metric("Customer Age", f"{int(cust_profile['age'])} yrs")
        stat2.metric("Customer Gender", cust_profile['gender'])
        stat3.metric("Geography Region", cust_profile['region'])
        stat4.metric("Historic Revenue Spend", f"${cust_profile['total_revenue']:,.2f}")
        
        # Risk gauge meter
        risk_prob = cust_profile["churn_probability"] * 100
        risk_cat = cust_profile["risk_category"]
        
        st.markdown("#### Retention Churn Risk Assessment Score")
        
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = risk_prob,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"Risk Category: {risk_cat}", 'font': {'size': 24}},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': "#1e293b"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 30], 'color': '#10b981'},  # Low risk: Green
                    {'range': [30, 70], 'color': '#fbbf24'}, # Med risk: Yellow
                    {'range': [70, 100], 'color': '#ef4444'}  # High risk: Red
                ]
            }
        ))
        fig_gauge.update_layout(paper_bgcolor='#0f172a', font={'color': "white", 'family': "Arial"})
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Action recommendation
        st.markdown("#### Strategic Retention recommendation")
        if risk_cat == "High Risk":
            st.error("🚨 **High Risk Customer**: Trigger **REC004 (Win-back discount incentive email)** immediately. Provide a targeted 15% discount code on next order.")
        elif risk_cat == "Medium Risk":
            st.warning("⚠️ **Medium Risk Customer**: Group under the **REC010 (Frequency Booster Email campaign)** program to upsell office catalog staples.")
        else:
            st.success("✅ **Low Risk/Loyal Customer**: Group in the **REC015 (VIP Club invitation)** program to incentivize word-of-mouth brand referrals.")

# Tab 5: Data Pipeline & Reports
elif selected_tab == "📤 Data Pipeline & Reports":
    st.title("Ingestion Ingestion Pipeline & PDF Reports")
    st.markdown("---")
    
    col_up, col_dn = st.columns(2)
    
    with col_up:
        st.markdown("### Ingest a New Retail Dataset")
        st.markdown("Upload a new raw transactions CSV file matching the relational structures. This will automatically trigger cleaning pipelines, update databases, and retrain machine learning classifiers.")
        
        uploaded_file = st.file_uploader("Choose Raw Superstore CSV", type=["csv"])
        
        if uploaded_file is not None:
            # Save raw file
            with open("data/raw_superstore.csv", "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("New raw transaction file uploaded successfully!")
            
            if st.button("Trigger Pipeline & Model Training", use_container_width=True):
                run_pipeline()
                
    with col_dn:
        st.markdown("### Export Reports and Tables")
        st.markdown("Download pre-calculated dataset files and project documentation sheets.")
        
        # Download Master Dataset
        with open("data/master_dataset.csv", "rb") as f:
            st.download_button(
                label="Download Clean Master Dataset (CSV)",
                data=f,
                file_name="master_dataset.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        # Download Churn Predictions
        with open("data/customer_risk_predictions.csv", "rb") as f:
            st.download_button(
                label="Download Churn Risk Scores (CSV)",
                data=f,
                file_name="customer_risk_predictions.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        # Download Inventory safety stock
        with open("data/inventory_recommendations.csv", "rb") as f:
            st.download_button(
                label="Download Inventory safety stock Rules (CSV)",
                data=f,
                file_name="inventory_recommendations.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        # Download Insights report
        if os.path.exists("reports/business_insights_report.md"):
            with open("reports/business_insights_report.md", "rb") as f:
                st.download_button(
                    label="Download Strategic Insights Report (Markdown)",
                    data=f,
                    file_name="business_insights_report.md",
                    mime="text/markdown",
                    use_container_width=True
                )
