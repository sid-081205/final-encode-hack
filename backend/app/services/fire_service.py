from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from typing import List, Optional
import uuid

from app.models.fire import FireDetection, FireDetectionCreate, FireDetectionResponse
from app.services.fire_api import FireAPIService
from app.services.historical_fire_service import HistoricalFireService
from app.utils.regions import is_point_in_region

class FireService:
    def __init__(self, db: Session):
        self.db = db
        self.api_service = FireAPIService()
        self.historical_service = HistoricalFireService()
    
    def get_fires_by_filters(self, 
                           region: str = "all-northern-india",
                           date_range: str = "24hr",
                           custom_start_date: Optional[str] = None,
                           custom_end_date: Optional[str] = None,
                           sources: dict = None) -> List[FireDetectionResponse]:
        """
        Get fires based on filters
        
        Args:
            region: Region to filter by
            date_range: "24hr", "7day", or "custom"
            custom_start_date: Start date for custom range (YYYY-MM-DD)
            custom_end_date: End date for custom range (YYYY-MM-DD)
            sources: Dictionary of enabled sources
            
        Returns:
            List of FireDetectionResponse objects
        """
        if sources is None:
            sources = {"MODIS": True, "VIIRS": True, "User Reported": False}
        
        if date_range in ["24hr", "7day"]:
            # Use API for recent data
            return self._get_recent_fires(region, date_range, sources)
        elif date_range == "custom" and custom_start_date and custom_end_date:
            # Use database for custom date range
            return self._get_custom_date_fires(region, custom_start_date, custom_end_date, sources)
        else:
            return []
    
    def _get_recent_fires(self, region: str, date_range: str, sources: dict) -> List[FireDetectionResponse]:
        """Get recent fires from API and update database"""
        fires = []
        
        try:
            if sources.get("MODIS", False):
                if date_range == "24hr":
                    api_fires = self.api_service.get_24hr_fires(region)
                else:  # 7day
                    api_fires = self.api_service.get_7day_fires(region)
                
                # Save to database and convert to response format
                for fire_data in api_fires:
                    fire_db = self._save_fire_to_db(fire_data)
                    if fire_db:
                        fires.append(self._convert_to_response(fire_db))
            
            # TODO: Add VIIRS support when available
            # if sources.get("VIIRS", False):
            #     viirs_fires = self.api_service.get_viirs_fires(region, date_range)
            #     for fire_data in viirs_fires:
            #         fire_db = self._save_fire_to_db(fire_data)
            #         if fire_db:
            #             fires.append(self._convert_to_response(fire_db))
            
        except Exception as e:
            print(f"Error fetching recent fires: {e}")
        
        return fires
    
    def _get_custom_date_fires(self, region: str, start_date: str, end_date: str, sources: dict) -> List[FireDetectionResponse]:
        """Get fires from historical database for custom date range"""
        try:
            # Use historical fire service for custom date ranges
            return self.historical_service.get_fires_by_date_range(
                start_date=start_date,
                end_date=end_date,
                region=region,
                sources=sources
            )
            
        except Exception as e:
            print(f"Error fetching custom date fires: {e}")
            return []
    
    def _save_fire_to_db(self, fire_data: FireDetectionCreate) -> Optional[FireDetection]:
        """Save fire data to database"""
        try:
            # Generate unique ID
            fire_id = f"{fire_data.source}_{fire_data.latitude:.4f}_{fire_data.longitude:.4f}_{fire_data.acq_date}_{fire_data.acq_time}"
            
            # Check if fire already exists
            existing_fire = self.db.query(FireDetection).filter(FireDetection.id == fire_id).first()
            if existing_fire:
                return existing_fire
            
            # Parse acquisition datetime
            try:
                acq_datetime = datetime.strptime(f"{fire_data.acq_date} {fire_data.acq_time.zfill(4)}", "%Y-%m-%d %H%M")
            except:
                acq_datetime = datetime.now()
            
            # Create new fire record
            fire_db = FireDetection(
                id=fire_id,
                latitude=fire_data.latitude,
                longitude=fire_data.longitude,
                brightness=fire_data.brightness,
                confidence=fire_data.confidence,
                acq_date=fire_data.acq_date,
                acq_time=fire_data.acq_time,
                acq_datetime=acq_datetime,
                source=fire_data.source,
                frp=fire_data.frp,
                scan=fire_data.scan,
                track=fire_data.track,
                state=fire_data.state,
                district=fire_data.district
            )
            
            self.db.add(fire_db)
            self.db.commit()
            self.db.refresh(fire_db)
            
            return fire_db
            
        except Exception as e:
            print(f"Error saving fire to database: {e}")
            self.db.rollback()
            return None
    
    def _convert_to_response(self, fire_db: FireDetection) -> FireDetectionResponse:
        """Convert database model to response model"""
        return FireDetectionResponse(
            id=fire_db.id,
            latitude=fire_db.latitude,
            longitude=fire_db.longitude,
            brightness=fire_db.brightness,
            confidence=fire_db.confidence,
            acq_date=fire_db.acq_date,
            acq_time=fire_db.acq_time,
            acq_datetime=fire_db.acq_datetime,
            source=fire_db.source,
            frp=fire_db.frp,
            scan=fire_db.scan,
            track=fire_db.track,
            state=fire_db.state,
            district=fire_db.district,
            created_at=fire_db.created_at
        )
    
    def get_fire_statistics(self, fires: List[FireDetectionResponse]) -> dict:
        """Calculate statistics for fire data"""
        if not fires:
            return {
                "total_fires": 0,
                "high_confidence_fires": 0,
                "average_confidence": 0,
                "total_fire_power": 0.0,
                "sources": {},
                "states": {}
            }
        
        total_fires = len(fires)
        high_confidence_fires = len([f for f in fires if f.confidence >= 80])
        average_confidence = sum(f.confidence for f in fires) / total_fires
        total_fire_power = sum(f.frp for f in fires if f.frp)
        
        # Count by source
        sources = {}
        for fire in fires:
            sources[fire.source] = sources.get(fire.source, 0) + 1
        
        # Count by state
        states = {}
        for fire in fires:
            if fire.state:
                states[fire.state] = states.get(fire.state, 0) + 1
        
        return {
            "total_fires": total_fires,
            "high_confidence_fires": high_confidence_fires,
            "average_confidence": round(average_confidence, 1),
            "total_fire_power": round(total_fire_power, 1),
            "sources": sources,
            "states": states
        }