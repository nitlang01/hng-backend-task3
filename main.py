from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.responses import FileResponse
from db import SessionLocal, engine, get_db
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Base, Country
from tasks import refresh_countries
from datetime import datetime
import os
import requests

app = FastAPI()


Base.metadata.create_all(bind=engine)

@app.post("/countries/refresh")
def refresh():
    try:
        result = refresh_countries()
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail={"error": str(e)})


@app.get("/countries")
def get_countries(
    region: str = Query(None),
    currency: str = Query(None),
    sort: str = Query(None)
):
    db = SessionLocal()
    query = db.query(Country)

    if region:
        query = query.filter(Country.region.ilike(f"%{region}%"))
    if currency:
        query = query.filter(Country.currency_code == currency)

    if sort == "gdp_desc":
        query = query.order_by(Country.estimated_gdp.desc())

    countries = query.all()
    db.close()
    return countries


@app.get("/countries/{name}")
def get_country(name: str):
    db = SessionLocal()
    country = db.query(Country).filter(Country.name.ilike(name)).first()
    db.close()
    if not country:
        raise HTTPException(status_code=404, detail={"error": "Country not found"})
    return country


@app.delete("/countries/{name}")
def delete_country(name: str):
    db = SessionLocal()
    country = db.query(Country).filter(Country.name.ilike(name)).first()
    if not country:
        db.close()
        raise HTTPException(status_code=404, detail={"error": "Country not found"})
    db.delete(country)
    db.commit()
    db.close()
    return {"message": f"{name} deleted successfully"}


@app.get("/status")
def get_status():
    db = SessionLocal()
    total = db.query(Country).count()
    last = db.query(Country.last_refreshed_at).order_by(Country.last_refreshed_at.desc()).first()
    db.close()
    return {
        "total_countries": total,
        "last_refreshed_at": last[0].isoformat() if last and last[0] else None
    }

from fastapi import Query

@app.get("/countries/image")
def get_summary_image():
    image_path = os.path.join("cache", "summary.png")
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail={"error": "Summary image not found"})
    return FileResponse(image_path, media_type="image/png")