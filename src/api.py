"""
The World - Dwarf Fortress Style
FastAPI server for AI agents
"""

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import threading
import time
import json
import random
import asyncio

# Import our modules
from src.world import World
from src.agent import Agent
from src.civilization import Civilization
from src.save import save_state, load_state

# Create FastAPI app
app = FastAPI(title="The World", description="Dwarf Fortress style colony simulation")

# Mount static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Global state
world = None
civilization = None
agents = {}  # agent_id -> agent
agent_last_active = {}
SLEEP_TIMEOUT = 30

# Thread-safe state for WebSocket
state_lock = threading.Lock()
latest_state = None


# Pydantic models
class RegisterRequest(BaseModel):
    agent_id: str
    job: str = None


class ActRequest(BaseModel):
    target_x: float = None
    target_y: float = None
    job: str = None


# Initialize world
def init_world():
    global world, civilization
    
    world = World(width=1200, height=800)
    civilization = Civilization(world)
    
    # Spawn initial agents
    for i in range(10):
        agent = Agent(
            random.uniform(100, world.width - 100),
            random.uniform(100, world.height - 100)
        )
        world.add_agent(agent)
    
    return world, civilization


# Background simulation - thread-safe
def simulation_loop():
    global world, civilization, latest_state
    
    while True:
        # Update world (thread-safe)
        with state_lock:
            world.update(1/60)
            civilization.update(1/60)
            
            # Prepare state for WebSocket
            state = {
                'world': world.get_state(),
                'civilization': civilization.get_stats(),
                'agents': [a.get_state() for a in world.agents if a.alive]
            }
            latest_state = json.dumps(state, default=str)
        
        time.sleep(1/60)


# WebSocket - thread-safe
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("👀 Spectator connected")
    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
            except asyncio.TimeoutError:
                pass
            
            # Send latest state (read-only copy)
            with state_lock:
                if latest_state:
                    try:
                        await websocket.send_text(latest_state)
                    except:
                        break
    except Exception:
        pass
    print("👀 Spectator disconnected")


# Serve viewer
@app.get("/")
async def serve_viewer():
    return FileResponse("src/static/ascii.html")


# API Endpoints - thread-safe
@app.get("/world")
async def get_world():
    with state_lock:
        return world.get_state()


@app.get("/civilization")
async def get_civilization():
    with state_lock:
        return civilization.get_stats()


@app.post("/agent/register")
async def register_agent(request: RegisterRequest):
    with state_lock:
        if request.agent_id in agents:
            return {'error': 'Agent already registered'}
        
        # Find available spot
        x = random.uniform(100, world.width - 100)
        y = random.uniform(100, world.height - 100)
        
        agent = Agent(x, y)
        if request.job:
            agent.job = request.job
        
        agents[request.agent_id] = agent
        world.add_agent(agent)
        agent_last_active[request.agent_id] = time.time()
        
        return {
            'success': True,
            'agent_id': request.agent_id,
            'agent': agent.get_state()
        }


@app.get("/agent/{agent_id}")
async def get_agent(agent_id: str):
    with state_lock:
        if agent_id not in agents:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agents[agent_id].get_state()


@app.post("/agent/{agent_id}/act")
async def agent_act(agent_id: str, action: ActRequest):
    with state_lock:
        if agent_id not in agents:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent = agents[agent_id]
        agent_last_active[agent_id] = time.time()
        
        if action.target_x is not None and action.target_y is not None:
            agent.move_towards(action.target_x, action.target_y, world)
        
        if action.job:
            agent.job = action.job
        
        return {'success': True}


@app.get("/agents")
async def get_agents():
    with state_lock:
        return [a.get_state() for a in world.agents if a.alive]


@app.get("/events")
async def get_events():
    with state_lock:
        return world.events[-20:]


@app.post("/save")
async def save_simulation(filename: str = "save.json"):
    with state_lock:
        try:
            return {'success': True, 'filename': filename}
        except Exception as e:
            return {'error': str(e)}


# Start server
def run_server(host="0.0.0.0", port=8080):
    # Initialize
    init_world()
    
    # Start simulation thread
    sim_thread = threading.Thread(target=simulation_loop, daemon=True)
    sim_thread.start()
    
    print(f"⛏ The World started - Dwarf Fortress Style")
    print(f"🌐 Server: http://{host}:{port}")
    
    # Run server
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
