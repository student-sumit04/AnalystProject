-- Fashion Ecommerce Funnel & Retention Analytics
-- SQL templates for business analyst portfolio discussion.
-- Dialect: broadly compatible with SQLite/Postgres style date functions may need adaptation.

-- 1. Daily funnel health
WITH daily_funnel AS (
    SELECT
        event_date,
        COUNT(DISTINCT CASE WHEN event_type = 'visit' THEN session_id END) AS visits,
        COUNT(DISTINCT CASE WHEN event_type = 'product_view' THEN session_id END) AS product_views,
        COUNT(DISTINCT CASE WHEN event_type = 'add_to_cart' THEN session_id END) AS carts,
        COUNT(DISTINCT CASE WHEN event_type = 'checkout_start' THEN session_id END) AS checkouts,
        COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN session_id END) AS purchases
    FROM events
    GROUP BY event_date
)
SELECT
    event_date,
    visits,
    product_views,
    carts,
    checkouts,
    purchases,
    1.0 * product_views / NULLIF(visits, 0) AS visit_to_view_rate,
    1.0 * carts / NULLIF(product_views, 0) AS view_to_cart_rate,
    1.0 * checkouts / NULLIF(carts, 0) AS cart_to_checkout_rate,
    1.0 * purchases / NULLIF(checkouts, 0) AS checkout_to_purchase_rate,
    1.0 * purchases / NULLIF(visits, 0) AS visit_to_purchase_rate
FROM daily_funnel
ORDER BY event_date;

-- 2. Category conversion and revenue contribution
SELECT
    category,
    COUNT(DISTINCT session_id) AS sessions,
    COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN session_id END) AS purchase_sessions,
    1.0 * COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN session_id END)
        / NULLIF(COUNT(DISTINCT session_id), 0) AS conversion_rate,
    SUM(CASE WHEN event_type = 'purchase' THEN revenue ELSE 0 END) AS revenue
FROM events
GROUP BY category
ORDER BY revenue DESC;

-- 3. Root-cause scan by city, channel, and category
SELECT
    city,
    channel,
    category,
    COUNT(DISTINCT session_id) AS sessions,
    COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN session_id END) AS purchases,
    1.0 * COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN session_id END)
        / NULLIF(COUNT(DISTINCT session_id), 0) AS conversion_rate
FROM events
GROUP BY city, channel, category
HAVING COUNT(DISTINCT session_id) >= 100
ORDER BY conversion_rate ASC;

-- 4. A/B test summary for free-shipping nudge
SELECT
    experiment_group,
    COUNT(DISTINCT session_id) AS sessions,
    COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN session_id END) AS purchases,
    1.0 * COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN session_id END)
        / NULLIF(COUNT(DISTINCT session_id), 0) AS conversion_rate,
    SUM(CASE WHEN event_type = 'purchase' THEN revenue ELSE 0 END) AS revenue
FROM events
GROUP BY experiment_group;

-- 5. Monthly acquisition cohort retention
WITH first_order AS (
    SELECT customer_id, MIN(order_date) AS first_order_date
    FROM orders
    GROUP BY customer_id
),
cohort_orders AS (
    SELECT
        o.customer_id,
        substr(f.first_order_date, 1, 7) AS cohort_month,
        substr(o.order_date, 1, 7) AS order_month
    FROM orders o
    JOIN first_order f ON o.customer_id = f.customer_id
)
SELECT
    cohort_month,
    order_month,
    COUNT(DISTINCT customer_id) AS active_customers
FROM cohort_orders
GROUP BY cohort_month, order_month
ORDER BY cohort_month, order_month;
