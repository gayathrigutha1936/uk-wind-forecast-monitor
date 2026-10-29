import asyncio
from datetime import date

from app.elexon import fetch_actuals, fetch_forecasts


async def main():
    delivery_date = date(2026, 1, 16)
    decision_date = date(2026, 1, 15)

    actuals, forecasts = await asyncio.gather(
        fetch_actuals(delivery_date),
        fetch_forecasts(decision_date, delivery_date),
    )

    print("\n--- ACTUAL WIND DATA ---")
    print("Records:", len(actuals))
    for row in actuals[:3]:
        print(row)

    print("\n--- FORECAST DATA ---")
    print("Records:", len(forecasts))
    for row in forecasts[:3]:
        print(row)


asyncio.run(main())
