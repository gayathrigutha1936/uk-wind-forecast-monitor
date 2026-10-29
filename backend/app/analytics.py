from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
import math

import pandas as pd

UK_TZ = ZoneInfo("Europe/London")


def parse_datetime(value):
    parsed = pd.Timestamp(value).to_pydatetime()

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)


def to_number(value):
    if value is None:
        return None

    if str(value).strip().upper() in {"", "NULL", "N/A", "NAN"}:
        return None

    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def calculate_analysis(
    actual_records: list[dict],
    forecast_records: list[dict],
    delivery_date: date,
    cutoff_hour: int = 10,
) -> dict:
    """Compare actual generation with the latest forecast available at cutoff."""

    if not 0 <= cutoff_hour <= 23:
        raise ValueError("cutoff_hour must be between 0 and 23")

    decision_date = delivery_date - timedelta(days=1)

    cutoff_local = datetime.combine(
        decision_date,
        time(hour=cutoff_hour),
        tzinfo=UK_TZ,
    )
    cutoff_utc = cutoff_local.astimezone(timezone.utc)

    actual_by_time = {}

    for record in actual_records:
        if str(record.get("fuelType", "")).upper() != "WIND":
            continue

        start = record.get("startTime")
        generation = to_number(record.get("generation"))

        if not start or generation is None:
            continue

        try:
            timestamp = parse_datetime(start)
        except (ValueError, TypeError):
            continue

        if timestamp.astimezone(UK_TZ).date() != delivery_date:
            continue

        actual_by_time[timestamp] = generation

    eligible_by_time = {}

    for record in forecast_records:
        start = record.get("startTime")
        published = record.get("publishTime")
        generation = to_number(record.get("generation"))

        if not start or not published or generation is None:
            continue

        try:
            target_time = parse_datetime(start)
            publish_time = parse_datetime(published)
        except (ValueError, TypeError):
            continue

        if target_time.astimezone(UK_TZ).date() != delivery_date:
            continue

        if publish_time > cutoff_utc:
            continue

        previous = eligible_by_time.get(target_time)

        if previous is None or publish_time > previous["publishTime"]:
            eligible_by_time[target_time] = {
                "publishTime": publish_time,
                "forecast": generation,
            }

    rows = []

    for target_time in sorted(actual_by_time.keys()):
        forecast_record = eligible_by_time.get(target_time)

        if forecast_record is None:
            continue

        actual = actual_by_time[target_time]
        forecast = forecast_record["forecast"]
        error = forecast - actual

        rows.append({
            "startTime": target_time.isoformat(),
            "publishTime": forecast_record["publishTime"].isoformat(),
            "forecast": forecast,
            "actual": actual,
            "error": error,
            "absoluteError": abs(error),
        })

    if rows:
        errors = [row["error"] for row in rows]
        absolute_errors = [abs(error) for error in errors]

        mae = sum(absolute_errors) / len(errors)
        rmse = math.sqrt(sum(error ** 2 for error in errors) / len(errors))
        bias = sum(errors) / len(errors)
    else:
        mae = None
        rmse = None
        bias = None

    return {
        "decisionDate": decision_date.isoformat(),
        "deliveryDate": delivery_date.isoformat(),
        "cutoffHourUK": cutoff_hour,
        "cutoffTimeUK": cutoff_local.isoformat(),
        "matchedPeriods": len(rows),
        "metrics": {
            "mae": mae,
            "rmse": rmse,
            "bias": bias,
        },
        "periods": rows,
    }
