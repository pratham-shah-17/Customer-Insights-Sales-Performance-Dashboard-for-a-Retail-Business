# Data Dictionary - Customer Insights & Sales Performance Dashboard

This document details the schema definitions, data types, and business descriptions of the tables composing the retail relational database model.

---

## 1. Customer Data
Contains demographic and registration details for each unique customer.

| Column Name | Data Type | Description | Sample/Format |
| :--- | :--- | :--- | :--- |
| **Customer ID** | VARCHAR (PK) | Unique identifier for each customer | `AA-10315`, `CG-12520` |
| **Name** | VARCHAR | Full name of the customer | `Alex Avila`, `Claire Gute` |
| **Gender** | VARCHAR | Demographical gender classification | `Male`, `Female` |
| **Age** | INTEGER | Age of the customer in years | `32`, `55` |
| **City** | VARCHAR | Primary city of the customer | `Henderson`, `Los Angeles` |
| **Region** | VARCHAR | Geographical region classification | `South`, `West`, `East`, `Central` |
| **Registration Date** | DATE | The date the customer registered their profile | `YYYY-MM-DD` |

---

## 2. Orders Data
Contains details of transactional sales records at the order-line level.

| Column Name | Data Type | Description | Sample/Format |
| :--- | :--- | :--- | :--- |
| **Order ID** | VARCHAR | Unique identifier for the order transaction | `CA-2023-152156` |
| **Customer ID** | VARCHAR (FK) | Reference identifier to the Customer | `CG-12520` |
| **Product ID** | VARCHAR (FK) | Reference identifier to the Product | `FUR-BO-10001798` |
| **Quantity** | INTEGER | Units purchased in the transaction | `2`, `5` |
| **Sales Amount** | DECIMAL | Gross sale value of the transaction | `261.96` |
| **Profit** | DECIMAL | Net profit earned from this item sale | `41.91` |
| **Discount** | DECIMAL | Rate of discount applied to the purchase | `0.15` (15%) |
| **Order Date** | DATE | Transaction purchase date | `YYYY-MM-DD` |

---

## 3. Product Data
Contains catalog definitions and pricing models for each product sold.

| Column Name | Data Type | Description | Sample/Format |
| :--- | :--- | :--- | :--- |
| **Product ID** | VARCHAR (PK) | Unique identifier for each product | `FUR-BO-10001798` |
| **Product Name** | VARCHAR | Complete catalog name of the product | `Bush Somerset Bookcase` |
| **Category** | VARCHAR | Broad product classification | `Furniture`, `Office Supplies`, `Technology` |
| **Sub-category** | VARCHAR | Narrow sub-classification level | `Bookcases`, `Art`, `Phones` |
| **Cost Price** | DECIMAL | Cost to acquire/manufacture the item | `185.00` |
| **Selling Price** | DECIMAL | Catalog unit selling price (before discounts) | `261.96` |

---

## 4. Region Data
Enforces geographical normalization and relationships.

| Column Name | Data Type | Description | Sample/Format |
| :--- | :--- | :--- | :--- |
| **Region** | VARCHAR | Primary regional segment | `South`, `West`, `Central`, `East` |
| **State** | VARCHAR | State name | `Kentucky`, `California` |
| **City** | VARCHAR | City name | `Henderson`, `Los Angeles` |

---

## 5. Marketing Spend Data
Tracks campaign spending metrics across different regions.

| Column Name | Data Type | Description | Sample/Format |
| :--- | :--- | :--- | :--- |
| **Region** | VARCHAR | Target geographic region | `East`, `West`, `Central`, `South` |
| **Campaign Type** | VARCHAR | Promotional channel type | `Social Media`, `PPC`, `Email`, `Influencer` |
| **Spend Amount** | DECIMAL | Advertising budget spent | `1250.75` |
| **Campaign Date** | DATE | Month/Date of the advertising spend | `YYYY-MM-DD` |
