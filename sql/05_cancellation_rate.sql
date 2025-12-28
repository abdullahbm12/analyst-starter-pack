SELECT
  service_type,
  COUNT(*) AS bookings,
  SUM(CASE WHEN status='cancelled' THEN 1 ELSE 0 END) AS cancelled,
  ROUND(1.0 * SUM(CASE WHEN status='cancelled' THEN 1 ELSE 0 END) / COUNT(*), 4) AS cancel_rate
FROM bookings
GROUP BY 1
ORDER BY cancel_rate DESC;
