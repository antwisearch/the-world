#!/bin/bash
# Start the turn-based game server

cd /home/x/.openclaw/Antwi-workspace/biological-chaos
source venv/bin/activate

echo "Starting turn-based game server on port 8080..."
echo "Open http://localhost:8080 to play"
echo ""
echo "To join as an AI agent:"
echo "  1. Read SKILL.md for available actions"
echo "  2. Connect via WebSocket to /ws_game"
echo "  3. Send {type: 'register', name: 'YourName', job: 'gatherer'}"
echo ""

nohup python3 -m src.turn_api > server.log 2>&1 &
echo $! > server.pid
echo "Server started with PID $(cat server.pid)"