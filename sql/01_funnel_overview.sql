WITH base AS (
  SELECT s.session_id
  FROM sessions s
),
q AS (
  SELECT session_id FROM quotes
),
b AS (
  SELECT session_id, booking_id, status
  FROM bookings
),
c AS (
  SELECT session_id
  FROM bookings
  WHERE status = 'completed'
)
SELECT
  (SELECT COUNT(*) FROM base) AS sessions,
  (SELECT COUNT(*) FROM q)    AS quotes,
  (SELECT COUNT(*) FROM b)    AS bookings,
  (SELECT COUNT(*) FROM c)    AS completed,
  ROUND(1.0 * (SELECT COUNT(*) FROM b) / (SELECT COUNT(*) FROM base), 4) AS session_to_booking,
  ROUND(1.0 * (SELECT COUNT(*) FROM c) / (SELECT COUNT(*) FROM base), 4) AS session_to_complete;
