# RetailPulse — Interview Guide

A comprehensive Q&A guide to confidently explain and defend every technical and business decision in the RetailPulse project during interviews.

---

## 1. Project Overview Questions

**Q: Walk me through the RetailPulse project.**

> RetailPulse is an end-to-end retail analytics project simulating a multi-category Indian retail company with 40+ stores, 15,000 customers, and 3 years of transactional data. I built the full analytics pipeline: data generation with realistic quality issues, a Python cleaning pipeline, exploratory data analysis with 16+ charts, SQL analytics using window functions and CTEs, customer segmentation using RFM, time series forecasting using Holt-Winters, and a 5-page Power BI dashboard with a star schema and DAX measures. The goal was to answer concrete business questions around revenue, profitability, customer retention, inventory risk, and forecasting.

**Q: Why did you build your own dataset instead of using a public one?**

> Building synthetic data gave me full control over the schema design, data quality issues, and business logic. Real retail datasets are either too simple or not granular enough for a full analytics showcase. I introduced intentional quality issues (missing values, duplicates, inconsistent categories, outlier prices) to demonstrate a realistic cleaning pipeline — which is often the hardest part of real data work.

---

## 2. Data Engineering & Cleaning

**Q: What data quality issues did you introduce and how did you handle them?**

| Issue | Table | Fix Applied |
|-------|-------|-------------|
| Missing gender/age | Customers | Filled with mode/median |
| City casing inconsistency | Customers | `.str.title()` normalisation |
| Invalid registration date | Customers | Coerce + drop |
| Negative/zero selling prices | Products | Replace with median |
| Inconsistent category names | Products | Regex replacement map |
| Fat-finger price outliers | Order Details | IQR cap (1%–99%) |
| Zero quantity rows | Order Details | Drop invalid rows |
| Missing discount | Order Details | Fill with 0 (no discount assumed) |
| Duplicate rows | All tables | `drop_duplicates()` |
| Missing quantity | Inventory | Drop rows |

**Q: How did you handle outliers in unit prices?**

> I used IQR-based capping at the 1st and 99th percentiles. This is more robust than z-score for skewed distributions like retail prices. The data had 5 rows where a fat-finger error multiplied prices by 1,000 (e.g., ₹500 → ₹500,000). The IQR cap brought these back to the 99th percentile value without dropping legitimate high-value transactions.

**Q: Why did you fill missing discount with 0 rather than imputing with the mean?**

> A missing discount in an order detail row most likely means no discount was applied — it's a data capture omission, not a random missing value. The business default is "no discount" unless explicitly recorded. Imputing the mean discount (~8%) would artificially inflate discount-related metrics and distort margin calculations.

---

## 3. SQL Analytics

**Q: What's the most complex SQL query in this project?**

> The RFM scoring query uses a multi-level CTE structure: the first CTE computes the reference date, the second aggregates recency, frequency, and monetary per customer, the third applies `NTILE(5)` window functions to score each RFM dimension, and the outer query joins back to customer details and applies the segment classification CASE logic. The key challenge was the `NTILE` window function — recency needs to be ranked *descendingly* (lower recency = better), while frequency and monetary rank ascendingly.

**Q: Explain the difference between the staging tables and fact/dim tables.**

> The staging tables (`orders`, `order_details`, `inventory_transactions`) mirror the raw CSV structure with minimal transformation — they're the load target for LOAD DATA INFILE. The fact and dimension tables (`fact_sales`, `dim_customer`, etc.) form the star schema. `fact_sales` is a denormalised table that pre-joins order details with cost prices to pre-compute `profit` and `margin_pct` — this makes dashboard queries fast and avoids repeated joins in Power BI DAX.

**Q: Why use window functions instead of subqueries for ranking?**

> Window functions like `RANK() OVER (PARTITION BY region ORDER BY revenue DESC)` compute ranking per-partition in a single pass over the data. Equivalent correlated subqueries would require N scans of the table — O(N²) complexity. At 300,000 order detail rows, window functions are significantly faster and more readable.

---

## 4. Python & Data Analysis

**Q: Why Holt-Winters for forecasting instead of ARIMA?**

> Holt-Winters was the right choice because:
> 1. The data has **clear trend** (overall growth) and **stable additive seasonality** (recurring festival patterns at fixed months).
> 2. Holt-Winters has fewer parameters to tune and is more interpretable than ARIMA.
> 3. With only 36 months of data, we're at the lower bound for SARIMA parameter stability — Holt-Winters is more robust with limited history.
> ARIMA would be preferred if the seasonal pattern were irregular or if the data showed non-stationary seasonality. I evaluated both on a 6-month hold-out; Holt-Winters achieved lower MAPE.

**Q: How did you validate your forecasting model?**

> I used a walk-forward validation approach: trained on months 1–30, tested on months 31–36 (hold-out). This simulates real-world forecasting where you predict into the future. I computed MAE, RMSE, and MAPE. MAPE is the most business-interpretable metric — it tells you "the forecast is off by X% on average". I plotted actuals vs. forecast on a chart with an approximate confidence interval (±1.5σ of residuals).

**Q: Walk me through the RFM scoring logic.**

> 1. Compute **Recency** = days between each customer's last order and the reference date (day after last order in dataset).
> 2. Compute **Frequency** = number of distinct delivered orders per customer.
> 3. Compute **Monetary** = sum of line_total from delivered orders per customer.
> 4. Score each dimension 1–5 using `pd.qcut` quintile binning. For Recency, labels are reversed (5=most recent, 1=least recent) because lower recency (more recent) is better.
> 5. Concatenate R, F, M scores into a 3-digit string (e.g., "554" = Champion).
> 6. Apply segment logic using a priority-ordered set of conditions to assign each customer to one of 11 business segments.

**Q: What would you do differently with more time?**

> - Use **LSTM or Prophet** for forecasting to capture non-linear patterns and handle Indian holiday calendars automatically.
> - Build a **churn prediction model** using logistic regression or gradient boosting with RFM + behavioural features.
> - Implement **cohort analysis** — track customer retention rates by acquisition month cohort.
> - Automate the full pipeline with Apache Airflow DAGs.
> - Add a **real-time inventory alert** microservice triggered by stock levels crossing the reorder threshold.

---

## 5. Power BI & DAX

**Q: Why did you use a star schema instead of loading flat CSVs directly?**

> A star schema separates facts (measurements) from dimensions (descriptors), which:
> 1. Enables **fast aggregations** — Power BI's VertiPaq engine compresses dimension tables aggressively.
> 2. Makes **DAX time intelligence** reliable — DimDate must be a proper date dimension.
> 3. Reduces **data redundancy** — product and customer attributes are stored once, not repeated per order.
> 4. Makes the **model self-documenting** — relationships are explicit and visual in the Model view.

**Q: Explain the CALCULATE function in DAX.**

> `CALCULATE` is DAX's filter context modifier. It evaluates an expression in a modified filter context. Example: `Revenue LY = CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(DimDate[date_id]))` — this takes the Total Revenue measure but replaces the current year context with the same period one year prior. Without `CALCULATE`, you can't override the implicit filter context from slicers or report-level filters.

**Q: What's the difference between a measure and a calculated column?**

> - **Calculated column**: Computed row-by-row at data refresh time, stored in the model, evaluated in row context. Use for values needed in slicers/rows (e.g., `Order Year`, `Margin %` per line).
> - **Measure**: Computed dynamically at query time, not stored, evaluated in filter context. Use for aggregations (e.g., `Total Revenue`, `Gross Margin %`). Measures are lazy — they only compute when a visual requests them — making them more memory-efficient.

---

## 6. Business Acumen Questions

**Q: What is the single most important insight from this project?**

> The revenue concentration risk: **top 5% of customers generate ~22% of revenue**, and ~22% of customers are already at-risk or lost. This means the business is exposed to significant revenue decline if it doesn't actively retain its Champions and win back At-Risk customers. A targeted retention programme for the top 500–1,000 customers is the highest-ROI action the business can take.

**Q: How would you present these findings to a non-technical business audience?**

> I'd lead with the three business questions they care about most: "Are we growing?", "Who are our best customers?", and "Where are we at risk?" I'd use the Power BI dashboard with visual KPI cards and drill-through capabilities. For inventory risk, I'd show the "12 products facing stockout" list with estimated lost revenue per day of stockout — converting a technical metric into a financial cost. I avoid jargon like "IQR" or "MAPE" in business presentations.

**Q: What is the Pareto principle insight you found in customer data?**

> Across 3 years, roughly **80% of total revenue comes from 20% of customers** — this is slightly better than the classic Pareto split (here it's closer to 28% of revenue from the top 3.3% of customers). The implication is that acquiring new customers is less impactful than retaining and growing existing top-tier customers. LTV maximisation strategies — upsell, cross-sell, VIP retention — deliver higher ROI than acquisition campaigns at this stage.

---

## 7. Technical Implementation Details

**Q: How did you ensure reproducibility of the generated dataset?**

> I set `random.seed(42)`, `np.random.seed(42)`, and `fake.seed_instance(42)` at the top of `data_generation.py`. This ensures every run of the script produces identical output — same customer names, same order dates, same quality issues. This is critical for a portfolio project where reviewers may run the code.

**Q: How did you handle the seasonal date weighting in data generation?**

> I computed a `seasonal_weight()` function that maps each date to a multiplier based on known Indian retail patterns (Diwali = 1.65×, January = 0.70×, etc.). I then used `random.choices()` with these weights as probabilities when sampling order dates from the 2021–2023 date range. This produces a realistic distribution where ~18% of all orders fall in October–November.

**Q: What is the performance implication of your EDA code on large datasets?**

> The master sales table has ~250,000+ rows after joining delivered orders with order details. I use Pandas groupby + agg operations which are vectorised — they avoid Python loops and run in Cython/NumPy. For the scatter chart, I sample 5,000 rows to avoid over-plotting. For production use, I'd push aggregations to the database layer (SQL) and only pull summary data into Python for visualisation.

---

## 8. Quick-Fire Technical Questions

| Question | Answer |
|----------|--------|
| What does `NTILE(5)` do? | Divides rows into 5 equal-sized buckets ordered by the specified column |
| What is the Star Schema? | Fact table at centre, dimension tables on edges, single-level JOIN relationships |
| What is MAPE? | Mean Absolute Percentage Error — average % deviation of forecast from actual |
| What is RFM? | Recency, Frequency, Monetary — customer segmentation framework |
| What is a CTE? | Common Table Expression — named temporary result set used within a query |
| What does IQR stand for? | Interquartile Range — range between 25th and 75th percentile |
| Why use Faker library? | To generate realistic synthetic personal data (names, addresses) with locale support |
| What is SAMEPERIODLASTYEAR? | DAX time intelligence function returning same period from prior year |
| What is VertiPaq? | Power BI's columnar in-memory storage engine that compresses and indexes data |
| What is a Slowly Changing Dimension? | Dimension data that changes over time (e.g., customer address changes) |

---

*Prepared for interview prep as part of the RetailPulse data analytics portfolio project.*
