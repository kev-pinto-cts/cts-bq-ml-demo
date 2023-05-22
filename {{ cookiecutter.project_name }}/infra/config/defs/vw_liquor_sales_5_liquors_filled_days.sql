WITH
  top_5_sales AS (
  SELECT
    item_name,
    COUNT(*) qty_days
  FROM
    `iowa_demo.liquor_sales`
  GROUP BY
    item_name QUALIFY DENSE_RANK() OVER(ORDER BY qty_days DESC) <= 5 ),
  calendar AS (
  SELECT
    day
  FROM
    UNNEST(GENERATE_DATE_ARRAY('2021-01-01', '2022-06-30')) day),
  cross_joined_calendar_with_top_5_items AS (
  SELECT
    sl.item_name,
    cl.day
  FROM
    calendar cl,
    top_5_sales sl )
SELECT
  cj.item_name,
  cj.day,
  COALESCE(ls.total_amount_sold,0) total_amount_sold
FROM
  cross_joined_calendar_with_top_5_items cj
LEFT JOIN
  iowa_demo.liquor_sales ls
ON
  (cj.item_name=ls.item_name
    AND cj.day=ls.day)
ORDER BY
  cj.item_name,
  cj.day
