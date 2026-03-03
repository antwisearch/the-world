"""
AI Behavior - better agent decision making
"""

import random


class Behavior:
    """Base behavior"""
    
    @classmethod
    def think(cls, agent, world):
        """Decide what to do - override"""
        pass


class Survivor(Behavior):
    """Prioritize needs"""
    
    @classmethod
    def think(cls, agent, world):
        # Critical needs
        if agent.needs['food'] < 20:
            # Find food
            food = world.resources
            if food:
                nearest = min(food, key=lambda r: ((r['x']-agent.x)**2 + (r['y']-agent.y)**2)**0.5)
                agent.move_towards(nearest['x'], nearest['y'], world)
                return 'seeking_food'
        
        if agent.needs['water'] < 20:
            # Find water
            water = world.water_sources
            if water:
                nearest = min(water, key=lambda w: ((w['x']-agent.x)**2 + (w['y']-agent.y)**2)**0.5)
                agent.move_towards(nearest['x'], nearest['y'], world)
                return 'seeking_water'
        
        if agent.needs['shelter'] < 20:
            # Find or build shelter
            agent.job = 'builder'
            return 'seeking_shelter'
        
        if agent.needs['happiness'] < 30:
            # Find other agents to socialize
            others = [a for a in world.agents if a != agent and a.alive]
            if others:
                friend = min(others, key=lambda a: ((a.x-agent.x)**2 + (a.y-agent.y)**2)**0.5)
                if ((friend.x-agent.x)**2 + (friend.y-agent.y)**2)**0.5 > 10:
                    agent.move_towards(friend.x, friend.y, world)
                    return 'socializing'
        
        return None


class Defender(Behavior):
    """Respond to threats"""
    
    @classmethod
    def think(cls, agent, world):
        # Check for raiders
        if hasattr(world, 'raiders'):
            for raider in world.raiders:
                dist = ((raider.x - agent.x)**2 + (raider.y - agent.y)**2)**0.5
                if dist < 30:
                    # Defend!
                    agent.job = 'guard'
                    agent.move_towards(raider.x, raider.y, world)
                    return 'defending'
        
        # Check for low happiness - might leave
        if agent.needs['happiness'] < 10:
            # Sad agent might leave
            if random.random() < 0.01:
                world.log_event(f"😢 A {agent.job} has left the colony")
                agent.alive = False
        
        return None


class Builder(Behavior):
    """Build intelligently"""
    
    @classmethod
    def think(cls, agent, world):
        # If builder and has resources, build
        if agent.job == 'builder':
            wood = agent.inventory.get('wood', 0)
            
            # Priority: shelter if homeless
            if not agent.home and wood >= 5:
                return None  # Let builder job handle
            
            # Build farm if food low
            if agent.needs['food'] < 50 and wood >= 3:
                return None
            
            # Otherwise store wood
            return 'building'
        
        return None


class FarmerBehavior(Behavior):
    """Farm intelligently"""
    
    @classmethod
    def think(cls, agent, world):
        if agent.job == 'farmer':
            # Check existing farm
            for b in world.buildings:
                if b.get('type') == 'farm' and b.get('owner') == id(agent):
                    return 'farming'
            
            # Build farm if has resources
            if agent.inventory.get('wood', 0) >= 3:
                return None  # Let farmer job handle
        
        return None


# Registry
BEHAVIORS = [
    Survivor,
    Defender,
    Builder,
    FarmerBehavior
]


def agent_think(agent, world):
    """Main AI thinking - called each tick"""
    for behavior in BEHAVIORS:
        result = behavior.think(agent, world)
        if result:
            return result
    
    # Default: continue job
    return 'working'
