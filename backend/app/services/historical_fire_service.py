import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional
from app.models.fire import FireDetectionCreate, FireDetectionResponse
from app.utils.regions import get_region_bounds

class HistoricalFireService:
    def __init__(self, db_path: str = "/Users/siddharthgianchandani/final-encode-hack/fire_data.db"):
        self.db_path = db_path
    
    def get_fires_by_date_range(self, 
                               start_date: str, 
                               end_date: str,
                               region: str = "all-northern-india",
                               sources: dict = None) -> List[FireDetectionResponse]:
        """
        Get fires from historical database for custom date range
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            region: Region to filter by
            sources: Dictionary of enabled sources
            
        Returns:
            List of FireDetectionResponse objects
        """
        if sources is None:
            sources = {"MODIS": True, "VIIRS": True, "User Reported": False}
        
        try:
            # Validate date range (max 31 days)
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            if (end_dt - start_dt).days > 31:
                raise ValueError("Date range cannot exceed 31 days")
            
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            
            # Build query
            query = """
            SELECT latitude, longitude, acq_date, acq_time, confidence, 
                   brightness, frp, instrument, satellite, track, scan
            FROM fires 
            WHERE acq_date >= ? AND acq_date <= ?
            """
            
            # Execute query
            df = pd.read_sql_query(query, conn, params=(start_date, end_date))
            conn.close()
            
            if df.empty:
                return []
            
            # Convert data types
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
            df['brightness'] = pd.to_numeric(df['brightness'], errors='coerce')
            df['confidence'] = pd.to_numeric(df['confidence'], errors='coerce')
            df['frp'] = pd.to_numeric(df['frp'], errors='coerce')
            
            # Remove rows with invalid coordinates
            df = df.dropna(subset=['latitude', 'longitude'])
            
            # Filter by Northern India bounds first
            northern_india_bounds = get_region_bounds("all-northern-india")
            if northern_india_bounds:
                ni_mask = (
                    (df['latitude'] >= northern_india_bounds['min_lat']) &
                    (df['latitude'] <= northern_india_bounds['max_lat']) &
                    (df['longitude'] >= northern_india_bounds['min_lon']) &
                    (df['longitude'] <= northern_india_bounds['max_lon'])
                )
                df = df[ni_mask]
                print(f"Filtered to Northern India bounds: {len(df)} records")
            
            # Then filter for specific region if not "all-northern-india"
            if region != "all-northern-india":
                region_bounds = get_region_bounds(region)
                if region_bounds:
                    region_mask = (
                        (df['latitude'] >= region_bounds['min_lat']) &
                        (df['latitude'] <= region_bounds['max_lat']) &
                        (df['longitude'] >= region_bounds['min_lon']) &
                        (df['longitude'] <= region_bounds['max_lon'])
                    )
                    df = df[region_mask]
                    print(f"Filtered to {region}: {len(df)} records")
            
            # Filter by sources
            enabled_sources = []
            if sources.get("VIIRS", False):
                enabled_sources.append("VIIRS")
            if sources.get("MODIS", False):
                enabled_sources.append("MODIS")
            
            if enabled_sources:
                df = df[df['instrument'].isin(enabled_sources)]
                print(f"Filtered by sources {enabled_sources}: {len(df)} records")
            
            # Convert to FireDetectionResponse objects
            fires = []
            for _, row in df.iterrows():
                try:
                    # Generate unique ID
                    fire_id = f"HIST_{row['instrument']}_{row['latitude']:.4f}_{row['longitude']:.4f}_{row['acq_date']}_{row['acq_time']}"
                    
                    # Parse acquisition datetime
                    try:
                        acq_datetime = datetime.strptime(f"{row['acq_date']} {str(row['acq_time']).zfill(4)}", "%Y-%m-%d %H%M")
                    except:
                        acq_datetime = datetime.strptime(row['acq_date'], "%Y-%m-%d")
                    
                    # Determine state based on coordinates
                    state = self._get_state_from_coordinates(row['latitude'], row['longitude'])
                    
                    fire = FireDetectionResponse(
                        id=fire_id,
                        latitude=float(row['latitude']),
                        longitude=float(row['longitude']),
                        brightness=float(row['brightness']) if pd.notna(row['brightness']) else 0.0,
                        confidence=int(row['confidence']) if pd.notna(row['confidence']) else 0,
                        acq_date=str(row['acq_date']),
                        acq_time=str(row['acq_time']).zfill(4),
                        acq_datetime=acq_datetime,
                        source=str(row['instrument']),
                        frp=float(row['frp']) if pd.notna(row['frp']) else None,
                        scan=float(row['scan']) if pd.notna(row['scan']) else None,
                        track=float(row['track']) if pd.notna(row['track']) else None,
                        state=state,
                        district=None,
                        created_at=datetime.now()
                    )
                    
                    fires.append(fire)
                    
                except Exception as e:
                    print(f"Error processing historical fire record: {e}")
                    continue
            
            print(f"Successfully processed {len(fires)} historical fires")
            return fires
            
        except Exception as e:
            print(f"Error querying historical fires: {e}")
            return []
    
    def _get_state_from_coordinates(self, lat: float, lon: float) -> Optional[str]:
        """Determine state based on coordinates"""
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
    
    def get_available_date_range(self) -> dict:
        """Get the available date range in the historical database"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = "SELECT MIN(acq_date) as min_date, MAX(acq_date) as max_date FROM fires"
            result = pd.read_sql_query(query, conn)
            conn.close()
            
            return {
                "min_date": result['min_date'].iloc[0],
                "max_date": result['max_date'].iloc[0]
            }
        except Exception as e:
            print(f"Error getting date range: {e}")
            return {"min_date": "2023-01-01", "max_date": "2025-06-21"}