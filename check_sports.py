
import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("THE_ODDS_API_KEY")

async def check_sports():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://api.the-odds-api.com/v4/sports?apiKey={API_KEY}")
        if resp.status_code == 200:
            sports = resp.json()
            print("Active Sports:")
            for s in sports:
                if 'tennis' in s['key']:
                    print(f"- {s['key']} ({s['title']})")
        else:
            print(f"Error: {resp.status_code} {resp.text}")

asyncio.run(check_sports())
