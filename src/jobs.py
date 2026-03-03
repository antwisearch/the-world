"""
Agent jobs - modular job behaviors
"""

import random


class Job:
    """Base job class"""
    name = "base"
    
    @classmethod
    def do_job(cls, agent, world):
        """Perform job action - override in subclasses"""
        pass


class Gatherer(Job):
    name = "gatherer"
    
    @classmethod
    def do_job(cls, agent, world):
        for resource in world.resources[:]:
            dx = resource['x'] - agent.x
            dy = resource['y'] - agent.y
            dist = (dx*dx + dy*dy) ** 0.5
            
            if dist < 10:
                if resource['type'] == 'food':
                    agent.inventory['food'] += resource.get('amount', 5)
                    agent.needs['food'] = min(100, agent.needs['food'] + 10)
                    world.resources.remove(resource)
                elif resource['type'] == 'wood':
                    agent.inventory['wood'] += resource.get('amount', 1)
                elif resource['type'] == 'stone':
                    agent.inventory['stone'] += resource.get('amount', 1)
                elif resource['type'] == 'ore':
                    agent.inventory['ore'] += resource.get('amount', 1)
                
                agent.skills['gathering'] += 0.1
                agent.jobs_done += 1
                break
        
        agent.move_towards(random.uniform(0, world.width), random.uniform(0, world.height), world)


class Builder(Job):
    name = "builder"
    
    BUILDINGS = {
        'workshop': {'wood': 10, 'skill': 2},
        'shelter': {'wood': 5, 'skill': 1},
        'farm': {'wood': 3, 'skill': 1}
    }
    
    @classmethod
    def do_job(cls, agent, world):
        wood = agent.inventory.get('wood', 0)
        
        # Try biggest first
        for btype, info in cls.BUILDINGS.items():
            if wood >= info['wood']:
                if btype == 'workshop':
                    world.buildings.append({
                        'type': 'workshop',
                        'x': agent.x + random.uniform(-15, 15),
                        'y': agent.y + random.uniform(-15, 15),
                        'owner': id(agent),
                        'size': 15
                    })
                elif btype == 'shelter':
                    world.buildings.append({
                        'type': 'shelter',
                        'x': agent.x + random.uniform(-10, 10),
                        'y': agent.y + random.uniform(-10, 10),
                        'owner': id(agent),
                        'size': 10
                    })
                    agent.home = world.buildings[-1]
                    agent.needs['shelter'] = min(100, agent.needs['shelter'] + 30)
                elif btype == 'farm':
                    world.buildings.append({
                        'type': 'farm',
                        'x': agent.x,
                        'y': agent.y,
                        'owner': id(agent),
                        'size': 8,
                        'growth': 0
                    })
                
                agent.inventory['wood'] -= info['wood']
                agent.skills['building'] += info['skill']
                agent.jobs_done += 1
                world.log_event(f"Agent built {btype}")
                return
        
        # Move to find wood
        agent.move_towards(random.uniform(0, world.width), random.uniform(0, world.height), world)


class Hunter(Job):
    name = "hunter"
    
    @classmethod
    def do_job(cls, agent, world):
        for prey in world.agents:
            if prey == agent or not prey.alive:
                continue
            
            dx = prey.x - agent.x
            dy = prey.y - agent.y
            dist = (dx*dx + dy*dy) ** 0.5
            
            if dist < 15:
                damage = agent.skills['combat'] * 0.01
                prey.needs['happiness'] -= damage * 10
                
                if prey.needs['happiness'] <= 0:
                    prey.alive = False
                    agent.inventory['food'] += 10
                    agent.skills['combat'] += 2
                    agent.jobs_done += 1
                    world.log_event(f"Hunter killed prey")
                break
        
        agent.move_towards(random.uniform(0, world.width), random.uniform(0, world.height), world)


class Farmer(Job):
    name = "farmer"
    
    @classmethod
    def do_job(cls, agent, world):
        # Check existing farm
        for building in world.buildings:
            if building.get('type') == 'farm' and building.get('owner') == id(agent):
                agent.inventory['food'] += 5
                agent.skills['farming'] += 0.5
                agent.jobs_done += 1
                return
        
        # Build farm
        if agent.inventory.get('wood', 0) >= 3:
            world.buildings.append({
                'type': 'farm',
                'x': agent.x,
                'y': agent.y,
                'owner': id(agent),
                'growth': 0
            })
            agent.inventory['wood'] -= 3
            agent.skills['farming'] += 1


class Trader(Job):
    name = "trader"
    
    @classmethod
    def do_job(cls, agent, world):
        for other in world.agents:
            if other == agent or not other.alive:
                continue
            
            dx = other.x - agent.x
            dy = other.y - agent.y
            dist = (dx*dx + dy*dy) ** 0.5
            
            if dist < 5:
                if agent.inventory.get('food', 0) > 5 and other.inventory.get('goods', 0) > 0:
                    agent.inventory['food'] -= 3
                    other.inventory['food'] += 3
                    agent.inventory['goods'] += 1
                    other.inventory['goods'] -= 1
                    
                    agent.needs['happiness'] = min(100, agent.needs['happiness'] + 5)
                    other.needs['happiness'] = min(100, other.needs['happiness'] + 5)
                    
                    agent.skills['trading'] += 1
                    agent.jobs_done += 1


class Guard(Job):
    name = "guard"
    
    @classmethod
    def do_job(cls, agent, world):
        if agent.home:
            agent.move_towards(agent.home['x'], agent.home['y'], world)
        
        for enemy in world.agents:
            if enemy == agent or not enemy.alive:
                continue
            
            dx = enemy.x - agent.x
            dy = enemy.y - agent.y
            dist = (dx*dx + dy*dy) ** 0.5
            
            if dist < 20 and enemy.genome.get('aggression', 0.3) > 0.5:
                enemy.needs['happiness'] -= agent.skills['combat'] * 0.1
                agent.skills['combat'] += 0.5


# Job registry
JOBS = {
    'gatherer': Gatherer,
    'builder': Builder,
    'hunter': Hunter,
    'farmer': Farmer,
    'trader': Trader,
    'guard': Guard
}


def get_job(name):
    """Get job class by name"""
    return JOBS.get(name, Gatherer)
