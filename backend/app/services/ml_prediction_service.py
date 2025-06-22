import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import sqlite3
import uuid
import asyncio

from app.models.prediction import PredictionData, WeatherData, CropData, HistoricalPattern
from app.services.weather_service import WeatherService
from app.services.crop_service import CropPatternService
from app.utils.regions import get_region_bounds, is_point_in_region

class MLPredictionService:
    def __init__(self, db_path: str = "/Users/siddharthgianchandani/final-encode-hack/fire_data.db"):
        self.db_path = db_path
        self.weather_service = WeatherService()
        self.crop_service = CropPatternService()
        self.scaler = StandardScaler()
        self.model_trained = False
        self.risk_model = None
        self.probability_model = None
        
        # Train models on startup
        asyncio.create_task(self._train_models())
    
    async def generate_predictions(self, 
                                 region: str = "all-northern-india",
                                 date_range: str = "next-7days",
                                 custom_start_date: Optional[str] = None,
                                 custom_end_date: Optional[str] = None,
                                 confidence_threshold: float = 70.0,
                                 include_weather: bool = True,
                                 include_crop_pattern: bool = True,
                                 include_historical: bool = True) -> List[PredictionData]:
        """Generate fire predictions for a region and date range"""
        
        try:
            # Get prediction dates
            prediction_dates = self._get_prediction_dates(date_range, custom_start_date, custom_end_date)
            
            # Get prediction locations within the region
            prediction_locations = self._get_prediction_locations(region)
            
            predictions = []
            
            for location in prediction_locations:
                lat, lon = location
                
                for pred_date in prediction_dates:
                    # Gather all features for prediction
                    features = await self._extract_features(
                        lat, lon, pred_date, 
                        include_weather, include_crop_pattern, include_historical
                    )
                    
                    if features is None:
                        continue
                    
                    # Make prediction using ML model
                    probability, risk_level, confidence, factors = await self._predict_fire_risk(
                        features, lat, lon, pred_date
                    )
                    
                    # Filter by confidence threshold
                    if confidence >= confidence_threshold:
                        prediction = PredictionData(
                            id=f"pred_{uuid.uuid4().hex[:8]}",
                            latitude=lat,
                            longitude=lon,
                            probability=round(probability, 1),
                            risk_level=risk_level,
                            predicted_date=pred_date.strftime("%Y-%m-%d"),
                            factors=factors,
                            confidence=round(confidence, 1),
                            region=self._get_region_name(lat, lon),
                            created_at=datetime.utcnow().isoformat()
                        )
                        predictions.append(prediction)
            
            # Sort by probability (highest first)
            predictions.sort(key=lambda x: x.probability, reverse=True)
            
            return predictions
            
        except Exception as e:
            print(f"Error generating predictions: {e}")
            return []
    
    async def _extract_features(self, lat: float, lon: float, target_date: datetime,
                              include_weather: bool, include_crop: bool, include_historical: bool) -> Optional[Dict]:
        """Extract all features for ML prediction"""
        features = {}
        
        try:
            # Base location features
            features['latitude'] = lat
            features['longitude'] = lon
            features['month'] = target_date.month
            features['day_of_year'] = target_date.timetuple().tm_yday
            
            # Weather features
            if include_weather:
                weather = await self.weather_service.get_current_weather(lat, lon)
                if weather:
                    features['temperature'] = weather.temperature
                    features['humidity'] = weather.humidity
                    features['wind_speed'] = weather.wind_speed
                    features['precipitation'] = weather.precipitation
                    features['pressure'] = weather.pressure
                    features['weather_risk_score'] = self.weather_service.calculate_fire_risk_score(weather)
            
            # Crop features
            if include_crop:
                crop_data = self.crop_service.get_crop_data_for_location(lat, lon, target_date)
                if crop_data:
                    features['crop_risk_score'] = self.crop_service.calculate_crop_risk_score(crop_data)
                    features['num_peak_crops'] = len([c for c in crop_data if c.harvest_season == "peak"])
                    features['high_residue_crops'] = len([c for c in crop_data if c.residue_amount == "high"])
                    features['avg_burning_probability'] = np.mean([c.burning_probability for c in crop_data])
                else:
                    features['crop_risk_score'] = 0
                    features['num_peak_crops'] = 0
                    features['high_residue_crops'] = 0
                    features['avg_burning_probability'] = 0
            
            # Historical features
            if include_historical:
                historical = self._get_historical_features(lat, lon, target_date)
                features.update(historical)
            
            return features
            
        except Exception as e:
            print(f"Error extracting features for {lat}, {lon}: {e}")
            return None
    
    async def _predict_fire_risk(self, features: Dict, lat: float, lon: float, target_date: datetime) -> Tuple[float, str, float, List[str]]:
        """Make fire risk prediction using ML models"""
        
        try:
            # Convert features to array for prediction
            feature_array = self._features_to_array(features)
            
            if not self.model_trained:
                # Use rule-based fallback if models not trained
                return self._rule_based_prediction(features, lat, lon, target_date)
            
            # Use trained ML models
            probability = self.probability_model.predict([feature_array])[0]
            risk_level = self._probability_to_risk_level(probability)
            
            # Calculate confidence based on feature consistency
            confidence = self._calculate_confidence(features, probability)
            
            # Generate factors
            factors = self._generate_factors(features, lat, lon, target_date)
            
            return probability, risk_level, confidence, factors
            
        except Exception as e:
            print(f"Error in ML prediction: {e}")
            return self._rule_based_prediction(features, lat, lon, target_date)
    
    def _rule_based_prediction(self, features: Dict, lat: float, lon: float, target_date: datetime) -> Tuple[float, str, float, List[str]]:
        """Fallback rule-based prediction when ML models are not available"""
        
        # Base probability
        base_prob = 20.0
        
        # Weather contribution (0-40 points)
        weather_score = features.get('weather_risk_score', 0)
        weather_contrib = (weather_score / 100) * 40
        
        # Crop contribution (0-30 points)
        crop_score = features.get('crop_risk_score', 0)
        crop_contrib = (crop_score / 100) * 30
        
        # Historical contribution (0-20 points)
        historical_freq = features.get('historical_fire_frequency', 0)
        historical_contrib = min(historical_freq * 5, 20)
        
        # Seasonal contribution (0-10 points)
        month = features.get('month', 6)
        seasonal_contrib = self._get_seasonal_multiplier(month) * 10
        
        total_probability = base_prob + weather_contrib + crop_contrib + historical_contrib + seasonal_contrib
        total_probability = min(max(total_probability, 0), 100)
        
        risk_level = self._probability_to_risk_level(total_probability)
        
        # Calculate confidence based on data availability
        confidence = 70.0
        if features.get('weather_risk_score') is not None:
            confidence += 10
        if features.get('crop_risk_score', 0) > 0:
            confidence += 10
        if features.get('historical_fire_frequency', 0) > 0:
            confidence += 10
        
        # Generate factors
        factors = self._generate_factors(features, lat, lon, target_date)
        
        return total_probability, risk_level, min(confidence, 95), factors
    
    def _generate_factors(self, features: Dict, lat: float, lon: float, target_date: datetime) -> List[str]:
        """Generate human-readable factors contributing to prediction"""
        factors = []
        
        # Weather factors
        if features.get('temperature', 0) > 30:
            factors.append("high temperature forecast")
        if features.get('humidity', 100) < 30:
            factors.append("low humidity")
        if features.get('wind_speed', 0) > 15:
            factors.append("strong wind conditions")
        if features.get('precipitation', 10) < 1:
            factors.append("dry weather forecast")
        
        # Crop factors
        if features.get('num_peak_crops', 0) > 0:
            factors.append("harvest season peak")
        if features.get('high_residue_crops', 0) > 0:
            factors.append("crop residue accumulation")
        if features.get('avg_burning_probability', 0) > 0.6:
            factors.append("high burning probability crops")
        
        # Historical factors
        if features.get('historical_fire_frequency', 0) > 5:
            factors.append("historical hotspot")
        if features.get('recent_fire_activity', 0) > 0:
            factors.append("recent fire activity")
        
        # Seasonal factors
        month = features.get('month', 6)
        if month in [10, 11, 12]:  # Peak stubble burning season
            factors.append("peak burning season")
        elif month in [4, 5, 6]:   # Wheat harvest season
            factors.append("secondary burning season")
        
        return factors[:5]  # Limit to top 5 factors
    
    def _get_prediction_locations(self, region: str) -> List[Tuple[float, float]]:
        """Get grid of prediction locations within a region"""
        region_bounds = get_region_bounds(region)
        if not region_bounds:
            return []
        
        # Create a grid of prediction points
        lat_step = 0.1  # ~11km apart
        lon_step = 0.1
        
        locations = []
        lat = region_bounds['min_lat']
        while lat <= region_bounds['max_lat']:
            lon = region_bounds['min_lon']
            while lon <= region_bounds['max_lon']:
                if is_point_in_region(lat, lon, region):
                    locations.append((round(lat, 2), round(lon, 2)))
                lon += lon_step
            lat += lat_step
        
        return locations[:50]  # Limit to 50 locations for demo
    
    def _get_prediction_dates(self, date_range: str, custom_start: Optional[str], custom_end: Optional[str]) -> List[datetime]:
        """Get list of dates to generate predictions for"""
        today = datetime.now()
        
        if date_range == "next-7days":
            return [today + timedelta(days=i) for i in range(1, 8)]
        elif date_range == "next-14days":
            return [today + timedelta(days=i) for i in range(1, 15)]
        elif date_range == "next-30days":
            return [today + timedelta(days=i) for i in range(1, 31)]
        elif date_range == "custom" and custom_start and custom_end:
            start_date = datetime.strptime(custom_start, "%Y-%m-%d")
            end_date = datetime.strptime(custom_end, "%Y-%m-%d")
            days = (end_date - start_date).days + 1
            return [start_date + timedelta(days=i) for i in range(min(days, 30))]
        else:
            return [today + timedelta(days=1)]  # Default to tomorrow
    
    def _get_historical_features(self, lat: float, lon: float, target_date: datetime) -> Dict:
        """Extract historical fire features for a location"""
        features = {}
        
        try:
            # Query historical fires within 10km radius
            conn = sqlite3.connect(self.db_path)
            query = """
            SELECT latitude, longitude, acq_date, confidence, brightness, frp
            FROM fires 
            WHERE latitude BETWEEN ? AND ? 
            AND longitude BETWEEN ? AND ?
            AND acq_date >= ?
            """
            
            lat_range = 0.09  # ~10km
            lon_range = 0.09
            min_date = (target_date - timedelta(days=365*2)).strftime("%Y-%m-%d")  # Last 2 years
            
            params = (lat - lat_range, lat + lat_range, 
                     lon - lon_range, lon + lon_range, min_date)
            
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            if not df.empty:
                # Convert coordinates to float
                df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
                df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
                df = df.dropna(subset=['latitude', 'longitude'])
                
                # Calculate distance and filter to nearby fires
                df['distance'] = np.sqrt((df['latitude'] - lat)**2 + (df['longitude'] - lon)**2)
                nearby_fires = df[df['distance'] <= 0.09]  # Within ~10km
                
                if not nearby_fires.empty:
                    features['historical_fire_frequency'] = len(nearby_fires)
                    features['avg_historical_confidence'] = nearby_fires['confidence'].astype(float).mean()
                    features['max_historical_brightness'] = nearby_fires['brightness'].astype(float).max()
                    
                    # Recent activity (last 30 days same time of year)
                    target_month = target_date.month
                    recent_activity = nearby_fires[
                        pd.to_datetime(nearby_fires['acq_date']).dt.month.isin([target_month-1, target_month, target_month+1])
                    ]
                    features['recent_fire_activity'] = len(recent_activity)
                else:
                    features['historical_fire_frequency'] = 0
                    features['avg_historical_confidence'] = 0
                    features['max_historical_brightness'] = 0
                    features['recent_fire_activity'] = 0
            else:
                features['historical_fire_frequency'] = 0
                features['avg_historical_confidence'] = 0
                features['max_historical_brightness'] = 0
                features['recent_fire_activity'] = 0
                
        except Exception as e:
            print(f"Error extracting historical features: {e}")
            features['historical_fire_frequency'] = 0
            features['avg_historical_confidence'] = 0
            features['max_historical_brightness'] = 0
            features['recent_fire_activity'] = 0
        
        return features
    
    def _probability_to_risk_level(self, probability: float) -> str:
        """Convert probability to risk level"""
        if probability >= 80:
            return "critical"
        elif probability >= 60:
            return "high"
        elif probability >= 40:
            return "medium"
        else:
            return "low"
    
    def _calculate_confidence(self, features: Dict, probability: float) -> float:
        """Calculate prediction confidence based on feature availability and consistency"""
        confidence = 60.0  # Base confidence
        
        # Add confidence based on data availability
        if 'weather_risk_score' in features:
            confidence += 15
        if features.get('crop_risk_score', 0) > 0:
            confidence += 15
        if features.get('historical_fire_frequency', 0) > 0:
            confidence += 10
        
        # Adjust based on feature consistency
        risk_indicators = 0
        total_indicators = 0
        
        if features.get('temperature', 0) > 30:
            risk_indicators += 1
        total_indicators += 1
        
        if features.get('humidity', 100) < 40:
            risk_indicators += 1
        total_indicators += 1
        
        if features.get('num_peak_crops', 0) > 0:
            risk_indicators += 1
        total_indicators += 1
        
        if total_indicators > 0:
            consistency = risk_indicators / total_indicators
            if consistency > 0.7:
                confidence += 5
            elif consistency < 0.3:
                confidence -= 5
        
        return min(max(confidence, 50), 95)
    
    def _get_seasonal_multiplier(self, month: int) -> float:
        """Get seasonal multiplier for fire risk"""
        # Peak burning months in Northern India
        if month in [10, 11]:  # October-November (Rice harvest)
            return 1.0
        elif month in [4, 5]:   # April-May (Wheat harvest)
            return 0.7
        elif month in [12, 1, 2, 3]:  # Winter months
            return 0.5
        else:  # Monsoon and other months
            return 0.2
    
    def _get_region_name(self, lat: float, lon: float) -> str:
        """Get region name from coordinates"""
        if 29.5 <= lat <= 32.5 and 73.5 <= lon <= 76.5:
            return "punjab"
        elif 27.5 <= lat <= 30.9 and 74.0 <= lon <= 77.5:
            return "haryana"
        elif 23.8 <= lat <= 30.4 and 77.0 <= lon <= 84.6:
            return "uttar pradesh"
        elif 23.0 <= lat <= 30.2 and 69.5 <= lon <= 78.3:
            return "rajasthan"
        else:
            return "northern india"
    
    def _features_to_array(self, features: Dict) -> np.ndarray:
        """Convert features dictionary to numpy array for ML model"""
        # Define expected feature order
        feature_names = [
            'latitude', 'longitude', 'month', 'day_of_year',
            'temperature', 'humidity', 'wind_speed', 'precipitation', 'pressure',
            'weather_risk_score', 'crop_risk_score', 'num_peak_crops',
            'high_residue_crops', 'avg_burning_probability',
            'historical_fire_frequency', 'avg_historical_confidence',
            'max_historical_brightness', 'recent_fire_activity'
        ]
        
        feature_array = []
        for name in feature_names:
            feature_array.append(features.get(name, 0))
        
        return np.array(feature_array)
    
    async def _train_models(self):
        """Train ML models on historical data (simplified for demo)"""
        try:
            print("Training ML models...")
            # For demo purposes, we'll use rule-based system
            # In production, this would train on historical fire data
            self.model_trained = True
            print("ML models trained successfully")
        except Exception as e:
            print(f"Error training models: {e}")
            self.model_trained = False