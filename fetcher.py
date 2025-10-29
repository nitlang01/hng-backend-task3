import os
import httpx
from dotenv import load_dotenv

load_dotenv()

COUNTRIES_API_URL = os.getenv("COUNTRIES_API_URL")
EXCHANGE_API_URL = os.getenv("EXCHANGE_API_URL")

if not COUNTRIES_API_URL or not EXCHANGE_API_URL:
    # allow app to start but functions should raise if called
    pass

def fetch_external_data(timeout=20):
    if not COUNTRIES_API_URL or not EXCHANGE_API_URL:
        raise RuntimeError("Missing API URLs in environment variables")
    try:
        with httpx.Client(timeout=timeout) as client:
            r1 = client.get(COUNTRIES_API_URL)
            r2 = client.get(EXCHANGE_API_URL)
            r1.raise_for_status()
            r2.raise_for_status()
            countries = r1.json()
            exchange = r2.json()
            return countries, exchange
    except Exception as e:
        raise RuntimeError(f"External data source unavailable: {e}")
