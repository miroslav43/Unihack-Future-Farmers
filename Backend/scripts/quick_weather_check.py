"""Quick check of weather data in MongoDB"""
import sys
from pathlib import Path
from pymongo import MongoClient

sys.path.append(str(Path(__file__).parent.parent))
from app.config.settings import settings

client = MongoClient(settings.MONGO_API_KEY)
db = client[settings.DATABASE_NAME]
weather_collection = db['weather_logs']

print(f"Total weather records: {weather_collection.count_documents({})}")
print(f"Database: {settings.DATABASE_NAME}")
print(f"Collection: weather_logs")
print("\nSample record:")
sample = weather_collection.find_one()
if sample:
    print(f"  Date: {sample['date']}")
    print(f"  Temp: {sample['min_temp_celsius']}C - {sample['max_temp_celsius']}C")
    print(f"  Location: {sample['location']}")
    print("\n[OK] Weather data is in MongoDB!")
else:
    print("[ERROR] No data found!")

client.close()

