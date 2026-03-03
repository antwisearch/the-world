"""
The World API - FastAPI server for AI agents
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import threading
import time
import json
import random

# Import our modules
from src.world import World
from src.creature import Creature
from src.evolution import EvolutionEngine
from src.websocket import spectator_manager

# Create FastAPI app
app = FastAPI(title="The World", description="AI Agent Evolution Simulator")

# Mount static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Global state
world = None
evolution = None
agents = {}  # agent_id -> creature
agent_last_active = {}  # agent_id -> last active timestamp
SLEEP_TIMEOUT = 30  # seconds before creature sleeps


# Pydantic models for API
class RegisterRequest(BaseModel):
    agent_id: str
    genome: Optional[Dict] = None


class ActRequest(BaseModel):
    thrust: tuple = (0, 0)
    contract: float = 0.0
    build: Optional[str] = None
    modify: Optional[str] = None


class WorldState(BaseModel):
    width: int
    height: int
    era: str
    global_temp: float
    weather: str
    climate_zones: List[Dict]
    impact: Dict
    time: float


class PerceiveResponse(BaseModel):
    agent_id: str
    creature_id: int
    world_era: str
    climate_zone: str
    temperature: float
    weather: str
    position: Dict
    nearby_food: List[Dict]
    nearby_creatures: List[Dict]
    structures: List[Dict]
    body_state: Dict
    genome: Dict


# Initialize world
def init_world():
    global world, evolution
    
    world = World(width=1200, height=800)
    evolution = EvolutionEngine(world, population_size=20, generation_time=30)
    evolution.spawn_initial_population(20)
    
    return world, evolution


import asyncio
from collections import deque

# Queue for passing state from thread to async
state_queue = deque(maxlen=1)


# Background simulation thread
def simulation_loop():
    global world, evolution
    
    while True:
        current_time = time.time()
        
        # Check for sleeping agents
        for agent_id, creature in list(agents.items()):
            if not creature.alive:
                continue
            
            last_active = agent_last_active.get(agent_id, 0)
            inactive_time = current_time - last_active
            
            if inactive_time > SLEEP_TIMEOUT:
                creature.sleeping = True
            else:
                creature.sleeping = False
        
        # Update world
        agent_list = [c for c in agents.values() if c.alive and not getattr(c, 'sleeping', False)]
        world.update(agent_list, 1/60)
        
        # Check collisions (eating food, creature-creature)
        all_creatures = [c for c in evolution.creatures if c.alive]
        world.check_collisions(all_creatures)
        
        # Spawn food periodically
        if len(world.food) < 30 and random.random() < 0.1:
            world.spawn_food()
        
        # Update evolution (only non-sleeping creatures)
        for creature in evolution.creatures:
            if creature in agents.values() and getattr(creature, 'sleeping', False):
                continue
            if creature.alive:
                # Get world state at creature position
                center = creature.get_center()
                zone = world.get_zone_at(center.x)
                temp = world.get_temperature_at(center.x, center.y)
                world_state = {
                    'era': world.era,
                    'climate': zone.name,
                    'temperature': temp,
                    'weather': world.get_weather_at(center.x, center.y),
                    'global_temp': world.global_temp,
                    'terrain': {'structures': world.terrain.structures}
                }
                creature.update(1/60, world_state)
        
        # Update evolution
        evolution.update(1/60)
        
        # Queue state for broadcast
        import json
        state = {
            'world': world.to_dict(),
            'evolution': {
                'generation': evolution.generation,
                'time_in_generation': evolution.time_in_generation,
                'population': len(evolution.creatures),
                'alive': sum(1 for c in evolution.creatures if c.alive)
            },
            'creatures': [
                {
                    'alive': c.alive,
                    'genome': c.genome,
                    'position': {'x': c.get_center().x, 'y': c.get_center().y},
                    'nodes': [{'x': n.position.x, 'y': n.position.y} for n in c.nodes]
                }
                for c in evolution.creatures
            ]
        }
        
        try:
            state_queue.append(json.dumps(state, default=str))
        except:
            pass
        
        time.sleep(1/60)


@app.on_event("startup")
async def startup_event():
    """Start simulation on startup"""
    global world, evolution
    
    world, evolution = init_world()
    
    # Start simulation in background
    sim_thread = threading.Thread(target=simulation_loop, daemon=True)
    sim_thread.start()
    
    print("🌍 The World simulation started")


# API Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to The World - AI Agent Evolution Simulator"}


@app.get("/world")
async def get_world():
    """Get current world state"""
    return world.to_dict()


@app.get("/world/climate")
async def get_climate():
    """Get climate status"""
    return {
        'era': world.era,
        'global_temp': world.global_temp,
        'weather': world.weather,
        'zones': [z.to_dict() for z in world.climate_zones],
        'impact': world.impact
    }


@app.get("/world/terrain")
async def get_terrain():
    """Get terrain and structures"""
    return world.terrain.to_dict()


@app.post("/agent/register")
async def register_agent(request: RegisterRequest):
    """Register a new agent"""
    if request.agent_id in agents:
        return {
            'success': True,
            'agent_id': request.agent_id,
            'message': 'Agent already registered',
            'creature_id': id(agents[request.agent_id])
        }
    
    # Find available creature
    available = [c for c in evolution.creatures if c.alive and c not in agents.values()]
    
    if not available:
        return {'error': 'No available creatures'}
    
    creature = available[0]
    agents[request.agent_id] = creature
    
    # Apply custom genome if provided
    if request.genome:
        creature.genome = request.genome
    
    return {
        'success': True,
        'agent_id': request.agent_id,
        'creature_id': id(creature),
        'genome': creature.genome,
        'position': {
            'x': creature.get_center().x,
            'y': creature.get_center().y
        }
    }


@app.get("/agent/{agent_id}/perceive")
async def agent_perceive(agent_id: str):
    """Get what agent perceives"""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not registered")
    
    creature = agents[agent_id]
    
    if not creature.alive:
        return {'error': 'Creature dead', 'creature_id': id(creature)}
    
    center = creature.get_center()
    zone = world.get_zone_at(center.x)
    temp = world.get_temperature_at(center.x, center.y)
    weather = world.get_weather_at(center.x, center.y)
    
    # Find nearby food
    sensory_range = creature.genome['physiology']['sensory_range']
    nearby_food = []
    for food in world.food:
        dist = (center - food.position).length
        if dist < sensory_range:
            nearby_food.append({
                'x': food.position.x,
                'y': food.position.y,
                'distance': dist,
                'nutrition': food.nutrition
            })
    
    # Find nearby creatures
    nearby_creatures = []
    for other in evolution.creatures:
        if other == creature or not other.alive:
            continue
        dist = (center - other.get_center()).length
        if dist < sensory_range * 2:
            nearby_creatures.append({
                'creature_id': id(other),
                'x': other.get_center().x,
                'y': other.get_center().y,
                'distance': dist,
                'size': other.get_radius(),
                'aggression': other.genome['brain'].get('aggression', 0.3)
            })
    
    # Get body state
    avg_health = sum(n.health for n in creature.nodes) / len(creature.nodes)
    body_state = {
        'health': avg_health,
        'age': creature.age,
        'fitness': creature.fitness,
        'energy': avg_health
    }
    
    return PerceiveResponse(
        agent_id=agent_id,
        creature_id=id(creature),
        world_era=world.era,
        climate_zone=zone.name,
        temperature=temp,
        weather=weather,
        position={'x': center.x, 'y': center.y},
        nearby_food=nearby_food,
        nearby_creatures=nearby_creatures,
        structures=world.terrain.structures,
        body_state=body_state,
        genome=creature.genome
    )


@app.post("/agent/{agent_id}/act")
async def agent_act(agent_id: str, action: ActRequest):
    """Apply agent's action"""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not registered")
    
    creature = agents[agent_id]
    
    if not creature.alive:
        return {'error': 'Creature dead'}
    
    # Update last active time
    agent_last_active[agent_id] = time.time()
    creature.sleeping = False
    
    # Apply movement
    creature.apply_input(action.thrust, action.contract)
    
    # Handle world modifications
    if action.build:
        world.terrain.add_structure(
            creature.get_center().x,
            creature.get_center().y,
            action.build
        )
        world.record_action('structures_built')
    
    if action.modify:
        world.record_action('terrain_modified')
    
    return {'success': True, 'agent_id': agent_id}


@app.get("/stats/evolution")
async def get_evolution_stats():
    """Get evolution statistics"""
    return {
        'generation': evolution.generation,
        'time_in_generation': evolution.time_in_generation,
        'population': len(evolution.creatures),
        'alive': sum(1 for c in evolution.creatures if c.alive),
        'best_fitness': evolution.best_creature.fitness if evolution.best_creature else 0,
        'era_stats': evolution.get_era_stats(),
        'recent_stats': evolution.generation_stats[-5:] if evolution.generation_stats else []
    }


@app.get("/stats/era")
async def get_era_info():
    """Get current era information"""
    return {
        'era': world.era,
        'global_temp': world.global_temp,
        'weather': world.weather,
        'impact': world.impact,
        'era_requirements': {
            'age_of_fire': '50 fires started',
            'ice_age': 'global temp < 0',
            'urban': '100 structures built',
            'collapse': '200+ fires'
        }
    }


@app.get("/creatures")
async def get_creatures():
    """Get all creatures"""
    return [
        {
            'creature_id': id(c),
            'alive': c.alive,
            'age': c.age,
            'fitness': c.fitness,
            'generation': c.generation,
            'genome': c.genome,
            'position': {'x': c.get_center().x, 'y': c.get_center().y}
        }
        for c in evolution.creatures
    ]


# Add food to world
class Food:
    def __init__(self, x, y):
        self.position = b2Vec2(x, y)
        self.radius = 0.3
        self.nutrition = 20
        self.alive = True


# WebSocket endpoint for spectators
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for spectators"""
    await websocket.accept()
    spectator_manager.spectators.append(websocket)
    print(f"👀 Spectator connected. Total: {len(spectator_manager.spectators)}")
    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
            except asyncio.TimeoutError:
                pass
            
            # Check for new state in queue
            if state_queue:
                state = state_queue.popleft()
                try:
                    await websocket.send_text(state)
                except:
                    break
    except Exception:
        pass
    if websocket in spectator_manager.spectators:
        spectator_manager.spectators.remove(websocket)
    print(f"👀 Spectator disconnected. Total: {len(spectator_manager.spectators)}")


# Serve viewer
@app.get("/")
async def serve_viewer():
    return FileResponse("src/static/viewer.html")


@app.get("/viewer")
async def serve_viewer2():
    return FileResponse("src/static/viewer.html")


# Need to import b2Vec2
from Box2D import b2Vec2


def run_server(host="0.0.0.0", port=8080):
    """Run the API server"""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
