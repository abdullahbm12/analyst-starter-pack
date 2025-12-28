WITH sess AS (
  SELECT session_id, service_type
  FROM sessions
),
book AS (
  SELECT session_id, status
  FROM bookings
)
SELECT
  s.service_type,
  COUNT(*) AS sessions,
  SUM(CASE WHEN b.session_id IS NOT NULL THEN 1 ELSE 0 END) AS bookings,
  SUM(CASE WHEN b.status = 'completed' THEN 1 ELSE 0 END) AS completed,
  ROUND(1.0 * SUM(CASE WHEN b.session_id IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 4) AS session_to_booking,
  ROUND(1.0 * SUM(CASE WHEN b.status = 'completed' THEN 1 ELSE 0 END) / COUNT(*), 4) AS session_to_complete
FROM sess s
LEFT JOIN book b ON b.session_id = s.session_id
GROUP BY 1
ORDER BY sessions DESC;
