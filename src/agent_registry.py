"""
Agent Registry - Persistent storage for game agents
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import uuid


AGENTS_FILE = "agents.json"


@dataclass
class PersistentAgent:
    """Agent data that persists across sessions"""
    id: str
    name: str
    job: str
    created_at: str
    last_active: str
    position: Dict
    needs: Dict
    skills: Dict
    inventory: Dict
    is_player: bool
    is_alive: bool
    generation: int
    deaths: int
    total_actions: int
    
    def to_dict(self):
        return asdict(self)


class AgentRegistry:
    """Manages persistent agents"""
    
    def __init__(self, data_dir: str = "."):
        self.data_dir = data_dir
        self.agents: Dict[str, PersistentAgent] = {}
        self.load()
    
    def load(self):
        """Load agents from disk"""
        filepath = os.path.join(self.data_dir, AGENTS_FILE)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    for agent_id, agent_data in data.items():
                        self.agents[agent_id] = PersistentAgent(**agent_data)
                print(f"Loaded {len(self.agents)} persistent agents")
            except Exception as e:
                print(f"Error loading agents: {e}")
                self.agents = {}
    
    def save(self):
        """Save agents to disk"""
        filepath = os.path.join(self.data_dir, AGENTS_FILE)
        try:
            data = {aid: agent.to_dict() for aid, agent in self.agents.items()}
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving agents: {e}")
    
    def create_agent(self, name: str, job: str = "gatherer", is_player: bool = False) -> PersistentAgent:
        """Create a new persistent agent"""
        agent_id = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()
        
        agent = PersistentAgent(
            id=agent_id,
            name=name,
            job=job,
            created_at=now,
            last_active=now,
            position={"x": 600, "y": 400},  # Center of map
            needs={"food": 80, "water": 80, "shelter": 50, "happiness": 70},
            skills={
                "gathering": 10,
                "farming": 10,
                "building": 10,
                "combat": 10,
                "trading": 10,
                "healing": 10,
                "teaching": 10,
                "research": 10
            },
            inventory={"food": 5, "wood": 2},
            is_player=is_player,
            is_alive=True,
            generation=1,
            deaths=0,
            total_actions=0
        )
        
        self.agents[agent_id] = agent
        self.save()
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[PersistentAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def get_player_agents(self) -> List[PersistentAgent]:
        """Get all player-controlled agents"""
        return [a for a in self.agents.values() if a.is_player and a.is_alive]
    
    def get_ai_agents(self) -> List[PersistentAgent]:
        """Get all AI-controlled agents"""
        return [a for a in self.agents.values() if not a.is_player and a.is_alive]
    
    def update_agent(self, agent_id: str, **kwargs):
        """Update agent properties"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            for key, value in kwargs.items():
                if hasattr(agent, key):
                    setattr(agent, key, value)
            agent.last_active = datetime.now().isoformat()
            self.save()
    
    def record_action(self, agent_id: str, action: str, success: bool):
        """Record an action taken by an agent"""
        if agent_id in self.agents:
            self.agents[agent_id].total_actions += 1
            self.save()
    
    def kill_agent(self, agent_id: str, cause: str = "unknown"):
        """Mark agent as dead"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.is_alive = False
            agent.deaths += 1
            self.save()
            print(f"Agent {agent.name} died: {cause}")
    
    def reset_agent(self, agent_id: str):
        """Reset agent to starting state (after death)"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.is_alive = True
            agent.position = {"x": 600, "y": 400}
            agent.needs = {"food": 80, "water": 80, "shelter": 50, "happiness": 70}
            agent.inventory = {"food": 5, "wood": 2}
            agent.generation += 1
            self.save()
    
    def delete_agent(self, agent_id: str):
        """Delete an agent permanently"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            self.save()
    
    def get_leaderboard(self) -> List[Dict]:
        """Get leaderboard of top agents"""
        sorted_agents = sorted(
            self.agents.values(),
            key=lambda a: (a.total_actions, a.generation),
            reverse=True
        )
        return [
            {
                "rank": i + 1,
                "name": a.name,
                "job": a.job,
                "generation": a.generation,
                "actions": a.total_actions,
                "alive": a.is_alive
            }
            for i, a in enumerate(sorted_agents[:10])
        ]


# Global registry instance
registry = None

def get_registry(data_dir: str = ".") -> AgentRegistry:
    """Get or create the global registry"""
    global registry
    if registry is None:
        registry = AgentRegistry(data_dir)
    return registry