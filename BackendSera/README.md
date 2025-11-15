# 🏡 Backend FastAPI pentru Control Seră ESP32

Backend REST API construit cu FastAPI pentru controlul sistemelor de seră bazate pe ESP32 cu 4 motoare stepper.

## 📋 Funcționalități

- ✅ Control complet pentru 4 motoare stepper (roof_left, roof_right, axis_x, axis_y)
- ✅ Mișcare precisă în centimetri cu viteză configurabilă
- ✅ Stop individual sau colectiv al motoarelor
- ✅ Emergency stop pentru toate motoarele
- ✅ Monitorizare status în timp real
- ✅ Configurare parametri motoare (mm/rotație, microsteps, viteza max)
- ✅ Validare automată cu Pydantic
- ✅ Documentație interactivă (Swagger UI)
- ✅ Health check pentru ESP32

## 🚀 Instalare Rapidă

### 1. Creează Virtual Environment

```bash
cd BackendSera
python3 -m venv venv
source venv/bin/activate  # Pe Windows: venv\Scripts\activate
```

### 2. Instalează Dependențele

```bash
pip install -r requirements.txt
```

### 3. Configurează .env

```bash
cp .env.example .env
# Editează .env și setează ESP32_HOST cu IP-ul sau hostname-ul ESP32
```

### 4. Pornește Serverul

```bash
python main.py
```

Sau cu uvicorn direct:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API-ul va fi disponibil la: **http://localhost:8000**

Documentație interactivă: **http://localhost:8000/docs**

## 📡 Configurare ESP32

În fișierul `.env` trebuie să setezi IP-ul sau hostname-ul ESP32:

```env
# Variantă 1: Folosind mDNS (dacă funcționează în rețeaua ta)
ESP32_HOST=esp-multi.local

# Variantă 2: IP direct (mai sigur)
ESP32_HOST=192.168.1.100

ESP32_PORT=8080
```

### Cum afli IP-ul ESP32?

1. Uită-te în Serial Monitor când pornești ESP32
2. Verifică în routerul tău lista de dispozitive conectate
3. Folosește `ping esp-multi.local` pentru a testa mDNS

## 🎯 Endpoint-uri API

### 1. **POST** `/motors/move` - Mișcă motoarele

```bash
# Mișcă un singur motor
curl -X POST http://localhost:8000/motors/move \
  -H "Content-Type: application/json" \
  -d '{
    "roof_left": {
      "cm": 20,
      "speed": 5,
      "dir": 1
    }
  }'

# Mișcă mai multe motoare simultan
curl -X POST http://localhost:8000/motors/move \
  -H "Content-Type: application/json" \
  -d '{
    "roof_left": {"cm": 15, "speed": 4, "dir": 1},
    "roof_right": {"cm": 15, "speed": 4, "dir": 1},
    "axis_x": {"cm": 10, "speed": 3, "dir": 0}
  }'
```

**Parametri pentru fiecare motor:**
- `cm` (float): Distanța în centimetri (0-1000)
- `speed` (float): Viteza în cm/s (1-30)
- `dir` (int): Direcție - `1` = înainte, `0` = înapoi

### 2. **POST** `/motors/stop` - Oprește motoarele

```bash
# Oprește motoare specifice
curl -X POST http://localhost:8000/motors/stop \
  -H "Content-Type: application/json" \
  -d '{
    "motors": ["axis_x", "axis_y"]
  }'

# Oprește toate motoarele
curl -X POST http://localhost:8000/motors/stop \
  -H "Content-Type: application/json" \
  -d '{
    "motors": "all"
  }'
```

### 3. **POST** `/motors/emergency-stop` - Emergency Stop

```bash
curl -X POST http://localhost:8000/motors/emergency-stop
```

Oprește **toate motoarele imediat**, fără parametri.

### 4. **GET** `/motors/status` - Status Motoare

```bash
curl http://localhost:8000/motors/status
```

Returnează:
```json
{
  "roof_left": {
    "en": true,
    "sp_cm": 5.0,
    "dir": 1,
    "cm_rem": 12.5,
    "cfg": {
      "mmrev": 40.0,
      "ms": 8,
      "max_cm": 30.0,
      "steps_mm": 40.0
    }
  },
  ...
}
```

### 5. **POST** `/motors/config` - Configurare Motoare

```bash
curl -X POST http://localhost:8000/motors/config \
  -H "Content-Type: application/json" \
  -d '{
    "roof_left": {
      "mm_per_rev": 40.0,
      "microstep": 8,
      "max_speed": 30.0
    }
  }'
```

### 6. **GET** `/motors/health` - Health Check

```bash
curl http://localhost:8000/motors/health
```

Verifică dacă ESP32 este accesibil.

## 🐍 Exemple Python

### Exemplu Simplu

```python
import requests

BASE_URL = "http://localhost:8000"

# Mișcă roof_left
response = requests.post(
    f"{BASE_URL}/motors/move",
    json={
        "roof_left": {
            "cm": 20,
            "speed": 5,
            "dir": 1
        }
    }
)
print(response.json())
```

### Exemplu Complet cu httpx (async)

```python
import httpx
import asyncio

async def control_greenhouse():
    async with httpx.AsyncClient() as client:
        base_url = "http://localhost:8000"
        
        # 1. Verifică conexiunea
        health = await client.get(f"{base_url}/motors/health")
        print("Health:", health.json())
        
        # 2. Obține status
        status = await client.get(f"{base_url}/motors/status")
        print("Status:", status.json())
        
        # 3. Mișcă motoarele
        move_response = await client.post(
            f"{base_url}/motors/move",
            json={
                "roof_left": {"cm": 10, "speed": 5, "dir": 1},
                "axis_x": {"cm": 5, "speed": 3, "dir": 0}
            }
        )
        print("Move:", move_response.json())
        
        # 4. Așteaptă puțin
        await asyncio.sleep(2)
        
        # 5. Oprește toate motoarele
        stop_response = await client.post(
            f"{base_url}/motors/stop",
            json={"motors": "all"}
        )
        print("Stop:", stop_response.json())

# Rulează
asyncio.run(control_greenhouse())
```

## 📦 Structura Proiectului

```
BackendSera/
├── main.py                 # Aplicația FastAPI principală
├── config.py              # Configurări (Settings)
├── requirements.txt       # Dependențe Python
├── .env                   # Variabile de mediu (nu se comite)
├── .env.example          # Template pentru .env
├── models/
│   ├── __init__.py
│   └── motor_models.py   # Modele Pydantic
├── services/
│   ├── __init__.py
│   └── esp32_service.py  # Serviciu comunicare ESP32
└── routes/
    ├── __init__.py
    └── motor_routes.py   # Rute API motoare
```

## 🔍 Debugging

### Verifică logs

API-ul loghează toate request-urile și response-urile. Verifică terminalul unde rulează serverul.

### Testează conexiunea ESP32

```bash
curl http://localhost:8000/motors/health
```

Dacă `esp32_reachable` este `false`:
1. Verifică că ESP32 este pornit
2. Verifică că ești în aceeași rețea
3. Ping ESP32: `ping <IP_ESP32>`
4. Verifică `ESP32_HOST` în `.env`

### Testează direct ESP32

```bash
# Test direct către ESP32 (bypassing FastAPI)
curl http://<IP_ESP32>:8080/api/status
```

## 🛠️ Troubleshooting

### Eroare: "Connection refused"

- ESP32 nu este pornit sau nu e în rețea
- IP-ul/hostname-ul greșit în `.env`
- Firewall blochează portul 8080

### Eroare: "Timeout"

- ESP32 e prea încărcat
- Rețeaua e lentă
- Crește `ESP32_TIMEOUT` în `.env`

### mDNS nu funcționează

- Folosește IP direct în loc de `esp-multi.local`
- Pe Windows, mDNS poate necesita Bonjour

## 📚 Documentație Adițională

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔐 Securitate

⚠️ **Atenție**: Acest API nu are autentificare. Pentru producție:

1. Adaugă autentificare (JWT, API keys)
2. Folosește HTTPS
3. Limitează CORS la origini specifice
4. Adaugă rate limiting

## 📝 License

MIT

## 👨‍💻 Autor

Backend dezvoltat pentru sistem de control seră automată cu ESP32.
