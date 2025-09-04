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
