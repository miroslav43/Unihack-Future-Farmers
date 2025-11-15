# 🧪 Ghid Complet de Testare - Sistem Modular Fermieri

## 🚀 Pornire Rapidă

### 1. Pornește Backend-ul
```bash
cd Backend
python run.py
```

**✅ Verificare:** Backend rulează pe http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- Health: http://localhost:8000/health

---

## 📝 Testare Completă - Pas cu Pas

### PASUL 1: Creează un Fermier

```bash
curl -X POST http://localhost:8000/api/v1/farmers/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Ion",
    "last_name": "Popescu",
    "cnp": "1800101123456",
    "email": "ion.test@gmail.com",
    "phone": "0712345678",
    "age": 45,
    "experience_years": 20,
    "experience_level": "advanced",
    "total_parcels": 3,
    "total_land_area": 15.5,
    "has_equipment": true,
    "has_irrigation": true,
    "has_storage": true,
    "county": "Ilfov",
    "city": "Bucuresti",
    "address": "Str. Agricultorilor nr. 10"
  }'
```

**📝 IMPORTANT:** Salvează `_id` din răspuns - îl vei folosi în toate testele următoare!

---

### PASUL 2: Testează Orders (Comenzi)

#### 2.1 Crează o comandă
```bash
curl -X POST http://localhost:8000/api/v1/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "FARMER_ID_AICI",
    "customer_name": "Restaurant Gradina",
    "customer_phone": "0722334455",
    "customer_email": "contact@restaurant.ro",
    "items": [
      {
        "product_name": "Roșii",
        "quantity": 50,
        "unit": "kg",
        "price_per_unit": 5.0,
        "total_price": 250.0
      },
      {
        "product_name": "Castraveți",
        "quantity": 30,
        "unit": "kg",
        "price_per_unit": 4.5,
        "total_price": 135.0
      }
    ],
    "total_amount": 385.0,
    "delivery_address": "Str. Unirii nr. 15, Bucuresti",
    "notes": "Livrare dimineață, 8-10"
  }'
```

#### 2.2 Mai crează câteva comenzi pentru statistici
```bash
# Comandă 2
curl -X POST http://localhost:8000/api/v1/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "FARMER_ID_AICI",
    "customer_name": "Piața Centrală",
    "customer_phone": "0733445566",
    "items": [
      {
        "product_name": "Ardei",
        "quantity": 20,
        "unit": "kg",
        "price_per_unit": 6.0,
        "total_price": 120.0
      }
    ],
    "total_amount": 120.0
  }'

# Comandă 3
curl -X POST http://localhost:8000/api/v1/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "FARMER_ID_AICI",
    "customer_name": "Magazin Bio",
    "items": [
      {
        "product_name": "Salată",
        "quantity": 15,
        "unit": "kg",
        "price_per_unit": 8.0,
        "total_price": 120.0
      }
    ],
    "total_amount": 120.0
  }'
```

#### 2.3 Verifică comenzile
```bash
# Comenzi de astăzi
curl http://localhost:8000/api/v1/orders/farmer/FARMER_ID_AICI/today

# Toate comenzile
curl http://localhost:8000/api/v1/orders/farmer/FARMER_ID_AICI

# Statistici
curl http://localhost:8000/api/v1/orders/farmer/FARMER_ID_AICI/statistics
```

---

### PASUL 3: Testează Inventory (Stoc)

#### 3.1 Adaugă produse în stoc
```bash
# Roșii
curl -X POST http://localhost:8000/api/v1/inventory/ \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "FARMER_ID_AICI",
    "product_name": "Roșii cherry",
    "category": "vegetables",
    "quantity": 150,
    "unit": "kg",
    "price_per_unit": 6.5,
    "location": "Sera 1"
  }'

# Castraveți
curl -X POST http://localhost:8000/api/v1/inventory/ \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "FARMER_ID_AICI",
    "product_name": "Castraveți",
    "category": "vegetables",
    "quantity": 80,
    "unit": "kg",
    "price_per_unit": 4.0,
    "location": "Sera 2"
  }'

# Mere
curl -X POST http://localhost:8000/api/v1/inventory/ \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "FARMER_ID_AICI",
    "product_name": "Mere Golden",
    "category": "fruits",
    "quantity": 200,
    "unit": "kg",
    "price_per_unit": 3.5,
    "location": "Depozit frigorific"
  }'
```

#### 3.2 Verifică inventarul
```bash
# Tot inventarul
curl http://localhost:8000/api/v1/inventory/farmer/FARMER_ID_AICI

# Valoare totală stoc
curl http://localhost:8000/api/v1/inventory/farmer/FARMER_ID_AICI/value

# Pe categorii
curl http://localhost:8000/api/v1/inventory/farmer/FARMER_ID_AICI/by-category
```

---

### PASUL 4: Testează Crops (Culturi)

#### 4.1 Adaugă culturi
```bash
# Cultură de tomate (gata de recoltat)
curl -X POST http://localhost:8000/api/v1/crops/ \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "FARMER_ID_AICI",
    "crop_name": "Tomate",
    "area_hectares": 2.5,
    "planting_date": "2024-05-01",
    "expected_harvest_date": "2024-11-10",
    "estimated_yield": 45
  }'

# Cultură de castraveți (în creștere)
curl -X POST http://localhost:8000/api/v1/crops/ \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "FARMER_ID_AICI",
    "crop_name": "Castraveți",
    "area_hectares": 1.8,
    "planting_date": "2024-06-15",
    "expected_harvest_date": "2025-01-15",
    "estimated_yield": 30
  }'

# Cultură de porumb (planificată)
curl -X POST http://localhost:8000/api/v1/crops/ \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "FARMER_ID_AICI",
    "crop_name": "Porumb",
    "area_hectares": 5.0,
    "planting_date": "2025-03-01",
    "expected_harvest_date": "2025-08-15",
    "estimated_yield": 80
  }'
```

#### 4.2 Update status cultură
```bash
# Update prima cultură la status PLANTED
curl -X PUT http://localhost:8000/api/v1/crops/CROP_ID_AICI \
  -H "Content-Type: application/json" \
  -d '{
    "status": "planted"
  }'
```

#### 4.3 Verifică culturile
```bash
# Toate culturile
curl http://localhost:8000/api/v1/crops/farmer/FARMER_ID_AICI

# Culturi active
curl http://localhost:8000/api/v1/crops/farmer/FARMER_ID_AICI/active

# Gata de recoltat
curl http://localhost:8000/api/v1/crops/farmer/FARMER_ID_AICI/harvest-ready

# Statistici
curl http://localhost:8000/api/v1/crops/farmer/FARMER_ID_AICI/statistics
```

---

### PASUL 5: Testează Tasks (Task-uri)

#### 5.1 Crează task-uri
```bash
# Task pentru astăzi - prioritate HIGH
curl -X POST http://localhost:8000/api/v1/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "FARMER_ID_AICI",
    "title": "Udare sera 1",
    "description": "Sistem de udare automată trebuie verificat",
    "priority": "high",
    "due_date": "2024-11-15"
  }'

# Task pentru mâine - prioritate MEDIUM
curl -X POST http://localhost:8000/api/v1/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "FARMER_ID_AICI",
    "title": "Verificare sol sera 2",
    "description": "Test pH și nutrienți",
    "priority": "medium",
    "due_date": "2024-11-16"
  }'

# Task întârziat - prioritate URGENT
curl -X POST http://localhost:8000/api/v1/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "FARMER_ID_AICI",
    "title": "Reparație sistem irigație",
    "description": "Scurgere la valva principală",
    "priority": "urgent",
    "due_date": "2024-11-10"
  }'

# Task low priority
curl -X POST http://localhost:8000/api/v1/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "FARMER_ID_AICI",
    "title": "Inventar echipament",
    "description": "Verificare și catalogare unelte",
    "priority": "low",
    "due_date": "2024-11-20"
  }'
```

#### 5.2 Update task (marchează ca done)
```bash
curl -X PUT http://localhost:8000/api/v1/tasks/TASK_ID_AICI \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed"
  }'
```

#### 5.3 Verifică task-urile
```bash
# Task-uri de astăzi
curl http://localhost:8000/api/v1/tasks/farmer/FARMER_ID_AICI/today

# Task-uri întârziate
curl http://localhost:8000/api/v1/tasks/farmer/FARMER_ID_AICI/overdue

# Toate task-urile pending
curl http://localhost:8000/api/v1/tasks/farmer/FARMER_ID_AICI/pending

# Statistici
curl http://localhost:8000/api/v1/tasks/farmer/FARMER_ID_AICI/statistics
```

---

### PASUL 6: 🤖 Testează API Conversațional (CRUCIAL!)

Acesta este endpoint-ul pentru integrarea cu agenți AI vocali!

#### 6.1 Întrebări despre comenzi
```bash
# "Ce comenzi am astăzi?"
curl -X POST http://localhost:8000/api/v1/conversational/query \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "FARMER_ID_AICI",
    "query": "ce comenzi am astazi?"
  }'

# "Câte comenzi am făcut în ultima lună?"
curl -X POST http://localhost:8000/api/v1/conversational/query \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "FARMER_ID_AICI",
    "query": "cate comenzi am facut in ultima luna?"
  }'

# "Cât am vândut săptămâna asta?"
curl -X POST http://localhost:8000/api/v1/conversational/query \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "FARMER_ID_AICI",
    "query": "cat am vandut saptamana asta?"
  }'
```

#### 6.2 Întrebări despre culturi
```bash
# "Ce culturi am gata de recoltat?"
curl -X POST http://localhost:8000/api/v1/conversational/query \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "FARMER_ID_AICI",
    "query": "ce culturi am gata de recoltat?"
  }'

# "Câte culturi am plantat?"
curl -X POST http://localhost:8000/api/v1/conversational/query \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "FARMER_ID_AICI",
    "query": "cate culturi am plantat?"
  }'
```

#### 6.3 Întrebări despre task-uri
```bash
# "Ce trebuie să fac astăzi?"
curl -X POST http://localhost:8000/api/v1/conversational/query \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "FARMER_ID_AICI",
    "query": "ce trebuie sa fac astazi?"
  }'

# "Am task-uri întârziate?"
curl -X POST http://localhost:8000/api/v1/conversational/query \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "FARMER_ID_AICI",
    "query": "am taskuri intarziate?"
  }'
```

---

## 📊 Verificare Completă în Swagger UI

1. Deschide: http://localhost:8000/api/docs
2. Toate endpoint-urile sunt disponibile cu documentație
3. Poți testa direct din browser cu butonul "Try it out"

---

## 🎯 Checklist Final

- [ ] Backend pornește fără erori
- [ ] Health check funcționează
- [ ] Fermier creat în MongoDB
- [ ] 3+ comenzi create
- [ ] 3+ produse în inventar
- [ ] 3+ culturi adăugate
- [ ] 4+ task-uri create
- [ ] API conversațional răspunde corect la 5+ întrebări diferite
- [ ] Swagger UI se deschide și arată toate endpoint-urile

---

## 🐛 Troubleshooting

### Backend nu pornește
```bash
# Verifică Python
python --version  # Trebuie 3.9+

# Reinstalează dependințe
pip install -r requirements.txt

# Verifică MongoDB connection
# Editează .env dacă e nevoie
```

### Eroare "Farmer not found"
- Verifică că folosești `_id` corect din răspunsul de la creare fermier
- ID-ul trebuie să fie string, nu ObjectId

### API conversațional nu înțelege query-ul
- Încearcă cu keywords clare: "comenzi", "culturi", "task"
- Vezi `/api/v1/conversational/intents` pentru exemple

---

## 🚀 Next Steps După Testare

1. **Integrare cu AI Agent vocal:**
   - Speech-to-text → `/api/v1/conversational/query`
   - Text-to-speech ← `response.answer`

2. **Frontend components:**
   - Dashboard cu statistici
   - Liste interactive pentru orders/crops/tasks
   - Voice input button

3. **Analytics avansate:**
   - Grafice venituri
   - Predicții recoltă
   - Optimizare task-uri

---

**✅ SISTEM COMPLET FUNCȚIONAL!**

Toate componentele sunt modulare și independente. Fiecare poate fi extinsă sau modificată fără a afecta restul sistemului.
