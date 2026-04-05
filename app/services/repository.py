from __future__ import annotations

from typing import Iterable

from app.database import get_connection


VALID_DAYS = {30, 90, 180}


def list_companies() -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT DISTINCT symbol, company_name
            FROM stock_prices
            ORDER BY company_name
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_company_data(symbol: str, days: int = 30) -> list[dict]:
    if days <= 0:
        raise ValueError("days must be positive")

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT symbol, company_name, date, open, high, low, close, volume,
                   daily_return, ma_7, high_52w, low_52w, volatility_7d
            FROM stock_prices
            WHERE symbol = ?
            ORDER BY date DESC
            LIMIT ?
            """,
            (symbol.upper(), days),
        ).fetchall()

    return [dict(row) for row in reversed(rows)]


def get_company_summary(symbol: str) -> dict | None:
    with get_connection() as connection:
        latest_row = connection.execute(
            """
            SELECT symbol, company_name, close, daily_return, volatility_7d
            FROM stock_prices
            WHERE symbol = ?
            ORDER BY date DESC
            LIMIT 1
            """,
            (symbol.upper(),),
        ).fetchone()

        if latest_row is None:
            return None

        stats_row = connection.execute(
            """
            SELECT COUNT(*) AS available_days,
                   AVG(close) AS average_close,
                   MAX(high) AS high_52w,
                   MIN(low) AS low_52w
            FROM stock_prices
            WHERE symbol = ?
            """,
            (symbol.upper(),),
        ).fetchone()

    return {
        "symbol": latest_row["symbol"],
        "company_name": latest_row["company_name"],
        "latest_close": round(latest_row["close"], 2),
        "average_close": round(stats_row["average_close"], 2),
        "high_52w": round(stats_row["high_52w"], 2),
        "low_52w": round(stats_row["low_52w"], 2),
        "latest_daily_return": round(latest_row["daily_return"], 4),
        "latest_volatility_7d": round(latest_row["volatility_7d"], 4),
        "available_days": int(stats_row["available_days"]),
    }


def get_comparison(symbols: Iterable[str], days: int) -> list[dict]:
    normalized_symbols = [symbol.upper() for symbol in symbols]
    return [
        {
            "symbol": symbol,
            "company_name": _get_company_name(symbol),
            "points": get_company_data(symbol, days=days),
        }
        for symbol in normalized_symbols
    ]


def _get_company_name(symbol: str) -> str:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT company_name
            FROM stock_prices
            WHERE symbol = ?
            LIMIT 1
            """,
            (symbol.upper(),),
        ).fetchone()

    if row is None:
        raise ValueError(f"Unknown symbol: {symbol}")
    return str(row["company_name"])
