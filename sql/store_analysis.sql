-- ============================================================
-- RetailPulse — Store Analysis Queries
-- ============================================================
-- Covers: store KPIs, city/region performance, top/bottom stores,
--         store-type comparison, growth trends
-- ============================================================

USE retailpulse;

-- ─────────────────────────────────────────────────────────────
-- 1. OVERALL STORE KPIs
-- ─────────────────────────────────────────────────────────────

SELECT
    COUNT(DISTINCT store_id)                                   AS total_stores,
    COUNT(DISTINCT city)                                       AS cities_covered,
    COUNT(DISTINCT region)                                     AS regions_covered
FROM dim_store;

-- ─────────────────────────────────────────────────────────────
-- 2. STORE PERFORMANCE SUMMARY
-- ─────────────────────────────────────────────────────────────

SELECT
    fs.store_id,
    s.store_name,
    s.city,
    s.region,
    s.store_type,
    COUNT(DISTINCT fs.order_id)                                AS orders,
    COUNT(DISTINCT fs.customer_id)                             AS unique_customers,
    ROUND(SUM(fs.line_total), 0)                               AS revenue,
    ROUND(SUM(fs.profit), 0)                                   AS profit,
    ROUND(SUM(fs.profit) / NULLIF(SUM(fs.line_total), 0) * 100, 2) AS margin_pct,
    ROUND(SUM(fs.line_total) / COUNT(DISTINCT fs.order_id), 2) AS avg_order_value
FROM fact_sales fs
JOIN dim_store s ON fs.store_id = s.store_id
WHERE fs.order_status = 'Delivered'
GROUP BY fs.store_id, s.store_name, s.city, s.region, s.store_type
ORDER BY revenue DESC;

-- ─────────────────────────────────────────────────────────────
-- 3. TOP 10 STORES BY REVENUE
-- ─────────────────────────────────────────────────────────────

SELECT
    fs.store_id,
    s.store_name,
    s.city,
    s.region,
    ROUND(SUM(fs.line_total), 0)  AS revenue,
    ROUND(SUM(fs.profit), 0)      AS profit,
    ROUND(SUM(fs.profit) / NULLIF(SUM(fs.line_total), 0) * 100, 2) AS margin_pct
FROM fact_sales fs
JOIN dim_store s ON fs.store_id = s.store_id
WHERE fs.order_status = 'Delivered'
GROUP BY fs.store_id, s.store_name, s.city, s.region
ORDER BY revenue DESC
LIMIT 10;

-- ─────────────────────────────────────────────────────────────
-- 4. BOTTOM 10 STORES BY PROFIT MARGIN (Underperformers)
-- ─────────────────────────────────────────────────────────────

SELECT
    fs.store_id,
    s.store_name,
    s.city,
    s.region,
    s.store_type,
    COUNT(DISTINCT fs.order_id)                                AS orders,
    ROUND(SUM(fs.line_total), 0)                               AS revenue,
    ROUND(SUM(fs.profit), 0)                                   AS profit,
    ROUND(SUM(fs.profit) / NULLIF(SUM(fs.line_total), 0) * 100, 2) AS margin_pct
FROM fact_sales fs
JOIN dim_store s ON fs.store_id = s.store_id
WHERE fs.order_status = 'Delivered'
GROUP BY fs.store_id, s.store_name, s.city, s.region, s.store_type
HAVING orders >= 100   -- Exclude very low-traffic stores
ORDER BY margin_pct
LIMIT 10;

-- ─────────────────────────────────────────────────────────────
-- 5. REVENUE BY REGION
-- ─────────────────────────────────────────────────────────────

SELECT
    s.region,
    COUNT(DISTINCT fs.store_id)                               AS stores,
    COUNT(DISTINCT fs.customer_id)                            AS customers,
    COUNT(DISTINCT fs.order_id)                               AS orders,
    ROUND(SUM(fs.line_total), 0)                              AS revenue,
    ROUND(SUM(fs.profit), 0)                                  AS profit,
    ROUND(SUM(fs.profit) / NULLIF(SUM(fs.line_total), 0) * 100, 2) AS margin_pct,
    ROUND(SUM(fs.line_total) / COUNT(DISTINCT fs.store_id), 0) AS revenue_per_store
FROM fact_sales fs
JOIN dim_store s ON fs.store_id = s.store_id
WHERE fs.order_status = 'Delivered'
GROUP BY s.region
ORDER BY revenue DESC;

-- ─────────────────────────────────────────────────────────────
-- 6. REVENUE BY CITY
-- ─────────────────────────────────────────────────────────────

SELECT
    s.city,
    s.region,
    COUNT(DISTINCT fs.store_id)                               AS stores,
    COUNT(DISTINCT fs.order_id)                               AS orders,
    ROUND(SUM(fs.line_total), 0)                              AS revenue,
    ROUND(SUM(fs.profit), 0)                                  AS profit,
    ROUND(SUM(fs.profit) / NULLIF(SUM(fs.line_total), 0) * 100, 2) AS margin_pct
FROM fact_sales fs
JOIN dim_store s ON fs.store_id = s.store_id
WHERE fs.order_status = 'Delivered'
GROUP BY s.city, s.region
ORDER BY revenue DESC;

-- ─────────────────────────────────────────────────────────────
-- 7. STORE TYPE COMPARISON
-- ─────────────────────────────────────────────────────────────

SELECT
    s.store_type,
    COUNT(DISTINCT fs.store_id)                               AS stores,
    COUNT(DISTINCT fs.order_id)                               AS orders,
    ROUND(SUM(fs.line_total), 0)                              AS total_revenue,
    ROUND(SUM(fs.line_total) / COUNT(DISTINCT fs.store_id), 0) AS avg_revenue_per_store,
    ROUND(SUM(fs.profit) / NULLIF(SUM(fs.line_total), 0) * 100, 2) AS avg_margin_pct
FROM fact_sales fs
JOIN dim_store s ON fs.store_id = s.store_id
WHERE fs.order_status = 'Delivered'
GROUP BY s.store_type
ORDER BY avg_revenue_per_store DESC;

-- ─────────────────────────────────────────────────────────────
-- 8. STORE REVENUE GROWTH (2022 → 2023)
-- ─────────────────────────────────────────────────────────────

WITH yearly AS (
    SELECT
        fs.store_id,
        YEAR(fs.order_date)         AS yr,
        SUM(fs.line_total)          AS revenue
    FROM fact_sales fs
    WHERE fs.order_status = 'Delivered'
      AND YEAR(fs.order_date) IN (2022, 2023)
    GROUP BY fs.store_id, YEAR(fs.order_date)
),
pivoted AS (
    SELECT
        store_id,
        SUM(CASE WHEN yr = 2022 THEN revenue ELSE 0 END) AS rev_2022,
        SUM(CASE WHEN yr = 2023 THEN revenue ELSE 0 END) AS rev_2023
    FROM yearly
    GROUP BY store_id
)
SELECT
    p.store_id,
    s.store_name,
    s.city,
    s.region,
    ROUND(p.rev_2022, 0)       AS rev_2022,
    ROUND(p.rev_2023, 0)       AS rev_2023,
    ROUND((p.rev_2023 - p.rev_2022) / NULLIF(p.rev_2022, 0) * 100, 2) AS growth_pct
FROM pivoted p
JOIN dim_store s ON p.store_id = s.store_id
ORDER BY growth_pct DESC;

-- ─────────────────────────────────────────────────────────────
-- 9. STORE RANK WITHIN REGION (Window Function)
-- ─────────────────────────────────────────────────────────────

SELECT
    fs.store_id,
    s.store_name,
    s.city,
    s.region,
    ROUND(SUM(fs.line_total), 0) AS revenue,
    RANK() OVER (PARTITION BY s.region ORDER BY SUM(fs.line_total) DESC) AS rank_in_region
FROM fact_sales fs
JOIN dim_store s ON fs.store_id = s.store_id
WHERE fs.order_status = 'Delivered'
GROUP BY fs.store_id, s.store_name, s.city, s.region
ORDER BY s.region, rank_in_region;

-- ─────────────────────────────────────────────────────────────
-- 10. STORE REVENUE ROLLING 3-MONTH AVERAGE
-- ─────────────────────────────────────────────────────────────

WITH monthly_store AS (
    SELECT
        fs.store_id,
        DATE_FORMAT(fs.order_date, '%Y-%m') AS yr_month,
        ROUND(SUM(fs.line_total), 0)         AS revenue
    FROM fact_sales fs
    WHERE fs.order_status = 'Delivered'
    GROUP BY fs.store_id, DATE_FORMAT(fs.order_date, '%Y-%m')
)
SELECT
    store_id,
    yr_month,
    revenue,
    ROUND(AVG(revenue) OVER (
        PARTITION BY store_id
        ORDER BY yr_month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 0) AS rolling_3m_avg_revenue
FROM monthly_store
ORDER BY store_id, yr_month;
