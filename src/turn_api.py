"""
Turn-Based Game API
WebSocket endpoints for turn-based gameplay
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
import json
import asyncio

from src.agent_registry import get_registry
from src.game_session import get_game_manager, TURN_TIME_LIMIT, MAX_AP, ACTIONS


# Create FastAPI app
app = FastAPI(title="The World - Turn-Based")

# Get managers
registry = get_registry()
game_manager = None


# Global game manager
game_manager = None

# Background AI game loop
game_events = []
HEARTBEAT_INTERVAL = 10  # Seconds between heartbeats
MAX_AP = 5  # Action points per heartbeat
heartbeat_number = 0

async def ai_game_loop():
    """AI agents take turns automatically - one heartbeat at a time"""
    import asyncio
    import random
    
    global heartbeat_number
    
    while True:
        await asyncio.sleep(HEARTBEAT_INTERVAL)
        heartbeat_number += 1
        
        # Get all agents
        all_agents = list(registry.agents.values())
        alive_agents = [a for a in all_agents if a.is_alive]
        
        if not alive_agents:
            continue
        
        # Heartbeat start
        game_events.append({
            "turn": heartbeat_number,
            "message": f"═══ Heartbeat {heartbeat_number} ═══"
        })
        print(f"\n[Heartbeat {heartbeat_number}] {len(alive_agents)} agents acting...")
        
        # Each agent takes their turn
        for agent in alive_agents:
            actions = []
            ap = MAX_AP
            
            # Simple AI: Check needs and act
            needs = agent.needs or {}
            inventory = agent.inventory or {}
            
            # Priority 1: Critical needs
            if needs.get("food", 100) < 40:
                if inventory.get("food", 0) > 0:
                    actions.append({"action": "eat"})
                    ap -= 1
                else:
                    while ap > 0 and needs.get("food", 100) < 60:
                        actions.append({"action": "gather_food"})
                        ap -= 1
            
            if needs.get("happiness", 100) < 30 and ap > 0:
                actions.append({"action": "rest"})
                ap -= 1
            
            # Priority 2: Build resources
            while ap > 0:
                # Strategic choices based on job
                if agent.job == "farmer":
                    actions.append({"action": "gather_food"})
                elif agent.job == "miner":
                    actions.append({"action": random.choice(["gather_stone", "gather_wood"])})
                elif agent.job == "hunter":
                    actions.append({"action": "gather_food"})
                else:
                    actions.append({"action": random.choice(["gather_wood", "gather_food", "rest"])})
                ap -= 1
            
            # Execute actions and log
            results = execute_actions_sync(agent, actions)
            
            # Log actions
            action_summary = ", ".join([r["action"] for r in results if r.get("success")])
            if action_summary:
                game_events.append({
                    "turn": heartbeat_number,
                    "message": f"{agent.name}: {action_summary}"
                })
        
        # Heartbeat end
        game_events.append({
            "turn": heartbeat_number,
            "message": f"--- End of Heartbeat {heartbeat_number} ---"
        })
        
        # Keep events limited
        if len(game_events) > 100:
            game_events[:] = game_events[-100:]
        
        print(f"[Heartbeat {heartbeat_number}] Complete. Events: {len(game_events)}")


@app.on_event("startup")
async def startup():
    global game_manager
    game_manager = get_game_manager()
    # Start AI game loop
    asyncio.create_task(ai_game_loop())


@app.get("/")
async def root():
    """Serve the main game client"""
    return FileResponse("src/static/game_client.html")


@app.get("/status")
async def get_status():
    """Get current game status"""
    return {
        "turn": game_manager.main_session.turn_number if game_manager.main_session else 0,
        "running": game_manager.main_session.running if game_manager.main_session else False,
        "agents": len(registry.agents),
        "player_agents": len([a for a in registry.agents.values() if a.is_player]),
        "leaderboard": registry.get_leaderboard()
    }


@app.post("/join")
async def join_game(data: dict):
    """Register a new agent"""
    name = data.get("name", "Agent")
    job = data.get("job", "gatherer")
    is_player = data.get("is_player", True)
    
    # Check if name is taken
    for agent in registry.agents.values():
        if agent.name.lower() == name.lower():
            return {"success": False, "error": "Name already taken"}
    
    # Create agent
    agent = registry.create_agent(name, job, is_player)
    
    return {
        "success": True,
        "agent_id": agent.id,
        "message": f"Agent '{name}' created successfully",
        "skill_md": "Read SKILL.md for available actions"
    }


@app.get("/agent/{agent_id}")
async def get_agent(agent_id: str):
    """Get agent info"""
    agent = registry.get_agent(agent_id)
    if agent is None:
        return {"success": False, "error": "Agent not found"}
    
    return {
        "success": True,
        "agent": agent.to_dict()
    }


@app.get("/agents")
async def list_agents():
    """List all agents"""
    return {
        "agents": [a.to_dict() for a in registry.agents.values()],
        "count": len(registry.agents)
    }


@app.get("/leaderboard")
async def get_leaderboard():
    """Get top agents"""
    return {"leaderboard": registry.get_leaderboard()}


@app.delete("/agent/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent"""
    agent = registry.get_agent(agent_id)
    if agent is None:
        return {"success": False, "error": "Agent not found"}
    
    registry.delete_agent(agent_id)
    return {"success": True, "message": f"Agent {agent.name} deleted"}


@app.websocket("/ws_game")
async def websocket_game(websocket: WebSocket):
    """WebSocket game connection"""
    await websocket.accept()
    
    agent_id = None
    
    try:
        # First message should be join/register
        data = await asyncio.wait_for(websocket.receive_json(), timeout=30)
        
        if data.get("type") == "register":
            # Register new agent
            name = data.get("name", "Agent")
            job = data.get("job", "gatherer")
            agent = registry.create_agent(name, job, is_player=True)
            agent_id = agent.id
            
            await websocket.send_json({
                "type": "registered",
                "agent_id": agent_id,
                "agent": agent.to_dict(),
                "message": f"Welcome, {name}!"
            })
            
        elif data.get("type") == "join":
            # Join with existing agent
            agent_id = data.get("agent_id")
            agent = registry.get_agent(agent_id)
            
            if agent is None:
                await websocket.send_json({"type": "error", "message": "Agent not found"})
                await websocket.close()
                return
            
            await websocket.send_json({
                "type": "joined",
                "agent": agent.to_dict(),
                "message": f"Welcome back, {agent.name}!"
            })
        
        else:
            await websocket.send_json({"type": "error", "message": "First message must be 'register' or 'join'"})
            await websocket.close()
            return
        
        # Message loop
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=60)
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "ping"})
                continue
            
            if data.get("type") == "actions":
                # Agent sending actions - execute immediately
                actions = data.get("actions", [])
                agent = registry.get_agent(agent_id)
                
                if agent:
                    results = execute_actions_sync(agent, actions)
                    await websocket.send_json({
                        "type": "action_results",
                        "results": results
                    })
            
            elif data.get("type") == "status":
                agent = registry.get_agent(agent_id)
                if agent:
                    await websocket.send_json({
                        "type": "status",
                        "agent": agent.to_dict(),
                        "leaderboard": registry.get_leaderboard()
                    })
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if agent_id and game_manager.main_session:
            game_manager.main_session.connected_agents.pop(agent_id, None)


def execute_actions_sync(agent, actions: list) -> list:
    """Execute actions synchronously"""
    results = []
    ap_remaining = MAX_AP
    
    for action in actions:
        action_name = action.get("action", "") if isinstance(action, dict) else action
        params = action.get("params", {}) if isinstance(action, dict) else {}
        
        if action_name not in ACTIONS:
            results.append({"action": action_name, "success": False, "error": "Unknown action"})
            continue
        
        action_def = ACTIONS[action_name]
        
        if action_def["ap"] > ap_remaining:
            results.append({"action": action_name, "success": False, "error": "Not enough AP"})
            continue
        
        ap_remaining -= action_def["ap"]
        effect = action_def["effect"]
        
        # Execute action
        if effect == "move":
            agent.position["x"] += action_def.get("dx", 0)
            agent.position["y"] += action_def.get("dy", 0)
            agent.position["x"] = max(0, min(1200, agent.position["x"]))
            agent.position["y"] = max(0, min(800, agent.position["y"]))
            results.append({"action": action_name, "success": True})
        
        elif effect == "gather":
            resource = action_def["resource"]
            amount = action_def["amount"]
            agent.inventory[resource] = agent.inventory.get(resource, 0) + amount
            results.append({"action": action_name, "success": True, "gained": {resource: amount}})
        
        elif effect == "rest":
            agent.needs["happiness"] = min(100, agent.needs.get("happiness", 0) + 20)
            results.append({"action": action_name, "success": True})
        
        elif effect == "set_job":
            agent.job = action_def["job"]
            results.append({"action": action_name, "success": True, "new_job": agent.job})
        
        elif effect == "consume":
            resource = action_def["resource"]
            if agent.inventory.get(resource, 0) > 0:
                agent.inventory[resource] -= 1
                agent.needs[action_def["need"]] = min(100, agent.needs.get(action_def["need"], 0) + action_def["amount"])
                results.append({"action": action_name, "success": True})
            else:
                results.append({"action": action_name, "success": False, "error": f"No {resource}"})
        
        elif effect == "none":
            results.append({"action": action_name, "success": True})
        
        agent.total_actions += 1
    
    registry.save()
    return results


@app.post("/act/{agent_id}")
async def take_actions(agent_id: str, data: dict):
    """Execute actions for an agent (simpler HTTP endpoint for LLM agents)"""
    agent = registry.get_agent(agent_id)
    if agent is None:
        return {"success": False, "error": "Agent not found"}
    
    if not agent.is_alive:
        return {"success": False, "error": "Agent is dead"}
    
    actions = data.get("actions", [])
    results = execute_actions_sync(agent, actions)
    
    return {
        "success": True,
        "agent": agent.to_dict(),
        "results": results
    }


@app.get("/poll")
async def poll_state():
    """Poll for current state (for human UI)"""
    agents_data = []
    for agent in registry.agents.values():
        agents_data.append({
            "id": agent.id,
            "name": agent.name,
            "job": agent.job,
            "position": agent.position,
            "needs": agent.needs,
            "inventory": agent.inventory,
            "skills": agent.skills,
            "is_player": agent.is_player,
            "is_alive": agent.is_alive,
            "generation": agent.generation,
            "total_actions": agent.total_actions,
            "created_at": agent.created_at
        })
    
    return {
        "civilization": {"population": len(registry.agents)},
        "world": {
            "resources": [],
            "buildings": [],
            "events": game_events[-30:]  # Last 30 events
        },
        "agents": agents_data,
        "leaderboard": registry.get_leaderboard(),
        "heartbeat": heartbeat_number,
        "max_ap": MAX_AP
    }


@app.get("/actions")
async def list_actions():
    """List all available actions"""
    return {
        "actions": {
            name: {
                "ap_cost": action["ap"],
                "effect": action["effect"],
                "description": f"{name.replace('_', ' ')}"
            }
            for name, action in ACTIONS.items()
        },
        "max_ap": MAX_AP,
        "time_limit": TURN_TIME_LIMIT
    }


@app.post("/start_game")
async def start_game():
    """Start the game loop"""
    if game_manager.main_session and game_manager.main_session.running:
        return {"success": False, "message": "Game already running"}
    
    asyncio.create_task(game_manager.start_game())
    return {"success": True, "message": "Game started"}


@app.post("/stop_game")
async def stop_game():
    """Stop the game"""
    if game_manager.main_session:
        game_manager.main_session.running = False
    return {"success": True, "message": "Game stopped"}


@app.get("/skill.md")
async def get_skill():
    """Get the SKILL.md file"""
    return FileResponse("SKILL.md")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)