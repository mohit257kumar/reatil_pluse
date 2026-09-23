"""
RetailPulse â€” RFM Customer Segmentation
=========================================
Performs Recency-Frequency-Monetary (RFM) analysis on delivered orders
to segment customers into actionable business segments.

RFM Scoring:
  - Recency  (R): Days since last order (lower = better â†’ higher score)
  - Frequency (F): Number of distinct orders (higher = better â†’ higher score)
  - Monetary  (M): Total revenue from customer (higher = better â†’ higher score)
  - Scores:  Each dimension scored 1â€“5 using quintile binning
  - RFM Score: Concatenated string e.g. "555" (Champion)

Customer Segments (11 segments):
  Champions          â€” Best customers; bought recently, frequently, high spend
  Loyal Customers    â€” Regular buyers with solid monetary value
  Potential Loyalist â€” Recent customers with decent frequency
  New Customers      â€” Bought very recently but only once/twice
  Promising          â€” Recent low-frequency shoppers
  Need Attention     â€” Above-average R/F/M but haven't bought recently
  About to Sleep     â€” Below-average recency, frequency, and monetary
  At Risk            â€” Bought often and spent well but haven't returned
  Can't Lose Them    â€” Made big purchases but haven't returned
  Hibernating        â€” Last purchase was long ago, low frequency
  Lost               â€” Lowest recency, frequency, and monetary scores

Run:
    python python/rfm_analysis.py

Output:
    data/processed/customer_rfm.csv
    reports/figures/rfm_segment_distribution.png
    reports/figures/rfm_revenue_by_segment.png
    reports/figures/rfm_scatter.png
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

warnings.filterwarnings("ignore")

# â”€â”€ Paths â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
PROC_DIR  = os.path.join(BASE_DIR, "..", "data", "processed")
FIG_DIR   = os.path.join(BASE_DIR, "..", "reports", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

sns.set_theme(style="whitegrid")
plt.rcParams.update({"figure.dpi": 150, "savefig.bbox": "tight"})

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# RFM SEGMENT MAPPING
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def assign_segment(r: int, f: int, m: int) -> str:
    """Map RFM score integers to business segment name."""
    rfm = f"{r}{f}{m}"
    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    elif r >= 3 and f >= 3 and m >= 3:
        return "Loyal Customers"
    elif r >= 4 and f <= 2:
        return "New Customers"
    elif r >= 3 and f >= 1 and m <= 2:
        return "Promising"
    elif r >= 4 and f >= 2 and m <= 3:
        return "Potential Loyalist"
    elif r == 3 and f >= 3:
        return "Need Attention"
    elif r <= 2 and f >= 3 and m >= 3:
        return "At Risk"
    elif r <= 2 and f >= 4 and m >= 4:
        return "Can't Lose Them"
    elif r <= 2 and f <= 2 and m <= 2:
        return "Lost"
    elif r == 2 and f <= 2:
        return "About to Sleep"
    else:
        return "Hibernating"

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# COMPUTE RFM
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def compute_rfm(orders: pd.DataFrame, order_det: pd.DataFrame) -> pd.DataFrame:
    """
    Compute RFM metrics for each customer.

    Analysis reference date = 1 day after the last order in dataset.
    """
    # Use only delivered orders
    delivered_orders = orders[orders["order_status"] == "Delivered"].copy()

    # Merge with order_details to get revenue
    merged = delivered_orders.merge(
        order_det[["order_id", "line_total"]], on="order_id", how="left"
    )

    reference_date = delivered_orders["order_date"].max() + pd.Timedelta(days=1)
    print(f"  RFM reference date: {reference_date.date()}")

    # Aggregate per customer
    rfm = merged.groupby("customer_id").agg(
        last_order_date=("order_date", "max"),
        frequency=("order_id", "nunique"),
        monetary=("line_total", "sum"),
    ).reset_index()

    rfm["recency"] = (reference_date - rfm["last_order_date"]).dt.days

    # â”€â”€ Score each dimension 1â€“5 using quintile binning â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Recency: LOWER is better â†’ invert scoring
    rfm["r_score"] = pd.qcut(rfm["recency"], q=5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), q=5,
                              labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["m_score"] = pd.qcut(rfm["monetary"].rank(method="first"), q=5,
                              labels=[1, 2, 3, 4, 5]).astype(int)

    rfm["rfm_score"] = rfm["r_score"].astype(str) + rfm["f_score"].astype(str) + rfm["m_score"].astype(str)
    rfm["rfm_total"] = rfm["r_score"] + rfm["f_score"] + rfm["m_score"]

    # Assign business segment
    rfm["segment"] = rfm.apply(
        lambda row: assign_segment(row["r_score"], row["f_score"], row["m_score"]), axis=1
    )

    return rfm, reference_date

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# CHARTS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

SEGMENT_COLORS = {
    "Champions":          "#1a9641",
    "Loyal Customers":    "#52b788",
    "Potential Loyalist": "#74c476",
    "New Customers":      "#abd9e9",
    "Promising":          "#a6d96a",
    "Need Attention":     "#fdae61",
    "About to Sleep":     "#f46d43",
    "At Risk":            "#d7191c",
    "Can't Lose Them":    "#762a83",
    "Hibernating":        "#c0c0c0",
    "Lost":               "#4d4d4d",
}

def chart_segment_distribution(rfm):
    seg_counts = rfm["segment"].value_counts().sort_values(ascending=True)
    colors = [SEGMENT_COLORS.get(s, "#aaaaaa") for s in seg_counts.index]

    fig, ax = plt.subplots(figsize=(10, 7))
    bars = ax.barh(seg_counts.index, seg_counts.values, color=colors)
    for bar, v in zip(bars, seg_counts.values):
        pct = v / len(rfm) * 100
        ax.text(bar.get_width() + 50, bar.get_y() + bar.get_height() / 2,
                f"{v:,} ({pct:.1f}%)", va="center", fontsize=9)
    ax.set_xlabel("Number of Customers")
    ax.set_title("RFM Customer Segment Distribution")
    ax.set_xlim(0, seg_counts.max() * 1.2)
    plt.tight_layout()
    path = os.path.join(FIG_DIR, "rfm_segment_distribution.png")
    plt.savefig(path)
    plt.close()
    print(f"  Saved: rfm_segment_distribution.png")


def chart_revenue_by_segment(rfm):
    seg_rev = (rfm.groupby("segment")["monetary"]
               .agg(["sum", "mean", "count"])
               .sort_values("sum", ascending=True))
    seg_rev.columns = ["total_revenue", "avg_revenue", "customer_count"]
    colors = [SEGMENT_COLORS.get(s, "#aaaaaa") for s in seg_rev.index]

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(seg_rev.index, seg_rev["total_revenue"] / 1e6, color=colors)
    ax.set_xlabel("Total Revenue (â‚¹ Million)")
    ax.set_title("Total Revenue by Customer Segment")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"â‚¹{x:.0f}M"))
    plt.tight_layout()
    path = os.path.join(FIG_DIR, "rfm_revenue_by_segment.png")
    plt.savefig(path)
    plt.close()
    print(f"  Saved: rfm_revenue_by_segment.png")


def chart_rfm_scatter(rfm):
    """Recency vs Frequency scatter, sized by Monetary."""
    sample = rfm.sample(min(3000, len(rfm)), random_state=42)
    colors = [SEGMENT_COLORS.get(s, "#aaaaaa") for s in sample["segment"]]
    sizes  = (sample["monetary"] / sample["monetary"].max() * 200).clip(5)

    fig, ax = plt.subplots(figsize=(11, 7))
    sc = ax.scatter(sample["recency"], sample["frequency"],
                    c=sample["rfm_total"], cmap="RdYlGn",
                    s=sizes, alpha=0.6, edgecolors="none")
    plt.colorbar(sc, ax=ax, label="RFM Total Score")
    ax.set_xlabel("Recency (days since last order)")
    ax.set_ylabel("Frequency (number of orders)")
    ax.set_title("RFM Scatter â€” Recency vs Frequency\n(bubble size = Monetary value)")
    plt.tight_layout()
    path = os.path.join(FIG_DIR, "rfm_scatter.png")
    plt.savefig(path)
    plt.close()
    print(f"  Saved: rfm_scatter.png")

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# MAIN
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def main():
    print("=" * 60)
    print("RetailPulse â€” RFM Customer Segmentation")
    print("=" * 60)

    orders    = pd.read_csv(os.path.join(PROC_DIR, "orders_clean.csv"), parse_dates=["order_date"])
    order_det = pd.read_csv(os.path.join(PROC_DIR, "order_details_clean.csv"))
    customers = pd.read_csv(os.path.join(PROC_DIR, "customers_clean.csv"))

    print(f"\nDelivered orders: {(orders['order_status'] == 'Delivered').sum():,}")

    rfm, ref_date = compute_rfm(orders, order_det)

    # Merge customer details
    rfm = rfm.merge(customers[["customer_id", "customer_name", "gender",
                                "age", "city", "region"]], on="customer_id", how="left")

    # Reorder columns
    rfm = rfm[["customer_id", "customer_name", "gender", "age", "city", "region",
               "recency", "frequency", "monetary",
               "r_score", "f_score", "m_score", "rfm_score", "rfm_total",
               "segment", "last_order_date"]]

    # Save
    out_path = os.path.join(PROC_DIR, "customer_rfm.csv")
    rfm.to_csv(out_path, index=False)
    print(f"\nâœ…  RFM data saved to: {out_path}")
    print(f"   Total customers analysed: {len(rfm):,}")

    # Segment summary
    print("\nSegment Summary:")
    print("-" * 60)
    seg_summary = (rfm.groupby("segment")
                   .agg(customers=("customer_id", "count"),
                        avg_recency=("recency", "mean"),
                        avg_frequency=("frequency", "mean"),
                        avg_monetary=("monetary", "mean"),
                        total_revenue=("monetary", "sum"))
                   .sort_values("total_revenue", ascending=False))
    seg_summary["pct_customers"] = (seg_summary["customers"] / len(rfm) * 100).round(1)
    seg_summary["pct_revenue"]   = (seg_summary["total_revenue"] / rfm["monetary"].sum() * 100).round(1)
    with pd.option_context("display.float_format", "{:,.0f}".format,
                           "display.max_columns", 10, "display.width", 120):
        print(seg_summary.to_string())

    # Charts
    print("\nGenerating RFM charts...")
    chart_segment_distribution(rfm)
    chart_revenue_by_segment(rfm)
    chart_rfm_scatter(rfm)

    print("\nNext step: python python/forecasting.py")


if __name__ == "__main__":
    main()
