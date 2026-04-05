from __future__ import annotations

import math
from datetime import datetime

import numpy as np
import pandas as pd

from app.database import get_connection

SEED_COMPANIES = {
    "RELIANCE.NS": {"company_name": "Reliance Industries", "base_price": 2850, "trend": 0.42},
    "TCS.NS": {"company_name": "Tata Consultancy Services", "base_price": 3925, "trend": 0.28},
    "INFY.NS": {"company_name": "Infosys", "base_price": 1615, "trend": 0.24},
    "HDFCBANK.NS": {"company_name": "HDFC Bank", "base_price": 1540, "trend": 0.19},
    "ICICIBANK.NS": {"company_name": "ICICI Bank", "base_price": 1180, "trend": 0.21},
    "LT.NS": {"company_name": "Larsen & Toubro", "base_price": 3475, "trend": 0.31},
}


def ensure_seed_data() -> None:
    with get_connection() as connection:
        row = connection.execute("SELECT COUNT(*) AS count FROM stock_prices").fetchone()
        if row["count"] > 0:
            return

    frames = [_build_company_frame(symbol, details) for symbol, details in SEED_COMPANIES.items()]
    dataset = pd.concat(frames, ignore_index=True)

    with get_connection() as connection:
        dataset.to_sql("stock_prices", connection, if_exists="append", index=False)


def _build_company_frame(symbol: str, details: dict) -> pd.DataFrame:
    rng = np.random.default_rng(abs(hash(symbol)) % (2**32))
    business_days = pd.bdate_range(end=datetime(2026, 4, 4), periods=220)
    baseline = details["base_price"]
    trend = details["trend"]

    rows: list[dict] = []
    previous_close = baseline
    for index, current_date in enumerate(business_days):
        seasonal_wave = math.sin(index / 8.0) * baseline * 0.006
        drift = trend * index
        noise = rng.normal(0, baseline * 0.008)
        open_price = max(previous_close + rng.normal(0, baseline * 0.004), baseline * 0.5)
        close_price = max(baseline + drift + seasonal_wave + noise, baseline * 0.5)
        high_price = max(open_price, close_price) + abs(rng.normal(0, baseline * 0.006))
        low_price = min(open_price, close_price) - abs(rng.normal(0, baseline * 0.006))
        volume = int(rng.integers(900_000, 3_600_000))

        rows.append(
            {
                "symbol": symbol,
                "company_name": details["company_name"],
                "date": current_date.strftime("%Y-%m-%d"),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(max(low_price, 1), 2),
                "close": round(close_price, 2),
                "volume": volume,
            }
        )
        previous_close = close_price

    frame = pd.DataFrame(rows)
    frame["date"] = pd.to_datetime(frame["date"])
    frame = frame.sort_values("date").reset_index(drop=True)
    frame["daily_return"] = ((frame["close"] - frame["open"]) / frame["open"]).fillna(0)
    frame["ma_7"] = frame["close"].rolling(window=7, min_periods=1).mean()
    frame["high_52w"] = frame["high"].rolling(window=220, min_periods=1).max()
    frame["low_52w"] = frame["low"].rolling(window=220, min_periods=1).min()
    frame["volatility_7d"] = frame["daily_return"].rolling(window=7, min_periods=1).std().fillna(0)

    numeric_columns = ["daily_return", "ma_7", "high_52w", "low_52w", "volatility_7d"]
    frame[numeric_columns] = frame[numeric_columns].round(4)
    frame["date"] = frame["date"].dt.strftime("%Y-%m-%d")
    return frame
