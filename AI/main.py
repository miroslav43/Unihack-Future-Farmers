from agents.agent import build_farmers_team
from models.model import get_gemini_model, get_openrouter_model
from agents.tools import WEATHER_AGENT, AGENT2, AGENT3

import asyncio

model_agent1 = get_openrouter_model()
model_agent2 = get_openrouter_model()
model_agent3 = get_openrouter_model()
team_model = get_openrouter_model()

async def main():
    await WEATHER_AGENT.connect()
    await AGENT2.connect()
    await AGENT3.connect()

    agent = build_farmers_team(model_agent1, model_agent2, model_agent3, team_model)

    await agent.aprint_response("Today is 15 november 2025. I am in Timisora, Romania. How was the weather yesterday? How will the weather be the next week? And how will the weather be on the 25 th of November? Respond to all of these questions for me please.")

    await AGENT3.close()
    await AGENT2.close()
    await WEATHER_AGENT.close()


if __name__ == "__main__":
    asyncio.run(main())
