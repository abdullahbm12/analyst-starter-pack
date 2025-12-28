SELECT
  ROUND(SUM(revenue), 2) AS revenue,
  ROUND(SUM(cogs), 2) AS cogs,
  ROUND(SUM(contribution_margin), 2) AS contribution_margin,
  ROUND(1.0 * SUM(contribution_margin) / NULLIF(SUM(revenue),0), 4) AS cm_pct
FROM finance;
