import requests
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from app.models.prediction import WeatherData
import json

class WeatherService:
    def __init__(self, api_key: Optional[str] = None):
        # Using OpenWeatherMap API (free tier)
        # For production, get API key from: https://openweathermap.org/api
        self.api_key = api_key or "demo_key"  # Replace with real API key
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
    async def get_current_weather(self, latitude: float, longitude: float) -> Optional[WeatherData]:
        """Get current weather data for a location"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": self.api_key,
                "units": "metric"
            }
            
            # For demo purposes, return simulated data if API key is demo
            if self.api_key == "demo_key":
                return self._generate_demo_weather(latitude, longitude)
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return WeatherData(
                temperature=data["main"]["temp"],
                humidity=data["main"]["humidity"],
                wind_speed=data["wind"].get("speed", 0),
                wind_direction=data["wind"].get("deg", 0),
                precipitation=data.get("rain", {}).get("1h", 0),
                pressure=data["main"]["pressure"],
                visibility=data.get("visibility", 10000) / 1000,  # Convert to km
                weather_condition=data["weather"][0]["main"],
                location=f"{latitude:.4f},{longitude:.4f}",
                timestamp=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return self._generate_demo_weather(latitude, longitude)
    
    async def get_weather_forecast(self, latitude: float, longitude: float, days: int = 7) -> List[WeatherData]:
        """Get weather forecast for next N days"""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": self.api_key,
                "units": "metric",
                "cnt": min(days * 8, 40)  # 8 forecasts per day (3-hour intervals), max 40
            }
            
            # For demo purposes, return simulated data
            if self.api_key == "demo_key":
                return self._generate_demo_forecast(latitude, longitude, days)
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            forecasts = []
            for item in data["list"]:
                forecast = WeatherData(
                    temperature=item["main"]["temp"],
                    humidity=item["main"]["humidity"],
                    wind_speed=item["wind"].get("speed", 0),
                    wind_direction=item["wind"].get("deg", 0),
                    precipitation=item.get("rain", {}).get("3h", 0),
                    pressure=item["main"]["pressure"],
                    visibility=item.get("visibility", 10000) / 1000,
                    weather_condition=item["weather"][0]["main"],
                    location=f"{latitude:.4f},{longitude:.4f}",
                    timestamp=item["dt_txt"]
                )
                forecasts.append(forecast)
            
            return forecasts
            
        except Exception as e:
            print(f"Error fetching weather forecast: {e}")
            return self._generate_demo_forecast(latitude, longitude, days)
    
    def calculate_fire_risk_score(self, weather: WeatherData) -> float:
        """Calculate fire risk score based on weather conditions (0-100)"""
        # Higher temperature increases risk
        temp_score = min((weather.temperature - 15) / 25 * 40, 40)  # Max 40 points
        temp_score = max(temp_score, 0)
        
        # Lower humidity increases risk
        humidity_score = max((100 - weather.humidity) / 100 * 30, 0)  # Max 30 points
        
        # Higher wind speed increases risk
        wind_score = min(weather.wind_speed / 20 * 20, 20)  # Max 20 points
        
        # No precipitation increases risk
        precip_score = max((10 - weather.precipitation) / 10 * 10, 0)  # Max 10 points
        
        total_score = temp_score + humidity_score + wind_score + precip_score
        return min(total_score, 100)
    
    def get_weather_factors(self, weather: WeatherData) -> List[str]:
        """Get list of weather factors contributing to fire risk"""
        factors = []
        
        if weather.temperature > 30:
            factors.append("high temperature forecast")
        if weather.humidity < 30:
            factors.append("low humidity")
        if weather.wind_speed > 15:
            factors.append("strong wind conditions")
        if weather.precipitation < 1:
            factors.append("dry weather forecast")
        if weather.weather_condition in ["Clear", "Clouds"]:
            factors.append("clear/partly cloudy conditions")
            
        return factors
    
    def _generate_demo_weather(self, latitude: float, longitude: float) -> WeatherData:
        """Generate realistic demo weather data for Northern India"""
        import random
        
        # Simulate typical Northern India weather during stubble burning season
        base_temp = 25 + random.uniform(-5, 15)  # 20-40°C range
        base_humidity = 40 + random.uniform(-20, 40)  # 20-80% range
        
        return WeatherData(
            temperature=round(base_temp, 1),
            humidity=round(max(10, min(90, base_humidity)), 1),
            wind_speed=round(random.uniform(5, 25), 1),
            wind_direction=round(random.uniform(0, 360), 0),
            precipitation=round(random.uniform(0, 5), 1),
            pressure=round(1010 + random.uniform(-15, 15), 1),
            visibility=round(random.uniform(5, 15), 1),
            weather_condition=random.choice(["Clear", "Clouds", "Haze", "Mist"]),
            location=f"{latitude:.4f},{longitude:.4f}",
            timestamp=datetime.utcnow().isoformat()
        )
    
    def _generate_demo_forecast(self, latitude: float, longitude: float, days: int) -> List[WeatherData]:
        """Generate demo forecast data"""
        forecasts = []
        
        for i in range(days):
            future_date = datetime.utcnow() + timedelta(days=i)
            weather = self._generate_demo_weather(latitude, longitude)
            weather.timestamp = future_date.isoformat()
            forecasts.append(weather)
            
        return forecasts