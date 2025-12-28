# Healthcare Store Analyst Starter Pack (Synthetic)

An analyst “starter pack” for a healthcare marketplace/store:
- SQLite database
- SQL question bank
- Streamlit dashboard (KPIs, funnel, channel conversion, service margin)
- Fully synthetic data (no PHI)

## What this answers
- How is the funnel performing (sessions → bookings → completed)?
- Which acquisition channels convert best?
- Which services drive the most contribution margin?
- What trends/risks show up (e.g., cancellation rate)?

## How to run locally
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt

python scripts/01_generate_data.py
python scripts/02_build_sqlite.py
streamlit run app.py
