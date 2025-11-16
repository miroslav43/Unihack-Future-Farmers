"""
Script to load database with data from ferma.json and oameni.json
This script reads JSON files and inserts the data into MongoDB collections
"""
import asyncio
import json
import random
from datetime import datetime
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient

# Import settings to get MongoDB connection
import sys
sys.path.append(str(Path(__file__).parent.parent))

from app.config.settings import settings

# Helper to generate Romanian CNP
def generate_cnp(age: int) -> str:
    """Generate a dummy Romanian CNP"""
    birth_year = 2025 - age
    sex = random.choice([1, 2])  # 1=male, 2=female
    yy = str(birth_year)[-2:]
    mm = str(random.randint(1, 12)).zfill(2)
    dd = str(random.randint(1, 28)).zfill(2)
    county = str(random.randint(1, 52)).zfill(2)
    nnn = str(random.randint(1, 999)).zfill(3)
    cnp_base = f"{sex}{yy}{mm}{dd}{county}{nnn}"
    # Simple checksum (not real algorithm, just for demo)
    return cnp_base + str(random.randint(0, 9))


async def load_farmers(db, oameni_data):
    """Load farmers collection from oameni.json"""
    farmers_collection = db.farmers
    
    print(f"\n{'='*60}")
    print(f"LOADING FARMERS FROM oameni.json")
    print(f"{'='*60}")
    
    worker_id_to_mongodb_id = {}
    
    # Extended list of Romanian counties (50+)
    counties = [
        "Ilfov", "Prahova", "Dâmbovița", "Teleorman", "Giurgiu", "Ialomița", "Călărași",
        "Argeș", "Buzău", "Brăila", "Constanța", "Tulcea", "Galați", "Vrancea",
        "Bacău", "Vaslui", "Iași", "Neamț", "Suceava", "Botoșani",
        "Mureș", "Harghita", "Covasna", "Brașov", "Sibiu", "Alba", "Cluj",
        "Bihor", "Sălaj", "Maramureș", "Satu Mare", "Bistrița-Năsăud",
        "Arad", "Timiș", "Caraș-Severin", "Hunedoara", "Mehedinți",
        "Gorj", "Vâlcea", "Olt", "Dolj", "Teleorman"
    ]
    
    # Extended list of cities/towns (50+)
    cities = [
        "București", "Ploiești", "Târgoviște", "Alexandria", "Giurgiu", "Slobozia", "Călărași",
        "Pitești", "Buzău", "Brăila", "Constanța", "Tulcea", "Galați", "Focșani",
        "Bacău", "Vaslui", "Iași", "Piatra Neamț", "Suceava", "Botoșani",
        "Târgu Mureș", "Miercurea Ciuc", "Sfântu Gheorghe", "Brașov", "Sibiu", "Alba Iulia", "Cluj-Napoca",
        "Oradea", "Zalău", "Baia Mare", "Satu Mare", "Bistrița",
        "Arad", "Timișoara", "Reșița", "Deva", "Drobeta-Turnu Severin",
        "Târgu Jiu", "Râmnicu Vâlcea", "Slatina", "Craiova", "Roșiorii de Vede",
        "Turda", "Mediaș", "Făgăraș", "Curtea de Argeș", "Câmpulung", "Moreni",
        "Tecuci", "Bârlad", "Huși", "Adjud"
    ]
    
    # Extended list of street names (30+)
    streets = [
        "Principală", "Agricultorilor", "Câmpului", "Semănătorilor", "Recoltei",
        "Grâului", "Porumbului", "Florilor", "Păcii", "Libertății",
        "Unirii", "Victoriei", "Independenței", "Republicii", "Mihai Viteazul",
        "Stefan cel Mare", "Cuza Vodă", "Avram Iancu", "Horea", "Closca",
        "Crișan", "Tudor Vladimirescu", "Nicolae Bălcescu", "Vasile Alecsandri",
        "Mihai Eminescu", "Ion Creangă", "George Coșbuc", "Octavian Goga",
        "Lucian Blaga", "Liviu Rebreanu", "Cireșilor", "Trandafirilor",
        "Viilor", "Dealului", "Munților", "Pădurilor", "Izvorului"
    ]
    
    for person in oameni_data:
        # Split name into first and last
        name_parts = person["name"].split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else "Unknown"
        
        # Generate unique identifiers
        cnp = generate_cnp(person["age"])
        email = f"{first_name.lower()}.{last_name.lower().replace(' ', '')}@farmworkers.ro"
        phone = f"07{random.randint(10000000, 99999999)}"
        
        # Select random county, city, and street
        county = random.choice(counties)
        city = random.choice(cities)
        street = random.choice(streets)
        address = f"Str. {street} nr. {random.randint(1, 200)}, {city}, Jud. {county}"
        
        # Create farmer document
        farmer_doc = {
            "first_name": first_name,
            "last_name": last_name,
            "cnp": cnp,
            "email": email,
            "phone": phone,
            "age": person["age"],
            "role": person["role"],
            "payday": person["payday"],
            "experience_years": random.randint(1, min(person["age"] - 18, 30)),
            "experience_level": random.choices(
                ["beginner", "intermediate", "advanced", "expert"],
                weights=[15, 35, 35, 15]  # More realistic distribution
            )[0],
            "total_parcels": random.choices(
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15],
                weights=[10, 20, 25, 20, 10, 5, 4, 3, 1, 1, 0.5, 0.5]
            )[0],
            "total_land_area": round(random.uniform(0.5, 50.0), 2),
            "has_equipment": random.choices([True, False], weights=[60, 40])[0],
            "has_irrigation": random.choices([True, False], weights=[45, 55])[0],
            "has_storage": random.choices([True, False], weights=[55, 45])[0],
            "county": county,
            "city": city,
            "address": address,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert farmer
        result = await farmers_collection.insert_one(farmer_doc)
        mongodb_id = str(result.inserted_id)
        worker_id_to_mongodb_id[person["id"]] = mongodb_id
        
        print(f"[+] Created farmer: {first_name} {last_name} (original_id={person['id']} -> MongoDB _id={mongodb_id})")
    
    print(f"\n[+] Successfully created {len(oameni_data)} farmers")
    print(f"[+] Worker ID mapping created: {len(worker_id_to_mongodb_id)} entries")
    
    return worker_id_to_mongodb_id


async def load_harvest_logs(db, ferma_data, worker_mapping):
    """Load harvest_logs collection from ferma.json"""
    harvest_collection = db.harvest_logs
    
    print(f"\n{'='*60}")
    print(f"LOADING HARVEST LOGS FROM ferma.json")
    print(f"{'='*60}")
    
    inserted_count = 0
    skipped_count = 0
    
    for idx, log_entry in enumerate(ferma_data, 1):
        # Transform equipment: worker_id → farmer_id
        equipment_transformed = []
        all_worker_ids_valid = True
        
        for eq in log_entry.get("equipment", []):
            worker_id = eq.get("worker_id")
            
            # Check if worker_id exists in mapping
            if worker_id not in worker_mapping:
                print(f"[!] Warning: Log #{idx} - worker_id {worker_id} not found in mapping. Skipping this log.")
                all_worker_ids_valid = False
                break
            
            equipment_transformed.append({
                "equipment_type": eq["equipment_type"],
                "farmer_id": worker_mapping[worker_id],  # Transform to farmer_id
                "work_hours": eq["work_hours"],
                "fuel_consumed_liters": eq["fuel_consumed_liters"]
            })
        
        if not all_worker_ids_valid:
            skipped_count += 1
            continue
        
        # Parse date
        log_date = datetime.strptime(log_entry["date"], "%Y-%m-%d")
        
        # Create harvest log document
        harvest_doc = {
            "date": log_date,
            "notes": log_entry.get("notes"),
            "wheat_sown_hectares": log_entry.get("wheat_sown_hectares", 0.0),
            "sunflower_harvested_hectares": log_entry.get("sunflower_harvested_hectares", 0.0),
            "beans_harvested_hectares": log_entry.get("beans_harvested_hectares", 0.0),
            "tomatoes_harvested_hectares": log_entry.get("tomatoes_harvested_hectares", 0.0),
            "oil_price_per_liter": log_entry.get("oil_price_per_liter", 0.0),
            "equipment": equipment_transformed,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert harvest log
        try:
            await harvest_collection.insert_one(harvest_doc)
            inserted_count += 1
            if inserted_count % 20 == 0:
                print(f"[+] Inserted {inserted_count} harvest logs...")
        except Exception as e:
            print(f"[-] Error inserting log #{idx} for date {log_entry['date']}: {e}")
            skipped_count += 1
    
    print(f"\n[+] Successfully inserted {inserted_count} harvest logs")
    if skipped_count > 0:
        print(f"[!] Skipped {skipped_count} logs due to errors")


async def main():
    """Main function to load database"""
    print("\n" + "="*60)
    print("DATABASE LOADING SCRIPT")
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
    
    # Load JSON files
    print("\n[*] Loading JSON files...")
    base_path = Path(__file__).parent.parent / "to_add_in_database"
    
    with open(base_path / "oameni.json", "r", encoding="utf-8") as f:
        oameni_data = json.load(f)
    print(f"[+] Loaded {len(oameni_data)} workers from oameni.json")
    
    with open(base_path / "ferma.json", "r", encoding="utf-8") as f:
        ferma_data = json.load(f)
    print(f"[+] Loaded {len(ferma_data)} harvest logs from ferma.json")
    
    # Step 1: Load farmers
    worker_mapping = await load_farmers(db, oameni_data)
    
    # Step 2: Load harvest logs
    await load_harvest_logs(db, ferma_data, worker_mapping)
    
    # Summary
    print("\n" + "="*60)
    print("DATABASE LOADING COMPLETE!")
    print("="*60)
    print(f"[+] Farmers created: {len(worker_mapping)}")
    print(f"[+] Check your MongoDB to verify the data")
    print("\n[*] Next steps:")
    print("  - Visit http://localhost:8000/api/docs")
    print("  - Test GET /api/v1/farmers/ to see all farmers")
    print("  - Test GET /api/v1/harvest-logs/ to see all harvest logs")
    print("="*60 + "\n")
    
    # Close connection
    client.close()


if __name__ == "__main__":
    asyncio.run(main())

