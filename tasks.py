import os, random
from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError
from db import SessionLocal
from models import Country
from fetcher import fetch_external_data
from utils import make_summary_image
from dotenv import load_dotenv

load_dotenv()

RANDOM_MIN = int(os.getenv("RANDOM_MIN", "1000"))
RANDOM_MAX = int(os.getenv("RANDOM_MAX", "2000"))
SUMMARY_PATH = os.getenv("SUMMARY_IMAGE_PATH", "cache/summary.png")

def refresh_countries():
    try:
        countries_json, exchange_json = fetch_external_data()
    except Exception as e:
        return {"error": f"External data source unavailable: {e}"}, 503

    rates = exchange_json.get("rates") or {}
    last_ref = datetime.now(timezone.utc)

    db = SessionLocal()
    try:
        for c in countries_json:
            name = None
            if isinstance(c.get("name"), dict):
                name = c.get("name").get("common") or c.get("name").get("official")
            else:
                name = c.get("name")
            if not name or not c.get("population"):
                continue

            population = int(c.get("population", 0))
            capital = c.get("capital")
            region = c.get("region")
            flag = c.get("flag") or c.get("flags", {}).get("svg") or c.get("flag_url")
            currencies = c.get("currencies") or []
            currency_code = None
            exchange_rate = None
            estimated_gdp = None

            if isinstance(currencies, list) and len(currencies) > 0:
                first = currencies[0]
                code = first.get("code") if isinstance(first, dict) else None
            elif isinstance(currencies, dict):
                keys = list(currencies.keys())
                code = keys[0] if keys else None
            else:
                code = None

            if code:
                currency_code = code
                rate = rates.get(code)
                if rate is None:
                    exchange_rate = None
                    estimated_gdp = None
                else:
                    exchange_rate = float(rate)
                    multiplier = random.uniform(RANDOM_MIN, RANDOM_MAX)
                    estimated_gdp = population * multiplier / exchange_rate
            else:
                currency_code = None
                exchange_rate = None
                estimated_gdp = 0

            existing = db.query(Country).filter(Country.name.ilike(name)).first()
            if existing:
                existing.capital = capital
                existing.region = region
                existing.population = population
                existing.currency_code = currency_code
                existing.exchange_rate = exchange_rate
                existing.estimated_gdp = estimated_gdp
                existing.flag_url = flag
                existing.last_refreshed_at = last_ref
            else:
                new = Country(
                    name=name,
                    capital=capital,
                    region=region,
                    population=population,
                    currency_code=currency_code,
                    exchange_rate=exchange_rate,
                    estimated_gdp=estimated_gdp,
                    flag_url=flag,
                    last_refreshed_at=last_ref
                )
                db.add(new)
        db.commit()

        total = db.query(Country).count()
        top5 = db.query(Country).order_by(Country.estimated_gdp.desc().nullslast()).limit(5).all()
        make_summary_image(total, top5, last_ref, SUMMARY_PATH)

        return {"total": total, "last_refreshed_at": last_ref.isoformat()}, 200

    except SQLAlchemyError as e:
        db.rollback()
        return {"error": "Internal server error"}, 500
    finally:
        db.close()
