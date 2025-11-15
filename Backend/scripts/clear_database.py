"""
Script to clear farmers and harvest_logs collections
"""
import asyncio
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient

# Import settings to get MongoDB connection
import sys
sys.path.append(str(Path(__file__).parent.parent))

from app.config.settings import settings


async def main():
    """Clear database collections"""
    print("\n" + "="*60)
    print("DATABASE CLEANUP SCRIPT")
    print("="*60)
    
    # Connect to MongoDB
    print("\n[*] Connecting to MongoDB...")
    client = AsyncIOMotorClient(settings.MONGO_API_KEY)
    db = client[settings.DATABASE_NAME]
    
    try:
        await client.admin.command('ping')
        print("[+] Connected to MongoDB successfully")
    except Exception as e:
        print(f"[-] Failed to connect to MongoDB: {e}")
        return
    
    # Delete all farmers
    print("\n[*] Deleting all farmers...")
    result = await db.farmers.delete_many({})
    print(f"[+] Deleted {result.deleted_count} farmers")
    
    # Delete all harvest logs
    print("\n[*] Deleting all harvest logs...")
    result = await db.harvest_logs.delete_many({})
    print(f"[+] Deleted {result.deleted_count} harvest logs")
    
    print("\n" + "="*60)
    print("DATABASE CLEANUP COMPLETE!")
    print("="*60 + "\n")
    
    # Close connection
    client.close()


if __name__ == "__main__":
    asyncio.run(main())

