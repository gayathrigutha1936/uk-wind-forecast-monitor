import asyncio
import httpx

async def main():
    url = "https://data.elexon.co.uk/bmrs/api/v1/forecast/generation/wind/history"
    params = {"publishTime": "2026-01-15T10:00:00Z"}

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        payload = response.json()

    records = payload.get("data", [])

    target_records = [
        row for row in records
        if row.get("startTime", "").startswith("2026-01-16")
    ]

    print("Total historical records:", len(records))
    print("Records targeting January 16:", len(target_records))

    for row in target_records[:10]:
        print(row)

    if not target_records:
        print("No January 16 target records in this response.")

asyncio.run(main())
