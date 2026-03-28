-- ============================================================
-- Customer Segmentation & RFM Analysis
-- Tool: SQLite (run via Python notebook or any SQL client)
-- Table: transactions (loaded from Online Retail II dataset)
-- ============================================================


-- ─────────────────────────────────────────────────
-- Query 1: Overall business metrics
-- ─────────────────────────────────────────────────
SELECT
    COUNT(DISTINCT "Customer ID")           AS total_customers,
    COUNT(DISTINCT Invoice)                  AS total_orders,
    ROUND(SUM(Revenue), 2)                   AS total_revenue,
    ROUND(AVG(Revenue), 2)                   AS avg_order_value
FROM transactions;


-- ─────────────────────────────────────────────────
-- Query 2: Top 10 customers by revenue
-- ─────────────────────────────────────────────────
SELECT
    "Customer ID",
    COUNT(DISTINCT Invoice)         AS total_orders,
    ROUND(SUM(Revenue), 2)          AS total_revenue,
    ROUND(AVG(Revenue), 2)          AS avg_order_value
FROM transactions
GROUP BY "Customer ID"
ORDER BY total_revenue DESC
LIMIT 10;


-- ─────────────────────────────────────────────────
-- Query 3: Monthly revenue trend
-- ─────────────────────────────────────────────────
SELECT
    SUBSTR(InvoiceDate, 1, 7)       AS month,
    COUNT(DISTINCT Invoice)         AS orders,
    COUNT(DISTINCT "Customer ID")   AS unique_customers,
    ROUND(SUM(Revenue), 2)          AS monthly_revenue
FROM transactions
GROUP BY month
ORDER BY month;


-- ─────────────────────────────────────────────────
-- Query 4: Revenue by country
-- ─────────────────────────────────────────────────
SELECT
    Country,
    COUNT(DISTINCT "Customer ID")   AS customers,
    ROUND(SUM(Revenue), 2)          AS total_revenue,
    ROUND(100.0 * SUM(Revenue) /
        (SELECT SUM(Revenue) FROM transactions), 2) AS revenue_pct
FROM transactions
GROUP BY Country
ORDER BY total_revenue DESC
LIMIT 10;


-- ─────────────────────────────────────────────────
-- Query 5: RFM metrics per customer
-- Recency = days since last purchase
-- Frequency = number of unique orders
-- Monetary = total spend
-- ─────────────────────────────────────────────────
SELECT
    "Customer ID",
    CAST(JULIANDAY('now') - JULIANDAY(MAX(InvoiceDate)) AS INTEGER)
                                    AS recency_days,
    COUNT(DISTINCT Invoice)         AS frequency,
    ROUND(SUM(Revenue), 2)          AS monetary
FROM transactions
GROUP BY "Customer ID"
ORDER BY monetary DESC;


-- ─────────────────────────────────────────────────
-- Query 6: Average Order Value (AOV) by country
-- ─────────────────────────────────────────────────
SELECT
    Country,
    COUNT(DISTINCT Invoice)         AS orders,
    ROUND(SUM(Revenue), 2)          AS total_revenue,
    ROUND(SUM(Revenue) /
          COUNT(DISTINCT Invoice), 2) AS avg_order_value
FROM transactions
GROUP BY Country
HAVING COUNT(DISTINCT Invoice) > 50
ORDER BY avg_order_value DESC
LIMIT 10;


-- ─────────────────────────────────────────────────
-- Query 7: High-value customers (top 20% by spend)
-- ─────────────────────────────────────────────────
WITH customer_spend AS (
    SELECT
        "Customer ID",
        ROUND(SUM(Revenue), 2) AS total_spend
    FROM transactions
    GROUP BY "Customer ID"
),
percentile AS (
    SELECT PERCENTILE_CONT(0.80) WITHIN GROUP (ORDER BY total_spend) AS p80
    FROM customer_spend
)
SELECT
    c."Customer ID",
    c.total_spend
FROM customer_spend c, percentile p
WHERE c.total_spend >= p.p80
ORDER BY c.total_spend DESC;
