#!/bin/bash

# Quick test script for Jarvis commands
# Usage: ./test_commands.sh [command_number]

SERVER_URL="http://localhost:6000/command"

echo "🧪 Testing Jarvis Commands"
echo "=========================="

# Test based on command argument
case "$1" in
  "1")
    echo "Testing: OPEN ROOF (code 1)"
    curl -X POST "$SERVER_URL" \
      -H "Content-Type: application/json" \
      -d '{"code": 1, "action": "OPEN ROOF", "text": "open"}' \
      -w "\n"
    ;;
  "2")
    echo "Testing: CLOSE ROOF (code 2)"
    curl -X POST "$SERVER_URL" \
      -H "Content-Type: application/json" \
      -d '{"code": 2, "action": "CLOSE ROOF", "text": "close"}' \
      -w "\n"
    ;;
  "7")
    PLANT_NUM=${2:-5}
    echo "Testing: GO TO PLANT $PLANT_NUM (code 7)"
    curl -X POST "$SERVER_URL" \
      -H "Content-Type: application/json" \
      -d "{\"code\": 7, \"action\": \"GO TO PLANT $PLANT_NUM\", \"plant_number\": $PLANT_NUM, \"text\": \"go to plant $PLANT_NUM\"}" \
      -w "\n"
    ;;
  "8")
    echo "Testing: FULL AUTO TOUR (code 8)"
    curl -X POST "$SERVER_URL" \
      -H "Content-Type: application/json" \
      -d '{"code": 8, "action": "START FULL AUTO TOUR", "text": "full tour"}' \
      -w "\n"
    ;;
  "9")
    HOME_X=${2:-22.5}
    HOME_Y=${3:-31.5}
    echo "Testing: MAP HOME POSITION (code 9) at ($HOME_X, $HOME_Y)"
    curl -X POST "$SERVER_URL" \
      -H "Content-Type: application/json" \
      -d "{\"code\": 9, \"action\": \"MAP HOME POSITION\", \"text\": \"map home\", \"home_x\": $HOME_X, \"home_y\": $HOME_Y}" \
      -w "\n"
    ;;
  *)
    echo "Available tests:"
    echo "  ./test_commands.sh 1                    # Test open roof"
    echo "  ./test_commands.sh 2                    # Test close roof"
    echo "  ./test_commands.sh 7 [1-12]            # Test go to plant (default: 5)"
    echo "  ./test_commands.sh 8                    # Test full auto tour"
    echo "  ./test_commands.sh 9 [x] [y]           # Test map home (default: 22.5, 31.5)"
    echo ""
    echo "Examples:"
    echo "  ./test_commands.sh 9 20 30             # Map HOME to (20, 30)"
    echo "  ./test_commands.sh 7 1                 # Go to plant 1"
    echo "  ./test_commands.sh 7 12                # Go to plant 12"
    echo "  ./test_commands.sh 8                   # Start full tour"
    ;;
esac

