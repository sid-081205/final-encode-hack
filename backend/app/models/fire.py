from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

Base = declarative_base()

class FireDetection(Base):
    __tablename__ = "fire_detections"
    
    id = Column(String, primary_key=True, index=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    brightness = Column(Float, nullable=False)
    confidence = Column(Integer, nullable=False)
    acq_date = Column(String, nullable=False, index=True)
    acq_time = Column(String, nullable=False)
    acq_datetime = Column(DateTime, nullable=False, index=True)
    source = Column(String, nullable=False, index=True)  # MODIS, VIIRS, User Reported
    frp = Column(Float, nullable=True)  # Fire Radiative Power
    scan = Column(Float, nullable=True)
    track = Column(Float, nullable=True)
    
    # Additional fields for region identification
    state = Column(String, nullable=True, index=True)
    district = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Pydantic models for API
class FireDetectionBase(BaseModel):
    latitude: float
    longitude: float
    brightness: float
    confidence: int
    acq_date: str
    acq_time: str
    source: str
    frp: Optional[float] = None
    scan: Optional[float] = None
    track: Optional[float] = None
    state: Optional[str] = None
    district: Optional[str] = None

class FireDetectionCreate(FireDetectionBase):
    pass

class FireDetectionResponse(FireDetectionBase):
    id: str
    acq_datetime: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class FireFilterRequest(BaseModel):
    region: str = "all-northern-india"
    date_range: str = "24hr"  # "24hr", "7day", "custom"
    custom_start_date: Optional[str] = None
    custom_end_date: Optional[str] = None
    sources: dict = {
        "MODIS": True,
        "VIIRS": True,
        "User Reported": False
    }

class FireFilterResponse(BaseModel):
    fires: List[FireDetectionResponse]
    total_count: int
    filtered_count: int
    region: str
    date_range: str