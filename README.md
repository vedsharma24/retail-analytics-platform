# Retail Sales & Customer Analytics Platform

End-to-end analytics project on the **Online Retail II** dataset (UK-based online retailer, 2009-2011 transactions). Goal: go from raw transactional data to a full analytics stack — cleaned data, a normalized PostgreSQL warehouse, SQL-based analysis (revenue trends, RFM, cohorts), Python-based customer segmentation (K-means, CLV, market-basket analysis), an Excel cross-check, and a Power BI dashboard — telling one coherent business story.

## Stack
- **Python** — cleaning, exploration, clustering, CLV, market-basket analysis
- **PostgreSQL** — normalized warehouse (customers, products, orders, order_lines, countries)
- **DBeaver** — SQL client for Postgres
- **SQL** — analytical queries (revenue, RFM, cohorts, cancellations, country performance)
- **Excel** — reconciliation / what-if modeling
- **Power BI** — final dashboard, connected directly to Postgres

## Repo structure
```
/data
  /raw          raw Kaggle CSV (gitignored)
  /processed    cleaned dataset (gitignored)
/sql
  schema.sql
  /analysis     reusable analytical queries
/python         cleaning, loading, and analysis scripts/notebooks
/powerbi        Power BI files
/excel          reconciliation / what-if workbook
/docs           cleaning log, case study, notes
```

## Setup
1. Create/activate the venv: `python -m venv .venv` then `.venv\Scripts\activate` (Windows)
2. Install dependencies: `pip install -r requirements.txt`
3. PostgreSQL: local instance running on `localhost:5432`, database `retail_analytics`. Connection details are in `.env` (gitignored, not committed).
4. DBeaver: connect to `retail_analytics` using the same credentials as `.env`.
5. Dataset: place `online_retail_II.csv` (from Kaggle) in `/data/raw`.

## Status
Phase 0 (setup) in progress — see `CHECKLIST.md` for full project plan and progress.
