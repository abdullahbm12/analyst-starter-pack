# Healthcare Store Analyst Starter Pack (Synthetic)

A lightweight analytics dashboard simulating how an analyst at a healthcare marketplace
might evaluate funnel performance, channel efficiency, and service-level margins.

🔗 Live dashboard: https://analyst-starter-pack.streamlit.app/

## What this shows
- Session → quote → booking → completion funnel
- Conversion efficiency by acquisition channel
- Contribution margin by service line
- Auto-generated insights an analyst could surface to leadership

## Why this exists
This project mirrors the type of exploratory and decision-support analysis
an early-career analyst might do when partnering with operations, growth,
and finance leaders at a healthcare marketplace.

All data is **synthetic**, generated to reflect realistic healthcare workflows.

## Stack
- Python
- SQLite
- SQL (CTEs, aggregation, joins)
- Pandas
- Streamlit
- Plotly

## How to run locally
```bash
pip install -r requirements.txt
streamlit run app.py

