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

# Serve chronicle (agent book)
@app.get("/chronicle")
async def serve_chronicle():
    return FileResponse("src/static/chronicle.html")

# Serve player dashboard
@app.get("/player")
async def serve_player():
    return FileResponse("src/static/player.html")


# Player actions
@app.post("/action")
async def player_action(data: dict):
    try:
        action = data.get('action', '')
        
        # Process actions
        result = {"success": False, "message": "Unknown action"}
        
        # Get resources count
        resources = world.resources if hasattr(world, 'resources') else []
        res_count = {}
        for r in resources:
            res_count[r.type] = res_count.get(r.type, 0) + getattr(r, 'amount', 1)
        
        if action == 'recruit':
            if res_count.get('food', 0) >= 20:
                result = {"success": True, "message": "New settler recruited! (+1 population)"}
            else:
                result = {"success": False, "message": "Need 20 food to recruit"}
        
        elif action == 'build_shelter':
            if res_count.get('wood', 0) >= 10:
                result = {"success": True, "message": "Shelter construction started!"}
            else:
                result = {"success": False, "message": "Need 10 wood to build shelter"}
        
        elif action == 'build_farm':
            if res_count.get('wood', 0) >= 15:
                result = {"success": True, "message": "Farm construction started!"}
            else:
                result = {"success": False, "message": "Need 15 wood to build farm"}
        
        elif action == 'gather':
            result = {"success": True, "message": "Gathering resources... (+5 wood, +3 food)"}
        
        elif action == 'mine':
            result = {"success": True, "message": "Mining... (+2 ore, +1 stone)"}
        
        elif action == 'trade':
            result = {"success": True, "message": "Trading post ready!"}
        
        return result
    except Exception as e:
        return {"success": False, "message": str(e)}


# Create player's agent
player_agent = None

@app.post("/create_agent")
async def create_player_agent(data: dict):
    global player_agent
    try:
        name = data.get('name', 'Player')
        job = data.get('job', 'gatherer')
        
        # Create agent
        from src.agent import Agent
        import random
        
        agent = Agent(
            random.uniform(100, 1100),
            random.uniform(100, 700)
        )
        agent.job = job
        agent.biography.name = name
        agent.is_player = True  # Mark as player's agent
        
        # Add to world
        with state_lock:
            world.agents.append(agent)
            player_agent = agent
        
        return {
            "success": True,
            "message": f"{name} has entered the world!",
            "agent": {
                "name": name,
                "job": job,
                "position": {"x": agent.x, "y": agent.y}
            }
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


@app.get("/my_agent")
async def get_player_agent():
    global player_agent
    if player_agent is None:
        return {"success": False, "message": "No player agent yet. Create one first!"}
    
    try:
        with state_lock:
            if hasattr(player_agent, 'get_state'):
                state = player_agent.get_state()
                state['is_player'] = True
                return {"success": True, "agent": state}
            else:
                return {"success": False, "message": "Agent not found"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@app.post("/command")
async def command_agent(data: dict):
    global player_agent
    if player_agent is None:
        return {"success": False, "message": "No player agent. Create one first!"}
    
    try:
        command = data.get('command', '')
        
        # Process commands for player's agent
        result = {"success": True, "message": f"Command '{command}' acknowledged"}
        
        # Movement commands
        if command == 'move_north':
            player_agent.y = max(0, player_agent.y - 10)
            result['message'] = "Moved north"
        elif command == 'move_south':
            player_agent.y = min(800, player_agent.y + 10)
            result['message'] = "Moved south"
        elif command == 'move_east':
            player_agent.x = min(1200, player_agent.x + 10)
            result['message'] = "Moved east"
        elif command == 'move_west':
            player_agent.x = max(0, player_agent.x - 10)
            result['message'] = "Moved west"
        
        # Job commands
        elif command.startswith('set_job_'):
            new_job = command.replace('set_job_', '')
            player_agent.job = new_job
            result['message'] = f"Now working as {new_job}"
        
        # Action commands
        elif command == 'gather_food':
            player_agent.inventory['food'] = player_agent.inventory.get('food', 0) + 3
            result['message'] = "Gathered 3 food"
        elif command == 'gather_wood':
            player_agent.inventory['wood'] = player_agent.inventory.get('wood', 0) + 2
            result['message'] = "Gathered 2 wood"
        elif command == 'rest':
            player_agent.needs['happiness'] = min(100, player_agent.needs.get('happiness', 0) + 20)
            result['message'] = "Rested (+20 happiness)"
        
        return result
    except Exception as e:
        return {"success": False, "message": str(e)}


# Polling endpoint (fallback when WebSocket fails)
@app.get("/poll")
async def poll_state():
    with state_lock:
        return {
            'world': world.get_state(),
            'civilization': civilization.get_stats(),
            'agents': [a.get_state() for a in world.agents if a.alive]
        }


# Error logging endpoint
@app.post("/log-error")
async def log_error(request):
    try:
        data = await request.json()
        with open("js-errors.log", "a") as f:
            f.write(f"[{data.get('msg', 'unknown')}] at {data.get('url', '')}:{data.get('line', '')}:{data.get('col', '')}\n")
            if data.get('error'):
                f.write(f"  Stack: {data.get('error')}\n")
        return {"status": "logged"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


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
async def save_simulation(filename: str = "savegame"):
    with state_lock:
        try:
            from src.save_manager import SaveManager
            filepath = SaveManager.save_game(world, filename)
            return {'success': True, 'filename': filepath}
        except Exception as e:
            return {'error': str(e)}


@app.get("/load/{filename}")
async def load_simulation(filename: str = "savegame"):
    with state_lock:
        try:
            from src.save_manager import SaveManager
            save_data = SaveManager.load_game(filename)
            if save_data is None:
                return {'error': 'Save file not found'}
            return save_data
        except Exception as e:
            return {'error': str(e)}


@app.get("/saves")
async def list_saves():
    try:
        from src.save_manager import SaveManager
        return {'saves': SaveManager.list_saves()}
    except Exception as e:
        return {'error': str(e), 'saves': []}


# Trading endpoints
@app.get("/trading/offers")
async def get_offers():
    """Get available trade offers"""
    from src.trading import trade_manager
    offers = []
    for offer in trade_manager.get_available_offers():
        offers.append({
            'id': offer.id,
            'seller': offer.seller,
            'items_offering': offer.items_offering,
            'items_wanted': offer.items_wanted,
            'gold_offering': offer.gold_offering,
            'gold_wanted': offer.gold_wanted,
            'created_at': offer.created_at
        })
    return {'offers': offers}


@app.get("/trading/market")
async def get_market_prices():
    """Get current market prices"""
    from src.trading import trade_manager
    return {'prices': trade_manager.market_prices}


@app.get("/trading/history")
async def get_trade_history():
    """Get recent trades"""
    from src.trading import trade_manager
    trades = []
    for trade in trade_manager.get_trade_history(20):
        trades.append({
            'id': trade.id,
            'buyer': trade.buyer,
            'seller': trade.seller,
            'items': trade.items,
            'gold': trade.gold,
            'timestamp': trade.timestamp
        })
    return {'trades': trades}


@app.get("/trading/items")
async def get_trade_items():
    """Get list of tradeable items"""
    from src.trading import ITEMS
    return {'items': ITEMS}


@app.get("/trading/traders")
async def get_traders():
    """Get active wandering traders"""
    from src.trading import trade_manager
    return {'traders': trade_manager.get_active_traders()}


@app.get("/trading/shops")
async def get_shops():
    """Get all shops"""
    from src.trading import trade_manager
    return {'shops': trade_manager.get_shops()}


@app.get("/trading/shops/near")
async def get_shops_near(x: int, y: int, radius: int = 100):
    """Get shops near a location"""
    from src.trading import trade_manager
    return {'shops': trade_manager.get_shops_near(x, y, radius)}


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
