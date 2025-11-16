from agno.tools.mcp import MCPTools

WEATHER_AGENT = MCPTools(
    url = "http://127.0.0.1:8000/mcp/mcp_weather_agent/mcp",
    transport= "streamable-http",
    timeout_seconds= 1000
)

VEHICLES_AGENT = MCPTools(
    url = "http://127.0.0.1:8000/mcp/mcp_vehicles_agent/mcp",
    transport= "streamable-http",
    timeout_seconds= 1000
)

EMPLOYEES_AGENT = MCPTools(
    url = "http://127.0.0.1:8000/mcp/mcp_employees_agent/mcp",
    transport= "streamable-http",
    timeout_seconds= 1000
)

HARVEST_AGENT  = MCPTools(
    url = "http://127.0.0.1:8000/mcp/mcp_harvest_agent/mcp",
    transport= "streamable-http",
    timeout_seconds= 1000
)

