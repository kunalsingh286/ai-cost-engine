import sys
from pathlib import Path

# Add project root to Python path
ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


import streamlit as st
import matplotlib.pyplot as plt

from accounting.database import SessionLocal
from dashboard.queries import AnalyticsService
from forecasting.service import ForecastService


st.set_page_config(
    page_title="AI Cost Engine Dashboard",
    layout="wide"
)


def get_db():
    return SessionLocal()


st.title("AI Cost & Capacity Optimization Dashboard")


db = get_db()

analytics = AnalyticsService(db)

forecast = ForecastService(db)


# ----------------- KPIs -----------------

st.header("Key Metrics")

cost_df = analytics.cost_over_time()
token_df = analytics.tokens_over_time()

total_cost = cost_df["cost"].sum() if not cost_df.empty else 0
total_tokens = token_df["tokens"].sum() if not token_df.empty else 0

col1, col2, col3 = st.columns(3)

col1.metric("Total Cost ($)", round(total_cost, 4))
col2.metric("Total Tokens", int(total_tokens))
col3.metric("Requests", len(token_df))


# ----------------- Cost Over Time -----------------

st.header("Cost Over Time")

if not cost_df.empty:

    fig, ax = plt.subplots()

    ax.plot(cost_df["date"], cost_df["cost"])

    ax.set_xlabel("Date")
    ax.set_ylabel("Cost ($)")

    st.pyplot(fig)

else:
    st.info("No cost data available")


# ----------------- Token Usage -----------------

st.header("Token Usage")

if not token_df.empty:

    fig, ax = plt.subplots()

    ax.plot(token_df["date"], token_df["tokens"])

    ax.set_xlabel("Date")
    ax.set_ylabel("Tokens")

    st.pyplot(fig)

else:
    st.info("No token data available")


# ----------------- Cost by Model -----------------

st.header("Cost by Model")

model_df = analytics.cost_by_model()

if not model_df.empty:

    fig, ax = plt.subplots()

    ax.bar(model_df["model"], model_df["cost"])

    ax.set_xlabel("Model")
    ax.set_ylabel("Cost ($)")

    st.pyplot(fig)

else:
    st.info("No model data available")


# ----------------- Top Users -----------------

st.header("Top Users")

user_df = analytics.top_users()

st.table(user_df)


# ----------------- Forecast -----------------

st.header("Usage Forecast")

days = st.slider("Forecast Days", 3, 30, 7)

forecast_result = forecast.generate(days)

if forecast_result["status"] == "ok":

    st.subheader(f"Granularity: {forecast_result['granularity']}")

    st.write("Capacity Estimate:")

    st.json(forecast_result["capacity"])

    st.subheader("Token Forecast")

    st.line_chart(
        forecast_result["token_forecast"]
    )

    st.subheader("Cost Forecast")

    st.line_chart(
        forecast_result["cost_forecast"]
    )

else:
    st.warning("Not enough data for forecast")


db.close()
