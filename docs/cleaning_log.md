# Data Cleaning Log — Phase 1

**Source:** `data/raw/online_retail_II.csv` — single combined file covering
2009-12-01 to 2011-12-09 (Kaggle's "both sheets" are already merged here).

**Script:** `python/01_clean_explore.py`

## Profile (raw)
- 1,067,371 rows, 8 columns
- `Description`: 4,382 nulls
- `Customer ID`: 243,007 nulls (~22.8%)
- 34,335 exact duplicate rows
- 22,950 rows with negative `Quantity`
- 5 rows with negative `Price`, 6,202 rows with `Price` == 0
- 19,494 rows on cancelled invoices (`Invoice` starts with `C`)
- 6 rows on `A`-prefix invoices (bad-debt write-offs, e.g. `Price` = -53594.36)
- 68 distinct non-numeric-looking `StockCode`s — a mix of genuine
  postage/fee/admin codes (`POST`, `DOT`, `BANK CHARGES`, ...) **and** real
  products with alphanumeric codes (`79323LP`, `DCGS0058`, `15056BL`, ...)

## Decisions

| Issue | Decision | Rationale |
|---|---|---|
| Cancelled orders (`Invoice` starts with `C`) | **Keep**, flagged via `IsCancelled` | Needed for cancellation-rate analysis (Phase 3); dropping would understate churn/return signals |
| `A`-prefix invoices (6 rows) | **Dropped** | Internal bad-debt write-offs, not customer transactions — no `CustomerID`, nonsensical negative prices |
| Missing `CustomerID` (243k rows) | **Keep** rows, but exclude from customer-level analysis (RFM/CLV/clustering) | Still valid for revenue/product-level analysis; can't attribute to a customer so must be excluded downstream |
| Negative `Quantity` | **Keep** | Legitimate — corresponds to returns/cancellations, consistent with `IsCancelled` |
| `Price` <= 0 (6,202 rows after `A`-prefix drop) | **Dropped** | Data-entry artifacts / zero-value adjustments; contribute no real revenue and distort per-unit price metrics |
| Non-product `StockCode`s (postage, fees, manual adjustments, gift vouchers, test rows) | **Kept**, flagged via `IsNonProduct` using a curated code list — **not** a numeric-format regex, since several real products (`79323LP`, `DCGS0058`, `15056BL`) also have alphanumeric codes that a regex would misclassify | Needed for full revenue reconciliation, but excluded from product-level analysis (top products, market basket) |
| Exact duplicate rows (34,147 after price filter) | **Dropped** | Same invoice/stockcode/quantity/date/price repeated — data entry duplication, not repeat purchases |

## Derived fields added
- `LineTotal` = `Quantity * Price`
- `InvoiceDate` cast to datetime
- `IsCancelled` (bool)
- `IsNonProduct` (bool)

## Result
- Cleaned dataset: `data/processed/online_retail_clean.parquet`
- 1,027,016 rows (1,067,371 raw − 6 `A`-prefix − 6,202 zero/negative price − 34,147 duplicates)
