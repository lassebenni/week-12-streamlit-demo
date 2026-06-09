"""
Week 12 Pipeline Health Dashboard — demo with mock data.

This app shows what the finished engineering dashboard looks like.
No real credentials needed: all data is hardcoded to realistic values.

When you build your own version in the assignment, you replace the
mock_* functions with real API calls to Airflow and Postgres.
"""

import pandas as pd
import streamlit as st
from datetime import date, timedelta
import random

st.set_page_config(page_title="Pipeline Health Dashboard (Demo)", layout="wide")

# ── Demo banner ─────────────────────────────────────────────────────────────
st.info(
    "**Demo mode** — this dashboard uses sample data. "
    "Your version (Chapters 4-5) will connect to the real Airflow REST API "
    "and Azure Postgres. The layout and panels will look exactly like this."
)

# ── Sidebar: DAG selector ────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    dag_id = st.selectbox(
        "DAG",
        options=["ingest_taxi_month", "dbt_run", "dbt_test"],
        index=0,
    )
    st.caption(f"Showing data for: **{dag_id}**")
    st.divider()
    st.markdown("**About this demo**")
    st.markdown(
        "This is a static mock of the pipeline health dashboard you build "
        "in [Week 12, Chapter 5](https://github.com/HackYourFuture/hyf-datatrack). "
        "Switch the DAG selector to see how the panels respond."
    )

st.title("Pipeline Health Dashboard")

# ── Mock data per DAG ────────────────────────────────────────────────────────
DAG_CONFIGS = {
    "ingest_taxi_month": {
        "state": "success",
        "started": "2025-01-15 03:14 UTC",
        "duration_base_min": 4.2,
        "row_count": 57_842,
        "last_updated": "2025-01-15 04:01 UTC",
        "spike_day": 22,
    },
    "dbt_run": {
        "state": "success",
        "started": "2025-01-15 04:05 UTC",
        "duration_base_min": 1.8,
        "row_count": 57_842,
        "last_updated": "2025-01-15 04:12 UTC",
        "spike_day": 15,
    },
    "dbt_test": {
        "state": "failed",
        "started": "2025-01-15 04:14 UTC",
        "duration_base_min": 0.6,
        "row_count": 57_842,
        "last_updated": "2025-01-15 04:12 UTC",
        "spike_day": None,
    },
}

cfg = DAG_CONFIGS[dag_id]


def mock_last_run(cfg):
    return {"state": cfg["state"], "started": cfg["started"]}


def mock_run_durations(cfg, n=30):
    random.seed(42)
    base = cfg["duration_base_min"]
    today = date.today()
    rows = []
    for i in range(n):
        d = today - timedelta(days=n - i - 1)
        duration = base + random.uniform(-0.4, 0.4)
        if cfg["spike_day"] and i == cfg["spike_day"]:
            duration = base * 9.5  # one realistic spike
        rows.append({"date": d, "duration_min": round(duration, 1)})
    return pd.DataFrame(rows)


def mock_mart_stats(cfg):
    return {"row_count": cfg["row_count"], "last_updated": cfg["last_updated"]}


# ── Panel 1: Last run status ─────────────────────────────────────────────────
st.subheader("Last run status")

run = mock_last_run(cfg)
state = run["state"]

col1, col2, col3 = st.columns(3)
col1.metric("State", state)
col2.metric("Started", run["started"])
col3.metric("DAG", dag_id)

if state == "success":
    st.success("Last run completed successfully.")
elif state == "failed":
    st.error("Last run failed. Check Airflow logs for details.")
else:
    st.warning(f"Run is currently: {state}")

st.divider()

# ── Panel 2: Run duration trend ───────────────────────────────────────────────
st.subheader("Run duration (last 30 runs, minutes)")

duration_df = mock_run_durations(cfg)
st.line_chart(duration_df.set_index("date")["duration_min"])

if cfg["spike_day"]:
    st.caption(
        f"The spike around day {cfg['spike_day']} is a common pattern: "
        "a data volume increase or a slow upstream query. "
        "Duration spikes are often the first signal of a problem before a failure occurs."
    )

st.divider()

# ── Panel 3: Data freshness ───────────────────────────────────────────────────
st.subheader("Data freshness — fct_trips")

stats = mock_mart_stats(cfg)

col1, col2 = st.columns(2)
col1.metric("fct_trips row count", f"{stats['row_count']:,}")
col2.metric("Last updated", stats["last_updated"])

st.caption(
    "Row count and last-updated timestamp are read from Azure Postgres "
    "(`MAX(updated_at)` or `MAX(pickup_datetime)` on `fct_trips`). "
    "In the real app, these are cached with `@st.cache_data(ttl=3600)` "
    "since the table updates at most once per day."
)
