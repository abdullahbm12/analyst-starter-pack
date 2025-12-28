SELECT
  COUNT(*) AS responses,
  ROUND(AVG(nps), 2) AS avg_nps,
  SUM(CASE WHEN nps >= 9 THEN 1 ELSE 0 END) AS promoters,
  SUM(CASE WHEN nps <= 6 THEN 1 ELSE 0 END) AS detractors,
  ROUND(
    100.0 * SUM(CASE WHEN nps >= 9 THEN 1 ELSE 0 END) / COUNT(*)
    - 100.0 * SUM(CASE WHEN nps <= 6 THEN 1 ELSE 0 END) / COUNT(*)
  , 2) AS nps_score
FROM fulfillment;
