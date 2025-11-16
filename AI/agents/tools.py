from agno.tools.mcp import MCPTools

WEATHER_AGENT = MCPTools(
    url = "http://127.0.0.1:8000/mcp/mcp_weather_agent/mcp",
    transport= "streamable-http",
    timeout_seconds= 1000
)

AGENT2 = MCPTools(
    url = "http://127.0.0.1:8000/mcp/agent2/mcp",
    transport= "streamable-http",
    timeout_seconds= 1000
)

AGENT3 = MCPTools(
    url = "http://127.0.0.1:8000/mcp/agent3/mcp",
    transport= "streamable-http",
    timeout_seconds= 1000
)

