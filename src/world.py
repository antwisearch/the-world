"""
World - Modular world with resources and buildings
"""

import random
from src.resources import spawn_resource, spawn_initial_resources
from src.events import trigger_random_event
from src.history import WorldHistory
from src.artifacts import ArtifactManager, ArtifactGenerator
from src.legends import LegendsManager
from src.event_chains import setup_event_chains, check_for_chain
from src.terrain import TerrainGenerator
from src.biomes import BiomeResourceManager
from src.relationships import RelationshipManager
from src.goap import GOAPAgent, plan_for_goal
from src.economy import Economy
from src.seasons import SeasonManager
from src.more_events import EVENTS as MORE_EVENTS


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
        
        # World History
        self.history = WorldHistory()
        
        # Artifacts
        self.artifacts = ArtifactManager()
        
        # Legends system
        self.legends = LegendsManager()
        
        # Event chains
        setup_event_chains()
        
        # Terrain generation
        self.terrain = TerrainGenerator(width, height)
        
        # Biome-based resources
        self.biome_manager = BiomeResourceManager(self)
        
        # Relationships
        self.relationships = RelationshipManager()
        
        # Economy
        self.economy = Economy(self)
        
        # Seasons
        self.seasons = SeasonManager()
        
        # Spawn initial resources
        spawn_initial_resources(self)
        
        # Initialize biome resources
        self.biome_manager.spawn_biome_resources()
    
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
        # Economy
        self.economy.tick()
        
        # Trigger random events
        event_result = trigger_random_event(self)
        
        # Trigger more events (lower chance)
        if random.random() < 0.001:  # 0.1% chance per tick
            more_event = random.choice(MORE_EVENTS)
            more_event.apply(self)
        
        # Check for event chains
        if event_result:
            event_name = list(event_result.keys())[0] if event_result else None
            if event_name:
                chain_result = check_for_chain(self, event_name)
        
        # Update raiders
        if hasattr(self, 'raiders'):
            for raider in self.raiders:
                if not raider.alive:
                    continue
                # Raiders attack nearest agent
                alive = [a for a in self.agents if a.alive]
                if alive:
                    target = min(alive, key=lambda a: ((a.x-raider.x)**2 + (a.y-raider.y)**2)**0.5)
                    raider.move_towards(target.x, target.y, self)
                    if ((target.x-raider.x)**2 + (target.y-raider.y)**2)**0.5 < 5:
                        target.needs['happiness'] -= 10
                        if target.needs['happiness'] <= 0:
                            target.alive = False
        
        # Update agents
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
            # Record death properly
            if agent.needs['food'] <= 0:
                cause = 'starvation'
            elif agent.needs['water'] <= 0:
                cause = 'dehydration'
            else:
                cause = 'violence'  # Default
            
            # Check if should become a legend
            legend = self.legends.check_agent(agent, self.history.year)
            if legend:
                self.log_event(f"📜 {agent.biography.name} has become a legend!")
            
            # Record in biography
            agent.biography.record_death(agent.age, cause, 
                                         {'x': agent.x, 'y': agent.y})
            
            # Generate artifacts from dead agent
            new_artifacts = ArtifactGenerator.generate_from_agent(agent)
            for art in new_artifacts:
                art.x = agent.x + random.uniform(-10, 10)
                art.y = agent.y + random.uniform(-10, 10)
                self.artifacts.add_artifact(art)
            
            # Record in world history
            obituary = agent.biography.generate_obituary()
            if obituary:
                self.log_event(obituary)
            
            # Check for legendary death
            is_legendary = (agent.biography.kills > 5 or 
                          agent.biography.buildings_built > 5)
            self.history.record_death(agent.biography.name, cause, is_legendary)
            
            self.remove_agent(agent)
        
        # Advance world time
        self.history.advance_year()
        
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
        # Sample biomes across the map
        biome_samples = {}
        if hasattr(self, 'biome_manager'):
            sample_points = [
                (self.width * 0.25, self.height * 0.25),
                (self.width * 0.75, self.height * 0.75),
                (self.width * 0.5, self.height * 0.5),
                (self.width * 0.25, self.height * 0.75),
                (self.width * 0.75, self.height * 0.25),
            ]
            for x, y in sample_points:
                biome = self.biome_manager.get_biome_at(x, y)
                biome_samples[biome] = biome_samples.get(biome, 0) + 1
        
        return {
            'width': self.width,
            'height': self.height,
            'era': self.era,
            'resources': self.resources,
            'buildings': self.buildings,
            'water_sources': self.water_sources,
            'agents_count': len([a for a in self.agents if a.alive]),
            'events': self.events[-10:],
            'history': self.history.to_dict(),
            'artifacts': self.artifacts.to_dict(),
            'legends': self.legends.to_dict(),
            'biome': list(biome_samples.keys())[0] if biome_samples else 'unknown',
            'biomes': list(biome_samples.keys()),
            'relationships': self.relationships.to_dict(),
            'economy': self.economy.to_dict(),
            'seasons': self.seasons.to_dict()
        }
