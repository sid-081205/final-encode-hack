from sqlalchemy import Column, String, Float, Integer, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

Base = declarative_base()

class FirePrediction(Base):
    __tablename__ = "fire_predictions"
    
    id = Column(String, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    probability = Column(Float, nullable=False)  # 0-100
    risk_level = Column(String, nullable=False)  # low, medium, high, critical
    predicted_date = Column(String, nullable=False)  # YYYY-MM-DD
    factors = Column(JSON, nullable=False)  # List of contributing factors
    confidence = Column(Float, nullable=False)  # 0-100
    region = Column(String, nullable=False)
    weather_data = Column(JSON, nullable=True)  # Weather conditions at prediction time
    crop_data = Column(JSON, nullable=True)    # Crop pattern data
    historical_data = Column(JSON, nullable=True)  # Historical fire data summary
    model_version = Column(String, nullable=False, default="v1.0")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

# Pydantic models for API
class PredictionRequest(BaseModel):
    region: str = "all-northern-india"
    date_range: str = "next-7days"  # next-7days, next-14days, next-30days, custom
    custom_start_date: Optional[str] = None
    custom_end_date: Optional[str] = None
    confidence_level: float = 70.0  # Minimum confidence threshold
    include_weather: bool = True
    include_crop_pattern: bool = True
    include_historical: bool = True

class PredictionData(BaseModel):
    id: str
    latitude: float
    longitude: float
    probability: float
    risk_level: str
    predicted_date: str
    factors: List[str]
    confidence: float
    region: str
    created_at: str

class PredictionResponse(BaseModel):
    predictions: List[PredictionData]
    total_count: int
    filtered_count: int
    region: str
    date_range: str
    model_info: Dict[str, str]

class WeatherData(BaseModel):
    temperature: float
    humidity: float
    wind_speed: float
    wind_direction: float
    precipitation: float
    pressure: float
    visibility: float
    weather_condition: str
    location: str
    timestamp: str

class CropData(BaseModel):
    crop_type: str
    harvest_season: str
    burning_probability: float
    residue_amount: str  # low, medium, high
    area_hectares: float
    location: str

class HistoricalPattern(BaseModel):
    location: str
    fire_frequency: int
    seasonal_peak: str
    avg_confidence: float
    last_fire_date: Optional[str]
    fire_intensity_trend: str