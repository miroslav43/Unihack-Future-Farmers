#!/usr/bin/env python3
"""
Script to import seed data from JSON files into MongoDB database.

Usage:
    python scripts/import_seed_data.py
"""
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime, date

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings


async def load_json_file(file_path: Path) -> list:
    """Load JSON file and return data"""
    print(f"Loading {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✓ Loaded {len(data)} records from {file_path.name}")
    return data


async def import_workers_as_farmers(db, workers_data: list):
    """Import workers from oameni.json as farmers"""
    print("\n📥 Importing workers as farmers...")
    
    farmers_collection = db.farmers
    inserted_count = 0
    updated_count = 0
    
    for worker in workers_data:
        # Extract worker data
        worker_id = worker.get("id")
        name = worker.get("name", "")
        age = worker.get("age")
        payday = worker.get("payday")
        role = worker.get("role", "")
        
        # Split name into first and last name
        name_parts = name.split(" ", 1)
        first_name = name_parts[0] if len(name_parts) > 0 else "Unknown"
        last_name = name_parts[1] if len(name_parts) > 1 else "Unknown"
        
        # Generate CNP (dummy for demo purposes)
        cnp = f"1{age:02d}0101000{worker_id:03d}"[:13].ljust(13, '0')
        
        # Check if farmer with this worker_id already exists
        existing = await farmers_collection.find_one({"worker_id": worker_id})
        
        if existing:
            # Update existing farmer
            await farmers_collection.update_one(
                {"worker_id": worker_id},
                {"$set": {
                    "role": role,
                    "payday": payday,
                    "age": age,
                    "updated_at": datetime.utcnow()
                }}
            )
            updated_count += 1
        else:
            # Create new farmer record
            farmer_doc = {
                "first_name": first_name,
                "last_name": last_name,
                "cnp": cnp,
                "email": f"{first_name.lower()}.{last_name.lower()}@farm.ro",
                "phone": f"07{worker_id:08d}",
                "age": age,
                "worker_id": worker_id,
                "role": role,
                "payday": payday,
                "experience_years": max(0, age - 20),  # Estimate
                "experience_level": "intermediate",
                "total_parcels": 0,
                "total_land_area": 0.0,
                "has_equipment": "operator" in role.lower() or "driver" in role.lower(),
                "has_irrigation": False,
                "has_storage": False,
                "county": "Ilfov",
                "city": "Bucuresti",
                "address": f"Str. Fermei nr. {worker_id}",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            try:
                await farmers_collection.insert_one(farmer_doc)
                inserted_count += 1
            except Exception as e:
                print(f"  ⚠ Error inserting worker {worker_id} ({name}): {e}")
    
    print(f"✓ Farmers: {inserted_count} inserted, {updated_count} updated")
    return inserted_count, updated_count


async def import_harvest_logs(db, harvest_data: list):
    """Import harvest logs from ferma.json"""
    print("\n📥 Importing harvest logs...")
    
    harvest_collection = db.harvest_logs
    inserted_count = 0
    updated_count = 0
    
    for log_entry in harvest_data:
        # Extract date
        log_date_str = log_entry.get("date")
        log_date = datetime.fromisoformat(log_date_str) if log_date_str else datetime.utcnow()
        
        # Check if log for this date already exists
        existing = await harvest_collection.find_one({"date": log_date})
        
        # Prepare equipment list
        equipment_list = []
        for eq in log_entry.get("equipment", []):
            equipment_list.append({
                "equipment_type": eq.get("equipment_type", "Unknown"),
                "worker_id": eq.get("worker_id", 0),
                "work_hours": float(eq.get("work_hours", 0)),
                "fuel_consumed_liters": float(eq.get("fuel_consumed_liters", 0))
            })
        
        harvest_doc = {
            "date": log_date,
            "notes": log_entry.get("notes", ""),
            "wheat_sown_hectares": float(log_entry.get("wheat_sown_hectares", 0)),
            "sunflower_harvested_hectares": float(log_entry.get("sunflower_harvested_hectares", 0)),
            "beans_harvested_hectares": float(log_entry.get("beans_harvested_hectares", 0)),
            "tomatoes_harvested_hectares": float(log_entry.get("tomatoes_harvested_hectares", 0)),
            "oil_price_per_liter": float(log_entry.get("oil_price_per_liter", 0)),
            "equipment": equipment_list,
            "farmer_id": None,  # Can be linked later if needed
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        if existing:
            # Update existing log
            await harvest_collection.update_one(
                {"date": log_date},
                {"$set": harvest_doc}
            )
            updated_count += 1
        else:
            # Insert new log
            try:
                await harvest_collection.insert_one(harvest_doc)
                inserted_count += 1
            except Exception as e:
                print(f"  ⚠ Error inserting harvest log for {log_date_str}: {e}")
    
    print(f"✓ Harvest logs: {inserted_count} inserted, {updated_count} updated")
    return inserted_count, updated_count


async def main():
    """Main import function"""
    print("=" * 60)
    print("🌾 SEED DATA IMPORT SCRIPT")
    print("=" * 60)
    
    # Define file paths
    base_dir = Path(__file__).parent.parent
    workers_file = base_dir / "to_add_in_database" / "oameni.json"
    harvest_file = base_dir / "to_add_in_database" / "ferma.json"
    
    # Check if files exist
    if not workers_file.exists():
        print(f"❌ Error: {workers_file} not found!")
        return
    
    if not harvest_file.exists():
        print(f"❌ Error: {harvest_file} not found!")
        return
    
    # Load data from JSON files
    workers_data = await load_json_file(workers_file)
    harvest_data = await load_json_file(harvest_file)
    
    # Connect to MongoDB
    print(f"\n🔌 Connecting to MongoDB...")
    print(f"Database: {settings.DATABASE_NAME}")
    
    try:
        client = AsyncIOMotorClient(
            settings.MONGO_API_KEY,
            serverSelectionTimeoutMS=5000
        )
        
        # Test connection
        await client.admin.command('ping')
        print("✓ Connected to MongoDB")
        
        db = client[settings.DATABASE_NAME]
        
        # Import workers as farmers
        workers_inserted, workers_updated = await import_workers_as_farmers(db, workers_data)
        
        # Import harvest logs
        logs_inserted, logs_updated = await import_harvest_logs(db, harvest_data)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 IMPORT SUMMARY")
        print("=" * 60)
        print(f"Workers/Farmers: {workers_inserted} inserted, {workers_updated} updated")
        print(f"Harvest Logs:    {logs_inserted} inserted, {logs_updated} updated")
        print(f"Total Records:   {workers_inserted + logs_inserted} new, {workers_updated + logs_updated} updated")
        print("=" * 60)
        print("✅ Import completed successfully!")
        
        # Close connection
        client.close()
        
    except Exception as e:
        print(f"\n❌ Error during import: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

