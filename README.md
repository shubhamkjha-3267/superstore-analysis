# Superstore Sales & Profitability Analysis (SQL + Python + Power BI)

An end-to-end analyst project on a **real** retail dataset: data cleaning and
star-schema modeling, SQL for every business question, Python for the
pipeline and charts, and a Power BI-ready data model with DAX measures and a
dashboard build guide.

> Live preview of the dashboard concept: open [`dashboard/index.html`](dashboard/index.html)
> in a browser, or see `visuals/powerbi_dashboard.png` once you've built the
> `.pbix` (see [Power BI section](#power-bi-dashboard) below).

## Problem Statement

A Canadian office-supplies retailer wants to know: **where is the company
actually making money, and where is it quietly losing it?** Sales volume
alone is a misleading KPI — this project digs into profit, discounting
behavior, shipping performance, and customer value to find the answers.

## Dataset

Real historical order data (not synthetic) — 8,399 order line items across
5,496 orders, 2009–2012, sourced from the widely-used Superstore Sales
dataset ([source](https://raw.githubusercontent.com/curran/data/gh-pages/superstoreSales/superstoreSales.csv)).
21 original columns including Sales, Profit, Discount, Shipping Cost, Order
Priority, and Product Base Margin — real enough to have actual data quality
issues (63 missing margin values, encoding issues in the raw file) rather
than a pre-cleaned teaching dataset.

## Tools & Why

| Tool | Role |
|---|---|
| **Python (pandas)** | Cleaning, star-schema modeling |
| **SQL (SQLite)** | All 8 business-question queries — joins, CTEs, window functions |
| **Python (matplotlib)** | Static chart exports for the README/portfolio |
| **Power BI** | Interactive dashboard on the same star schema (DAX measures included) |

## Approach

1. **Clean & model** (`scripts/clean_and_model.py`) — parsed dates, validated
   ship dates never precede order dates, imputed 63 missing
   `product_base_margin` values with the category median (documented, not
   silently dropped), and built a proper **star schema**:
   `fact_sales` + `dim_customer` + `dim_product` + `dim_region` + `dim_date`.
2. **Analyze in SQL** (`sql/01_analysis_queries.sql`) — 8 business questions
   run against the star schema in SQLite (`scripts/run_sql_analysis.py`).
3. **Visualize in Python** — 5 charts in `visuals/`.
4. **Model in Power BI** — the same star schema imports directly into Power
   BI; see [`powerbi_guide/POWERBI_GUIDE.md`](powerbi_guide/POWERBI_GUIDE.md)
   for relationships, DAX measures, and dashboard layout.
5. **Bonus interactive dashboard** (`dashboard/index.html`) — a
   dependency-free HTML/JS dashboard covering the same KPIs, so the project
   has a working, clickable dashboard even before you open Power BI Desktop.

## Key Findings

- **Half of all order lines lose money.** 4,264 of 8,399 line items (50.8%)
  have negative profit, even though the company is profitable overall
  (10.2% margin) — losses are concentrated, not distributed evenly.
- **Furniture is the profit problem.** `Tables` alone lose **-₹99K** and
  `Bookcases` lose **-₹34K** — the two clearest candidates for a pricing or
  sourcing review. Meanwhile `Telephones`, `Office Machines`, and `Binders`
  each generate **₹300K+** in profit.
- **Deep discounts don't pay for themselves.** Orders discounted 0–10% keep
  a healthy 10–13% margin, but the (small) group of orders discounted
  11–30% flips to a **-21.3% margin** — this is a dollar-weighted figure, not
  a naive average, since row-level percentages are heavily skewed by tiny
  low-value orders (see the note in `sql/01_analysis_queries.sql` Q2 for why
  that distinction matters).
- **"Low" priority orders ship ~3x slower** than every other priority tier
  (4.24 days vs. ~1.5 days) — consistent across all three shipping modes, so
  it's a process/queuing effect, not a carrier issue.
- **Geographic concentration**: Nunavut and Newfoundland trail every other
  province in profit — plausible logistics-cost story worth a follow-up.

## Charts

| | |
|---|---|
| ![Profit by Sub-Category](visuals/profit_by_subcategory.png) | ![Discount vs Margin](visuals/discount_vs_margin.png) |
| ![Monthly Trend](visuals/monthly_sales_profit_trend.png) | ![Shipping by Mode](visuals/shipping_days_by_mode.png) |
| ![Losses by Category](visuals/losses_by_category.png) | |

## Power BI Dashboard

The star schema in `data/powerbi/` imports directly into Power BI Desktop.
Full build guide with DAX measures, relationship diagram, and layout
recommendations: **[`powerbi_guide/POWERBI_GUIDE.md`](powerbi_guide/POWERBI_GUIDE.md)**.

> Power BI Desktop is Windows-only and can't run in this project's build
> environment, so the `.pbix` itself isn't included — but the data model,
> every DAX measure, and the exact layout are ready to drop in, roughly a
> 20-minute build. Once built, export a screenshot to
> `visuals/powerbi_dashboard.png` and it'll show up here.

## Repo Structure

```
superstore-analysis/
├── data/
│   ├── raw/               # original CSV, as downloaded
│   ├── clean/              # cleaned flat table
│   ├── powerbi/            # star schema: fact_sales + 4 dim tables
│   └── results/            # one CSV per SQL business question
├── sql/
│   └── 01_analysis_queries.sql
├── scripts/
│   ├── clean_and_model.py  # raw -> clean -> star schema
│   └── run_sql_analysis.py # star schema -> SQLite -> queries -> charts
├── powerbi_guide/
│   └── POWERBI_GUIDE.md    # relationships, DAX, dashboard layout
├── dashboard/
│   └── index.html          # bonus interactive HTML dashboard
├── visuals/                 # PNG chart exports
└── README.md
```

## How to Run

```bash
pip install pandas numpy matplotlib
python3 scripts/clean_and_model.py     # clean raw data, build star schema
python3 scripts/run_sql_analysis.py    # load to SQLite, run SQL, build charts
```

Then open `dashboard/index.html` directly in a browser for the interactive
view, or follow `powerbi_guide/POWERBI_GUIDE.md` to build the Power BI
version.

## SQL Concepts Demonstrated

Everything from the previous project, plus:
- Star-schema joins (fact ↔ 4 dimension tables)
- `NTILE()` for customer value quartiles (lightweight RFM-style segmentation)
- `RANK()` for customer profit leaderboard
- Nested subqueries in `HAVING` for above/below-average filtering
- Dollar-weighted vs. naive-average aggregation — and why the difference
  changes the conclusion (see Q2)

## Possible Next Steps

- Rebuild the pipeline against PostgreSQL instead of SQLite (`psycopg2`)
- Add a `Sales YoY %` time-intelligence page in Power BI using the DAX
  measures already defined
- Investigate the Furniture loss with a cost/margin breakdown by supplier
  (not present in this dataset, but a natural next data pull)
