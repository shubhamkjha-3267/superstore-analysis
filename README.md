# Superstore Sales & Profitability Analysis

> **End-to-end retail analytics project using SQL, Python, and Power BI to uncover the drivers of sales, profitability, discounting, shipping performance, and customer value.**

**Raw Data → Data Cleaning → Star Schema → SQL Analysis → Python Visualization → Interactive Dashboard → Power BI**

This project uses a real historical Superstore retail dataset and demonstrates a complete data analytics workflow, from raw transactional data through data cleaning, dimensional modeling, business analysis, visualization, and dashboard development.

---

## 🔗 Project Links

- 🌐 **[Live Interactive Dashboard](https://shubhamkjha-3267.github.io/superstore-analysis/)**
- 📁 **[GitHub Repository](https://github.com/shubhamkjha-3267/superstore-analysis)**
- 🧮 **SQL Analysis:** `sql/01_analysis_queries.sql`
- 📖 **Power BI Build Guide:** `powerbi_guide/POWERBI_GUIDE.md`
- 📊 **Power BI Data Model:** `data/powerbi/`

---

# 🎯 Business Problem

A Canadian office-supplies retailer wants to understand:

> **Where is the company actually making money, and where is it quietly losing it?**

Looking only at sales can hide important problems. A product can generate high revenue while producing very little profit—or even losing money.

This project therefore focuses on:

- Sales performance
- Profitability
- Discounting
- Shipping performance
- Customer value
- Regional performance
- Product and category performance

The goal is to turn transactional data into **actionable business insights**, rather than simply reporting sales totals.

---

# 📊 Dataset

The project uses a **real historical retail dataset**, rather than synthetic data.

| Metric | Value |
|---|---:|
| Order line items | 8,399 |
| Orders | 5,496 |
| Time period | 2009–2012 |
| Original columns | 21 |
| Data type | Retail transactions |

The dataset contains fields including:

- Sales
- Profit
- Discount
- Shipping Cost
- Order Priority
- Product Base Margin
- Customer
- Product
- Region
- Order Date
- Ship Date

### Data Quality Issues

The raw dataset contains real-world data quality challenges, including:

- 63 missing `Product Base Margin` values
- Encoding issues in the original CSV
- Date validation requirements
- Dimensional values requiring normalization

### Dataset Source

[Superstore Sales Dataset](https://raw.githubusercontent.com/curran/data/gh-pages/superstoreSales/superstoreSales.csv)

---

# 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| **Python** | Data cleaning, transformation and pipeline automation |
| **Pandas** | Data manipulation and preprocessing |
| **NumPy** | Numerical operations |
| **Matplotlib** | Static data visualization |
| **SQL / SQLite** | Business analysis and querying |
| **Power BI** | Interactive dashboard and business reporting |
| **DAX** | Power BI measures and calculations |
| **Git/GitHub** | Version control and project documentation |

---

# 🔄 End-to-End Workflow

```text
                         RAW DATA
                            │
                            ▼
                     Data Cleaning
                            │
                            ▼
                  Cleaned Flat Table
                            │
                            ▼
                     Star Schema
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
           SQL            Python        Power BI
         Analysis       Analysis       Dashboard
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                   Business Insights🧹 Data Cleaning & Data Modeling

The cleaning and modeling pipeline is implemented in:

scripts/clean_and_model.py

The pipeline performs the following steps:

1. Date validation

Order and shipping dates are parsed and validated to ensure:

Ship Date ≥ Order Date

2. Missing-value handling

63 missing Product Base Margin values are imputed using the category median.

This decision is documented rather than silently dropping affected records.

3. Star-schema modeling

The cleaned data is transformed into:

fact_sales
    │
    ├── dim_customer
    ├── dim_product
    ├── dim_region
    └── dim_date

This structure is used consistently across the SQL analysis and Power BI model.

🧮 SQL Analysis

The SQL analysis is implemented in:

sql/01_analysis_queries.sql

Eight business questions are answered using SQLite.

SQL techniques demonstrated
Multi-table JOINs
GROUP BY
HAVING
CTEs
Nested subqueries
Window functions
RANK()
NTILE()
Conditional aggregation
Date-based analysis
Customer segmentation
Profitability analysis

The analysis also demonstrates an important analytical principle:

Dollar-weighted metrics can tell a very different story from simple row-level averages.

For example, the discount analysis uses revenue/profit-weighted calculations rather than simply averaging row-level margins.

💡 Key Business Findings
1. Half of Order Lines Lose Money

4,264 of 8,399 order lines — 50.8% — have negative profit.

Despite this, the company remains profitable overall with approximately a 10.2% profit margin.

This indicates that losses are concentrated rather than evenly distributed.

Business implication

Instead of treating profitability as a company-wide problem, management should identify the specific products, categories, customers, and regions responsible for the losses.

2. Furniture Is the Biggest Profitability Problem

Two products stand out:

Product	Profit
Tables	-₹99K
Bookcases	-₹34K

Together, these categories represent significant sources of negative profit.

Meanwhile:

Telephones
Office Machines
Binders

each generate ₹300K+ in profit.

Business implication

Furniture should be investigated further for:

Pricing strategy
Discounting
Product costs
Shipping costs
Supplier economics
Product-level margins
3. Deep Discounts Can Destroy Margin

Orders discounted between 0–10% maintain approximately 10–13% margins.

However, the group receiving 11–30% discounts falls to approximately:

-21.3% margin

This is a dollar-weighted metric, rather than a simple average of row-level percentages.

Business implication

Discounting may be driving sales volume without creating proportional profit.

A deeper pricing analysis should therefore examine:

Discount → Sales → Profit → Margin

rather than looking at revenue alone.

4. Low-Priority Orders Take Much Longer to Ship

Low-priority orders average approximately:

4.24 days

compared with approximately:

1.5 days

for the other priority levels.

The difference remains consistent across the three shipping modes.

Business implication

This suggests the delay may be related to internal prioritization or queue management, rather than being purely a carrier/shipping-mode issue.

5. Regional Profitability Is Uneven

Nunavut and Newfoundland have the weakest profitability among the provinces.

This could indicate potential relationships between:

Shipping costs
Order volume
Product mix
Regional demand
Pricing
Logistics

This should be treated as a follow-up hypothesis, rather than assuming geography itself is the cause.

📈 Visualizations

The Python pipeline generates five static charts.

Monthly Revenue Trend

Cumulative Revenue

Revenue by Region

Top Products by Profit

Order / Profitability Analysis

Note: Update the image filenames above if your current visuals/ directory uses different names.

📊 Power BI Dashboard

The project is designed to be directly compatible with Power BI.

The Power BI-ready star schema is located in:

data/powerbi/

It contains:

fact_sales
dim_customer
dim_product
dim_region
dim_date

The Power BI build guide contains:

Data import instructions
Table relationships
DAX measures
KPI recommendations
Dashboard layout
Visualization recommendations

See:

powerbi_guide/POWERBI_GUIDE.md
Recommended Dashboard Pages
Executive Overview
Total Sales
Total Profit
Profit Margin
Total Orders
Average Order Value
Sales Trend
Profit Trend
Product & Category Analysis
Sales by Category
Profit by Category
Top/Bottom Products
Discount vs Profit
Regional Analysis
Sales by Province
Profit by Province
Regional margin
Geographic performance
Customer Analysis
Customer Sales
Customer Profit
Customer value quartiles
Top customers
🌐 Interactive HTML Dashboard

The project also includes a lightweight interactive dashboard:

dashboard/index.html

It provides a browser-based view of the key KPIs and analysis without requiring Power BI Desktop.

Run locally

Simply open:

dashboard/index.html

in a browser.

If hosted through GitHub Pages, the dashboard can also be accessed directly from the repository's Pages URL.

📁 Project Structure
superstore-analysis/
│
├── data/
│   ├── raw/
│   │   └── superstore_sales.csv
│   │
│   ├── clean/
│   │   └── superstore_clean.csv
│   │
│   ├── powerbi/
│   │   ├── fact_sales.csv
│   │   ├── dim_customer.csv
│   │   ├── dim_product.csv
│   │   ├── dim_region.csv
│   │   └── dim_date.csv
│   │
│   └── results/
│       ├── Q1_result.csv
│       ├── Q2_result.csv
│       ├── ...
│       └── Q8_result.csv
│
├── sql/
│   └── 01_analysis_queries.sql
│
├── scripts/
│   ├── clean_and_model.py
│   └── run_sql_analysis.py
│
├── powerbi_guide/
│   └── POWERBI_GUIDE.md
│
├── dashboard/
│   └── index.html
│
├── visuals/
│   └── *.png
│
└── README.md
▶️ How to Run
1. Clone the repository
git clone https://github.com/shubhamkjha-3267/superstore-analysis.git
cd superstore-analysis
2. Install dependencies
pip install pandas numpy matplotlib
3. Clean and model the data
python3 scripts/clean_and_model.py

This creates the cleaned dataset and star-schema tables.

4. Run the SQL analysis
python3 scripts/run_sql_analysis.py

This:

Loads the star schema into SQLite
Executes all eight SQL business questions
Saves query results
Generates the visualization outputs
5. View the dashboard

Open:

dashboard/index.html

in your browser.

🧠 SQL Concepts Demonstrated
Relational Analysis
Fact-to-dimension joins
Multi-table joins
Star-schema querying
Aggregation
SUM()
COUNT()
AVG()
GROUP BY
HAVING
Advanced SQL
CTEs
Nested subqueries
Window functions
RANK()
NTILE()
Conditional logic
Analytical Techniques
Customer value quartiles
Profitability analysis
Discount analysis
Regional comparison
Time-based analysis
Dollar-weighted metrics
🎯 Skills Demonstrated
Data Analytics
Business problem solving
KPI analysis
Profitability analysis
Customer analysis
Product analysis
Regional analysis
Data-driven recommendations
SQL
Complex joins
CTEs
Subqueries
Aggregations
Window functions
SQLite
Python
Pandas
NumPy
Matplotlib
Data cleaning
Data transformation
Analytical pipelines
Power BI
Star-schema modeling
DAX
KPI design
Interactive dashboards
Business reporting
Data Modeling
Fact tables
Dimension tables
Date dimensions
Star-schema architecture
🚀 Future Improvements
 Rebuild the pipeline using PostgreSQL
 Add year-over-year sales and profit analysis
 Add customer cohort analysis
 Build RFM customer segmentation
 Add product-level margin analysis
 Investigate furniture profitability in greater depth
 Add shipping-cost optimization analysis
 Expand Power BI dashboard with time-intelligence measures
 Add automated dashboard data refresh
 Deploy the interactive dashboard using GitHub Pages
👤 Author

Shubham Jha

Data Analyst | Aspiring Data Scientist

Interested in Data Analytics, Business Intelligence, Data Science, and Python-based analytical roles.

⭐ If you found this project useful, feel free to explore the SQL analysis, Python pipeline, Power BI model, and interactive dashboard.

