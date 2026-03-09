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
from src.story_archive import get_archive


# Create FastAPI app
app = FastAPI(title="The World - Turn-Based")

# Get managers
registry = get_registry()
game_manager = None


# Global game manager
game_manager = None

# Background AI game loop
game_events = []
HEARTBEAT_INTERVAL = 1800  # 30 minutes between heartbeats (long-term game)
MAX_AP = 5  # Action points per heartbeat
heartbeat_number = 0
story_archive = None

def generate_diary(agent, actions: list, results: list) -> str:
    """Generate a diary entry for an agent based on their actions"""
    
    name = agent.name
    job = agent.job
    position = agent.position
    
    # Build action summary
    action_summary = []
    for r in results:
        if r.get("success"):
            action = r.get("action", "unknown")
            if action.startswith("gather_"):
                resource = action.replace("gather_", "")
                action_summary.append(f"gathered some {resource}")
            elif action == "rest":
                action_summary.append("took a moment to rest")
            elif action.startswith("move_"):
                direction = action.replace("move_", "")
                action_summary.append(f"traveled {direction}")
            elif action.startswith("set_job_"):
                new_job = action.replace("set_job_", "")
                action_summary.append(f"became a {new_job}")
            else:
                action_summary.append(action.replace("_", " "))
    
    # Generate diary based on actions and job
    import random
    
    templates = [
        f"Another heartbeat passes. I {', '.join(action_summary[:3])}. ",
        f"The day's work is done. I {', '.join(action_summary[:2])}. ",
        f"I spent this heartbeat {', '.join(action_summary[:3])}. ",
    ]
    
    base = random.choice(templates)
    
    # Add job-specific thoughts
    job_thoughts = {
        "farmer": "The soil needs tending. Every seed planted is hope for tomorrow.",
        "hunter": "The forest holds many secrets. Today I seek, tomorrow I might find.",
        "miner": "Deep in the earth, treasures await those patient enough to dig.",
        "builder": "Stone by stone, we raise structures that will outlast us all.",
        "gatherer": "The world provides for those who take the time to look.",
        "trader": "Value is in the eye of the beholder. Everything can be traded.",
    }
    
    thought = job_thoughts.get(job, "Each action brings me closer to my goals.")
    
    # Add needs-based thoughts
    needs = agent.needs or {}
    if needs.get("food", 100) < 50:
        base += " My stomach growls with hunger. "
    if needs.get("happiness", 100) < 30:
        base += " I feel weary in spirit. "
    
    # Add inventory thoughts
    inventory = agent.inventory or {}
    if inventory.get("wood", 0) >= 8:
        base += " My collection of wood grows. "
    if inventory.get("food", 0) >= 10:
        base += " I have gathered plenty of food. "
    
    return base + thought


async def ai_game_loop():
    """AI agents take turns automatically - one heartbeat at a time"""
    import asyncio
    import random
    
    global heartbeat_number, story_archive
    
    # Initialize story archive
    story_archive = get_archive("stories")
    
    while True:
        await asyncio.sleep(HEARTBEAT_INTERVAL)
        heartbeat_number += 1
        
        # Get all agents
        all_agents = list(registry.agents.values())
        player_agents = [a for a in all_agents if a.is_player and a.is_alive]
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
            
            # Determine actions based on needs and job
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
            
            # Priority 2: Job-based actions
            while ap > 0:
                if agent.job == "farmer":
                    actions.append({"action": "gather_food"})
                elif agent.job == "miner":
                    actions.append({"action": random.choice(["gather_stone", "gather_wood"])})
                elif agent.job == "hunter":
                    actions.append({"action": "gather_food"})
                elif agent.job == "trader":
                    actions.append({"action": random.choice(["gather_wood", "gather_food"])})
                else:
                    actions.append({"action": random.choice(["gather_wood", "gather_food", "rest"])})
                ap -= 1
            
            # Execute actions
            results = execute_actions_sync(agent, actions)
            
            # Log actions
            action_names = [r["action"] for r in results if r.get("success")]
            if action_names:
                game_events.append({
                    "turn": heartbeat_number,
                    "message": f"{agent.name}: {', '.join(action_names)}"
                })
            
            # Write diary entry (for player agents - LLM agents)
            if agent.is_player:
                diary = generate_diary(agent, actions, results)
                story_archive.save_diary(
                    agent_id=agent.id,
                    agent_name=agent.name,
                    heartbeat=heartbeat_number,
                    actions=actions,
                    diary=diary,
                    position=agent.position,
                    mood="neutral"
                )
                game_events.append({
                    "turn": heartbeat_number,
                    "message": f"📜 {agent.name} wrote in their diary."
                })
        
        # Heartbeat end
        game_events.append({
            "turn": heartbeat_number,
            "message": f"--- End of Heartbeat {heartbeat_number} ---"
        })
        
        # Keep events limited
        if len(game_events) > 100:
            game_events[:] = game_events[-100:]
        
        print(f"[Heartbeat {heartbeat_number}] Complete. Stories saved.")


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


@app.get("/diaries/{agent_id}")
async def get_agent_diaries(agent_id: str, limit: int = 50):
    """Get all diaries for an agent"""
    diaries = story_archive.get_all_diaries(agent_id, limit)
    return {
        "success": True,
        "agent_id": agent_id,
        "diaries": diaries
    }


@app.get("/stories")
async def get_all_stories():
    """Get recent stories from all agents"""
    events = story_archive.get_recent_events(100)
    return {
        "success": True,
        "stories": events
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