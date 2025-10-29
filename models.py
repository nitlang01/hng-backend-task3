from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from db import Base

class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    capital = Column(String, nullable=True)
    region = Column(String, nullable=True)
    population = Column(Integer, nullable=False)
    currency_code = Column(String, nullable=True)
    exchange_rate = Column(Float, nullable=True)
    estimated_gdp = Column(Float, nullable=True)
    flag_url = Column(String, nullable=True)
    last_refreshed_at = Column(DateTime, default=datetime.utcnow)
