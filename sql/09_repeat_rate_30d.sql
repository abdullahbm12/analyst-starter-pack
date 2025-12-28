WITH completed AS (
  SELECT
    user_id,
    DATE(booking_date) AS d
  FROM bookings
  WHERE status='completed'
),
next_visit AS (
  SELECT
    c1.user_id,
    c1.d AS first_date,
    MIN(c2.d) AS next_date
  FROM completed c1
  LEFT JOIN completed c2
    ON c2.user_id = c1.user_id
   AND c2.d > c1.d
  GROUP BY 1,2
)
SELECT
  COUNT(*) AS completed_visits,
  SUM(CASE WHEN next_date IS NOT NULL AND (JULIANDAY(next_date) - JULIANDAY(first_date)) <= 30 THEN 1 ELSE 0 END) AS repeats_30d,
  ROUND(
    1.0 * SUM(CASE WHEN next_date IS NOT NULL AND (JULIANDAY(next_date) - JULIANDAY(first_date)) <= 30 THEN 1 ELSE 0 END)
    / COUNT(*)
  , 4) AS repeat_rate_30d
FROM next_visit;
