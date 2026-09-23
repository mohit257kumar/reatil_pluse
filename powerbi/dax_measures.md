# RetailPulse — Power BI DAX Measures

All DAX measures used in the RetailPulse 5-page Power BI dashboard.
Format the `FactSales` and `FactInventory` tables in Power BI using the star schema defined in `sql/schema.sql`.

---

## Table: FactSales

### Core Revenue Measures

```dax
-- Total Revenue
Total Revenue =
CALCULATE(
    SUMX(FactSales, FactSales[line_total]),
    FactSales[order_status] = "Delivered"
)

-- Total Cost
Total Cost =
CALCULATE(
    SUMX(FactSales, FactSales[cost_total]),
    FactSales[order_status] = "Delivered"
)

-- Total Profit
Total Profit =
[Total Revenue] - [Total Cost]

-- Gross Margin %
Gross Margin % =
DIVIDE([Total Profit], [Total Revenue], 0) * 100

-- Total Orders
Total Orders =
CALCULATE(
    DISTINCTCOUNT(FactSales[order_id]),
    FactSales[order_status] = "Delivered"
)

-- Total Units Sold
Total Units Sold =
CALCULATE(
    SUM(FactSales[quantity]),
    FactSales[order_status] = "Delivered"
)

-- Average Order Value (AOV)
Avg Order Value =
DIVIDE([Total Revenue], [Total Orders], 0)

-- Unique Customers
Unique Customers =
CALCULATE(
    DISTINCTCOUNT(FactSales[customer_id]),
    FactSales[order_status] = "Delivered"
)
```

### Time Intelligence Measures

```dax
-- Revenue Last Month
Revenue LM =
CALCULATE(
    [Total Revenue],
    DATEADD(DimDate[date_id], -1, MONTH)
)

-- Revenue Last Year (same period)
Revenue LY =
CALCULATE(
    [Total Revenue],
    SAMEPERIODLASTYEAR(DimDate[date_id])
)

-- Revenue YoY Growth %
Revenue YoY % =
DIVIDE([Total Revenue] - [Revenue LY], [Revenue LY], BLANK()) * 100

-- Revenue Month-over-Month Growth %
Revenue MoM % =
DIVIDE([Total Revenue] - [Revenue LM], [Revenue LM], BLANK()) * 100

-- Year-to-Date Revenue
Revenue YTD =
CALCULATE(
    [Total Revenue],
    DATESYTD(DimDate[date_id])
)

-- Previous Year YTD Revenue
Revenue PYTD =
CALCULATE(
    [Total Revenue],
    DATESYTD(DATEADD(DimDate[date_id], -1, YEAR))
)

-- YTD vs PYTD %
YTD vs PYTD % =
DIVIDE([Revenue YTD] - [Revenue PYTD], [Revenue PYTD], BLANK()) * 100

-- Rolling 3-Month Revenue
Revenue Rolling 3M =
CALCULATE(
    [Total Revenue],
    DATESINPERIOD(DimDate[date_id], LASTDATE(DimDate[date_id]), -3, MONTH)
)

-- Rolling 12-Month Revenue
Revenue Rolling 12M =
CALCULATE(
    [Total Revenue],
    DATESINPERIOD(DimDate[date_id], LASTDATE(DimDate[date_id]), -12, MONTH)
)
```

### Profit Measures

```dax
-- Profit Last Year
Profit LY =
CALCULATE(
    [Total Profit],
    SAMEPERIODLASTYEAR(DimDate[date_id])
)

-- Profit YoY Growth %
Profit YoY % =
DIVIDE([Total Profit] - [Profit LY], [Profit LY], BLANK()) * 100

-- Profit YTD
Profit YTD =
CALCULATE(
    [Total Profit],
    DATESYTD(DimDate[date_id])
)

-- Average Discount %
Avg Discount % =
CALCULATE(
    AVERAGE(FactSales[discount]),
    FactSales[order_status] = "Delivered"
) * 100
```

### Customer Measures

```dax
-- New Customers (first purchase in selected period)
New Customers =
CALCULATE(
    DISTINCTCOUNT(FactSales[customer_id]),
    FILTER(
        FactSales,
        CALCULATE(
            MIN(FactSales[order_date]),
            ALLEXCEPT(FactSales, FactSales[customer_id])
        ) >= MIN(DimDate[date_id])
        && CALCULATE(
            MIN(FactSales[order_date]),
            ALLEXCEPT(FactSales, FactSales[customer_id])
        ) <= MAX(DimDate[date_id])
    )
)

-- Returning Customers
Returning Customers =
[Unique Customers] - [New Customers]

-- Revenue per Customer
Revenue per Customer =
DIVIDE([Total Revenue], [Unique Customers], 0)

-- Repeat Purchase Rate %
Repeat Rate % =
DIVIDE(
    CALCULATE(
        DISTINCTCOUNT(FactSales[customer_id]),
        FILTER(
            VALUES(FactSales[customer_id]),
            CALCULATE(DISTINCTCOUNT(FactSales[order_id])) > 1
        )
    ),
    [Unique Customers],
    0
) * 100
```

---

## Table: FactInventory

### Inventory Measures

```dax
-- Total Units IN
Total Units IN =
CALCULATE(
    SUM(FactInventory[quantity]),
    FactInventory[transaction_type] = "IN"
)

-- Total Units OUT
Total Units OUT =
CALCULATE(
    SUM(FactInventory[quantity]),
    FactInventory[transaction_type] = "OUT"
)

-- Net Stock Movement
Net Stock Movement =
[Total Units IN] - [Total Units OUT]

-- Products Below Reorder Level
Products Below Reorder =
CALCULATE(
    COUNTROWS(DimProduct),
    DimProduct[stock_quantity] < DimProduct[reorder_level]
)

-- Out of Stock Products
Out of Stock Products =
CALCULATE(
    COUNTROWS(DimProduct),
    DimProduct[stock_quantity] = 0
)

-- Total Inventory Value (at cost)
Total Inventory Value =
SUMX(DimProduct, DimProduct[stock_quantity] * DimProduct[cost_price])
```

---

## KPI Card Measures (for card visuals)

```dax
-- Revenue vs Target (example: static target)
Revenue vs Target % =
VAR Target = 500000000  -- ₹50 Cr annual target
RETURN DIVIDE([Revenue YTD], Target, 0) * 100

-- Formatted Revenue (crores)
Revenue Cr =
FORMAT([Total Revenue] / 10000000, "₹#,##0.0") & " Cr"

-- Formatted Profit (crores)
Profit Cr =
FORMAT([Total Profit] / 10000000, "₹#,##0.0") & " Cr"
```

---

## Calculated Columns (in FactSales)

```dax
-- Profit Per Line (calculated column)
Profit = FactSales[line_total] - FactSales[cost_total]

-- Margin % Per Line (calculated column)
Margin % = DIVIDE(FactSales[Profit], FactSales[line_total], 0) * 100

-- Order Year (calculated column)
Order Year = YEAR(FactSales[order_date])

-- Order Month (calculated column)
Order Month = MONTH(FactSales[order_date])

-- Order Quarter (calculated column)
Order Quarter = "Q" & QUARTER(FactSales[order_date])
```

---

## Dashboard Page Mapping

| Page | Key Measures Used |
|------|-------------------|
| **1. Executive Summary** | Total Revenue, Total Profit, Gross Margin %, Total Orders, AOV, Revenue YoY %, Revenue YTD |
| **2. Sales Trends** | Revenue Rolling 12M, Revenue MoM %, Revenue YoY %, Revenue by Channel, Seasonality |
| **3. Customer Analytics** | Unique Customers, New Customers, Returning Customers, Repeat Rate %, Revenue per Customer, RFM Segment |
| **4. Product & Category** | Total Revenue by Category, Gross Margin %, Top 10 Products, Avg Discount %, Velocity Quartile |
| **5. Inventory & Stores** | Total Inventory Value, Products Below Reorder, Out of Stock Products, Store Revenue, Region Margin % |

---

## Power BI Data Model Relationships

```
DimDate       [date_id]       ← FactSales    [order_date]       (Many-to-One)
DimCustomer   [customer_id]   ← FactSales    [customer_id]      (Many-to-One)
DimProduct    [product_id]    ← FactSales    [product_id]       (Many-to-One)
DimStore      [store_id]      ← FactSales    [store_id]         (Many-to-One)
DimProduct    [product_id]    ← FactInventory[product_id]       (Many-to-One)
DimStore      [store_id]      ← FactInventory[store_id]         (Many-to-One)
DimDate       [date_id]       ← FactInventory[transaction_date] (Many-to-One)
```

> **Note:** Mark `DimDate` as a Date Table in Power BI (Right-click → Mark as Date Table → select `date_id` column) to enable Time Intelligence functions correctly.
