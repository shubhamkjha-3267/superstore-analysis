"""
Cleans the raw Superstore export and builds a star schema:
    fact_sales, dim_customer, dim_product, dim_region, dim_date

Output:
    data/clean/*.csv   -> cleaned flat table (for SQL loading)
    data/powerbi/*.csv -> star schema, ready to import into Power BI
"""

import pandas as pd
import numpy as np
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(ROOT, "data", "raw", "superstore_sales.csv")
CLEAN_DIR = os.path.join(ROOT, "data", "clean")
PBI_DIR = os.path.join(ROOT, "data", "powerbi")
os.makedirs(CLEAN_DIR, exist_ok=True)
os.makedirs(PBI_DIR, exist_ok=True)

df = pd.read_csv(RAW_PATH, encoding="latin1")

# ---------------------------------------------------------------------------
# Standardize column names
# ---------------------------------------------------------------------------
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

# ---------------------------------------------------------------------------
# Parse dates
# ---------------------------------------------------------------------------
df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
df["ship_date"] = pd.to_datetime(df["ship_date"], errors="coerce")

before = len(df)
df = df.dropna(subset=["order_date", "ship_date"])
print(f"Dropped {before - len(df)} rows with unparseable dates")

# sanity check: ship date should never precede order date
bad_ship = df[df["ship_date"] < df["order_date"]]
print(f"Rows where ship_date < order_date: {len(bad_ship)} (kept, flagged for review)")

df["shipping_days"] = (df["ship_date"] - df["order_date"]).dt.days

# ---------------------------------------------------------------------------
# Impute missing Product Base Margin with the category-level median
# (documented assumption: 63 of 8,399 rows, ~0.75% -- imputing avoids
# dropping otherwise-complete revenue/profit rows)
# ---------------------------------------------------------------------------
missing_margin = df["product_base_margin"].isna().sum()
df["product_base_margin"] = df.groupby("product_category")["product_base_margin"] \
    .transform(lambda x: x.fillna(x.median()))
print(f"Imputed {missing_margin} missing product_base_margin values with category median")

# ---------------------------------------------------------------------------
# Derived fields
# ---------------------------------------------------------------------------
df["profit_margin_pct"] = np.where(df["sales"] != 0, 100 * df["profit"] / df["sales"], np.nan)
df["is_loss_making"] = df["profit"] < 0

df.to_csv(os.path.join(CLEAN_DIR, "superstore_clean.csv"), index=False)
print(f"\nSaved cleaned flat table: {len(df)} rows -> data/clean/superstore_clean.csv")

# ---------------------------------------------------------------------------
# Build star schema for Power BI / SQL
# ---------------------------------------------------------------------------

# dim_customer
dim_customer = (
    df[["customer_name", "customer_segment"]]
    .drop_duplicates()
    .reset_index(drop=True)
)
dim_customer["customer_id"] = dim_customer.index + 1
dim_customer = dim_customer[["customer_id", "customer_name", "customer_segment"]]

# dim_product
dim_product = (
    df[["product_name", "product_category", "product_sub-category", "product_container"]]
    .drop_duplicates()
    .reset_index(drop=True)
)
dim_product["product_id"] = dim_product.index + 1
dim_product = dim_product.rename(columns={"product_sub-category": "product_sub_category"})
dim_product = dim_product[["product_id", "product_name", "product_category", "product_sub_category", "product_container"]]

# dim_region
dim_region = (
    df[["region", "province"]]
    .drop_duplicates()
    .reset_index(drop=True)
)
dim_region["region_id"] = dim_region.index + 1
dim_region = dim_region[["region_id", "region", "province"]]

# dim_date (calendar table spanning min-max order dates, standard Power BI pattern)
all_dates = pd.date_range(df["order_date"].min(), df["ship_date"].max(), freq="D")
dim_date = pd.DataFrame({"date": all_dates})
dim_date["date_id"] = dim_date["date"].dt.strftime("%Y%m%d").astype(int)
dim_date["year"] = dim_date["date"].dt.year
dim_date["month"] = dim_date["date"].dt.month
dim_date["month_name"] = dim_date["date"].dt.strftime("%b")
dim_date["quarter"] = dim_date["date"].dt.quarter
dim_date["weekday"] = dim_date["date"].dt.strftime("%A")
dim_date["is_weekend"] = dim_date["date"].dt.dayofweek >= 5
dim_date = dim_date[["date_id", "date", "year", "month", "month_name", "quarter", "weekday", "is_weekend"]]

# fact_sales -- join back to get surrogate keys
fact = df.merge(dim_customer, on=["customer_name", "customer_segment"], how="left")
fact = fact.merge(
    dim_product.rename(columns={"product_sub_category": "product_sub-category"}),
    on=["product_name", "product_category", "product_sub-category", "product_container"],
    how="left",
)
fact = fact.merge(dim_region, on=["region", "province"], how="left")

fact["order_date_id"] = fact["order_date"].dt.strftime("%Y%m%d").astype(int)
fact["ship_date_id"] = fact["ship_date"].dt.strftime("%Y%m%d").astype(int)

fact_sales = fact[[
    "row_id", "order_id", "customer_id", "product_id", "region_id",
    "order_date_id", "ship_date_id", "order_priority", "ship_mode",
    "order_quantity", "unit_price", "discount", "sales", "profit",
    "shipping_cost", "product_base_margin", "shipping_days",
    "profit_margin_pct", "is_loss_making",
]].rename(columns={"order_quantity": "quantity"})

# Save star schema
dim_customer.to_csv(os.path.join(PBI_DIR, "dim_customer.csv"), index=False)
dim_product.to_csv(os.path.join(PBI_DIR, "dim_product.csv"), index=False)
dim_region.to_csv(os.path.join(PBI_DIR, "dim_region.csv"), index=False)
dim_date.to_csv(os.path.join(PBI_DIR, "dim_date.csv"), index=False)
fact_sales.to_csv(os.path.join(PBI_DIR, "fact_sales.csv"), index=False)

print("\nStar schema saved to data/powerbi/:")
print(f"  fact_sales    : {len(fact_sales)} rows")
print(f"  dim_customer  : {len(dim_customer)} rows")
print(f"  dim_product   : {len(dim_product)} rows")
print(f"  dim_region    : {len(dim_region)} rows")
print(f"  dim_date      : {len(dim_date)} rows")
