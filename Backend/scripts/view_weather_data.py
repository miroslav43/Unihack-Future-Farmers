"""
Script to view weather data from MongoDB
"""
import sys
from pathlib import Path
from pymongo import MongoClient

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))
from app.config.settings import settings

def view_weather_data():
    """View weather data from MongoDB"""
    
    # Connect to MongoDB
    print("Connecting to MongoDB...")
    client = MongoClient(settings.MONGO_API_KEY)
    db = client[settings.DATABASE_NAME]
    weather_collection = db['weather_logs']
    
    # Get total count
    total = weather_collection.count_documents({})
    print(f"\nTotal weather records: {total}")
    
    # Show first 5 records
    print("\n" + "="*80)
    print("FIRST 5 RECORDS:")
    print("="*80)
    for record in weather_collection.find().limit(5):
        print(f"\nDate: {record['date']}")
        print(f"  Temperature: {record['min_temp_celsius']}C - {record['max_temp_celsius']}C")
        print(f"  Location: {record['location']}")
        if record.get('weather_description'):
            print(f"  Weather: {record['weather_description']}")
        print(f"  Sources: {', '.join(record['data_sources'])}")
    
    # Show last 5 records
    print("\n" + "="*80)
    print("LAST 5 RECORDS:")
    print("="*80)
    for record in weather_collection.find().sort("date", -1).limit(5):
        print(f"\nDate: {record['date']}")
        print(f"  Temperature: {record['min_temp_celsius']}C - {record['max_temp_celsius']}C")
        if record.get('weather_description'):
            print(f"  Weather: {record['weather_description']}")
    
    # Statistics
    print("\n" + "="*80)
    print("STATISTICS:")
    print("="*80)
    
    # Hottest day
    hottest = weather_collection.find_one(sort=[("max_temp_celsius", -1)])
    print(f"\nHottest day: {hottest['date']} - {hottest['max_temp_celsius']}C")
    
    # Coldest day
    coldest = weather_collection.find_one(sort=[("min_temp_celsius", 1)])
    print(f"Coldest day: {coldest['date']} - {coldest['min_temp_celsius']}C")
    
    # Days with rain
    rainy_days = weather_collection.count_documents({
        "weather_description": {"$regex": "ploaie|rain|shower", "$options": "i"}
    })
    print(f"Days with rain: {rainy_days}")
    
    # Days with snow
    snowy_days = weather_collection.count_documents({
        "weather_description": {"$regex": "ninsoare|snow", "$options": "i"}
    })
    print(f"Days with snow: {snowy_days}")
    
    # Average temperatures
    pipeline = [
        {
            "$group": {
                "_id": None,
                "avg_max": {"$avg": "$max_temp_celsius"},
                "avg_min": {"$avg": "$min_temp_celsius"}
            }
        }
    ]
    avg_result = list(weather_collection.aggregate(pipeline))
    if avg_result:
        print(f"\nAverage temperatures:")
        print(f"  Max: {avg_result[0]['avg_max']:.1f}C")
        print(f"  Min: {avg_result[0]['avg_min']:.1f}C")
    
    client.close()
    print("\n[OK] Done!")

if __name__ == "__main__":
    try:
        view_weather_data()
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

