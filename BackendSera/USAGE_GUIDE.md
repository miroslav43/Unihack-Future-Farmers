# 📖 Ghid de Utilizare - ESP32 Greenhouse Control API

## 🎯 Pas cu Pas: Cum să faci call-uri din Python

### Metoda 1: Folosind `requests` (simplu)

```python
import requests

BASE_URL = "http://localhost:8001"

# 1. Verifică conexiunea
response = requests.get(f"{BASE_URL}/motors/health")
print(response.json())

# 2. Mișcă un motor
response = requests.post(
    f"{BASE_URL}/motors/move",
    json={
        "roof_left": {
            "cm": 20,
            "speed": 5,
            "dir": 1  # 1 = înainte, 0 = înapoi
        }
    }
)
print(response.json())  # {"moved": ["roof_left"]}

# 3. Oprește motorul
response = requests.post(
    f"{BASE_URL}/motors/stop",
    json={"motors": ["roof_left"]}
)
print(response.json())
```

### Metoda 2: Folosind clasa helper

```python
from examples import GreenhouseController
import asyncio

async def main():
    controller = GreenhouseController("http://localhost:8000")
    
    # Mișcă motor simplu
    await controller.move_motor("roof_left", distance_cm=20, speed_cm_s=5)
    
    # Oprește toate motoarele
    await controller.stop_all()

asyncio.run(main())
```

## 📡 Toate Endpoint-urile

### 1. POST `/motors/move` - Mișcă Motoare

```python
# Un motor
requests.post("http://localhost:8000/motors/move",
    json={"roof_left": {"cm": 20, "speed": 5, "dir": 1}})

# Mai multe motoare
requests.post("http://localhost:8000/motors/move",
    json={
        "roof_left": {"cm": 15, "speed": 4, "dir": 1},
        "roof_right": {"cm": 15, "speed": 4, "dir": 1}
    })
```

### 2. POST `/motors/stop` - Oprește Motoare

```python
# Motoare specifice
requests.post("http://localhost:8000/motors/stop",
    json={"motors": ["roof_left", "axis_x"]})

# Toate
requests.post("http://localhost:8000/motors/stop",
    json={"motors": "all"})
```

### 3. POST `/motors/emergency-stop` - Stop Urgență

```python
requests.post("http://localhost:8001/motors/emergency-stop")
```

### 4. GET `/motors/status` - Status

```python
response = requests.get("http://localhost:8001/motors/status")
print(response.json())
```

## 🎮 Scenarii Practice

### Deschide/Închide Acoperiș

```python
def open_roof():
    return requests.post("http://localhost:8000/motors/move",
        json={
            "roof_left": {"cm": 30, "speed": 5, "dir": 1},
            "roof_right": {"cm": 30, "speed": 5, "dir": 1}
        }).json()

def close_roof():
    return requests.post("http://localhost:8000/motors/move",
        json={
            "roof_left": {"cm": 30, "speed": 5, "dir": 0},
            "roof_right": {"cm": 30, "speed": 5, "dir": 0}
        }).json()
```

### Monitorizare în Timp Real

```python
import time

def monitor_motor(motor_name):
    while True:
        status = requests.get("http://localhost:8000/motors/status").json()
        motor = status[motor_name]
        
        if not motor["en"]:
            print(f"✅ {motor_name} oprit")
            break
        
        print(f"🔄 {motor_name}: {motor['cm_rem']:.2f} cm rămas")
        time.sleep(0.5)
```

## 🐛 Troubleshooting

### Check API

```python
try:
    r = requests.get("http://localhost:8001/health", timeout=2)
    print("✅ API OK:", r.json())
except:
    print("❌ API offline! Rulează: python main.py")
```

### Check ESP32

```python
r = requests.get("http://localhost:8001/motors/health")
if r.json()["esp32_reachable"]:
    print("✅ ESP32 OK")
else:
    print("❌ ESP32 offline! Verifică .env")
```

## 📚 Resurse

- **Documentație**: http://localhost:8000/docs
- **Teste**: `python test_api.py`
- **Exemple**: `python examples.py`
