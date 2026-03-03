"""
World - Modular world with resources and buildings
"""

import random
from src.resources import spawn_resource, spawn_initial_resources


class World:
    """The game world"""
    
    def __init__(self, width=1200, height=800):
        self.width = width
        self.height = height
        
        # Resources
        self.resources = []
        
        # Buildings
        self.buildings = []
        
        # Water sources
        self.water_sources = [
            {'x': 200, 'y': 200, 'radius': 50},
            {'x': 800, 'y': 600, 'radius': 80}
        ]
        
        # Agents
        self.agents = []
        
        # Events
        self.events = []
        
        # Era
        self.era = 'settlement'
        
        # Spawn initial resources
        spawn_initial_resources(self)
    
    def spawn_more_resources(self):
        """Spawn more resources over time"""
        if random.random() < 0.3:
            self.resources.append(spawn_resource(self, 'food'))
        
        if random.random() < 0.1:
            self.resources.append(spawn_resource(self, 'wood'))
    
    def add_agent(self, agent):
        self.agents.append(agent)
    
    def remove_agent(self, agent):
        if agent in self.agents:
            self.agents.remove(agent)
    
    def update(self, dt):
        """Update world"""
        for agent in self.agents:
            if agent.alive:
                agent.update_needs(dt)
                agent.do_job(self)
                
                if agent.needs['food'] < 30:
                    agent.eat()
                
                if agent.needs['water'] < 30:
                    agent.drink(self)
                
                agent.fitness += dt * (1 + agent.jobs_done * 0.1)
        
        # Remove dead
        dead = [a for a in self.agents if not a.alive]
        for agent in dead:
            self.remove_agent(agent)
            self.log_event(f"Agent died (age: {agent.age:.1f}, jobs: {agent.jobs_done})")
        
        # Spawn resources
        self.spawn_more_resources()
    
    def log_event(self, message):
        self.events.append({
            'time': len(self.events),
            'message': message
        })
        if len(self.events) > 100:
            self.events = self.events[-100:]
    
    def get_state(self):
        return {
            'width': self.width,
            'height': self.height,
            'era': self.era,
            'resources': self.resources,
            'buildings': self.buildings,
            'water_sources': self.water_sources,
            'agents_count': len([a for a in self.agents if a.alive]),
            'events': self.events[-10:]
        }
