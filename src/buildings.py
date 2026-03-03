"""
Building system - modular buildings
"""

import random


class BuildingType:
    """Base building type"""
    name = "base"
    symbol = "B"
    cost = {'wood': 0}
    
    @classmethod
    def on_build(cls, agent, world):
        """Called when built"""
        pass
    
    @classmethod
    def tick(cls, building, agent, world):
        """Called each tick - return effect"""
        pass


class Shelter(BuildingType):
    name = "shelter"
    symbol = "[#]"
    cost = {'wood': 5}
    
    @classmethod
    def on_build(cls, agent, world):
        agent.needs['shelter'] = min(100, agent.needs['shelter'] + 30)
        agent.home = None  # Will be set by caller


class Farm(BuildingType):
    name = "farm"
    symbol = "[+]"
    cost = {'wood': 3}
    
    @classmethod
    def tick(cls, building, agent, world):
        # Grow food
        building['growth'] = building.get('growth', 0) + 0.1
        if building['growth'] >= 10:
            agent.inventory['food'] += 3
            building['growth'] = 0
            return {'harvest': 3}
        return None


class Workshop(BuildingType):
    name = "workshop"
    symbol = "[%]"
    cost = {'wood': 10}
    
    @classmethod
    def on_build(cls, agent, world):
        # Can produce goods here
        pass
    
    @classmethod
    def tick(cls, building, agent, world):
        # Produce goods occasionally
        if random.random() < 0.01:
            agent.inventory['goods'] += 1
            return {'produced': 1}
        return None


# Building registry
BUILDINGS = {
    'shelter': Shelter,
    'farm': Farm,
    'workshop': Workshop
}


def get_building(name):
    return BUILDINGS.get(name, BuildingType)


def build(agent, world, btype):
    """Try to build a structure"""
    bclass = get_building(btype)
    cost = bclass.cost
    
    # Check resources
    for res, amount in cost.items():
        if agent.inventory.get(res, 0) < amount:
            return False, f"Need {amount} {res}"
    
    # Pay cost
    for res, amount in cost.items():
        agent.inventory[res] -= amount
    
    # Build
    building = {
        'type': btype,
        'x': agent.x + random.uniform(-10, 10),
        'y': agent.y + random.uniform(-10, 10),
        'owner': id(agent),
        'size': 10
    }
    
    world.buildings.append(building)
    bclass.on_build(agent, world)
    
    return True, f"Built {btype}"
