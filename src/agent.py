"""
Agent - Dwarf Fortress style creature with needs, jobs, skills
"""

import random


class Agent:
    """An agent with needs, jobs, skills, and inventory"""
    
    JOBS = ['gatherer', 'builder', 'hunter', 'farmer', 'trader', 'guard']
    
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
        
        # Position and movement
        self.position = {'x': x, 'y': y}
        self.velocity = {'x': 0, 'y': 0}
        
        # Needs (0-100)
        self.needs = {
            'food': 80,
            'water': 80,
            'shelter': 50,
            'happiness': 70
        }
        
        # Job assignment
        self.job = random.choice(self.JOBS)
        
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
        
        # Home (structure)
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
        
        # Food decreases based on metabolism
        self.needs['food'] -= dt * 2 * metabolism
        self.needs['water'] -= dt * 3  # Water depletes faster
        
        # Shelter affects happiness
        if self.home:
            self.needs['shelter'] = min(100, self.needs['shelter'] + dt * 5)
            self.needs['happiness'] = min(100, self.needs['happiness'] + dt * 2)
        else:
            self.needs['shelter'] -= dt * 2
            self.needs['happiness'] -= dt * 3
        
        # Low food affects happiness
        if self.needs['food'] < 20:
            self.needs['happiness'] -= dt * 5
        
        # Check death
        if self.needs['food'] <= 0 or self.needs['water'] <= 0:
            self.alive = False
        
        # Clamp needs
        for need in self.needs:
            self.needs[need] = max(0, min(100, self.needs[need]))
    
    def do_job(self, world):
        """Perform job actions based on assigned job"""
        if not self.alive:
            return
        
        if self.job == 'gatherer':
            self.gather(world)
        elif self.job == 'builder':
            self.build(world)
        elif self.job == 'hunter':
            self.hunt(world)
        elif self.job == 'farmer':
            self.farm(world)
        elif self.job == 'trader':
            self.trade(world)
        elif self.job == 'guard':
            self.guard(world)
    
    def gather(self, world):
        """Gather resources from environment"""
        # Find nearby resources
        for resource in world.resources[:]:
            dx = resource['x'] - self.x
            dy = resource['y'] - self.y
            dist = (dx*dx + dy*dy) ** 0.5
            
            if dist < 10:  # Can gather
                if resource['type'] == 'food':
                    self.inventory['food'] += resource.get('amount', 5)
                    self.needs['food'] = min(100, self.needs['food'] + 10)
                    world.resources.remove(resource)
                elif resource['type'] == 'wood':
                    self.inventory['wood'] += resource.get('amount', 1)
                elif resource['type'] == 'stone':
                    self.inventory['stone'] += resource.get('amount', 1)
                elif resource['type'] == 'ore':
                    self.inventory['ore'] += resource.get('amount', 1)
                
                # Skill up
                self.skills['gathering'] += 0.1
                self.jobs_done += 1
                break
        
        # Move randomly to find resources
        self.move_towards(random.uniform(0, world.width), random.uniform(0, world.height), world)
    
    def build(self, world):
        """Build structures"""
        wood = self.inventory.get('wood', 0)
        
        if wood >= 10:
            # Build workshop
            world.buildings.append({
                'type': 'workshop',
                'x': self.x + random.uniform(-15, 15),
                'y': self.y + random.uniform(-15, 15),
                'owner': id(self),
                'size': 15
            })
            self.inventory['wood'] -= 10
            self.skills['building'] += 2
            self.jobs_done += 1
            
        elif wood >= 5:
            # Build shelter
            world.buildings.append({
                'type': 'shelter',
                'x': self.x + random.uniform(-10, 10),
                'y': self.y + random.uniform(-10, 10),
                'owner': id(self),
                'size': 10
            })
            self.inventory['wood'] -= 5
            self.needs['shelter'] = min(100, self.needs['shelter'] + 30)
            self.home = world.buildings[-1]
            self.skills['building'] += 1
            self.jobs_done += 1
            
        elif wood >= 3:
            # Build farm
            world.buildings.append({
                'type': 'farm',
                'x': self.x,
                'y': self.y,
                'owner': id(self),
                'size': 8,
                'growth': 0
            })
            self.inventory['wood'] -= 3
            self.skills['building'] += 1
            self.jobs_done += 1
        else:
            # Move to find wood
            self.move_towards(random.uniform(0, world.width), random.uniform(0, world.height), world)
    
    def hunt(self, world):
        """Hunt for food"""
        # Look for prey
        for prey in world.agents:
            if prey == self or not prey.alive:
                continue
            
            dx = prey.x - self.x
            dy = prey.y - self.y
            dist = (dx*dx + dy*dy) ** 0.5
            
            if dist < 15:
                # Attack
                damage = self.skills['combat'] * 0.01
                prey.needs['happiness'] -= damage * 10
                
                if prey.needs['happiness'] <= 0:
                    # Kill and take food
                    prey.alive = False
                    self.inventory['food'] += 10
                    self.skills['combat'] += 2
                    self.jobs_done += 1
                break
        
        # Move to find prey
        self.move_towards(random.uniform(0, world.width), random.uniform(0, world.height), world)
    
    def farm(self, world):
        """Farm food"""
        # Check for farm plot
        for building in world.buildings:
            if building.get('type') == 'farm' and building.get('owner') == id(self):
                # Harvest
                self.inventory['food'] += 5
                self.skills['farming'] += 0.5
                self.jobs_done += 1
                return
        
        # Build farm if have resources
        if self.inventory.get('wood', 0) >= 3:
            world.buildings.append({
                'type': 'farm',
                'x': self.x,
                'y': self.y,
                'owner': id(self),
                'growth': 0
            })
            self.inventory['wood'] -= 3
            self.skills['farming'] += 1
    
    def trade(self, world):
        """Trade with other agents"""
        for other in world.agents:
            if other == self or not other.alive:
                continue
            
            dx = other.x - self.x
            dy = other.y - self.y
            dist = (dx*dx + dy*dy) ** 0.5
            
            if dist < 5:
                # Exchange goods
                if self.inventory.get('food', 0) > 5 and other.inventory.get('goods', 0) > 0:
                    self.inventory['food'] -= 3
                    other.inventory['food'] += 3
                    self.inventory['goods'] += 1
                    other.inventory['goods'] -= 1
                    
                    self.needs['happiness'] = min(100, self.needs['happiness'] + 5)
                    other.needs['happiness'] = min(100, other.needs['happiness'] + 5)
                    
                    self.skills['trading'] += 1
                    self.jobs_done += 1
    
    def guard(self, world):
        """Guard area"""
        # Stay near home or center
        if self.home:
            self.move_towards(self.home['x'], self.home['y'], world)
        
        # Look for threats
        for enemy in world.agents:
            if enemy == self or not enemy.alive:
                continue
            
            dx = enemy.x - self.x
            dy = enemy.y - self.y
            dist = (dx*dx + dy*dy) ** 0.5
            
            if dist < 20 and enemy.genome.get('aggression', 0.3) > 0.5:
                # Attack
                enemy.needs['happiness'] -= self.skills['combat'] * 0.1
                self.skills['combat'] += 0.5
    
    def move_towards(self, target_x, target_y, world):
        """Move towards target"""
        dx = target_x - self.x
        dy = target_y - self.y
        dist = (dx*dx + dy*dy) ** 0.5
        
        if dist > 1:
            speed = 2  # Movement speed
            self.x += (dx / dist) * speed
            self.y += (dy / dist) * speed
        
        # Clamp to world bounds
        self.x = max(0, min(world.width, self.x))
        self.y = max(0, min(world.height, self.y))
        
        # Update position dict
        self.position = {'x': self.x, 'y': self.y}
    
    def eat(self):
        """Eat from inventory"""
        if self.inventory.get('food', 0) > 0:
            self.inventory['food'] -= 1
            self.needs['food'] = min(100, self.needs['food'] + 20)
    
    def drink(self, world):
        """Find water to drink"""
        for water in world.water_sources:
            dx = water['x'] - self.x
            dy = water['y'] - self.y
            dist = (dx*dx + dy*dy) ** 0.5
            
            if dist < 5:
                self.needs['water'] = min(100, self.needs['water'] + 30)
                return True
        return False
    
    def get_state(self):
        """Get agent state for API"""
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
