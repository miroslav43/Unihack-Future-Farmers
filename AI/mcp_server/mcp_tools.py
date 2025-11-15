from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI
import asyncio
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware to the main FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including OPTIONS
    allow_headers=["*"],
)

mcp_agent1 = FastMCP("Agent 1 MCP server", stateless_http=True, port=8001)
mcp_agent2 = FastMCP("Agent 2 MCP server", stateless_http=True, port=8002)
mcp_agent3 = FastMCP("Agent 3 MCP server", stateless_http=True, port=8003)

@mcp_agent1.tool()
async def tool1v1(variable1: str) -> str:
    """
        Description of the tool
    """

    return "something1"

@mcp_agent1.tool()
async def tool1v2(variable1: str) -> str:
    """
        Description of the tool
    """

    return "something1"

@mcp_agent2.tool()
async def tool2(variable1: str) -> str:
    """
        Description of the tool
    """

    return "something2"

@mcp_agent3.tool()
async def tool3(variable1: str) -> str:
    """
        Description of the tool
    """

    return "something3"

# npx @modelcontextprotocol/inspector
# uvicorn mcp_server.mcp_tools:app --host 0.0.0.0 --port 8000

# ====== Mount the 3 servers ======
asyncio.gather(mcp_agent1.run_streamable_http_async(), mcp_agent2.run_streamable_http_async(), mcp_agent3.run_streamable_http_async())

app.mount("/mcp/agent1", mcp_agent1.streamable_http_app())
app.mount("/mcp/agent2", mcp_agent2.streamable_http_app())
app.mount("/mcp/agent3", mcp_agent3.streamable_http_app())