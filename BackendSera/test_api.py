"""
Script de testare pentru API-ul de control ESP32
Rulează cu: python test_api.py
"""
import httpx
import asyncio
import sys
from typing import Dict, Any


BASE_URL = "http://localhost:8009"


async def test_health():
    """Testează health check-ul API-ului și ESP32"""
    print("\n" + "="*60)
    print("🏥 TEST: Health Check")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        try:
            # Test API health
            response = await client.get(f"{BASE_URL}/health")
            print(f"✅ API Health: {response.json()}")
            
            # Test ESP32 connection
            response = await client.get(f"{BASE_URL}/motors/health")
            data = response.json()
            print(f"📡 ESP32 Health: {data}")
            
            if not data.get("esp32_reachable"):
                print("⚠️  WARNING: ESP32 nu este accesibil!")
                print(f"   Target: {data.get('esp32_host')}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ EROARE: {e}")
            return False


async def test_status():
    """Testează obținerea status-ului motoarelor"""
    print("\n" + "="*60)
    print("📊 TEST: Status Motoare")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/motors/status")
            data = response.json()
            
            print("Status motoare:")
            for motor_name, motor_status in data.items():
                print(f"\n  🔧 {motor_name}:")
                print(f"     Activ: {motor_status['en']}")
                print(f"     Viteză: {motor_status['sp_cm']} cm/s")
                print(f"     Direcție: {'înainte' if motor_status['dir'] == 1 else 'înapoi'}")
                print(f"     Rămas: {motor_status['cm_rem']} cm")
                print(f"     Config: {motor_status['cfg']}")
            
            return True
            
        except Exception as e:
            print(f"❌ EROARE: {e}")
            return False


async def test_move_single_motor():
    """Testează mișcarea unui singur motor"""
    print("\n" + "="*60)
    print("🏃 TEST: Mișcare Motor Individual (roof_left)")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        try:
            move_data = {
                "roof_left": {
                    "cm": 10,
                    "speed": 5,
                    "dir": 1
                }
            }
            
            print(f"📤 Trimit comandă: {move_data}")
            
            response = await client.post(
                f"{BASE_URL}/motors/move",
                json=move_data
            )
            data = response.json()
            
            print(f"✅ Response: {data}")
            print(f"   Motoare mișcate: {', '.join(data['moved'])}")
            
            return True
            
        except Exception as e:
            print(f"❌ EROARE: {e}")
            return False


async def test_move_multiple_motors():
    """Testează mișcarea mai multor motoare simultan"""
    print("\n" + "="*60)
    print("🏃‍♂️ TEST: Mișcare Multiplă (roof_left + axis_x)")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        try:
            move_data = {
                "roof_left": {
                    "cm": 15,
                    "speed": 4,
                    "dir": 1
                },
                "axis_x": {
                    "cm": 8,
                    "speed": 3,
                    "dir": 0
                }
            }
            
            print(f"📤 Trimit comandă: {move_data}")
            
            response = await client.post(
                f"{BASE_URL}/motors/move",
                json=move_data
            )
            data = response.json()
            
            print(f"✅ Response: {data}")
            print(f"   Motoare mișcate: {', '.join(data['moved'])}")
            
            return True
            
        except Exception as e:
            print(f"❌ EROARE: {e}")
            return False


async def test_stop_specific():
    """Testează oprirea motoarelor specifice"""
    print("\n" + "="*60)
    print("🛑 TEST: Stop Motoare Specifice")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        try:
            stop_data = {
                "motors": ["roof_left", "axis_x"]
            }
            
            print(f"📤 Trimit comandă stop: {stop_data}")
            
            response = await client.post(
                f"{BASE_URL}/motors/stop",
                json=stop_data
            )
            data = response.json()
            
            print(f"✅ Response: {data}")
            
            return True
            
        except Exception as e:
            print(f"❌ EROARE: {e}")
            return False


async def test_stop_all():
    """Testează oprirea tuturor motoarelor"""
    print("\n" + "="*60)
    print("🛑 TEST: Stop Toate Motoarele")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        try:
            stop_data = {
                "motors": "all"
            }
            
            print(f"📤 Trimit comandă stop all")
            
            response = await client.post(
                f"{BASE_URL}/motors/stop",
                json=stop_data
            )
            data = response.json()
            
            print(f"✅ Response: {data}")
            
            return True
            
        except Exception as e:
            print(f"❌ EROARE: {e}")
            return False


async def test_emergency_stop():
    """Testează emergency stop"""
    print("\n" + "="*60)
    print("🚨 TEST: Emergency Stop")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        try:
            print(f"📤 Trimit comandă EMERGENCY STOP")
            
            response = await client.post(f"{BASE_URL}/motors/emergency-stop")
            data = response.json()
            
            print(f"✅ Response: {data}")
            
            return True
            
        except Exception as e:
            print(f"❌ EROARE: {e}")
            return False


async def test_config():
    """Testează configurarea motoarelor"""
    print("\n" + "="*60)
    print("⚙️  TEST: Configurare Motor")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        try:
            config_data = {
                "roof_left": {
                    "mm_per_rev": 40.0,
                    "microstep": 8,
                    "max_speed": 30.0
                }
            }
            
            print(f"📤 Trimit configurare: {config_data}")
            
            response = await client.post(
                f"{BASE_URL}/motors/config",
                json=config_data
            )
            data = response.json()
            
            print(f"✅ Config aplicată, status nou:")
            print(f"   roof_left cfg: {data['roof_left']['cfg']}")
            
            return True
            
        except Exception as e:
            print(f"❌ EROARE: {e}")
            return False


async def run_all_tests():
    """Rulează toate testele"""
    print("\n" + "🚀"*30)
    print("  SUITE DE TESTARE API - ESP32 GREENHOUSE CONTROL")
    print("🚀"*30)
    
    # Check dacă API-ul rulează
    print(f"\n📍 Target API: {BASE_URL}")
    
    tests = [
        ("Health Check", test_health),
        ("Status Motoare", test_status),
        ("Mișcare Motor Individual", test_move_single_motor),
        ("Mișcare Motoare Multiple", test_move_multiple_motors),
        ("Stop Motoare Specifice", test_stop_specific),
        ("Stop Toate", test_stop_all),
        ("Emergency Stop", test_emergency_stop),
        ("Configurare", test_config),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
            
            # Pauză între teste
            if test_func != test_health:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            print("\n⚠️  Testare întreruptă de utilizator")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Excepție neașteptată în {test_name}: {e}")
            results.append((test_name, False))
    
    # Rezumat
    print("\n" + "="*60)
    print("📋 REZUMAT TESTE")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print("\n" + "="*60)
    print(f"📊 REZULTAT FINAL: {passed}/{total} teste trecute")
    print("="*60 + "\n")
    
    return passed == total


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════╗
    ║  ESP32 Greenhouse Control - Test Suite        ║
    ║  Asigură-te că serverul rulează pe port 8000   ║
    ╚════════════════════════════════════════════════╝
    """)
    
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Testare anulată de utilizator")
        sys.exit(0)
