# Power BI Dashboard — Build Guide

The data model is fully prepped as a star schema in `data/powerbi/` — import it
directly into Power BI Desktop and follow the steps below. Total build time is
roughly 20–30 minutes since the modeling and cleaning work is already done.

## 1. Import the data

In Power BI Desktop: **Get Data → Text/CSV**, import all five files from
`data/powerbi/`:

- `fact_sales.csv`
- `dim_customer.csv`
- `dim_product.csv`
- `dim_region.csv`
- `dim_date.csv`

## 2. Build the relationships (star schema)

Go to **Model view** and create these relationships (all single-direction,
one-to-many from dim → fact):

| From | To | Cardinality |
|---|---|---|
| `dim_customer[customer_id]` | `fact_sales[customer_id]` | 1 → * |
| `dim_product[product_id]` | `fact_sales[product_id]` | 1 → * |
| `dim_region[region_id]` | `fact_sales[region_id]` | 1 → * |
| `dim_date[date_id]` | `fact_sales[order_date_id]` | 1 → * |

Mark `dim_date` as a **Date Table** (Table tools → Mark as date table →
select the `date` column) so time intelligence functions work correctly.

## 3. DAX measures

Create a new measure table (Model view → New Table, name it `_Measures`) and
add these:

```dax
Total Sales = SUM(fact_sales[sales])

Total Profit = SUM(fact_sales[profit])

Profit Margin % =
DIVIDE([Total Profit], [Total Sales], 0)

Total Orders = DISTINCTCOUNT(fact_sales[order_id])

Avg Order Value = DIVIDE([Total Sales], [Total Orders], 0)

Avg Discount = AVERAGE(fact_sales[discount])

Loss-Making Orders = CALCULATE(COUNTROWS(fact_sales), fact_sales[is_loss_making] = TRUE)

Avg Shipping Days = AVERAGE(fact_sales[shipping_days])

Sales LY = CALCULATE([Total Sales], SAMEPERIODLASTYEAR(dim_date[date]))

Sales YoY % =
DIVIDE([Total Sales] - [Sales LY], [Sales LY], 0)

Profit Margin Color =
IF([Profit Margin %] < 0, "#ef4444", "#059669")
```

## 4. Suggested dashboard layout (one page)

**Top row — KPI cards:**
`Total Sales` | `Total Profit` | `Profit Margin %` | `Loss-Making Orders`

**Row 2 — left: line chart**
X-axis: `dim_date[month]` / Y-axis: `Total Sales` and `Total Profit` (dual line)
→ mirrors `visuals/monthly_sales_profit_trend.png`, but interactive

**Row 2 — right: bar chart**
`dim_product[product_sub_category]` (Y-axis) vs `Total Profit` (X-axis),
sorted ascending, conditionally colored red/green using `Profit Margin Color`
→ mirrors `visuals/profit_by_subcategory.png`

**Row 3 — left: map**
Filled map of Canada using `dim_region[province]`, bubble/color = `Total Sales`

**Row 3 — right: matrix table**
Rows: `dim_customer[customer_name]`, Values: `Total Sales`, `Total Profit` —
sorted by Total Profit descending, top 10 filter → mirrors Q3 SQL result

**Slicers (top of page):** `dim_date[year]`, `dim_product[product_category]`,
`dim_region[region]`, `fact_sales[order_priority]`

## 5. Save & publish

Save as `superstore_dashboard.pbix`. If you have a Power BI Service license,
publish and generate a shareable link; otherwise export a PDF/screenshot of
the finished dashboard and add it to `visuals/` as `powerbi_dashboard.png` —
link it from the main README so the portfolio shows the finished result even
for people who don't open the `.pbix` file.

## Why a star schema instead of one flat table?

A flat table works but a star schema is what Power BI (and real BI teams)
expect: it keeps the fact table narrow, lets filters propagate correctly
through relationships, and is the standard your interviewer will look for if
they open the model view. It also makes the DAX above simpler and faster to
compute than doing the same joins/aggregations inside a single wide table.
