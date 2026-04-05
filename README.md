# Stock Data Intelligence Dashboard

This project is a mini financial data platform built for the JarNox Software Intern assignment. It demonstrates end-to-end handling of stock market data: collection, cleaning, analytics, REST API development, and frontend visualization.

## Assignment Coverage

### Part 1: Data Collection and Preparation

Implemented in:
- [seed.py](D:\mini financial data platform\app\services\seed.py)
- [fetch_real_data.py](D:\mini financial data platform\scripts\fetch_real_data.py)

What is covered:
- stock data collection using:
  - deterministic seeded mock stock data for out-of-the-box execution
  - optional public API fetching using `yfinance`
- cleaning and organization with Pandas
- date normalization using `pd.to_datetime(...)`
- missing-value handling in the real-data pipeline using `dropna()`
- calculated metrics:
  - daily return
  - 7-day moving average
  - 52-week high
  - 52-week low
- custom metric:
  - 7-day volatility score

### Part 2: Backend API Development

Implemented in:
- [main.py](D:\mini financial data platform\app\main.py)
- [repository.py](D:\mini financial data platform\app\services\repository.py)
- [schemas.py](D:\mini financial data platform\app\schemas.py)

Endpoints:
- `GET /companies`
- `GET /data/{symbol}`
- `GET /summary/{symbol}`
- `GET /compare?symbol1=...&symbol2=...&days=...`

Swagger documentation is available automatically through FastAPI at:
- `http://127.0.0.1:8000/docs`

### Part 3: Visualization Dashboard

Implemented in:
- [index.html](D:\mini financial data platform\templates\index.html)
- [styles.css](D:\mini financial data platform\static\styles.css)
- [app.js](D:\mini financial data platform\static\app.js)

Dashboard features:
- company list panel
- closing-price chart
- last 30 / 90 / 180 day filters
- compare two stocks on one chart
- summary cards
- chart zoom:
  - mouse wheel
  - touchpad pinch
  - `+` / `-` / `Reset` buttons

### Part 4: Optional Add-On

Included:
- Dockerized backend setup
- async FastAPI route handlers

Not included:
- deployed cloud link
- ML prediction model
- caching layer

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

## Data Strategy

The application seeds the database automatically on first run with realistic stock-like sample data. This ensures the project works even without internet or third-party API access.

If real stock data is preferred, the project also includes a script that fetches approximately one year of daily data using `yfinance`.

Seeded symbols:
- `RELIANCE.NS`
- `TCS.NS`
- `INFY.NS`
- `HDFCBANK.NS`
- `ICICIBANK.NS`
- `LT.NS`

## Calculated Metrics

- `daily_return = (close - open) / open`
- `ma_7 = 7-day moving average of close`
- `high_52w = rolling 52-week high`
- `low_52w = rolling 52-week low`
- `volatility_7d = rolling 7-day standard deviation of daily_return`

## Local Setup

1. Create a virtual environment

```powershell
python -m venv .venv
```

2. Activate it

```powershell
.venv\Scripts\Activate.ps1
```

3. Install dependencies

```powershell
pip install -r requirements.txt
```

4. Start the backend

```powershell
uvicorn app.main:app --reload
```

5. Open in browser

- Dashboard: `http://127.0.0.1:8000/`
- Swagger docs: `http://127.0.0.1:8000/docs`

## Docker Setup

Build the image:

```powershell
docker build -t stock-dashboard .
```

Run the container:

```powershell
docker run -p 8000:8000 stock-dashboard
```

Then open:

- Dashboard: `http://127.0.0.1:8000/`
- Swagger docs: `http://127.0.0.1:8000/docs`

## API Testing URLs

- `http://127.0.0.1:8000/companies`
- `http://127.0.0.1:8000/data/INFY.NS`
- `http://127.0.0.1:8000/summary/INFY.NS`
- `http://127.0.0.1:8000/compare?symbol1=INFY.NS&symbol2=TCS.NS&days=30`

## Optional Real Data Fetch

Run:

```powershell
python scripts/fetch_real_data.py
```

This replaces the seeded data with actual downloaded stock history for the curated symbol list.

## Notes for Evaluation

- The project is intentionally structured to be easy to review: data preparation, database logic, API routes, and frontend code are separated.
- Seeded data guarantees a working demo even if public APIs are unavailable.
- The custom creativity metric is the 7-day volatility score, visible in both the API responses and dashboard.
