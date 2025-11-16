from agents.agent import build_farmers_team
from models.model import get_gemini_model, get_openrouter_model
from agents.tools import WEATHER_AGENT, VEHICLES_AGENT, EMPLOYEES_AGENT, HARVEST_AGENT

import asyncio

model_agent1 = get_openrouter_model()
model_agent2 = get_openrouter_model()
model_agent3 = get_openrouter_model()
model_agent4 = get_openrouter_model()
team_model = get_openrouter_model()

async def main():
    await WEATHER_AGENT.connect()
    await VEHICLES_AGENT.connect()
    await EMPLOYEES_AGENT.connect()
    await HARVEST_AGENT.connect()

    agent = build_farmers_team(model_agent1, model_agent2, model_agent3, model_agent4, team_model)

    await agent.aprint_response("Today is 16 november 2025. I am in Timisoara, Romania. Tell me how the weather will be this next week. Tell me what employees must be paid this next week starting today. Tell me how much money we spent on oil in the last 7 days, ending yesterday. Also tell me the yels for beans, tomatoes, weath and sunflower from July 14-21, 2025.")

    await HARVEST_AGENT.close()
    await EMPLOYEES_AGENT.close()
    await VEHICLES_AGENT.close()
    await WEATHER_AGENT.close()


if __name__ == "__main__":
    asyncio.run(main())
