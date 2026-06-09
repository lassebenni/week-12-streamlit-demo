# Week 12 Pipeline Health Dashboard — Demo

A mock version of the engineering dashboard students build in [HYF Data Track Week 12, Chapter 5](https://github.com/lassebenni/hyf-datatrack).

All data is hardcoded to realistic values. No credentials or external services required.

## What it shows

- **Last run status**: DAG run state (`success` / `failed` / `running`), start time, and DAG name
- **Run duration trend**: line chart of the last 30 run durations in minutes (with a realistic spike)
- **Data freshness**: row count and last-updated timestamp from the `fct_trips` mart table
- **Sidebar DAG selector**: switch between `ingest_taxi_month`, `dbt_run`, and `dbt_test`

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## The real version

In the assignment, students replace the `mock_*` functions with real calls to:

- The **Airflow REST API** (`GET /api/v1/dags/{dag_id}/dagRuns`) for run history
- **Azure Postgres** (`sqlalchemy` + `fct_trips`) for data freshness

Credentials are stored in a `.env` file and loaded with `python-dotenv`.
