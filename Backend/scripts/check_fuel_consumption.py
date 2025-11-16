"""Check current fuel consumption in harvest logs"""
import sys
from pathlib import Path
from pymongo import MongoClient

sys.path.append(str(Path(__file__).parent.parent))
from app.config.settings import settings

client = MongoClient(settings.MONGO_API_KEY)
db = client[settings.DATABASE_NAME]
harvest_collection = db['harvest_logs']

print("Checking fuel consumption in harvest logs...")
print("="*80)

logs = list(harvest_collection.find())
print(f"\nTotal harvest logs: {len(logs)}")

if logs:
    print("\nFuel consumption by equipment:\n")
    for log in logs:
        date = log.get('date', 'N/A')
        equipment = log.get('equipment', [])
        
        if equipment:
            print(f"Date: {date}")
            for eq in equipment:
                eq_type = eq.get('equipment_type', 'Unknown')
                work_hours = eq.get('work_hours', 0)
                fuel = eq.get('fuel_consumed_liters', 0)
                
                if work_hours > 0:
                    consumption_per_hour = fuel / work_hours
                    print(f"  - {eq_type}: {fuel:.1f}L in {work_hours:.1f}h = {consumption_per_hour:.1f}L/h")
                else:
                    print(f"  - {eq_type}: {fuel:.1f}L in {work_hours:.1f}h")
            print()

    # Statistics
    all_fuel = []
    all_consumption_rates = []
    
    for log in logs:
        for eq in log.get('equipment', []):
            fuel = eq.get('fuel_consumed_liters', 0)
            work_hours = eq.get('work_hours', 0)
            if fuel > 0:
                all_fuel.append(fuel)
                if work_hours > 0:
                    all_consumption_rates.append(fuel / work_hours)
    
    if all_fuel:
        print("\n" + "="*80)
        print("STATISTICS:")
        print("="*80)
        print(f"Total equipment entries: {len(all_fuel)}")
        print(f"Average fuel per entry: {sum(all_fuel)/len(all_fuel):.1f}L")
        print(f"Max fuel per entry: {max(all_fuel):.1f}L")
        print(f"Min fuel per entry: {min(all_fuel):.1f}L")
        
        if all_consumption_rates:
            print(f"\nAverage consumption rate: {sum(all_consumption_rates)/len(all_consumption_rates):.1f}L/h")
            print(f"Max consumption rate: {max(all_consumption_rates):.1f}L/h")
            print(f"Min consumption rate: {min(all_consumption_rates):.1f}L/h")

client.close()

