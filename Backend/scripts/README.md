# Data Import Scripts

This directory contains scripts for importing seed data into the MongoDB database.

## Available Scripts

### `import_seed_data.py`

Imports workers and harvest logs from JSON files into the database.

**What it does:**
- Imports workers from `to_add_in_database/oameni.json` as farmers
- Imports daily harvest logs from `to_add_in_database/ferma.json`
- Creates or updates existing records (idempotent)
- Creates proper relationships between workers and equipment usage

**Usage:**

```bash
# Make sure you're in the project root directory
cd Backend

# Run the import script
python scripts/import_seed_data.py
```

**Requirements:**
- MongoDB connection configured in `.env` file
- `to_add_in_database/oameni.json` file present
- `to_add_in_database/ferma.json` file present

## Data Mapping

### Workers (oameni.json) → Farmers Collection

The script maps worker data to farmer records:

| Source Field | Target Field | Notes |
|--------------|--------------|-------|
| `id` | `worker_id` | Used for cross-referencing |
| `name` | `first_name`, `last_name` | Split by space |
| `age` | `age` | Direct mapping |
| `payday` | `payday` | Day of month for payment |
| `role` | `role` | Job role/title |
| - | `cnp` | Generated (demo purposes) |
| - | `email` | Generated from name |
| - | `phone` | Generated from worker_id |

### Harvest Logs (ferma.json) → Harvest Logs Collection

The script imports daily operational logs:

- `date` - Date of operations
- `notes` - Daily notes (e.g., "Normal", "Weekend", "Rain")
- Crop metrics (wheat sown, sunflower/beans/tomatoes harvested in hectares)
- `oil_price_per_liter` - Fuel price for that day
- `equipment` - Array of equipment usage records:
  - `equipment_type` - Type of machinery
  - `worker_id` - Worker operating the equipment
  - `work_hours` - Hours worked
  - `fuel_consumed_liters` - Fuel consumption

## Notes

- The script is **idempotent** - running it multiple times won't create duplicates
- Existing records are updated with new data
- Worker IDs from equipment logs can be cross-referenced with farmer records
- The script automatically creates database indexes for optimal performance

## Troubleshooting

**Connection Error:**
- Check your `.env` file has correct `MONGO_API_KEY`
- Verify MongoDB cluster is accessible

**File Not Found:**
- Ensure JSON files are in `to_add_in_database/` directory
- Check file names are exactly `oameni.json` and `ferma.json`

**Import Errors:**
- Check JSON file format is valid
- Review error messages for specific records that failed
- Script will continue importing other records if one fails

