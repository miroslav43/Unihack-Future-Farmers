from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI
import asyncio
from fastapi.middleware.cors import CORSMiddleware

# from mcp_server.db import serialize_datetime
from mcp_server.db import collection_weather

import json

from datetime import datetime, timedelta

def serialize_datetime(dt):
    """Helper function to serialize datetime objects"""
    if dt is None:
        return None
    if isinstance(dt, datetime):
        return dt.isoformat()
    if isinstance(dt, str):
        return dt
    return str(dt)

def serialize_objectid(obj_id):
    """Helper function to serialize ObjectId"""
    if obj_id is None:
        return None
    if isinstance(obj_id, ObjectId):
        return str(obj_id)
    return obj_id

app = FastAPI()

# Add CORS middleware to the main FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including OPTIONS
    allow_headers=["*"],
)

mcp_weather_agent = FastMCP("Agent Weather MCP server", stateless_http=True, port=8001)
mcp_agent2 = FastMCP("Agent 2 MCP server", stateless_http=True, port=8002)
mcp_agent3 = FastMCP("Agent 3 MCP server", stateless_http=True, port=8003)

@mcp_weather_agent.tool()
async def get_weather_informations_for_last_n_days(number_of_days: int, today_day: int, today_month:int, today_year: int) -> dict:
    """
        Tool description:
            Tool used to get information about the weather for the past n days, starting from
        today. This tool queries the weather database, where we have scrapped important information in this direction.

        Input: 
            type: (int), name: days, equal with n from the description above, and means the number of days to fetch the weather information from the past relative to today.
            type: (int), name: today_day, today_month, today_year represents the date (day - month - year) that we are currently in.

        Output:
            type: (dict), meaning: a mapping for the weather (temperature and possible description) for the days that have been requested when calling this tool. 
    """

    # Build the "today" date
    today = datetime(today_year, today_month, today_day)

    # Build list of date strings in format "YYYY-MM-DD"
    requested_dates = [
        (today - timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(number_of_days)
    ]

    # Build query: find all documents WHERE date ∈ requested_dates
    query = {
        "date": {"$in": requested_dates}
    }

    # Convert cursor to list to avoid serialization issues
    cursor = collection_weather.find(query)
    documents = list(cursor)

    # Build response dictionary
    results = {}

    for doc in documents:
        date_key = doc.get("date")
        results[date_key] = {
            "max_temp_celsius": doc.get("max_temp_celsius"),
            "min_temp_celsius": doc.get("min_temp_celsius"),
            "weather_description": doc.get("weather_description"),
            "location": doc.get("location"),
            "temperature_unit": doc.get("temperature_unit"),
            "imported_at": serialize_datetime(doc.get("imported_at"))
            # Note: Removed _id from results since it's not needed and causes serialization issues
        }

    return results

@mcp_weather_agent.tool()
async def get_weather_info_for_the_next_n_days(days: int, today_day: int, today_month:int, today_year: int) -> dict:
    """
        Tool description:
            Tool used to get information about the weather for the next n days (! if available !), starting from
        today. This tool queries the weather database, where we have scrapped important information in this direction.

        Input: 
            type: (int), name: days, equal with n from the description above, and means the number of days to fetch the weather information from the past relative to today.
            type: (int), name: today_day, today_month, today_year represents the date (day - month - year) that we are currently in.

        Output:
            type: (dict), meaning: a mapping for the weather (temperature and possible description) for the days that have been requested when calling this tool. 
    """

    today = datetime(today_year, today_month, today_day).strftime("%Y-%m-%d")

    # Query for dates greater than today
    query = {
        "date": {"$gt": today}
    }

    # Sort ascending (nearest dates first), limit N days
    cursor = collection_weather.find(query).sort("date", 1).limit(days)

    documents = list(cursor)

    results = {}
    for doc in documents:
        date_key = doc.get("date")
        results[date_key] = {
            "max_temp_celsius": doc.get("max_temp_celsius"),
            "min_temp_celsius": doc.get("min_temp_celsius"),
            "weather_description": doc.get("weather_description"),
            "location": doc.get("location"),
            "temperature_unit": doc.get("temperature_unit"),
            "imported_at": serialize_datetime(doc.get("imported_at")),
        }

    return results

@mcp_weather_agent.tool()
async def get_weather_info_for_a_speciffic_day(day: int, month:int, year: int) -> dict:
    """
        Tool description:
            Tool used to get information about the weather for a speciffic day. This tool queries the weather database, 
        where we have scrapped important information in this direction.

        Input: 
            type: (int), name: day, month, year represents the date (day - month - year) that we request the weather information for.

        Output:
            type: (dict), meaning: a mapping for the weather (temperature and possible description) for the date this tool was called with.
    """

    # Convert input date to string format "YYYY-MM-DD"
    requested_date = datetime(year, month, day).strftime("%Y-%m-%d")

    # Build query: find a document where date == requested_date
    query = {"date": requested_date}

    doc = collection_weather.find_one(query)

    # If nothing found → return empty dict
    if not doc:
        return {}

    # Build response
    result = {
        "date": doc.get("date"),
        "max_temp_celsius": doc.get("max_temp_celsius"),
        "min_temp_celsius": doc.get("min_temp_celsius"),
        "weather_description": doc.get("weather_description"),
        "location": doc.get("location"),
        "temperature_unit": doc.get("temperature_unit"),
        "imported_at": serialize_datetime(doc.get("imported_at")),
    }

    return result

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
asyncio.gather(mcp_weather_agent.run_streamable_http_async(), mcp_agent2.run_streamable_http_async(), mcp_agent3.run_streamable_http_async())

app.mount("/mcp/mcp_weather_agent", mcp_weather_agent.streamable_http_app())
app.mount("/mcp/agent2", mcp_agent2.streamable_http_app())
app.mount("/mcp/agent3", mcp_agent3.streamable_http_app())