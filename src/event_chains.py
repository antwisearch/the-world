"""
Event Chains - Events that trigger other events
"""

import random

class EventChain:
    """Events that can trigger follow-up events"""
    
    def __init__(self, trigger_event, follow_up_chance=0.3):
        self.trigger_event = trigger_event
        self.follow_up_chance = follow_up_chance
        self.possible_consequences = []
    
    def add_consequence(self, event_class, weight=1):
        """Add a possible follow-up event"""
        self.possible_consequences.append((event_class, weight))
    
    def trigger(self, world, original_event):
        """Trigger follow-up event"""
        if random.random() > self.follow_up_chance:
            return None
        
        # Weighted random choice
        if not self.possible_consequences:
            return None
        
        weights = [w for _, w in self.possible_consequences]
        total = sum(weights)
        r = random.random() * total
        
        cumulative = 0
        for event_class, weight in self.possible_consequences:
            cumulative += weight
            if r <= cumulative:
                return event_class.apply(world)
        
        return None


# Event chain registry
EVENT_CHAINS = {}


def register_chain(trigger_name, chain):
    """Register an event chain"""
    EVENT_CHAINS[trigger_name] = chain


def check_for_chain(world, event_name):
    """Check if an event triggers a chain"""
    if event_name in EVENT_CHAINS:
        return EVENT_CHAINS[event_name].trigger(world, event_name)
    return None


# Setup some event chains

def setup_event_chains():
    """Initialize event chains"""
    
    # Raiders → Fortification
    chain = EventChain('raiders', 0.5)
    chain.add_consequence(RaiderAftermath, 1)
    register_chain('raiders', chain)
    
    # Discovery → Follow-up research
    chain = EventChain('discovery', 0.3)
    chain.add_consequence(ResearchBreakthrough, 1)
    register_chain('discovery', chain)
    
    # Plague → Quarantine
    chain = EventChain('plague', 0.4)
    chain.add_consequence(Recovery, 1)
    register_chain('plague', chain)


# Follow-up event classes

class RaiderAftermath:
    """After raiders, maybe fortify"""
    @classmethod
    def apply(cls, world):
        # Chance to add a simple defense
        if random.random() < 0.3:
            world.log_event("🏰 Defenses were strengthened after the raid!")
        return {'aftermath': 'fortified'}


class ResearchBreakthrough:
    """After discovery, more findings"""
    @classmethod
    def apply(cls, world):
        # Add more resources
        for _ in range(3):
            world.resources.append({
                'type': random.choice(['ore', 'stone']),
                'x': random.uniform(50, world.width-50),
                'y': random.uniform(50, world.height-50),
                'amount': random.randint(5, 20)
            })
        world.log_event("📜 Further research reveals more!")
        return {'breakthrough': True}


class Recovery:
    """After plague, recovery"""
    @classmethod
    def apply(cls, world):
        # Boost happiness slightly
        for agent in world.agents:
            if agent.alive:
                agent.needs['happiness'] = min(100, agent.needs['happiness'] + 10)
        world.log_event("💚 The colony recovers from the plague.")
        return {'recovery': True}


# Import needed classes
from src.events import Raiders, Discovery, Plague
