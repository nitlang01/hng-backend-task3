from dotenv import load_dotenv
load_dotenv()  # MUST be first
import os
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse, JSONResponse
from db import engine, Base, SessionLocal
from models import Country
from tasks import refresh_countries
from utils import serialize_country

app = FastAPI(title="Country Currency & Exchange API")

Base.metadata.create_all(bind=engine)

@app.post("/countries/refresh")
def post_refresh():
    payload, status = refresh_countries()
    return JSONResponse(content=payload, status_code=status)

@app.get("/countries")
def list_countries(region: str = None, currency: str = None, sort: str = None, limit: int = Query(None, ge=0)):
    db = SessionLocal()
    try:
        q = db.query(Country)
        if region:
            q = q.filter(Country.region == region)
        if currency:
            q = q.filter(Country.currency_code == currency)
        if sort == "gdp_desc":
            q = q.order_by(Country.estimated_gdp.desc().nullslast())
        if limit:
            q = q.limit(limit)
        rows = q.all()
        return [serialize_country(r) for r in rows]
    finally:
        db.close()

@app.get("/countries/{name}")
def get_country(name: str):
    db = SessionLocal()
    try:
        c = db.query(Country).filter(Country.name.ilike(name)).first()
        if not c:
            raise HTTPException(status_code=404, detail={"error": "Country not found"})
        return serialize_country(c)
    finally:
        db.close()

@app.delete("/countries/{name}", status_code=204)
def delete_country(name: str):
    db = SessionLocal()
    try:
        c = db.query(Country).filter(Country.name.ilike(name)).first()
        if not c:
            raise HTTPException(status_code=404, detail={"error": "Country not found"})
        db.delete(c)
        db.commit()
        return Response(status_code=204)
    finally:
        db.close()

@app.get("/status")
def status():
    db = SessionLocal()
    try:
        total = db.query(Country).count()
        last = db.query(Country).order_by(Country.last_refreshed_at.desc()).first()
        return {"total_countries": total, "last_refreshed_at": last.last_refreshed_at.isoformat() if last and last.last_refreshed_at else None}
    finally:
        db.close()

@app.get("/countries/image")
def serve_image():
    path = os.getenv("SUMMARY_IMAGE_PATH", "cache/summary.png")
    if not os.path.exists(path):
        return JSONResponse(status_code=404, content={"error": "Summary image not found"})
    return FileResponse(path, media_type="image/png")
