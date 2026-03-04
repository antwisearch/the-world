"""
More interesting events for emergent stories
"""

import random


class RomanceEvent:
    """Agents fall in love"""
    name = "romance"
    
    @classmethod
    def apply(cls, world):
        alive = [a for a in world.agents if a.alive and hasattr(a, 'biography')]
        if len(alive) >= 2:
            a1, a2 = random.sample(alive, 2)
            
            # Check if they can be together
            if a1.job != a2.job or random.random() < 0.3:
                # Add relationship
                if hasattr(world, 'relationships'):
                    rel = world.relationships.add_relationship(a1, a2, 'family')
                    world.log_event(f"💕 {a1.biography.name} and {a2.biography.name} have become close!")
                    
                    # Chance of baby
                    if random.random() < 0.2:
                        cls._try_baby(world, a1, a2)
    
    @classmethod
    def _try_baby(cls, world, parent1, parent2):
        """Try to have a baby"""
        if parent1.needs['happiness'] > 60 and parent2.needs['happiness'] > 60:
            if parent1.inventory.get('food', 0) > 10 and parent2.inventory.get('food', 0) > 10:
                baby_x = (parent1.x + parent2.x) / 2
                baby_y = (parent1.y + parent2.y) / 2
                
                from src.agent import Agent
                baby = Agent(baby_x, baby_y, parent1.genome)
                baby.generation = max(parent1.generation, parent2.generation) + 1
                
                # Family
                baby.biography.parents = [parent1.biography.name, parent2.biography.name]
                parent1.biography.children.append(baby.biography.name)
                parent2.biography.children.append(baby.biography.name)
                
                # Take food
                parent1.inventory['food'] -= 10
                parent2.inventory['food'] -= 10
                
                world.add_agent(baby)
                world.log_event(f"👶 {baby.biography.name} was born to {parent1.biography.name} and {parent2.biography.name}!")


class FeudEvent:
    """Agents start a feud"""
    name = "feud"
    
    @classmethod
    def apply(cls, world):
        alive = [a for a in world.agents if a.alive and hasattr(a, 'biography')]
        
        if len(alive) >= 2:
            a1, a2 = random.sample(alive, 2)
            
            # Create enemy relationship
            if hasattr(world, 'relationships'):
                rel = world.relationships.add_relationship(a1, a2, 'enemy')
                
                reasons = [
                    f"disputed over resources",
                    f"had a disagreement",
                    f"competed for the same job",
                    f"accused each other of theft",
                ]
                reason = random.choice(reasons)
                
                world.log_event(f"😠 {a1.biography.name} and {a2.biography.name} are now feuding - {reason}!")


class AllianceEvent:
    """Agents become allies"""
    name = "alliance"
    
    @classmethod
    def apply(cls, world):
        alive = [a for a in world.agents if a.alive and hasattr(a, 'biography')]
        
        if len(alive) >= 3:
            # Pick 3 agents to form alliance
            agents = random.sample(alive, min(3, len(alive)))
            names = [a.biography.name for a in agents]
            
            world.log_event(f"🤝 {' and '.join(names[:-1])} and {names[-1]} have formed an alliance!")
            
            # Boost their happiness
            for a in agents:
                a.needs['happiness'] = min(100, a.needs['happiness'] + 15)


class DiscoveryEvent:
    """Major discovery"""
    name = "major_discovery"
    
    DISCOVERIES = [
        ("discovered ancient ruins", "ruins", 50),
        ("found a gold deposit", "gold", 100),
        ("discovered a sacred spring", "spring", 30),
        ("found ancient texts", "texts", 40),
    ]
    
    @classmethod
    def apply(cls, world):
        discoverers = [a for a in world.agents if a.alive and a.job in ['gatherer', 'hunter']]
        
        if not discoverers:
            discoverers = [a for a in world.agents if a.alive]
        
        if discoverers:
            discoverer = random.choice(discoverers)
            disc, restype, value = random.choice(cls.DISCOVERIES)
            
            # Add resources
            for _ in range(5):
                world.resources.append({
                    'type': restype if restype != 'ruins' else 'treasure',
                    'x': discoverer.x + random.uniform(-20, 20),
                    'y': discoverer.y + random.uniform(-20, 20),
                    'amount': value
                })
            
            discoverer.biography.achievements.append(disc)
            world.log_event(f"🔱 {discoverer.biography.name} {disc}! A great discovery!")


class FestivalEvent:
    """Hold a festival"""
    name = "festival"
    
    @classmethod
    def apply(cls, world):
        alive = [a for a in world.agents if a.alive]
        
        if len(alive) >= 5:
            # Boost everyone's happiness
            for a in alive:
                a.needs['happiness'] = min(100, a.needs['happiness'] + 20)
                a.needs['food'] = min(100, a.needs['food'] + 10)
            
            world.log_event(f"🎉 The colony holds a grand festival! Everyone celebrates!")


class MigrationEvent:
    """Mass migration"""
    name = "migration"
    
    @classmethod
    def apply(cls, world):
        # New group arrives
        num_new = random.randint(2, 5)
        
        from src.agent import Agent
        for _ in range(num_new):
            new_agent = Agent(
                random.uniform(50, world.width - 50),
                random.uniform(50, world.height - 50)
            )
            new_agent.needs['food'] = 30
            world.add_agent(new_agent)
        
        world.log_event(f"🏕️ A group of {num_new} new settlers has joined the colony!")


# More dramatic events

class GreatBattle:
    """Epic battle"""
    name = "great_battle"
    
    @classmethod
    def apply(cls, world):
        guards = [a for a in world.agents if a.alive and a.job == 'guard']
        raiders = getattr(world, 'raiders', [])
        
        if guards and raiders:
            guard = random.choice(guards)
            raider = random.choice(raiders)
            
            # Combat
            guard_skill = guard.skills.get('combat', 10)
            raider_skill = raider.skills.get('combat', 10)
            
            if guard_skill > raider_skill:
                raider.alive = False
                guard.biography.kills += 1
                guard.biography.achievements.append(f"defeated raider")
                world.log_event(f"⚔️ {guard.biography.name} defeated a raider in epic combat!")
            else:
                guard.alive = False
                raider.biography.kills += 1
                world.log_event(f"💀 A raider defeated {guard.biography.name} in battle!")


class Epidemic:
    """Disease spreads"""
    name = "epidemic"
    
    @classmethod
    def apply(cls, world):
        alive = [a for a in world.agents if a.alive]
        
        if len(alive) >= 3:
            # Multiple agents affected
            victims = random.sample(alive, min(3, len(alive)))
            
            for v in victims:
                v.needs['happiness'] -= 40
                v.needs['food'] -= 30
            
            world.log_event(f"🤧 A disease spreads through the colony! {len(victims)} agents are affected!")


# Export
EVENTS = [
    RomanceEvent,
    FeudEvent,
    AllianceEvent,
    DiscoveryEvent,
    FestivalEvent,
    MigrationEvent,
    GreatBattle,
    Epidemic,
]
