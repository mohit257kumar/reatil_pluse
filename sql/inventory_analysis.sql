-- ============================================================
-- RetailPulse — Inventory Analysis Queries
-- ============================================================
-- Covers: current stock levels, stockout risk, days of stock,
--         reorder alerts, inventory turnover, excess stock
-- ============================================================

USE retailpulse;

-- ─────────────────────────────────────────────────────────────
-- 1. CURRENT STOCK SNAPSHOT
-- ─────────────────────────────────────────────────────────────

SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.brand,
    p.stock_quantity,
    p.reorder_level,
    p.lead_time_days,
    CASE
        WHEN p.stock_quantity = 0          THEN 'Out of Stock'
        WHEN p.stock_quantity < p.reorder_level THEN 'Below Reorder Level'
        WHEN p.stock_quantity < p.reorder_level * 1.5 THEN 'Low Stock'
        ELSE 'Adequate'
    END AS stock_status
FROM dim_product p
ORDER BY p.stock_quantity;

-- ─────────────────────────────────────────────────────────────
-- 2. DAILY SALES VELOCITY (avg units sold per day)
--    Using last 90 days of inventory OUT transactions
-- ─────────────────────────────────────────────────────────────

WITH recent_out AS (
    SELECT
        product_id,
        SUM(quantity)  AS units_out,
        COUNT(DISTINCT transaction_date) AS active_days,
        90             AS window_days
    FROM fact_inventory
    WHERE transaction_type = 'OUT'
      AND transaction_date >= DATE_SUB(
            (SELECT MAX(transaction_date) FROM fact_inventory), INTERVAL 90 DAY
          )
    GROUP BY product_id
)
SELECT
    ro.product_id,
    p.product_name,
    p.category,
    p.stock_quantity,
    p.reorder_level,
    ROUND(ro.units_out / ro.window_days, 2)          AS daily_velocity,
    ROUND(
        p.stock_quantity / NULLIF(ro.units_out / ro.window_days, 0), 1
    )                                                 AS days_of_stock_remaining,
    CASE
        WHEN p.stock_quantity / NULLIF(ro.units_out / ro.window_days, 0) < 7  THEN 'CRITICAL (< 7 days)'
        WHEN p.stock_quantity / NULLIF(ro.units_out / ro.window_days, 0) < 14 THEN 'LOW (< 14 days)'
        WHEN p.stock_quantity / NULLIF(ro.units_out / ro.window_days, 0) < 30 THEN 'MODERATE (< 30 days)'
        ELSE 'ADEQUATE'
    END                                              AS stockout_risk
FROM recent_out ro
JOIN dim_product p ON ro.product_id = p.product_id
ORDER BY days_of_stock_remaining;

-- ─────────────────────────────────────────────────────────────
-- 3. REORDER ALERT — PRODUCTS NEEDING IMMEDIATE REORDER
-- ─────────────────────────────────────────────────────────────

WITH velocity AS (
    SELECT
        product_id,
        ROUND(SUM(quantity) / 90.0, 2) AS daily_velocity
    FROM fact_inventory
    WHERE transaction_type = 'OUT'
      AND transaction_date >= DATE_SUB(
            (SELECT MAX(transaction_date) FROM fact_inventory), INTERVAL 90 DAY
          )
    GROUP BY product_id
)
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.stock_quantity,
    p.reorder_level,
    p.lead_time_days,
    v.daily_velocity,
    ROUND(v.daily_velocity * p.lead_time_days, 0)    AS demand_during_lead_time,
    ROUND(p.stock_quantity / NULLIF(v.daily_velocity, 0), 1) AS days_of_stock,
    ROUND(v.daily_velocity * 30, 0)                  AS suggested_reorder_qty   -- 30-day supply
FROM dim_product p
JOIN velocity v ON p.product_id = v.product_id
WHERE p.stock_quantity <= p.reorder_level
   OR p.stock_quantity / NULLIF(v.daily_velocity, 0) <= p.lead_time_days
ORDER BY days_of_stock;

-- ─────────────────────────────────────────────────────────────
-- 4. INVENTORY TURNOVER RATIO (by category)
--    Turnover = COGS / Average Inventory Value
-- ─────────────────────────────────────────────────────────────

SELECT
    p.category,
    ROUND(SUM(fs.cost_total), 0)                            AS cogs,
    ROUND(AVG(p.stock_quantity * p.cost_price), 0)          AS avg_inventory_value,
    ROUND(
        SUM(fs.cost_total)
        / NULLIF(AVG(p.stock_quantity * p.cost_price), 0), 2
    )                                                       AS inventory_turnover,
    ROUND(
        365 / NULLIF(
            SUM(fs.cost_total) / NULLIF(AVG(p.stock_quantity * p.cost_price), 0), 0
        ), 0
    )                                                       AS days_inventory_outstanding
FROM fact_sales fs
JOIN dim_product p ON fs.product_id = p.product_id
WHERE fs.order_status = 'Delivered'
GROUP BY p.category
ORDER BY inventory_turnover DESC;

-- ─────────────────────────────────────────────────────────────
-- 5. EXCESS INVENTORY (High stock, low velocity)
-- ─────────────────────────────────────────────────────────────

WITH velocity AS (
    SELECT
        product_id,
        ROUND(SUM(quantity) / 90.0, 2) AS daily_velocity
    FROM fact_inventory
    WHERE transaction_type = 'OUT'
      AND transaction_date >= DATE_SUB(
            (SELECT MAX(transaction_date) FROM fact_inventory), INTERVAL 90 DAY
          )
    GROUP BY product_id
),
stock_days AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.stock_quantity,
        p.cost_price,
        v.daily_velocity,
        ROUND(p.stock_quantity / NULLIF(v.daily_velocity, 0), 0) AS days_of_stock,
        ROUND(p.stock_quantity * p.cost_price, 2)                AS tied_up_capital
    FROM dim_product p
    JOIN velocity v ON p.product_id = v.product_id
)
SELECT *
FROM stock_days
WHERE days_of_stock > 90
  AND stock_quantity > 50
ORDER BY tied_up_capital DESC
LIMIT 25;

-- ─────────────────────────────────────────────────────────────
-- 6. MONTHLY INVENTORY FLOW (IN vs OUT)
-- ─────────────────────────────────────────────────────────────

SELECT
    DATE_FORMAT(transaction_date, '%Y-%m')  AS txn_month,
    SUM(CASE WHEN transaction_type = 'IN'  THEN quantity ELSE 0 END) AS units_in,
    SUM(CASE WHEN transaction_type = 'OUT' THEN quantity ELSE 0 END) AS units_out,
    SUM(CASE WHEN transaction_type = 'ADJUSTMENT' THEN quantity ELSE 0 END) AS adjustments,
    SUM(CASE WHEN transaction_type = 'IN'  THEN quantity ELSE 0 END)
    - SUM(CASE WHEN transaction_type = 'OUT' THEN quantity ELSE 0 END)
    + SUM(CASE WHEN transaction_type = 'ADJUSTMENT' THEN quantity ELSE 0 END) AS net_flow
FROM fact_inventory
GROUP BY txn_month
ORDER BY txn_month;

-- ─────────────────────────────────────────────────────────────
-- 7. PRODUCTS WITH ZERO STOCK AND HIGH DEMAND
-- ─────────────────────────────────────────────────────────────

WITH velocity AS (
    SELECT product_id, SUM(quantity) / 90.0 AS daily_velocity
    FROM fact_inventory
    WHERE transaction_type = 'OUT'
      AND transaction_date >= DATE_SUB(
            (SELECT MAX(transaction_date) FROM fact_inventory), INTERVAL 90 DAY
          )
    GROUP BY product_id
)
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.stock_quantity,
    ROUND(v.daily_velocity, 2)              AS daily_velocity,
    ROUND(v.daily_velocity * 30, 0)         AS est_monthly_demand,
    ROUND(v.daily_velocity * p.lead_time_days, 0) AS emergency_reorder_qty
FROM dim_product p
JOIN velocity v ON p.product_id = v.product_id
WHERE p.stock_quantity = 0
  AND v.daily_velocity > (SELECT AVG(daily_velocity) FROM velocity)
ORDER BY v.daily_velocity DESC;

-- ─────────────────────────────────────────────────────────────
-- 8. STORE-LEVEL INVENTORY POSITION
--    (Net stock per store from transaction history)
-- ─────────────────────────────────────────────────────────────

SELECT
    fi.store_id,
    s.city,
    s.region,
    p.category,
    SUM(CASE WHEN fi.transaction_type = 'IN'  THEN fi.quantity ELSE 0 END) AS total_in,
    SUM(CASE WHEN fi.transaction_type = 'OUT' THEN fi.quantity ELSE 0 END) AS total_out,
    SUM(CASE WHEN fi.transaction_type = 'IN'  THEN fi.quantity
             WHEN fi.transaction_type = 'OUT' THEN -fi.quantity
             ELSE fi.quantity END)                                          AS net_stock
FROM fact_inventory fi
JOIN dim_store s   ON fi.store_id   = s.store_id
JOIN dim_product p ON fi.product_id = p.product_id
GROUP BY fi.store_id, s.city, s.region, p.category
ORDER BY fi.store_id, p.category;
