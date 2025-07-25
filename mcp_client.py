#!/usr/bin/env python3
"""
MCP Client for communicating with the Weather MCP Server
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, Optional
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPClient:
    """MCP Client for communicating with MCP servers"""
    
    def __init__(self, server_url: str = None):
        self.server_url = server_url or f"http://{os.getenv('MCP_SERVER_HOST', 'localhost')}:{os.getenv('MCP_SERVER_PORT', '8000')}"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to the MCP server"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        request_data = {
            "method": method,
            "params": params or {}
        }
        
        try:
            async with self.session.post(f"{self.server_url}/mcp", json=request_data) as response:
                response.raise_for_status()
                result = await response.json()
                return result
        except aiohttp.ClientError as e:
            logger.error(f"Error making request to MCP server: {e}")
            return {"error": f"Failed to connect to MCP server: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"error": f"Unexpected error: {str(e)}"}
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get server capabilities"""
        try:
            async with self.session.get(f"{self.server_url}/capabilities") as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Error getting capabilities: {e}")
            return {"error": f"Failed to get capabilities: {str(e)}"}
    
    async def get_current_weather(self, city: str, country_code: Optional[str] = None) -> Dict[str, Any]:
        """Get current weather for a city"""
        params = {"city": city}
        if country_code:
            params["country_code"] = country_code
        
        return await self._make_request("weather/get_current", params)
    
    async def get_weather_forecast(self, city: str, country_code: Optional[str] = None, days: int = 5) -> Dict[str, Any]:
        """Get weather forecast for a city"""
        params = {"city": city, "days": days}
        if country_code:
            params["country_code"] = country_code
        
        return await self._make_request("weather/get_forecast", params)

class WeatherService:
    """High-level weather service using MCP client"""
    
    def __init__(self, server_url: str = None):
        self.server_url = server_url
    
    async def get_weather_info(self, city: str, country_code: Optional[str] = None) -> str:
        """Get formatted weather information for a city"""
        async with MCPClient(self.server_url) as client:
            result = await client.get_current_weather(city, country_code)
            
            if "error" in result:
                return f"Error getting weather: {result['error']}"
            
            weather_data = result.get("result", {})
            if "error" in weather_data:
                return f"Weather service error: {weather_data['error']}"
            
            # Format the weather information
            temp = weather_data["temperature"]["current"]
            feels_like = weather_data["temperature"]["feels_like"]
            description = weather_data["description"]
            humidity = weather_data["humidity"]
            wind_speed = weather_data["wind"]["speed"]
            
            weather_info = f"""
Current weather in {weather_data['city']}, {weather_data['country']}:
• Temperature: {temp}°C (feels like {feels_like}°C)
• Conditions: {description}
• Humidity: {humidity}%
• Wind Speed: {wind_speed} m/s
"""
            return weather_info.strip()
    
    async def get_forecast_info(self, city: str, country_code: Optional[str] = None, days: int = 3) -> str:
        """Get formatted forecast information for a city"""
        async with MCPClient(self.server_url) as client:
            result = await client.get_weather_forecast(city, country_code, days)
            
            if "error" in result:
                return f"Error getting forecast: {result['error']}"
            
            forecast_data = result.get("result", {})
            if "error" in forecast_data:
                return f"Forecast service error: {forecast_data['error']}"
            
            # Format the forecast information
            forecast_info = f"Weather forecast for {forecast_data['city']}, {forecast_data['country']}:\n\n"
            
            # Group by day
            daily_forecasts = {}
            for item in forecast_data["forecast"]:
                date = item["datetime"].split()[0]  # Get just the date part
                if date not in daily_forecasts:
                    daily_forecasts[date] = []
                daily_forecasts[date].append(item)
            
            for date, forecasts in list(daily_forecasts.items())[:days]:
                # Get average/min/max for the day
                temps = [f["temperature"]["current"] for f in forecasts]
                avg_temp = sum(temps) / len(temps)
                min_temp = min(temps)
                max_temp = max(temps)
                
                # Get most common description
                descriptions = [f["description"] for f in forecasts]
                most_common_desc = max(set(descriptions), key=descriptions.count)
                
                forecast_info += f"📅 {date}:\n"
                forecast_info += f"   Temperature: {avg_temp:.1f}°C (min: {min_temp:.1f}°C, max: {max_temp:.1f}°C)\n"
                forecast_info += f"   Conditions: {most_common_desc}\n\n"
            
            return forecast_info.strip()

# Example usage
async def test_weather_service():
    """Test the weather service"""
    weather_service = WeatherService()
    
    print("Testing weather service...")
    
    # Test current weather
    weather_info = await weather_service.get_weather_info("London", "GB")
    print("Current Weather:")
    print(weather_info)
    print("\n" + "="*50 + "\n")
    
    # Test forecast
    forecast_info = await weather_service.get_forecast_info("London", "GB", 3)
    print("Forecast:")
    print(forecast_info)

if __name__ == "__main__":
    asyncio.run(test_weather_service()) 