from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from app.models.prediction import CropData
import calendar

class CropPatternService:
    def __init__(self):
        # Northern India crop patterns and burning seasons
        self.crop_patterns = {
            "punjab": {
                "rice": {
                    "harvest_months": [10, 11],  # October-November
                    "burning_peak": [11, 12],    # November-December
                    "area_percentage": 60,
                    "burning_probability": 0.85
                },
                "wheat": {
                    "harvest_months": [4, 5],    # April-May
                    "burning_peak": [5, 6],      # May-June
                    "area_percentage": 35,
                    "burning_probability": 0.45
                },
                "sugarcane": {
                    "harvest_months": [12, 1, 2, 3],  # Dec-March
                    "burning_peak": [2, 3],      # February-March
                    "area_percentage": 5,
                    "burning_probability": 0.30
                }
            },
            "haryana": {
                "rice": {
                    "harvest_months": [10, 11],
                    "burning_peak": [11, 12],
                    "area_percentage": 45,
                    "burning_probability": 0.75
                },
                "wheat": {
                    "harvest_months": [4, 5],
                    "burning_peak": [5, 6],
                    "area_percentage": 50,
                    "burning_probability": 0.40
                },
                "mustard": {
                    "harvest_months": [3, 4],
                    "burning_peak": [4, 5],
                    "area_percentage": 5,
                    "burning_probability": 0.35
                }
            },
            "uttar-pradesh": {
                "rice": {
                    "harvest_months": [10, 11, 12],
                    "burning_peak": [11, 12],
                    "area_percentage": 40,
                    "burning_probability": 0.65
                },
                "wheat": {
                    "harvest_months": [4, 5],
                    "burning_peak": [5, 6],
                    "area_percentage": 45,
                    "burning_probability": 0.35
                },
                "sugarcane": {
                    "harvest_months": [12, 1, 2, 3],
                    "burning_peak": [2, 3],
                    "area_percentage": 15,
                    "burning_probability": 0.25
                }
            },
            "rajasthan": {
                "wheat": {
                    "harvest_months": [3, 4, 5],
                    "burning_peak": [4, 5],
                    "area_percentage": 60,
                    "burning_probability": 0.30
                },
                "mustard": {
                    "harvest_months": [3, 4],
                    "burning_peak": [4, 5],
                    "area_percentage": 25,
                    "burning_probability": 0.40
                },
                "barley": {
                    "harvest_months": [3, 4],
                    "burning_peak": [4, 5],
                    "area_percentage": 15,
                    "burning_probability": 0.25
                }
            }
        }
    
    def get_crop_data_for_location(self, latitude: float, longitude: float, target_date: datetime = None) -> List[CropData]:
        """Get crop data for a specific location and date"""
        if target_date is None:
            target_date = datetime.now()
        
        region = self._get_region_from_coordinates(latitude, longitude)
        if not region or region not in self.crop_patterns:
            return []
        
        crop_data_list = []
        current_month = target_date.month
        
        for crop_name, crop_info in self.crop_patterns[region].items():
            # Determine if we're in harvest or burning season
            harvest_season = self._get_season_status(current_month, crop_info["harvest_months"])
            burning_season = self._get_season_status(current_month, crop_info["burning_peak"])
            
            # Calculate burning probability based on season
            base_probability = crop_info["burning_probability"]
            if burning_season == "peak":
                burning_probability = base_probability * 1.0
            elif burning_season == "active":
                burning_probability = base_probability * 0.7
            elif harvest_season == "peak":
                burning_probability = base_probability * 0.5
            elif harvest_season == "active":
                burning_probability = base_probability * 0.3
            else:
                burning_probability = base_probability * 0.1
            
            # Determine residue amount based on area percentage and season
            if crop_info["area_percentage"] > 50:
                residue_amount = "high"
            elif crop_info["area_percentage"] > 25:
                residue_amount = "medium"
            else:
                residue_amount = "low"
                
            # Increase residue during harvest season
            if harvest_season in ["peak", "active"]:
                if residue_amount == "low":
                    residue_amount = "medium"
                elif residue_amount == "medium":
                    residue_amount = "high"
            
            crop_data = CropData(
                crop_type=crop_name,
                harvest_season=harvest_season,
                burning_probability=round(burning_probability, 3),
                residue_amount=residue_amount,
                area_hectares=self._estimate_area_hectares(crop_info["area_percentage"], region),
                location=f"{latitude:.4f},{longitude:.4f}"
            )
            
            crop_data_list.append(crop_data)
        
        return crop_data_list
    
    def calculate_crop_risk_score(self, crop_data_list: List[CropData]) -> float:
        """Calculate overall crop-based fire risk score (0-100)"""
        if not crop_data_list:
            return 0
        
        total_score = 0
        total_weight = 0
        
        for crop in crop_data_list:
            # Base score from burning probability
            base_score = crop.burning_probability * 100
            
            # Weight by area (more area = higher impact)
            area_weight = min(crop.area_hectares / 10000, 1.0)  # Normalize to max 1.0
            
            # Adjust by residue amount
            residue_multiplier = {
                "high": 1.2,
                "medium": 1.0,
                "low": 0.7
            }.get(crop.residue_amount, 1.0)
            
            # Season multiplier
            season_multiplier = {
                "peak": 1.3,
                "active": 1.0,
                "off": 0.5
            }.get(crop.harvest_season, 0.5)
            
            crop_score = base_score * residue_multiplier * season_multiplier
            weighted_score = crop_score * area_weight
            
            total_score += weighted_score
            total_weight += area_weight
        
        if total_weight > 0:
            return min(total_score / total_weight, 100)
        return 0
    
    def get_crop_factors(self, crop_data_list: List[CropData]) -> List[str]:
        """Get list of crop-related factors contributing to fire risk"""
        factors = []
        
        peak_crops = [crop for crop in crop_data_list if crop.harvest_season == "peak"]
        high_residue_crops = [crop for crop in crop_data_list if crop.residue_amount == "high"]
        high_prob_crops = [crop for crop in crop_data_list if crop.burning_probability > 0.6]
        
        if peak_crops:
            factors.append("harvest season peak")
        
        if high_residue_crops:
            factors.append("crop residue accumulation")
        
        if high_prob_crops:
            factors.append("high burning probability crops")
        
        # Check for specific crop patterns
        rice_crops = [crop for crop in crop_data_list if crop.crop_type == "rice" and crop.harvest_season in ["peak", "active"]]
        if rice_crops:
            factors.append("rice harvest season")
        
        wheat_crops = [crop for crop in crop_data_list if crop.crop_type == "wheat" and crop.harvest_season in ["peak", "active"]]
        if wheat_crops:
            factors.append("wheat harvest season")
        
        return factors
    
    def _get_region_from_coordinates(self, latitude: float, longitude: float) -> str:
        """Determine region based on coordinates"""
        # Simplified region detection based on coordinate ranges
        if 29.5 <= latitude <= 32.5 and 73.5 <= longitude <= 76.5:
            return "punjab"
        elif 27.5 <= latitude <= 30.9 and 74.0 <= longitude <= 77.5:
            return "haryana"
        elif 23.8 <= latitude <= 30.4 and 77.0 <= longitude <= 84.6:
            return "uttar-pradesh"
        elif 23.0 <= latitude <= 30.2 and 69.5 <= longitude <= 78.3:
            return "rajasthan"
        else:
            return "unknown"
    
    def _get_season_status(self, current_month: int, season_months: List[int]) -> str:
        """Determine if current month is in peak, active, or off season"""
        if current_month in season_months:
            return "peak"
        
        # Check if within 1 month of season
        extended_months = []
        for month in season_months:
            extended_months.extend([month - 1, month + 1])
        
        # Handle year boundaries
        extended_months = [(m % 12) or 12 for m in extended_months]
        
        if current_month in extended_months:
            return "active"
        
        return "off"
    
    def _estimate_area_hectares(self, area_percentage: float, region: str) -> float:
        """Estimate actual hectares based on percentage and region"""
        # Rough estimates of agricultural area by region (in hectares)
        region_areas = {
            "punjab": 4200000,
            "haryana": 3600000,
            "uttar-pradesh": 17500000,
            "rajasthan": 20000000
        }
        
        total_area = region_areas.get(region, 5000000)
        return (area_percentage / 100) * total_area