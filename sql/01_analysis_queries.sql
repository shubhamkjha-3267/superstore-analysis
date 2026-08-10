-- ============================================================================
-- 01_analysis_queries.sql
-- Business questions run against the star schema (fact_sales + dims), loaded
-- into SQLite by scripts/run_sql_analysis.py.
-- Concepts: multi-table JOINs, GROUP BY/HAVING, CTEs, window functions
-- (RANK, NTILE, LAG, running SUM), subqueries, CASE.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Q1. Profitability by product category and sub-category
-- (Sales != revenue-is-good: a category can have high sales and negative profit)
-- ----------------------------------------------------------------------------
SELECT
    p.product_category,
    p.product_sub_category,
    ROUND(SUM(f.sales), 2)              AS total_sales,
    ROUND(SUM(f.profit), 2)             AS total_profit,
    ROUND(100.0 * SUM(f.profit) / NULLIF(SUM(f.sales), 0), 1) AS profit_margin_pct,
    COUNT(*)                            AS num_line_items
FROM fact_sales f
JOIN dim_product p ON p.product_id = f.product_id
GROUP BY p.product_category, p.product_sub_category
ORDER BY total_profit ASC;

-- ----------------------------------------------------------------------------
-- Q2. Discount impact on profit (does discounting kill margin?)
-- CASE statement to bucket discount levels
-- ----------------------------------------------------------------------------
-- NOTE: we deliberately use SUM(profit)/SUM(sales) here (a dollar-weighted
-- margin), not AVG(row-level profit_margin_pct). Averaging row-level
-- percentages is misleading in this dataset: a $1 sale with -$10 profit is a
-- -1000% row, and a handful of tiny-value orders like that will drag a naive
-- average massively negative even though the business is profitable overall.
SELECT
    CASE
        WHEN discount = 0 THEN '0% (no discount)'
        WHEN discount <= 0.1 THEN '1-10%'
        WHEN discount <= 0.3 THEN '11-30%'
        ELSE '30%+'
    END AS discount_bucket,
    COUNT(*)                                                    AS num_orders,
    ROUND(AVG(profit), 2)                                       AS avg_profit,
    ROUND(SUM(profit), 2)                                       AS total_profit,
    ROUND(100.0 * SUM(profit) / NULLIF(SUM(sales), 0), 1)       AS weighted_profit_margin_pct
FROM fact_sales
GROUP BY discount_bucket
ORDER BY MIN(discount);

-- ----------------------------------------------------------------------------
-- Q3. Top 10 customers by profit, with their rank and profit share
-- (window functions: RANK, running-percentage via SUM OVER)
-- ----------------------------------------------------------------------------
WITH customer_profit AS (
    SELECT
        c.customer_id,
        c.customer_name,
        c.customer_segment,
        SUM(f.sales)  AS total_sales,
        SUM(f.profit) AS total_profit
    FROM fact_sales f
    JOIN dim_customer c ON c.customer_id = f.customer_id
    GROUP BY c.customer_id, c.customer_name, c.customer_segment
)
SELECT
    customer_name,
    customer_segment,
    ROUND(total_sales, 2)  AS total_sales,
    ROUND(total_profit, 2) AS total_profit,
    RANK() OVER (ORDER BY total_profit DESC) AS profit_rank
FROM customer_profit
ORDER BY total_profit DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- Q4. Regional performance vs. company average (subquery in HAVING)
-- ----------------------------------------------------------------------------
SELECT
    r.region,
    r.province,
    ROUND(SUM(f.sales), 2)  AS region_sales,
    ROUND(SUM(f.profit), 2) AS region_profit
FROM fact_sales f
JOIN dim_region r ON r.region_id = f.region_id
GROUP BY r.region, r.province
HAVING SUM(f.profit) < (
    SELECT AVG(prov_profit) FROM (
        SELECT SUM(f2.profit) AS prov_profit
        FROM fact_sales f2
        JOIN dim_region r2 ON r2.region_id = f2.region_id
        GROUP BY r2.province
    )
)
ORDER BY region_profit ASC;

-- ----------------------------------------------------------------------------
-- Q5. Monthly sales & profit trend with month-over-month change
-- (CTE + window function LAG)
-- ----------------------------------------------------------------------------
WITH monthly AS (
    SELECT
        d.year,
        d.month,
        d.month_name,
        SUM(f.sales)  AS sales,
        SUM(f.profit) AS profit
    FROM fact_sales f
    JOIN dim_date d ON d.date_id = f.order_date_id
    GROUP BY d.year, d.month, d.month_name
)
SELECT
    year,
    month_name,
    ROUND(sales, 2)  AS sales,
    ROUND(profit, 2) AS profit,
    ROUND(profit - LAG(profit) OVER (ORDER BY year, month), 2) AS profit_mom_change
FROM monthly
ORDER BY year, month;

-- ----------------------------------------------------------------------------
-- Q6. Shipping performance by ship mode & order priority
-- (does "High" priority actually ship faster?)
-- ----------------------------------------------------------------------------
SELECT
    ship_mode,
    order_priority,
    COUNT(*)                        AS num_orders,
    ROUND(AVG(shipping_days), 1)    AS avg_shipping_days,
    ROUND(AVG(shipping_cost), 2)    AS avg_shipping_cost
FROM fact_sales
GROUP BY ship_mode, order_priority
ORDER BY ship_mode, avg_shipping_days;

-- ----------------------------------------------------------------------------
-- Q7. Customer value tiers using NTILE (quartile segmentation -- a lightweight
-- RFM-style approach used constantly in real analyst work)
-- ----------------------------------------------------------------------------
WITH customer_sales AS (
    SELECT
        c.customer_id,
        c.customer_name,
        SUM(f.sales) AS total_sales
    FROM fact_sales f
    JOIN dim_customer c ON c.customer_id = f.customer_id
    GROUP BY c.customer_id, c.customer_name
)
SELECT
    customer_name,
    ROUND(total_sales, 2) AS total_sales,
    NTILE(4) OVER (ORDER BY total_sales DESC) AS value_quartile
FROM customer_sales
ORDER BY total_sales DESC;

-- ----------------------------------------------------------------------------
-- Q8. Loss-making orders: how much profit is being lost, and where
-- ----------------------------------------------------------------------------
SELECT
    p.product_category,
    COUNT(*)                     AS loss_making_orders,
    ROUND(SUM(f.profit), 2)      AS total_loss,
    ROUND(AVG(f.discount), 2)    AS avg_discount_on_losses
FROM fact_sales f
JOIN dim_product p ON p.product_id = f.product_id
WHERE f.is_loss_making = 1
GROUP BY p.product_category
ORDER BY total_loss ASC;
