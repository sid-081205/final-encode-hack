import requests
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app.models.fire import FireDetectionCreate
from app.utils.regions import get_region_bounds, is_point_in_region

class FireAPIService:
    def __init__(self, map_key: str = "8895c7fb00b5e05b915b2bcddf354a2b"):
        self.map_key = map_key
        self.base_url = f"https://firms.modaps.eosdis.nasa.gov/mapserver/wfs/South_Asia/{map_key}/"
    
    def fetch_fire_data(self, typename: str, count: int = 1000) -> pd.DataFrame:
        """
        Fetch fire data from NASA FIRMS WFS service
        
        Args:
            typename: Either 'ms:fires_modis_24hrs' or 'ms:fires_modis_7days'
            count: Maximum number of records to fetch
        
        Returns:
            pandas.DataFrame: Fire data
        """
        params = {
            'SERVICE': 'WFS',
            'REQUEST': 'GetFeature',
            'VERSION': '2.0.0',
            'TYPENAME': typename,
            'STARTINDEX': 0,
            'COUNT': count,
            'SRSNAME': 'urn:ogc:def:crs:EPSG::4326',
            'BBOX': '-90,-180,90,180,urn:ogc:def:crs:EPSG::4326',
            'outputformat': 'csv'
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            # Read CSV data into DataFrame
            csv_data = StringIO(response.text)
            df = pd.read_csv(csv_data)
            
            return df
            
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()
    
    def get_24hr_fires(self, region: str = "all-northern-india") -> List[FireDetectionCreate]:
        """Get 24-hour fire data"""
        df = self.fetch_fire_data('ms:fires_modis_24hrs')
        return self._process_fire_data(df, region, "MODIS")
    
    def get_7day_fires(self, region: str = "all-northern-india") -> List[FireDetectionCreate]:
        """Get 7-day fire data"""
        df = self.fetch_fire_data('ms:fires_modis_7days')
        return self._process_fire_data(df, region, "MODIS")
    
    def _process_fire_data(self, df: pd.DataFrame, region: str, source: str) -> List[FireDetectionCreate]:
        """Process raw fire data into FireDetectionCreate objects"""
        if df.empty:
            return []
        
        fires = []
        
        # Find latitude and longitude columns (case insensitive)
        lat_col = None
        lon_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if 'lat' in col_lower and lat_col is None:
                lat_col = col
            elif 'lon' in col_lower and lon_col is None:
                lon_col = col
        
        if lat_col is None or lon_col is None:
            print("Warning: Could not find latitude/longitude columns")
            print("Available columns:", df.columns.tolist())
            return []
        
        # Always filter for Northern India bounds first (since we're getting South Asia data)
        northern_india_bounds = get_region_bounds("all-northern-india")
        if northern_india_bounds:
            ni_mask = (
                (df[lat_col] >= northern_india_bounds['min_lat']) &
                (df[lat_col] <= northern_india_bounds['max_lat']) &
                (df[lon_col] >= northern_india_bounds['min_lon']) &
                (df[lon_col] <= northern_india_bounds['max_lon'])
            )
            df = df[ni_mask]
            print(f"Filtered to Northern India: {len(df)} records remaining")
        
        # Then filter for the specific region if not "all-northern-india"
        if region != "all-northern-india":
            bounds = get_region_bounds(region)
            if bounds:
                mask = (
                    (df[lat_col] >= bounds['min_lat']) &
                    (df[lat_col] <= bounds['max_lat']) &
                    (df[lon_col] >= bounds['min_lon']) &
                    (df[lon_col] <= bounds['max_lon'])
                )
                df = df[mask]
                print(f"Filtered to {region}: {len(df)} records remaining")
        
        # Convert DataFrame rows to FireDetectionCreate objects
        for _, row in df.iterrows():
            try:
                # Generate unique ID
                fire_id = f"{source}_{row[lat_col]:.4f}_{row[lon_col]:.4f}_{row.get('acq_date', '')}_{row.get('acq_time', '')}"
                
                # Parse acquisition datetime
                acq_date = str(row.get('acq_date', ''))
                acq_time = str(row.get('acq_time', '0000')).zfill(4)
                
                # Determine state based on coordinates
                state = self._get_state_from_coordinates(row[lat_col], row[lon_col])
                
                fire = FireDetectionCreate(
                    latitude=float(row[lat_col]),
                    longitude=float(row[lon_col]),
                    brightness=float(row.get('brightness', 0)),
                    confidence=int(row.get('confidence', 0)),
                    acq_date=acq_date,
                    acq_time=acq_time,
                    source=source,
                    frp=float(row.get('frp', 0)) if pd.notna(row.get('frp')) else None,
                    scan=float(row.get('scan', 0)) if pd.notna(row.get('scan')) else None,
                    track=float(row.get('track', 0)) if pd.notna(row.get('track')) else None,
                    state=state
                )
                
                fires.append(fire)
                
            except Exception as e:
                print(f"Error processing fire data row: {e}")
                continue
        
        print(f"Processed {len(fires)} fires for region {region}")
        return fires
    
    def _get_state_from_coordinates(self, lat: float, lon: float) -> Optional[str]:
        """Determine state based on coordinates"""
        # Simple state detection based on coordinate ranges
        # This is a simplified version - you might want to use a more sophisticated method
        
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