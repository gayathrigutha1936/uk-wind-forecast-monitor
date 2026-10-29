# UK Wind Forecast Monitor

A full-stack dashboard for monitoring UK wind power forecast accuracy using public data from Elexon.

## Features

- Select a decision date in January 2026.
- Adjust the forecast decision cutoff hour.
- Compare wind generation forecasts with actual generation.
- Visualize forecast and actual generation.
- Review forecast errors for matched settlement periods.
- Calculate Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and forecast bias.

## Technology Stack

- Frontend: React, Vite, Recharts
- Backend: Python, FastAPI
- Data processing: Pandas, NumPy
- HTTP requests: HTTPX
- Testing: Pytest
- Containerization: Docker and Docker Compose

## Data Sources

This project uses public data from Elexon:

- Actual generation: [FUELHH dataset documentation](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/FUELHH/stream)
- Wind forecast history: [Historical wind forecast endpoint](https://data.elexon.co.uk/bmrs/api/v1/forecast/generation/wind/history)
- Forecast dataset: [WINDFOR dataset documentation](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/WINDFOR/stream)

## Decision-Time Assumption

The default decision cutoff is 10:00 UK local time on the decision date. For a selected decision date, the application evaluates the following delivery date.

For each delivery period, the analysis selects the latest eligible forecast published at or before the selected cutoff. The analysis uses UK local dates and accounts for the UK time zone.

## Evaluation Metrics

- **Error:** Forecast generation minus actual generation.
- **MAE:** Average absolute forecast error.
- **RMSE:** Square root of the average squared forecast error.
- **Bias:** Average signed forecast error. Positive bias indicates overforecasting; negative bias indicates underforecasting.

Metrics are calculated only for periods with both actual and eligible forecast values. Forecast and actual data may have different time resolutions, so unmatched periods are excluded.

## Run Locally

### Backend

Open a terminal in the project root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend API runs at `http://localhost:8000`.

API health check: `http://localhost:8000/api/health`

API documentation: `http://localhost:8000/docs`

### Frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the frontend URL printed by Vite, normally `http://localhost:5173`.

## Run with Docker

From the project root, run:

```powershell
docker compose up --build
```

The frontend is available at `http://localhost:5173` and the backend at `http://localhost:8000`.

To stop the containers, press `Ctrl+C` and then run:

```powershell
docker compose down
```

## Tests

From the project root, activate the backend virtual environment and run:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest
```

## Limitations

- The analysis is limited to January 2026 decision dates.
- Forecast accuracy does not by itself determine the amount of electricity that must be purchased; demand, existing positions, market prices, and other operational data are not included.
- Results depend on the completeness and availability of the public Elexon data.
- Only periods with matching actual and forecast timestamps are used in the metrics.

## AI Use Disclosure

AI assistance was used during development to help with implementation guidance, debugging, documentation, and project explanations. The code and outputs should be reviewed and tested by the project author before submission.
