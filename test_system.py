#!/usr/bin/env python3
"""
Test script for the Weather AI Chatbot system
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_mcp_client():
    """Test the MCP client functionality"""
    print("🧪 Testing MCP Client...")
    
    try:
        from mcp_client import WeatherService
        
        weather_service = WeatherService()
        
        # Test current weather
        print("  Testing current weather for London...")
        weather_info = await weather_service.get_weather_info("London", "GB")
        if "Error" not in weather_info:
            print("  ✅ Current weather test passed")
        else:
            print(f"  ❌ Current weather test failed: {weather_info}")
            return False
        
        # Test forecast
        print("  Testing weather forecast for London...")
        forecast_info = await weather_service.get_forecast_info("London", "GB", 2)
        if "Error" not in forecast_info:
            print("  ✅ Forecast test passed")
        else:
            print(f"  ❌ Forecast test failed: {forecast_info}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ MCP client test failed: {e}")
        return False

def test_openai_connection():
    """Test OpenAI API connection"""
    print("🧪 Testing OpenAI Connection...")
    
    try:
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Simple test request
        async def test_request():
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say 'Hello, World!'"}],
                max_tokens=10
            )
            return response.choices[0].message.content
        
        result = asyncio.run(test_request())
        if "Hello" in result:
            print("  ✅ OpenAI connection test passed")
            return True
        else:
            print(f"  ❌ OpenAI test failed: {result}")
            return False
            
    except Exception as e:
        print(f"  ❌ OpenAI connection test failed: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("🧪 Testing Environment Configuration...")
    
    # Check API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    weather_key = os.getenv("OPENWEATHER_API_KEY")
    
    if not openai_key or openai_key == "your_openai_api_key_here":
        print("  ❌ OpenAI API key not configured")
        return False
    
    if not weather_key or weather_key == "your_openweather_api_key_here":
        print("  ❌ OpenWeatherMap API key not configured")
        return False
    
    print("  ✅ API keys are configured")
    
    # Check dependencies
    try:
        import openai
        import requests
        import aiohttp
        print("  ✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"  ❌ Missing dependency: {e}")
        return False

async def test_chatbot():
    """Test the chatbot functionality"""
    print("🧪 Testing Chatbot...")
    
    try:
        from chatbot import WeatherChatbot
        
        chatbot = WeatherChatbot()
        
        # Test weather query detection
        weather_query = "What's the weather in Paris?"
        is_weather = chatbot._is_weather_query(weather_query)
        if is_weather:
            print("  ✅ Weather query detection passed")
        else:
            print("  ❌ Weather query detection failed")
            return False
        
        # Test location extraction
        location = chatbot._extract_location(weather_query)
        if location == "Paris":
            print("  ✅ Location extraction passed")
        else:
            print(f"  ❌ Location extraction failed: got '{location}', expected 'Paris'")
            return False
        
        # Test conversation
        response = await chatbot.chat("Hello!")
        if response and len(response) > 0:
            print("  ✅ Basic conversation test passed")
        else:
            print("  ❌ Basic conversation test failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Chatbot test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🌤️  Weather AI Chatbot System Tests")
    print("=" * 50)
    
    tests = [
        ("Environment", test_environment),
        ("OpenAI Connection", test_openai_connection),
        ("MCP Client", test_mcp_client),
        ("Chatbot", test_chatbot)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        print("\nTo start the system, run:")
        print("  python start_services.py")
    else:
        print("⚠️  Some tests failed. Please check the configuration and try again.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 