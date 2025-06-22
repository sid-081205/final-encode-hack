import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import uuid
import time

from app.models.prediction import PredictionData
from app.utils.regions import get_region_bounds, is_point_in_region

class SimplePredictionService:
    def __init__(self, db_path: str = "/Users/siddharthgianchandani/final-encode-hack/fire_data.db"):
        self.db_path = db_path
        
    def generate_predictions(self, 
                           region: str = "all-northern-india",
                           date_range: str = "next-7days",
                           custom_start_date: str = None,
                           custom_end_date: str = None,
                           confidence_threshold: float = 70.0) -> List[PredictionData]:
        """Generate fire predictions based on historical patterns"""
        
        try:
            print(f"Starting prediction generation for {region}...")
            
            # Get prediction dates
            prediction_dates = self._get_prediction_dates(date_range, custom_start_date, custom_end_date)
            print(f"Predicting for {len(prediction_dates)} days")
            
            # Load and analyze historical data
            historical_data = self._load_historical_data(region)
            print(f"Loaded {len(historical_data)} historical fire records")
            
            if historical_data.empty:
                print("No historical data found for region")
                return []
            
            # Analyze patterns
            fire_patterns = self._analyze_fire_patterns(historical_data)
            print(f"Identified {len(fire_patterns)} fire pattern locations")
            
            # Generate predictions for each pattern and date
            all_predictions = []
            
            for pattern in fire_patterns:
                for pred_date in prediction_dates:
                    prediction = self._create_prediction_from_pattern(pattern, pred_date, region)
                    
                    if prediction:  # Generate all predictions regardless of confidence threshold
                        all_predictions.append(prediction)
            
            # Sort by probability (highest first) and prioritize Punjab region
            # Separate Punjab predictions and others
            punjab_predictions = [p for p in all_predictions if 'punjab' in p.region.lower()]
            other_predictions = [p for p in all_predictions if 'punjab' not in p.region.lower()]
            
            # Sort both groups by probability
            punjab_predictions.sort(key=lambda x: x.probability, reverse=True)
            other_predictions.sort(key=lambda x: x.probability, reverse=True)
            
            # Create a gradient of confidence levels
            # Take high confidence predictions from Punjab
            high_conf_punjab = [p for p in punjab_predictions if p.confidence >= confidence_threshold][:25]
            med_conf_punjab = [p for p in punjab_predictions if 50 <= p.confidence < confidence_threshold][:15]
            low_conf_punjab = [p for p in punjab_predictions if p.confidence < 50][:10]
            
            # Take predictions from other regions
            high_conf_other = [p for p in other_predictions if p.confidence >= confidence_threshold][:15]
            med_conf_other = [p for p in other_predictions if 50 <= p.confidence < confidence_threshold][:10]
            low_conf_other = [p for p in other_predictions if p.confidence < 50][:5]
            
            # Combine all predictions to create a gradient
            limited_predictions = (high_conf_punjab + med_conf_punjab + low_conf_punjab + 
                                 high_conf_other + med_conf_other + low_conf_other)
            
            # Final sort by confidence and probability
            limited_predictions.sort(key=lambda x: (x.confidence, x.probability), reverse=True)
            limited_predictions = limited_predictions[:80]
            
            # Count predictions by confidence level for logging
            high_conf_count = len([p for p in limited_predictions if p.confidence >= confidence_threshold])
            med_conf_count = len([p for p in limited_predictions if 50 <= p.confidence < confidence_threshold])
            low_conf_count = len([p for p in limited_predictions if p.confidence < 50])
            
            print(f"Generated {len(limited_predictions)} total predictions: {high_conf_count} high confidence ({confidence_threshold}%+), {med_conf_count} medium confidence (50-{confidence_threshold-1}%), {low_conf_count} low confidence (<50%)")
            return limited_predictions
            
        except Exception as e:
            print(f"Error generating predictions: {e}")
            return []
    
    def _load_historical_data(self, region: str) -> pd.DataFrame:
        """Load historical fire data for the region"""
        try:
            # Get region bounds
            region_bounds = get_region_bounds(region)
            if not region_bounds:
                return pd.DataFrame()
            
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            
            # Query fires within region bounds
            query = """
            SELECT latitude, longitude, acq_date, acq_time, confidence, brightness, frp
            FROM fires 
            WHERE latitude BETWEEN ? AND ? 
            AND longitude BETWEEN ? AND ?
            AND acq_date >= ?
            """
            
            # Use last 2 years of data
            min_date = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")
            
            params = (
                region_bounds['min_lat'], region_bounds['max_lat'],
                region_bounds['min_lon'], region_bounds['max_lon'],
                min_date
            )
            
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            if not df.empty:
                # Convert data types
                df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
                df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
                df['confidence'] = pd.to_numeric(df['confidence'], errors='coerce')
                df['brightness'] = pd.to_numeric(df['brightness'], errors='coerce')
                df['frp'] = pd.to_numeric(df['frp'], errors='coerce')
                
                # Remove invalid data
                df = df.dropna(subset=['latitude', 'longitude'])
                
                # Add date parsing
                df['fire_date'] = pd.to_datetime(df['acq_date'])
                df['month'] = df['fire_date'].dt.month
                df['day_of_year'] = df['fire_date'].dt.dayofyear
                
                # Filter to region again to ensure precise bounds
                if region != "all-northern-india":
                    df = df[df.apply(lambda row: is_point_in_region(row['latitude'], row['longitude'], region), axis=1)]
            
            return df
            
        except Exception as e:
            print(f"Error loading historical data: {e}")
            return pd.DataFrame()
    
    def _analyze_fire_patterns(self, historical_data: pd.DataFrame) -> List[Dict]:
        """Analyze historical data to identify fire patterns"""
        patterns = []
        
        # Group fires by approximate location (0.05 degree grid ~ 5.5km)
        historical_data['lat_grid'] = (historical_data['latitude'] / 0.05).round() * 0.05
        historical_data['lon_grid'] = (historical_data['longitude'] / 0.05).round() * 0.05
        
        # Group by grid location
        location_groups = historical_data.groupby(['lat_grid', 'lon_grid'])
        
        for (lat, lon), group in location_groups:
            if len(group) >= 1:  # Include even single fire locations for lower confidence predictions
                
                # Calculate statistics
                fire_count = len(group)
                avg_confidence = group['confidence'].mean()
                avg_brightness = group['brightness'].mean()
                
                # Seasonal analysis
                month_counts = group['month'].value_counts()
                peak_month = month_counts.index[0] if not month_counts.empty else 6
                seasonal_strength = month_counts.iloc[0] / fire_count if not month_counts.empty else 0
                
                # Recent activity
                recent_fires = group[group['fire_date'] > (datetime.now() - timedelta(days=365))]
                recent_activity = len(recent_fires)
                
                # Calculate base probability based on historical frequency
                base_probability = min((fire_count / 24) * 100, 85)  # Max 85% from frequency
                
                pattern = {
                    'latitude': lat,
                    'longitude': lon,
                    'fire_count': fire_count,
                    'avg_confidence': avg_confidence,
                    'avg_brightness': avg_brightness,
                    'peak_month': peak_month,
                    'seasonal_strength': seasonal_strength,
                    'recent_activity': recent_activity,
                    'base_probability': base_probability,
                    'last_fire_date': group['fire_date'].max()
                }
                
                patterns.append(pattern)
        
        # Create a mix of high and low confidence patterns
        # Sort by fire count (most active locations first)
        patterns.sort(key=lambda x: x['fire_count'], reverse=True)
        
        # Take top 100 high-fire-count patterns
        high_confidence_patterns = patterns[:100]
        
        # Also include some lower fire count patterns for variety
        low_confidence_patterns = [p for p in patterns[100:] if p['fire_count'] <= 3]
        low_confidence_patterns = low_confidence_patterns[:50]  # Take up to 50 low confidence
        
        # Combine and return
        all_patterns = high_confidence_patterns + low_confidence_patterns
        return all_patterns[:200]  # Limit to 200 total patterns
    
    def _create_prediction_from_pattern(self, pattern: Dict, pred_date: datetime, region: str) -> PredictionData:
        """Create a prediction from a fire pattern"""
        try:
            # Calculate probability based on pattern and date
            probability = self._calculate_probability(pattern, pred_date)
            
            # Determine risk level
            risk_level = self._probability_to_risk_level(probability)
            
            # Calculate confidence
            confidence = self._calculate_confidence(pattern, pred_date)
            
            # Generate factors
            factors = self._generate_factors(pattern, pred_date)
            
            prediction = PredictionData(
                id=f"hist_{uuid.uuid4().hex[:8]}",
                latitude=round(pattern['latitude'], 4),
                longitude=round(pattern['longitude'], 4),
                probability=round(probability, 1),
                risk_level=risk_level,
                predicted_date=pred_date.strftime("%Y-%m-%d"),
                factors=factors,
                confidence=round(confidence, 1),
                region=self._get_region_name(pattern['latitude'], pattern['longitude']),
                created_at=datetime.utcnow().isoformat()
            )
            
            return prediction
            
        except Exception as e:
            print(f"Error creating prediction: {e}")
            return None
    
    def _calculate_probability(self, pattern: Dict, pred_date: datetime) -> float:
        """Calculate fire probability based on pattern and date"""
        base_prob = pattern['base_probability']
        
        # Seasonal adjustment
        current_month = pred_date.month
        peak_month = pattern['peak_month']
        
        # Higher probability during peak month
        if current_month == peak_month:
            seasonal_multiplier = 1.0 + (pattern['seasonal_strength'] * 0.5)
        elif abs(current_month - peak_month) <= 1 or abs(current_month - peak_month) >= 11:
            seasonal_multiplier = 1.0 + (pattern['seasonal_strength'] * 0.2)
        else:
            seasonal_multiplier = max(0.3, 1.0 - (pattern['seasonal_strength'] * 0.3))
        
        # Recent activity boost
        if pattern['recent_activity'] > 0:
            recent_multiplier = 1.0 + min(pattern['recent_activity'] / 10, 0.3)
        else:
            recent_multiplier = 0.8
        
        # Time since last fire
        days_since_last = (pred_date - pattern['last_fire_date']).days
        if days_since_last < 30:
            recency_multiplier = 0.7  # Lower probability if very recent fire
        elif days_since_last < 365:
            recency_multiplier = 1.0 + (365 - days_since_last) / 365 * 0.2
        else:
            recency_multiplier = 1.0
        
        total_probability = base_prob * seasonal_multiplier * recent_multiplier * recency_multiplier
        
        return min(max(total_probability, 10), 95)  # Keep between 10-95%
    
    def _calculate_confidence(self, pattern: Dict, pred_date: datetime) -> float:
        """Calculate prediction confidence with varied distribution"""
        # Start with a lower base confidence
        base_confidence = 45.0
        
        # Fire count boost - more gradual scaling
        if pattern['fire_count'] >= 15:
            fire_count_boost = 25  # Very high confidence for hotspots
        elif pattern['fire_count'] >= 10:
            fire_count_boost = 15  # Good confidence
        elif pattern['fire_count'] >= 5:
            fire_count_boost = 8   # Medium confidence
        elif pattern['fire_count'] >= 3:
            fire_count_boost = 3   # Low confidence
        else:
            fire_count_boost = 0   # Very low confidence
        
        # Historical confidence boost - more nuanced
        if pattern['avg_confidence'] >= 80:
            confidence_boost = 12
        elif pattern['avg_confidence'] >= 70:
            confidence_boost = 8
        elif pattern['avg_confidence'] >= 60:
            confidence_boost = 4
        elif pattern['avg_confidence'] >= 50:
            confidence_boost = 2
        else:
            confidence_boost = -2  # Actually reduce confidence for low-quality historical data
        
        # Seasonal pattern boost - more gradual
        seasonal_boost = pattern['seasonal_strength'] * 8  # Reduced from 10
        
        # Recent activity boost - more nuanced
        if pattern['recent_activity'] >= 3:
            recent_boost = 8
        elif pattern['recent_activity'] >= 1:
            recent_boost = 4
        else:
            recent_boost = -3  # Reduce confidence if no recent activity
        
        # Time since last fire factor
        days_since_last = (pred_date - pattern['last_fire_date']).days
        if days_since_last < 60:
            recency_boost = 5   # Recent fire increases confidence
        elif days_since_last < 180:
            recency_boost = 2
        elif days_since_last < 365:
            recency_boost = 0
        else:
            recency_boost = -5  # Very old fires reduce confidence
        
        total_confidence = base_confidence + fire_count_boost + confidence_boost + seasonal_boost + recent_boost + recency_boost
        
        # Allow wider range: 35% to 95%
        return min(max(total_confidence, 35), 95)
    
    def _generate_factors(self, pattern: Dict, pred_date: datetime) -> List[str]:
        """Generate human-readable factors"""
        factors = []
        
        if pattern['fire_count'] >= 10:
            factors.append("historical hotspot")
        elif pattern['fire_count'] >= 5:
            factors.append("recurring fire location")
        
        current_month = pred_date.month
        if current_month == pattern['peak_month']:
            factors.append("peak fire season")
        elif abs(current_month - pattern['peak_month']) <= 1:
            factors.append("active fire season")
        
        if pattern['recent_activity'] > 0:
            factors.append("recent fire activity")
        
        if pattern['seasonal_strength'] > 0.5:
            factors.append("strong seasonal pattern")
        
        if pattern['avg_confidence'] > 70:
            factors.append("high-confidence location")
        
        # Month-specific factors
        if current_month in [10, 11, 12]:
            factors.append("stubble burning season")
        elif current_month in [4, 5, 6]:
            factors.append("summer fire season")
        
        return factors[:4]  # Limit to 4 factors
    
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
    
    def _get_prediction_dates(self, date_range: str, custom_start: str, custom_end: str) -> List[datetime]:
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