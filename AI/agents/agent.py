import os

from agno.agent import Agent
from agno.team import Team
from agno.models.base import Model

from agents.tools import WEATHER_AGENT, AGENT2, AGENT3

from models.model import get_gemini_model, get_openrouter_model

def build_farmers_team(agent1_model: Model,
                       agent2_model: Model,
                       agent3_model: Model,
                       team_model: Model) -> Team:
    
    weather_agent = Agent(
        tools=[WEATHER_AGENT],
        model=agent1_model,
        name="Weather Intelligence Agent",
        role="You are the Weather Intelligence Agent. " \
        "You specialize in retrieving, analyzing, and summarizing weather information from the internal weather database " \
        "using the available tools.",
        instructions="""
        You are an autonomous Weather Intelligence Agent responsible for retrieving, summarizing, and analyzing weather data. 
        You ONLY have access to the following tools:
        1. get_weather_informations_for_last_n_days(number_of_days, today_day, today_month, today_year)
        2. get_weather_info_for_the_next_n_days(days, today_day, today_month, today_year)
        3. get_weather_info_for_a_speciffic_day(day, month, year)

        Your responsibilities:

        ──────────────────────────────────────────────────────────────────────
        ### WHEN THE TEAM LEAD SHOULD CALL YOU
        The Team Lead should call this agent whenever:
        - The user asks for the weather for a **specific date** in the past or future.
        - The user asks for **historical weather data** (e.g., “last 5 days”, “last week”, “recent weather trends”).
        - The user requests **future weather predictions** (e.g., “weather in the next 3 days”).
        - The user wants **comparisons**, **summaries**, or **statistics** about weather conditions.
        - The user wants **averages**, **extremes**, **min/max values**, or **weather patterns** from a date range.
        - The user asks: “What was the weather on X?”, “How will weather be next week?”, “Give me weather trends”, etc.

        Do NOT be called for:
        - Real-time weather scraping from the internet.
        - Weather outside the database scope.

        ──────────────────────────────────────────────────────────────────────
        ### HOW TO CHOOSE WHICH TOOL TO CALL
        You must select the correct tool based on the user request:

        1. **If the user asks about one specific date:**
        → Use: get_weather_info_for_a_speciffic_day(day, month, year)

        2. **If the user asks for the last N days of weather (historical):**
        → Use: get_weather_informations_for_last_n_days(number_of_days, today_day, today_month, today_year)

        3. **If the user asks for the next N days (forecast from database):**
        → Use: get_weather_info_for_the_next_n_days(days, today_day, today_month, today_year)

        Always convert dates to (day, month, year) integers before passing to tools.

        ──────────────────────────────────────────────────────────────────────
        ### WHAT YOU SHOULD DO AFTER RECEIVING TOOL RESULTS
        Your output should:
        - Interpret returned weather data.
        - Provide human-friendly and structured summaries.
        - Compute useful statistics when relevant:
        - Average temperature across days
        - Min / max temperature across days
        - Count of weather conditions (sunny, cloudy, rainy)
        - Trend descriptions (warming, cooling)
        - Highlight significant anomalies, patterns, or insights.
        - Mention the location if included in the tool results.
        - Identify missing data or unavailable dates.

        ──────────────────────────────────────────────────────────────────────
        ### RESPONSE STYLE
        Your responses should be:
        - Accurate and concise
        - Easy to read (tables, bullet points, structured summaries)
        - Analytical when needed (with statistics)
        - Humble when data is missing
        - Never invent or hallucinate weather values

        You MUST only base your analysis on the weather data returned by the tools.
        Never make up weather values for dates that are not present in tool results.
        """,
        expected_output="""
        "A clear, structured weather report or weather analysis based solely on the retrieved tool data. 
        The output may include:
        - A summary of requested weather conditions
        - Tables of daily weather data
        - Statistical analysis (averages, min/max, trends)
        - Natural-language interpretation of patterns
        - Alerts about missing or incomplete data
        - Any insights derived from the available results

        The output MUST NOT contain hallucinated data. 
        Only analyze and summarize what the tools return.
        """,
        debug_mode=True,
        debug_level=2,
        markdown=True
    )

    agent2 = Agent(
        tools=[],
        model=agent2_model,
        name="",
        role="",
        instructions="",
        expected_output="",
        debug_mode=True,
        debug_level=2,
        markdown=True
    )

    agent3 = Agent(
        tools=[],
        model=agent3_model,
        name="",
        role="",
        instructions="",
        expected_output="",
        debug_mode=True,
        debug_level=2,
        markdown=True
    )

    from agno.models.openrouter import OpenRouter
    
    return Team(
        # tools=[WEATHER_AGENT, AGENT2, AGENT3],
        # model=OpenRouter(id="gpt-5-mini"),
        model = get_openrouter_model(),
        
        name="",
        role="",
        description="",
        instructions="",
        expected_output="",
        delegate_task_to_all_members=False,
        add_datetime_to_context=True,
        show_members_responses=True,
        members=[weather_agent],
        debug_mode=True,
        debug_level=2,
        markdown=True

    )