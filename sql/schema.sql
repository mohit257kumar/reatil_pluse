-- ============================================================
-- RetailPulse — Database Schema (MySQL 8.0)
-- ============================================================
-- Star Schema for Power BI + SQL Analytics
--
-- Fact Tables:   fact_sales, fact_inventory
-- Dimension Tables: dim_customer, dim_product, dim_store, dim_date
-- ============================================================

CREATE DATABASE IF NOT EXISTS retailpulse
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE retailpulse;

-- ─────────────────────────────────────────────────────────────
-- DIMENSION: dim_date
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS dim_date (
    date_id         DATE         NOT NULL,
    day             TINYINT      NOT NULL,
    month           TINYINT      NOT NULL,
    month_name      VARCHAR(12)  NOT NULL,
    quarter         TINYINT      NOT NULL,
    year            SMALLINT     NOT NULL,
    week_of_year    TINYINT      NOT NULL,
    day_of_week     TINYINT      NOT NULL,   -- 1=Monday … 7=Sunday
    day_name        VARCHAR(12)  NOT NULL,
    is_weekend      TINYINT(1)   NOT NULL DEFAULT 0,
    is_holiday      TINYINT(1)   NOT NULL DEFAULT 0,
    fiscal_year     SMALLINT     NOT NULL,   -- Indian FY: Apr–Mar
    fiscal_quarter  TINYINT      NOT NULL,
    PRIMARY KEY (date_id)
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
-- DIMENSION: dim_customer
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id       VARCHAR(10)  NOT NULL,
    customer_name     VARCHAR(120) NOT NULL,
    gender            VARCHAR(10),
    age               TINYINT,
    city              VARCHAR(50)  NOT NULL,
    state             VARCHAR(60)  NOT NULL,
    region            VARCHAR(20)  NOT NULL,
    registration_date DATE         NOT NULL,
    PRIMARY KEY (customer_id),
    INDEX idx_region   (region),
    INDEX idx_city     (city),
    INDEX idx_reg_date (registration_date)
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
-- DIMENSION: dim_product
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS dim_product (
    product_id       VARCHAR(8)    NOT NULL,
    product_name     VARCHAR(200)  NOT NULL,
    category         VARCHAR(60)   NOT NULL,
    sub_category     VARCHAR(80)   NOT NULL,
    brand            VARCHAR(80)   NOT NULL,
    supplier         VARCHAR(120)  NOT NULL,
    cost_price       DECIMAL(12,2) NOT NULL,
    selling_price    DECIMAL(12,2) NOT NULL,
    stock_quantity   INT           NOT NULL DEFAULT 0,
    reorder_level    INT           NOT NULL DEFAULT 20,
    lead_time_days   TINYINT       NOT NULL DEFAULT 7,
    PRIMARY KEY (product_id),
    INDEX idx_category (category),
    INDEX idx_brand    (brand)
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
-- DIMENSION: dim_store
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS dim_store (
    store_id      VARCHAR(8)   NOT NULL,
    store_name    VARCHAR(150) NOT NULL,
    city          VARCHAR(50)  NOT NULL,
    state         VARCHAR(60)  NOT NULL,
    region        VARCHAR(20)  NOT NULL,
    store_type    VARCHAR(20)  NOT NULL,
    opening_date  DATE,
    PRIMARY KEY (store_id),
    INDEX idx_region (region),
    INDEX idx_city   (city)
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
-- STAGING: orders  (raw transactional header)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS orders (
    order_id        VARCHAR(10)  NOT NULL,
    customer_id     VARCHAR(10)  NOT NULL,
    store_id        VARCHAR(8)   NOT NULL,
    order_date      DATE         NOT NULL,
    order_status    VARCHAR(20)  NOT NULL,
    payment_method  VARCHAR(30),
    sales_channel   VARCHAR(20)  NOT NULL,
    PRIMARY KEY (order_id),
    INDEX idx_customer   (customer_id),
    INDEX idx_store      (store_id),
    INDEX idx_order_date (order_date),
    INDEX idx_status     (order_status),
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    CONSTRAINT fk_orders_store    FOREIGN KEY (store_id)    REFERENCES dim_store(store_id)
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
-- STAGING: order_details (raw line items)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS order_details (
    order_detail_id VARCHAR(12)   NOT NULL,
    order_id        VARCHAR(10)   NOT NULL,
    product_id      VARCHAR(8)    NOT NULL,
    quantity        SMALLINT      NOT NULL,
    unit_price      DECIMAL(12,2) NOT NULL,
    discount        DECIMAL(5,4)  NOT NULL DEFAULT 0,
    line_total      DECIMAL(14,2) NOT NULL,
    PRIMARY KEY (order_detail_id),
    INDEX idx_order   (order_id),
    INDEX idx_product (product_id),
    CONSTRAINT fk_od_order   FOREIGN KEY (order_id)   REFERENCES orders(order_id),
    CONSTRAINT fk_od_product FOREIGN KEY (product_id) REFERENCES dim_product(product_id)
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
-- STAGING: inventory_transactions
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS inventory_transactions (
    transaction_id    VARCHAR(10)  NOT NULL,
    product_id        VARCHAR(8)   NOT NULL,
    store_id          VARCHAR(8)   NOT NULL,
    transaction_date  DATE         NOT NULL,
    transaction_type  VARCHAR(12)  NOT NULL,   -- IN / OUT / ADJUSTMENT
    quantity          INT          NOT NULL,
    PRIMARY KEY (transaction_id),
    INDEX idx_product (product_id),
    INDEX idx_store   (store_id),
    INDEX idx_date    (transaction_date),
    INDEX idx_type    (transaction_type),
    CONSTRAINT fk_inv_product FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
    CONSTRAINT fk_inv_store   FOREIGN KEY (store_id)   REFERENCES dim_store(store_id)
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
-- FACT: fact_sales  (denormalised for analytics & Power BI)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fact_sales (
    sale_id          BIGINT        NOT NULL AUTO_INCREMENT,
    order_detail_id  VARCHAR(12)   NOT NULL,
    order_id         VARCHAR(10)   NOT NULL,
    order_date       DATE          NOT NULL,
    customer_id      VARCHAR(10)   NOT NULL,
    product_id       VARCHAR(8)    NOT NULL,
    store_id         VARCHAR(8)    NOT NULL,
    sales_channel    VARCHAR(20)   NOT NULL,
    payment_method   VARCHAR(30),
    order_status     VARCHAR(20)   NOT NULL,
    quantity         SMALLINT      NOT NULL,
    unit_price       DECIMAL(12,2) NOT NULL,
    discount         DECIMAL(5,4)  NOT NULL DEFAULT 0,
    line_total       DECIMAL(14,2) NOT NULL,   -- revenue (unit_price × qty)
    cost_total       DECIMAL(14,2) NOT NULL,   -- cost_price × qty
    profit           DECIMAL(14,2) NOT NULL,   -- line_total − cost_total
    margin_pct       DECIMAL(7,4),             -- profit / line_total × 100
    PRIMARY KEY (sale_id),
    UNIQUE KEY uq_od (order_detail_id),
    INDEX idx_date     (order_date),
    INDEX idx_customer (customer_id),
    INDEX idx_product  (product_id),
    INDEX idx_store    (store_id),
    INDEX idx_channel  (sales_channel),
    INDEX idx_status   (order_status),
    CONSTRAINT fk_fs_customer FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    CONSTRAINT fk_fs_product  FOREIGN KEY (product_id)  REFERENCES dim_product(product_id),
    CONSTRAINT fk_fs_store    FOREIGN KEY (store_id)    REFERENCES dim_store(store_id)
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
-- FACT: fact_inventory (denormalised inventory fact)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fact_inventory (
    inv_id           BIGINT       NOT NULL AUTO_INCREMENT,
    transaction_id   VARCHAR(10)  NOT NULL,
    product_id       VARCHAR(8)   NOT NULL,
    store_id         VARCHAR(8)   NOT NULL,
    transaction_date DATE         NOT NULL,
    transaction_type VARCHAR(12)  NOT NULL,
    quantity         INT          NOT NULL,
    PRIMARY KEY (inv_id),
    UNIQUE KEY uq_txn (transaction_id),
    INDEX idx_product (product_id),
    INDEX idx_store   (store_id),
    INDEX idx_date    (transaction_date),
    CONSTRAINT fk_fi_product FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
    CONSTRAINT fk_fi_store   FOREIGN KEY (store_id)   REFERENCES dim_store(store_id)
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
-- POPULATE dim_date (2020-01-01 to 2024-12-31)
-- Run this once after schema creation.
-- ─────────────────────────────────────────────────────────────
DROP PROCEDURE IF EXISTS sp_populate_dim_date;
DELIMITER $$
CREATE PROCEDURE sp_populate_dim_date(IN start_date DATE, IN end_date DATE)
BEGIN
    DECLARE cur_date DATE DEFAULT start_date;
    WHILE cur_date <= end_date DO
        INSERT IGNORE INTO dim_date (
            date_id, day, month, month_name, quarter, year,
            week_of_year, day_of_week, day_name, is_weekend,
            is_holiday, fiscal_year, fiscal_quarter
        )
        VALUES (
            cur_date,
            DAY(cur_date),
            MONTH(cur_date),
            MONTHNAME(cur_date),
            QUARTER(cur_date),
            YEAR(cur_date),
            WEEK(cur_date, 3),
            DAYOFWEEK(cur_date),
            DAYNAME(cur_date),
            IF(DAYOFWEEK(cur_date) IN (1, 7), 1, 0),
            0,
            -- Indian fiscal year: Apr–Mar
            IF(MONTH(cur_date) >= 4, YEAR(cur_date), YEAR(cur_date) - 1),
            CASE
                WHEN MONTH(cur_date) IN (4,5,6)   THEN 1
                WHEN MONTH(cur_date) IN (7,8,9)   THEN 2
                WHEN MONTH(cur_date) IN (10,11,12) THEN 3
                ELSE 4
            END
        );
        SET cur_date = DATE_ADD(cur_date, INTERVAL 1 DAY);
    END WHILE;
END$$
DELIMITER ;

-- Execute: CALL sp_populate_dim_date('2020-01-01', '2024-12-31');

-- ─────────────────────────────────────────────────────────────
-- VIEWS (convenience views for SQL analytics)
-- ─────────────────────────────────────────────────────────────

-- Monthly revenue summary
CREATE OR REPLACE VIEW vw_monthly_revenue AS
SELECT
    YEAR(order_date)              AS year,
    MONTH(order_date)             AS month,
    DATE_FORMAT(order_date, '%Y-%m') AS year_month,
    COUNT(DISTINCT order_id)      AS orders,
    SUM(line_total)               AS revenue,
    SUM(cost_total)               AS cost,
    SUM(profit)                   AS profit,
    ROUND(SUM(profit) / NULLIF(SUM(line_total), 0) * 100, 2) AS margin_pct
FROM fact_sales
WHERE order_status = 'Delivered'
GROUP BY YEAR(order_date), MONTH(order_date), DATE_FORMAT(order_date, '%Y-%m');

-- Product performance summary
CREATE OR REPLACE VIEW vw_product_performance AS
SELECT
    fs.product_id,
    p.product_name,
    p.category,
    p.sub_category,
    p.brand,
    COUNT(DISTINCT fs.order_id)  AS orders,
    SUM(fs.quantity)             AS units_sold,
    SUM(fs.line_total)           AS revenue,
    SUM(fs.profit)               AS profit,
    ROUND(SUM(fs.profit) / NULLIF(SUM(fs.line_total), 0) * 100, 2) AS margin_pct,
    AVG(fs.discount) * 100       AS avg_discount_pct
FROM fact_sales fs
JOIN dim_product p ON fs.product_id = p.product_id
WHERE fs.order_status = 'Delivered'
GROUP BY fs.product_id, p.product_name, p.category, p.sub_category, p.brand;

-- Customer lifetime value summary
CREATE OR REPLACE VIEW vw_customer_ltv AS
SELECT
    fs.customer_id,
    c.customer_name,
    c.city,
    c.region,
    MIN(fs.order_date)                          AS first_order_date,
    MAX(fs.order_date)                          AS last_order_date,
    COUNT(DISTINCT fs.order_id)                 AS total_orders,
    SUM(fs.line_total)                          AS total_revenue,
    SUM(fs.profit)                              AS total_profit,
    ROUND(SUM(fs.line_total) / COUNT(DISTINCT fs.order_id), 2) AS avg_order_value,
    DATEDIFF(MAX(fs.order_date), MIN(fs.order_date)) AS customer_lifespan_days
FROM fact_sales fs
JOIN dim_customer c ON fs.customer_id = c.customer_id
WHERE fs.order_status = 'Delivered'
GROUP BY fs.customer_id, c.customer_name, c.city, c.region;
