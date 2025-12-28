import os
import numpy as np
import pandas as pd
from faker import Faker

fake = Faker()
rng = np.random.default_rng(42)

OUT_DIR = "data"
os.makedirs(OUT_DIR, exist_ok=True)

N_USERS = 1200
MAX_SESSIONS_PER_USER = 8

SERVICE_TYPES = ["virtual_visit", "in_person_visit", "labs", "imaging", "rx"]
CHANNELS = ["organic", "paid_search", "referral", "partner", "email"]

def sigmoid(x: float) -> float:
    return 1 / (1 + np.exp(-x))

# ---------- Users ----------
users = []
for i in range(N_USERS):
    user_id = f"u{i:05d}"
    users.append({
        "user_id": user_id,
        "signup_date": fake.date_between(start_date="-180d", end_date="today").isoformat(),
        "state": fake.state_abbr(),
        "age": int(np.clip(rng.normal(38, 12), 18, 80)),
        "channel_first_touch": rng.choice(CHANNELS, p=[0.35, 0.25, 0.15, 0.10, 0.15]),
    })
df_users = pd.DataFrame(users)

# ---------- Sessions ----------
sessions = []
session_id_ctr = 0
for _, u in df_users.iterrows():
    n_sess = int(rng.integers(1, MAX_SESSIONS_PER_USER + 1))
    for _ in range(n_sess):
        session_id = f"s{session_id_ctr:07d}"
        session_id_ctr += 1
        svc = rng.choice(SERVICE_TYPES, p=[0.38, 0.20, 0.16, 0.10, 0.16])
        device = rng.choice(["mobile", "desktop"], p=[0.65, 0.35])
        sessions.append({
            "session_id": session_id,
            "user_id": u["user_id"],
            "session_date": fake.date_between(start_date="-180d", end_date="today").isoformat(),
            "service_type": svc,
            "device": device,
            "channel": rng.choice(CHANNELS, p=[0.32, 0.28, 0.16, 0.10, 0.14]),
        })
df_sessions = pd.DataFrame(sessions)

# ---------- Quotes (cash + insurance) ----------
quotes = []
for _, s in df_sessions.iterrows():
    # baseline cash price by service
    base_cash = {
        "virtual_visit": 59,
        "in_person_visit": 139,
        "labs": 79,
        "imaging": 249,
        "rx": 25
    }[s["service_type"]]

    # add noise and some price variance
    cash_price = float(np.clip(rng.normal(base_cash, base_cash * 0.15), 10, 800))

    # insurance price often lower, but not always (simulate odd plans)
    ins_multiplier = float(np.clip(rng.normal(0.75, 0.18), 0.35, 1.10))
    insurance_price = float(np.clip(cash_price * ins_multiplier, 5, 800))

    # probability user sees insurance price
    has_insurance = rng.choice([0, 1], p=[0.22, 0.78])
    showed_insurance = int(has_insurance and (rng.random() < 0.85))

    quotes.append({
        "quote_id": f"q{s['session_id']}",
        "session_id": s["session_id"],
        "cash_price": round(cash_price, 2),
        "insurance_price": round(insurance_price, 2) if showed_insurance else None,
        "has_insurance": int(has_insurance),
        "showed_insurance_price": showed_insurance
    })
df_quotes = pd.DataFrame(quotes)

# ---------- Bookings + fulfillment ----------
bookings = []
fulfillment = []
booking_ctr = 0

for _, s in df_sessions.iterrows():
    q = df_quotes.loc[df_quotes["session_id"] == s["session_id"]].iloc[0]

    # Features affecting conversion
    price = q["insurance_price"] if (q["showed_insurance_price"] and pd.notna(q["insurance_price"])) else q["cash_price"]
    log_price = np.log(float(price))

    is_mobile = 1 if s["device"] == "mobile" else 0
    is_paid = 1 if s["channel"] == "paid_search" else 0
    svc = s["service_type"]

    # booking probability (synthetic but directional)
    # lower price -> higher conversion; mobile -> slight boost; paid -> slightly lower quality
    svc_bias = {"virtual_visit": 0.9, "in_person_visit": 0.3, "labs": 0.4, "imaging": -0.1, "rx": 0.6}[svc]
    p_book = sigmoid(2.2 - 0.55 * log_price + 0.15 * is_mobile - 0.10 * is_paid + svc_bias)

    booked = rng.random() < p_book
    if not booked:
        continue

    booking_id = f"b{booking_ctr:07d}"
    booking_ctr += 1

    visit_mode = "virtual" if svc == "virtual_visit" else ("in_person" if svc in ["in_person_visit", "imaging", "labs"] else "delivery")
    wait_days = int(np.clip(rng.normal(2.5 if visit_mode != "virtual" else 0.5, 2.0), 0, 21))

    # completion probability: longer waits -> more cancels; service specific
    p_complete = sigmoid(2.5 - 0.18 * wait_days + (0.4 if visit_mode == "virtual" else 0.0))
    completed = rng.random() < p_complete

    bookings.append({
        "booking_id": booking_id,
        "session_id": s["session_id"],
        "user_id": s["user_id"],
        "service_type": svc,
        "visit_mode": visit_mode,
        "booking_date": fake.date_between(start_date="-180d", end_date="today").isoformat(),
        "price_paid": float(price),
        "used_insurance_price": int(q["showed_insurance_price"] and pd.notna(q["insurance_price"])),
        "wait_time_days": wait_days,
        "status": "completed" if completed else "cancelled"
    })

    if completed:
        completed_date = pd.to_datetime(bookings[-1]["booking_date"]) + pd.to_timedelta(wait_days, unit="D")
        fulfillment.append({
            "booking_id": booking_id,
            "completed_date": completed_date.date().isoformat(),
            "nps": int(np.clip(rng.normal(8.0, 1.8), 0, 10)),
        })

df_bookings = pd.DataFrame(bookings)
df_fulfillment = pd.DataFrame(fulfillment)

# ---------- Simple finance table ----------
# approximate COGS by service (synthetic)
COGS_RATE = {
    "virtual_visit": 0.35,
    "in_person_visit": 0.45,
    "labs": 0.50,
    "imaging": 0.55,
    "rx": 0.60
}

finance_rows = []
for _, b in df_bookings.iterrows():
    rev = float(b["price_paid"]) if b["status"] == "completed" else 0.0
    cogs = rev * COGS_RATE[b["service_type"]]
    finance_rows.append({
        "booking_id": b["booking_id"],
        "revenue": round(rev, 2),
        "cogs": round(cogs, 2),
        "contribution_margin": round(rev - cogs, 2),
    })
df_finance = pd.DataFrame(finance_rows)

# ---------- Save CSVs ----------
df_users.to_csv(os.path.join(OUT_DIR, "users.csv"), index=False)
df_sessions.to_csv(os.path.join(OUT_DIR, "sessions.csv"), index=False)
df_quotes.to_csv(os.path.join(OUT_DIR, "quotes.csv"), index=False)
df_bookings.to_csv(os.path.join(OUT_DIR, "bookings.csv"), index=False)
df_fulfillment.to_csv(os.path.join(OUT_DIR, "fulfillment.csv"), index=False)
df_finance.to_csv(os.path.join(OUT_DIR, "finance.csv"), index=False)

print("Wrote:", [f for f in os.listdir(OUT_DIR) if f.endswith(".csv")])
print("Rows:",
      "users", len(df_users),
      "sessions", len(df_sessions),
      "quotes", len(df_quotes),
      "bookings", len(df_bookings),
      "fulfillment", len(df_fulfillment),
      "finance", len(df_finance))
