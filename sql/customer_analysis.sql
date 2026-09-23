-- ============================================================
-- RetailPulse — Customer Analysis Queries
-- ============================================================
-- Covers: customer count, new vs returning, repeat rate,
--         RFM segmentation (SQL), top customers, LTV, churn risk
-- ============================================================

USE retailpulse;

-- ─────────────────────────────────────────────────────────────
-- 1. TOTAL CUSTOMERS & BASIC DEMOGRAPHICS
-- ─────────────────────────────────────────────────────────────

SELECT
    COUNT(*)                              AS total_customers,
    ROUND(AVG(age), 1)                    AS avg_age,
    MIN(age)                              AS min_age,
    MAX(age)                              AS max_age,
    SUM(CASE WHEN gender = 'Male'   THEN 1 ELSE 0 END)  AS male_count,
    SUM(CASE WHEN gender = 'Female' THEN 1 ELSE 0 END)  AS female_count
FROM dim_customer;

-- ─────────────────────────────────────────────────────────────
-- 2. NEW CUSTOMERS BY MONTH
-- ─────────────────────────────────────────────────────────────

SELECT
    DATE_FORMAT(registration_date, '%Y-%m') AS reg_month,
    COUNT(*)                                AS new_customers
FROM dim_customer
GROUP BY reg_month
ORDER BY reg_month;

-- ─────────────────────────────────────────────────────────────
-- 3. NEW vs RETURNING CUSTOMERS PER YEAR
-- ─────────────────────────────────────────────────────────────

WITH first_orders AS (
    SELECT customer_id, MIN(order_date) AS first_order_date
    FROM fact_sales
    WHERE order_status = 'Delivered'
    GROUP BY customer_id
)
SELECT
    YEAR(fo.first_order_date)                                   AS yr,
    COUNT(DISTINCT fo.customer_id)                              AS new_customers,
    COUNT(DISTINCT fs.customer_id) - COUNT(DISTINCT fo.customer_id) AS returning_customers
FROM fact_sales fs
LEFT JOIN first_orders fo
       ON fs.customer_id = fo.customer_id
       AND YEAR(fo.first_order_date) = YEAR(fs.order_date)
WHERE fs.order_status = 'Delivered'
GROUP BY YEAR(fo.first_order_date)
ORDER BY yr;

-- ─────────────────────────────────────────────────────────────
-- 4. REPEAT PURCHASE RATE
-- ─────────────────────────────────────────────────────────────

SELECT
    COUNT(DISTINCT customer_id)                                     AS total_buyers,
    SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END)               AS repeat_buyers,
    ROUND(
        SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END)
        / COUNT(DISTINCT customer_id) * 100, 2
    )                                                               AS repeat_rate_pct
FROM (
    SELECT customer_id, COUNT(DISTINCT order_id) AS order_count
    FROM fact_sales
    WHERE order_status = 'Delivered'
    GROUP BY customer_id
) t;

-- ─────────────────────────────────────────────────────────────
-- 5. TOP 20 CUSTOMERS BY LIFETIME VALUE
-- ─────────────────────────────────────────────────────────────

SELECT
    customer_id,
    customer_name,
    city,
    region,
    total_orders,
    ROUND(total_revenue, 0)         AS total_revenue,
    ROUND(total_profit, 0)          AS total_profit,
    ROUND(avg_order_value, 2)       AS avg_order_value,
    customer_lifespan_days
FROM vw_customer_ltv
ORDER BY total_revenue DESC
LIMIT 20;

-- ─────────────────────────────────────────────────────────────
-- 6. CUSTOMER REVENUE CONCENTRATION (PARETO)
-- ─────────────────────────────────────────────────────────────

WITH ranked AS (
    SELECT
        customer_id,
        SUM(line_total)  AS revenue,
        NTILE(10)  OVER (ORDER BY SUM(line_total) DESC) AS decile
    FROM fact_sales
    WHERE order_status = 'Delivered'
    GROUP BY customer_id
)
SELECT
    decile,
    COUNT(*)                                              AS customers,
    ROUND(SUM(revenue), 0)                               AS revenue,
    ROUND(SUM(revenue) / SUM(SUM(revenue)) OVER () * 100, 2) AS pct_of_revenue
FROM ranked
GROUP BY decile
ORDER BY decile;

-- ─────────────────────────────────────────────────────────────
-- 7. RFM SCORING (Pure SQL)
--    Reference date = MAX order_date + 1 day
-- ─────────────────────────────────────────────────────────────

WITH ref AS (
    SELECT DATE_ADD(MAX(order_date), INTERVAL 1 DAY) AS ref_date
    FROM fact_sales
    WHERE order_status = 'Delivered'
),
rfm_raw AS (
    SELECT
        fs.customer_id,
        DATEDIFF((SELECT ref_date FROM ref), MAX(fs.order_date)) AS recency,
        COUNT(DISTINCT fs.order_id)                              AS frequency,
        ROUND(SUM(fs.line_total), 2)                             AS monetary
    FROM fact_sales fs
    WHERE fs.order_status = 'Delivered'
    GROUP BY fs.customer_id
),
rfm_scored AS (
    SELECT
        customer_id,
        recency,
        frequency,
        monetary,
        NTILE(5) OVER (ORDER BY recency DESC)    AS r_score,
        NTILE(5) OVER (ORDER BY frequency)       AS f_score,
        NTILE(5) OVER (ORDER BY monetary)        AS m_score
    FROM rfm_raw
)
SELECT
    rs.customer_id,
    c.customer_name,
    c.region,
    rs.recency,
    rs.frequency,
    ROUND(rs.monetary, 0)                                   AS monetary,
    rs.r_score,
    rs.f_score,
    rs.m_score,
    CONCAT(rs.r_score, rs.f_score, rs.m_score)              AS rfm_score,
    rs.r_score + rs.f_score + rs.m_score                    AS rfm_total,
    CASE
        WHEN rs.r_score >= 4 AND rs.f_score >= 4 AND rs.m_score >= 4 THEN 'Champions'
        WHEN rs.r_score >= 3 AND rs.f_score >= 3 AND rs.m_score >= 3 THEN 'Loyal Customers'
        WHEN rs.r_score >= 4 AND rs.f_score <= 2                      THEN 'New Customers'
        WHEN rs.r_score >= 3 AND rs.m_score <= 2                      THEN 'Promising'
        WHEN rs.r_score <= 2 AND rs.f_score >= 3 AND rs.m_score >= 3  THEN 'At Risk'
        WHEN rs.r_score <= 2 AND rs.f_score >= 4 AND rs.m_score >= 4  THEN 'Can''t Lose Them'
        WHEN rs.r_score <= 2 AND rs.f_score <= 2 AND rs.m_score <= 2  THEN 'Lost'
        WHEN rs.r_score = 2  AND rs.f_score <= 2                      THEN 'About to Sleep'
        ELSE 'Hibernating'
    END                                                     AS segment
FROM rfm_scored rs
JOIN dim_customer c ON rs.customer_id = c.customer_id
ORDER BY rfm_total DESC;

-- ─────────────────────────────────────────────────────────────
-- 8. CUSTOMERS BY REGION
-- ─────────────────────────────────────────────────────────────

SELECT
    c.region,
    COUNT(DISTINCT c.customer_id)                           AS customer_count,
    COUNT(DISTINCT fs.order_id)                             AS orders,
    ROUND(SUM(fs.line_total), 0)                            AS revenue,
    ROUND(SUM(fs.line_total) / COUNT(DISTINCT c.customer_id), 2) AS revenue_per_customer
FROM dim_customer c
LEFT JOIN fact_sales fs ON c.customer_id = fs.customer_id AND fs.order_status = 'Delivered'
GROUP BY c.region
ORDER BY revenue DESC;

-- ─────────────────────────────────────────────────────────────
-- 9. CUSTOMER ORDER FREQUENCY DISTRIBUTION
-- ─────────────────────────────────────────────────────────────

SELECT
    order_count,
    COUNT(*)                              AS customer_count,
    ROUND(COUNT(*) * 100.0 /
          SUM(COUNT(*)) OVER (), 2)       AS pct_of_customers
FROM (
    SELECT customer_id, COUNT(DISTINCT order_id) AS order_count
    FROM fact_sales
    WHERE order_status = 'Delivered'
    GROUP BY customer_id
) t
GROUP BY order_count
ORDER BY order_count;

-- ─────────────────────────────────────────────────────────────
-- 10. CHURN RISK — CUSTOMERS WHO HAVEN'T ORDERED IN 180+ DAYS
-- ─────────────────────────────────────────────────────────────

WITH last_orders AS (
    SELECT
        customer_id,
        MAX(order_date)   AS last_order_date,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(line_total)   AS total_revenue
    FROM fact_sales
    WHERE order_status = 'Delivered'
    GROUP BY customer_id
),
ref AS (
    SELECT DATE_ADD(MAX(order_date), INTERVAL 1 DAY) AS ref_date
    FROM fact_sales
    WHERE order_status = 'Delivered'
)
SELECT
    lo.customer_id,
    c.customer_name,
    c.region,
    lo.last_order_date,
    DATEDIFF((SELECT ref_date FROM ref), lo.last_order_date) AS days_since_last_order,
    lo.total_orders,
    ROUND(lo.total_revenue, 0)                               AS total_revenue
FROM last_orders lo
JOIN dim_customer c ON lo.customer_id = c.customer_id
CROSS JOIN ref r
WHERE DATEDIFF(r.ref_date, lo.last_order_date) >= 180
ORDER BY lo.total_revenue DESC
LIMIT 50;
