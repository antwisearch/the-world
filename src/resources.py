"""
Resource system - modular resources
"""

import random


class ResourceType:
    """Base resource type"""
    name = "base"
    symbol = "?"
    color = "#fff"
    
    @classmethod
    def on_gather(cls, agent, resource):
        """Called when agent gathers this resource"""
        pass


class Food(ResourceType):
    name = "food"
    symbol = "*"
    color = "#0f0"
    
    @classmethod
    def on_gather(cls, agent, resource):
        agent.inventory['food'] += resource.get('amount', 5)
        agent.needs['food'] = min(100, agent.needs['food'] + 10)


class Wood(ResourceType):
    name = "wood"
    symbol = "T"
    color = "#8B4513"
    
    @classmethod
    def on_gather(cls, agent, resource):
        agent.inventory['wood'] += resource.get('amount', 1)


class Stone(ResourceType):
    name = "stone"
    symbol = "O"
    color = "#888"
    
    @classmethod
    def on_gather(cls, agent, resource):
        agent.inventory['stone'] += resource.get('amount', 1)


class Ore(ResourceType):
    name = "ore"
    symbol = "#"
    color = "#CD853F"
    
    @classmethod
    def on_gather(cls, agent, resource):
        agent.inventory['ore'] += resource.get('amount', 1)


# Resource registry
RESOURCES = {
    'food': Food,
    'wood': Wood,
    'stone': Stone,
    'ore': Ore
}


def get_resource(name):
    return RESOURCES.get(name, ResourceType)


def spawn_resource(world, rtype=None):
    """Spawn a random resource"""
    if rtype is None:
        rtype = random.choice(['food', 'food', 'food', 'wood', 'wood', 'stone', 'ore'])
    
    amounts = {
        'food': (5, 15),
        'wood': (3, 10),
        'stone': (2, 8),
        'ore': (1, 5)
    }
    
    min_a, max_a = amounts.get(rtype, (1, 5))
    
    return {
        'type': rtype,
        'x': random.uniform(50, world.width - 50),
        'y': random.uniform(50, world.height - 50),
        'amount': random.randint(min_a, max_a)
    }


def spawn_initial_resources(world):
    """Spawn initial resources"""
    # More food
    for _ in range(30):
        world.resources.append(spawn_resource(world, 'food'))
    
    # Wood
    for _ in range(20):
        world.resources.append(spawn_resource(world, 'wood'))
    
    # Stone
    for _ in range(15):
        world.resources.append(spawn_resource(world, 'stone'))
    
    # Ore
    for _ in range(10):
        world.resources.append(spawn_resource(world, 'ore'))
