"""
RetailPulse â€” Exploratory Data Analysis (EDA)
===============================================
Loads all cleaned datasets and produces 15+ publication-ready charts
saved to reports/figures/.

Charts produced:
  01_monthly_revenue.png          â€” Monthly revenue trend (2021â€“2023)
  02_revenue_by_category.png      â€” Revenue & profit by category (bar)
  03_margin_by_category.png       â€” Gross margin % by category
  04_top10_products.png           â€” Top 10 products by revenue
  05_bottom10_products.png        â€” Bottom 10 products by revenue
  06_orders_by_channel.png        â€” Orders by sales channel (pie)
  07_orders_by_status.png         â€” Order status distribution
  08_revenue_by_region.png        â€” Revenue & profit by region
  09_top10_stores.png             â€” Top 10 stores by revenue
  10_discount_vs_margin.png       â€” Discount rate vs. line margin (scatter)
  11_customer_age_distribution.pngâ€” Customer age histogram
  12_customer_gender_split.png    â€” Gender split (pie)
  13_new_customers_monthly.png    â€” New customer registrations by month
  14_payment_method.png           â€” Payment method distribution
  15_inventory_stock_dist.png     â€” Product stock quantity distribution
  16_revenue_heatmap.png          â€” Revenue heatmap by month Ã— year

Run:
    python python/eda.py

Output:
    reports/figures/*.png
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

warnings.filterwarnings("ignore")

# â”€â”€ Paths â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
PROC_DIR   = os.path.join(BASE_DIR, "..", "data", "processed")
FIG_DIR    = os.path.join(BASE_DIR, "..", "reports", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# â”€â”€ Style â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
sns.set_theme(style="whitegrid", palette="muted")
BRAND_COLORS = ["#2C7BB6", "#D7191C", "#1A9641", "#FDAE61",
                "#ABD9E9", "#F46D43", "#A6D96A", "#762A83",
                "#D9EF8B", "#74ADD1"]
plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.bbox": "tight",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
})

def savefig(name: str):
    path = os.path.join(FIG_DIR, name)
    plt.savefig(path)
    plt.close()
    print(f"  Saved: {name}")


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# LOAD DATA
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def load_data():
    print("Loading cleaned data...")
    customers  = pd.read_csv(os.path.join(PROC_DIR, "customers_clean.csv"), parse_dates=["registration_date"])
    products   = pd.read_csv(os.path.join(PROC_DIR, "products_clean.csv"))
    stores     = pd.read_csv(os.path.join(PROC_DIR, "stores_clean.csv"), parse_dates=["opening_date"])
    orders     = pd.read_csv(os.path.join(PROC_DIR, "orders_clean.csv"), parse_dates=["order_date"])
    order_det  = pd.read_csv(os.path.join(PROC_DIR, "order_details_clean.csv"))
    inventory  = pd.read_csv(os.path.join(PROC_DIR, "inventory_transactions_clean.csv"), parse_dates=["transaction_date"])
    print("  All datasets loaded.")
    return customers, products, stores, orders, order_det, inventory


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# BUILD MASTER SALES TABLE
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def build_sales(orders, order_det, products, stores):
    """Merge orders + order_details + products + stores into one flat table."""
    sales = order_det.merge(orders[["order_id", "order_date", "customer_id",
                                    "store_id", "order_status", "sales_channel",
                                    "payment_method"]], on="order_id", how="left")
    sales = sales.merge(products[["product_id", "product_name", "category",
                                   "sub_category", "brand", "cost_price"]], on="product_id", how="left")
    sales = sales.merge(stores[["store_id", "city", "state", "region"]], on="store_id", how="left")

    # Only delivered orders for revenue/profit analysis
    delivered = sales[sales["order_status"] == "Delivered"].copy()
    delivered["revenue"] = delivered["line_total"]
    delivered["cost"]    = (delivered["cost_price"] * delivered["quantity"]).round(2)
    delivered["profit"]  = (delivered["revenue"] - delivered["cost"]).round(2)
    delivered["margin_pct"] = (delivered["profit"] / delivered["revenue"].replace(0, np.nan) * 100).round(2)
    delivered["year"]   = delivered["order_date"].dt.year
    delivered["month"]  = delivered["order_date"].dt.month
    delivered["year_month"] = delivered["order_date"].dt.to_period("M")

    return delivered


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# CHARTS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def chart_monthly_revenue(sales):
    monthly = (sales.groupby("year_month")["revenue"]
               .sum().reset_index()
               .sort_values("year_month"))
    monthly["year_month_str"] = monthly["year_month"].astype(str)

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(monthly["year_month_str"], monthly["revenue"] / 1e6,
            color=BRAND_COLORS[0], linewidth=2, marker="o", markersize=4)
    ax.fill_between(monthly["year_month_str"], monthly["revenue"] / 1e6,
                    alpha=0.15, color=BRAND_COLORS[0])
    ax.set_title("Monthly Revenue Trend (2021â€“2023)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (â‚¹ Million)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"â‚¹{x:.1f}M"))
    step = max(1, len(monthly) // 12)
    ax.set_xticks(range(0, len(monthly), step))
    ax.set_xticklabels(monthly["year_month_str"].iloc[::step], rotation=45, ha="right")
    plt.tight_layout()
    savefig("01_monthly_revenue.png")


def chart_revenue_by_category(sales):
    cat = (sales.groupby("category")
           .agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
           .sort_values("revenue", ascending=True))

    fig, ax = plt.subplots(figsize=(10, 7))
    y = range(len(cat))
    bars_r = ax.barh(y, cat["revenue"] / 1e6, height=0.4, label="Revenue",
                     color=BRAND_COLORS[0], align="center")
    bars_p = ax.barh([i + 0.42 for i in y], cat["profit"] / 1e6, height=0.4, label="Profit",
                     color=BRAND_COLORS[2], align="center")
    ax.set_yticks([i + 0.21 for i in y])
    ax.set_yticklabels(cat.index)
    ax.set_xlabel("Amount (â‚¹ Million)")
    ax.set_title("Revenue & Profit by Category")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"â‚¹{x:.0f}M"))
    ax.legend()
    plt.tight_layout()
    savefig("02_revenue_by_category.png")


def chart_margin_by_category(sales):
    margin = (sales.groupby("category")["margin_pct"]
              .mean()
              .sort_values(ascending=True))

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = [BRAND_COLORS[2] if v >= margin.mean() else BRAND_COLORS[1] for v in margin]
    ax.barh(margin.index, margin.values, color=colors)
    ax.axvline(margin.mean(), color="black", linestyle="--", linewidth=1.2,
               label=f"Avg: {margin.mean():.1f}%")
    ax.set_xlabel("Gross Margin (%)")
    ax.set_title("Average Gross Margin % by Category")
    ax.legend()
    plt.tight_layout()
    savefig("03_margin_by_category.png")


def chart_top10_products(sales):
    top10 = (sales.groupby("product_name")["revenue"]
             .sum().nlargest(10).sort_values())

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.barh(top10.index, top10.values / 1e6, color=BRAND_COLORS[0])
    ax.set_xlabel("Revenue (â‚¹ Million)")
    ax.set_title("Top 10 Products by Revenue")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"â‚¹{x:.1f}M"))
    plt.tight_layout()
    savefig("04_top10_products.png")


def chart_bottom10_products(sales):
    bottom10 = (sales.groupby("product_name")["revenue"]
                .sum().nsmallest(10).sort_values(ascending=False))

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.barh(bottom10.index, bottom10.values / 1e3, color=BRAND_COLORS[1])
    ax.set_xlabel("Revenue (â‚¹ Thousand)")
    ax.set_title("Bottom 10 Products by Revenue")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"â‚¹{x:.1f}K"))
    plt.tight_layout()
    savefig("05_bottom10_products.png")


def chart_orders_by_channel(orders):
    channel_counts = orders["sales_channel"].value_counts()
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(channel_counts, labels=channel_counts.index, autopct="%1.1f%%",
           colors=BRAND_COLORS[:len(channel_counts)], startangle=90,
           wedgeprops={"edgecolor": "white", "linewidth": 1.5})
    ax.set_title("Orders by Sales Channel")
    plt.tight_layout()
    savefig("06_orders_by_channel.png")


def chart_orders_by_status(orders):
    status_counts = orders["order_status"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(status_counts.index, status_counts.values,
           color=BRAND_COLORS[:len(status_counts)])
    ax.set_xlabel("Order Status")
    ax.set_ylabel("Number of Orders")
    ax.set_title("Order Status Distribution")
    for i, v in enumerate(status_counts):
        ax.text(i, v + 500, f"{v:,}", ha="center", va="bottom", fontsize=10)
    plt.tight_layout()
    savefig("07_orders_by_status.png")


def chart_revenue_by_region(sales):
    region = (sales.groupby("region")
              .agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
              .sort_values("revenue", ascending=False))

    x = range(len(region))
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar([i - 0.2 for i in x], region["revenue"] / 1e6, width=0.4,
           label="Revenue", color=BRAND_COLORS[0])
    ax.bar([i + 0.2 for i in x], region["profit"] / 1e6, width=0.4,
           label="Profit", color=BRAND_COLORS[2])
    ax.set_xticks(list(x))
    ax.set_xticklabels(region.index)
    ax.set_ylabel("Amount (â‚¹ Million)")
    ax.set_title("Revenue & Profit by Region")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"â‚¹{x:.0f}M"))
    ax.legend()
    plt.tight_layout()
    savefig("08_revenue_by_region.png")


def chart_top10_stores(sales):
    top_stores = (sales.groupby("store_id")["revenue"]
                  .sum().nlargest(10).sort_values())

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top_stores.index, top_stores.values / 1e6, color=BRAND_COLORS[3])
    ax.set_xlabel("Revenue (â‚¹ Million)")
    ax.set_title("Top 10 Stores by Revenue")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"â‚¹{x:.1f}M"))
    plt.tight_layout()
    savefig("09_top10_stores.png")


def chart_discount_vs_margin(sales):
    sample = sales.sample(min(5000, len(sales)), random_state=42)
    fig, ax = plt.subplots(figsize=(9, 6))
    sc = ax.scatter(sample["discount"] * 100, sample["margin_pct"],
                    alpha=0.3, s=10, c=sample["margin_pct"],
                    cmap="RdYlGn", vmin=-20, vmax=70)
    plt.colorbar(sc, ax=ax, label="Margin %")
    ax.set_xlabel("Discount (%)")
    ax.set_ylabel("Line Margin (%)")
    ax.set_title("Discount Rate vs. Line Margin")
    # Trend line
    z = np.polyfit(sample["discount"] * 100, sample["margin_pct"].fillna(0), 1)
    p = np.poly1d(z)
    xs = np.linspace(0, 30, 100)
    ax.plot(xs, p(xs), "r--", linewidth=1.5, label=f"Trend (slope={z[0]:.2f})")
    ax.legend()
    plt.tight_layout()
    savefig("10_discount_vs_margin.png")


def chart_customer_age(customers):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(customers["age"].dropna(), bins=30, color=BRAND_COLORS[0],
            edgecolor="white", linewidth=0.5)
    ax.axvline(customers["age"].mean(), color="red", linestyle="--",
               label=f"Mean: {customers['age'].mean():.1f}")
    ax.set_xlabel("Age")
    ax.set_ylabel("Number of Customers")
    ax.set_title("Customer Age Distribution")
    ax.legend()
    plt.tight_layout()
    savefig("11_customer_age_distribution.png")


def chart_customer_gender(customers):
    gender = customers["gender"].value_counts()
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(gender, labels=gender.index, autopct="%1.1f%%",
           colors=BRAND_COLORS[:len(gender)], startangle=90,
           wedgeprops={"edgecolor": "white", "linewidth": 2})
    ax.set_title("Customer Gender Split")
    plt.tight_layout()
    savefig("12_customer_gender_split.png")


def chart_new_customers_monthly(customers):
    customers["reg_month"] = customers["registration_date"].dt.to_period("M")
    monthly_reg = customers.groupby("reg_month").size().reset_index(name="new_customers")
    monthly_reg["reg_month_str"] = monthly_reg["reg_month"].astype(str)

    fig, ax = plt.subplots(figsize=(13, 5))
    ax.bar(monthly_reg["reg_month_str"], monthly_reg["new_customers"],
           color=BRAND_COLORS[4])
    step = max(1, len(monthly_reg) // 12)
    ax.set_xticks(range(0, len(monthly_reg), step))
    ax.set_xticklabels(monthly_reg["reg_month_str"].iloc[::step], rotation=45, ha="right")
    ax.set_ylabel("New Customers")
    ax.set_title("New Customer Registrations by Month")
    plt.tight_layout()
    savefig("13_new_customers_monthly.png")


def chart_payment_method(orders):
    pm = orders["payment_method"].value_counts()
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(pm.index, pm.values, color=BRAND_COLORS[:len(pm)])
    ax.set_ylabel("Number of Orders")
    ax.set_title("Payment Method Distribution")
    for i, v in enumerate(pm):
        ax.text(i, v + 300, f"{v:,}", ha="center", va="bottom", fontsize=9)
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    savefig("14_payment_method.png")


def chart_inventory_stock(products):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(products["stock_quantity"], bins=40, color=BRAND_COLORS[2],
            edgecolor="white", linewidth=0.5)
    ax.axvline(products["reorder_level"].mean(), color="red", linestyle="--",
               label=f"Avg Reorder Level: {products['reorder_level'].mean():.0f}")
    ax.set_xlabel("Stock Quantity")
    ax.set_ylabel("Number of Products")
    ax.set_title("Product Stock Quantity Distribution")
    ax.legend()
    plt.tight_layout()
    savefig("15_inventory_stock_dist.png")


def chart_revenue_heatmap(sales):
    pivot = (sales.groupby(["year", "month"])["revenue"]
             .sum().unstack(level="month").fillna(0))
    pivot = pivot / 1e6

    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    pivot.columns = [month_names[m - 1] for m in pivot.columns]

    fig, ax = plt.subplots(figsize=(13, 4))
    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="YlOrRd", ax=ax,
                linewidths=0.5, cbar_kws={"label": "Revenue (â‚¹ Million)"})
    ax.set_title("Revenue Heatmap by Month Ã— Year (â‚¹ Million)")
    ax.set_ylabel("Year")
    ax.set_xlabel("Month")
    plt.tight_layout()
    savefig("16_revenue_heatmap.png")


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# MAIN
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def main():
    print("=" * 60)
    print("RetailPulse -- EDA")
    print("=" * 60)

    customers, products, stores, orders, order_det, inventory = load_data()
    sales = build_sales(orders, order_det, products, stores)

    print(f"\nMaster sales table: {len(sales):,} delivered line items")
    print(f"Total Revenue: Rs.{sales['revenue'].sum() / 1e7:.2f} Cr")
    print(f"Total Profit:  Rs.{sales['profit'].sum() / 1e7:.2f} Cr")
    print(f"Avg Margin:    {sales['margin_pct'].mean():.1f}%")
    print(f"\nGenerating charts -> {FIG_DIR}\n")

    chart_monthly_revenue(sales)
    chart_revenue_by_category(sales)
    chart_margin_by_category(sales)
    chart_top10_products(sales)
    chart_bottom10_products(sales)
    chart_orders_by_channel(orders)
    chart_orders_by_status(orders)
    chart_revenue_by_region(sales)
    chart_top10_stores(sales)
    chart_discount_vs_margin(sales)
    chart_customer_age(customers)
    chart_customer_gender(customers)
    chart_new_customers_monthly(customers)
    chart_payment_method(orders)
    chart_inventory_stock(products)
    chart_revenue_heatmap(sales)

    print("\n[OK]  All 16 charts saved to reports/figures/")
    print("Next step: python python/rfm_analysis.py")


if __name__ == "__main__":
    main()
