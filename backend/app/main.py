import asyncio
import os
from datetime import date, timedelta

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.analytics import calculate_analysis
from app.elexon import fetch_actuals, fetch_forecasts

app = FastAPI(
    title="UK Wind Forecast Monitor",
    description="Wind forecast accuracy for January 2026",
    version="1.0.0",
)

frontend_origins = [
    "http://localhost:5173",
    "https://uk-wind-forecast-monitor-beige.vercel.app",
]

configured_origin = os.getenv("FRONTEND_ORIGIN")
if configured_origin:
    frontend_origins.append(configured_origin.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(set(frontend_origins)),
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/dates")
async def available_dates():
    first_day = date(2026, 1, 1)
    return {"dates": [(first_day + timedelta(days=i)).isoformat() for i in range(31)]}


@app.get("/api/analysis")
async def get_analysis(
    decision_date: date = Query(alias="date"),
    cutoff_hour: int = Query(default=10, ge=0, le=23),
):
    if decision_date.year != 2026 or decision_date.month != 1:
        raise HTTPException(
            status_code=400,
            detail="Only January 2026 decision dates are supported.",
        )

    delivery_date = decision_date + timedelta(days=1)

    try:
        actuals, forecasts = await asyncio.gather(
            fetch_actuals(delivery_date),
            fetch_forecasts(decision_date, delivery_date, cutoff_hour),
        )

        return calculate_analysis(
            actual_records=actuals,
            forecast_records=forecasts,
            delivery_date=delivery_date,
            cutoff_hour=cutoff_hour,
        )

    except Exception as exc:
        print(f"Analysis failed: {exc}")
        raise HTTPException(
            status_code=502,
            detail="Could not retrieve or process Elexon data.",
        ) from exc
