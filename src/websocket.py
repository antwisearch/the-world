"""
WebSocket spectator for The World
Streams simulation state to browser viewers
"""

import asyncio
import json
from fastapi import WebSocket
from typing import List


class SpectatorManager:
    """Manages WebSocket spectators"""
    
    def __init__(self):
        self.spectators: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.spectators.append(websocket)
        print(f"[+] Spectator connected. Total: {len(self.spectators)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.spectators:
            self.spectators.remove(websocket)
        print(f"[-] Spectator disconnected. Total: {len(self.spectators)}")
    
    async def broadcast(self, data):
        """Send state to all spectators"""
        if not self.spectators:
            return
        
        # Remove dead connections
        dead = []
        for ws in self.spectators:
            try:
                if isinstance(data, str):
                    await ws.send_text(data)
                else:
                    await ws.send_json(data)
            except:
                dead.append(ws)
        
        for ws in dead:
            self.disconnect(ws)


# Global spectator manager
spectator_manager = SpectatorManager()


async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for spectators"""
    await spectator_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, wait for messages (optional)
            data = await websocket.receive_text()
            # Could handle commands like 'pause', 'resume', 'change_view'
    except Exception:
        spectator_manager.disconnect(websocket)
