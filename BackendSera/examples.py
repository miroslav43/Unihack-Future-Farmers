"""
Exemple practice de utilizare a API-ului FastAPI pentru ESP32
"""
import httpx
import asyncio
from typing import Optional


class GreenhouseController:
    """Clasă helper pentru controlul serei"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
    
    async def move_motor(
        self,
        motor_name: str,
        distance_cm: float,
        speed_cm_s: float,
        forward: bool = True
    ) -> dict:
        """
        Mișcă un motor individual
        
        Args:
            motor_name: Numele motorului (roof_left, roof_right, axis_x, axis_y)
            distance_cm: Distanța în centimetri
            speed_cm_s: Viteza în cm/s
            forward: True pentru înainte, False pentru înapoi
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/motors/move",
                json={
                    motor_name: {
                        "cm": distance_cm,
                        "speed": speed_cm_s,
                        "dir": 1 if forward else 0
                    }
                }
            )
            return response.json()
    
    async def move_multiple(self, commands: dict) -> dict:
        """
        Mișcă mai multe motoare simultan
        
        Args:
            commands: Dict cu comenzi pentru fiecare motor
            Exemplu: {
                "roof_left": {"cm": 10, "speed": 5, "dir": 1},
                "axis_x": {"cm": 5, "speed": 3, "dir": 0}
            }
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/motors/move",
                json=commands
            )
            return response.json()
    
    async def stop_motor(self, motor_name: str) -> dict:
        """Oprește un motor specific"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/motors/stop",
                json={"motors": [motor_name]}
            )
            return response.json()
    
    async def stop_all(self) -> dict:
        """Oprește toate motoarele"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/motors/stop",
                json={"motors": "all"}
            )
            return response.json()
    
    async def emergency_stop(self) -> dict:
        """Emergency stop - oprește tot imediat"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/motors/emergency-stop"
            )
            return response.json()
    
    async def get_status(self) -> dict:
        """Obține status-ul tuturor motoarelor"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/motors/status"
            )
            return response.json()
    
    async def check_motor_active(self, motor_name: str) -> bool:
        """Verifică dacă un motor este activ"""
        status = await self.get_status()
        return status[motor_name]["en"]
    
    async def get_remaining_distance(self, motor_name: str) -> float:
        """Obține distanța rămasă pentru un motor"""
        status = await self.get_status()
        return status[motor_name]["cm_rem"]


# ============================================================================
# EXEMPLE DE UTILIZARE
# ============================================================================

async def example_1_basic_movement():
    """Exemplu 1: Mișcare simplă a unui motor"""
    print("\n" + "="*60)
    print("📌 EXEMPLU 1: Mișcare Simplă")
    print("="*60)
    
    controller = GreenhouseController()
    
    # Mișcă roof_left 20 cm înainte cu viteza 5 cm/s
    result = await controller.move_motor(
        motor_name="roof_left",
        distance_cm=20,
        speed_cm_s=5,
        forward=True
    )
    print(f"✅ Motoare mișcate: {result['moved']}")


async def example_2_open_roof():
    """Exemplu 2: Deschide acoperișul (ambele motoare sincron)"""
    print("\n" + "="*60)
    print("📌 EXEMPLU 2: Deschide Acoperișul")
    print("="*60)
    
    controller = GreenhouseController()
    
    # Deschide acoperișul mișcând ambele motoare
    result = await controller.move_multiple({
        "roof_left": {"cm": 30, "speed": 5, "dir": 1},
        "roof_right": {"cm": 30, "speed": 5, "dir": 1}
    })
    print(f"✅ Acoperiș deschis: {result['moved']}")


async def example_3_close_roof():
    """Exemplu 3: Închide acoperișul"""
    print("\n" + "="*60)
    print("📌 EXEMPLU 3: Închide Acoperișul")
    print("="*60)
    
    controller = GreenhouseController()
    
    # Închide acoperișul (direcția inversă)
    result = await controller.move_multiple({
        "roof_left": {"cm": 30, "speed": 5, "dir": 0},
        "roof_right": {"cm": 30, "speed": 5, "dir": 0}
    })
    print(f"✅ Acoperiș închis: {result['moved']}")


async def example_4_position_cart():
    """Exemplu 4: Poziționează cărucior pe axele X și Y"""
    print("\n" + "="*60)
    print("📌 EXEMPLU 4: Poziționare Cărucior")
    print("="*60)
    
    controller = GreenhouseController()
    
    # Mută cărucior la poziția X=50cm, Y=30cm
    result = await controller.move_multiple({
        "axis_x": {"cm": 50, "speed": 8, "dir": 1},
        "axis_y": {"cm": 30, "speed": 8, "dir": 1}
    })
    print(f"✅ Cărucior poziționat: {result['moved']}")


async def example_5_monitor_movement():
    """Exemplu 5: Monitorizează mișcarea unui motor în timp real"""
    print("\n" + "="*60)
    print("📌 EXEMPLU 5: Monitorizare în Timp Real")
    print("="*60)
    
    controller = GreenhouseController()
    
    # Start mișcare
    print("🚀 Pornesc motor axis_x pentru 40 cm...")
    await controller.move_motor("axis_x", distance_cm=40, speed_cm_s=5)
    
    # Monitorizează până când se oprește
    while True:
        status = await controller.get_status()
        motor_status = status["axis_x"]
        
        if not motor_status["en"]:
            print("✅ Motor oprit")
            break
        
        print(f"  🔄 În mișcare... rămas: {motor_status['cm_rem']:.2f} cm")
        await asyncio.sleep(0.5)


async def example_6_sequential_operations():
    """Exemplu 6: Operațiuni secvențiale"""
    print("\n" + "="*60)
    print("📌 EXEMPLU 6: Operațiuni Secvențiale")
    print("="*60)
    
    controller = GreenhouseController()
    
    # 1. Deschide acoperișul
    print("1️⃣ Deschid acoperișul...")
    await controller.move_multiple({
        "roof_left": {"cm": 25, "speed": 4, "dir": 1},
        "roof_right": {"cm": 25, "speed": 4, "dir": 1}
    })
    await asyncio.sleep(6)  # Așteaptă să termine
    
    # 2. Mută cărucior
    print("2️⃣ Mut cărucior pe axa X...")
    await controller.move_motor("axis_x", distance_cm=20, speed_cm_s=8)
    await asyncio.sleep(3)
    
    # 3. Revino la poziția inițială
    print("3️⃣ Revin la poziția inițială...")
    await controller.move_motor("axis_x", distance_cm=20, speed_cm_s=8, forward=False)
    await asyncio.sleep(3)
    
    # 4. Închide acoperișul
    print("4️⃣ Închid acoperișul...")
    await controller.move_multiple({
        "roof_left": {"cm": 25, "speed": 4, "dir": 0},
        "roof_right": {"cm": 25, "speed": 4, "dir": 0}
    })
    
    print("✅ Operațiuni completate!")


async def example_7_emergency_handling():
    """Exemplu 7: Gestionare urgențe"""
    print("\n" + "="*60)
    print("📌 EXEMPLU 7: Gestionare Urgențe")
    print("="*60)
    
    controller = GreenhouseController()
    
    # Start mișcare
    print("🚀 Pornesc mai multe motoare...")
    await controller.move_multiple({
        "roof_left": {"cm": 50, "speed": 3, "dir": 1},
        "roof_right": {"cm": 50, "speed": 3, "dir": 1},
        "axis_x": {"cm": 40, "speed": 5, "dir": 1}
    })
    
    # Așteaptă puțin
    await asyncio.sleep(2)
    
    # Simulează urgență
    print("🚨 URGENȚĂ DETECTATĂ! Opresc toate motoarele...")
    result = await controller.emergency_stop()
    print(f"✅ Emergency stop executat: {result}")


async def example_8_check_status():
    """Exemplu 8: Verificare status detaliat"""
    print("\n" + "="*60)
    print("📌 EXEMPLU 8: Status Detaliat")
    print("="*60)
    
    controller = GreenhouseController()
    
    status = await controller.get_status()
    
    print("\n📊 Status Complet Motoare:")
    for motor_name, motor_data in status.items():
        print(f"\n  🔧 {motor_name.upper()}:")
        print(f"     • Activ: {'✅ DA' if motor_data['en'] else '❌ NU'}")
        print(f"     • Viteză: {motor_data['sp_cm']} cm/s")
        print(f"     • Direcție: {'⬆️  Înainte' if motor_data['dir'] == 1 else '⬇️  Înapoi'}")
        print(f"     • Distanță rămasă: {motor_data['cm_rem']:.2f} cm")
        
        cfg = motor_data['cfg']
        print(f"     • Config:")
        print(f"       - mm/rotație: {cfg['mmrev']}")
        print(f"       - Microsteps: {cfg['ms']}")
        print(f"       - Viteză max: {cfg['max_cm']} cm/s")


async def example_9_smart_positioning():
    """Exemplu 9: Poziționare inteligentă cu verificări"""
    print("\n" + "="*60)
    print("📌 EXEMPLU 9: Poziționare Inteligentă")
    print("="*60)
    
    controller = GreenhouseController()
    
    target_x = 35  # cm
    target_y = 20  # cm
    
    print(f"🎯 Țintă: X={target_x}cm, Y={target_y}cm")
    
    # Verifică dacă motoarele sunt libere
    status = await controller.get_status()
    if status["axis_x"]["en"] or status["axis_y"]["en"]:
        print("⚠️  Motoarele sunt ocupate! Opresc...")
        await controller.stop_all()
        await asyncio.sleep(1)
    
    # Pornește mișcarea
    print("🚀 Pornesc mișcarea...")
    await controller.move_multiple({
        "axis_x": {"cm": target_x, "speed": 8, "dir": 1},
        "axis_y": {"cm": target_y, "speed": 8, "dir": 1}
    })
    
    # Monitorizează progresul
    while True:
        x_active = await controller.check_motor_active("axis_x")
        y_active = await controller.check_motor_active("axis_y")
        
        if not x_active and not y_active:
            print("✅ Poziție atinsă!")
            break
        
        x_rem = await controller.get_remaining_distance("axis_x")
        y_rem = await controller.get_remaining_distance("axis_y")
        
        print(f"  🔄 X rămas: {x_rem:.1f}cm | Y rămas: {y_rem:.1f}cm")
        await asyncio.sleep(0.5)


async def example_10_weather_response():
    """Exemplu 10: Răspuns automat la vreme (simulat)"""
    print("\n" + "="*60)
    print("📌 EXEMPLU 10: Răspuns Automat la Vreme")
    print("="*60)
    
    controller = GreenhouseController()
    
    # Simulează senzor de ploaie
    is_raining = True
    
    if is_raining:
        print("🌧️  Ploaie detectată! Închid acoperișul...")
        await controller.move_multiple({
            "roof_left": {"cm": 30, "speed": 8, "dir": 0},   # 0 = închide
            "roof_right": {"cm": 30, "speed": 8, "dir": 0}
        })
        print("✅ Acoperiș închis pentru protecție")
    else:
        print("☀️  Vreme bună! Deschid acoperișul...")
        await controller.move_multiple({
            "roof_left": {"cm": 30, "speed": 5, "dir": 1},   # 1 = deschide
            "roof_right": {"cm": 30, "speed": 5, "dir": 1}
        })
        print("✅ Acoperiș deschis pentru ventilație")


# ============================================================================
# MAIN - Rulează exemplele
# ============================================================================

async def run_all_examples():
    """Rulează toate exemplele"""
    examples = [
        example_1_basic_movement,
        example_2_open_roof,
        example_3_close_roof,
        example_4_position_cart,
        # example_5_monitor_movement,      # Decomentează pentru a testa
        # example_6_sequential_operations,  # Decomentează pentru a testa
        example_7_emergency_handling,
        example_8_check_status,
        # example_9_smart_positioning,     # Decomentează pentru a testa
        example_10_weather_response,
    ]
    
    print("\n" + "🌱"*30)
    print("  EXEMPLE PRACTICE - GREENHOUSE CONTROL")
    print("🌱"*30)
    
    for i, example in enumerate(examples, 1):
        try:
            await example()
            await asyncio.sleep(1)  # Pauză între exemple
        except Exception as e:
            print(f"\n❌ Eroare în {example.__name__}: {e}")
    
    print("\n" + "="*60)
    print("✅ TOATE EXEMPLELE AU FOST EXECUTATE")
    print("="*60 + "\n")


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════╗
    ║  ESP32 Greenhouse - Exemple Practice          ║
    ║  Asigură-te că API-ul rulează pe port 8000     ║
    ╚════════════════════════════════════════════════╝
    """)
    
    try:
        asyncio.run(run_all_examples())
    except KeyboardInterrupt:
        print("\n\n👋 Exemple întrerupte de utilizator")
