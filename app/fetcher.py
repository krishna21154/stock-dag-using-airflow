from __future__ import annotations

from datetime import datetime
from typing import List, Dict, Any

import pandas as pd
import yfinance as yf


def _to_utc_naive(ts: pd.Timestamp) -> datetime:
    if ts.tzinfo is not None:
        return ts.tz_convert("UTC").tz_localize(None).to_pydatetime()
    return ts.to_pydatetime()


def fetch_prices(tickers: List[str], start: datetime, end: datetime, interval: str = "1h") -> List[Dict[str, Any]]:
    if not tickers:
        return []
    data = yf.download(
        tickers=tickers,
        start=start,
        end=end,
        interval=interval,
        auto_adjust=False,
        group_by="ticker",
        threads=True,
        progress=False,
    )

    rows: List[Dict[str, Any]] = []

    # yfinance returns multi-index columns when multiple tickers
    if isinstance(data.columns, pd.MultiIndex):
        for ticker in tickers:
            if ticker not in data.columns.levels[0]:
                continue
            df = data[ticker].dropna(how="any")
            for ts, r in df.iterrows():
                rows.append(
                    {
                        "ticker": ticker,
                        "price_ts": _to_utc_naive(pd.Timestamp(ts)),
                        "open": float(r.get("Open")) if pd.notna(r.get("Open")) else None,
                        "high": float(r.get("High")) if pd.notna(r.get("High")) else None,
                        "low": float(r.get("Low")) if pd.notna(r.get("Low")) else None,
                        "close": float(r.get("Close")) if pd.notna(r.get("Close")) else None,
                        "volume": int(r.get("Volume")) if pd.notna(r.get("Volume")) else None,
                    }
                )
    else:
        # Single ticker
        df = data.dropna(how="any")
        ticker = tickers[0]
        for ts, r in df.iterrows():
            rows.append(
                {
                    "ticker": ticker,
                    "price_ts": _to_utc_naive(pd.Timestamp(ts)),
                    "open": float(r.get("Open")) if pd.notna(r.get("Open")) else None,
                    "high": float(r.get("High")) if pd.notna(r.get("High")) else None,
                    "low": float(r.get("Low")) if pd.notna(r.get("Low")) else None,
                    "close": float(r.get("Close")) if pd.notna(r.get("Close")) else None,
                    "volume": int(r.get("Volume")) if pd.notna(r.get("Volume")) else None,
                }
            )

    return rows


