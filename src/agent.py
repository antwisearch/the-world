"""
Agent - Modular Dwarf Fortress style creature
"""

import random
from src.jobs import get_job, JOBS
from src.resources import get_resource


class Agent:
    """An agent with needs, jobs, skills, and inventory"""
    
    def __init__(self, x, y, genome=None):
        self.x = x
        self.y = y
        self.alive = True
        self.generation = 1
        
        # Genome / traits
        if genome:
            self.genome = genome
        else:
            self.genome = self.random_genome()
        
        # Position
        self.position = {'x': x, 'y': y}
        
        # Needs (0-100)
        self.needs = {
            'food': 80,
            'water': 80,
            'shelter': 50,
            'happiness': 70
        }
        
        # Job assignment
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
        """Perform job - uses modular job system"""
        if not self.alive:
            return
        
        job_class = get_job(self.job)
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
            'position': self.position,
            'alive': self.alive,
            'needs': self.needs,
            'job': self.job,
            'skills': self.skills,
            'inventory': self.inventory,
            'generation': self.generation,
            'fitness': self.fitness
        }
