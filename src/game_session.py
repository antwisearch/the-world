"""
Turn-Based Game Session Handler
WebSocket-based turn system for AI agents
"""

import asyncio
import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
import uuid

from src.agent_registry import get_registry, PersistentAgent


# Action definitions with AP costs
ACTIONS = {
    # Movement (1 AP)
    "move_north": {"ap": 1, "effect": "move", "dx": 0, "dy": -10},
    "move_south": {"ap": 1, "effect": "move", "dx": 0, "dy": 10},
    "move_east": {"ap": 1, "effect": "move", "dx": 10, "dy": 0},
    "move_west": {"ap": 1, "effect": "move", "dx": -10, "dy": 0},
    
    # Gathering (1 AP)
    "gather_food": {"ap": 1, "effect": "gather", "resource": "food", "amount": 3},
    "gather_wood": {"ap": 1, "effect": "gather", "resource": "wood", "amount": 2},
    "gather_stone": {"ap": 1, "effect": "gather", "resource": "stone", "amount": 1},
    
    # Rest (1 AP)
    "rest": {"ap": 1, "effect": "rest", "happiness": 20},
    
    # Job changes (1 AP)
    "set_job_farmer": {"ap": 1, "effect": "set_job", "job": "farmer"},
    "set_job_hunter": {"ap": 1, "effect": "set_job", "job": "hunter"},
    "set_job_builder": {"ap": 1, "effect": "set_job", "job": "builder"},
    "set_job_miner": {"ap": 1, "effect": "set_job", "job": "miner"},
    "set_job_trader": {"ap": 1, "effect": "set_job", "job": "trader"},
    "set_job_guard": {"ap": 1, "effect": "set_job", "job": "guard"},
    "set_job_gatherer": {"ap": 1, "effect": "set_job", "job": "gatherer"},
    
    # Building (2 AP)
    "build_shelter": {"ap": 2, "effect": "build", "type": "shelter", "cost": {"wood": 10}},
    "build_farm": {"ap": 2, "effect": "build", "type": "farm", "cost": {"wood": 15}},
    
    # Consumables (1 AP)
    "eat": {"ap": 1, "effect": "consume", "resource": "food", "need": "food", "amount": 30},
    "drink": {"ap": 1, "effect": "consume", "resource": "water", "need": "water", "amount": 30},
    
    # Trade (1 AP)
    "trade": {"ap": 1, "effect": "trade"},
    
    # Wait (0 AP)
    "wait": {"ap": 0, "effect": "none"},
    
    # Debug
    "debug": {"ap": 0, "effect": "debug"},
}

# Time limit per turn (seconds)
TURN_TIME_LIMIT = 30

# Max AP per turn
MAX_AP = 3


@dataclass
class GameSession:
    """A game session with connected agents"""
    session_id: str
    turn_number: int
    current_agent_index: int
    agent_order: List[str]
    connected_agents: Dict[str, any]  # agent_id -> websocket
    pending_actions: Dict[str, List]
    world_state: Dict
    running: bool
    round_phase: str  # "player_turns" or "ai_turns"
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.turn_number = 1
        self.current_agent_index = 0
        self.agent_order = []
        self.connected_agents = {}
        self.pending_actions = {}
        self.world_state = {}
        self.running = False
        self.round_phase = "player_turns"


class TurnGameManager:
    """Manages turn-based game sessions"""
    
    def __init__(self, world):
        self.world = world
        self.registry = get_registry()
        self.sessions: Dict[str, GameSession] = {}
        self.main_session: Optional[GameSession] = None
    
    def create_session(self) -> GameSession:
        """Create a new game session"""
        session = GameSession(str(uuid.uuid4())[:8])
        self.sessions[session.session_id] = session
        return session
    
    def get_or_create_main_session(self) -> GameSession:
        """Get the main game session or create it"""
        if self.main_session is None or not self.main_session.running:
            self.main_session = self.create_session()
        return self.main_session
    
    def join_game(self, agent_id: str, websocket) -> bool:
        """Add an agent to the game"""
        session = self.get_or_create_main_session()
        agent = self.registry.get_agent(agent_id)
        
        if agent is None:
            return False
        
        if agent_id not in session.agent_order:
            session.agent_order.append(agent_id)
        
        session.connected_agents[agent_id] = websocket
        
        # Send welcome message
        welcome = {
            "type": "joined",
            "session_id": session.session_id,
            "your_agent": agent.to_dict(),
            "message": f"Welcome, {agent.name}! Waiting for game to start..."
        }
        asyncio.create_task(websocket.send_json(welcome))
        
        return True
    
    async def start_game(self):
        """Start the turn-based game loop"""
        session = self.get_or_create_main_session()
        if session.running:
            return
        
        session.running = True
        
        # Game loop
        while session.running:
            await self.run_turn(session)
    
    async def run_turn(self, session: GameSession):
        """Run a single turn"""
        # Update world state
        session.world_state = self.get_world_state()
        
        # Check if there are player agents
        player_agents = [aid for aid in session.agent_order 
                        if self.registry.get_agent(aid).is_player]
        
        if not player_agents:
            # No players, run AI turn
            await self.run_ai_turn(session)
            return
        
        # Player turns
        for agent_id in session.agent_order[:]:
            if not session.running:
                break
            
            agent = self.registry.get_agent(agent_id)
            if agent is None or not agent.is_alive:
                continue
            
            # Notify agent it's their turn
            await self.notify_turn(session, agent_id)
            
            # Wait for actions (with timeout)
            actions = await self.wait_for_actions(session, agent_id)
            
            # Execute actions
            await self.execute_actions(session, agent_id, actions)
            
            # Notify all of state change
            await self.broadcast_state(session)
        
        # AI turn
        await self.run_ai_turn(session)
        
        # End turn
        session.turn_number += 1
    
    async def notify_turn(self, session: GameSession, agent_id: str):
        """Notify an agent it's their turn"""
        agent = self.registry.get_agent(agent_id)
        if agent_id not in session.connected_agents:
            return
        
        ws = session.connected_agents[agent_id]
        message = {
            "type": "your_turn",
            "turn_number": session.turn_number,
            "your_agent": agent.to_dict(),
            "world_state": session.world_state,
            "action_points": MAX_AP,
            "time_limit": TURN_TIME_LIMIT,
            "available_actions": list(ACTIONS.keys())
        }
        
        try:
            await ws.send_json(message)
        except Exception as e:
            print(f"Error notifying {agent_id}: {e}")
    
    async def wait_for_actions(self, session: GameSession, agent_id: str) -> List[Dict]:
        """Wait for agent's actions with timeout"""
        start_time = time.time()
        actions = []
        ap_remaining = MAX_AP
        
        while time.time() - start_time < TURN_TIME_LIMIT:
            if agent_id in session.pending_actions:
                actions = session.pending_actions.pop(agent_id)
                break
            await asyncio.sleep(0.1)
        
        # Validate and filter actions
        valid_actions = []
        for action in actions:
            action_name = action.get("action", "") if isinstance(action, dict) else action
            if action_name in ACTIONS:
                ap_cost = ACTIONS[action_name]["ap"]
                if ap_remaining >= ap_cost:
                    valid_actions.append(action)
                    ap_remaining -= ap_cost
                else:
                    print(f"Not enough AP for {action_name}")
            else:
                print(f"Invalid action: {action_name}")
        
        return valid_actions
    
    async def execute_actions(self, session: GameSession, agent_id: str, actions: List[Dict]):
        """Execute a list of actions for an agent"""
        agent = self.registry.get_agent(agent_id)
        if agent is None:
            return
        
        results = []
        
        for action in actions:
            action_name = action.get("action", "") if isinstance(action, dict) else action
            params = action.get("params", {}) if isinstance(action, dict) else {}
            
            if action_name not in ACTIONS:
                results.append({"action": action_name, "success": False, "error": "Unknown action"})
                continue
            
            action_def = ACTIONS[action_name]
            effect = action_def["effect"]
            
            # Execute based on effect type
            if effect == "move":
                agent.position["x"] += action_def.get("dx", 0)
                agent.position["y"] += action_def.get("dy", 0)
                # Clamp to world bounds
                agent.position["x"] = max(0, min(1200, agent.position["x"]))
                agent.position["y"] = max(0, min(800, agent.position["y"]))
                results.append({"action": action_name, "success": True, "new_pos": agent.position})
            
            elif effect == "gather":
                resource = action_def["resource"]
                amount = action_def["amount"]
                agent.inventory[resource] = agent.inventory.get(resource, 0) + amount
                results.append({"action": action_name, "success": True, "gained": {resource: amount}})
            
            elif effect == "rest":
                agent.needs["happiness"] = min(100, agent.needs.get("happiness", 0) + action_def["happiness"])
                results.append({"action": action_name, "success": True})
            
            elif effect == "set_job":
                agent.job = action_def["job"]
                results.append({"action": action_name, "success": True, "new_job": agent.job})
            
            elif effect == "build":
                # Check resources
                can_build = True
                for res, cost in action_def["cost"].items():
                    if agent.inventory.get(res, 0) < cost:
                        can_build = False
                        break
                
                if can_build:
                    for res, cost in action_def["cost"].items():
                        agent.inventory[res] -= cost
                    # Add building to world (simplified)
                    results.append({"action": action_name, "success": True, "built": action_def["type"]})
                else:
                    results.append({"action": action_name, "success": False, "error": "Not enough resources"})
            
            elif effect == "consume":
                resource = action_def["resource"]
                if agent.inventory.get(resource, 0) > 0:
                    agent.inventory[resource] -= 1
                    agent.needs[action_def["need"]] = min(100, agent.needs.get(action_def["need"], 0) + action_def["amount"])
                    results.append({"action": action_name, "success": True})
                else:
                    results.append({"action": action_name, "success": False, "error": f"No {resource} in inventory"})
            
            elif effect == "debug":
                results.append({"action": action_name, "success": True, "state": agent.to_dict()})
            
            elif effect == "none":
                results.append({"action": action_name, "success": True})
            
            agent.total_actions += 1
        
        # Save changes
        self.registry.save()
        
        # Send results
        if agent_id in session.connected_agents:
            try:
                await session.connected_agents[agent_id].send_json({
                    "type": "action_results",
                    "results": results
                })
            except:
                pass
    
    async def run_ai_turn(self, session: GameSession):
        """Run AI agent turns"""
        ai_agents = self.registry.get_ai_agents()
        
        for agent in ai_agents:
            if not agent.is_alive:
                continue
            
            # Simple AI: gather food if hungry, else gather wood
            actions = []
            
            if agent.needs.get("food", 100) < 50:
                actions.append({"action": "gather_food"})
            else:
                actions.append({"action": "gather_wood"})
            
            if agent.needs.get("happiness", 100) < 30:
                actions.append({"action": "rest"})
            
            # Execute AI actions
            await self.execute_actions(session, agent.id, actions)
    
    async def broadcast_state(self, session: GameSession):
        """Broadcast current state to all connected agents"""
        state = self.get_world_state()
        state["type"] = "state_update"
        state["turn_number"] = session.turn_number
        
        disconnected = []
        for agent_id, ws in session.connected_agents.items():
            try:
                await ws.send_json(state)
            except:
                disconnected.append(agent_id)
        
        # Remove disconnected
        for agent_id in disconnected:
            session.connected_agents.pop(agent_id, None)
    
    def get_world_state(self) -> Dict:
        """Get current world state"""
        return {
            "agents": [a.to_dict() for a in self.registry.agents.values()],
            "leaderboard": self.registry.get_leaderboard(),
            "resources": [],  # Would come from world
            "buildings": [],  # Would come from world
        }
    
    def receive_actions(self, session_id: str, agent_id: str, actions: List):
        """Receive actions from an agent"""
        session = self.sessions.get(session_id)
        if session:
            session.pending_actions[agent_id] = actions


# Global game manager
game_manager = None

def get_game_manager(world=None) -> TurnGameManager:
    """Get or create the global game manager"""
    global game_manager
    if game_manager is None:
        game_manager = TurnGameManager(world)
    return game_manager