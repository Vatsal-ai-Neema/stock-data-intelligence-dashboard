# Build Stock Data Intelligence Dashboard

I built this project as part of the JarNox Software Intern assignment. It is a mini financial data platform that demonstrates stock data collection, cleaning, REST API development, and interactive visualization.

## Project Overview

In this project, I focused on building an end-to-end workflow:

- collecting stock data
- cleaning and transforming it with Pandas
- storing it in SQLite
- exposing it through FastAPI APIs
- visualizing it in a dashboard with filters, comparison, and zoom controls

## Tech Stack

- Python
- FastAPI
- SQLite
- Pandas
- NumPy
- yfinance
- HTML
- CSS
- JavaScript
- Chart.js
- Docker

## Assignment Coverage

### Part 1: Data Collection and Preparation

For data collection, I used `yfinance` to fetch real stock market data for selected NSE-listed companies.

Symbols used:
- `RELIANCE.NS`
- `TCS.NS`
- `INFY.NS`
- `HDFCBANK.NS`
- `ICICIBANK.NS`
- `LT.NS`

The real-data fetch script is available in [fetch_real_data.py](D:\mini financial data platform\scripts\fetch_real_data.py).

I also kept a seeded-data fallback in [seed.py](D:\mini financial data platform\app\services\seed.py) so the project can still run even if an external API is unavailable.

### Data Cleaning and Transformation

I used Pandas to clean and prepare the stock data.

The following transformations are implemented:
- handling missing values using `dropna()`
- converting date columns properly using `pd.to_datetime(...)`
- sorting data by date
- calculating:
  - daily return
  - 7-day moving average
  - 52-week high
  - 52-week low

### Custom Metric / Creativity

As an additional custom insight, I added a volatility score:

- `volatility_7d = rolling 7-day standard deviation of daily_return`

This metric is visible in:
- the summary API response
- the stock data API response
- the dashboard summary card

### Part 2: Backend API Development

I built the backend using FastAPI.

Implemented endpoints:
- `GET /companies`
- `GET /data/{symbol}`
- `GET /summary/{symbol}`
- `GET /compare?symbol1=...&symbol2=...&days=...`

These endpoints are defined in [main.py](D:\mini financial data platform\app\main.py), and the database query logic is handled in [repository.py](D:\mini financial data platform\app\services\repository.py).

Swagger documentation is available automatically through FastAPI at:
- `http://127.0.0.1:8000/docs`

### Part 3: Visualization Dashboard

I built a dashboard that includes:
- a company list panel
- a closing-price line chart
- 30 / 90 / 180 day filters
- stock comparison on a single chart
- summary cards for key metrics
- chart zoom controls

Frontend files:
- [index.html](D:\mini financial data platform\templates\index.html)
- [styles.css](D:\mini financial data platform\static\styles.css)
- [app.js](D:\mini financial data platform\static\app.js)

### Part 4: Optional Add-On

To strengthen the submission, I also added:
- Docker support
- async FastAPI route handlers

## Project Structure

```text
app/
  main.py
  database.py
  schemas.py
  services/
    repository.py
    seed.py
scripts/
  seed_data.py
  fetch_real_data.py
templates/
  index.html
static/
  styles.css
  app.js
data/
  stocks.db
requirements.txt
Dockerfile
.dockerignore
README.md
```

## File Purpose

- `app/main.py`  
  Main FastAPI application and route definitions.

- `app/database.py`  
  SQLite database connection and table setup.

- `app/schemas.py`  
  Pydantic response models for API validation and Swagger documentation.

- `app/services/repository.py`  
  Database query logic for companies, stock data, summaries, and comparison.

- `app/services/seed.py`  
  Seeded fallback stock data generation with derived metrics.

- `scripts/fetch_real_data.py`  
  Fetches real stock data from `yfinance` and stores it in SQLite.

- `scripts/seed_data.py`  
  Manually loads seeded data into the database.

- `templates/index.html`  
  Dashboard HTML structure.

- `static/styles.css`  
  Dashboard styling and responsive layout.

- `static/app.js`  
  Frontend logic for filters, comparison, chart rendering, and zoom controls.

## Calculated Metrics

- `daily_return = (close - open) / open`
- `ma_7 = 7-day moving average of close`
- `high_52w = rolling 52-week high`
- `low_52w = rolling 52-week low`
- `volatility_7d = rolling 7-day standard deviation of daily_return`

## How to Run the Project

### 1. Install dependencies

```powershell
pip install -r requirements.txt
```

### 2. Fetch real stock data

```powershell
python -m scripts.fetch_real_data
```

This downloads stock data using `yfinance` and stores it in:

- [stocks.db](D:\mini financial data platform\data\stocks.db)

### 3. Start the backend server

```powershell
uvicorn app.main:app --reload
```

### 4. Open in browser

- Dashboard: `http://127.0.0.1:8000/`
- Swagger docs: `http://127.0.0.1:8000/docs`

## API Endpoints for Testing

- `http://127.0.0.1:8000/companies`
- `http://127.0.0.1:8000/data/INFY.NS`
- `http://127.0.0.1:8000/summary/INFY.NS`
- `http://127.0.0.1:8000/compare?symbol1=INFY.NS&symbol2=TCS.NS&days=30`

## Dashboard Features

- company selection from sidebar
- closing-price chart
- 30 / 90 / 180 day filters
- compare two companies on one chart
- mouse wheel / touchpad zoom
- `+`, `-`, and `Reset` zoom buttons
- key metrics display

## Docker Support

Build:

```powershell
docker build -t stock-dashboard .
```

Run:

```powershell
docker run -p 8000:8000 stock-dashboard
```

## Notes

- The project supports both real data and seeded fallback data.
- Real stock data was successfully fetched using `yfinance`.
- The custom creativity metric in this project is the 7-day volatility score.
- FastAPI automatically provides API documentation through Swagger.
