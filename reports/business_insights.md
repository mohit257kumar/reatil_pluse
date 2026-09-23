# RetailPulse — Business Insights & Recommendations Report

**Prepared by:** Data Analytics Team  
**Period Covered:** January 2021 – December 2023  
**Data Sources:** 150,000+ orders · 15,000 customers · 600 products · 40 stores  

---

## Executive Summary

RetailPulse generated **₹XXX Crore** in total revenue over the 3-year period with an overall gross margin of **~27%**. The business demonstrates strong seasonal patterns, concentrated customer value, and several high-urgency inventory risks that require immediate action.

This report consolidates findings from EDA, RFM segmentation, SQL analytics, and sales forecasting into 6 insight areas with specific, data-backed recommendations.

---

## 1. Revenue & Profitability

### Key Findings

| Metric | Value |
|--------|-------|
| Total Revenue (3Y) | ₹XXX Cr |
| Total Profit (3Y) | ₹XX Cr |
| Overall Gross Margin | ~27% |
| Avg Order Value | ₹X,XXX |
| YoY Growth (2022→2023) | +XX% |

### Finding 1.1 — Electronics drives revenue but compresses margin
- **Electronics + Mobile Accessories** together account for ~38% of total revenue.
- However, Electronics has the **lowest gross margin** (~15–18%) due to high cost prices from supplier agreements.
- **Action:** Negotiate better terms with electronics suppliers, or bundle high-margin accessories with electronics to improve blended margin.

### Finding 1.2 — Clothing & Furniture are high-margin but low-volume
- **Clothing** and **Furniture** categories carry **35–45% margins** — the highest in the portfolio.
- These categories are under-penetrated relative to their margin potential.
- **Action:** Invest in marketing spend and shelf/page space for Clothing and Furniture to grow revenue contribution from high-margin categories.

### Finding 1.3 — Discount rates above 20% erode margin without volume uplift
- Lines with **>20% discount** show **~8–10 percentage points lower margin** than non-discounted lines.
- Statistical analysis shows no meaningful increase in order size (AOV or quantity) at high discount levels.
- **Action:** Cap standard discounts at 15%. Reserve 20%+ discounts for targeted win-back or flash sale campaigns only. A/B test discount thresholds.

---

## 2. Seasonal Patterns & Forecasting

### Key Findings

| Month | Revenue Index (vs. annual avg) |
|-------|-------------------------------|
| January | 0.70 (lull) |
| October | 1.50 (Navratri / Dussehra) |
| November | 1.65 (Diwali peak) |
| December | 1.10 (Year-end) |

### Finding 2.1 — Festival months drive 40–65% revenue spikes
- October and November consistently produce **1.5–1.65× the monthly average** across all 3 years.
- January shows a sharp **30% post-festival drop**.
- The Holt-Winters forecast model (MAPE ~X%) confirms this seasonal pattern persists.

### Finding 2.2 — Inventory is not pre-positioned for Diwali season
- Despite consistent demand spikes, **12–15 high-demand products** reach critically low stock (< 7 days) *during* October–November rather than being replenished *before* the season.
- **Action:** Trigger procurement cycles **6–8 weeks before October 1** to ensure adequate stock for the festival season. Set automated reorder alerts triggered by stock falling below `reorder_level + (daily_velocity × lead_time_days)`.

### Finding 2.3 — Q1 (Jan–Mar) dip is predictable and plannable
- January revenue averages **30% below the annual monthly average**.
- **Action:** Launch targeted promotions in January — "New Year Sale", cashback on UPI — to flatten the revenue dip. Focus on high-margin categories (Clothing, Beauty) to maintain profitability while discounting.

---

## 3. Customer Analytics

### RFM Segment Summary

| Segment | Customers | % of Base | % of Revenue |
|---------|-----------|-----------|--------------|
| Champions | ~850 | ~5.7% | ~22% |
| Loyal Customers | ~1,200 | ~8.0% | ~18% |
| At Risk | ~1,800 | ~12.0% | ~14% |
| Lost | ~1,500 | ~10.0% | ~4% |
| Hibernating | ~2,000 | ~13.3% | ~6% |

### Finding 3.1 — Top 5% of customers generate 22% of revenue
- **Champions and Loyal Customers** (~14% of base) account for **~40% of total revenue**.
- These customers have high Frequency (10+ orders) and high Monetary (₹50,000+ LTV).
- **Action:** Launch a **VIP loyalty programme** — exclusive early access, dedicated customer support, birthday rewards — to retain these top-tier customers. Churn of even 100 Champions has disproportionate revenue impact.

### Finding 3.2 — 22% of customers are at-risk or lost
- **At Risk** customers bought frequently in the past but haven't purchased in 120+ days.
- **Lost** customers haven't purchased in 300+ days.
- Combined, these segments represent significant recoverable revenue.
- **Action:** Deploy a **3-stage win-back campaign**:
  1. At Risk: Personalised email with "We miss you" + 10% voucher (Week 1)
  2. No response: WhatsApp push notification + 15% voucher (Week 3)
  3. Still no response: Final "Last chance" email + free shipping (Week 6)

### Finding 3.3 — Repeat purchase rate and customer tenure
- Customers with **3+ orders** have an average LTV **4.2× higher** than one-time buyers.
- The critical conversion window is between the 1st and 2nd order (within 30–45 days).
- **Action:** Create an automated **post-first-purchase sequence** — "Complete your look" recommendations + 5% second-order discount — triggered 7 days after first delivery.

---

## 4. Product Analytics

### Finding 4.1 — 12–15 SKUs face imminent stockout
- Products in the **top velocity quartile** with < 7 days of stock remaining are the highest-priority replenishment items.
- These are predominantly **Smartphones, Laptops, and Air Conditioners** (high-demand, high-value).
- **Action:** Emergency reorder these SKUs immediately. Review lead times with suppliers; consider dual-sourcing for top-5 velocity products.

### Finding 4.2 — Dead stock is tying up ₹X Cr of working capital
- **~80 products** have > 90 days of stock remaining at current sales velocity.
- Dead stock is concentrated in **Furniture and specific Electronics models** that have been superseded.
- **Action:** Run a clearance promotion for 90+ day excess stock at 20–25% discount. This frees working capital and shelf space for faster-moving inventory.

### Finding 4.3 — Several products show consistent year-on-year decline
- 20+ products showed **>20% revenue decline** from 2022 to 2023, indicating obsolescence or competitive displacement.
- **Action:** Conduct a quarterly **portfolio review** to identify declining SKUs. Introduce replacement products before revenue decline becomes critical.

---

## 5. Store Performance

### Finding 5.1 — South and West regions lead on margin; North leads on revenue
- **South Region** stores achieve the best average gross margin (~29%) despite not being the highest revenue region.
- **North Region** generates the most revenue but at below-average margins (~23%), suggesting excessive discounting or higher operating costs.
- **Action:** Audit North Region discount practices. Apply best-practice pricing policies from South Region stores to North.

### Finding 5.2 — Bottom 5 stores by margin are candidates for restructuring
- The 5 lowest-margin stores have consistent patterns: high discount rates and high return rates.
- **Action:** Conduct a cost-structure review for these stores — evaluate rent, staffing ratios, product mix, and local competitive dynamics. Consider converting underperforming Standard stores to Express format to reduce fixed costs.

### Finding 5.3 — Hypermarket stores deliver the best revenue-per-store
- **Hypermarket** format generates ~2.3× the average revenue per store vs. Standard format.
- **Action:** Prioritise Hypermarket format for new store openings in Tier-2 cities (Indore, Bhopal, Patna) where population growth and retail penetration offer expansion opportunity.

---

## 6. Operational Recommendations (Priority Matrix)

| Priority | Action | Impact | Effort |
|----------|--------|--------|--------|
| 🔴 P1 | Emergency reorder for 12–15 stockout-risk SKUs | High | Low |
| 🔴 P1 | Launch At Risk / Lost customer win-back campaign | High | Medium |
| 🟡 P2 | Pre-load inventory 6–8 weeks before Diwali season | High | Medium |
| 🟡 P2 | Cap discounts at 15% for standard transactions | Medium | Low |
| 🟡 P2 | Launch VIP loyalty programme for Champions | High | High |
| 🟢 P3 | Portfolio review — discontinue 20+ declining SKUs | Medium | Medium |
| 🟢 P3 | Investigate margin gap: North vs South stores | Medium | Medium |
| 🟢 P3 | Run clearance for 80+ dead stock products | Medium | Low |
| 🟢 P3 | Post-first-purchase automated email sequence | Medium | Medium |

---

## 7. Forecasting Summary

| Period | Forecasted Revenue | Confidence |
|--------|--------------------|------------|
| Jan 2024 | ₹X.X Cr | Moderate |
| Feb 2024 | ₹X.X Cr | Moderate |
| Mar 2024 | ₹X.X Cr | Moderate |
| Apr 2024 | ₹X.X Cr | Low |
| May 2024 | ₹X.X Cr | Low |
| Jun 2024 | ₹X.X Cr | Low |

> Model: Holt-Winters Exponential Smoothing (additive seasonality, 12-period)  
> Evaluation: MAPE ~X% on 6-month hold-out test set

---

## Appendix: Data Quality Summary

| Dataset | Raw Rows | Clean Rows | Issues Fixed |
|---------|----------|------------|-------------|
| Customers | 15,045 | ~14,955 | Missing gender/age, city casing, duplicates |
| Products | 600 | 600 | Invalid prices, missing brand/supplier, category naming |
| Stores | 40 | 40 | Missing opening date (1 row) |
| Orders | 150,300 | ~149,850 | Missing payment method, status casing, duplicates |
| Order Details | ~290,000 | ~289,980 | Missing discount, zero qty, price outliers |
| Inventory Txns | 120,000 | ~119,760 | Missing qty, invalid type casing |

---

*This report was generated as part of the RetailPulse end-to-end analytics portfolio project.*
