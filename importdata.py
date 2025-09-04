from pathlib import Path

# Define SQL content
sql_content = """-- Star schema DDL for the diagram (PostgreSQL/MySQL-compatible)

-- ===== Dimension tables =====
CREATE TABLE dim_store (
  store_id      INT PRIMARY KEY,
  store_address VARCHAR(256),
  city          VARCHAR(128),
  region        VARCHAR(128),
  state         VARCHAR(128),
  country       VARCHAR(128)
);

CREATE TABLE dim_sales_type (
  sales_type_id INT PRIMARY KEY,
  type_name     VARCHAR(128)
);

CREATE TABLE dim_employee (
  employee_id INT PRIMARY KEY,
  first_name  VARCHAR(128),
  last_name   VARCHAR(128),
  birth_year  INT
);

CREATE TABLE dim_time (
  time_id        INT PRIMARY KEY,
  action_date    DATE,
  action_week    INT,
  action_month   INT,
  action_year    INT,
  action_weekday VARCHAR(16)
);

CREATE TABLE dim_product (
  product_id   INT PRIMARY KEY,
  product_name VARCHAR(256),
  product_type VARCHAR(256)
);

-- ===== Fact table =====
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

-- Helpful indexes for common rollups
CREATE INDEX idx_fact_sales_time       ON fact_sales(time_id);
CREATE INDEX idx_fact_sales_store      ON fact_sales(store_id);
CREATE INDEX idx_fact_sales_employee   ON fact_sales(employee_id);
CREATE INDEX idx_fact_sales_product    ON fact_sales(product_id);
CREATE INDEX idx_fact_sales_salestype  ON fact_sales(sales_type_id);


-- (Optional) Management queries

-- 1) Doanh thu theo tháng & cửa hàng
SELECT
  t.action_year,
  t.action_month,
  s.store_id,
  SUM(f.price * f.quantity) AS revenue
FROM fact_sales f
JOIN dim_time   t ON f.time_id = t.time_id
JOIN dim_store  s ON f.store_id = s.store_id
GROUP BY t.action_year, t.action_month, s.store_id
ORDER BY t.action_year, t.action_month, s.store_id;

-- 2) Top 10 sản phẩm theo doanh thu
SELECT p.product_id, p.product_name,
       SUM(f.price * f.quantity) AS revenue
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.product_id, p.product_name
ORDER BY revenue DESC
LIMIT 10;

-- 3) Hiệu suất nhân viên theo loại bán hàng
SELECT e.employee_id,
       e.first_name, e.last_name,
       st.type_name,
       SUM(f.price * f.quantity) AS revenue
FROM fact_sales f
JOIN dim_employee   e  ON f.employee_id = e.employee_id
JOIN dim_sales_type st ON f.sales_type_id = st.sales_type_id
GROUP BY e.employee_id, e.first_name, e.last_name, st.type_name
ORDER BY revenue DESC;
"""

# Save to file
file_path = Path("/mnt/data/star_schema.sql")
file_path.write_text(sql_content, encoding="utf-8")

file_path
