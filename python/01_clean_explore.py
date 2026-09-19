"""
Phase 1 - Clean & Explore
Loads the raw Online Retail II data, profiles it, applies cleaning
decisions, and writes the cleaned dataset to /data/processed.
"""
import pandas as pd
import numpy as np
from pathlib import Path

RAW_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "online_retail_II.csv"
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "online_retail_clean.parquet"

# ---------------------------------------------------------------------------
# 1. Load
# ---------------------------------------------------------------------------
df = pd.read_csv(RAW_PATH, encoding="latin1")
df.columns = [c.strip().replace(" ", "") for c in df.columns]  # "Customer ID" -> "CustomerID"
print(f"Loaded {len(df):,} rows, {df.shape[1]} columns")
print(df.dtypes)

# ---------------------------------------------------------------------------
# 2. Profile
# ---------------------------------------------------------------------------
print("\n--- Nulls ---")
print(df.isna().sum())

print("\n--- Duplicates (full row) ---")
print(df.duplicated().sum())

print("\n--- Negative Quantity ---")
print((df["Quantity"] < 0).sum())

print("\n--- Negative/zero Price ---")
print((df["Price"] <= 0).sum())

print("\n--- Cancelled invoices (Invoice starts with 'C') ---")
df["Invoice"] = df["Invoice"].astype(str)
print(df["Invoice"].str.startswith("C").sum())

print("\n--- Non-numeric StockCodes (likely fees/postage/manual) ---")
non_product = df.loc[~df["StockCode"].astype(str).str.match(r"^\d{5}"), "StockCode"].value_counts()
print(non_product.head(20))

# ---------------------------------------------------------------------------
# 3. Cleaning decisions
# ---------------------------------------------------------------------------
# - IsCancelled flag for Invoice starting with 'C' (kept, not dropped -
#   needed for cancellation-rate analysis in Phase 3)
# - Missing CustomerID rows kept but flagged; excluded from customer-level
#   analysis (RFM/CLV/clustering) later, since they can't be attributed
# - Negative Quantity: legitimate for returns/cancellations (paired with
#   IsCancelled) - kept, not clipped
# - Price <= 0: drop, these are data-entry artifacts (adjustments, free
#   samples with 0 price add no revenue signal and can distort per-unit metrics)
# - Non-product StockCodes (POST, DOT, M, BANK CHARGES, etc.): flagged via
#   IsNonProduct so they can be excluded from product-level analysis while
#   staying in revenue totals

NON_PRODUCT_CODES = {"POST", "DOT", "M", "MANUAL", "BANK CHARGES", "AMAZONFEE",
                      "CRUK", "PADS", "C2", "TEST001", "TEST002", "ADJUST", "ADJUST2"}

df["IsCancelled"] = df["Invoice"].str.startswith("C")
df["IsNonProduct"] = df["StockCode"].astype(str).str.upper().isin(NON_PRODUCT_CODES)
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
df["LineTotal"] = df["Quantity"] * df["Price"]

before = len(df)
df = df[df["Price"] > 0].copy()
print(f"\nDropped {before - len(df):,} rows with Price <= 0")

# ---------------------------------------------------------------------------
# 4. Deduplicate
# ---------------------------------------------------------------------------
before = len(df)
df = df.drop_duplicates()
print(f"Dropped {before - len(df):,} exact duplicate rows")

# ---------------------------------------------------------------------------
# 5. Save
# ---------------------------------------------------------------------------
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
df.to_parquet(OUT_PATH, index=False)
print(f"\nSaved cleaned dataset: {OUT_PATH} ({len(df):,} rows)")
