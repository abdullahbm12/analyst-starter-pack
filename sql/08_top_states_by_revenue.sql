SELECT
  u.state,
  COUNT(*) AS bookings,
  ROUND(SUM(f.revenue), 2) AS revenue,
  ROUND(SUM(f.contribution_margin), 2) AS contribution_margin
FROM bookings b
JOIN users u ON u.user_id = b.user_id
JOIN finance f ON f.booking_id = b.booking_id
GROUP BY 1
ORDER BY revenue DESC
LIMIT 10;
