from fastapi import Query, HTTPException
from db import SessionLocal
from models import Country
import requests
import os
from datetime import datetime


def get_all_countries(region: str = None, currency: str = None, sort: str = None):
    session = SessionLocal()
    query = session.query(Country)
    if region:
        query = query.filter(Country.region.ilike(f"%{region}%"))
    if currency:
        query = query.filter(Country.currency_code.ilike(f"%{currency}%"))
    countries = query.all()
    result = [c.to_dict() for c in countries]

    if sort == "gdp":
        result = sorted(result, key=lambda x: x["gdp"], reverse=True)

    return result

import random

import requests
import random
from db import SessionLocal
from models import Country

def refresh_countries():
    db = SessionLocal()

    try:
        countries_resp = requests.get("https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies")
        rates_resp = requests.get("https://open.er-api.com/v6/latest/USD")

        countries_data = countries_resp.json()
        rates_data = rates_resp.json()
        exchange_rates = rates_data.get("rates", {})

        for country in countries_data:
            name = country.get("name")
            capital = country.get("capital")
            region = country.get("region")
            population = country.get("population")
            flag = country.get("flag")

            # handle currencies
            currencies = country.get("currencies")
            if currencies and isinstance(currencies, list) and len(currencies) > 0:
                currency_code = currencies[0].get("code")
            else:
                currency_code = None

            # match exchange rate
            exchange_rate = exchange_rates.get(currency_code) if currency_code else None

            # compute GDP
            if exchange_rate and exchange_rate > 0:
                multiplier = random.randint(1000, 2000)
                estimated_gdp = population * multiplier / exchange_rate
            else:
                estimated_gdp = 0

            # store in DB...
            existing = db.query(Country).filter(Country.name.ilike(name)).first()
            if existing:
                existing.capital = capital
                existing.region = region
                existing.population = population
                existing.currency_code = currency_code
                existing.exchange_rate = exchange_rate
                existing.estimated_gdp = estimated_gdp
                existing.flag_url = flag
            else:
                new_country = Country(
                    name=name,
                    capital=capital,
                    region=region,
                    population=population,
                    currency_code=currency_code,
                    exchange_rate=exchange_rate,
                    estimated_gdp=estimated_gdp,
                    flag_url=flag
                )
                db.add(new_country)

        db.commit()
        return {"message": "Countries refreshed successfully"}

    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI()

@app.get("/countries/image")
def get_summary_image():
    image_path = os.path.join("cache", "summary.png")
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail={"error": "Summary image not found"})
    return FileResponse(image_path, media_type="image/png")

@app.get("/status")
def get_status():
    session = SessionLocal()
    total = session.query(Country).count()
    session.close()
    return {
        "total_countries": total,
        "last_refreshed_at": datetime.utcnow().isoformat()
    }

@app.exception_handler(404)
def not_found(request, exc):
    return JSONResponse(status_code=404, content={"error": "Not found"})
