from flask import Flask, request, jsonify

app = Flask(__name__)

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
        print("🔓 OPENING THE ROOF...")
        # Your roof opening code here
        
    elif command_code == 2:
        print("🔒 CLOSING THE ROOF...")
        # Your roof closing code here
        
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
        
    else:
        print("❓ Unknown command")
    
    return jsonify({
        "status": "success", 
        "received_code": command_code,
        "plant_number": plant_number
    }), 200

if __name__ == '__main__':
    print("🚀 Command Server is running and waiting for commands...")
    print("Listening on http://localhost:5000/command")
    print("\nSupported commands:")
    print("  Code 1: Open roof")
    print("  Code 2: Close roof")
    print("  Code 3: Water all plants")
    print("  Code 4: Water plant [1-12]")
    print("  Code 5: Send photo of plant [1-12]")
    print("  Code 6: Get greenhouse sensors")
    print("\nPress Ctrl+C to stop\n")
    
    # Run server (always listening)
    app.run(host='0.0.0.0', port=5000, debug=False)