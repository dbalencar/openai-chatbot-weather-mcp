#!/usr/bin/env python3
"""
MCP Server for Weather Data from OpenWeatherMap API
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherMCPServer:
    """MCP Server that provides weather data from OpenWeatherMap API"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENWEATHER_API_KEY environment variable is required")
        
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
    async def get_weather(self, city: str, country_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current weather for a city
        
        Args:
            city: City name
            country_code: Optional country code (e.g., 'US', 'GB')
            
        Returns:
            Weather data dictionary
        """
        try:
            # Build location string
            location = city
            if country_code:
                location = f"{city},{country_code}"
            
            # Make API request
            url = f"{self.base_url}/weather"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric"  # Use Celsius
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant information
            weather_info = {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": {
                    "current": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "min": data["main"]["temp_min"],
                    "max": data["main"]["temp_max"]
                },
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "description": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"],
                "wind": {
                    "speed": data["wind"]["speed"],
                    "direction": data["wind"].get("deg", "N/A")
                },
                "visibility": data.get("visibility", "N/A"),
                "clouds": data["clouds"]["all"]
            }
            
            return weather_info
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching weather data: {e}")
            return {"error": f"Failed to fetch weather data: {str(e)}"}
        except KeyError as e:
            logger.error(f"Unexpected API response format: {e}")
            return {"error": "Unexpected API response format"}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"error": f"Unexpected error: {str(e)}"}
    
    async def get_forecast(self, city: str, country_code: Optional[str] = None, days: int = 5) -> Dict[str, Any]:
        """
        Get weather forecast for a city
        
        Args:
            city: City name
            country_code: Optional country code
            days: Number of days for forecast (max 5)
            
        Returns:
            Forecast data dictionary
        """
        try:
            # Build location string
            location = city
            if country_code:
                location = f"{city},{country_code}"
            
            # Make API request
            url = f"{self.base_url}/forecast"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric",
                "cnt": min(days * 8, 40)  # 8 forecasts per day, max 40
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Process forecast data
            forecast_data = []
            for item in data["list"]:
                forecast_item = {
                    "datetime": item["dt_txt"],
                    "temperature": {
                        "current": item["main"]["temp"],
                        "feels_like": item["main"]["feels_like"],
                        "min": item["main"]["temp_min"],
                        "max": item["main"]["temp_max"]
                    },
                    "humidity": item["main"]["humidity"],
                    "description": item["weather"][0]["description"],
                    "icon": item["weather"][0]["icon"],
                    "wind_speed": item["wind"]["speed"],
                    "clouds": item["clouds"]["all"]
                }
                forecast_data.append(forecast_item)
            
            return {
                "city": data["city"]["name"],
                "country": data["city"]["country"],
                "forecast": forecast_data
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching forecast data: {e}")
            return {"error": f"Failed to fetch forecast data: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"error": f"Unexpected error: {str(e)}"}

# MCP Protocol Implementation
class MCPWeatherServer:
    """MCP Server implementation for weather data"""
    
    def __init__(self):
        self.weather_service = WeatherMCPServer()
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP requests"""
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "weather/get_current":
            city = params.get("city")
            country_code = params.get("country_code")
            
            if not city:
                return {"error": "City parameter is required"}
            
            result = await self.weather_service.get_weather(city, country_code)
            return {"result": result}
            
        elif method == "weather/get_forecast":
            city = params.get("city")
            country_code = params.get("country_code")
            days = params.get("days", 5)
            
            if not city:
                return {"error": "City parameter is required"}
            
            result = await self.weather_service.get_forecast(city, country_code, days)
            return {"result": result}
            
        else:
            return {"error": f"Unknown method: {method}"}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return server capabilities"""
        return {
            "methods": {
                "weather/get_current": {
                    "description": "Get current weather for a city",
                    "parameters": {
                        "city": {"type": "string", "description": "City name"},
                        "country_code": {"type": "string", "description": "Optional country code"}
                    }
                },
                "weather/get_forecast": {
                    "description": "Get weather forecast for a city",
                    "parameters": {
                        "city": {"type": "string", "description": "City name"},
                        "country_code": {"type": "string", "description": "Optional country code"},
                        "days": {"type": "integer", "description": "Number of days (max 5)"}
                    }
                }
            }
        }

async def main():
    """Main function to run the MCP server"""
    server = MCPWeatherServer()
    
    # Simple HTTP server implementation
    import aiohttp
    from aiohttp import web
    
    async def handle_mcp_request(request):
        try:
            data = await request.json()
            response = await server.handle_request(data)
            return web.json_response(response)
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_capabilities(request):
        return web.json_response(server.get_capabilities())
    
    app = web.Application()
    app.router.add_post("/mcp", handle_mcp_request)
    app.router.add_get("/capabilities", handle_capabilities)
    
    host = os.getenv("MCP_SERVER_HOST", "localhost")
    port = int(os.getenv("MCP_SERVER_PORT", "8000"))
    
    logger.info(f"Starting MCP Weather Server on {host}:{port}")
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    
    logger.info(f"MCP Weather Server is running at http://{host}:{port}")
    logger.info("Available endpoints:")
    logger.info("  POST /mcp - Handle MCP requests")
    logger.info("  GET  /capabilities - Get server capabilities")
    
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        logger.info("Shutting down MCP Weather Server...")
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 