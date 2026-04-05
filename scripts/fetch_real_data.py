from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.database import DB_PATH, initialize_database

SYMBOLS = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "LT.NS",
]

COMPANY_NAMES = {
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS": "Tata Consultancy Services",
    "INFY.NS": "Infosys",
    "HDFCBANK.NS": "HDFC Bank",
    "ICICIBANK.NS": "ICICI Bank",
    "LT.NS": "Larsen & Toubro",
}


def prepare_frame(symbol: str, history: pd.DataFrame) -> pd.DataFrame:
    frame = history.reset_index().rename(columns=str.lower)
    frame = frame[["date", "open", "high", "low", "close", "volume"]].copy()
    frame["symbol"] = symbol
    frame["company_name"] = COMPANY_NAMES[symbol]
    frame["date"] = pd.to_datetime(frame["date"])
    frame = frame.sort_values("date").dropna()
    frame["daily_return"] = ((frame["close"] - frame["open"]) / frame["open"]).fillna(0)
    frame["ma_7"] = frame["close"].rolling(window=7, min_periods=1).mean()
    frame["high_52w"] = frame["high"].rolling(window=252, min_periods=1).max()
    frame["low_52w"] = frame["low"].rolling(window=252, min_periods=1).min()
    frame["volatility_7d"] = frame["daily_return"].rolling(window=7, min_periods=1).std().fillna(0)
    frame["date"] = frame["date"].dt.strftime("%Y-%m-%d")

    ordered_columns = [
        "symbol",
        "company_name",
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "daily_return",
        "ma_7",
        "high_52w",
        "low_52w",
        "volatility_7d",
    ]
    return frame[ordered_columns].round(4)


def main() -> None:
    initialize_database()
    print("Starting real data download...")
    print("Importing yfinance...")
    try:
        import yfinance as yf
    except KeyboardInterrupt as exc:
        raise SystemExit(
            "The script was interrupted while importing yfinance. Try running it again and let the import finish."
        ) from exc

    rows = []
    for symbol in SYMBOLS:
        print(f"Fetching {symbol}...")
        history = yf.Ticker(symbol).history(period="1y", interval="1d", auto_adjust=False)
        if history.empty:
            print(f"No data returned for {symbol}, skipping.")
            continue
        rows.append(prepare_frame(symbol, history))

    if not rows:
        raise RuntimeError("No data downloaded from yfinance.")

    dataset = pd.concat(rows, ignore_index=True)
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("DELETE FROM stock_prices")
        dataset.to_sql("stock_prices", connection, if_exists="append", index=False)

    print(f"Loaded {len(dataset)} rows into {DB_PATH}")


if __name__ == "__main__":
    main()
