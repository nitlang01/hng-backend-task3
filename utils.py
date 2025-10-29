import os
from PIL import Image, ImageDraw, ImageFont
from typing import List
from models import Country

def serialize_country(c: Country):
    return {
        "id": c.id,
        "name": c.name,
        "capital": c.capital,
        "region": c.region,
        "population": c.population,
        "currency_code": c.currency_code,
        "exchange_rate": c.exchange_rate,
        "estimated_gdp": c.estimated_gdp,
        "flag_url": c.flag_url,
        "last_refreshed_at": c.last_refreshed_at.isoformat() if c.last_refreshed_at else None
    }

def make_summary_image(total: int, top5: List[Country], last_ref, path="cache/summary.png"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    width, height = 800, 600
    img = Image.new("RGBA", (width, height), (255,255,255,255))
    draw = ImageDraw.Draw(img)

    # basic fonts – system fallback
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        font_sm = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
        font_sm = ImageFont.load_default()

    draw.text((20,20), f"Total countries: {total}", font=font, fill="black")
    draw.text((20,60), f"Last refresh: {last_ref.isoformat()}", font=font_sm, fill="black")

    draw.text((20,110), "Top 5 by estimated GDP:", font=font, fill="black")
    y = 150
    for i, c in enumerate(top5, start=1):
        name = c.name
        gdp = f"{c.estimated_gdp:,.2f}" if c.estimated_gdp else "N/A"
        draw.text((30, y), f"{i}. {name} — {gdp}", font=font_sm, fill="black")
        y += 30

    img.save(path)
