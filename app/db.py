import os
import logging
from typing import List, Dict, Any

import psycopg2
import psycopg2.extras


def _get_connection_dsn() -> str:
    # Prefer full connection URL if provided
    conn_url = os.getenv("AIRFLOW_CONN_STOCK_POSTGRES")
    if conn_url:
        # Normalize Airflow/SQLAlchemy style to libpq/psycopg2 friendly URI
        if conn_url.startswith("postgresql+psycopg2://"):
            conn_url = conn_url.replace("postgresql+psycopg2://", "postgresql://", 1)
        if conn_url.startswith("postgres+psycopg2://"):
            conn_url = conn_url.replace("postgres+psycopg2://", "postgres://", 1)
        return conn_url
    # Fallback to discrete env vars
    user = os.getenv("POSTGRES_USER", "airflow")
    password = os.getenv("POSTGRES_PASSWORD", "airflow")
    host = os.getenv("POSTGRES_HOST", "postgres")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB_STOCKS", "stocks")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


def get_connection():
    dsn = _get_connection_dsn()
    return psycopg2.connect(dsn)


def ensure_schema() -> None:
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS public.stock_prices (
        ticker TEXT NOT NULL,
        price_ts TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        open NUMERIC,
        high NUMERIC,
        low NUMERIC,
        close NUMERIC,
        volume BIGINT,
        PRIMARY KEY (ticker, price_ts)
    );
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(create_table_sql)
        conn.commit()


def upsert_stock_prices(rows: List[Dict[str, Any]]) -> int:
    if not rows:
        return 0
    # Normalize rows and drop invalids
    normalized = []
    for r in rows:
        try:
            normalized.append(
                (
                    r["ticker"],
                    r["price_ts"],
                    r.get("open"),
                    r.get("high"),
                    r.get("low"),
                    r.get("close"),
                    r.get("volume"),
                )
            )
        except Exception:
            logging.warning("Skipping invalid row: %s", r)

    if not normalized:
        return 0

    insert_sql = """
        INSERT INTO public.stock_prices (
            ticker, price_ts, open, high, low, close, volume
        ) VALUES %s
        ON CONFLICT (ticker, price_ts) DO UPDATE SET
            open = EXCLUDED.open,
            high = EXCLUDED.high,
            low = EXCLUDED.low,
            close = EXCLUDED.close,
            volume = EXCLUDED.volume
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            psycopg2.extras.execute_values(
                cur,
                insert_sql,
                normalized,
                template="(%s,%s,%s,%s,%s,%s,%s)",
                page_size=1000,
            )
        conn.commit()
    return len(normalized)


