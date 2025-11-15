"""
Quick script to count farmers and harvest logs documents.
"""
import asyncio
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient

from app.config.settings import settings


async def main():
    client = AsyncIOMotorClient(settings.MONGO_API_KEY)
    db = client[settings.DATABASE_NAME]

    farmers_count = await db.farmers.count_documents({})
    harvest_count = await db.harvest_logs.count_documents({})

    print(f"Farmers count: {farmers_count}")
    print(f"Harvest logs count: {harvest_count}")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())

