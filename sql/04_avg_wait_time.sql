SELECT
  service_type,
  visit_mode,
  ROUND(AVG(wait_time_days), 2) AS avg_wait_days,
  COUNT(*) AS bookings
FROM bookings
GROUP BY 1,2
ORDER BY bookings DESC;
