#!/bin/bash
cd /home/x/.openclaw/Antwi-workspace/biological-chaos
if [ -f server.pid ]; then
    kill $(cat server.pid) 2>/dev/null
    rm server.pid
    echo "Server stopped"
else
    pkill -f "python3 -m src.api"
    echo "Server stopped (no pid file)"
fi