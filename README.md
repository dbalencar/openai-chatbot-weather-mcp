# Weather AI Chatbot with MCP Integration

A Python-based AI chatbot that uses OpenAI's GPT model and integrates with a Model Context Protocol (MCP) server to provide real-time weather information from OpenWeatherMap API.

## Features

- 🤖 **AI-Powered Chatbot**: Uses OpenAI's GPT-3.5-turbo for natural language processing
- 🌤️ **Real-time Weather Data**: Access current weather and forecasts for any city worldwide
- 🔌 **MCP Integration**: Implements Model Context Protocol for modular service architecture
- 💬 **Conversational Interface**: Natural language interaction with weather queries
- 📊 **Detailed Weather Information**: Temperature, humidity, wind, pressure, and more
- 🗓️ **Weather Forecasts**: Multi-day weather predictions
- 🔄 **Conversation Memory**: Maintains context across conversation turns

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Chatbot       │    │   MCP Client    │    │   MCP Server    │
│   (OpenAI)      │◄──►│   (HTTP)        │◄──►│   (Weather API) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- OpenWeatherMap API key

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   OPENWEATHER_API_KEY=your_openweather_api_key_here
   MCP_SERVER_HOST=localhost
   MCP_SERVER_PORT=8000
   ```

## Getting API Keys

### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key to your `.env` file

### OpenWeatherMap API Key
1. Go to [OpenWeatherMap](https://openweathermap.org/)
2. Sign up for a free account
3. Navigate to API Keys section
4. Generate a new API key
5. Copy the key to your `.env` file

## Usage

### Starting the MCP Weather Server

First, start the MCP server that provides weather data:

```bash
python weather_mcp_server.py
```

The server will start on `http://localhost:8000` by default.

### Running the Chatbot

In a new terminal, start the chatbot:

```bash
python chatbot.py
```

### Example Conversations

```
🤖 You: What's the weather in London?
🤖 Assistant: Current weather in London, GB:
• Temperature: 18°C (feels like 16°C)
• Conditions: scattered clouds
• Humidity: 72%
• Wind Speed: 3.2 m/s

The weather in London is quite pleasant today! It's 18°C with scattered clouds, which makes for a nice day to be outdoors. The humidity is moderate at 72%, and there's a gentle breeze at 3.2 m/s. You might want to bring a light jacket since it feels like 16°C.

🤖 You: What's the forecast for New York this week?
🤖 Assistant: Weather forecast for New York, US:

📅 2024-01-15:
   Temperature: 12.3°C (min: 8.2°C, max: 16.4°C)
   Conditions: clear sky

📅 2024-01-16:
   Temperature: 14.1°C (min: 10.1°C, max: 18.2°C)
   Conditions: few clouds

📅 2024-01-17:
   Temperature: 11.8°C (min: 7.9°C, max: 15.7°C)
   Conditions: light rain

The weather in New York this week looks quite variable! You'll have clear skies on Monday, some clouds on Tuesday, and light rain on Wednesday. Temperatures will range from around 8°C to 18°C, so you'll want to dress in layers. Don't forget an umbrella for Wednesday!

🤖 You: Tell me a joke
🤖 Assistant: Here's a weather-related joke for you:

Why don't meteorologists like to go outside?

Because they're afraid of getting caught in their own forecasts! 😄

Actually, meteorologists are quite brave - they have to deal with people complaining about the weather whether they predict it correctly or not!

🤖 You: quit
👋 Goodbye! Have a great day!
```

## Available Commands

- `quit`, `exit`, `bye` - End the conversation
- `reset` - Clear conversation history

## Weather Query Examples

The chatbot can understand various ways to ask about weather:

- "What's the weather in Paris?"
- "How's the weather in Tokyo?"
- "Weather forecast for London"
- "Temperature in New York"
- "What's the weather like in Sydney?"
- "Forecast for Berlin this week"
- "Weather in Toronto tomorrow"

## MCP Server Endpoints

The MCP server provides the following endpoints:

- `POST /mcp` - Handle MCP requests
- `GET /capabilities` - Get server capabilities

### Available Methods

1. **weather/get_current**
   - Parameters: `city` (required), `country_code` (optional)
   - Returns: Current weather information

2. **weather/get_forecast**
   - Parameters: `city` (required), `country_code` (optional), `days` (optional, max 5)
   - Returns: Weather forecast information

## Testing

You can test the MCP client independently:

```bash
python mcp_client.py
```

This will test the weather service with sample requests.

## Error Handling

The system includes comprehensive error handling for:

- API connection issues
- Invalid city names
- Missing API keys
- Network timeouts
- Malformed responses

## Configuration

You can customize the following settings in your `.env` file:

- `MCP_SERVER_HOST` - MCP server hostname (default: localhost)
- `MCP_SERVER_PORT` - MCP server port (default: 8000)
- `OPENAI_API_KEY` - Your OpenAI API key
- `OPENWEATHER_API_KEY` - Your OpenWeatherMap API key

## Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY environment variable is required"**
   - Make sure you've set up your `.env` file correctly
   - Verify your OpenAI API key is valid

2. **"OPENWEATHER_API_KEY environment variable is required"**
   - Ensure your OpenWeatherMap API key is in the `.env` file
   - Check that the API key is active

3. **"Failed to connect to MCP server"**
   - Make sure the MCP server is running (`python weather_mcp_server.py`)
   - Check that the host and port settings are correct

4. **"City not found" errors**
   - Verify the city name spelling
   - Try adding a country code (e.g., "London, GB")

### Debug Mode

To enable debug logging, modify the logging level in the Python files:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

Feel free to contribute to this project by:

1. Reporting bugs
2. Suggesting new features
3. Improving documentation
4. Adding new weather data sources

## License

This project is open source and available under the MIT License.

## Acknowledgments

- OpenAI for providing the GPT API
- OpenWeatherMap for weather data
- The MCP community for the protocol specification 