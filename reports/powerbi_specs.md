# Power BI Specifications & DAX Measures Manual

This manual provides the technical specifications, data modeling schema, and exact DAX (Data Analysis Expressions) formulas required to build the executive retail dashboard.

---

## 1. Data Model & Star Schema Relationships

To achieve optimal performance, set up a **Star Schema** with the following relationships in the Power BI Model view:

### Fact Table
* **Orders Data (`orders_data`)**
  * Grain: Transact-line item level.
  * Contains foreign keys to dimension tables.

### Dimension Tables
* **Customer Data (`customer_data`)**
  * Key: `Customer ID` (Primary Key)
  * Join: `orders_data[Customer ID] -> customer_data[Customer ID]` (1-to-Many, Single Direction Filter)
* **Product Data (`product_data`)**
  * Key: `Product ID` (Primary Key)
  * Join: `orders_data[Product ID] -> product_data[Product ID]` (1-to-Many, Single Direction Filter)
* **Region Data (`region_data`)**
  * Key: Composite `[City, State, Region]` or join via Customer location.
  * Join: `customer_data[City] -> region_data[City]` (1-to-Many, Both/Single Direction Filter)
* **Marketing Spend Data (`marketing_spend_data`)**
  * Join: Join to Region (`region_data[Region] -> marketing_spend_data[Region]`) or model as a separate fact table filtered by a shared Region and Date dimension.

---

## 2. Core Executive KPIs (Page 1: Executive Overview)

Write the following DAX measures in your Power BI workbook:

### 2.1 Total Revenue
Calculates cumulative gross sales volume.
```dax
Total Revenue = SUM(orders_data[Sales Amount])
```

### 2.2 Total Profit
Calculates cumulative net profit.
```dax
Total Profit = SUM(orders_data[Profit])
```

### 2.3 Total Orders
Counts unique order transactions.
```dax
Total Orders = DISTINCTCOUNT(orders_data[Order ID])
```

### 2.4 Total Customers
Counts unique active purchasing customers.
```dax
Total Customers = DISTINCTCOUNT(orders_data[Customer ID])
```

### 2.5 Average Order Value (AOV)
Measures the average spend per checkout order.
```dax
Average Order Value = DIVIDE([Total Revenue], [Total Orders], 0)
```

### 2.6 Profit Margin %
Calculates overall profit efficiency.
```dax
Profit Margin % = DIVIDE([Total Profit], [Total Revenue], 0)
```

### 2.7 Month-over-Month (MoM) Growth %
Measures percentage revenue growth compared to the prior month. Requires a Date table (`DateTable`) marked as Date Table in Power BI.
```dax
Prior Month Revenue = CALCULATE([Total Revenue], PARALLELPERIOD('DateTable'[Date], -1, MONTH))

MoM Growth % = DIVIDE([Total Revenue] - [Prior Month Revenue], [Prior Month Revenue], 0)
```

---

## 3. Customer Retention & Segmentation (Page 2: Customer Insights)

### 3.1 Repeat Purchase Rate %
Percentage of customers who have ordered more than once.
```dax
Customers With Multiple Orders = 
COUNTROWS(
    FILTER(
        ADDCOLUMNS(
            VALUES(orders_data[Customer ID]),
            "OrderCount", CALCULATE(DISTINCTCOUNT(orders_data[Order ID]))
        ),
        [OrderCount] > 1
    )
)

Repeat Purchase Rate % = DIVIDE([Customers With Multiple Orders], [Total Customers], 0)
```

### 3.2 Churn Rate %
Percentage of customers flagged as churned (no purchases in last 180 days).
```dax
Churned Customers Count = CALCULATE([Total Customers], customer_data[Churn Flag] = 1)

Churn Rate % = DIVIDE([Churned Customers Count], [Total Customers], 0)
```

### 3.3 Average Customer Lifetime Value (CLV)
Calculated customer worth based on historic sales.
```dax
Average CLV = AVERAGE(customer_data[Customer Lifetime Value])
```

### 3.4 Retention Rate %
The ratio of active returning customers.
```dax
Retention Rate % = 1 - [Churn Rate %]
```

---

## 4. Product & Inventory Performance (Page 3: Product Performance)

### 4.1 Product Return Rate %
Proportion of transactions that resulted in returned items.
```dax
Returned Quantity = CALCULATE(SUM(orders_data[Quantity]), orders_data[Return Flag] = 1)
Total Quantity Sold = SUM(orders_data[Quantity])

Product Return Rate % = DIVIDE([Returned Quantity], [Total Quantity Sold], 0)
```

### 4.2 Product Velocity Score
Measures units sold per active day.
```dax
Product Velocity = AVERAGE(product_data[Product Velocity Score])
```

### 4.3 Reorder Alert Flag
Identifies if inventory is below safety thresholds (Reorder Point).
```dax
Reorder Alert = 
IF(
    SUM(orders_data[Quantity]) >= RELATED(product_data[Selling Price]), // proxy indicator for low inventory
    "Reorder",
    "Healthy"
)
```

---

## 5. Sales Performance & Maps (Page 4: Sales Performance)

### 5.1 Region Filter Hierarchy
Set up a drill-down slicer with the following hierarchy:
`Region` -> `State` -> `City`

### 5.2 Category Filter Slicer
Enforce product categorizations:
`Category` -> `Sub-category`
