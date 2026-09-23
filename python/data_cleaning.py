"""
RetailPulse â€” Data Cleaning Pipeline
======================================
Reads all 6 raw CSVs from data/raw/, applies a full cleaning pipeline,
and writes cleaned CSVs to data/processed/.

Cleaning steps applied per dataset:
  - Strip whitespace from string columns
  - Standardise casing (title/upper as appropriate)
  - Drop exact duplicate rows
  - Parse and validate dates; drop rows with unparseable dates
  - Fill or drop missing values with documented strategy
  - Fix invalid numeric values (negative prices, zero quantities, etc.)
  - Cap statistical outliers using IQR method where appropriate

Run:
    python python/data_cleaning.py

Output:
    data/processed/customers_clean.csv
    data/processed/products_clean.csv
    data/processed/stores_clean.csv
    data/processed/orders_clean.csv
    data/processed/order_details_clean.csv
    data/processed/inventory_transactions_clean.csv
    data/processed/cleaning_report.txt
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime

# â”€â”€ Directories â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
RAW_DIR     = os.path.join(BASE_DIR, "..", "data", "raw")
PROC_DIR    = os.path.join(BASE_DIR, "..", "data", "processed")
os.makedirs(PROC_DIR, exist_ok=True)

report_lines = []

def log(msg: str):
    print(msg)
    report_lines.append(msg)

def section(title: str):
    log("\n" + "=" * 60)
    log(f"  {title}")
    log("=" * 60)

def strip_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Strip leading/trailing whitespace from all string columns."""
    for col in df.select_dtypes(include=["object", "str"]).columns:
        df[col] = df[col].str.strip()
    return df

def iqr_cap(series: pd.Series, lower_q=0.01, upper_q=0.99) -> pd.Series:
    """Cap values outside [lower_q, upper_q] quantiles."""
    lo = series.quantile(lower_q)
    hi = series.quantile(upper_q)
    return series.clip(lower=lo, upper=hi)

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 1. CLEAN CUSTOMERS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def clean_customers(path: str) -> pd.DataFrame:
    section("1. Customers")
    df = pd.read_csv(path)
    log(f"  Raw rows: {len(df):,}")

    # Strip whitespace
    df = strip_strings(df)

    # Standardise city casing â†’ Title Case
    df["city"] = df["city"].str.title()
    df["state"] = df["state"].str.title()
    df["region"] = df["region"].str.title()

    # Standardise gender â†’ Title Case
    df["gender"] = df["gender"].str.title()
    valid_genders = {"Male", "Female", "Other"}
    invalid_mask = ~df["gender"].isin(valid_genders) & df["gender"].notna()
    df.loc[invalid_mask, "gender"] = np.nan

    # Fill missing gender with mode
    mode_gender = df["gender"].mode()[0]
    n_fill = df["gender"].isna().sum()
    df["gender"] = df["gender"].fillna(mode_gender)
    log(f"  gender: filled {n_fill} missing with '{mode_gender}'")

    # Fill missing age with median (cast to int)
    median_age = df["age"].median()
    n_fill = df["age"].isna().sum()
    df["age"] = df["age"].fillna(median_age).astype(int)
    log(f"  age: filled {n_fill} missing with median ({median_age:.0f})")

    # Validate registration_date
    df["registration_date"] = pd.to_datetime(df["registration_date"], errors="coerce")
    n_bad = df["registration_date"].isna().sum()
    df = df.dropna(subset=["registration_date"])
    log(f"  registration_date: dropped {n_bad} unparseable rows")

    # Drop exact duplicates
    before = len(df)
    df = df.drop_duplicates()
    log(f"  Duplicates dropped: {before - len(df):,}")

    log(f"  Clean rows: {len(df):,}")
    return df

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 2. CLEAN PRODUCTS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def clean_products(path: str) -> pd.DataFrame:
    section("2. Products")
    df = pd.read_csv(path)
    log(f"  Raw rows: {len(df):,}")

    df = strip_strings(df)

    # Standardise category names
    category_map = {
        "electronics": "Electronics",
        "ELECTRONICS": "Electronics",
        "clothing": "Clothing",
        "CLOTHING": "Clothing",
        "grocery ": "Grocery",
        "GROCERY": "Grocery",
    }
    df["category"] = df["category"].replace(category_map)
    # Any remaining all-caps/lower â†’ title-case
    df["category"] = df["category"].str.strip().str.title()
    # Restore known multi-word categories
    df["category"] = df["category"].replace({
        "Computers & Accessories": "Computers & Accessories",
        "Mobile Accessories": "Mobile Accessories",
        "Home Appliances": "Home Appliances",
        "Beauty & Personal Care": "Beauty & Personal Care",
        "Sports & Fitness": "Sports & Fitness",
    })

    # Fill missing brand with 'Unknown'
    n_fill = df["brand"].isna().sum()
    df["brand"] = df["brand"].fillna("Unknown")
    log(f"  brand: filled {n_fill} missing with 'Unknown'")

    # Fill missing supplier with 'Unknown Supplier'
    n_fill = df["supplier"].isna().sum()
    df["supplier"] = df["supplier"].fillna("Unknown Supplier")
    log(f"  supplier: filled {n_fill} missing with 'Unknown Supplier'")

    # Fix invalid selling prices (â‰¤ 0) â†’ replace with median of valid prices
    invalid_price_mask = df["selling_price"] <= 0
    n_invalid = invalid_price_mask.sum()
    median_price = df.loc[~invalid_price_mask, "selling_price"].median()
    df.loc[invalid_price_mask, "selling_price"] = median_price
    log(f"  selling_price: fixed {n_invalid} invalid values with median ({median_price:.2f})")

    # Recalculate cost_price for fixed rows (use category avg margin)
    # (cost_price for newly fixed rows may also be wrong; cap outliers)
    df["cost_price"] = df["cost_price"].clip(lower=0)
    # Ensure cost_price < selling_price
    bad_cost = df["cost_price"] >= df["selling_price"]
    if bad_cost.any():
        df.loc[bad_cost, "cost_price"] = df.loc[bad_cost, "selling_price"] * 0.75
        log(f"  cost_price: fixed {bad_cost.sum()} rows where cost >= selling price")

    # Cap unit price outliers (IQR)
    df["selling_price"] = iqr_cap(df["selling_price"])

    # Drop exact duplicates
    before = len(df)
    df = df.drop_duplicates()
    log(f"  Duplicates dropped: {before - len(df):,}")

    log(f"  Clean rows: {len(df):,}")
    return df

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 3. CLEAN STORES
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def clean_stores(path: str) -> pd.DataFrame:
    section("3. Stores")
    df = pd.read_csv(path)
    log(f"  Raw rows: {len(df):,}")

    df = strip_strings(df)

    # Parse opening_date; fill missing with median date
    df["opening_date"] = pd.to_datetime(df["opening_date"], errors="coerce")
    n_missing = df["opening_date"].isna().sum()
    if n_missing > 0:
        median_date = df["opening_date"].dropna().median()
        df["opening_date"] = df["opening_date"].fillna(median_date)
        log(f"  opening_date: filled {n_missing} missing with median date")

    df = df.drop_duplicates()
    log(f"  Clean rows: {len(df):,}")
    return df

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 4. CLEAN ORDERS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def clean_orders(path: str) -> pd.DataFrame:
    section("4. Orders")
    df = pd.read_csv(path)
    log(f"  Raw rows: {len(df):,}")

    df = strip_strings(df)

    # Standardise order_status â†’ Title Case
    df["order_status"] = df["order_status"].str.title()

    # Fill missing payment_method with mode
    mode_pm = df["payment_method"].mode()[0]
    n_fill = df["payment_method"].isna().sum()
    df["payment_method"] = df["payment_method"].fillna(mode_pm)
    log(f"  payment_method: filled {n_fill} missing with '{mode_pm}'")

    # Parse order_date
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    n_bad = df["order_date"].isna().sum()
    df = df.dropna(subset=["order_date"])
    log(f"  order_date: dropped {n_bad} unparseable rows")

    # Drop exact duplicates
    before = len(df)
    df = df.drop_duplicates()
    log(f"  Duplicates dropped: {before - len(df):,}")

    log(f"  Clean rows: {len(df):,}")
    return df

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 5. CLEAN ORDER DETAILS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def clean_order_details(path: str) -> pd.DataFrame:
    section("5. Order Details")
    df = pd.read_csv(path)
    log(f"  Raw rows: {len(df):,}")

    # Fill missing discount with 0
    n_fill = df["discount"].isna().sum()
    df["discount"] = df["discount"].fillna(0.0)
    log(f"  discount: filled {n_fill} missing with 0")

    # Drop rows with zero or negative quantity
    n_invalid = (df["quantity"] <= 0).sum()
    df = df[df["quantity"] > 0]
    log(f"  quantity: dropped {n_invalid} rows with quantity â‰¤ 0")

    # Cap extreme unit_price outliers (IQR 1%-99%)
    before_max = df["unit_price"].max()
    df["unit_price"] = iqr_cap(df["unit_price"])
    after_max = df["unit_price"].max()
    log(f"  unit_price: capped outliers ({before_max:,.2f} â†’ {after_max:,.2f})")

    # Ensure discount is in [0, 1]
    df["discount"] = df["discount"].clip(0, 1)

    # Add line_total for convenience
    df["line_total"] = (df["unit_price"] * df["quantity"]).round(2)

    # Drop exact duplicates
    before = len(df)
    df = df.drop_duplicates()
    log(f"  Duplicates dropped: {before - len(df):,}")

    log(f"  Clean rows: {len(df):,}")
    return df

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 6. CLEAN INVENTORY TRANSACTIONS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def clean_inventory(path: str) -> pd.DataFrame:
    section("6. Inventory Transactions")
    df = pd.read_csv(path)
    log(f"  Raw rows: {len(df):,}")

    df = strip_strings(df)

    # Standardise transaction_type â†’ Upper Case
    df["transaction_type"] = df["transaction_type"].str.upper()
    valid_types = {"IN", "OUT", "ADJUSTMENT"}
    invalid_mask = ~df["transaction_type"].isin(valid_types) & df["transaction_type"].notna()
    n_invalid = invalid_mask.sum()
    if n_invalid:
        df = df[~invalid_mask]
        log(f"  transaction_type: dropped {n_invalid} invalid type rows")

    # Drop rows with missing quantity
    n_missing = df["quantity"].isna().sum()
    df = df.dropna(subset=["quantity"])
    log(f"  quantity: dropped {n_missing} rows with missing quantity")

    # Parse transaction_date
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    n_bad = df["transaction_date"].isna().sum()
    df = df.dropna(subset=["transaction_date"])
    log(f"  transaction_date: dropped {n_bad} unparseable rows")

    # Drop exact duplicates
    before = len(df)
    df = df.drop_duplicates()
    log(f"  Duplicates dropped: {before - len(df):,}")

    log(f"  Clean rows: {len(df):,}")
    return df

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# MAIN
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def main():
    log("=" * 60)
    log("RetailPulse â€” Data Cleaning Pipeline")
    log(f"Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 60)

    customers   = clean_customers(os.path.join(RAW_DIR, "customers_raw.csv"))
    products    = clean_products(os.path.join(RAW_DIR, "products_raw.csv"))
    stores      = clean_stores(os.path.join(RAW_DIR, "stores_raw.csv"))
    orders      = clean_orders(os.path.join(RAW_DIR, "orders_raw.csv"))
    order_det   = clean_order_details(os.path.join(RAW_DIR, "order_details_raw.csv"))
    inventory   = clean_inventory(os.path.join(RAW_DIR, "inventory_transactions_raw.csv"))

    # Save cleaned files
    section("Saving cleaned files")
    datasets = {
        "customers_clean.csv":              customers,
        "products_clean.csv":               products,
        "stores_clean.csv":                 stores,
        "orders_clean.csv":                 orders,
        "order_details_clean.csv":          order_det,
        "inventory_transactions_clean.csv": inventory,
    }
    for fname, df in datasets.items():
        out_path = os.path.join(PROC_DIR, fname)
        df.to_csv(out_path, index=False)
        log(f"  Saved: {fname}  ({len(df):,} rows)")

    section("Summary")
    log(f"  Customers:               {len(customers):>10,}")
    log(f"  Products:                {len(products):>10,}")
    log(f"  Stores:                  {len(stores):>10,}")
    log(f"  Orders:                  {len(orders):>10,}")
    log(f"  Order Details:           {len(order_det):>10,}")
    log(f"  Inventory Transactions:  {len(inventory):>10,}")
    log("\nNext step: python python/eda.py")

    # Save report
    report_path = os.path.join(PROC_DIR, "cleaning_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"\nCleaning report saved to: {report_path}")


if __name__ == "__main__":
    main()
