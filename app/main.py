from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import initialize_database
from app.schemas import CompareResponse, CompanyResponse, SummaryResponse
from app.services.repository import VALID_DAYS, get_company_data, get_company_summary, get_comparison, list_companies
from app.services.seed import ensure_seed_data

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    ensure_seed_data()
    yield


app = FastAPI(
    title="Stock Data Intelligence Dashboard",
    description="A mini financial data platform built for the JarNox internship assignment.",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/companies", response_model=list[CompanyResponse])
async def companies() -> list[CompanyResponse]:
    return [CompanyResponse(**company) for company in list_companies()]


@app.get("/data/{symbol}")
async def stock_data(
    symbol: str,
    days: int = Query(30, description="Number of days of historical data to fetch. Frontend uses 30, 90, or 180."),
):
    try:
        records = get_company_data(symbol, days=days)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not records:
        raise HTTPException(status_code=404, detail=f"No stock data found for {symbol}.")
    return {"symbol": symbol.upper(), "days": days, "points": records}


@app.get("/summary/{symbol}", response_model=SummaryResponse)
async def summary(symbol: str) -> SummaryResponse:
    result = get_company_summary(symbol)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No summary found for {symbol}.")
    return SummaryResponse(**result)


@app.get("/compare", response_model=CompareResponse)
async def compare(
    symbol1: str = Query(..., description="Primary stock symbol."),
    symbol2: str = Query(..., description="Secondary stock symbol."),
    days: int = Query(30, description="Number of days to compare. Recommended values: 30, 90, 180."),
) -> CompareResponse:
    if days not in VALID_DAYS:
        raise HTTPException(status_code=400, detail=f"days must be one of {sorted(VALID_DAYS)}")
    if symbol1.upper() == symbol2.upper():
        raise HTTPException(status_code=400, detail="Please choose two different symbols for comparison.")
    try:
        series = get_comparison([symbol1, symbol2], days)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return CompareResponse(days=days, series=series)
