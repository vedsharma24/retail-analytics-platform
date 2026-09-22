"""Phase 2: load the cleaned dataset into PostgreSQL per sql/schema.sql."""
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

load_dotenv()

DATA_PATH = Path("data/processed/online_retail_clean.parquet")
SCHEMA_PATH = Path("sql/schema.sql")

# Built via URL.create (not string interpolation) so special characters in
# PGPASSWORD (e.g. "@") are percent-encoded correctly.
engine = create_engine(URL.create(
    "postgresql+psycopg2",
    username=os.environ["PGUSER"],
    password=os.environ["PGPASSWORD"],
    host=os.environ["PGHOST"],
    port=int(os.environ["PGPORT"]),
    database=os.environ["PGDATABASE"],
))

df = pd.read_parquet(DATA_PATH)
print(f"Loaded {len(df):,} rows from {DATA_PATH}")

# Step 1: (re)create schema
with engine.begin() as conn:
    conn.execute(text(SCHEMA_PATH.read_text()))
print("Schema created.")

# Step 2: countries
countries = pd.DataFrame({"country_name": sorted(df["Country"].dropna().unique())})
countries.to_sql("countries", engine, if_exists="append", index=False)
country_ids = pd.read_sql("SELECT country_id, country_name FROM countries", engine)
country_map = dict(zip(country_ids["country_name"], country_ids["country_id"]))
print(f"Loaded {len(countries):,} countries.")

# Step 3: customers — most frequent country per customer resolves the 13
# customers with >1 distinct country in the source data
cust_rows = df.dropna(subset=["CustomerID"])
customer_country = (
    cust_rows.groupby("CustomerID")["Country"]
    .agg(lambda s: s.value_counts().idxmax())
    .reset_index()
)
customers = pd.DataFrame({
    "customer_id": customer_country["CustomerID"].astype("int64"),
    "country_id": customer_country["Country"].map(country_map),
})
customers.to_sql("customers", engine, if_exists="append", index=False)
print(f"Loaded {len(customers):,} customers.")

# Step 4: products — most frequent description per stock code resolves the
# 648 codes with >1 distinct description in the source data
product_desc = (
    df.groupby("StockCode")["Description"]
    .agg(lambda s: s.value_counts().idxmax() if s.notna().any() else None)
)
product_flag = df.groupby("StockCode")["IsNonProduct"].any()
products = pd.DataFrame({
    "stock_code": product_desc.index,
    "description": product_desc.values,
    "is_non_product": product_flag.reindex(product_desc.index).values,
})
products.to_sql("products", engine, if_exists="append", index=False)
print(f"Loaded {len(products):,} products.")

# Step 5: orders — one row per invoice, collapsed from line items.
# Within an invoice, CustomerID/Country/IsCancelled are consistent in the
# source data, so the first value per group is representative.
orders_src = df.groupby("Invoice", as_index=False).agg(
    CustomerID=("CustomerID", "first"),
    Country=("Country", "first"),
    InvoiceDate=("InvoiceDate", "first"),
    IsCancelled=("IsCancelled", "first"),
)
customer_id_set = set(customers["customer_id"])
orders = pd.DataFrame({
    "invoice": orders_src["Invoice"],
    "customer_id": orders_src["CustomerID"].apply(
        lambda v: int(v) if pd.notna(v) and int(v) in customer_id_set else None
    ),
    "country_id": orders_src["Country"].map(country_map),
    "invoice_date": orders_src["InvoiceDate"],
    "is_cancelled": orders_src["IsCancelled"],
})
orders.to_sql("orders", engine, if_exists="append", index=False)
print(f"Loaded {len(orders):,} orders.")

# Step 6: order_lines — one row per source transaction line
order_lines = pd.DataFrame({
    "invoice": df["Invoice"],
    "stock_code": df["StockCode"],
    "quantity": df["Quantity"],
    "price": df["Price"],
    "line_total": df["LineTotal"],
})
order_lines.to_sql("order_lines", engine, if_exists="append", index=False, chunksize=50_000)
print(f"Loaded {len(order_lines):,} order lines.")

print("\nDone.")
