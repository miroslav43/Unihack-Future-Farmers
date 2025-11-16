"""
Script to import weather data from JSON file directly into MongoDB
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))
from app.config.settings import settings

def import_weather_data():
    """Import weather data from merged_weather_timisoara.json into MongoDB"""
    
    # Connect to MongoDB
    print(f"Connecting to MongoDB...")
    client = MongoClient(settings.MONGO_API_KEY)
    db = client[settings.DATABASE_NAME]
    
    # Create weather_logs collection
    weather_collection = db['weather_logs']
    
    # Create index on date field for faster queries
    print("Creating index on date field...")
    weather_collection.create_index([("date", ASCENDING)], unique=True)
    
    # Read the JSON file
    json_file_path = Path(__file__).parent.parent / "merged_weather_timisoara.json"
    print(f"Reading weather data from {json_file_path}...")
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        weather_data = json.load(f)
    
    # Extract metadata
    metadata = {
        "location": weather_data.get("location"),
        "temperature_unit": weather_data.get("temperature_unit"),
        "merged_date": weather_data.get("merged_date"),
        "total_days": weather_data.get("total_days"),
        "sources": weather_data.get("sources"),
        "note": weather_data.get("note")
    }
    
    print(f"\nImporting weather data for {metadata['location']}")
    print(f"Total days: {metadata['total_days']}")
    print(f"Data sources: {', '.join(metadata['sources'])}")
    print(f"Merged date: {metadata['merged_date']}\n")
    
    # Prepare documents for insertion
    weather_logs = []
    for day_data in weather_data.get("data", []):
        document = {
            "date": day_data["date"],
            "max_temp_celsius": day_data["max_temp_celsius"],
            "min_temp_celsius": day_data["min_temp_celsius"],
            "data_sources": day_data["data_sources"],
            "weather_description": day_data.get("weather_description"),
            "location": metadata["location"],
            "temperature_unit": metadata["temperature_unit"],
            "imported_at": datetime.utcnow().isoformat()
        }
        weather_logs.append(document)
    
    # Insert documents
    print(f"Inserting {len(weather_logs)} weather records...")
    inserted_count = 0
    updated_count = 0
    skipped_count = 0
    
    for log in weather_logs:
        try:
            weather_collection.insert_one(log)
            inserted_count += 1
            print(f"[+] Inserted: {log['date']} - {log['min_temp_celsius']}C to {log['max_temp_celsius']}C")
        except DuplicateKeyError:
            # Update existing record
            result = weather_collection.update_one(
                {"date": log["date"]},
                {"$set": log}
            )
            if result.modified_count > 0:
                updated_count += 1
                print(f"[*] Updated: {log['date']} - {log['min_temp_celsius']}C to {log['max_temp_celsius']}C")
            else:
                skipped_count += 1
                print(f"[-] Skipped (no changes): {log['date']}")
        except Exception as e:
            print(f"[!] Error inserting {log['date']}: {str(e)}")
    
    # Print summary
    print("\n" + "="*60)
    print("IMPORT SUMMARY")
    print("="*60)
    print(f"Total records processed: {len(weather_logs)}")
    print(f"[+] Inserted: {inserted_count}")
    print(f"[*] Updated: {updated_count}")
    print(f"[-] Skipped: {skipped_count}")
    print(f"Total in database: {weather_collection.count_documents({})}")
    print("="*60)
    
    # Show some sample queries
    print("\nSample queries:")
    print("\n1. Hottest day:")
    hottest = weather_collection.find_one(sort=[("max_temp_celsius", -1)])
    if hottest:
        print(f"   {hottest['date']}: {hottest['max_temp_celsius']}°C")
    
    print("\n2. Coldest day:")
    coldest = weather_collection.find_one(sort=[("min_temp_celsius", 1)])
    if coldest:
        print(f"   {coldest['date']}: {coldest['min_temp_celsius']}°C")
    
    print("\n3. Days with rain:")
    rainy_days = weather_collection.count_documents({
        "weather_description": {"$regex": "ploaie|rain|shower", "$options": "i"}
    })
    print(f"   {rainy_days} days with rain")
    
    print("\n4. Average temperature:")
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
        print(f"   Max: {avg_result[0]['avg_max']:.1f}°C, Min: {avg_result[0]['avg_min']:.1f}°C")
    
    print("\n[OK] Weather data import completed successfully!")
    
    client.close()

if __name__ == "__main__":
    try:
        import_weather_data()
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

