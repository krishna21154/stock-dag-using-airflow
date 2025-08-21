from __future__ import annotations

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

from airflow import DAG
from airflow.decorators import task
from airflow.utils.dates import days_ago
from airflow.utils.session import provide_session

# Modular utilities
from app.db import ensure_schema, upsert_stock_prices
from app.fetcher import fetch_prices


DEFAULT_TICKERS = [t.strip() for t in os.getenv("STOCK_TICKERS", "AAPL,MSFT").split(",") if t.strip()]
SCHEDULE_INTERVAL = os.getenv("SCHEDULE_INTERVAL", "0 * * * *")  # default hourly


with DAG(
    dag_id="stock_prices_pipeline",
    description="Fetch OHLCV data from yfinance and upsert into Postgres",
    start_date=days_ago(1),
    schedule=SCHEDULE_INTERVAL,
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "airflow",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
) as dag:

    @task
    def init_schema() -> None:
        logging.info("Ensuring database schema is present...")
        ensure_schema()

    @task
    def extract(tickers: List[str], window: Dict[str, str]) -> List[Dict[str, Any]]:
        try:
            start_dt = datetime.fromisoformat(window["start"]) 
            end_dt = datetime.fromisoformat(window["end"]) 
        except Exception:
            end_dt = datetime.utcnow()
            start_dt = end_dt - timedelta(days=2)

        logging.info("Fetching prices for %s from %s to %s", tickers, start_dt, end_dt)
        try:
            rows = fetch_prices(tickers=tickers, start=start_dt, end=end_dt, interval="1d")
            logging.info("Fetched %d rows", len(rows))
            return rows
        except Exception as exc:
            logging.exception("Failed to fetch data: %s", exc)
            raise

    @task
    def load(rows: List[Dict[str, Any]]) -> int:
        if not rows:
            logging.warning("No rows to upsert. Skipping load phase.")
            return 0
        try:
            affected = upsert_stock_prices(rows)
            logging.info("Upserted %d rows", affected)
            return affected
        except Exception as exc:
            logging.exception("Failed to upsert rows: %s", exc)
            raise

    init = init_schema()

    from airflow.operators.empty import EmptyOperator
    start = EmptyOperator(task_id="start")

    @task
    def context_window() -> Dict[str, str]:
        # Use a simple fallback approach for time window
        now = datetime.utcnow()
        start_dt = now - timedelta(days=7)  # Get last 7 days of data
        end_dt = now - timedelta(days=1)    # End yesterday to avoid market closure issues
        return {"start": start_dt.isoformat(), "end": end_dt.isoformat()}

    window = context_window()
    rows = extract(DEFAULT_TICKERS, window)
    done = load(rows)

    start >> init >> rows >> done
