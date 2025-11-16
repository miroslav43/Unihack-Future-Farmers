from flask import Flask, request, jsonify
import requests
import json
import os
from gtts import gTTS
import subprocess

# Configuration
BACKEND_SERA_URL = "http://localhost:8009"
HOME_POSITION_FILE = os.path.join(os.path.dirname(__file__), "jarvis_home_position.json")
TTS_OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "jarvis_response.mp3")

app = Flask(__name__)

def speak(text):
    """Generate speech and play it"""
    try:
        print(f"🔊 Jarvis says: {text}")
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(TTS_OUTPUT_FILE)
        
        # Play the audio (macOS)
        subprocess.run(['afplay', TTS_OUTPUT_FILE], check=False)
        
        # Clean up
        try:
            os.remove(TTS_OUTPUT_FILE)
        except:
            pass
    except Exception as e:
        print(f"⚠️ TTS Error: {e}")

def load_home_position():
    """Load saved HOME position from file"""
    if os.path.exists(HOME_POSITION_FILE):
        try:
            with open(HOME_POSITION_FILE, 'r') as f:
                data = json.load(f)
                print(f"✅ Loaded HOME position: {data}")
                return data
        except Exception as e:
            print(f"⚠️ Error loading HOME position: {e}")
    
    # Default HOME if no file exists
    default = {"x": 22.5, "y": 31.5}
    print(f"ℹ️ Using default HOME position: {default}")
    return default

def save_home_position(position):
    """Save HOME position to file"""
    try:
        with open(HOME_POSITION_FILE, 'w') as f:
            json.dump(position, f, indent=2)
        print(f"✅ Saved HOME position: {position}")
        return True
    except Exception as e:
        print(f"❌ Error saving HOME position: {e}")
        return False

def get_current_position():
    """Get current position from backend"""
    try:
        # Try to get status from backend
        response = requests.get(f"{BACKEND_SERA_URL}/motors/health", timeout=5)
        if response.ok:
            # For now, return saved HOME as fallback
            # In a real system, you'd track position in backend
            return load_home_position()
    except:
        pass
    
    # Fallback to saved HOME
    return load_home_position()

@app.route('/command', methods=['POST'])
def receive_command():
    """Receives commands from Jarvis"""
    data = request.get_json()
    command_code = data.get('code')
    command_text = data.get('text', '')
    plant_number = data.get('plant_number')
    action = data.get('action', 'Unknown')
    
    print(f"\n{'='*50}")
    print(f"📨 Message received!")
    print(f"Code: {command_code}")
    print(f"Action: {action}")
    print(f"Text: {command_text}")
    if plant_number:
        print(f"Plant Number: {plant_number}")
    print(f"{'='*50}\n")
    
    # Process commands
    if command_code == 1:
        speak("Sure, I will open the roof")
        print("🔓 OPENING THE ROOF...")
        try:
            response = requests.post(
                f"{BACKEND_SERA_URL}/motors/move",
                json={
                    "roof_left": {"cm": 2, "speed": 1, "dir": 1},
                    "roof_right": {"cm": 2, "speed": 1, "dir": 1}
                },
                timeout=5
            )
            if response.ok:
                print("✅ Roof opened successfully")
                speak("Roof opened successfully")
            else:
                print(f"⚠️ Error opening roof: {response.status_code}")
                speak("Sorry, I encountered an error opening the roof")
        except Exception as e:
            print(f"❌ Failed to open roof: {e}")
            speak("Sorry, I could not connect to the greenhouse system")
        
    elif command_code == 2:
        speak("Sure, I will close the roof")
        print("🔒 CLOSING THE ROOF...")
        try:
            response = requests.post(
                f"{BACKEND_SERA_URL}/motors/move",
                json={
                    "roof_left": {"cm": 2, "speed": 1, "dir": 0},
                    "roof_right": {"cm": 2, "speed": 1, "dir": 0}
                },
                timeout=5
            )
            if response.ok:
                print("✅ Roof closed successfully")
                speak("Roof closed successfully")
            else:
                print(f"⚠️ Error closing roof: {response.status_code}")
                speak("Sorry, I encountered an error closing the roof")
        except Exception as e:
            print(f"❌ Failed to close roof: {e}")
            speak("Sorry, I could not connect to the greenhouse system")
        
    elif command_code == 3:
        print("💧 WATERING ALL PLANTS...")
        # Your code to water all 12 plants
        
    elif command_code == 4:
        print(f"💧 WATERING PLANT #{plant_number}...")
        # Your code to water specific plant
        
    elif command_code == 5:
        print(f"📸 SENDING PHOTO OF PLANT #{plant_number}...")
        # Your code to take and send photo
        
    elif command_code == 6:
        print("🌡️ READING GREENHOUSE SENSORS...")
        # Your code to read temperature, humidity, soil moisture, etc.
        # Example: 
        # temp = read_temperature()
        # humidity = read_humidity()
        # print(f"Temperature: {temp}°C, Humidity: {humidity}%")
        
    elif command_code == 7:
        speak(f"Sure, I will go to plant {plant_number}")
        print(f"🌱 GOING TO PLANT #{plant_number}...")
        try:
            # Load saved HOME position
            home_position = load_home_position()
            current_position = get_current_position()
            
            # Plant positions (relative to HOME)
            plant_positions = [
                {"x": -12, "y": 18},  # Plant 1
                {"x": 0, "y": 18},    # Plant 2
                {"x": 12, "y": 18},   # Plant 3
                {"x": -12, "y": 9},   # Plant 4
                {"x": 0, "y": 9},     # Plant 5
                {"x": 12, "y": 9},    # Plant 6
                {"x": -12, "y": -9},  # Plant 7
                {"x": 0, "y": -9},    # Plant 8
                {"x": 12, "y": -9},   # Plant 9
                {"x": -12, "y": -18}, # Plant 10
                {"x": 0, "y": -18},   # Plant 11
                {"x": 12, "y": -18},  # Plant 12
            ]
            
            if plant_number < 1 or plant_number > 12:
                print(f"⚠️ Invalid plant number: {plant_number}")
                speak("Sorry, plant number must be between 1 and 12")
                return jsonify({"status": "error", "message": "Plant number must be 1-12"}), 400
            
            # Get target position (absolute)
            relative_pos = plant_positions[plant_number - 1]
            target_pos = {
                "x": home_position["x"] + relative_pos["x"],
                "y": home_position["y"] + relative_pos["y"]
            }
            
            print(f"  📍 HOME: ({home_position['x']}, {home_position['y']})")
            print(f"  📍 Current: ({current_position['x']}, {current_position['y']})")
            print(f"  → Target: Plant {plant_number} at ({relative_pos['x']}, {relative_pos['y']}) relative")
            print(f"  → Absolute: ({target_pos['x']}, {target_pos['y']})")
            
            # Move to plant
            response = requests.post(
                f"{BACKEND_SERA_URL}/motors/position",
                json={
                    "target_x": target_pos["x"],
                    "target_y": target_pos["y"],
                    "current_x": current_position["x"],
                    "current_y": current_position["y"],
                    "speed": 8
                },
                timeout=30
            )
            
            if response.ok:
                result = response.json()
                print(f"✅ Moved to plant {plant_number}")
                print(f"  ⏱️ Travel time: {result.get('travel_time', 0):.1f}s")
                speak(f"Arrived at plant {plant_number}")
                
                # Wait 5 seconds at plant
                import time
                print("  ⏳ Waiting 5 seconds at plant...")
                time.sleep(5)
                
                # Update current position to target
                current_position = target_pos
                
                # Return to HOME
                print("  🏠 Returning to HOME...")
                speak("Returning to home position")
                response = requests.post(
                    f"{BACKEND_SERA_URL}/motors/position",
                    json={
                        "target_x": home_position["x"],
                        "target_y": home_position["y"],
                        "current_x": current_position["x"],
                        "current_y": current_position["y"],
                        "speed": 8
                    },
                    timeout=30
                )
                if response.ok:
                    result = response.json()
                    print(f"✅ Returned to HOME")
                    print(f"  ⏱️ Travel time: {result.get('travel_time', 0):.1f}s")
                    speak("Back at home position")
                else:
                    print(f"⚠️ Error returning to HOME: {response.status_code}")
                    speak("Sorry, I encountered an error returning to home")
            else:
                print(f"⚠️ Error moving to plant: {response.status_code}")
                speak(f"Sorry, I could not reach plant {plant_number}")
        except Exception as e:
            print(f"❌ Failed to go to plant: {e}")
            speak("Sorry, something went wrong")
            import traceback
            traceback.print_exc()
    
    elif command_code == 8:
        speak("Starting full auto tour of all plants")
        print("🤖 STARTING FULL AUTO TOUR...")
        try:
            import time
            import math
            
            # Load saved HOME position
            home_position = load_home_position()
            current_position = get_current_position()
            
            # Plant positions (relative to HOME) - EXACT ca în frontend
            plant_positions = [
                {"x": -12, "y": 18},  # Plant 1
                {"x": 0, "y": 18},    # Plant 2
                {"x": 12, "y": 18},   # Plant 3
                {"x": -12, "y": 9},   # Plant 4
                {"x": 0, "y": 9},     # Plant 5
                {"x": 12, "y": 9},    # Plant 6
                {"x": -12, "y": -9},  # Plant 7
                {"x": 0, "y": -9},    # Plant 8
                {"x": 12, "y": -9},   # Plant 9
                {"x": -12, "y": -18}, # Plant 10
                {"x": 0, "y": -18},   # Plant 11
                {"x": 12, "y": -18},  # Plant 12
            ]
            
            # Zig-zag order - EXACT ca în frontend
            zigzag_order = [
                0, 1, 2,     # Rând 1: index 0,1,2 (plante 1,2,3)
                5, 4, 3,     # Rând 2: index 5,4,3 (plante 6,5,4) - INVERS
                6, 7, 8,     # Rând 3: index 6,7,8 (plante 7,8,9)
                11, 10, 9,   # Rând 4: index 11,10,9 (plante 12,11,10) - INVERS
            ]
            
            print(f"  📍 HOME: ({home_position['x']}, {home_position['y']})")
            print(f"  📍 Current: ({current_position['x']}, {current_position['y']})")
            print(f"  🌱 Visiting {len(zigzag_order)} plants in zig-zag pattern")
            
            for step in range(len(zigzag_order)):
                i = zigzag_order[step]
                relative_pos = plant_positions[i]
                target_absolute = {
                    "x": home_position["x"] + relative_pos["x"],
                    "y": home_position["y"] + relative_pos["y"]
                }
                
                # Calculează distanța și timpul necesar pentru mișcare - EXACT ca în frontend
                delta_x = abs(target_absolute["x"] - current_position["x"])
                delta_y = abs(target_absolute["y"] - current_position["y"])
                distance = math.sqrt(delta_x * delta_x + delta_y * delta_y)
                speed = 8  # cm/s
                
                # Timp realist: include accelerare/decelerare + overhead motor - EXACT ca în frontend
                # Formula: (distanță / viteză) * 2.0 pentru overhead FOARTE realist
                base_travel_time = (distance / speed) * 1000  # milisecunde
                realistic_travel_time = base_travel_time * 2.0  # ×2 pentru siguranță
                
                print(f"\n  [{step+1}/{len(zigzag_order)}] Planta {i+1}: ({relative_pos['x']}, {relative_pos['y']}) - Dist: {distance:.1f}cm, Timp estimat: {(realistic_travel_time/1000):.1f}s")
                
                # Move to plant
                response = requests.post(
                    f"{BACKEND_SERA_URL}/motors/position",
                    json={
                        "target_x": target_absolute["x"],
                        "target_y": target_absolute["y"],
                        "current_x": current_position["x"],
                        "current_y": current_position["y"],
                        "speed": speed
                    },
                    timeout=30
                )
                
                if response.ok:
                    result = response.json()
                    new_position = {
                        "x": result["new_position"]["x"],
                        "y": result["new_position"]["y"]
                    }
                    print(f"  ✅ Moved to plant {i+1}")
                    
                    # AȘTEAPTĂ ca motorul să ajungă la destinație - EXACT ca în frontend
                    # Buffer de 3 secunde pentru siguranță + timp realist de călătorie
                    wait_time = max(realistic_travel_time + 3000, 3000) / 1000  # convertim în secunde
                    print(f"  ⏱️ Aștept {wait_time:.1f}s ca motorul să execute comanda...")
                    time.sleep(wait_time)
                    
                    # Update current position pentru următoarea iterație
                    current_position = new_position
                    
                    # La finalul fiecărui rând (după 3 plante), PAUZĂ 2 secunde - EXACT ca în frontend
                    if (step + 1) % 3 == 0 and step < len(zigzag_order) - 1:
                        print(f"  🔄 Schimbare rând - Pauză 2 sec (după planta {i+1})")
                        time.sleep(2)
                else:
                    print(f"  ⚠️ Error moving to plant {i+1}: {response.status_code}")
            
            # Așteaptă 2 secunde înainte de a merge la HOME - EXACT ca în frontend
            print(f"\n  🏠 Pregătire întoarcere la HOME - Pauză 2 sec...")
            time.sleep(2)
            
            # Calculează distanța până la HOME - EXACT ca în frontend
            delta_x = abs(home_position["x"] - current_position["x"])
            delta_y = abs(home_position["y"] - current_position["y"])
            distance = math.sqrt(delta_x * delta_x + delta_y * delta_y)
            speed = 8  # cm/s
            
            # Timp realist cu overhead - EXACT ca în frontend
            base_travel_time = (distance / speed) * 1000
            realistic_travel_time = base_travel_time * 2.0  # ×2 pentru siguranță
            
            print(f"  Întoarcere la HOME (0,0) - Dist: {distance:.1f}cm, Timp estimat: {(realistic_travel_time/1000):.1f}s")
            
            # Return to HOME
            speak("Tour complete, returning to home position")
            response = requests.post(
                f"{BACKEND_SERA_URL}/motors/position",
                json={
                    "target_x": home_position["x"],
                    "target_y": home_position["y"],
                    "current_x": current_position["x"],
                    "current_y": current_position["y"],
                    "speed": speed
                },
                timeout=30
            )
            
            if response.ok:
                result = response.json()
                
                # Așteaptă ca motorul să ajungă la HOME - EXACT ca în frontend
                wait_time = max(realistic_travel_time + 3000, 3000) / 1000
                print(f"  ⏱️ Aștept {wait_time:.1f}s ca motorul să ajungă la HOME...")
                time.sleep(wait_time)
                
                print(f"  ✅ Back at HOME")
                speak("Full auto tour completed successfully. All plants visited and system returned to home")
            else:
                print(f"  ⚠️ Error returning to HOME: {response.status_code}")
                speak("Tour completed but could not return to home")
                
        except Exception as e:
            print(f"❌ Failed to complete full tour: {e}")
            speak("Sorry, I could not complete the auto tour")
            import traceback
            traceback.print_exc()
    
    elif command_code == 9:
        speak("Mapping home position")
        print("🏠 MAPPING HOME POSITION...")
        try:
            # Get position from request or use current
            new_home_x = data.get('home_x')
            new_home_y = data.get('home_y')
            
            if new_home_x is not None and new_home_y is not None:
                # Use provided coordinates
                new_home = {"x": float(new_home_x), "y": float(new_home_y)}
            else:
                # Use current position as HOME
                new_home = get_current_position()
            
            # Save the new HOME position
            if save_home_position(new_home):
                print(f"✅ HOME position mapped to: ({new_home['x']}, {new_home['y']})")
                print("  → All future plant movements will be relative to this position")
                speak(f"Home position set to {new_home['x']:.1f}, {new_home['y']:.1f}")
            else:
                print("❌ Failed to save HOME position")
                speak("Sorry, I could not save the home position")
        except Exception as e:
            print(f"❌ Failed to map home: {e}")
            speak("Sorry, something went wrong while mapping home")
            import traceback
            traceback.print_exc()
        
    else:
        print("❓ Unknown command")
    
    return jsonify({
        "status": "success", 
        "received_code": command_code,
        "plant_number": plant_number
    }), 200

if __name__ == '__main__':
    print("🚀 Command Server is running and waiting for commands...")
    print("Listening on http://localhost:6000/command")
    print("\nSupported commands:")
    print("  Code 1: Open roof")
    print("  Code 2: Close roof")
    print("  Code 3: Water all plants")
    print("  Code 4: Water plant [1-12]")
    print("  Code 5: Send photo of plant [1-12]")
    print("  Code 6: Get greenhouse sensors")
    print("  Code 7: Go to plant [1-12] (stays 5 sec, returns to HOME)")
    print("  Code 8: Start full auto tour")
    print("  Code 9: Map home position (saves current position as HOME)")
    print("\nPress Ctrl+C to stop\n")
    
    # Load and display current HOME position
    home = load_home_position()
    print(f"📍 Current HOME position: ({home['x']}, {home['y']})")
    print(f"   (Saved in: {HOME_POSITION_FILE})\n")
    
    # Run server (always listening)
    app.run(host='0.0.0.0', port=6000, debug=False)