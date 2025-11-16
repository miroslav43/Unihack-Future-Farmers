"""Fix unrealistic fuel consumption in harvest logs"""
import sys
import random
from pathlib import Path
from pymongo import MongoClient

sys.path.append(str(Path(__file__).parent.parent))
from app.config.settings import settings

# Realistic fuel consumption rates (liters per hour)
REALISTIC_CONSUMPTION = {
    "Tractor": (8, 15),  # 8-15 L/h
    "Wheat Harvester": (15, 22),  # 15-22 L/h
    "Sunflower Harvester": (15, 22),  # 15-22 L/h
    "Bean Harvester": (12, 20),  # 12-20 L/h
    "Tomato Harvester": (15, 25),  # 15-25 L/h (mai mare pentru echipamente specializate)
    "Other": (10, 18)  # 10-18 L/h
}

def fix_fuel_consumption():
    """Update fuel consumption to realistic values"""
    
    client = MongoClient(settings.MONGO_API_KEY)
    db = client[settings.DATABASE_NAME]
    harvest_collection = db['harvest_logs']
    
    print("Fixing fuel consumption in harvest logs...")
    print("="*80)
    
    logs = list(harvest_collection.find())
    print(f"\nTotal harvest logs: {len(logs)}")
    
    updated_count = 0
    total_equipment = 0
    
    for log in logs:
        log_id = log['_id']
        equipment = log.get('equipment', [])
        
        if not equipment:
            continue
        
        updated_equipment = []
        log_updated = False
        
        for eq in equipment:
            eq_type = eq.get('equipment_type', 'Other')
            work_hours = eq.get('work_hours', 0)
            old_fuel = eq.get('fuel_consumed_liters', 0)
            
            # Get realistic consumption range for this equipment type
            if eq_type in REALISTIC_CONSUMPTION:
                min_rate, max_rate = REALISTIC_CONSUMPTION[eq_type]
            else:
                min_rate, max_rate = REALISTIC_CONSUMPTION["Other"]
            
            # Calculate new realistic fuel consumption
            # Add some variation for realism
            consumption_rate = random.uniform(min_rate, max_rate)
            new_fuel = round(work_hours * consumption_rate, 1)
            
            # Update equipment entry
            eq['fuel_consumed_liters'] = new_fuel
            updated_equipment.append(eq)
            
            total_equipment += 1
            
            if abs(new_fuel - old_fuel) > 0.1:
                log_updated = True
                print(f"  {eq_type}: {old_fuel:.1f}L -> {new_fuel:.1f}L ({work_hours:.1f}h @ {consumption_rate:.1f}L/h)")
        
        if log_updated:
            # Recalculate totals
            total_fuel = sum(eq.get('fuel_consumed_liters', 0) for eq in updated_equipment)
            oil_price = log.get('oil_price_per_liter', 0)
            fuel_cost = round(total_fuel * oil_price, 2)
            
            # Update the log
            harvest_collection.update_one(
                {'_id': log_id},
                {
                    '$set': {
                        'equipment': updated_equipment,
                        'total_fuel_consumed': round(total_fuel, 2),
                        'fuel_cost': fuel_cost
                    }
                }
            )
            updated_count += 1
            print(f"Updated log {log.get('date')}: Total fuel {total_fuel:.1f}L, Cost {fuel_cost:.2f} RON\n")
    
    print("\n" + "="*80)
    print("UPDATE SUMMARY")
    print("="*80)
    print(f"Total logs processed: {len(logs)}")
    print(f"Logs updated: {updated_count}")
    print(f"Total equipment entries: {total_equipment}")
    
    # Show new statistics
    print("\n" + "="*80)
    print("NEW STATISTICS:")
    print("="*80)
    
    logs = list(harvest_collection.find())
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
        print(f"Average fuel per entry: {sum(all_fuel)/len(all_fuel):.1f}L")
        print(f"Max fuel per entry: {max(all_fuel):.1f}L")
        print(f"Min fuel per entry: {min(all_fuel):.1f}L")
        
        if all_consumption_rates:
            print(f"\nAverage consumption rate: {sum(all_consumption_rates)/len(all_consumption_rates):.1f}L/h")
            print(f"Max consumption rate: {max(all_consumption_rates):.1f}L/h")
            print(f"Min consumption rate: {min(all_consumption_rates):.1f}L/h")
    
    print("\n[OK] Fuel consumption fixed successfully!")
    client.close()

if __name__ == "__main__":
    try:
        fix_fuel_consumption()
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

