import sqlite3
from datetime import date

import pandas as pd
import streamlit as st
import plotly.express as px

DB_PATH = "data/gm.db"

st.set_page_config(page_title="Healthcare Store Analyst Starter Pack", layout="wide")

@st.cache_data(show_spinner=False)
def load_table(table: str) -> pd.DataFrame:
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM {table};", con)
    con.close()
    df.columns = [c.strip().lower() for c in df.columns]
    return df

# Load base tables
users = load_table("users")
sessions = load_table("sessions")
quotes = load_table("quotes")
bookings = load_table("bookings")
finance = load_table("finance")

# Normalize dates
sessions["session_date"] = pd.to_datetime(sessions["session_date"])
bookings["booking_date"] = pd.to_datetime(bookings["booking_date"])

st.title("Healthcare Store Analyst Starter Pack (Synthetic)")
st.caption("KPIs + Funnel + Mix + Margin — powered by SQLite")

# ---------------- Filters ----------------
min_d = sessions["session_date"].min().date()
max_d = sessions["session_date"].max().date()

with st.sidebar:
    st.header("Filters")
    dr = st.date_input("Session date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)

    all_services = ["All"] + sorted(sessions["service_type"].unique().tolist())
    all_channels = ["All"] + sorted(sessions["channel"].unique().tolist())

    svc = st.selectbox("Service", all_services, index=0)
    ch = st.selectbox("Channel", all_channels, index=0)

# Coerce date range selection
if isinstance(dr, tuple) and len(dr) == 2:
    start_d, end_d = dr
else:
    start_d, end_d = min_d, max_d

# Apply filters on sessions
f_sessions = sessions[(sessions["session_date"].dt.date >= start_d) & (sessions["session_date"].dt.date <= end_d)].copy()
if svc != "All":
    f_sessions = f_sessions[f_sessions["service_type"] == svc]
if ch != "All":
    f_sessions = f_sessions[f_sessions["channel"] == ch]

# Filter related tables by session_id
sess_ids = set(f_sessions["session_id"].unique())
f_quotes = quotes[quotes["session_id"].isin(sess_ids)].copy()
f_bookings = bookings[bookings["session_id"].isin(sess_ids)].copy()
f_finance = finance[finance["booking_id"].isin(f_bookings["booking_id"].unique())].copy()

# ---------------- KPIs ----------------
sessions_n = len(f_sessions)
quotes_n = len(f_quotes)
bookings_n = len(f_bookings)
completed_n = int((f_bookings["status"] == "completed").sum())

session_to_booking = (bookings_n / sessions_n) if sessions_n else 0.0
session_to_complete = (completed_n / sessions_n) if sessions_n else 0.0

revenue = float(f_finance["revenue"].sum()) if len(f_finance) else 0.0
cm = float(f_finance["contribution_margin"].sum()) if len(f_finance) else 0.0
cm_pct = (cm / revenue) if revenue else 0.0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Sessions", f"{sessions_n:,}")
c2.metric("Bookings", f"{bookings_n:,}", f"{session_to_booking*100:.1f}% session→booking")
c3.metric("Completed", f"{completed_n:,}", f"{session_to_complete*100:.1f}% session→complete")
c4.metric("Contribution Margin", f"${cm:,.0f}", f"{cm_pct*100:.1f}% CM")

st.divider()

# ---------------- Key Insights ----------------
def safe_pct(x):
    return f"{x*100:.1f}%" if pd.notna(x) else "—"

insight_left, insight_right = st.columns([1.1, 1])

with insight_left:
    st.subheader("Key Insights (auto)")

    # best channel by session→complete (within date range; ignoring channel filter so you can compare)
    comp = bookings.merge(sessions[["session_id", "channel", "service_type", "session_date"]], on="session_id", how="left")
    comp = comp[(comp["session_date"].dt.date >= start_d) & (comp["session_date"].dt.date <= end_d)]
    if svc != "All":
        comp = comp[comp["service_type"] == svc]

    by_ch = comp.groupby("channel").apply(lambda g: (g["status"] == "completed").sum() / g["session_id"].nunique()).reset_index(name="session_to_complete")
    best_ch = by_ch.sort_values("session_to_complete", ascending=False).head(1)
    worst_ch = by_ch.sort_values("session_to_complete", ascending=True).head(1)

    # best service by CM%
    bs = f_bookings.merge(f_finance, on="booking_id", how="left")
    by_svc = bs.groupby("service_type").agg(revenue=("revenue", "sum"), cm=("contribution_margin", "sum"), bookings=("booking_id", "count")).reset_index()
    by_svc["cm_pct"] = by_svc["cm"] / by_svc["revenue"].replace({0: pd.NA})

    best_svc = by_svc.sort_values("cm_pct", ascending=False).head(1)

    # cancel rate
    cancel_rate = (f_bookings["status"].eq("cancelled").mean()) if len(f_bookings) else 0.0

    st.write(
        f"- **Best channel (session→complete):** {best_ch.iloc[0]['channel']} ({safe_pct(best_ch.iloc[0]['session_to_complete'])})"
        if len(best_ch) else "- **Best channel:** —"
    )
    st.write(
        f"- **Lowest channel (session→complete):** {worst_ch.iloc[0]['channel']} ({safe_pct(worst_ch.iloc[0]['session_to_complete'])})"
        if len(worst_ch) else "- **Lowest channel:** —"
    )
    st.write(
        f"- **Best margin service (CM%):** {best_svc.iloc[0]['service_type']} ({safe_pct(best_svc.iloc[0]['cm_pct'])})"
        if len(best_svc) else "- **Best margin service:** —"
    )
    st.write(f"- **Cancellation rate (filtered):** {cancel_rate*100:.1f}%")

with insight_right:
    st.subheader("Funnel Overview")
    funnel_df = pd.DataFrame([{
        "sessions": sessions_n,
        "quotes": quotes_n,
        "bookings": bookings_n,
        "completed": completed_n,
        "session_to_booking": round(session_to_booking, 4),
        "session_to_complete": round(session_to_complete, 4),
    }])
    st.dataframe(funnel_df, use_container_width=True)

st.divider()

# ---------------- Charts ----------------
left, right = st.columns(2)

with left:
    st.subheader("Margin by Service")
    if len(f_bookings) and len(f_finance):
        df_ms = f_bookings.merge(f_finance, on="booking_id", how="left").groupby("service_type").agg(
            revenue=("revenue", "sum"),
            contribution_margin=("contribution_margin", "sum"),
            bookings=("booking_id", "count"),
        ).reset_index()
        fig = px.bar(df_ms, x="service_type", y="contribution_margin", hover_data=["revenue", "bookings"])
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_ms, use_container_width=True)
    else:
        st.info("No data for current filter selection.")

with right:
    st.subheader("Conversion by Channel (sessions → completed)")
    comp2 = bookings.merge(sessions[["session_id", "channel", "service_type", "session_date"]], on="session_id", how="left")
    comp2 = comp2[(comp2["session_date"].dt.date >= start_d) & (comp2["session_date"].dt.date <= end_d)]
    if svc != "All":
        comp2 = comp2[comp2["service_type"] == svc]

    ch_df = comp2.groupby("channel").apply(lambda g: (g["status"] == "completed").sum() / g["session_id"].nunique()).reset_index(name="session_to_complete")
    fig2 = px.bar(ch_df, x="channel", y="session_to_complete")
    st.plotly_chart(fig2, use_container_width=True)
    st.dataframe(ch_df.sort_values("session_to_complete", ascending=False), use_container_width=True)
