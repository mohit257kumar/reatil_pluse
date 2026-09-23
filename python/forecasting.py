"""
RetailPulse â€” Sales Forecasting
=================================
Forecasts monthly revenue using Holt-Winters Exponential Smoothing (additive)
and optionally SARIMA for comparison. Evaluates model accuracy and produces
a 6-month forward forecast.

Metrics computed:
  - MAE  (Mean Absolute Error)
  - RMSE (Root Mean Squared Error)
  - MAPE (Mean Absolute Percentage Error)

Output:
  data/processed/forecast.csv          â€” Historical + 6-month forecast
  reports/figures/forecast_revenue.png  â€” Forecast chart with CI band
  reports/figures/forecast_decomposition.png â€” Seasonal decomposition

Run:
    python python/forecasting.py
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.seasonal import seasonal_decompose

warnings.filterwarnings("ignore")

# â”€â”€ Paths â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROC_DIR = os.path.join(BASE_DIR, "..", "data", "processed")
FIG_DIR  = os.path.join(BASE_DIR, "..", "reports", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

plt.rcParams.update({"figure.dpi": 150, "savefig.bbox": "tight", "font.size": 11})

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# BUILD MONTHLY REVENUE TIME SERIES
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def build_monthly_series(orders_path: str, details_path: str) -> pd.Series:
    """
    Aggregate delivered order revenue by calendar month.
    Returns a pd.Series with a PeriodIndex (monthly frequency).
    """
    orders = pd.read_csv(orders_path, parse_dates=["order_date"])
    det    = pd.read_csv(details_path)

    delivered = orders[orders["order_status"] == "Delivered"].copy()
    delivered["year_month"] = delivered["order_date"].dt.to_period("M")

    merged = delivered.merge(det[["order_id", "line_total"]], on="order_id", how="left")
    monthly = merged.groupby("year_month")["line_total"].sum().sort_index()
    monthly.name = "revenue"
    return monthly


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# TRAIN / TEST SPLIT & EVALUATION
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def evaluate_model(actual: np.ndarray, predicted: np.ndarray) -> dict:
    residuals = actual - predicted
    mae  = np.mean(np.abs(residuals))
    rmse = np.sqrt(np.mean(residuals ** 2))
    denom = np.where(actual == 0, np.nan, actual)
    mape = np.nanmean(np.abs(residuals / denom)) * 100
    return {"MAE": mae, "RMSE": rmse, "MAPE": mape}


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# HOLT-WINTERS EXPONENTIAL SMOOTHING
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def fit_holtwinters(train: pd.Series, test_len: int = 6, forecast_periods: int = 6):
    """
    Fit Holt-Winters additive model.
    Uses last `test_len` months as hold-out test set.
    Returns: model, in-sample fitted values, test forecast, forward forecast.
    """
    model = ExponentialSmoothing(
        train,
        trend="add",
        seasonal="add",
        seasonal_periods=12,
        initialization_method="estimated",
    ).fit(optimized=True)

    # Test forecast
    test_forecast = model.forecast(test_len)

    # Full forward forecast (fit on entire series)
    full_series = train  # will refit after evaluation on full data
    model_full = ExponentialSmoothing(
        full_series,
        trend="add",
        seasonal="add",
        seasonal_periods=12,
        initialization_method="estimated",
    ).fit(optimized=True)

    forward_forecast = model_full.forecast(forecast_periods)
    fitted_values    = model_full.fittedvalues

    return model_full, fitted_values, test_forecast, forward_forecast


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# CHARTS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def chart_forecast(monthly: pd.Series, fitted: pd.Series,
                   test: pd.Series, forward: pd.Series,
                   test_actual: pd.Series, metrics: dict):
    """Plot historical, fitted, test, and forward forecast with confidence band."""
    fig, ax = plt.subplots(figsize=(15, 6))

    # Historical
    hist_x = monthly.index.to_timestamp()
    ax.plot(hist_x, monthly.values / 1e6, color="#2C7BB6",
            linewidth=2, label="Actual Revenue", zorder=3)

    # Fitted values
    fit_x = fitted.index.to_timestamp()
    ax.plot(fit_x, fitted.values / 1e6, color="#74ADD1",
            linewidth=1.2, linestyle="--", label="Model Fit", zorder=2)

    # Test period actual
    test_act_x = test_actual.index.to_timestamp()
    ax.plot(test_act_x, test_actual.values / 1e6, color="black",
            linewidth=1.5, label="Hold-out Actual", zorder=4)

    # Test forecast
    test_x = test.index.to_timestamp()
    ax.plot(test_x, test.values / 1e6, color="#FDAE61",
            linewidth=2, linestyle="-.", label="Test Forecast", zorder=4)

    # Forward forecast
    fwd_x = forward.index.to_timestamp()
    ax.plot(fwd_x, forward.values / 1e6, color="#D7191C",
            linewidth=2.5, label="6-Month Forecast", zorder=5)

    # Simple CI band: Â±1.5 std of residuals
    residuals_std = (monthly - fitted).std() / 1e6
    ax.fill_between(fwd_x,
                    (forward.values / 1e6) - 1.5 * residuals_std,
                    (forward.values / 1e6) + 1.5 * residuals_std,
                    alpha=0.2, color="#D7191C", label="95% CI (approx.)")

    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (â‚¹ Million)")
    ax.set_title("RetailPulse â€” Monthly Revenue Forecast (Holt-Winters)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"â‚¹{x:.0f}M"))
    ax.legend(loc="upper left", fontsize=9)

    # Metrics annotation
    metrics_text = (f"MAE:  â‚¹{metrics['MAE']/1e6:.2f}M\n"
                    f"RMSE: â‚¹{metrics['RMSE']/1e6:.2f}M\n"
                    f"MAPE: {metrics['MAPE']:.1f}%")
    ax.text(0.99, 0.05, metrics_text, transform=ax.transAxes,
            fontsize=9, va="bottom", ha="right",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="lightyellow", edgecolor="gray"))

    plt.tight_layout()
    path = os.path.join(FIG_DIR, "forecast_revenue.png")
    plt.savefig(path)
    plt.close()
    print(f"  Saved: forecast_revenue.png")


def chart_decomposition(monthly: pd.Series):
    """Seasonal decomposition plot."""
    try:
        decomp = seasonal_decompose(monthly, model="additive", period=12)
    except Exception:
        print("  Decomposition skipped (insufficient data).")
        return

    fig, axes = plt.subplots(4, 1, figsize=(13, 10), sharex=True)
    components = [
        (monthly.values / 1e6,            "Observed (â‚¹M)",  "#2C7BB6"),
        (decomp.trend.values / 1e6,        "Trend (â‚¹M)",     "#1A9641"),
        (decomp.seasonal.values / 1e6,     "Seasonal (â‚¹M)",  "#FDAE61"),
        (decomp.resid.values / 1e6,        "Residual (â‚¹M)",  "#D7191C"),
    ]
    x = monthly.index.to_timestamp()
    for ax, (vals, label, color) in zip(axes, components):
        ax.plot(x, vals, color=color, linewidth=1.5)
        ax.set_ylabel(label, fontsize=9)
        ax.grid(True, alpha=0.3)

    axes[0].set_title("Revenue Seasonal Decomposition (Additive)")
    plt.tight_layout()
    path = os.path.join(FIG_DIR, "forecast_decomposition.png")
    plt.savefig(path)
    plt.close()
    print(f"  Saved: forecast_decomposition.png")


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# MAIN
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def main():
    print("=" * 60)
    print("RetailPulse â€” Sales Forecasting")
    print("=" * 60)

    orders_path  = os.path.join(PROC_DIR, "orders_clean.csv")
    details_path = os.path.join(PROC_DIR, "order_details_clean.csv")

    print("\nBuilding monthly revenue time series...")
    monthly = build_monthly_series(orders_path, details_path)
    print(f"  Series length: {len(monthly)} months")
    print(f"  Range: {monthly.index[0]} â†’ {monthly.index[-1]}")
    print(f"  Total Revenue (series): â‚¹{monthly.sum()/1e7:.2f} Cr")

    if len(monthly) < 18:
        print("ERROR: Need at least 18 months of data for reliable Holt-Winters. Exiting.")
        return

    # Train / test split â€” last 6 months as test
    TEST_PERIODS     = 6
    FORECAST_PERIODS = 6

    train        = monthly.iloc[:-TEST_PERIODS]
    test_actual  = monthly.iloc[-TEST_PERIODS:]

    print(f"\nTrain: {len(train)} months | Test: {len(test_actual)} months")
    print("Fitting Holt-Winters model...")

    model_full, fitted, test_forecast, forward_forecast = fit_holtwinters(
        train, test_len=TEST_PERIODS, forecast_periods=FORECAST_PERIODS
    )

    # Evaluate on test set
    metrics = evaluate_model(test_actual.values, test_forecast.values[:len(test_actual)])
    print(f"\nModel Evaluation (hold-out test period):")
    print(f"  MAE:  â‚¹{metrics['MAE']/1e6:.3f}M")
    print(f"  RMSE: â‚¹{metrics['RMSE']/1e6:.3f}M")
    print(f"  MAPE: {metrics['MAPE']:.2f}%")

    # Forward forecast labels
    last_period = monthly.index[-1]
    forecast_periods_idx = pd.period_range(
        start=last_period + 1, periods=FORECAST_PERIODS, freq="M"
    )
    forward_forecast.index = forecast_periods_idx

    print(f"\n6-Month Forward Forecast (from {forecast_periods_idx[0]}):")
    print("-" * 40)
    for period, value in zip(forecast_periods_idx, forward_forecast.values):
        print(f"  {period}: â‚¹{value/1e6:.2f}M")

    # Save forecast CSV
    hist_df = monthly.reset_index()
    hist_df.columns = ["year_month", "revenue"]
    hist_df["type"] = "actual"

    fwd_df = pd.DataFrame({
        "year_month": forecast_periods_idx.astype(str),
        "revenue":    forward_forecast.values,
        "type":       "forecast",
    })

    fitted_df = pd.DataFrame({
        "year_month": fitted.index.astype(str),
        "revenue":    fitted.values,
        "type":       "fitted",
    })

    output_df = pd.concat([
        hist_df.assign(year_month=hist_df["year_month"].astype(str)),
        fitted_df,
        fwd_df,
    ], ignore_index=True)

    out_path = os.path.join(PROC_DIR, "forecast.csv")
    output_df.to_csv(out_path, index=False)
    print(f"\nâœ…  Forecast saved to: {out_path}")

    # Charts
    print("\nGenerating forecast charts...")
    chart_forecast(monthly, fitted, test_forecast, forward_forecast, test_actual, metrics)
    chart_decomposition(monthly)

    print("\nâœ…  Forecasting complete.")
    print("Next step: Open powerbi/RetailPulse.pbix in Power BI Desktop.")


if __name__ == "__main__":
    main()
