from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.responses import FileResponse
from db import SessionLocal, engine, Base, get_db
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Base, Country
from tasks import refresh_countries
from datetime import datetime
import os
import requests

app = FastAPI()


Base.metadata.create_all(bind=engine)

def load_countries():
    db = SessionLocal()
    try:
        return [
            {
                "name": country.name,
                "capital": country.capital,
                "region": country.region,
                "population": country.population,
            }
            for country in db.query(Country).all()
        ]
    finally:
        db.close()

countries = load_countries()
last_refreshed_at = datetime.utcnow().isoformat()

@app.post("/countries/refresh")
def refresh_countries():
    db = SessionLocal()
    db.query(Country).delete()  # clear old data

    nigeria = Country(
        name="Nigeria",
        capital="Abuja",
        region="Africa",
        population=206139589,
        currency_code="NGN",
        exchange_rate=0.0013,
        estimated_gdp=432000000000,
        flag_url="https://flagcdn.com/w320/ng.png"
    )
    db.add(nigeria)
    db.commit()
    db.close()
    return {"message": "Countries refreshed successfully"}


from fastapi.responses import JSONResponse

from fastapi import HTTPException

@app.get("/countries")
def get_countries():
    db = SessionLocal()
    try:
        countries = db.query(Country).all()
        return {
            "countries": [
                {
                    "name": c.name,
                    "capital": c.capital,
                    "region": c.region,
                    "population": c.population,
                }
                for c in countries
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/countries/{name}")
def get_country(name: str):
    db = SessionLocal()
    country = db.query(Country).filter(Country.name.ilike(name)).first()
    db.close()

    if not country:
        raise HTTPException(status_code=404, detail=f"Country '{name}' not found")

    return {
        "name": country.name,
        "capital": country.capital,
        "region": country.region,
        "population": country.population,
        "currency_code": country.currency_code,
        "exchange_rate": country.exchange_rate,
        "estimated_gdp": country.estimated_gdp,
        "flag_url": country.flag_url,
        "last_refreshed_at": country.last_refreshed_at
    }

@app.get("/status")
def get_status():
    return {"total_countries": len(countries), "last_refreshed_at": last_refreshed_at}

from fastapi.responses import FileResponse
import os


from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError

from fastapi.responses import FileResponse
import os

@app.get("/countries/image")
def get_image():
    image_path = "summary_test.png"  
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(image_path, media_type="image/png")

@app.delete("/countries/{country_name}")
def delete_country(country_name: str):
    return {"message": f"{country_name} deleted successfully"}


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail if isinstance(exc.detail, dict) else {"message": str(exc.detail)}}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": "Invalid request", "details": exc.errors()})