#!/bin/bash
cd /home/x/.openclaw/Antwi-workspace/biological-chaos
source venv/bin/activate
nohup python3 -m src.api > server.log 2>&1 &
echo $! > server.pid
echo "Server started with PID $(cat server.pid)"