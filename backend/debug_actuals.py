import asyncio
import httpx

async def main():
    url = "https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH"

    params = {
        "settlementDateFrom": "2026-01-16",
        "settlementDateTo": "2026-01-16",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        print("Status:", response.status_code)
        print("URL:", response.url)
        response.raise_for_status()

        payload = response.json()
        records = payload if isinstance(payload, list) else payload.get("data", [])

        wind_records = [
            row for row in records
            if str(row.get("fuelType", "")).upper() == "WIND"
            and row.get("settlementDate") == "2026-01-16"
        ]

        print("Total records:", len(records))
        print("January 16 wind records:", len(wind_records))
        print("Dates returned:", sorted({
            str(row.get("settlementDate"))
            for row in records
        }))

        for row in wind_records[:5]:
            print(row)

asyncio.run(main())
