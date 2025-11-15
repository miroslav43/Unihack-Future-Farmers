# 🏡 Ghid Complet - Control Seră cu Grilă 4x3

## 📋 Ce am implementat

✅ Backend FastAPI cu endpoint-uri pentru poziționare absolută  
✅ Frontend React cu grilă 4x3 (12 poziții)  
✅ Calculul automat al mișcărilor relative  
✅ Buton HOME pentru revenire la centru  
✅ Status real-time și feedback vizual  

## 🎯 Specificații Seră

- **Dimensiuni**: 45cm (lățime) x 33cm (înălțime)
- **Grilă**: 4 coloane x 3 rânduri = **12 poziții**
- **Poziția HOME (centru)**: X=22.5cm, Y=16.5cm
- **ESP32 IP**: 10.249.174.190:8080 ✅ CONECTAT

## 📐 Harta Pozițiilor (Grilă 4x3)

```
    COL1      COL2      COL3      COL4
    (5.6cm)   (16.9cm)  (28.1cm)  (39.4cm)

RÂ  [  1  ]   [  2  ]   [  3  ]   [  4  ]   Y = 5.5cm
ND1

RÂ  [  5  ]   [  6  ]   [  7  ]   [  8  ]   Y = 16.5cm  ← CENTRU pe Y
ND2                    ↑         ↑
                    CENTRU    CENTRU
                    pe X      pe X

RÂ  [  9  ]   [ 10  ]   [ 11  ]   [ 12  ]   Y = 27.5cm
ND3
```

### Poziții exacte (X, Y):

| Buton | Coordonate | Descriere |
|-------|-----------|-----------|
| 1 | (5.6, 5.5) | Colț stânga-sus |
| 2 | (16.9, 5.5) | Sus, aproape centru |
| 3 | (28.1, 5.5) | Sus, aproape centru |
| 4 | (39.4, 5.5) | Colț dreapta-sus |
| 5 | (5.6, 16.5) | Stânga, centru pe Y |
| 6 | (16.9, 16.5) | **Aproape centru complet** |
| 7 | (28.1, 16.5) | **Aproape centru complet** |
| 8 | (39.4, 16.5) | Dreapta, centru pe Y |
| 9 | (5.6, 27.5) | Colț stânga-jos |
| 10 | (16.9, 27.5) | Jos, aproape centru |
| 11 | (28.1, 27.5) | Jos, aproape centru |
| 12 | (39.4, 27.5) | Colț dreapta-jos |

**HOME** = (22.5, 16.5) - Exact centrul geometric al serei

## 🚀 Pornire Rapidă

### 1. Pornește Backend-ul (dacă nu e pornit)

```bash
cd BackendSera
source venv/bin/activate
python main.py
```

Backend disponibil la: **http://localhost:8001**

### 2. Pornește Frontend-ul

```bash
cd Frontend
npm run dev
# sau
bun dev
```

Frontend disponibil la: **http://localhost:5173** (sau portul Vite)

### 3. Accesează Control Seră

Deschide browser la: **http://localhost:5173/sera**

## 🎮 Cum Folosești Grila

### Click pe Poziție (ex: butonul 12)

1. **Click pe butonul "12"**
2. Backend calculează automat:
   - Poziția target: (39.375cm, 27.5cm)
   - Poziția curentă: (22.5cm, 16.5cm) - dacă ești la HOME
   - Delta X = 39.375 - 22.5 = **16.875cm** (direcție: înainte)
   - Delta Y = 27.5 - 16.5 = **11cm** (direcție: înainte)
3. Trimite comenzi către ESP32:
   ```json
   {
     "axis_x": {"cm": 16.875, "speed": 8, "dir": 1},
     "axis_y": {"cm": 11, "speed": 8, "dir": 1}
   }
   ```
4. Actualizează poziția curentă în state

### Click pe HOME

- Te duce automat la centru (22.5cm, 16.5cm) de oriunde ai fi

### Emergency STOP

- Oprește toate motoarele imediat

## 🔌 Configurare ESP32

### În Backend (.env)

```env
ESP32_HOST=10.249.174.190  # IP-ul ESP32 (pe net)
ESP32_PORT=8080
ESP32_TIMEOUT=10
```

### În Frontend (greenhouseAPI.ts)

```typescript
const API_BASE_URL = 'http://localhost:8001';
```

## 📡 API Endpoints

### POST `/motors/position` - Poziționare absolută

```bash
curl -X POST http://localhost:8001/motors/position \
  -H "Content-Type: application/json" \
  -d '{
    "target_x": 28.125,
    "target_y": 27.5,
    "current_x": 22.5,
    "current_y": 16.5,
    "speed": 8
  }'
```

**Response:**
```json
{
  "moved": ["axis_x", "axis_y"],
  "delta_x": 5.625,
  "delta_y": 11.0,
  "new_position": {"x": 28.125, "y": 27.5}
}
```

### POST `/motors/home` - Întoarcere la centru

```bash
curl -X POST http://localhost:8001/motors/home \
  -H "Content-Type: application/json" \
  -d '{
    "current_x": 39.375,
    "current_y": 27.5,
    "speed": 8
  }'
```

### POST `/motors/emergency-stop` - Stop urgență

```bash
curl -X POST http://localhost:8001/motors/emergency-stop
```

### GET `/motors/health` - Check conexiune

```bash
curl http://localhost:8001/motors/health
```

**Response:**
```json
{
  "status": "ok",
  "esp32_host": "172.20.10.7:8080",
  "esp32_reachable": true
}
```

## 🧪 Testare Fără ESP32

Chiar dacă ESP32 nu e conectat, poți testa:

1. **UI-ul funcționează** - grila se afișează corect
2. **Calculele sunt corecte** - vezi în console log-urile
3. **API-ul răspunde** - primești erori clare când ESP32 lipsește

## 🔍 Debugging

### Check Backend

```bash
# Verifică dacă rulează
curl http://localhost:8001/health

# Verifică conexiunea ESP32
curl http://localhost:8001/motors/health
```

### Check Frontend

1. Deschide Developer Tools (F12)
2. Tab Console - vezi request-urile API
3. Tab Network - vezi răspunsurile

### Logs Backend

Backend-ul loghează toate operațiunile:

```
2025-11-15 13:17:14,421 - main - INFO - 📡 ESP32 Target: 172.20.10.7:8080
[API] Move to position: target=(28.125, 27.5), current=(22.5, 16.5), delta=(5.63, 11.00)
[API] Motors moved: ['axis_x', 'axis_y']
```

## 🎨 Features UI

- ✅ **Status real-time** - vezi poziția curentă X, Y
- ✅ **Visual feedback** - butonul curent e highlighted
- ✅ **Loading state** - animație când se mișcă
- ✅ **Error handling** - mesaje clare de eroare
- ✅ **Connection status** - indicator conectat/deconectat
- ✅ **Responsive design** - funcționează pe mobile

## 📊 Flow de Date

```
1. USER Click buton "12"
   ↓
2. FRONTEND calculează coordonate (39.375, 27.5)
   ↓
3. API POST /motors/position
   ↓
4. BACKEND calculează delta X, Y
   ↓
5. BACKEND trimite comenzi către ESP32
   ↓
6. ESP32 mișcă motoarele
   ↓
7. FRONTEND actualizează poziția curentă
```

## 🛠️ Troubleshooting

### ESP32 nu răspunde?

1. Verifică că ESP32 e pornit
2. Verifică IP-ul în Serial Monitor
3. Ping ESP32: `ping 10.249.174.190`
4. Test direct: `curl http://10.249.174.190:8080/api/status`

### Frontend nu se conectează la backend?

1. Verifică că backend-ul rulează pe 8001
2. Verifică CORS (ar trebui să fie permisiv)
3. Check console browser pentru erori

### Motoarele nu se mișcă corect?

1. Verifică direcțiile în ESP32 (dir: 1 = înainte, 0 = înapoi)
2. Verifică viteza (1-30 cm/s)
3. Verifică că `mm_per_rev` e setat corect în ESP32

## 📚 Structura Fișierelor

```
Unihack/
├── BackendSera/                # Backend FastAPI
│   ├── main.py                 # Server principal (PORT 8001)
│   ├── .env                    # Config ESP32 (172.20.10.7:8080)
│   ├── routes/
│   │   └── motor_routes.py     # Endpoint-uri + poziționare
│   ├── models/
│   │   └── motor_models.py     # PositionRequest, HomeRequest
│   └── services/
│       └── esp32_service.py    # Comunicare HTTP cu ESP32
│
└── Frontend/
    └── src/
        ├── services/
        │   └── greenhouseAPI.ts    # API Client
        ├── components/
        │   └── GreenhouseControl.tsx  # Componenta grilă 4x3
        └── pages/
            └── ControlSera.tsx     # Pagina /sera
```

## 🎯 Next Steps

1. **Pornește ESP32** și verifică IP-ul
2. **Actualizează `.env`** cu IP-ul corect (dacă e diferit)
3. **Testează HOME** pentru calibrare
4. **Testează toate cele 12 poziții**
5. **Ajustează viteza** dacă e nevoie (în UI sau în cod)

## 💡 Tips

- **Pornește mereu cu HOME** pentru calibrare
- **Viteza default: 8 cm/s** (modificabilă)
- **Toleranță mișcare: 0.1cm** (1mm)
- **Poziția se salvează în localStorage** pentru persistență

## 📞 Support

- **Backend API Docs**: http://localhost:8001/docs
- **Backend Health**: http://localhost:8001/health
- **Frontend**: http://localhost:5173/sera

---

✨ **Implementare completă cu Sequential Thinking MCP!** ✨
