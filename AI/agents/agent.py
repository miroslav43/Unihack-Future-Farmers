import os

from agno.agent import Agent
from agno.team import Team
from agno.models.base import Model

from agents.tools import AGENT1, AGENT2, AGENT3

from models.model import get_gemini_model, get_openrouter_model

def build_farmers_team(agent1_model: Model,
                       agent2_model: Model,
                       agent3_model: Model,
                       team_model: Model) -> Team:
    
    agent1 = Agent(
        tools=[],
        model=agent1_model,
        name="",
        role="",
        instructions="",
        expected_output="",
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
        tools=[AGENT1, AGENT2, AGENT3],
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
        members=[],
        debug_mode=True,
        debug_level=2,
        markdown=True

    )