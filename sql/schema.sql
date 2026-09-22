-- Phase 2: normalized schema for the Online Retail II analytics platform.
-- Source: data/processed/online_retail_clean.parquet (see docs/cleaning_log.md).

DROP TABLE IF EXISTS order_lines CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS countries CASCADE;

CREATE TABLE countries (
    country_id   SERIAL PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL UNIQUE
);

-- customer_id is the source CustomerID; rows with no CustomerID in the raw
-- data have no row here and are referenced only via orders.customer_id NULL.
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    country_id  INTEGER REFERENCES countries(country_id)
);

-- Description isn't 1:1 with StockCode in the raw data (typos/variants);
-- the load script picks the most frequent description per code as canonical.
CREATE TABLE products (
    stock_code     VARCHAR(20) PRIMARY KEY,
    description    VARCHAR(255),
    is_non_product BOOLEAN NOT NULL DEFAULT FALSE
);

-- One row per invoice, collapsed from the line-item source data.
CREATE TABLE orders (
    invoice      VARCHAR(10) PRIMARY KEY,
    customer_id  INTEGER REFERENCES customers(customer_id),
    country_id   INTEGER REFERENCES countries(country_id),
    invoice_date TIMESTAMP NOT NULL,
    is_cancelled BOOLEAN NOT NULL
);

CREATE TABLE order_lines (
    order_line_id BIGSERIAL PRIMARY KEY,
    invoice       VARCHAR(10) NOT NULL REFERENCES orders(invoice),
    stock_code    VARCHAR(20) NOT NULL REFERENCES products(stock_code),
    quantity      INTEGER NOT NULL,
    price         NUMERIC(12, 4) NOT NULL,
    line_total    NUMERIC(14, 4) NOT NULL
);

CREATE INDEX idx_customers_country_id ON customers(country_id);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_country_id ON orders(country_id);
CREATE INDEX idx_order_lines_invoice ON order_lines(invoice);
CREATE INDEX idx_order_lines_stock_code ON order_lines(stock_code);
