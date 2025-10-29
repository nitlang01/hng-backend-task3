from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from db import Base

class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    capital = Column(String(255))
    region = Column(String(255))
    population = Column(Integer, nullable=False)
    currency_code = Column(String(10))
    exchange_rate = Column(Float)        # may be null
    estimated_gdp = Column(Float)        # may be null or 0
    flag_url = Column(String(512))
    last_refreshed_at = Column(DateTime(timezone=True))
