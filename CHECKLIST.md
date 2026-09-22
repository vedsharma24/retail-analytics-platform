# Online Retail II Analytics Project — Checklist

**Pace:** Full-time, ~10–11 working days
**Stack:** Python, PostgreSQL, DBeaver, SQL, Excel, Power BI

---

## Phase 0 — Setup (Day 1)
- [x] Create GitHub repo with folder structure (`/data`, `/sql`, `/python`, `/powerbi`, `/excel`, `/docs`)
- [x] Set up Python virtual environment
- [x] Install packages: `pandas`, `numpy`, `sqlalchemy`, `psycopg2-binary`, `scikit-learn`, `matplotlib`, `seaborn`, `jupyter`
- [x] Install/confirm PostgreSQL running locally (or via Docker)
- [ ] Connect DBeaver to local Postgres instance, confirm it can browse/query
- [x] Download Online Retail II dataset from Kaggle, place in `/data/raw`
- [x] Write initial `README.md` with project goal/stack (fill in details as you go)

## Phase 1 — Clean & Explore in Python (Days 2–3)
- [x] Load both sheets/years, merge into single dataframe
- [x] Profile data: nulls, dtypes, duplicates, negative values
- [x] Decide + document handling for: cancelled orders (`C` prefix), missing `CustomerID`, negative `Quantity`/`UnitPrice`, non-product stock codes (postage, fees, manual entries)
- [x] Deduplicate line items where appropriate
- [x] Create derived fields (`LineTotal`, cleaned `InvoiceDate` as datetime, `IsCancelled` flag)
- [x] Save cleaned dataset to `/data/processed` (parquet or CSV)
- [x] Write up cleaning decisions in a short markdown log

## Phase 2 — Schema Design & Load into PostgreSQL (Days 4–5)
- [ ] Design normalized schema: `customers`, `products`, `orders`, `order_lines`, `countries`
- [ ] Write DDL scripts (`/sql/schema.sql`)
- [ ] Create tables in Postgres via DBeaver
- [ ] Write Python load script (SQLAlchemy) to push cleaned data into schema
- [ ] Validate row counts / spot-check a few records match source data

## Phase 3 — SQL Analytical Layer (Days 5.5–7)
- [ ] Monthly revenue trend query
- [ ] Top products / top customers queries
- [ ] RFM base query (recency, frequency, monetary per customer)
- [ ] Cohort retention query (first-purchase month vs. repeat-purchase month) using window functions
- [ ] Cancellation/return rate query
- [ ] Country-level performance query
- [ ] Save all as reusable `.sql` files in `/sql/analysis`

## Phase 4 — Advanced Python Analysis (Days 8–9)
- [ ] Pull RFM base table from Postgres into pandas
- [ ] K-means clustering on RFM → customer segments
- [ ] CLV estimate (simple or cohort-based)
- [ ] Market-basket / association-rule analysis (products bought together)
- [ ] Visualizations for case study (segment sizes, CLV distribution, basket rules)

## Phase 5 — Excel Cross-Check (Day 10, half day)
- [ ] Build either: (a) pivot-table reconciliation of key SQL numbers, or (b) a pricing/discount what-if model
- [ ] Document which one and why in README

## Phase 6 — Power BI Dashboard (Days 10–11)
- [ ] Connect Power BI directly to PostgreSQL
- [ ] Build star-schema data model + DAX measures
- [ ] Build pages: Sales Overview, Customer Segmentation (RFM), Product Performance, Geography
- [ ] Polish formatting/visuals

## Phase 7 — Documentation & Polish (Day 11)
- [ ] Finalize README (stack, why each tool, how to run)
- [ ] Write 1-page case study: 3–4 insights + business recommendations
- [ ] Clean repo, remove dead code/notebooks
- [ ] Final pass: does the story connect SQL → Python → BI into one narrative?
