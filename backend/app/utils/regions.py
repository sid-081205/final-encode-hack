from typing import Dict, Optional, Tuple

def get_region_bounds(region: str) -> Optional[Dict[str, float]]:
    """
    Get bounding box coordinates for different regions in Northern India
    
    Args:
        region: Region identifier
        
    Returns:
        Dictionary with min/max lat/lon bounds or None if region not found
    """
    region_bounds = {
        'all-northern-india': {
            'min_lat': 23.5, 'max_lat': 32.0,
            'min_lon': 73.0, 'max_lon': 84.5
        },
        'punjab': {
            'min_lat': 29.5, 'max_lat': 32.5,
            'min_lon': 73.5, 'max_lon': 76.5
        },
        'haryana': {
            'min_lat': 27.5, 'max_lat': 30.9,
            'min_lon': 74.0, 'max_lon': 77.5
        },
        'uttar-pradesh': {
            'min_lat': 23.8, 'max_lat': 30.4,
            'min_lon': 77.0, 'max_lon': 84.6
        },
        'delhi': {
            'min_lat': 28.4, 'max_lat': 28.9,
            'min_lon': 76.8, 'max_lon': 77.3
        },
        'rajasthan': {
            'min_lat': 23.0, 'max_lat': 30.2,
            'min_lon': 69.5, 'max_lon': 78.3
        },
        'himachal-pradesh': {
            'min_lat': 30.2, 'max_lat': 33.2,
            'min_lon': 75.5, 'max_lon': 79.0
        },
        'uttarakhand': {
            'min_lat': 28.4, 'max_lat': 31.5,
            'min_lon': 77.5, 'max_lon': 81.1
        },
        # City areas
        'chandigarh': {
            'min_lat': 30.6, 'max_lat': 30.8,
            'min_lon': 76.6, 'max_lon': 76.9
        },
        'amritsar': {
            'min_lat': 31.5, 'max_lat': 31.8,
            'min_lon': 74.7, 'max_lon': 75.0
        },
        'ludhiana': {
            'min_lat': 30.8, 'max_lat': 31.0,
            'min_lon': 75.7, 'max_lon': 76.0
        },
        'gurgaon': {
            'min_lat': 28.3, 'max_lat': 28.6,
            'min_lon': 76.8, 'max_lon': 77.2
        }
    }
    
    return region_bounds.get(region)

def is_point_in_region(lat: float, lon: float, region: str) -> bool:
    """
    Check if a coordinate point is within a specified region
    
    Args:
        lat: Latitude
        lon: Longitude
        region: Region identifier
        
    Returns:
        True if point is in region, False otherwise
    """
    bounds = get_region_bounds(region)
    if not bounds:
        return False
    
    return (bounds['min_lat'] <= lat <= bounds['max_lat'] and 
            bounds['min_lon'] <= lon <= bounds['max_lon'])

def get_region_center(region: str) -> Optional[Tuple[float, float]]:
    """
    Get center coordinates for a region
    
    Args:
        region: Region identifier
        
    Returns:
        Tuple of (latitude, longitude) or None if region not found
    """
    bounds = get_region_bounds(region)
    if not bounds:
        return None
    
    center_lat = (bounds['min_lat'] + bounds['max_lat']) / 2
    center_lon = (bounds['min_lon'] + bounds['max_lon']) / 2
    
    return (center_lat, center_lon)

def get_available_regions() -> Dict[str, str]:
    """
    Get list of available regions with display names
    
    Returns:
        Dictionary mapping region codes to display names
    """
    return {
        'all-northern-india': 'All of Northern India',
        'punjab': 'Punjab',
        'haryana': 'Haryana',
        'uttar-pradesh': 'Uttar Pradesh',
        'delhi': 'Delhi NCR',
        'rajasthan': 'Rajasthan',
        'himachal-pradesh': 'Himachal Pradesh',
        'uttarakhand': 'Uttarakhand',
        'chandigarh': 'Chandigarh Area',
        'amritsar': 'Amritsar Area',
        'ludhiana': 'Ludhiana Area',
        'gurgaon': 'Gurgaon Area'
    }