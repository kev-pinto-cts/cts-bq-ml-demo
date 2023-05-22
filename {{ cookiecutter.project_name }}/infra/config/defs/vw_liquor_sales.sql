SELECT
 date as day,
 item_description AS item_name,
 SUM(bottles_sold) AS total_amount_sold
FROM `iowa_demo.sales`
WHERE date BETWEEN '2021-01-01' AND '2022-06-30'
GROUP BY 1,2
