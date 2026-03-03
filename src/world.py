"""
World - Dwarf Fortress style with resources, buildings, zones
"""

import random


class World:
    """The game world with resources and buildings"""
    
    def __init__(self, width=1200, height=800):
        self.width = width
        self.height = height
        
        # Resources (food, wood, stone, ore)
        self.resources = []
        
        # Buildings (shelters, farms, workshops)
        self.buildings = []
        
        # Water sources
        self.water_sources = [
            {'x': 200, 'y': 200, 'radius': 50},
            {'x': 800, 'y': 600, 'radius': 80}
        ]
        
        # Agents in the world
        self.agents = []
        
        # Events (for storytelling)
        self.events = []
        
        # Era
        self.era = 'settlement'
        
        # Spawn initial resources
        self.spawn_resources()
    
    def spawn_resources(self):
        """Spawn resources in the world"""
        # Food sources
        for _ in range(30):
            self.resources.append({
                'type': 'food',
                'x': random.uniform(50, self.width - 50),
                'y': random.uniform(50, self.height - 50),
                'amount': random.randint(5, 15)
            })
        
        # Wood (forests)
        for _ in range(20):
            self.resources.append({
                'type': 'wood',
                'x': random.uniform(50, self.width - 50),
                'y': random.uniform(50, self.height - 50),
                'amount': random.randint(3, 10)
            })
        
        # Stone
        for _ in range(15):
            self.resources.append({
                'type': 'stone',
                'x': random.uniform(50, self.width - 50),
                'y': random.uniform(50, self.height - 50),
                'amount': random.randint(2, 8)
            })
        
        # Ore
        for _ in range(10):
            self.resources.append({
                'type': 'ore',
                'x': random.uniform(50, self.width - 50),
                'y': random.uniform(50, self.height - 50),
                'amount': random.randint(1, 5)
            })
    
    def spawn_more_resources(self):
        """Spawn more resources over time"""
        # Food respawns
        if random.random() < 0.3:
            self.resources.append({
                'type': 'food',
                'x': random.uniform(50, self.width - 50),
                'y': random.uniform(50, self.height - 50),
                'amount': random.randint(5, 15)
            })
        
        # Trees grow
        if random.random() < 0.1:
            self.resources.append({
                'type': 'wood',
                'x': random.uniform(50, self.width - 50),
                'y': random.uniform(50, self.height - 50),
                'amount': random.randint(3, 10)
            })
    
    def add_agent(self, agent):
        """Add an agent to the world"""
        self.agents.append(agent)
    
    def remove_agent(self, agent):
        """Remove an agent from the world"""
        if agent in self.agents:
            self.agents.remove(agent)
    
    def update(self, dt):
        """Update world"""
        # Update all agents
        for agent in self.agents:
            if agent.alive:
                # Update needs
                agent.update_needs(dt)
                
                # Do job
                agent.do_job(self)
                
                # Eat if hungry
                if agent.needs['food'] < 30:
                    agent.eat()
                
                # Drink if thirsty
                if agent.needs['water'] < 30:
                    agent.drink(self)
                
                # Update fitness (survival + jobs done)
                agent.fitness += dt * (1 + agent.jobs_done * 0.1)
        
        # Remove dead agents
        dead = [a for a in self.agents if not a.alive]
        for agent in dead:
            self.remove_agent(agent)
            self.log_event(f"Agent died (age: {agent.age:.1f}, jobs: {agent.jobs_done})")
        
        # Spawn more resources
        self.spawn_more_resources()
    
    def log_event(self, message):
        """Log an event"""
        self.events.append({
            'time': len(self.events),
            'message': message
        })
        # Keep only last 100 events
        if len(self.events) > 100:
            self.events = self.events[-100:]
    
    def get_state(self):
        """Get world state for API"""
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
