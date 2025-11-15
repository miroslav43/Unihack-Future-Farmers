from agno.tools.mcp import MCPTools

AGENT1 = MCPTools(
    url = "http://127.0.0.1:8000/mcp/agent1/mcp",
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

