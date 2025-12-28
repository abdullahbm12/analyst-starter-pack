SELECT
  b.service_type,
  COUNT(*) AS bookings,
  ROUND(SUM(f.revenue), 2) AS revenue,
  ROUND(SUM(f.cogs), 2) AS cogs,
  ROUND(SUM(f.contribution_margin), 2) AS contribution_margin,
  ROUND(1.0 * SUM(f.contribution_margin) / NULLIF(SUM(f.revenue),0), 4) AS cm_pct
FROM bookings b
JOIN finance f ON f.booking_id = b.booking_id
GROUP BY 1
ORDER BY revenue DESC;
