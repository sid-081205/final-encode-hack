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

class UserReportedFire(Base):
    __tablename__ = "user_reported_fires"
    
    id = Column(String, primary_key=True, index=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    
    # User-specific fields
    severity = Column(String, nullable=False)  # Low, Medium, High, Critical
    description = Column(String, nullable=True)
    reporter_name = Column(String, nullable=True)
    reporter_contact = Column(String, nullable=True)
    
    # Location details
    location_name = Column(String, nullable=True)
    state = Column(String, nullable=True, index=True)
    district = Column(String, nullable=True)
    
    # Fire details
    estimated_area = Column(Float, nullable=True)  # in hectares
    smoke_visibility = Column(String, nullable=True)  # None, Light, Moderate, Heavy
    fire_type = Column(String, default="Stubble Burning", index=True)
    
    # Status tracking
    status = Column(String, default="Reported", index=True)  # Reported, Verified, Resolved, False Report
    verified_by = Column(String, nullable=True)
    
    # Metadata
    reported_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

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

# User Reported Fire Pydantic Models
class UserReportedFireBase(BaseModel):
    latitude: float
    longitude: float
    severity: str  # Low, Medium, High, Critical
    description: Optional[str] = None
    reporter_name: Optional[str] = None
    reporter_contact: Optional[str] = None
    location_name: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    estimated_area: Optional[float] = None
    smoke_visibility: Optional[str] = None
    fire_type: str = "Stubble Burning"

class UserReportedFireCreate(UserReportedFireBase):
    pass

class UserReportedFireResponse(UserReportedFireBase):
    id: str
    status: str
    verified_by: Optional[str] = None
    reported_at: datetime
    verified_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True