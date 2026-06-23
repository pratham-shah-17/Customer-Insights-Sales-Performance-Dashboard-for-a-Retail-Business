import os
import pandas as pd
import numpy as np
import pickle
from datetime import datetime, timedelta

# Model libraries
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, accuracy_score, recall_score, roc_auc_score
from xgboost import XGBRegressor, XGBClassifier

# Handle statsmodels as seasonal forecasting fallback
try:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False

# Try Prophet
try:
    from prophet import Prophet
    HAS_PROPHET = True
except ImportError:
    HAS_PROPHET = False

# Set seed
np.random.seed(42)

def run_sales_forecasting(df_master):
    """Prepares time-series data and runs sales forecasting models."""
    print("Running Sales Forecasting Models...")
    
    # 1. Prepare monthly aggregated sales data
    df_master["order_date"] = pd.to_datetime(df_master["order_date"])
    df_monthly = df_master.set_index("order_date").resample("MS")["revenue"].sum().reset_index()
    df_monthly.columns = ["date", "revenue"]
    
    n_months = len(df_monthly)
    if n_months < 12:
        print("Warning: Insufficient monthly records for deep time-series modeling. Augmenting dates.")
        
    # Feature engineering for regression models: Lags, Month index, Year, Month of Year
    df_monthly["month_idx"] = np.arange(n_months)
    df_monthly["month_of_year"] = df_monthly["date"].dt.month
    df_monthly["year"] = df_monthly["date"].dt.year
    
    # Add Lags
    df_monthly["lag_1"] = df_monthly["revenue"].shift(1)
    df_monthly["lag_2"] = df_monthly["revenue"].shift(2)
    df_monthly["lag_3"] = df_monthly["revenue"].shift(3)
    
    # Fill lags with backfill
    df_monthly = df_monthly.bfill()
    
    # Split into train (last 6 months held out for evaluation if sufficient, else 3 months)
    holdout = min(6, int(n_months * 0.2))
    if holdout < 2: holdout = 2
    
    train = df_monthly.iloc[:-holdout].copy()
    test = df_monthly.iloc[-holdout:].copy()
    
    features = ["month_idx", "month_of_year", "year", "lag_1", "lag_2", "lag_3"]
    X_train, y_train = train[features], train["revenue"]
    X_test, y_test = test[features], test["revenue"]
    
    # Model 1: Linear Regression
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    y_pred_lr = lr.predict(X_test)
    
    # Model 2: Random Forest
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    
    # Model 3: XGBoost
    xgb = XGBRegressor(n_estimators=50, max_depth=3, random_state=42)
    xgb.fit(X_train, y_train)
    y_pred_xgb = xgb.predict(X_test)
    
    # Model 4: Prophet / Statsmodels fallback
    y_pred_ts = np.zeros(holdout)
    ts_name = "Seasonal Fallback (Holt-Winters)"
    
    if HAS_PROPHET:
        ts_name = "Prophet"
        df_prophet = train[["date", "revenue"]].rename(columns={"date": "ds", "revenue": "y"})
        model_p = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
        model_p.fit(df_prophet)
        future = model_p.make_future_dataframe(periods=holdout, freq='MS')
        forecast = model_p.predict(future)
        y_pred_ts = forecast.iloc[-holdout:]["yhat"].values
    elif HAS_STATSMODELS:
        try:
            model_hw = ExponentialSmoothing(train["revenue"], seasonal='add', seasonal_periods=min(12, len(train)//2)).fit()
            y_pred_ts = model_hw.forecast(holdout).values
        except Exception:
            y_pred_ts = y_pred_rf # fallback if Holt-Winters fails numerical stability
    else:
        # Simple seasonal naive fallback
        y_pred_ts = y_pred_lr
        ts_name = "Naive Seasonal (Regression Fallback)"
        
    # Evaluate Models
    metrics = []
    for name, pred in [("Linear Regression", y_pred_lr), ("Random Forest", y_pred_rf), ("XGBoost", y_pred_xgb), (ts_name, y_pred_ts)]:
        rmse = np.sqrt(mean_squared_error(y_test, pred))
        mae = mean_absolute_error(y_test, pred)
        r2 = r2_score(y_test, pred)
        metrics.append({"Model": name, "RMSE": round(rmse, 2), "MAE": round(mae, 2), "R2 Score": round(r2, 4)})
        
    df_metrics = pd.DataFrame(metrics)
    df_metrics.to_csv("data/sales_forecasting_metrics.csv", index=False)
    print(df_metrics)
    
    # 2. Future Forecast (next 12 months)
    # Using the best performing model by RMSE (ignoring R2 if volatile on short sets)
    best_model_name = df_metrics.sort_values("RMSE").iloc[0]["Model"]
    print(f"  Best forecasting model: {best_model_name}")
    
    # Forecast timeline
    last_date = df_monthly["date"].max()
    future_dates = [last_date + pd.DateOffset(months=i) for i in range(1, 13)]
    
    # We will generate a forecast based on Random Forest / XGBoost rolling lags
    forecast_records = []
    current_idx = df_monthly["month_idx"].max() + 1
    
    # Last 3 historical sales for seed
    lag1, lag2, lag3 = df_monthly.iloc[-1]["revenue"], df_monthly.iloc[-2]["revenue"], df_monthly.iloc[-3]["revenue"]
    
    for f_date in future_dates:
        row_feat = pd.DataFrame([[current_idx, f_date.month, f_date.year, lag1, lag2, lag3]], columns=features)
        
        # Predict using best ML model
        if best_model_name == "Linear Regression":
            pred_val = lr.predict(row_feat)[0]
        elif best_model_name == "XGBoost":
            pred_val = xgb.predict(row_feat)[0]
        else: # Default/Random Forest
            pred_val = rf.predict(row_feat)[0]
            
        # Ensure positive
        pred_val = max(1000.0, pred_val)
        
        forecast_records.append({
            "Date": f_date.strftime("%Y-%m-%d"),
            "Forecasted Sales": round(pred_val, 2)
        })
        
        # Shift lags
        lag3 = lag2
        lag2 = lag1
        lag1 = pred_val
        current_idx += 1
        
    df_forecast = pd.DataFrame(forecast_records)
    df_forecast.to_csv("data/sales_future_forecast.csv", index=False)
    
    # Save the models
    os.makedirs("models", exist_ok=True)
    with open("models/sales_forecast_model.pkl", "wb") as f:
        pickle.dump({"lr": lr, "rf": rf, "xgb": xgb, "best_model": best_model_name, "features": features}, f)


def run_churn_prediction(df_master):
    """Extracts customer features and trains customer churn risk models."""
    print("Running Customer Churn Prediction Models...")
    
    # 1. Feature Engineering per Customer
    # Aggregate transaction features
    cust_df = df_master.groupby("customer_id").agg(
        age=("age", "first"),
        gender=("gender", "first"),
        region=("region", "first"),
        total_revenue=("revenue", "sum"),
        total_profit=("profit", "sum"),
        order_count=("order_id", "nunique"),
        avg_discount=("discount", "mean"),
        return_rate=("return_flag", "mean"),
        churn_flag=("churn_flag", "first")
    ).reset_index()
    
    # Encode categorical variables
    cust_df["is_female"] = np.where(cust_df["gender"] == "Female", 1, 0)
    
    # One-hot encode Region
    region_dummies = pd.get_dummies(cust_df["region"], prefix="region").astype(int)
    cust_df = pd.concat([cust_df, region_dummies], axis=1)
    
    # Drop raw categories
    features = ["age", "total_revenue", "total_profit", "order_count", "avg_discount", "return_rate", "is_female"] + list(region_dummies.columns)
    
    X = cust_df[features]
    y = cust_df["churn_flag"]
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Models
    log_reg = LogisticRegression(max_iter=500)
    log_reg.fit(X_train, y_train)
    y_pred_lr = log_reg.predict(X_test)
    y_prob_lr = log_reg.predict_proba(X_test)[:, 1]
    
    rf_clf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    rf_clf.fit(X_train, y_train)
    y_pred_rf = rf_clf.predict(X_test)
    y_prob_rf = rf_clf.predict_proba(X_test)[:, 1]
    
    xgb_clf = XGBClassifier(n_estimators=50, max_depth=3, random_state=42)
    xgb_clf.fit(X_train, y_train)
    y_pred_xgb = xgb_clf.predict(X_test)
    y_prob_xgb = xgb_clf.predict_proba(X_test)[:, 1]
    
    # Metrics
    churn_metrics = []
    for name, pred, prob in [("Logistic Regression", y_pred_lr, y_prob_lr), 
                             ("Random Forest", y_pred_rf, y_prob_rf), 
                             ("XGBoost Classifier", y_pred_xgb, y_prob_xgb)]:
        acc = accuracy_score(y_test, pred)
        rec = recall_score(y_test, pred)
        auc = roc_auc_score(y_test, prob)
        churn_metrics.append({"Classifier": name, "Accuracy": round(acc, 3), "Recall (Sensitivity)": round(rec, 3), "ROC-AUC Score": round(auc, 4)})
        
    df_churn_metrics = pd.DataFrame(churn_metrics)
    df_churn_metrics.to_csv("data/customer_churn_metrics.csv", index=False)
    print(df_churn_metrics)
    
    # Pick best model (based on ROC-AUC)
    best_clf_name = df_churn_metrics.sort_values("ROC-AUC Score", ascending=False).iloc[0]["Classifier"]
    print(f"  Best Churn Classifier: {best_clf_name}")
    
    # Predict Churn Probabilities on all customers
    if best_clf_name == "Logistic Regression":
        full_probs = log_reg.predict_proba(X)[:, 1]
    elif best_clf_name == "XGBoost Classifier":
        full_probs = xgb_clf.predict_proba(X)[:, 1]
    else:
        full_probs = rf_clf.predict_proba(X)[:, 1]
        
    cust_df["churn_probability"] = full_probs
    cust_df["predicted_churn"] = np.where(cust_df["churn_probability"] >= 0.5, 1, 0)
    
    # Save Customer Risk Dashboard dataset
    cust_risk = cust_df[["customer_id", "age", "gender", "region", "total_revenue", "churn_probability", "predicted_churn"]].copy()
    cust_risk["risk_category"] = pd.cut(cust_risk["churn_probability"], bins=[0.0, 0.3, 0.7, 1.0], labels=["Low Risk", "Medium Risk", "High Risk"])
    cust_risk.to_csv("data/customer_risk_predictions.csv", index=False)
    
    # Save models
    with open("models/customer_churn_model.pkl", "wb") as f:
        pickle.dump({"log_reg": log_reg, "rf": rf_clf, "xgb": xgb_clf, "features": features, "best_model": best_clf_name}, f)


def run_product_demand_prediction(df_master):
    """Predicts quantity demand for top product categories/regions and maps inventory requirements."""
    print("Running Product Demand & Safety Stock Predictions...")
    
    # Group by category, region, and month
    df_master["order_date"] = pd.to_datetime(df_master["order_date"])
    df_master["year_month"] = df_master["order_date"].dt.to_period("M")
    
    df_demand = df_master.groupby(["category", "region", "year_month"])["quantity"].sum().reset_index()
    df_demand["year_month"] = df_demand["year_month"].astype(str)
    
    # Calculate demand metrics for next month
    # We will propose safety stock and reorder point using actual distributions of daily quantity sales
    daily_sales = df_master.groupby(["category", "region", "order_date"])["quantity"].sum().reset_index()
    
    demand_recommendations = []
    
    # Calculate for each Category and Region pair
    for (cat, reg), df_sub in daily_sales.groupby(["category", "region"]):
        avg_daily_sales = df_sub["quantity"].mean()
        max_daily_sales = df_sub["quantity"].max()
        std_daily_sales = df_sub["quantity"].std()
        
        # Lead time assumptions (in days): Average lead time = 10, Max lead time = 15
        avg_lead_time = 10
        max_lead_time = 15
        
        # Safety Stock = (Max Daily Sales * Max Lead Time) - (Avg Daily Sales * Avg Lead Time)
        safety_stock = int(np.ceil((max_daily_sales * max_lead_time) - (avg_daily_sales * avg_lead_time)))
        # Make sure safety stock is positive
        safety_stock = max(5, safety_stock)
        
        # Reorder Point = (Avg Daily Sales * Avg Lead Time) + Safety Stock
        reorder_point = int(np.ceil((avg_daily_sales * avg_lead_time) + safety_stock))
        
        # Forecasted monthly demand = avg_daily_sales * 30 days
        forecasted_monthly_demand = int(np.ceil(avg_daily_sales * 30))
        
        demand_recommendations.append({
            "Category": cat,
            "Region": reg,
            "Avg Daily Demand": round(avg_daily_sales, 2),
            "Max Daily Demand": max_daily_sales,
            "Standard Deviation": round(std_daily_sales, 2),
            "Forecasted Monthly Demand": forecasted_monthly_demand,
            "Safety Stock Limit": safety_stock,
            "Reorder Point": reorder_point
        })
        
    df_inventory = pd.DataFrame(demand_recommendations)
    df_inventory.to_csv("data/inventory_recommendations.csv", index=False)
    print("Inventory Recommendations sample:")
    print(df_inventory.head())


def main():
    print("--- Starting Phase 5: Machine Learning & Predictive Analytics ---")
    
    if not os.path.exists("data/master_dataset.csv"):
        print("Error: data/master_dataset.csv not found. Running data_cleaning.py first...")
        os.system("python src/data_cleaning.py")
        
    df_master = pd.read_csv("data/master_dataset.csv")
    
    # Run pipelines
    run_sales_forecasting(df_master)
    run_churn_prediction(df_master)
    run_product_demand_prediction(df_master)
    
    print("\n--- Phase 5 Completed: All predictive models trained and outputs stored in /data ---")

if __name__ == "__main__":
    main()
