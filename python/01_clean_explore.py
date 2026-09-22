"""Phase 1: Load, clean, and explore the Online Retail II dataset."""
from pathlib import Path

import pandas as pd

RAW_PATH = "data/raw/online_retail_II.csv"
OUT_PATH = Path("data/processed/online_retail_clean.parquet")

# Step 1: Load & inspect
df = pd.read_csv(RAW_PATH, encoding="ISO-8859-1")
df.columns = [c.strip().replace(" ", "") for c in df.columns]  # "Customer ID" -> "CustomerID"

print("shape:", df.shape)
print()
print(df.dtypes)
print()
print(df.head(5).to_string())

# Step 2: Profile data quality
print("\n--- Step 2: Profiling ---\n")

print("Null counts:")
print(df.isnull().sum())

n_dupes = df.duplicated().sum()
print(f"\nExact duplicate rows: {n_dupes}")

n_neg_qty = (df["Quantity"] < 0).sum()
n_neg_price = (df["Price"] < 0).sum()
n_zero_price = (df["Price"] == 0).sum()
print(f"\nNegative Quantity rows: {n_neg_qty}")
print(f"Negative Price rows: {n_neg_price}")
print(f"Zero Price rows: {n_zero_price}")

is_cancelled = df["Invoice"].astype(str).str.startswith("C")
print(f"\nCancelled invoices (Invoice starts with 'C'): {is_cancelled.sum()} rows")

# Non-numeric StockCodes are a mix of genuine postage/fee/admin entries
# (POST, BANK CHARGES, ...) and real products with unusual codes (79323LP,
# DCGS0058, ...) - inspect before deciding which to flag as non-product.
is_numeric_like = df["StockCode"].astype(str).str.match(r"^\d{4,6}[A-Za-z]?$")
non_product_codes = df.loc[~is_numeric_like, "StockCode"].value_counts()
print(f"\nDistinct non-numeric-looking StockCodes: {len(non_product_codes)}")
print(non_product_codes.head(20))

# Step 3: Cleaning decisions (see docs/cleaning_log.md for full reasoning)
print("\n--- Step 3: Applying decisions ---\n")

# Derived fields, added before filtering so they're available for every kept row
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
df["IsCancelled"] = df["Invoice"].astype(str).str.startswith("C")
df["LineTotal"] = df["Quantity"] * df["Price"]

# Curated list of genuine non-product codes (postage, fees, manual/bad-debt
# adjustments, gift vouchers, test rows) - NOT a numeric-code regex, since
# several real products also have alphanumeric codes (79323LP, DCGS0058, ...)
NON_PRODUCT_CODES = {
    "POST", "DOT", "M", "D", "S", "B", "C2", "C3", "BANK CHARGES",
    "ADJUST", "ADJUST2", "AMAZONFEE", "CRUK", "PADS", "GIFT",
    "TEST001", "TEST002",
}
stock_code_upper = df["StockCode"].astype(str).str.upper()
df["IsNonProduct"] = stock_code_upper.isin(NON_PRODUCT_CODES) | stock_code_upper.str.startswith("GIFT_0001_")

before = len(df)

# Drop 'A'-prefix rows: internal bad-debt write-offs, not customer transactions
# (no Customer ID, nonsensical negative prices, e.g. -53594.36)
df = df[~df["Invoice"].astype(str).str.startswith("A")]
print(f"Dropped 'A'-prefix adjustment rows: {before - len(df)}")

# Drop zero-price rows: not real transactions, would corrupt revenue/RFM monetary calcs
before = len(df)
df = df[df["Price"] > 0]
print(f"Dropped zero/negative price rows: {before - len(df)}")

# Drop exact duplicate rows: same invoice/stockcode/quantity/date/price repeated
# is data-entry duplication, not a repeat purchase
before = len(df)
df = df.drop_duplicates()
print(f"Dropped exact duplicate rows: {before - len(df)}")

print(f"\nRows remaining: {len(df)}")

# Step 4: Save
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
df.to_parquet(OUT_PATH, index=False)
print(f"\nSaved cleaned dataset: {OUT_PATH} ({len(df):,} rows)")
