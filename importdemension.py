from pathlib import Path

sql = """-- Star schema (expanded) DDL for the second diagram
-- Target: ANSI SQL (works on PostgreSQL/MySQL with minor/no changes)

/* =====================
   Dimension tables
   ===================== */

CREATE TABLE dim_sales_type (
  sales_type_id INT PRIMARY KEY,
  type_name     VARCHAR(128) NOT NULL
);

CREATE TABLE dim_employee (
  employee_id INT PRIMARY KEY,
  first_name  VARCHAR(128),
  last_name   VARCHAR(128),
  birth_year  INT
);

-- Optional: this is shown as FK to a city table in the diagram.
-- If you have a city dimension, create it and add the FK.
CREATE TABLE dim_store (
  store_id      INT PRIMARY KEY,
  store_address VARCHAR(256),
  city_id       INT  -- FK to dim_city(city_id) if available
);

CREATE TABLE dim_product_type (
  product_type_id   INT PRIMARY KEY,
  product_type_name VARCHAR(256) NOT NULL
);

CREATE TABLE dim_product (
  product_id     INT PRIMARY KEY,
  product_name   VARCHAR(256),
  product_type_id INT NOT NULL,
  CONSTRAINT fk_product_type
    FOREIGN KEY (product_type_id)
    REFERENCES dim_product_type(product_type_id)
      ON UPDATE CASCADE ON DELETE RESTRICT
);

-- Time sub-dimensions
CREATE TABLE dim_week (
  week_id     INT PRIMARY KEY,
  action_week INT NOT NULL
);

CREATE TABLE dim_month (
  month_id     INT PRIMARY KEY,
  action_month INT NOT NULL
);

CREATE TABLE dim_year (
  year_id     INT PRIMARY KEY,
  action_year INT NOT NULL
);

CREATE TABLE dim_weekday (
  weekday_id      INT PRIMARY KEY,
  action_weekday  VARCHAR(16) NOT NULL
);

-- Central time dimension referencing the sub-dimensions
CREATE TABLE dim_time (
  time_id     INT PRIMARY KEY,
  action_date DATE NOT NULL,
  week_id     INT NOT NULL,
  month_id    INT NOT NULL,
  year_id     INT NOT NULL,
  weekday_id  INT NOT NULL,
  CONSTRAINT fk_time_week
    FOREIGN KEY (week_id) REFERENCES dim_week(week_id)
      ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_time_month
    FOREIGN KEY (month_id) REFERENCES dim_month(month_id)
      ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_time_year
    FOREIGN KEY (year_id) REFERENCES dim_year(year_id)
      ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_time_weekday
    FOREIGN KEY (weekday_id) REFERENCES dim_weekday(weekday_id)
      ON UPDATE CASCADE ON DELETE RESTRICT
);

/* =====================
   Fact table
   ===================== */
CREATE TABLE fact_sales (
  product_id     INT NOT NULL,
  time_id        INT NOT NULL,
  store_id       INT NOT NULL,
  employee_id    INT NOT NULL,
  sales_type_id  INT NOT NULL,
  price          DECIMAL(8,2) NOT NULL,
  quantity       DECIMAL(8,2) NOT NULL,
  PRIMARY KEY (product_id, time_id, store_id, employee_id, sales_type_id),
  CONSTRAINT fk_fact_product
    FOREIGN KEY (product_id) REFERENCES dim_product(product_id)
      ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_fact_time
    FOREIGN KEY (time_id) REFERENCES dim_time(time_id)
      ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_fact_store
    FOREIGN KEY (store_id) REFERENCES dim_store(store_id)
      ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_fact_employee
    FOREIGN KEY (employee_id) REFERENCES dim_employee(employee_id)
      ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_fact_sales_type
    FOREIGN KEY (sales_type_id) REFERENCES dim_sales_type(sales_type_id)
      ON UPDATE CASCADE ON DELETE RESTRICT
);

/* =====================
   Helpful Indexes
   ===================== */
CREATE INDEX idx_fact_sales_time        ON fact_sales(time_id);
CREATE INDEX idx_fact_sales_store       ON fact_sales(store_id);
CREATE INDEX idx_fact_sales_employee    ON fact_sales(employee_id);
CREATE INDEX idx_fact_sales_product     ON fact_sales(product_id);
CREATE INDEX idx_fact_sales_salestype   ON fact_sales(sales_type_id);

CREATE INDEX idx_time_week     ON dim_time(week_id);
CREATE INDEX idx_time_month    ON dim_time(month_id);
CREATE INDEX idx_time_year     ON dim_time(year_id);
CREATE INDEX idx_time_weekday  ON dim_time(weekday_id);

/* =====================
   Sample management queries
   ===================== */

-- Revenue by year/month and product type
SELECT
  y.action_year,
  m.action_month,
  pt.product_type_name,
  SUM(f.price * f.quantity) AS revenue
FROM fact_sales f
JOIN dim_time t       ON f.time_id = t.time_id
JOIN dim_month m      ON t.month_id = m.month_id
JOIN dim_year y       ON t.year_id = y.year_id
JOIN dim_product p    ON f.product_id = p.product_id
JOIN dim_product_type pt ON p.product_type_id = pt.product_type_id
GROUP BY y.action_year, m.action_month, pt.product_type_name
ORDER BY y.action_year, m.action_month, pt.product_type_name;

-- Employee performance by sales type (this month)
-- Adjust predicates for your dialect/date handling.
SELECT
  e.employee_id,
  e.first_name, e.last_name,
  st.type_name,
  SUM(f.price * f.quantity) AS revenue
FROM fact_sales f
JOIN dim_employee e   ON f.employee_id = e.employee_id
JOIN dim_sales_type st ON f.sales_type_id = st.sales_type_id
JOIN dim_time t       ON f.time_id = t.time_id
JOIN dim_month m      ON t.month_id = m.month_id
JOIN dim_year y       ON t.year_id = y.year_id
WHERE y.action_year = EXTRACT(YEAR FROM CURRENT_DATE)
  AND m.action_month = EXTRACT(MONTH FROM CURRENT_DATE)
GROUP BY e.employee_id, e.first_name, e.last_name, st.type_name
ORDER BY revenue DESC;

-- Weekly trend for a given product_id
-- :product_id should be bound from your application.
SELECT
  w.action_week,
  y.action_year,
  SUM(f.price * f.quantity) AS revenue
FROM fact_sales f
JOIN dim_time t ON f.time_id = t.time_id
JOIN dim_week w ON t.week_id = w.week_id
JOIN dim_year y ON t.year_id = y.year_id
WHERE f.product_id = :product_id
GROUP BY y.action_year, w.action_week
ORDER BY y.action_year, w.action_week;
"""

path = Path("/mnt/data/star_schema_expanded.sql")
path.write_text(sql, encoding="utf-8")
path
