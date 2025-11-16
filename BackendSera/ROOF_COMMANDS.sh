#!/bin/bash
# Comenzi rapide pentru controlul acoperișului ESP32

ESP32_IP="172.16.32.190:8080"

# ========== RELEASE (MOALE) ==========
release_left() {
    echo "🔓 Relaxare roof_left..."
    curl -X POST http://$ESP32_IP/api/release \
      -H "Content-Type: application/json" \
      -d '{"motors":["roof_left"]}'
    echo -e "\n✅ roof_left MOALE"
}

release_right() {
    echo "🔓 Relaxare roof_right..."
    curl -X POST http://$ESP32_IP/api/release \
      -H "Content-Type: application/json" \
      -d '{"motors":["roof_right"]}'
    echo -e "\n✅ roof_right MOALE"
}

release_both() {
    echo "🔓 Relaxare AMBELE acoperișuri..."
    curl -X POST http://$ESP32_IP/api/release \
      -H "Content-Type: application/json" \
      -d '{"motors":["roof_left","roof_right"]}'
    echo -e "\n✅ AMBELE acoperișuri MOALE"
}

release_all() {
    echo "🔓 Relaxare TOATE motoarele..."
    curl -X POST http://$ESP32_IP/api/release \
      -H "Content-Type: application/json" \
      -d '{"motors":"all"}'
    echo -e "\n✅ TOATE motoarele MOALE"
}

# ========== DESCHIDE ==========
open_left() {
    echo "🟢 Deschidere roof_left..."
    curl -X POST http://$ESP32_IP/api/move \
      -H "Content-Type: application/json" \
      -d '{"roof_left":{"cm":2,"speed":1,"dir":1}}'
    echo -e "\n✅ roof_left deschis (HOLD)"
}

open_right() {
    echo "🟢 Deschidere roof_right..."
    curl -X POST http://$ESP32_IP/api/move \
      -H "Content-Type: application/json" \
      -d '{"roof_right":{"cm":2,"speed":1,"dir":1}}'
    echo -e "\n✅ roof_right deschis (HOLD)"
}

open_both() {
    echo "🟢 Deschidere AMBELE acoperișuri..."
    curl -X POST http://$ESP32_IP/api/move \
      -H "Content-Type: application/json" \
      -d '{"roof_left":{"cm":2,"speed":1,"dir":1},"roof_right":{"cm":2,"speed":1,"dir":1}}'
    echo -e "\n✅ AMBELE acoperișuri deschise (HOLD)"
}

# ========== ÎNCHIDE ==========
close_left() {
    echo "🟠 Închidere roof_left..."
    curl -X POST http://$ESP32_IP/api/move \
      -H "Content-Type: application/json" \
      -d '{"roof_left":{"cm":2,"speed":1,"dir":0}}'
    echo -e "\n✅ roof_left închis (HOLD)"
}

close_right() {
    echo "🟠 Închidere roof_right..."
    curl -X POST http://$ESP32_IP/api/move \
      -H "Content-Type: application/json" \
      -d '{"roof_right":{"cm":2,"speed":1,"dir":0}}'
    echo -e "\n✅ roof_right închis (HOLD)"
}

close_both() {
    echo "🟠 Închidere AMBELE acoperișuri..."
    curl -X POST http://$ESP32_IP/api/move \
      -H "Content-Type: application/json" \
      -d '{"roof_left":{"cm":2,"speed":1,"dir":0},"roof_right":{"cm":2,"speed":1,"dir":0}}'
    echo -e "\n✅ AMBELE acoperișuri închise (HOLD)"
}

# ========== STATUS ==========
status() {
    echo "📊 Status motoare:"
    curl -s http://$ESP32_IP/api/status | python3 -m json.tool
}

# ========== EMERGENCY STOP ==========
emergency() {
    echo "🚨 EMERGENCY STOP - RELEASE ALL!"
    curl -X POST http://$ESP32_IP/api/emergency_stop
    echo -e "\n✅ Emergency stop executat - toate motoarele MOALE"
}

# ========== HELP ==========
help() {
    cat << EOF
🏡 Comenzi Rapide Control Acoperiș

RELEASE (fără tensiune - MOALE):
  ./ROOF_COMMANDS.sh release_left     - Relaxare roof_left
  ./ROOF_COMMANDS.sh release_right    - Relaxare roof_right
  ./ROOF_COMMANDS.sh release_both     - Relaxare ambele
  ./ROOF_COMMANDS.sh release_all      - Relaxare TOATE motoarele

DESCHIDE (2cm înainte):
  ./ROOF_COMMANDS.sh open_left        - Deschide stânga
  ./ROOF_COMMANDS.sh open_right       - Deschide dreapta
  ./ROOF_COMMANDS.sh open_both        - Deschide ambele

ÎNCHIDE (2cm înapoi):
  ./ROOF_COMMANDS.sh close_left       - Închide stânga
  ./ROOF_COMMANDS.sh close_right      - Închide dreapta
  ./ROOF_COMMANDS.sh close_both       - Închide ambele

ALTELE:
  ./ROOF_COMMANDS.sh status           - Status motoare
  ./ROOF_COMMANDS.sh emergency        - Emergency stop

EXEMPLE:
  ./ROOF_COMMANDS.sh open_both        # Deschide ambele acoperișuri
  ./ROOF_COMMANDS.sh release_both     # Relaxează ambele (MOALE)
  ./ROOF_COMMANDS.sh status           # Verifică status
EOF
}

# ========== MAIN ==========
case "$1" in
    release_left)   release_left ;;
    release_right)  release_right ;;
    release_both)   release_both ;;
    release_all)    release_all ;;
    open_left)      open_left ;;
    open_right)     open_right ;;
    open_both)      open_both ;;
    close_left)     close_left ;;
    close_right)    close_right ;;
    close_both)     close_both ;;
    status)         status ;;
    emergency)      emergency ;;
    help|--help|-h) help ;;
    *)
        echo "❌ Comandă necunoscută: $1"
        echo "Folosește: ./ROOF_COMMANDS.sh help"
        exit 1
        ;;
esac

