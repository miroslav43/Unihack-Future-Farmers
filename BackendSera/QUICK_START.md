# ⚡ Quick Start - ESP32 Greenhouse Control

## 🚀 Start în 3 Pași

### 1️⃣ Instalare

```bash
cd BackendSera
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2️⃣ Configurare ESP32

Editează `.env` cu IP-ul ESP32:

```env
ESP32_HOST=192.168.1.150  # Sau esp-multi.local
```

### 3️⃣ Pornește Serverul

```bash
python main.py
```

API disponibil la: **http://localhost:8001/docs**

## 📱 Test Rapid din Terminal

```bash
# Health check
curl http://localhost:8000/motors/health

# Status motoare
curl http://localhost:8000/motors/status

# Mișcă motor
curl -X POST http://localhost:8000/motors/move \
  -H "Content-Type: application/json" \
  -d '{"roof_left":{"cm":20,"speed":5,"dir":1}}'

# Stop toate
curl -X POST http://localhost:8000/motors/stop \
  -H "Content-Type: application/json" \
  -d '{"motors":"all"}'
```

## 🐍 Test Rapid din Python

```python
import requests

BASE = "http://localhost:8001"

# 1. Check health
print(requests.get(f"{BASE}/motors/health").json())

# 2. Mișcă motor
print(requests.post(f"{BASE}/motors/move", 
    json={"roof_left": {"cm": 10, "speed": 5, "dir": 1}}).json())

# 3. Status
print(requests.get(f"{BASE}/motors/status").json())

# 4. Stop
print(requests.post(f"{BASE}/motors/stop", 
    json={"motors": "all"}).json())
```

## 🧪 Suite Complete de Teste

```bash
# Rulează toate testele
python test_api.py

# Rulează exemplele practice
python examples.py
```

## 📚 Documentație Completă

- **README.md** - Documentație completă
- **USAGE_GUIDE.md** - Ghid de utilizare detaliat
- **examples.py** - 10 exemple practice
- **Swagger UI** - http://localhost:8000/docs

## 🎯 Rutele Principale

| Metodă | Endpoint | Descriere |
|--------|----------|-----------|
| POST | `/motors/move` | Mișcă motoare |
| POST | `/motors/stop` | Oprește motoare |
| POST | `/motors/emergency-stop` | Stop urgență |
| GET | `/motors/status` | Status motoare |
| POST | `/motors/config` | Configurare |
| GET | `/motors/health` | Health check |

## 🏗️ Structura Proiectului

```
BackendSera/
├── main.py              # 🚀 Start aici
├── config.py            # ⚙️  Configurări
├── requirements.txt     # 📦 Dependențe
├── .env                 # 🔐 Configurare ESP32
├── models/
│   └── motor_models.py  # 📋 Modele Pydantic
├── services/
│   └── esp32_service.py # 📡 Comunicare ESP32
├── routes/
│   └── motor_routes.py  # 🛣️  API Routes
├── test_api.py          # 🧪 Suite de teste
├── examples.py          # 📖 10 exemple
└── README.md            # 📚 Documentație
```

## 🔧 Troubleshooting Rapid

**API nu pornește?**
```bash
# Asigură-te că serverul rulează pe port 80011 e liber
lsof -ti:80011
# Sau schimbă portul în main.py
```

**ESP32 offline?**
```bash
# Găsește IP-ul ESP32
ping esp-multi.local
# Sau verifică Serial Monitor

# Testează direct ESP32
curl http://192.168.1.150:8080/api/status
```

**Erori Python?**
```bash
# Reinstalează dependențe
pip install --upgrade -r requirements.txt
```

## 🎓 Next Steps

1. ✅ Citește **README.md** pentru detalii complete
2. ✅ Explorează **examples.py** pentru cod reutilizabil
3. ✅ Testează cu **test_api.py**
4. ✅ Integrează în aplicația ta

## 📞 Help

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Status API: http://localhost:8000/health
