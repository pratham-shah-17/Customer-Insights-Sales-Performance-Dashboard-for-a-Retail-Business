# Customer Insights & Sales Performance Dashboard for a Retail Business
*A Production-Grade, End-to-End Enterprise Analytics and Predictive Decision-Support System*

---

## 📋 Project Overview
This repository contains a complete, industry-standard data analytics capstone project designed to optimize operations, customer retention, inventory levels, and marketing budgets for a retail business. 

The system normalizes raw transaction logs (based on the popular retail "Superstore" dataset) into a relational database model, performs preprocessing and feature engineering in Pandas, conducts exploratory data analysis, trains machine learning models, programmatically generates business insights, and delivers both a Power BI Star Schema specification and an interactive Streamlit web dashboard.

---

## 🛠️ Project Architecture & Directory Structure
```
├── data/
│   ├── raw_superstore.csv             # Ingested raw transactional logs
│   ├── customer_data.csv              # Normalized customer profiles with demographics
│   ├── orders_data.csv                # Normalized order-line transactions
│   ├── product_data.csv               # Normalized catalog products with pricing metrics
│   ├── region_data.csv                # Normalized regional geographics mapping
│   ├── marketing_spend_data.csv       # Monthly regional campaign expenditures
│   ├── cleaned_data.csv               # Cleaned transaction table
│   ├── master_dataset.csv             # Merged analytical master dataset with features
│   ├── rfm_customer_segments.csv      # RFM Customer loyalty segments
│   ├── customer_risk_predictions.csv  # Churn risk classifications and probabilities
│   ├── sales_future_forecast.csv      # 12-month time-series sales projections
│   └── inventory_recommendations.csv  # Optimal safety stock and reorder point limits
├── models/
│   ├── sales_forecast_model.pkl       # Saved time-series forecasting model
│   └── customer_churn_model.pkl       # Saved customer churn classifier model
├── src/
│   ├── data_ingestion.py              # Normalized relational tables ingestion
│   ├── data_cleaning.py               # Preprocessing, joins, and feature engineering
│   ├── eda_engine.py                  # Exploratory plotting and RFM segmentation
│   ├── ml_pipeline.py                 # ML training (Sales forecast, Churn, Demand)
│   ├── insights_engine.py             # 20 Business rule diagnostics and ROI reports
│   └── streamlit_app.py               # Streamlit responsive frontend dashboard
├── static/
│   └── charts/                        # Saved PNG and HTML interactive EDA plots
├── reports/
│   ├── data_dictionary.md             # Variable explanations and data types
│   ├── powerbi_specs.md               # Power BI Star Schema and copy-paste DAX formulas
│   ├── business_insights_report.md    # Automated strategic recommendations report
│   ├── installation_guide.md          # Comprehensive deployment steps
│   └── project_report.md              # 45-page capstone thesis project report
├── presentation/
│   ├── final_presentation.md          # 18-slide presentation deck outline
│   ├── final_presentation.pptx        # Programmatically compiled slide deck
│   └── generate_ppt.py                # Python slide deck compiler script
├── requirements.txt                   # Dependency list
└── README.md                          # Startup and operational handbook
```

---

## 🚀 Setup & Execution Guide (Local Environment)

### Prerequisites
* Python 3.9, 3.10, or 3.11 installed.
* Standard Python package manager (`pip`) updated.

### Step 1: Install Dependencies
Open your command terminal in the project directory and run:
```bash
pip install -r requirements.txt
```

### Step 2: Execute the Analytics Pipeline
The analytical backend runs sequentially. To ingest, clean, segment, model, and analyze the dataset, run each pipeline script in order:

```bash
# 1. Ingest baseline dataset and split into normalized structures
python src/data_ingestion.py

# 2. Clean, deduplicate, and calculate metrics (CLV, Repeat rate, etc.)
python src/data_cleaning.py

# 3. Generate static/interactive EDA plots and calculate RFM segments
python src/eda_engine.py

# 4. Train forecasting, churn, and inventory models
python src/ml_pipeline.py

# 5. Programmatically evaluate business rules and output ROI impacts
python src/insights_engine.py
```

### Step 3: Run the Streamlit Dashboard
Launch the interactive web application to access metric overview cards, customer profiles, risk metrics, and time-series forecasts:
```bash
streamlit run src/streamlit_app.py
```
The application will open in a new tab in your default web browser (typically at `http://localhost:8501`).

### Step 4: Compile the Presentation Slide Deck
To generate the PowerPoint presentation `presentation/final_presentation.pptx` using python-pptx:
```bash
python presentation/generate_ppt.py
```

---

## 📊 Power BI Dashboard Implementation
To implement the Power BI reporting layer:
1. Load the five raw tables inside the `data/` folder (`customer_data.csv`, `orders_data.csv`, `product_data.csv`, `region_data.csv`, `marketing_spend_data.csv`) into **Power BI Desktop**.
2. Go to the **Model** tab and connect the tables in a **Star Schema** as detailed in [reports/powerbi_specs.md](file:///C:/Users/Pratham/Desktop/AI%20startup%20founder%20Simulator/reports/powerbi_specs.md).
3. Create a **Date Table** (`DateTable`) and mark it as the Date Table.
4. Copy-paste the DAX formulas provided in the manual to create measures for Total Revenue, Total Profit, AOV, MoM Growth %, Repeat Purchase Rate, Churn Rate %, Return Rate %, and CLV.
5. Set up dashboard visuals matching the guide templates.

---

## ☁️ Deployment Guide (Streamlit Sharing / Cloud Platforms)

### Streamlit Sharing
1. Push this project folder to your public repository on **GitHub**.
2. Log into [Streamlit Community Cloud](https://share.streamlit.io/).
3. Click **New App**, select your repository, branch, and specify the main path as `src/streamlit_app.py`.
4. Click **Deploy**. Streamlit Cloud will automatically build your environment from `requirements.txt`.
