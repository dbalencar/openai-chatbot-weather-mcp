#!/usr/bin/env python3
"""
AI Chatbot with OpenAI LLM and MCP Weather Integration
"""

import asyncio
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

from mcp_client import WeatherService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherChatbot:
    """AI Chatbot with weather capabilities via MCP"""
    
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.weather_service = WeatherService()
        self.conversation_history = []
        
        # Weather-related keywords to detect weather queries
        self.weather_keywords = [
            "weather", "temperature", "forecast", "climate", "rain", "snow", 
            "sunny", "cloudy", "wind", "humidity", "°C", "°F", "degrees"
        ]
        
        # System prompt for the chatbot
        self.system_prompt = """You are a helpful AI assistant with access to real-time weather information. You can:

1. Answer general questions and engage in conversation
2. Provide current weather information for any city
3. Provide weather forecasts for upcoming days
4. Help with weather-related planning and advice

When users ask about weather, you can access real-time data through the weather service. Be conversational and helpful, and provide detailed weather information when requested.

For weather queries, you can ask for:
- Current weather in a specific city
- Weather forecasts for upcoming days
- Weather comparisons between cities
- Weather-based recommendations

Always be friendly, informative, and helpful!"""
    
    def _is_weather_query(self, message: str) -> bool:
        """Check if the message is asking about weather"""
        message_lower = message.lower()
        
        # Check for weather-related keywords
        has_weather_keywords = any(keyword in message_lower for keyword in self.weather_keywords)
        
        # Check for location patterns (city names, etc.)
        location_patterns = [
            r"weather in (\w+)",
            r"temperature in (\w+)",
            r"forecast for (\w+)",
            r"how's the weather in (\w+)",
            r"what's the weather like in (\w+)",
            r"weather (\w+)",
            r"(\w+) weather"
        ]
        
        has_location = any(re.search(pattern, message_lower) for pattern in location_patterns)
        
        return has_weather_keywords or has_location
    
    def _extract_location(self, message: str) -> Optional[str]:
        """Extract city name from weather query"""
        message_lower = message.lower()
        
        # Common patterns for extracting city names
        patterns = [
            r"weather in (\w+(?:\s+\w+)*)",
            r"temperature in (\w+(?:\s+\w+)*)",
            r"forecast for (\w+(?:\s+\w+)*)",
            r"how's the weather in (\w+(?:\s+\w+)*)",
            r"what's the weather like in (\w+(?:\s+\w+)*)",
            r"weather (\w+(?:\s+\w+)*)",
            r"(\w+(?:\s+\w+)*) weather"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message_lower)
            if match:
                city = match.group(1).strip()
                # Clean up common words that might be captured
                city = re.sub(r'\b(in|for|the|like)\b', '', city).strip()
                if city and len(city) > 1:
                    return city.title()
        
        return None
    
    def _extract_country_code(self, message: str) -> Optional[str]:
        """Extract country code from message if present"""
        # Look for country codes like "US", "UK", "CA", etc.
        country_pattern = r'\b(US|UK|CA|AU|DE|FR|IT|ES|JP|CN|IN|BR|MX|RU|KR|NL|SE|NO|DK|FI|CH|AT|BE|PL|CZ|HU|RO|BG|HR|SI|SK|EE|LV|LT|MT|CY|LU|IE|PT|GR|PL)\b'
        match = re.search(country_pattern, message.upper())
        return match.group(1) if match else None
    
    async def _get_weather_response(self, message: str) -> str:
        """Get weather information and format response"""
        city = self._extract_location(message)
        country_code = self._extract_country_code(message)
        
        if not city:
            return "I'd be happy to help with weather information! Please specify a city name. For example: 'What's the weather in London?' or 'Weather in New York'"
        
        try:
            # Check if it's asking for forecast
            if any(word in message.lower() for word in ["forecast", "tomorrow", "week", "days", "upcoming"]):
                days = 3  # Default to 3 days
                if "week" in message.lower():
                    days = 7
                elif "tomorrow" in message.lower():
                    days = 1
                
                weather_info = await self.weather_service.get_forecast_info(city, country_code, days)
            else:
                weather_info = await self.weather_service.get_weather_info(city, country_code)
            
            return weather_info
            
        except Exception as e:
            logger.error(f"Error getting weather info: {e}")
            return f"I'm sorry, I couldn't get the weather information for {city}. Please try again or check if the city name is correct."
    
    async def _get_openai_response(self, message: str, weather_context: str = "") -> str:
        """Get response from OpenAI"""
        # Build the conversation context
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add weather context if available
        if weather_context:
            messages.append({
                "role": "system", 
                "content": f"Here is the current weather information that was requested: {weather_context}"
            })
        
        # Add conversation history
        messages.extend(self.conversation_history[-10:])  # Keep last 10 messages for context
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error getting OpenAI response: {e}")
            return "I'm sorry, I'm having trouble processing your request right now. Please try again later."
    
    async def chat(self, message: str) -> str:
        """Main chat method that handles both general conversation and weather queries"""
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Check if this is a weather query
        if self._is_weather_query(message):
            weather_response = await self._get_weather_response(message)
            
            # Get additional context from OpenAI
            ai_response = await self._get_openai_response(message, weather_response)
            
            # Combine weather info with AI response
            full_response = f"{weather_response}\n\n{ai_response}"
            
        else:
            # General conversation
            full_response = await self._get_openai_response(message)
        
        # Add assistant response to history
        self.conversation_history.append({"role": "assistant", "content": full_response})
        
        return full_response
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation_history = []
        return "Conversation history has been reset. How can I help you today?"

async def main():
    """Main function to run the chatbot"""
    print("🌤️  Weather AI Chatbot")
    print("=" * 50)
    print("I'm your AI assistant with access to real-time weather information!")
    print("You can ask me about:")
    print("• Current weather in any city")
    print("• Weather forecasts")
    print("• General questions and conversation")
    print("• Weather-based recommendations")
    print("\nType 'quit' or 'exit' to end the conversation.")
    print("Type 'reset' to clear conversation history.")
    print("=" * 50)
    
    chatbot = WeatherChatbot()
    
    try:
        while True:
            user_input = input("\n🤖 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye! Have a great day!")
                break
            
            elif user_input.lower() == 'reset':
                response = chatbot.reset_conversation()
                print(f"🤖 Assistant: {response}")
                continue
            
            elif not user_input:
                continue
            
            print("🤖 Assistant: Thinking...")
            response = await chatbot.chat(user_input)
            print(f"🤖 Assistant: {response}")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye! Have a great day!")
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 