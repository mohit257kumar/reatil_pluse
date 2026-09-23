-- ============================================================
-- RetailPulse — Sales Analysis Queries
-- ============================================================
-- Covers: total KPIs, monthly trends, YoY growth, seasonality,
--         channel performance, payment methods, AOV
-- ============================================================

USE retailpulse;

-- ─────────────────────────────────────────────────────────────
-- 1. OVERALL KPIs
-- ─────────────────────────────────────────────────────────────

SELECT
    COUNT(DISTINCT order_id)                                    AS total_orders,
    COUNT(DISTINCT customer_id)                                 AS unique_customers,
    ROUND(SUM(line_total), 0)                                   AS total_revenue,
    ROUND(SUM(cost_total), 0)                                   AS total_cost,
    ROUND(SUM(profit), 0)                                       AS total_profit,
    ROUND(SUM(profit) / NULLIF(SUM(line_total), 0) * 100, 2)   AS overall_margin_pct,
    ROUND(SUM(line_total) / COUNT(DISTINCT order_id), 2)        AS avg_order_value,
    ROUND(SUM(quantity), 0)                                     AS total_units_sold
FROM fact_sales
WHERE order_status = 'Delivered';

-- ─────────────────────────────────────────────────────────────
-- 2. MONTHLY REVENUE & PROFIT TREND
-- ─────────────────────────────────────────────────────────────

SELECT
    year_month,
    orders,
    ROUND(revenue, 0)    AS revenue,
    ROUND(profit, 0)     AS profit,
    margin_pct
FROM vw_monthly_revenue
ORDER BY year_month;

-- ─────────────────────────────────────────────────────────────
-- 3. YEAR-OVER-YEAR GROWTH
-- ─────────────────────────────────────────────────────────────

WITH yearly AS (
    SELECT
        YEAR(order_date)  AS yr,
        SUM(line_total)   AS revenue,
        SUM(profit)       AS profit,
        COUNT(DISTINCT order_id) AS orders
    FROM fact_sales
    WHERE order_status = 'Delivered'
    GROUP BY YEAR(order_date)
)
SELECT
    yr,
    ROUND(revenue, 0)       AS revenue,
    ROUND(profit, 0)        AS profit,
    orders,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY yr))
        / NULLIF(LAG(revenue) OVER (ORDER BY yr), 0) * 100, 2
    )                       AS revenue_growth_pct,
    ROUND(
        (profit - LAG(profit) OVER (ORDER BY yr))
        / NULLIF(LAG(profit) OVER (ORDER BY yr), 0) * 100, 2
    )                       AS profit_growth_pct
FROM yearly
ORDER BY yr;

-- ─────────────────────────────────────────────────────────────
-- 4. MONTH-OVER-MONTH REVENUE CHANGE (Running)
-- ─────────────────────────────────────────────────────────────

SELECT
    year_month,
    ROUND(revenue, 0)     AS revenue,
    ROUND(revenue - LAG(revenue) OVER (ORDER BY year_month), 0)  AS mom_change,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY year_month))
        / NULLIF(LAG(revenue) OVER (ORDER BY year_month), 0) * 100, 2
    )                     AS mom_growth_pct
FROM vw_monthly_revenue
ORDER BY year_month;

-- ─────────────────────────────────────────────────────────────
-- 5. SEASONALITY — AVERAGE REVENUE BY MONTH (ACROSS ALL YEARS)
-- ─────────────────────────────────────────────────────────────

SELECT
    month,
    CASE month
        WHEN 1  THEN 'January'    WHEN 2  THEN 'February'
        WHEN 3  THEN 'March'      WHEN 4  THEN 'April'
        WHEN 5  THEN 'May'        WHEN 6  THEN 'June'
        WHEN 7  THEN 'July'       WHEN 8  THEN 'August'
        WHEN 9  THEN 'September'  WHEN 10 THEN 'October'
        WHEN 11 THEN 'November'   WHEN 12 THEN 'December'
    END                                  AS month_name,
    ROUND(AVG(revenue), 0)               AS avg_monthly_revenue,
    ROUND(AVG(profit), 0)                AS avg_monthly_profit,
    ROUND(AVG(margin_pct), 2)            AS avg_margin_pct,
    ROUND(MAX(revenue) / MIN(revenue), 2) AS peak_to_trough_ratio
FROM vw_monthly_revenue
GROUP BY month
ORDER BY month;

-- ─────────────────────────────────────────────────────────────
-- 6. REVENUE BY SALES CHANNEL
-- ─────────────────────────────────────────────────────────────

SELECT
    sales_channel,
    COUNT(DISTINCT order_id)                                   AS orders,
    ROUND(SUM(line_total), 0)                                  AS revenue,
    ROUND(SUM(profit), 0)                                      AS profit,
    ROUND(SUM(profit) / NULLIF(SUM(line_total), 0) * 100, 2)  AS margin_pct,
    ROUND(SUM(line_total) / COUNT(DISTINCT order_id), 2)       AS avg_order_value
FROM fact_sales
WHERE order_status = 'Delivered'
GROUP BY sales_channel
ORDER BY revenue DESC;

-- ─────────────────────────────────────────────────────────────
-- 7. REVENUE BY PAYMENT METHOD
-- ─────────────────────────────────────────────────────────────

SELECT
    COALESCE(payment_method, 'Unknown')                        AS payment_method,
    COUNT(DISTINCT order_id)                                   AS orders,
    ROUND(SUM(line_total), 0)                                  AS revenue,
    ROUND(SUM(line_total) / COUNT(DISTINCT order_id), 2)       AS avg_order_value
FROM fact_sales
WHERE order_status = 'Delivered'
GROUP BY payment_method
ORDER BY revenue DESC;

-- ─────────────────────────────────────────────────────────────
-- 8. ORDER STATUS BREAKDOWN
-- ─────────────────────────────────────────────────────────────

SELECT
    order_status,
    COUNT(DISTINCT order_id)                                        AS orders,
    ROUND(COUNT(DISTINCT order_id) * 100.0 /
          SUM(COUNT(DISTINCT order_id)) OVER (), 2)                 AS pct_of_orders,
    ROUND(SUM(line_total), 0)                                       AS gross_revenue_impact
FROM fact_sales
GROUP BY order_status
ORDER BY orders DESC;

-- ─────────────────────────────────────────────────────────────
-- 9. AVERAGE ORDER VALUE TREND BY QUARTER
-- ─────────────────────────────────────────────────────────────

SELECT
    YEAR(order_date)                                            AS yr,
    QUARTER(order_date)                                         AS qtr,
    COUNT(DISTINCT order_id)                                    AS orders,
    ROUND(SUM(line_total), 0)                                   AS revenue,
    ROUND(SUM(line_total) / COUNT(DISTINCT order_id), 2)        AS avg_order_value
FROM fact_sales
WHERE order_status = 'Delivered'
GROUP BY YEAR(order_date), QUARTER(order_date)
ORDER BY yr, qtr;

-- ─────────────────────────────────────────────────────────────
-- 10. DISCOUNT IMPACT ON REVENUE AND MARGIN
-- ─────────────────────────────────────────────────────────────

SELECT
    CASE
        WHEN discount = 0             THEN '0%'
        WHEN discount <= 0.05         THEN '1-5%'
        WHEN discount <= 0.10         THEN '6-10%'
        WHEN discount <= 0.15         THEN '11-15%'
        WHEN discount <= 0.20         THEN '16-20%'
        WHEN discount <= 0.30         THEN '21-30%'
        ELSE '>30%'
    END                                                         AS discount_bucket,
    COUNT(*)                                                    AS line_items,
    ROUND(SUM(line_total), 0)                                   AS revenue,
    ROUND(AVG(margin_pct), 2)                                   AS avg_margin_pct
FROM fact_sales
WHERE order_status = 'Delivered'
GROUP BY discount_bucket
ORDER BY MIN(discount);

-- ─────────────────────────────────────────────────────────────
-- 11. RUNNING CUMULATIVE REVENUE (YTD per year)
-- ─────────────────────────────────────────────────────────────

SELECT
    year_month,
    year,
    ROUND(revenue, 0) AS monthly_revenue,
    ROUND(
        SUM(revenue) OVER (PARTITION BY year ORDER BY year_month
                           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 0
    ) AS ytd_revenue
FROM vw_monthly_revenue
ORDER BY year_month;
