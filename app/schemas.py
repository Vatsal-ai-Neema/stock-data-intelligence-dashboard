from __future__ import annotations

from pydantic import BaseModel, Field


class CompanyResponse(BaseModel):
    symbol: str
    company_name: str


class StockDataPoint(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    daily_return: float
    ma_7: float
    high_52w: float
    low_52w: float
    volatility_7d: float


class SummaryResponse(BaseModel):
    symbol: str
    company_name: str
    latest_close: float
    average_close: float
    high_52w: float
    low_52w: float
    latest_daily_return: float
    latest_volatility_7d: float
    available_days: int = Field(description="Number of daily records available for the company.")


class CompareSeries(BaseModel):
    symbol: str
    company_name: str
    points: list[StockDataPoint]


class CompareResponse(BaseModel):
    days: int
    series: list[CompareSeries]
