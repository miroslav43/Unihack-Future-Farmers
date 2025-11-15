from agents.agent import build_farmers_team
from models.model import get_gemini_model, get_openrouter_model
from agents.tools import AGENT1, AGENT2, AGENT3

import asyncio

model_agent1 = get_openrouter_model()
model_agent2 = get_openrouter_model()
model_agent3 = get_openrouter_model()
team_model = get_openrouter_model()

async def main():
    await AGENT1.connect()
    await AGENT2.connect()
    await AGENT3.connect()

    agent = build_farmers_team(model_agent1, model_agent2, model_agent3, team_model)

    await agent.aprint_response("What day is today?")

    await AGENT3.close()
    await AGENT2.close()
    await AGENT1.close()


if __name__ == "__main__":
    asyncio.run(main())
