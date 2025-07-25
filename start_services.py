#!/usr/bin/env python3
"""
Startup script for the Weather AI Chatbot system
"""

import asyncio
import subprocess
import sys
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import openai
        import requests
        import aiohttp
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_api_keys():
    """Check if API keys are configured"""
    openai_key = os.getenv("OPENAI_API_KEY")
    weather_key = os.getenv("OPENWEATHER_API_KEY")
    
    if not openai_key or openai_key == "your_openai_api_key_here":
        print("❌ OpenAI API key not configured")
        print("Please set OPENAI_API_KEY in your .env file")
        return False
    
    if not weather_key or weather_key == "your_openweather_api_key_here":
        print("❌ OpenWeatherMap API key not configured")
        print("Please set OPENWEATHER_API_KEY in your .env file")
        return False
    
    print("✅ API keys are configured")
    return True

def start_mcp_server():
    """Start the MCP weather server"""
    print("🚀 Starting MCP Weather Server...")
    try:
        process = subprocess.Popen([
            sys.executable, "weather_mcp_server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ MCP Weather Server is running")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Failed to start MCP server: {stderr.decode()}")
            return None
    except Exception as e:
        print(f"❌ Error starting MCP server: {e}")
        return None

def start_chatbot():
    """Start the chatbot"""
    print("🤖 Starting Weather AI Chatbot...")
    try:
        subprocess.run([sys.executable, "chatbot.py"])
    except KeyboardInterrupt:
        print("\n👋 Chatbot stopped by user")
    except Exception as e:
        print(f"❌ Error starting chatbot: {e}")

def main():
    """Main function"""
    print("🌤️  Weather AI Chatbot System")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check API keys
    if not check_api_keys():
        return
    
    print("\nStarting services...")
    
    # Start MCP server
    mcp_process = start_mcp_server()
    if not mcp_process:
        print("❌ Cannot start chatbot without MCP server")
        return
    
    try:
        # Start chatbot
        start_chatbot()
    finally:
        # Clean up MCP server
        if mcp_process:
            print("\n🛑 Stopping MCP Weather Server...")
            mcp_process.terminate()
            mcp_process.wait()
            print("✅ MCP Weather Server stopped")

if __name__ == "__main__":
    main() 