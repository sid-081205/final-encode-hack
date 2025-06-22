from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from typing import List, Optional
import uuid

from app.models.fire import FireDetection, FireDetectionCreate, FireDetectionResponse, UserReportedFire, UserReportedFireCreate, UserReportedFireResponse
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
            
            # Add user-reported fires if enabled
            if sources.get("User Reported", False):
                user_fires = self._get_user_reported_fires(region, date_range)
                fires.extend(user_fires)
            
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
    
    def create_user_report(self, report_data: UserReportedFireCreate) -> UserReportedFireResponse:
        """Create a new user-reported fire incident"""
        try:
            # Generate unique ID
            report_id = f"USER_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"
            
            # Determine state from coordinates (simplified)
            state = self._get_state_from_coordinates(report_data.latitude, report_data.longitude)
            
            # Create new user report
            user_report = UserReportedFire(
                id=report_id,
                latitude=report_data.latitude,
                longitude=report_data.longitude,
                severity=report_data.severity,
                description=report_data.description,
                reporter_name=report_data.reporter_name,
                reporter_contact=report_data.reporter_contact,
                location_name=report_data.location_name,
                state=state or report_data.state,
                district=report_data.district,
                estimated_area=report_data.estimated_area,
                smoke_visibility=report_data.smoke_visibility,
                fire_type=report_data.fire_type
            )
            
            self.db.add(user_report)
            self.db.commit()
            self.db.refresh(user_report)
            
            return self._convert_user_report_to_response(user_report)
            
        except Exception as e:
            print(f"Error creating user report: {e}")
            self.db.rollback()
            raise e
    
    def get_user_reports(self, region: str = "all-northern-india", status_filter: str = "all", limit: int = 100) -> List[UserReportedFireResponse]:
        """Get user-reported fire incidents"""
        try:
            query = self.db.query(UserReportedFire)
            
            # Filter by status
            if status_filter != "all":
                query = query.filter(UserReportedFire.status == status_filter)
            
            # Filter by region if not all-northern-india
            if region != "all-northern-india":
                # Add region filtering based on coordinates or state
                if region in ['punjab', 'haryana', 'uttar-pradesh', 'delhi', 'rajasthan', 'himachal-pradesh', 'uttarakhand']:
                    query = query.filter(UserReportedFire.state == region)
            
            # Order by most recent first
            query = query.order_by(UserReportedFire.reported_at.desc())
            
            # Apply limit
            reports = query.limit(limit).all()
            
            return [self._convert_user_report_to_response(report) for report in reports]
            
        except Exception as e:
            print(f"Error getting user reports: {e}")
            return []
    
    def verify_user_report(self, report_id: str, verified_by: str) -> Optional[UserReportedFireResponse]:
        """Verify a user-reported incident"""
        try:
            report = self.db.query(UserReportedFire).filter(UserReportedFire.id == report_id).first()
            
            if not report:
                return None
            
            report.status = "Verified"
            report.verified_by = verified_by
            report.verified_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(report)
            
            return self._convert_user_report_to_response(report)
            
        except Exception as e:
            print(f"Error verifying user report: {e}")
            self.db.rollback()
            return None
    
    def _get_user_reported_fires(self, region: str, date_range: str) -> List[FireDetectionResponse]:
        """Get user-reported fires in the format compatible with regular fire detection"""
        try:
            query = self.db.query(UserReportedFire)
            
            # Filter by date range
            if date_range == "24hr":
                since_date = datetime.now() - timedelta(hours=24)
                query = query.filter(UserReportedFire.reported_at >= since_date)
            elif date_range == "7day":
                since_date = datetime.now() - timedelta(days=7)
                query = query.filter(UserReportedFire.reported_at >= since_date)
            
            # Filter by region
            if region != "all-northern-india":
                if region in ['punjab', 'haryana', 'uttar-pradesh', 'delhi', 'rajasthan', 'himachal-pradesh', 'uttarakhand']:
                    query = query.filter(UserReportedFire.state == region)
            
            user_reports = query.all()
            
            # Convert to FireDetectionResponse format
            converted_fires = []
            for report in user_reports:
                # Convert severity to confidence score
                confidence_map = {"Low": 25, "Medium": 50, "High": 75, "Critical": 95}
                confidence = confidence_map.get(report.severity, 50)
                
                # Estimate brightness based on severity
                brightness_map = {"Low": 300, "Medium": 320, "High": 350, "Critical": 400}
                brightness = brightness_map.get(report.severity, 320)
                
                # Estimate FRP based on area and severity
                frp = 0
                if report.estimated_area:
                    base_frp = report.estimated_area * 2  # 2 MW per hectare base
                    severity_multiplier = {"Low": 1, "Medium": 1.5, "High": 2, "Critical": 3}
                    frp = base_frp * severity_multiplier.get(report.severity, 1)
                
                fire_response = FireDetectionResponse(
                    id=report.id,
                    latitude=report.latitude,
                    longitude=report.longitude,
                    brightness=brightness,
                    confidence=confidence,
                    acq_date=report.reported_at.strftime("%Y-%m-%d"),
                    acq_time=report.reported_at.strftime("%H%M"),
                    acq_datetime=report.reported_at,
                    source="User Reported",
                    frp=frp if frp > 0 else None,
                    scan=None,
                    track=None,
                    state=report.state,
                    district=report.district,
                    created_at=report.reported_at
                )
                converted_fires.append(fire_response)
            
            return converted_fires
            
        except Exception as e:
            print(f"Error getting user reported fires: {e}")
            return []
    
    def _convert_user_report_to_response(self, report: UserReportedFire) -> UserReportedFireResponse:
        """Convert user report database model to response model"""
        return UserReportedFireResponse(
            id=report.id,
            latitude=report.latitude,
            longitude=report.longitude,
            severity=report.severity,
            description=report.description,
            reporter_name=report.reporter_name,
            reporter_contact=report.reporter_contact,
            location_name=report.location_name,
            state=report.state,
            district=report.district,
            estimated_area=report.estimated_area,
            smoke_visibility=report.smoke_visibility,
            fire_type=report.fire_type,
            status=report.status,
            verified_by=report.verified_by,
            reported_at=report.reported_at,
            verified_at=report.verified_at,
            resolved_at=report.resolved_at
        )
    
    def _get_state_from_coordinates(self, lat: float, lon: float) -> Optional[str]:
        """Simple state detection based on coordinates"""
        state_bounds = {
            'punjab': {'min_lat': 29.5, 'max_lat': 32.5, 'min_lon': 73.5, 'max_lon': 76.5},
            'haryana': {'min_lat': 27.5, 'max_lat': 30.9, 'min_lon': 74.0, 'max_lon': 77.5},
            'uttar-pradesh': {'min_lat': 23.8, 'max_lat': 30.4, 'min_lon': 77.0, 'max_lon': 84.6},
            'delhi': {'min_lat': 28.4, 'max_lat': 28.9, 'min_lon': 76.8, 'max_lon': 77.3},
            'rajasthan': {'min_lat': 23.0, 'max_lat': 30.2, 'min_lon': 69.5, 'max_lon': 78.3},
            'himachal-pradesh': {'min_lat': 30.2, 'max_lat': 33.2, 'min_lon': 75.5, 'max_lon': 79.0},
            'uttarakhand': {'min_lat': 28.4, 'max_lat': 31.5, 'min_lon': 77.5, 'max_lon': 81.1}
        }
        
        for state, bounds in state_bounds.items():
            if (bounds['min_lat'] <= lat <= bounds['max_lat'] and 
                bounds['min_lon'] <= lon <= bounds['max_lon']):
                return state
        
        return None