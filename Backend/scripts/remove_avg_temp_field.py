"""
Script to remove avg_temp_celsius field from weather_logs collection
"""
import sys
from pathlib import Path
from pymongo import MongoClient

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))
from app.config.settings import settings

def remove_avg_temp_field():
    """Remove avg_temp_celsius field from all documents in weather_logs collection"""
    
    # Connect to MongoDB
    print("Connecting to MongoDB...")
    client = MongoClient(settings.MONGO_API_KEY)
    db = client[settings.DATABASE_NAME]
    weather_collection = db['weather_logs']
    
    # Get total count before operation
    total_docs = weather_collection.count_documents({})
    print(f"Total documents in weather_logs: {total_docs}")
    
    # Count documents with avg_temp_celsius field
    docs_with_field = weather_collection.count_documents({"avg_temp_celsius": {"$exists": True}})
    print(f"Documents with avg_temp_celsius field: {docs_with_field}")
    
    if docs_with_field == 0:
        print("\n[OK] No documents have the avg_temp_celsius field. Nothing to remove.")
        client.close()
        return
    
    # Remove the avg_temp_celsius field from all documents
    print(f"\nRemoving avg_temp_celsius field from {docs_with_field} documents...")
    result = weather_collection.update_many(
        {"avg_temp_celsius": {"$exists": True}},
        {"$unset": {"avg_temp_celsius": ""}}
    )
    
    print(f"\n[OK] Successfully removed avg_temp_celsius field!")
    print(f"Documents modified: {result.modified_count}")
    
    # Verify removal
    remaining_docs_with_field = weather_collection.count_documents({"avg_temp_celsius": {"$exists": True}})
    print(f"Documents with avg_temp_celsius field after removal: {remaining_docs_with_field}")
    
    # Show a sample document to verify
    print("\nSample document after removal:")
    sample = weather_collection.find_one()
    if sample:
        print(f"Date: {sample.get('date')}")
        print(f"Max temp: {sample.get('max_temp_celsius')}°C")
        print(f"Min temp: {sample.get('min_temp_celsius')}°C")
        print(f"Avg temp field present: {'avg_temp_celsius' in sample}")
    
    client.close()

if __name__ == "__main__":
    try:
        remove_avg_temp_field()
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
