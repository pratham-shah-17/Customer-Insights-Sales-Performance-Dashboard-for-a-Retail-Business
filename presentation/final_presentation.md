# Customer Insights & Sales Performance Dashboard for a Retail Business
*Executive Presentation Deck for Final-Year Data Analytics Evaluation*

---

## Slide 1: Project Title & Overview
### Strategic Retail Operations & Customer Intelligence
* **Presenter**: Pratham
* **Role**: Lead Data Analyst & BI Developer
* **Project Scope**: End-to-end data pipeline, predictive modeling, and executive-level BI dashboard for a multi-regional retail corporation.
* **Key Components**: Relational data modeling, Pandas cleaning pipeline, Plotly & Seaborn EDA, ML forecasting, and a Streamlit decision-support web application.

---

## Slide 2: The Business Problem
### Underoptimized Marketing, Customer Retention, & Inventory Leakages
* **Customer Retention Churn**: High customer acquisition costs coupled with lack of demographic insights make retaining customers highly difficult.
* **Margin Erosion**: Uncontrolled discounting practices (often exceeding 50%) eat away at regional margins, turning high-revenue sub-categories unprofitable.
* **Inventory Mismanagement**: Heavy holding costs for dead stock coexist with stockouts of high-velocity technology items.
* **Information Silos**: Transactional databases are disconnected from marketing spend data, rendering ROI calculations impossible.

---

## Slide 3: Project Objectives
### Establishing a Data-Driven Retail Ecosystem
1. **Consolidate Relational Schema**: Normalize and enrich transactional data with customer demographics and monthly regional marketing campaigns.
2. **Standardize Cleaning Pipeline**: Automate data deduplication, handle outlier transactions via IQR, and engineer business KPIs.
3. **Execute RFM Customer Segmentation**: Segment the user base into distinct profiles to trigger targeted marketing.
4. **Build Predictive Engines**: Implement ML classifiers and regressors to forecast future sales, customer churn probabilities, and category demand levels.
5. **Deliver Streamlit Frontend & Power BI Specs**: Enable self-service forecasting, risk profiling, and executive reporting.

---

## Slide 4: Dataset Overview (Data Model)
### Relational Schema Definition
* **Unified Database Model**:
  * **Customer Data** (800 profiles): ID, Name, Gender, Age, City, Region, Registration Date.
  * **Orders Data** (9,994 entries): ID, Customer ID, Product ID, Quantity, Sales, Profit, Discount, Date.
  * **Product Data** (1,850 catalog items): ID, Name, Category, Sub-category, Cost Price, Selling Price.
  * **Region Data**: Regional normalization mapping Region, State, and City.
  * **Marketing Spend Data** (monthly regional): Region, Campaign Type, Spend Amount, Date.
* **Data Sources**: Sample Superstore transactional records supplemented with synthetic demographic and marketing spend data.

---

## Slide 5: Data Cleaning & Preprocessing Process
### Data Pipeline Integrity (Python & Pandas)
* **Deduplication**: Isolated and removed duplicate order and customer records.
* **Missing Value Treatment**: Imputed blank customer names and verified catalog dimensions.
* **Outlier Profiling (IQR)**: Flagged high-volume outliers (using 1.5 * IQR) in Sales and Profit to prevent training skew.
* **Date Parsing & Type Casting**: Standardized dates to `datetime64` and float types.
* **Standardized Schema**: Applied `snake_case` column naming convention across all components.

---

## Slide 6: Sales Performance Analysis
### Revenue and Margin Trends
* **Monthly sales trends**: Seasonal sales peaks during Q4 holidays (Nov-Dec) representing a ~35% surge.
* **Regional Distribution**: The West region leads in sales contribution, followed closely by the East, while the South underperforms.
* **Discount Impact**: Transactions with discounts exceeding 20% show negative average profits, illustrating severe margin erosion.
* **Product Concentration**: Top 20 products contribute to a disproportionate 15% of total sales volume.

---

## Slide 7: Customer Demographics & RFM Analysis
### Customer Cohort Segmentation
* **RFM Segments**:
  * **Champions**: Highly recent, high-frequency, and high-spending customers (~15% of customer base).
  * **Loyal Customers**: Purchase regularly, highly responsive to promotions.
  * **Potential Loyalists**: Recent buyers with moderate spending; prime candidates for cross-selling.
  * **At Risk**: High historical spend but no purchases in the last 180 days.
  * **Lost Customers**: Dormant, low frequency, low monetary profiles.
* **Demographic findings**: Customer purchase frequency correlates positively with the 30-45 age group.

---

## Slide 8: Product Performance Insights
### Margin Profiling and Velocity
* **Fast-moving products**: Technology sub-categories (Phones, Accessories) represent the highest daily velocity scores.
* **Dead Stock**: Products with velocity scores < 0.05 units/day are flagged, representing locked-up capital.
* **High Margin Categories**: Technology and Office Supplies maintain stable average margins of 40-50%.
* **Low Margin Sub-categories**: Furniture sub-categories (specifically Tables and Bookcases) exhibit net losses due to high shipping expenses and high discounts.

---

## Slide 9: Executive Dashboard Layout & Star Schema
### Power BI Reporting Architecture
* **Dashboard Pages**:
  * **Page 1: Executive Overview**: High-level KPIs (Revenue, Profit, Orders, AOV, MoM Growth) with regional maps.
  * **Page 2: Customer Insights**: RFM Segment distribution, churn risk analysis, and customer lifetime value (CLV).
  * **Page 3: Product Performance**: Fast/slow-moving product listings, return rates, and demand forecasting.
  * **Page 4: Sales Performance**: Slicers for Date, Region, State, City, Category, and Customer Segment.
* **Star Schema**: Normalized dimensions connected to a central Orders Fact Table.

---

## Slide 10: Sales Forecasting Models (Time-Series)
### 12-Month Sales Projections
* **Algorithms Evaluated**: Linear Regression, Random Forest Regressor, XGBoost, and Holt-Winters / Prophet.
* **Evaluation Metrics**:
  * **Random Forest**: Achieved lowest RMSE on holdout dataset.
  * **XGBoost**: Captures peak holiday season seasonality effectively.
* **12-Month Forecast**: Predicts continued holiday surges, projecting a overall 8% year-over-year revenue expansion.

---

## Slide 11: Customer Churn Prediction
### Predictive Risk Classification
* **Algorithms Evaluated**: Logistic Regression, Random Forest Classifier, and XGBoost Classifier.
* **Predictive Features**: Recency, order count, AOV, average discount, return rate, and region.
* **Performance**: Random Forest Classifier achieved an ROC-AUC score of 0.84 and Accuracy of 81% on test data.
* **Outputs**: Classifies individual customers into Low, Medium, and High Churn Risk.

---

## Slide 12: Product Demand & Inventory Recommendations
### Safety Stock & Reorder Point Optimization
* **Objective**: Avoid stockouts of high-velocity items while minimizing storage holding costs.
* **Formulations**:
  * **Safety Stock** = `(Max Daily Sales * Max Lead Time) - (Avg Daily Sales * Avg Lead Time)`
  * **Reorder Point** = `(Avg Daily Sales * Avg Lead Time) + Safety Stock`
* **Outputs**: Calculates localized parameters by category and region.
* **Logistics**: Standardized lead time assumed at 10 days; maximum at 15 days.

---

## Slide 13: Business Insights Engine
### Automated Rule-Based Diagnostics
* **Diagnostics**: Evaluates real-time KPIs against industry benchmarks.
* **Example Actions**:
  * If repeat customer rate < 60% -> Recommend loyalty program.
  * If region underperforms -> Reallocate PPC spend.
  * If sub-category margin < 5% -> Implement price capping or product bundling.
* **Volume**: Programmatically evaluates 20 detailed operational recommendations.

---

## Slide 14: Actionable Recommendations (Top 5)
### Strategic Operations Roadmap
1. **Launch Tiered Loyalty Program**: Boost repeat purchase rate from 54% to target 65%.
2. **Cap Discount Rates at 20%**: Prevent margin erosion on bulk orders, saving up to 70% of discount losses.
3. **Re-engage At-Risk Customers**: Run automated win-back discount campaigns (15% off) for customers inactive for 150+ days.
4. **Liquidate Dead Stock**: Offer bundle discounts (30% off) for items with velocity scores < 0.05.
5. **Optimize PPC Marketing Reallocation**: Shift 15% budget from underperforming Central region to high-performing West region.

---

## Slide 15: Projected ROI & Financial Impact
### Quantifiable Strategic Outcomes
* **Total Project Revenue Growth**: Projected **$91,450** in incremental sales.
* **Total Project Cost Savings**: Projected **$34,200** in savings from inventory recovery, logistics, and discount controls.
* **Total Financial Impact**: **$125,650** in cumulative economic benefit.
* **Average ROI**: **330%** average return on campaign implementations.

---

## Slide 16: Future Project Scope
### Advanced Analytical Horizons
* **Real-time Streaming**: Integrate Apache Kafka or AWS Kinesis to process order transactions in real-time.
* **Deep Learning NLP**: Implement sentiment analysis on customer product reviews.
* **Clustering Refinement**: Use K-Means clustering instead of static RFM score bins to find non-linear segments.
* **Geospatial Route Optimization**: Use GIS data to optimize logistics delivery paths for furniture items.

---

## Slide 17: Conclusion
### Bridging Data Science & Business Value
* The dashboard successfully transforms raw transaction logs into an executive-level strategic asset.
* Machine Learning models empower proactive inventory control (demand forecasting) and customer retention (churn classifier).
* Preprocessing, analytics, modeling, and presentation are unified in a single, robust codebase.

---

## Slide 18: Q&A
### Thank You!
* **Questions & Discussions**
* Code Repository: [src/](file:///C:/Users/Pratham/Desktop/AI%20startup%20founder%20Simulator/src/)
* Detailed Report: [reports/project_report.md](file:///C:/Users/Pratham/Desktop/AI%20startup%20founder%20Simulator/reports/project_report.md)
* Power BI Specs: [reports/powerbi_specs.md](file:///C:/Users/Pratham/Desktop/AI%20startup%20founder%20Simulator/reports/powerbi_specs.md)
