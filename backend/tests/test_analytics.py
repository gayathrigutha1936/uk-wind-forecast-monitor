from datetime import date

from app.analytics import calculate_analysis


def test_latest_forecast_before_cutoff():
    actuals = [{
        "fuelType": "WIND",
        "startTime": "2026-01-16T09:00:00Z",
        "generation": 4200,
    }]

    forecasts = [
        {
            "startTime": "2026-01-16T09:00:00Z",
            "publishTime": "2026-01-15T08:00:00Z",
            "generation": 4000,
        },
        {
            "startTime": "2026-01-16T09:00:00Z",
            "publishTime": "2026-01-15T09:00:00Z",
            "generation": 4500,
        },
        {
            "startTime": "2026-01-16T09:00:00Z",
            "publishTime": "2026-01-15T11:00:00Z",
            "generation": 5000,
        },
    ]

    result = calculate_analysis(
        actuals, forecasts, date(2026, 1, 16), 10
    )

    assert result["matchedPeriods"] == 1
    assert result["periods"][0]["forecast"] == 4500
    assert result["metrics"]["mae"] == 300
    assert result["metrics"]["bias"] == 300


def test_ignores_non_wind_actuals():
    actuals = [{
        "fuelType": "BIOMASS",
        "startTime": "2026-01-16T09:00:00Z",
        "generation": 4200,
    }]

    forecasts = [{
        "startTime": "2026-01-16T09:00:00Z",
        "publishTime": "2026-01-15T09:00:00Z",
        "generation": 4500,
    }]

    result = calculate_analysis(
        actuals, forecasts, date(2026, 1, 16), 10
    )

    assert result["matchedPeriods"] == 0
