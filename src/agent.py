"""
Agent - Modular Dwarf Fortress style creature
"""

import random
from src.jobs import get_job, JOBS
from src.resources import get_resource
from src.behaviors import agent_think
from src.biography import Biography
from src.names import generate_full_name
from src.utility_ai import BehaviorTree, UtilityScore
from src.goap import plan_for_goal


class Agent:
    """An agent with needs, jobs, skills, and inventory"""
    
    def __init__(self, x, y, genome=None):
        self.x = x
        self.y = y
        self.alive = True
        self.generation = 1
        
        # Wealth
        self.wealth = random.randint(0, 20)
        
        # Genome / traits
        if genome:
            self.genome = genome
        else:
            self.genome = self.random_genome()
        
        # Biography - name, life story, family
        self.biography = Biography(x, y, self.generation)
        
        # Position
        self.position = {'x': x, 'y': y}
        
        # Needs (0-100)
        self.needs = {
            'food': 80,
            'water': 80,
            'shelter': 50,
            'happiness': 70
        }
        
        # Job assignment - use best job
        self.job = random.choice(list(JOBS.keys()))
        
        # Skills (0-100)
        self.skills = {
            'gathering': random.randint(10, 30),
            'building': random.randint(10, 30),
            'combat': random.randint(10, 30),
            'farming': random.randint(10, 30),
            'trading': random.randint(10, 30)
        }
        
        # Inventory
        self.inventory = {
            'food': random.randint(0, 10),
            'wood': 0,
            'stone': 0,
            'ore': 0,
            'goods': 0
        }
        
        # Home (building)
        self.home = None
        
        # Stats
        self.age = 0
        self.fitness = 0
        self.jobs_done = 0
    
    def random_genome(self):
        return {
            'body_size': random.uniform(0.8, 1.5),
            'color': (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)),
            'metabolism': random.uniform(0.3, 0.8),
            'sociability': random.uniform(0.2, 0.8),
            'aggression': random.uniform(0.1, 0.5)
        }
    
    def update_needs(self, dt):
        """Update needs over time"""
        metabolism = self.genome.get('metabolism', 0.5)
        
        self.needs['food'] -= dt * 2 * metabolism
        self.needs['water'] -= dt * 3
        
        # Shelter affects happiness
        if self.home:
            self.needs['shelter'] = min(100, self.needs['shelter'] + dt * 5)
            self.needs['happiness'] = min(100, self.needs['happiness'] + dt * 2)
        else:
            self.needs['shelter'] -= dt * 2
            self.needs['happiness'] -= dt * 3
        
        if self.needs['food'] < 20:
            self.needs['happiness'] -= dt * 5
        
        if self.needs['food'] <= 0 or self.needs['water'] <= 0:
            self.alive = False
        
        for need in self.needs:
            self.needs[need] = max(0, min(100, self.needs[need]))
    
    def do_job(self, world):
        """Perform job - uses Behavior Tree for decisions"""
        if not self.alive:
            return
        
        # Use Behavior Tree for priority decisions
        action, priority = BehaviorTree.evaluate(self, world)
        
        # Handle critical needs first
        if action == 'find_food':
            self._find_food(world)
            return
        elif action == 'find_water':
            self._find_water(world)
            return
        elif action == 'build_shelter':
            self._build_emergency_shelter(world)
            return
        
        # Then do normal job
        job_class = get_job(self.job)
        job_class.do_job(self, world)
    
    def _find_food(self, world):
        """Emergency food finding"""
        # Look for food
        for resource in world.resources:
            if resource['type'] == 'food':
                self.move_towards(resource['x'], resource['y'], world)
                if ((self.x - resource['x'])**2 + (self.y - resource['y'])**2)**0.5 < 5:
                    self.inventory['food'] = self.inventory.get('food', 0) + resource.get('amount', 1)
                    world.resources.remove(resource)
                    self.eat()
                    self.biography.achievements.append("found food in emergency")
                    return
        
        # Hunt if no food found
        self.job = 'hunter'
        job_class = get_job('hunter')
        job_class.do_job(self, world)
    
    def _find_water(self, world):
        """Emergency water finding"""
        for water in world.water_sources:
            dx = water['x'] - self.x
            dy = water['y'] - self.y
            dist = (dx*dx + dy*dy) ** 0.5
            
            if dist < water.get('radius', 50):
                self.needs['water'] = min(100, self.needs['water'] + 50)
                self.biography.achievements.append("found water in emergency")
                return
        
        # Move toward nearest water
        if world.water_sources:
            nearest = min(world.water_sources, key=lambda w: 
                (w['x']-self.x)**2 + (w['y']-self.y)**2)
            self.move_towards(nearest['x'], nearest['y'], world)
    
    def _build_emergency_shelter(self, world):
        """Build shelter in emergency"""
        # Check if we have resources
        if self.inventory.get('wood', 0) >= 10:
            # Add a simple shelter marker
            from src.buildings import Shelter
            building = Shelter()
            building.x = self.x + random.uniform(-10, 10)
            building.y = self.y + random.uniform(-10, 10)
            self.home = building
            self.inventory['wood'] -= 10
            self.biography.buildings_built += 1
            self.biography.achievements.append("built emergency shelter")
        else:
            # Gather wood first
            self.job = 'builder'
            job_class = get_job('builder')
            job_class.do_job(self, world)
    
    def move_towards(self, target_x, target_y, world):
        """Move towards target"""
        dx = target_x - self.x
        dy = target_y - self.y
        dist = (dx*dx + dy*dy) ** 0.5
        
        if dist > 1:
            speed = 2
            self.x += (dx / dist) * speed
            self.y += (dy / dist) * speed
        
        self.x = max(0, min(world.width, self.x))
        self.y = max(0, min(world.height, self.y))
        self.position = {'x': self.x, 'y': self.y}
    
    def eat(self):
        if self.inventory.get('food', 0) > 0:
            self.inventory['food'] -= 1
            self.needs['food'] = min(100, self.needs['food'] + 20)
    
    def drink(self, world):
        for water in world.water_sources:
            dx = water['x'] - self.x
            dy = water['y'] - self.y
            dist = (dx*dx + dy*dy) ** 0.5
            
            if dist < 5:
                self.needs['water'] = min(100, self.needs['water'] + 30)
                return True
        return False
    
    def get_state(self):
        return {
            'name': self.biography.name,
            'position': self.position,
            'alive': self.alive,
            'needs': self.needs,
            'job': self.job,
            'skills': self.skills,
            'inventory': self.inventory,
            'wealth': self.wealth,
            'generation': self.generation,
            'fitness': self.fitness,
            'personality': self.biography.personality_traits
        }
