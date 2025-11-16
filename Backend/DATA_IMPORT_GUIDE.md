# 🌾 Ghid Import Date - Farmer Assessment System

## Prezentare Generală

Acest ghid explică cum să imporți datele din fișierele JSON (`oameni.json` și `ferma.json`) în baza de date MongoDB.

## Modificări Aduse Sistemului

### 1. **Model Farmer Extins**
Am adăugat următoarele câmpuri noi în modelul `Farmer`:
- `worker_id` (int, opțional) - ID-ul lucrătorului din `oameni.json`
- `role` (string, opțional) - Rolul: "Farm Manager", "Tractor Driver", etc.
- `payday` (int, opțional) - Ziua din lună pentru plată (1-31)

### 2. **Model Nou: HarvestLog**
Am creat un model complet nou pentru loguri zilnice de recoltă:
- Data operațiunilor
- Note zilnice (ex: "Normal", "Weekend", "Ploaie")
- Hectare semănate/recoltate pentru fiecare cultură
- Preț combustibil
- Lista echipamentelor folosite cu detalii despre:
  - Tip echipament
  - ID lucrător operator
  - Ore de lucru
  - Combustibil consumat

### 3. **Endpoints Noi**

#### Harvest Logs
```
GET    /api/v1/harvest-logs              - Listă loguri
GET    /api/v1/harvest-logs/{id}         - Log specific
GET    /api/v1/harvest-logs/date/{date}  - Log pentru o dată
POST   /api/v1/harvest-logs              - Creare log nou
PUT    /api/v1/harvest-logs/{id}         - Actualizare log
DELETE /api/v1/harvest-logs/{id}         - Ștergere log

GET    /api/v1/harvest-logs/statistics/overview   - Statistici generale
GET    /api/v1/harvest-logs/statistics/equipment  - Statistici echipamente
```

## Cum să Imporți Datele

### Pasul 1: Verifică Fișierele
Asigură-te că ai fișierele în directorul corect:
```
Backend/
  └── to_add_in_database/
      ├── oameni.json    (50 de lucrători)
      └── ferma.json     (122 de zile de loguri)
```

### Pasul 2: Verifică Conexiunea MongoDB
În fișierul `.env`, asigură-te că ai:
```env
MONGO_API_KEY=mongodb+srv://user:pass@cluster...
DATABASE_NAME=farmer_assessment_db
```

### Pasul 3: Rulează Scriptul de Import
```bash
# Din directorul Backend
python scripts/import_seed_data.py
```

### Pasul 4: Verifică Rezultatele
Scriptul va afișa:
```
==============================================================
🌾 SEED DATA IMPORT SCRIPT
==============================================================
Loading to_add_in_database/oameni.json...
✓ Loaded 50 records from oameni.json
Loading to_add_in_database/ferma.json...
✓ Loaded 122 records from ferma.json

🔌 Connecting to MongoDB...
✓ Connected to MongoDB

📥 Importing workers as farmers...
✓ Farmers: 50 inserted, 0 updated

📥 Importing harvest logs...
✓ Harvest logs: 122 inserted, 0 updated

==============================================================
📊 IMPORT SUMMARY
==============================================================
Workers/Farmers: 50 inserted, 0 updated
Harvest Logs:    122 inserted, 0 updated
Total Records:   172 new, 0 updated
==============================================================
✅ Import completed successfully!
```

## Structura Datelor Importate

### Farmers (din oameni.json)
```json
{
  "_id": "...",
  "first_name": "Ion",
  "last_name": "Popescu",
  "worker_id": 1,
  "role": "Farm Manager",
  "age": 45,
  "payday": 15,
  "cnp": "...",
  "email": "ion.popescu@farm.ro",
  "phone": "0700000001",
  "experience_years": 25,
  "experience_level": "intermediate",
  "has_equipment": true,
  ...
}
```

### Harvest Logs (din ferma.json)
```json
{
  "_id": "...",
  "date": "2025-05-01T00:00:00",
  "notes": "Normal",
  "wheat_sown_hectares": 8.57,
  "sunflower_harvested_hectares": 0.82,
  "beans_harvested_hectares": 1.23,
  "tomatoes_harvested_hectares": 0.62,
  "oil_price_per_liter": 6.81,
  "equipment": [
    {
      "equipment_type": "Tractor",
      "worker_id": 28,
      "work_hours": 0.71,
      "fuel_consumed_liters": 16.3
    },
    {
      "equipment_type": "Wheat Harvester",
      "worker_id": 5,
      "work_hours": 2.0,
      "fuel_consumed_liters": 92.3
    }
  ],
  "created_at": "...",
  "updated_at": "..."
}
```

## Testare API-ului

### 1. Verifică Farmers Importați
```bash
curl http://localhost:8000/api/v1/farmers
```

### 2. Caută un Farmer după worker_id
Folosind serviciul, poți căuta farmers după `worker_id` pentru a vedea corespondența cu datele din echipamente.

### 3. Verifică Harvest Logs
```bash
# Toate logurile
curl http://localhost:8000/api/v1/harvest-logs

# Log pentru o dată specifică
curl http://localhost:8000/api/v1/harvest-logs/date/2025-05-01

# Statistici generale
curl http://localhost:8000/api/v1/harvest-logs/statistics/overview

# Statistici echipamente
curl http://localhost:8000/api/v1/harvest-logs/statistics/equipment
```

### 4. Filtrare pe Interval de Date
```bash
curl "http://localhost:8000/api/v1/harvest-logs?start_date=2025-05-01&end_date=2025-05-31"
```

## Cross-Reference între Date

Poți face corelații între:
- **Worker ID** din `equipment` → **worker_id** din `farmers`
- **Date** → **harvest_logs.date**
- **Equipment usage** → **Statistici pe lucrător**

Exemplu: Vezi ce echipamente a folosit lucrătorul cu ID 28:
```python
# În harvest logs, caută în toate equipment arrays
# unde equipment.worker_id == 28
```

## Re-import (Idempotență)

Scriptul este **idempotent** - poți să-l rulezi de mai multe ori:
- Înregistrările existente vor fi actualizate (nu duplicate)
- Logurile sunt identificate unic după dată
- Farmers sunt identificați după `worker_id`

## Erori Comune

### "File not found"
- Verifică că ești în directorul `Backend`
- Verifică că directorul `to_add_in_database` există

### "Connection failed"
- Verifică `MONGO_API_KEY` în `.env`
- Testează conexiunea manual cu MongoDB Compass

### "Duplicate key error"
- Normal la re-import - scriptul va actualiza înregistrările existente
- CNP-urile generate sunt unice per worker_id

## Next Steps

După import, poți:
1. Construi dashboard-uri cu statistici
2. Analiza eficiența lucrătorilor (ore vs. combustibil)
3. Corela performanța pe tip de echipament
4. Genera rapoarte pe perioade
5. Identifica pattern-uri sezoniere în date

## Support

Pentru probleme:
1. Verifică logs-urile scriptului
2. Testează conexiunea la MongoDB
3. Verifică formatul fișierelor JSON
4. Review scriptul în `scripts/import_seed_data.py`

