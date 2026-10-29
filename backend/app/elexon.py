from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import httpx

API_BASE = "https://data.elexon.co.uk/bmrs/api/v1"
UK_TZ = ZoneInfo("Europe/London")


def utc_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


async def get_json(url: str, params: dict) -> dict:
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        payload = response.json()

    if isinstance(payload, list):
        return {"data": payload}

    if isinstance(payload, dict):
        return payload

    raise ValueError("Unexpected response format from Elexon")


def day_range_utc(day: date) -> tuple[datetime, datetime]:
    start = datetime.combine(day, time.min, tzinfo=UK_TZ)
    end = datetime.combine(
        day + timedelta(days=1),
        time.min,
        tzinfo=UK_TZ,
    )

    return (
        start.astimezone(timezone.utc),
        end.astimezone(timezone.utc),
    )


async def fetch_actuals(delivery_date: date) -> list[dict]:
    url = f"{API_BASE}/datasets/FUELHH"

    payload = await get_json(
        url,
        {
            "settlementDateFrom": delivery_date.isoformat(),
            "settlementDateTo": delivery_date.isoformat(),
        },
    )

    records = payload.get("data", [])

    return [
        row for row in records
        if str(row.get("fuelType", "")).upper() == "WIND"
        and row.get("settlementDate") == delivery_date.isoformat()
    ]


async def fetch_forecasts(
    decision_date: date,
    delivery_date: date,
    cutoff_hour: int = 10,
) -> list[dict]:
    if not 0 <= cutoff_hour <= 23:
        raise ValueError("cutoff_hour must be between 0 and 23")

    cutoff_local = datetime.combine(
        decision_date,
        time(hour=cutoff_hour),
        tzinfo=UK_TZ,
    )

    url = f"{API_BASE}/forecast/generation/wind/history"

    payload = await get_json(
        url,
        {"publishTime": utc_iso(cutoff_local)},
    )

    records = payload.get("data", [])

    return [
        row for row in records
        if row.get("startTime", "").startswith(delivery_date.isoformat())
    ]
