import os
import urllib.request
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Create data directory if not exists
os.makedirs("data", exist_ok=True)

# Sources of Sample Superstore dataset
URLS = [
    "https://raw.githubusercontent.com/eyowhite/Data-Analysis/main/Sample%20-%20Superstore.csv",
    "https://raw.githubusercontent.com/aditya-y/Retail-Store-Analysis-Python/master/SampleSuperstore.csv",
    "https://raw.githubusercontent.com/tushar-ry/Superstore-Sales-Analysis/main/Sample%20-%20Superstore.csv"
]

def download_superstore():
    """Downloads the Superstore dataset from available mirrors."""
    for url in URLS:
        try:
            print(f"Attempting to download dataset from: {url}")
            # Use urllib to request with a standard user-agent to bypass blockages
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req) as response:
                content = response.read()
                # Determine encoding
                for encoding in ['utf-8', 'latin1', 'cp1252']:
                    try:
                        decoded = content.decode(encoding)
                        # Write local copy
                        raw_path = "data/raw_superstore.csv"
                        with open(raw_path, "w", encoding="utf-8") as f:
                            f.write(decoded)
                        print("Download successful!")
                        return pd.read_csv(raw_path)
                    except Exception:
                        continue
        except Exception as e:
            print(f"Failed download from {url}: {e}")
    return None

def generate_synthetic_superstore(num_records=9994):
    """Generates a high-quality synthetic fallback dataset resembling Superstore."""
    print("Generating high-fidelity synthetic fallback dataset...")
    np.random.seed(42)
    
    categories = {
        "Furniture": ["Bookcases", "Chairs", "Labels", "Tables", "Furnishings"],
        "Office Supplies": ["Appliances", "Art", "Envelopes", "Fasteners", "Paper", "Storage", "Supplies", "Binders"],
        "Technology": ["Phones", "Copiers", "Accessories", "Machines"]
    }
    
    regions = {
        "East": [("New York", "New York"), ("Massachusetts", "Boston"), ("Pennsylvania", "Philadelphia")],
        "West": [("California", "Los Angeles"), ("California", "San Francisco"), ("Washington", "Seattle")],
        "Central": [("Illinois", "Chicago"), ("Texas", "Houston"), ("Texas", "Dallas")],
        "South": [("Florida", "Miami"), ("Georgia", "Atlanta"), ("North Carolina", "Charlotte")]
    }
    
    # Generate static products catalog (approx 500 items)
    products = []
    for i in range(500):
        cat = np.random.choice(list(categories.keys()))
        subcat = np.random.choice(categories[cat])
        prod_id = f"{cat[:3]}-{subcat[:3]}-{10000000 + i}"
        prod_name = f"Retail {subcat[:-1] if subcat.endswith('s') else subcat} Product v{i}"
        base_price = round(np.random.exponential(50.0) + 5.0, 2)
        products.append((prod_id, prod_name, cat, subcat, base_price))
        
    # Generate customers catalog (approx 800 items)
    first_names = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles",
                   "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                  "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
    
    customers = []
    for i in range(800):
        cust_id = f"{chr(65 + i % 26)}{chr(65 + (i // 26) % 26)}-{10000 + i}"
        name = f"{np.random.choice(first_names)} {np.random.choice(last_names)}"
        gender = np.random.choice(["Male", "Female"], p=[0.48, 0.52])
        age = int(np.random.normal(42, 12))
        age = max(18, min(80, age))
        reg_year = np.random.choice([2022, 2023, 2024])
        reg_date = datetime(reg_year, np.random.randint(1, 13), np.random.randint(1, 28))
        customers.append((cust_id, name, gender, age, reg_date))
        
    # Build order dataset
    order_records = []
    start_date = datetime(2023, 1, 1)
    
    for i in range(num_records):
        order_id = f"CA-2023-{100000 + i}" if i % 2 == 0 else f"US-2024-{100000 + i}"
        cust_idx = np.random.randint(len(customers))
        cust = customers[cust_idx]
        
        reg_date = cust[4]
        order_date = reg_date + timedelta(days=np.random.randint(1, 800))
        # Cap date to present
        if order_date > datetime(2026, 6, 1):
            order_date = datetime(2026, 6, 1) - timedelta(days=np.random.randint(0, 30))
            
        ship_date = order_date + timedelta(days=np.random.randint(2, 6))
        ship_mode = np.random.choice(["Second Class", "Standard Class", "First Class", "Same Day"], p=[0.2, 0.6, 0.15, 0.05])
        
        # Pick region and matching state/city
        region = np.random.choice(list(regions.keys()))
        state_city = np.random.choice(len(regions[region]))
        state, city = regions[region][state_city]
        
        # Select 1 to 4 products per order
        num_items = np.random.randint(1, 5)
        for _ in range(num_items):
            prod = products[np.random.randint(len(products))]
            prod_id, prod_name, cat, subcat, selling_price = prod
            
            qty = int(np.random.choice([1, 2, 3, 4, 5, 7, 10], p=[0.3, 0.3, 0.15, 0.1, 0.08, 0.05, 0.02]))
            discount = np.random.choice([0.0, 0.1, 0.2, 0.45, 0.7, 0.8], p=[0.7, 0.05, 0.15, 0.05, 0.03, 0.02])
            
            # Profit calculation: Sales Amount = selling_price * qty * (1 - discount)
            # Cost price is synthetic but lower than selling price
            cost_price = round(selling_price * 0.6, 2)
            sales = round(selling_price * qty * (1 - discount), 2)
            profit = round(sales - (cost_price * qty), 2)
            
            order_records.append({
                "Row ID": i + 1,
                "Order ID": order_id,
                "Order Date": order_date.strftime("%Y-%m-%d"),
                "Ship Date": ship_date.strftime("%Y-%m-%d"),
                "Ship Mode": ship_mode,
                "Customer ID": cust[0],
                "Customer Name": cust[1],
                "Segment": np.random.choice(["Consumer", "Corporate", "Home Office"], p=[0.5, 0.3, 0.2]),
                "Country": "United States",
                "City": city,
                "State": state,
                "Postal Code": np.random.randint(10000, 99999),
                "Region": region,
                "Product ID": prod_id,
                "Category": cat,
                "Sub-Category": subcat,
                "Product Name": prod_name,
                "Sales": sales,
                "Quantity": qty,
                "Discount": discount,
                "Profit": profit
            })
            
    df = pd.DataFrame(order_records)
    df.to_csv("data/raw_superstore.csv", index=False, encoding="utf-8")
    return df

def generate_marketing_spend(region_df, start_date, end_date):
    """Generates synthetic regional marketing spend data."""
    print("Generating marketing spend dataset...")
    regions = region_df["Region"].unique()
    campaigns = ["Social Media", "PPC", "Email", "Influencer"]
    
    marketing_records = []
    current_date = start_date
    np.random.seed(101)
    
    while current_date <= end_date:
        for region in regions:
            for camp in campaigns:
                # Add regional seasonality and scale
                base_spend = {
                    "West": 1500,
                    "East": 1400,
                    "Central": 1000,
                    "South": 800
                }.get(region, 1000)
                
                spend = round(base_spend * np.random.uniform(0.7, 1.3), 2)
                # Boost during holiday season (Nov/Dec)
                if current_date.month in [11, 12]:
                    spend = round(spend * 1.5, 2)
                    
                marketing_records.append({
                    "Region": region,
                    "Campaign Type": camp,
                    "Spend Amount": spend,
                    "Campaign Date": current_date.strftime("%Y-%m-%d")
                })
        # Move to next month
        if current_date.month == 12:
            current_date = datetime(current_date.year + 1, 1, 1)
        else:
            current_date = datetime(current_date.year, current_date.month + 1, 1)
            
    df_marketing = pd.DataFrame(marketing_records)
    df_marketing.to_csv("data/marketing_spend_data.csv", index=False)
    return df_marketing

def main():
    print("--- Starting Phase 1: Data Collection & Ingestion ---")
    
    # Step 1: Download or generate raw superstore dataset
    df_raw = download_superstore()
    if df_raw is None:
        df_raw = generate_synthetic_superstore()
        
    print(f"Raw Superstore dataset dimensions: {df_raw.shape}")
    
    # Step 2: Set Random Seeds for repeatability
    np.random.seed(42)
    
    # Step 3: Extract & Build Normalized Tables
    
    # 3.1 Region Data
    print("Creating Region Data Table...")
    df_region = df_raw[["Region", "State", "City"]].drop_duplicates().reset_index(drop=True)
    df_region.to_csv("data/region_data.csv", index=False)
    print(f"Region Data: {df_region.shape[0]} unique locations.")
    
    # 3.2 Customer Data
    print("Creating Customer Data Table...")
    df_cust_base = df_raw[["Customer ID", "Customer Name", "City", "Region"]].drop_duplicates("Customer ID").reset_index(drop=True)
    
    # Enrich with Gender, Age, and Registration Date
    first_names = df_cust_base["Customer Name"].apply(lambda x: x.split()[0] if isinstance(x, str) else "")
    # Rough gender heuristics
    female_indicators = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen",
                         "Nancy", "Lisa", "Betty", "Margaret", "Sandra", "Ashley", "Kimberly", "Emily", "Donna", "Michelle",
                         "Carol", "Amanda", "Dorothy", "Melissa", "Deborah", "Stephanie", "Rebecca", "Sharon", "Laura", "Cynthia"]
    
    genders = []
    ages = []
    reg_dates = []
    
    # Get the earliest order date for each customer
    df_raw["Order Date"] = pd.to_datetime(df_raw["Order Date"])
    earliest_orders = df_raw.groupby("Customer ID")["Order Date"].min().to_dict()
    
    for idx, row in df_cust_base.iterrows():
        name = row["Customer Name"]
        fname = name.split()[0] if isinstance(name, str) else ""
        gender = "Female" if fname in female_indicators or np.random.rand() > 0.5 else "Male"
        genders.append(gender)
        
        # Age distribution
        age = int(np.random.normal(44, 13))
        age = max(18, min(82, age))
        ages.append(age)
        
        # Registration date: 30 to 730 days before their first purchase
        first_purchase = earliest_orders.get(row["Customer ID"], datetime(2024, 1, 1))
        reg_date = first_purchase - timedelta(days=np.random.randint(30, 730))
        reg_dates.append(reg_date.strftime("%Y-%m-%d"))
        
    df_customer = pd.DataFrame({
        "Customer ID": df_cust_base["Customer ID"],
        "Name": df_cust_base["Customer Name"],
        "Gender": genders,
        "Age": ages,
        "City": df_cust_base["City"],
        "Region": df_cust_base["Region"],
        "Registration Date": reg_dates
    })
    df_customer.to_csv("data/customer_data.csv", index=False)
    print(f"Customer Data: {df_customer.shape[0]} unique customers.")
    
    # 3.3 Product Data
    print("Creating Product Data Table...")
    df_prod_base = df_raw[["Product ID", "Product Name", "Category", "Sub-Category"]].drop_duplicates("Product ID").reset_index(drop=True)
    df_prod_base = df_prod_base.rename(columns={"Sub-Category": "Sub-category"})
    
    # Find base prices from transaction data
    # We estimate the standard Unit Selling Price as the median Sales / Quantity for each Product ID
    df_raw["Unit_Price"] = df_raw["Sales"] / df_raw["Quantity"]
    median_prices = df_raw.groupby("Product ID")["Unit_Price"].median().to_dict()
    
    selling_prices = []
    cost_prices = []
    
    for idx, row in df_prod_base.iterrows():
        pid = row["Product ID"]
        sel_price = round(median_prices.get(pid, np.random.uniform(5.0, 500.0)), 2)
        selling_prices.append(sel_price)
        
        # Cost Price: Base profit margins vary by category
        cat = row["Category"]
        margin_factors = {
            "Technology": 0.40,
            "Office Supplies": 0.50,
            "Furniture": 0.25
        }
        margin = margin_factors.get(cat, 0.35) * np.random.uniform(0.8, 1.2)
        cost_price = round(sel_price * (1 - margin), 2)
        cost_prices.append(cost_price)
        
    df_product = pd.DataFrame({
        "Product ID": df_prod_base["Product ID"],
        "Product Name": df_prod_base["Product Name"],
        "Category": df_prod_base["Category"],
        "Sub-category": df_prod_base["Sub-category"],
        "Cost Price": cost_prices,
        "Selling Price": selling_prices
    })
    df_product.to_csv("data/product_data.csv", index=False)
    print(f"Product Data: {df_product.shape[0]} unique products.")
    
    # 3.4 Orders Data
    print("Creating Orders Data Table...")
    # Map Orders to specific columns requested in Phase 1
    # Orders Data: Order ID, Customer ID, Product ID, Quantity, Sales Amount, Profit, Discount, Order Date
    df_orders = df_raw[["Order ID", "Customer ID", "Product ID", "Quantity", "Sales", "Profit", "Discount", "Order Date"]].copy()
    df_orders = df_orders.rename(columns={"Sales": "Sales Amount"})
    df_orders["Order Date"] = pd.to_datetime(df_orders["Order Date"]).dt.strftime("%Y-%m-%d")
    df_orders.to_csv("data/orders_data.csv", index=False)
    print(f"Orders Data: {df_orders.shape[0]} transaction items.")
    
    # 3.5 Marketing Spend Data
    print("Creating Marketing Spend Data Table...")
    min_date = df_raw["Order Date"].min()
    max_date = df_raw["Order Date"].max()
    df_marketing = generate_marketing_spend(df_region, min_date, max_date)
    print(f"Marketing Spend: {df_marketing.shape[0]} monthly regional records.")
    
    print("\n--- Phase 1 Completed: Data collection and normalization finished successfully! ---")

if __name__ == "__main__":
    main()
