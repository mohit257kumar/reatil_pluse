-- ============================================================
-- RetailPulse — Product Analysis Queries
-- ============================================================
-- Covers: top/bottom products, category performance, margin analysis,
--         fast/slow movers, brand analysis, discount patterns
-- ============================================================

USE retailpulse;

-- ─────────────────────────────────────────────────────────────
-- 1. REVENUE & PROFIT BY CATEGORY
-- ─────────────────────────────────────────────────────────────

SELECT
    p.category,
    COUNT(DISTINCT p.product_id)                               AS products,
    SUM(fs.quantity)                                           AS units_sold,
    ROUND(SUM(fs.line_total), 0)                               AS revenue,
    ROUND(SUM(fs.profit), 0)                                   AS profit,
    ROUND(SUM(fs.profit) / NULLIF(SUM(fs.line_total), 0) * 100, 2) AS margin_pct,
    ROUND(AVG(fs.discount) * 100, 2)                           AS avg_discount_pct,
    ROUND(SUM(fs.line_total) / COUNT(DISTINCT fs.order_id), 2) AS avg_order_value
FROM fact_sales fs
JOIN dim_product p ON fs.product_id = p.product_id
WHERE fs.order_status = 'Delivered'
GROUP BY p.category
ORDER BY revenue DESC;

-- ─────────────────────────────────────────────────────────────
-- 2. TOP 20 PRODUCTS BY REVENUE
-- ─────────────────────────────────────────────────────────────

SELECT
    product_id,
    product_name,
    category,
    brand,
    orders,
    units_sold,
    ROUND(revenue, 0)     AS revenue,
    ROUND(profit, 0)      AS profit,
    margin_pct,
    ROUND(avg_discount_pct, 2) AS avg_discount_pct
FROM vw_product_performance
ORDER BY revenue DESC
LIMIT 20;

-- ─────────────────────────────────────────────────────────────
-- 3. BOTTOM 20 PRODUCTS BY REVENUE (Slow Movers)
-- ─────────────────────────────────────────────────────────────

SELECT
    product_id,
    product_name,
    category,
    brand,
    orders,
    units_sold,
    ROUND(revenue, 0) AS revenue
FROM vw_product_performance
ORDER BY revenue
LIMIT 20;

-- ─────────────────────────────────────────────────────────────
-- 4. TOP 10 PRODUCTS BY PROFIT MARGIN
-- ─────────────────────────────────────────────────────────────

SELECT
    product_id,
    product_name,
    category,
    ROUND(revenue, 0)     AS revenue,
    ROUND(profit, 0)      AS profit,
    margin_pct
FROM vw_product_performance
WHERE units_sold >= 10   -- Exclude very low-volume products
ORDER BY margin_pct DESC
LIMIT 10;

-- ─────────────────────────────────────────────────────────────
-- 5. BOTTOM 10 PRODUCTS BY PROFIT MARGIN (Margin Leakers)
-- ─────────────────────────────────────────────────────────────

SELECT
    product_id,
    product_name,
    category,
    ROUND(revenue, 0)  AS revenue,
    ROUND(profit, 0)   AS profit,
    margin_pct
FROM vw_product_performance
WHERE units_sold >= 10
ORDER BY margin_pct
LIMIT 10;

-- ─────────────────────────────────────────────────────────────
-- 6. PRODUCT PERFORMANCE RANK WITHIN CATEGORY (Window Function)
-- ─────────────────────────────────────────────────────────────

SELECT
    category,
    product_name,
    ROUND(revenue, 0)                                AS revenue,
    ROUND(profit, 0)                                 AS profit,
    margin_pct,
    RANK() OVER (PARTITION BY category ORDER BY revenue DESC) AS rank_in_category
FROM vw_product_performance
ORDER BY category, rank_in_category
LIMIT 50;

-- ─────────────────────────────────────────────────────────────
-- 7. FAST MOVERS vs SLOW MOVERS (Quartile segmentation)
-- ─────────────────────────────────────────────────────────────

SELECT
    product_id,
    product_name,
    category,
    units_sold,
    ROUND(revenue, 0)  AS revenue,
    NTILE(4) OVER (ORDER BY units_sold DESC) AS velocity_quartile,
    CASE
        WHEN NTILE(4) OVER (ORDER BY units_sold DESC) = 1 THEN 'Fast Mover'
        WHEN NTILE(4) OVER (ORDER BY units_sold DESC) = 2 THEN 'Medium'
        WHEN NTILE(4) OVER (ORDER BY units_sold DESC) = 3 THEN 'Slow'
        ELSE 'Dead Stock Risk'
    END               AS velocity_label
FROM vw_product_performance
ORDER BY units_sold DESC;

-- ─────────────────────────────────────────────────────────────
-- 8. BRAND PERFORMANCE SUMMARY
-- ─────────────────────────────────────────────────────────────

SELECT
    p.brand,
    p.category,
    COUNT(DISTINCT p.product_id)                               AS product_count,
    SUM(fs.quantity)                                           AS units_sold,
    ROUND(SUM(fs.line_total), 0)                               AS revenue,
    ROUND(SUM(fs.profit), 0)                                   AS profit,
    ROUND(SUM(fs.profit) / NULLIF(SUM(fs.line_total), 0) * 100, 2) AS margin_pct
FROM fact_sales fs
JOIN dim_product p ON fs.product_id = p.product_id
WHERE fs.order_status = 'Delivered'
GROUP BY p.brand, p.category
ORDER BY revenue DESC
LIMIT 30;

-- ─────────────────────────────────────────────────────────────
-- 9. SUB-CATEGORY PERFORMANCE
-- ─────────────────────────────────────────────────────────────

SELECT
    p.category,
    p.sub_category,
    COUNT(DISTINCT p.product_id)                                AS products,
    SUM(fs.quantity)                                            AS units_sold,
    ROUND(SUM(fs.line_total), 0)                                AS revenue,
    ROUND(SUM(fs.profit), 0)                                    AS profit,
    ROUND(SUM(fs.profit) / NULLIF(SUM(fs.line_total), 0) * 100, 2) AS margin_pct
FROM fact_sales fs
JOIN dim_product p ON fs.product_id = p.product_id
WHERE fs.order_status = 'Delivered'
GROUP BY p.category, p.sub_category
ORDER BY p.category, revenue DESC;

-- ─────────────────────────────────────────────────────────────
-- 10. PRODUCTS WITH DECLINING REVENUE (2022 → 2023)
-- ─────────────────────────────────────────────────────────────

WITH yearly_prod AS (
    SELECT
        fs.product_id,
        p.product_name,
        p.category,
        YEAR(fs.order_date)      AS yr,
        SUM(fs.line_total)       AS revenue
    FROM fact_sales fs
    JOIN dim_product p ON fs.product_id = p.product_id
    WHERE fs.order_status = 'Delivered'
      AND YEAR(fs.order_date) IN (2022, 2023)
    GROUP BY fs.product_id, p.product_name, p.category, YEAR(fs.order_date)
),
pivoted AS (
    SELECT
        product_id,
        product_name,
        category,
        SUM(CASE WHEN yr = 2022 THEN revenue ELSE 0 END) AS rev_2022,
        SUM(CASE WHEN yr = 2023 THEN revenue ELSE 0 END) AS rev_2023
    FROM yearly_prod
    GROUP BY product_id, product_name, category
)
SELECT
    product_id,
    product_name,
    category,
    ROUND(rev_2022, 0)      AS rev_2022,
    ROUND(rev_2023, 0)      AS rev_2023,
    ROUND((rev_2023 - rev_2022) / NULLIF(rev_2022, 0) * 100, 2) AS growth_pct
FROM pivoted
WHERE rev_2022 > 0 AND rev_2023 < rev_2022
ORDER BY growth_pct
LIMIT 20;

-- ─────────────────────────────────────────────────────────────
-- 11. AVERAGE DISCOUNT BY CATEGORY
-- ─────────────────────────────────────────────────────────────

SELECT
    p.category,
    ROUND(AVG(fs.discount) * 100, 2)   AS avg_discount_pct,
    ROUND(MAX(fs.discount) * 100, 2)   AS max_discount_pct,
    SUM(CASE WHEN fs.discount > 0.20 THEN 1 ELSE 0 END) AS lines_over_20pct_discount
FROM fact_sales fs
JOIN dim_product p ON fs.product_id = p.product_id
WHERE fs.order_status = 'Delivered'
GROUP BY p.category
ORDER BY avg_discount_pct DESC;
