"""
Seasonal events - events that happen during specific seasons
"""

import random

class SeasonalEvent:
    """An event tied to a season"""
    
    def __init__(self, name, season, chance, action):
        self.name = name
        self.season = season  # spring, summer, autumn, winter
        self.chance = chance  # 0-1
        self.action = action
    
    def try_trigger(self, world):
        """Try to trigger this event"""
        if world.seasons.season != self.season:
            return False
        
        if random.random() < self.chance:
            self.action(world)
            return True
        return False


class SeasonalEventManager:
    """Manage seasonal events"""
    
    def __init__(self):
        self.events = []
        self._setup_events()
    
    def _setup_events(self):
        """Set up all seasonal events"""
        
        # Spring events
        self.events.append(SeasonalEvent(
            "spring_bloom",
            "spring",
            0.02,
            lambda w: w.log_event("🌸 Spring bloom! Food is plentiful.")
        ))
        
        self.events.append(SeasonalEvent(
            "migration",
            "spring",
            0.01,
            lambda w: self._add_migration(w)
        ))
        
        # Summer events
        self.events.append(SeasonalEvent(
            "heat_wave",
            "summer",
            0.02,
            lambda w: w.log_event("☀️ A heat wave strikes! Water is scarce.")
        ))
        
        # Autumn events
        self.events.append(SeasonalEvent(
            "harvest_festival",
            "autumn",
            0.03,
            lambda w: self._harvest_festival(w)
        ))
        
        # Winter events
        self.events.append(SeasonalEvent(
            "hard_frost",
            "winter",
            0.03,
            lambda w: w.log_event("❄️ A hard frost strikes! Resources are scarce.")
        ))
        
        self.events.append(SeasonalEvent(
            "winter_starvation",
            "winter",
            0.02,
            lambda w: w.log_event("🐺 Winter is harsh. Starvation looms.")
        ))
    
    def _add_migration(self, world):
        """Add migration event"""
        from src.agent import Agent
        num = random.randint(2, 4)
        for _ in range(num):
            agent = Agent(
                random.uniform(50, world.width-50),
                random.uniform(50, world.height-50)
            )
            world.add_agent(agent)
        world.log_event(f"🚶 A group of {num} wanderers arrives in spring!")
    
    def _harvest_festival(self, world):
        """Harvest festival - boost happiness"""
        for agent in world.agents:
            if agent.alive:
                agent.needs['happiness'] = min(100, agent.needs['happiness'] + 20)
        world.log_event("🎉 The harvest festival is a great success!")
    
    def tick(self, world):
        """Process seasonal events"""
        for event in self.events:
            event.try_trigger(world)
    
    def to_dict(self):
        return {'events': len(self.events)}
