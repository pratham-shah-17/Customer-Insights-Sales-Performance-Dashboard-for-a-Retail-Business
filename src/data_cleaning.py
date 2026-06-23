import os
import pandas as pd
import numpy as np

def clean_column_names(df):
    """Standardizes column names to lowercase snake_case."""
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('-', '_')
    return df

def detect_outliers_iqr(df, column):
    """Detects outliers using the Interquartile Range (IQR) method."""
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
    return outliers, lower_bound, upper_bound

def main():
    print("--- Starting Phase 2: Data Preprocessing & KPI Calculation ---")
    
    # 1. Load normalized tables
    print("Loading normalized tables...")
    df_cust = pd.read_csv("data/customer_data.csv")
    df_orders = pd.read_csv("data/orders_data.csv")
    df_prod = pd.read_csv("data/product_data.csv")
    df_region = pd.read_csv("data/region_data.csv")
    df_marketing = pd.read_csv("data/marketing_spend_data.csv")
    
    # 2. Standardize column names
    print("Standardizing column names...")
    df_cust = clean_column_names(df_cust)
    df_orders = clean_column_names(df_orders)
    df_prod = clean_column_names(df_prod)
    df_region = clean_column_names(df_region)
    df_marketing = clean_column_names(df_marketing)
    
    # Rename matching join keys to be uniform
    df_cust = df_cust.rename(columns={"name": "customer_name"})
    
    # 3. Handle duplicates and missing values
    print("Checking for duplicates and missing values...")
    # Remove duplicates
    df_cust = df_cust.drop_duplicates(subset=["customer_id"])
    df_orders = df_orders.drop_duplicates()
    df_prod = df_prod.drop_duplicates(subset=["product_id"])
    df_region = df_region.drop_duplicates()
    
    # Check missing values and impute if any
    for col in df_cust.columns:
        if df_cust[col].isnull().any():
            if df_cust[col].dtype == 'object':
                df_cust[col] = df_cust[col].fillna("Unknown")
            else:
                df_cust[col] = df_cust[col].fillna(df_cust[col].median())
                
    for col in df_orders.columns:
        if df_orders[col].isnull().any():
            if df_orders[col].dtype in ['float64', 'int64']:
                df_orders[col] = df_orders[col].fillna(0)
                
    # 4. Outlier detection on core variables (quantity, sales_amount, profit)
    print("Running outlier detection (IQR)...")
    for col in ["quantity", "sales_amount", "profit"]:
        outliers, lb, ub = detect_outliers_iqr(df_orders, col)
        print(f"  Outliers in {col}: {len(outliers)} records (Range: {lb:.2f} to {ub:.2f})")
        # We do not drop outliers because they represent real large transactions in retail,
        # but we flag them for modeling purposes later.
        df_orders[f"{col}_outlier"] = 0
        df_orders.loc[(df_orders[col] < lb) | (df_orders[col] > ub), f"{col}_outlier"] = 1

    # 5. Data type corrections
    print("Casting columns to proper data types...")
    df_cust["age"] = df_cust["age"].astype(int)
    df_cust["registration_date"] = pd.to_datetime(df_cust["registration_date"])
    df_orders["order_date"] = pd.to_datetime(df_orders["order_date"])
    df_orders["quantity"] = df_orders["quantity"].astype(int)
    df_orders["sales_amount"] = df_orders["sales_amount"].astype(float)
    df_orders["profit"] = df_orders["profit"].astype(float)
    df_orders["discount"] = df_orders["discount"].astype(float)
    df_marketing["campaign_date"] = pd.to_datetime(df_marketing["campaign_date"])
    df_marketing["spend_amount"] = df_marketing["spend_amount"].astype(float)

    # 6. Synthesize return flag (simulated business logic)
    # Different sub-categories have different return likelihoods
    print("Synthesizing order returns...")
    np.random.seed(42)
    # Join category info to orders temporarily to assign return rates
    df_order_prod_temp = pd.merge(df_orders, df_prod[["product_id", "category", "sub_category"]], on="product_id", how="left")
    
    return_probs = {
        "Furniture": 0.08,
        "Office Supplies": 0.04,
        "Technology": 0.05
    }
    
    # Hash-based return assignment for reproducibility
    def calculate_return(row):
        prob = return_probs.get(row["category"], 0.05)
        # Add modifier for discounts (higher discount -> higher return probability)
        if row["discount"] > 0.2:
            prob += 0.03
        return 1 if np.random.rand() < prob else 0
        
    df_orders["return_flag"] = df_order_prod_temp.apply(calculate_return, axis=1)
    print(f"  Total returned items: {df_orders['return_flag'].sum()} out of {len(df_orders)} transactions.")

    # 7. Merge datasets
    print("Merging normalized datasets into a master dataset...")
    # Merge orders with customers
    df_master = pd.merge(df_orders, df_cust, on="customer_id", how="left")
    # Merge with product details
    df_master = pd.merge(df_master, df_prod, on="product_id", how="left")
    
    # Note: region data is already present in customer (city, region) but we ensure state is joined
    # Map cities to their states from region_data
    df_city_state = df_region[["city", "state"]].drop_duplicates().reset_index(drop=True)
    df_master = pd.merge(df_master, df_city_state, on="city", how="left")
    
    # Merge marketing spend
    # Marketing spend is recorded monthly by region. Let's add a Year-Month column to both
    df_master["year_month"] = df_master["order_date"].dt.to_period("M")
    df_marketing["year_month"] = df_marketing["campaign_date"].dt.to_period("M")
    
    # Sum spend per region and year_month
    df_marketing_monthly = df_marketing.groupby(["region", "year_month"])["spend_amount"].sum().reset_index()
    df_marketing_monthly = df_marketing_monthly.rename(columns={"spend_amount": "total_regional_marketing_spend"})
    
    df_master = pd.merge(df_master, df_marketing_monthly, on=["region", "year_month"], how="left")
    df_master["total_regional_marketing_spend"] = df_master["total_regional_marketing_spend"].fillna(0)
    
    # Drop temp year_month column
    df_master = df_master.drop(columns=["year_month"])
    
    # 8. Feature Engineering and KPI Creation
    print("Calculating business KPIs and engineering features...")
    
    # 8.1 Revenue (validated as Sales Amount)
    # The sales_amount column represents the transaction value (Quantity * Selling Price * (1 - Discount))
    df_master["revenue"] = df_master["sales_amount"]
    
    # 8.2 Profit Margin %
    # Profit Margin % = profit / revenue
    df_master["profit_margin_pct"] = np.where(
        df_master["revenue"] > 0,
        df_master["profit"] / df_master["revenue"],
        0.0
    )
    
    # 8.3 Average Order Value (AOV), Repeat Purchase Rate, and Customer Lifetime Value (CLV)
    # We calculate these metrics at the customer level and join them back
    print("  Calculating Customer-level metrics...")
    
    # Group by customer_id
    cust_metrics = df_master.groupby("customer_id").agg(
        total_customer_revenue=("revenue", "sum"),
        total_customer_profit=("profit", "sum"),
        total_orders=("order_id", "nunique"),
        first_purchase_date=("order_date", "min"),
        last_purchase_date=("order_date", "max")
    ).reset_index()
    
    # Customer lifespan in years
    max_date = df_master["order_date"].max()
    cust_metrics["customer_lifespan_days"] = (cust_metrics["last_purchase_date"] - cust_metrics["first_purchase_date"]).dt.days
    cust_metrics["customer_lifespan_years"] = np.where(
        cust_metrics["customer_lifespan_days"] > 0,
        cust_metrics["customer_lifespan_days"] / 365.25,
        1.0 / 12.0 # minimum of 1 month
    )
    
    # Average Order Value (AOV)
    cust_metrics["average_order_value"] = cust_metrics["total_customer_revenue"] / cust_metrics["total_orders"]
    
    # Repeat Purchase Rate Flag
    cust_metrics["repeat_purchase_flag"] = np.where(cust_metrics["total_orders"] > 1, 1, 0)
    
    # Churn Flag: 1 if last purchase is > 180 days ago relative to dataset max_date
    cust_metrics["days_since_last_purchase"] = (max_date - cust_metrics["last_purchase_date"]).dt.days
    cust_metrics["churn_flag"] = np.where(cust_metrics["days_since_last_purchase"] > 180, 1, 0)
    
    # Customer Lifetime Value (CLV)
    # Formulated as: AOV * Purchase Frequency (orders per year) * Avg Profit Margin * Lifespan (years)
    # Which simplifies to historic cumulative net profit (clv_profit) or gross sales (clv_revenue)
    # We'll represent CLV as the cumulative historic gross revenue generated by the customer.
    cust_metrics["customer_lifetime_value"] = cust_metrics["total_customer_revenue"]
    
    # Merge customer-level metrics back into master dataset
    df_master = pd.merge(
        df_master, 
        cust_metrics[["customer_id", "average_order_value", "repeat_purchase_flag", "churn_flag", "customer_lifetime_value"]], 
        on="customer_id", 
        how="left"
    )
    
    # 8.4 Monthly Growth %
    print("  Calculating Monthly Growth %...")
    df_monthly = df_master.set_index("order_date").resample("ME")["revenue"].sum().reset_index()
    df_monthly["monthly_growth_pct"] = df_monthly["revenue"].pct_change()
    df_monthly["year_month"] = df_monthly["order_date"].dt.to_period("M")
    
    df_master["year_month"] = df_master["order_date"].dt.to_period("M")
    df_master = pd.merge(df_master, df_monthly[["year_month", "monthly_growth_pct"]], on="year_month", how="left")
    df_master["monthly_growth_pct"] = df_master["monthly_growth_pct"].fillna(0)
    df_master = df_master.drop(columns=["year_month"])
    
    # 8.5 Return Rate (at product and customer level)
    print("  Calculating Return Rates...")
    product_returns = df_master.groupby("product_id")["return_flag"].mean().rename("product_return_rate").reset_index()
    df_master = pd.merge(df_master, product_returns, on="product_id", how="left")
    
    # 8.6 Product Velocity Score
    # Product Velocity = Total Quantity Sold / Catalog Active Days
    print("  Calculating Product Velocity Scores...")
    prod_metrics = df_master.groupby("product_id").agg(
        total_qty=("quantity", "sum"),
        first_sale=("order_date", "min"),
        last_sale=("order_date", "max")
    ).reset_index()
    
    prod_metrics["active_days"] = (prod_metrics["last_sale"] - prod_metrics["first_sale"]).dt.days
    # Minimum of 1 day to avoid divide by zero
    prod_metrics["active_days"] = np.where(prod_metrics["active_days"] > 0, prod_metrics["active_days"], 1)
    prod_metrics["product_velocity_score"] = prod_metrics["total_qty"] / prod_metrics["active_days"]
    
    df_master = pd.merge(df_master, prod_metrics[["product_id", "product_velocity_score"]], on="product_id", how="left")
    
    # 9. Save output files
    print("Saving processed datasets to CSV...")
    # cleaned_data.csv: clean master orders (only primary and cleaning columns)
    cleaned_cols = [
        "order_id", "customer_id", "product_id", "quantity", "sales_amount", 
        "profit", "discount", "order_date", "return_flag"
    ]
    df_orders_cleaned = df_master[cleaned_cols].copy()
    df_orders_cleaned.to_csv("data/cleaned_data.csv", index=False)
    
    # master_dataset.csv: complete merged table with engineered features
    df_master.to_csv("data/master_dataset.csv", index=False)
    
    print(f"Cleaned orders dataset dimensions: {df_orders_cleaned.shape}")
    print(f"Master dataset dimensions: {df_master.shape}")
    print("\n--- Phase 2 Completed: Data cleaning and feature engineering finished successfully! ---")

if __name__ == "__main__":
    main()
