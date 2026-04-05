from __future__ import annotations

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "stocks.db"


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS stock_prices (
                symbol TEXT NOT NULL,
                company_name TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume INTEGER NOT NULL,
                daily_return REAL NOT NULL,
                ma_7 REAL NOT NULL,
                high_52w REAL NOT NULL,
                low_52w REAL NOT NULL,
                volatility_7d REAL NOT NULL,
                PRIMARY KEY (symbol, date)
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol_date
            ON stock_prices(symbol, date DESC)
            """
        )
