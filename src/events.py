"""
Event system - random events, dangers, stories
"""

import random


class Event:
    """Base event"""
    name = "base"
    
    @classmethod
    def trigger(cls, world, chance=0.001):
        """Trigger event with given chance"""
        if random.random() < chance:
            return cls.apply(world)
        return None
    
    @classmethod
    def apply(cls, world):
        """Apply event effects"""
        pass


class Raiders(Event):
    """Raiders attack!"""
    name = "raiders"
    
    @classmethod
    def apply(cls, world):
        # Spawn raiders
        raiders = []
        for _ in range(3):
            from src.agent import Agent
            raider = Agent(
                random.uniform(0, world.width),
                random.uniform(0, world.height)
            )
            raider.job = 'hunter'  # Attackers
            raider.needs['happiness'] = 100
            raider.genome['aggression'] = 1.0
            raiders.append(raider)
        
        world.raiders = raiders
        world.log_event("⚔️ Raiders spotted approaching!")
        
        return {'raiders': len(raiders)}


class Wanderer(Event):
    """Wanderer arrives"""
    name = "wanderer"
    
    @classmethod
    def apply(cls, world):
        from src.agent import Agent
        wanderer = Agent(
            random.uniform(0, world.width),
            random.uniform(0, world.height)
        )
        wanderer.needs['food'] = 10
        world.add_agent(wanderer)
        world.log_event("🚶 A wanderer has joined the colony")
        
        return {'joined': True}


class Discovery(Event):
    """Found something"""
    name = "discovery"
    
    DISCOVERIES = [
        ('found a gem vein', 'ore', 10),
        ('discovered a spring', 'water', 5),
        ('found ancient ruins', 'history', 1),
        ('found a cave', ' shelter', 1)
    ]
    
    @classmethod
    def apply(cls, world):
        disc, restype, amount = random.choice(cls.DISCOVERIES)
        
        if restype == 'ore':
            for _ in range(5):
                world.resources.append({
                    'type': 'ore',
                    'x': random.uniform(50, world.width-50),
                    'y': random.uniform(50, world.height-50),
                    'amount': amount
                })
        elif restype == 'water':
            world.water_sources.append({
                'x': random.uniform(100, world.width-100),
                'y': random.uniform(100, world.height-100),
                'radius': 30
            })
        
        world.log_event(f"💎 Scout {disc}!")
        
        return {'discovery': disc}


class Plague(Event):
    """Sickness spreads"""
    name = "plague"
    
    @classmethod
    def apply(cls, world):
        # Random agent gets sick
        alive = [a for a in world.agents if a.alive]
        if alive:
            victim = random.choice(alive)
            victim.needs['happiness'] -= 30
            world.log_event(f"🤒 {victim.job} has fallen ill!")
        
        return {'sick': True}


class GoodHarvest(Event):
    """Bountiful harvest"""
    name = "good_harvest"
    
    @classmethod
    def apply(cls, world):
        for _ in range(10):
            world.resources.append({
                'type': 'food',
                'x': random.uniform(50, world.width-50),
                'y': random.uniform(50, world.height-50),
                'amount': 20
            })
        
        world.log_event("🌾 Excellent harvest! Food is plentiful!")
        
        return {'food': 10}


class TradeCaravan(Event):
    """Trading caravan arrives"""
    name = "trade_caravan"
    
    @classmethod
    def apply(cls, world):
        # Give random resources
        alive = [a for a in world.agents if a.alive]
        for _ in range(3):
            if alive:
                agent = random.choice(alive)
                agent.inventory['goods'] += 5
        
        world.log_event("🐪 Trade caravan has arrived!")
        
        return {'goods': 5}


class Attack(Event):
    """Agents attack each other"""
    name = "attack"
    
    @classmethod
    def apply(cls, world):
        alive = [a for a in world.agents if a.alive]
        if len(alive) >= 2:
            a1, a2 = random.sample(alive, 2)
            damage = random.randint(10, 30)
            a2.needs['happiness'] -= damage
            world.log_event(f"⚔️ {a1.job} attacked {a2.job}!")
            
            if a2.needs['happiness'] <= 0:
                a2.alive = False
                world.log_event(f"💀 {a2.job} was killed!")
        
        return {'attack': True}


# Event registry
EVENTS = [
    Raiders,
    Wanderer,
    Discovery,
    Plague,
    GoodHarvest,
    TradeCaravan,
    Attack
]


def trigger_random_event(world):
    """Trigger a random event"""
    for event in EVENTS:
        result = event.trigger(world)
        if result:
            return result
    return None
