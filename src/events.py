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
            raider.biography.name = f"Raider {random.randint(1,100)}"
            raiders.append(raider)
        
        world.raiders = raiders
        
        # Get a random defender
        defenders = [a for a in world.agents if a.alive and a.job == 'guard']
        if defenders:
            defender = random.choice(defenders)
            world.log_event(f"⚔️ Raiders attacking! {defender.biography.name} defends!")
        else:
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
        world.log_event(f"🚶 {wanderer.biography.name} has joined the colony")
        
        return {'joined': True}


class Discovery(Event):
    """Found something"""
    name = "discovery"
    
    DISCOVERIES = [
        ('found a gem vein', 'ore', 10),
        ('discovered a spring', 'water', 5),
        ('found ancient ruins', 'history', 1),
        ('found a cave', 'shelter', 1),
        ('found buried treasure', 'treasure', 1),
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
            # Find who discovered
            workers = [a for a in world.agents if a.alive and a.job == 'gatherer']
            discoverer = random.choice(workers) if workers else None
            if discoverer:
                discoverer.biography.achievements.append("found gem vein")
                world.log_event(f"💎 {discoverer.biography.name} {disc}!")
            else:
                world.log_event(f"💎 Scout {disc}!")
                
        elif restype == 'water':
            world.water_sources.append({
                'x': random.uniform(100, world.width-100),
                'y': random.uniform(100, world.height-100),
                'radius': 30
            })
            world.log_event(f"🌊 A new spring has been discovered!")
        
        elif restype == 'treasure':
            from src.artifacts import Artifact
            treasures = [
                ("Ancient Gold Coin", "A coin from a fallen kingdom", 50),
                ("Mysterious Artifact", "An artifact of unknown origin", 100),
                ("Hero's Sword", "A sword of legend", 200),
            ]
            name, desc, val = random.choice(treasures)
            art = Artifact(name, 'treasure', desc, val)
            art.x = random.uniform(100, world.width-100)
            art.y = random.uniform(100, world.height-100)
            art.found = True
            world.artifacts.add_found(art)
            world.log_event(f"🗝️ {name} found!")
        
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
            victim.needs['food'] -= 20
            world.log_event(f"🤒 {victim.biography.name} has fallen ill!")
        
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
        
        farmers = [a for a in world.agents if a.alive and a.job == 'farmer']
        if farmers:
            farmer = random.choice(farmers)
            farmer.biography.achievements.append("good harvest")
            world.log_event(f"🌾 Excellent harvest thanks to {farmer.biography.name}!")
        else:
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
            
            world.log_event(f"⚔️ {a1.biography.name} ({a1.job}) attacked {a2.biography.name} ({a2.job})!")
            
            if a2.needs['happiness'] <= 0:
                a2.alive = False
                a1.biography.kills += 1
                a1.biography.achievements.append(f"killed {a2.biography.name}")
                world.log_event(f"💀 {a2.biography.name} was killed by {a1.biography.name}!")
                
                # Check for legendary battle
                if a1.biography.kills >= 5:
                    world.log_event(f"🏆 {a1.biography.name} has become a legendary warrior!")
        
        return {'attack': True}


class HeroicDeath(Event):
    """A heroic death is recorded"""
    name = "heroic_death"
    
    @classmethod
    def apply(cls, world):
        # Check for agents with many kills who died
        dead_killers = [a for a in world.agents if not a.alive and hasattr(a, 'biography') 
                       and a.biography.kills >= 3]
        
        if dead_killers:
            hero = random.choice(dead_killers)
            world.log_event(f"⚔️ {hero.biography.name} died heroically with {hero.biography.kills} kills!")
            
            # Add to legends
            legend = world.history.add_legend(
                hero.biography.name,
                "the Fallen Hero",
                f"Killed {hero.biography.kills} enemies in battle"
            )
            for deed in hero.biography.achievements:
                legend.add_deed(deed)
        
        return None


class Disaster(Event):
    """Natural disaster"""
    name = "disaster"
    
    DISASTERS = [
        ("Flood", "A terrible flood has struck!"),
        ("Fire", "A fire has broken out!"),
        ("Earthquake", "The ground shakes!"),
        ("Storm", "A fierce storm approaches!"),
    ]
    
    @classmethod
    def apply(cls, world):
        name, desc = random.choice(cls.DISASTERS)
        
        # Random agents affected
        alive = [a for a in world.agents if a.alive]
        victims = random.sample(alive, min(2, len(alive)))
        
        for victim in victims:
            victim.needs['happiness'] -= 20
            victim.needs['food'] -= 10
        
        world.log_event(f"🌋 {name}! {desc}")
        world.history.record_disaster(name, desc)
        
        return {'disaster': name}


# Event registry - more events, lower chances
EVENTS = [
    Raiders,
    Wanderer,
    Discovery,
    Plague,
    GoodHarvest,
    TradeCaravan,
    Attack,
    HeroicDeath,
    Disaster,
]


def trigger_random_event(world):
    """Trigger a random event"""
    for event in EVENTS:
        result = event.trigger(world)
        if result:
            return result
    return None
