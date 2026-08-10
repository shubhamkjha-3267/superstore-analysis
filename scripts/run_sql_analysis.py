"""
Loads the star schema (data/powerbi/*.csv) into SQLite, runs every business
question in sql/01_analysis_queries.sql, saves results to data/results/,
and produces charts in visuals/.

Run with: python3 scripts/run_sql_analysis.py
"""

import sqlite3
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "data", "superstore.db")
PBI_DIR = os.path.join(ROOT, "data", "powerbi")
RESULTS_DIR = os.path.join(ROOT, "data", "results")
VISUALS_DIR = os.path.join(ROOT, "visuals")

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(VISUALS_DIR, exist_ok=True)
plt.style.use("seaborn-v0_8-whitegrid")

# ---------------------------------------------------------------------------
# 1. Load star schema into SQLite
# ---------------------------------------------------------------------------
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
for name in ["fact_sales", "dim_customer", "dim_product", "dim_region", "dim_date"]:
    df = pd.read_csv(os.path.join(PBI_DIR, f"{name}.csv"))
    df.to_sql(name, conn, index=False, if_exists="replace")
print("Loaded star schema into SQLite ->", DB_PATH)

# ---------------------------------------------------------------------------
# 2. Parse and run each query
# ---------------------------------------------------------------------------
with open(os.path.join(ROOT, "sql", "01_analysis_queries.sql")) as f:
    sql_text = f.read()

blocks = re.split(r"-- Q(\d+)\.", sql_text)
queries = {}
for i in range(1, len(blocks), 2):
    qnum = blocks[i]
    qtext = blocks[i + 1]
    match = re.search(r"^\s*(SELECT|WITH)\b", qtext, re.IGNORECASE | re.MULTILINE)
    sql_stmt = qtext[match.start():].strip() if match else qtext.strip()
    queries[f"Q{qnum}"] = sql_stmt

results = {}
for qname, sql in queries.items():
    df = pd.read_sql(sql, conn)
    results[qname] = df
    df.to_csv(os.path.join(RESULTS_DIR, f"{qname}_result.csv"), index=False)
    print(f"{qname}: {len(df)} rows -> data/results/{qname}_result.csv")

# ---------------------------------------------------------------------------
# 3. Charts
# ---------------------------------------------------------------------------

# Chart 1: Profit by sub-category (highlights loss-making sub-categories)
df1 = results["Q1"].sort_values("total_profit")
colors = ["#ef4444" if v < 0 else "#059669" for v in df1["total_profit"]]
fig, ax = plt.subplots(figsize=(10, 8))
ax.barh(df1["product_sub_category"], df1["total_profit"], color=colors)
ax.axvline(0, color="black", linewidth=0.8)
ax.set_title("Profit by Product Sub-Category", fontsize=13, fontweight="bold")
ax.set_xlabel("Total Profit (Rs.)")
plt.tight_layout()
plt.savefig(os.path.join(VISUALS_DIR, "profit_by_subcategory.png"), dpi=150)
plt.close()

# Chart 2: Discount bucket vs avg profit margin
df2 = results["Q2"]
fig, ax = plt.subplots(figsize=(8, 5))
bar_colors = ["#059669" if v > 0 else "#ef4444" for v in df2["weighted_profit_margin_pct"]]
ax.bar(df2["discount_bucket"], df2["weighted_profit_margin_pct"], color=bar_colors)
ax.axhline(0, color="black", linewidth=0.8)
ax.set_title("Discount Level vs. Profit Margin (dollar-weighted)", fontsize=13, fontweight="bold")
ax.set_ylabel("Profit Margin (%)")
plt.tight_layout()
plt.savefig(os.path.join(VISUALS_DIR, "discount_vs_margin.png"), dpi=150)
plt.close()

# Chart 3: Monthly sales & profit trend
df5 = results["Q5"]
df5["period"] = df5["month_name"] + " " + df5["year"].astype(str)
fig, ax1 = plt.subplots(figsize=(12, 5))
ax1.plot(df5["period"], df5["sales"], color="#2563eb", label="Sales", linewidth=2)
ax1.set_ylabel("Sales (Rs.)", color="#2563eb")
ax2 = ax1.twinx()
ax2.plot(df5["period"], df5["profit"], color="#f59e0b", label="Profit", linewidth=2)
ax2.set_ylabel("Profit (Rs.)", color="#f59e0b")
ax1.set_title("Monthly Sales vs. Profit Trend", fontsize=13, fontweight="bold")
plt.xticks(rotation=90, fontsize=7)
plt.tight_layout()
plt.savefig(os.path.join(VISUALS_DIR, "monthly_sales_profit_trend.png"), dpi=150)
plt.close()

# Chart 4: Shipping days by ship mode
df6 = results["Q6"].groupby("ship_mode", as_index=False)["avg_shipping_days"].mean()
fig, ax = plt.subplots(figsize=(7, 5))
ax.bar(df6["ship_mode"], df6["avg_shipping_days"], color="#7c3aed")
ax.set_title("Avg Shipping Days by Ship Mode", fontsize=13, fontweight="bold")
ax.set_ylabel("Avg Days")
plt.tight_layout()
plt.savefig(os.path.join(VISUALS_DIR, "shipping_days_by_mode.png"), dpi=150)
plt.close()

# Chart 5: Loss-making orders by category
df8 = results["Q8"]
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(df8["product_category"], df8["total_loss"].abs(), color="#ef4444")
ax.set_title("Total Loss by Category (from loss-making orders)", fontsize=13, fontweight="bold")
ax.set_ylabel("Total Loss (Rs., absolute)")
plt.tight_layout()
plt.savefig(os.path.join(VISUALS_DIR, "losses_by_category.png"), dpi=150)
plt.close()

print("\nSaved 5 charts to visuals/")
conn.close()
print("Done. DB at data/superstore.db, results in data/results/, charts in visuals/")
