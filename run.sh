#!/bin/bash

# Weather AI Chatbot System Startup Script

echo "🌤️  Weather AI Chatbot System"
echo "================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "✅ Created .env file from template"
        echo "📝 Please edit .env file and add your API keys:"
        echo "   - OPENAI_API_KEY"
        echo "   - OPENWEATHER_API_KEY"
        exit 1
    else
        echo "❌ env.example file not found"
        exit 1
    fi
fi

# Check if requirements are installed
echo "🔍 Checking dependencies..."
if ! python3 -c "import openai, requests, aiohttp" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

echo "✅ Dependencies are installed"

# Run the startup script
echo "🚀 Starting the system..."
python3 start_services.py 