"""
Legends System - Track famous historical figures
"""

import random

class Legend:
    """A legendary historical figure"""
    
    def __init__(self, agent):
        self.name = agent.biography.name
        self.birth_year = 0
        self.death_year = 0
        self.profession = agent.job
        self.deeds = []
        self.notoriety = 0  # How famous
        self.alignment = 'neutral'  # good, evil, neutral
        
        # Transfer achievements
        for achievement in agent.biography.achievements:
            self.add_deed(achievement)
        
        self.notoriety = agent.biography.kills * 10
        self.notoriety += agent.biography.buildings_built * 5
        self.notoriety += agent.biography.resources_gathered
        
        # Determine alignment based on actions
        if agent.biography.kills > 5:
            self.alignment = 'warrior'
        elif agent.biography.buildings_built > 5:
            self.alignment = 'builder'
        elif agent.biography.achievements:
            self.alignment = 'explorer'
    
    def add_deed(self, deed):
        self.deeds.append(deed)
    
    def get_title(self):
        """Get legendary title"""
        if self.notoriety > 100:
            return "the Legendary"
        elif self.notoriety > 50:
            return "the Famous"
        elif self.notoriety > 25:
            return "the Noted"
        else:
            return "the Remembered"
    
    def to_dict(self):
        return {
            'name': self.name,
            'title': self.get_title(),
            'profession': self.profession,
            'deeds': self.deeds,
            'notoriety': self.notoriety,
            'alignment': self.alignment,
            'birth_year': self.birth_year,
            'death_year': self.death_year
        }


class LegendaryEvent:
    """A famous historical event"""
    
    def __init__(self, event_type, name, description, year, significance=5):
        self.event_type = event_type  # 'battle', 'disaster', 'founding', 'discovery'
        self.name = name
        self.description = description
        self.year = year
        self.significance = significance  # 1-10
        self.participants = []
    
    def add_participant(self, legend):
        self.participants.append(legend.name)
    
    def to_dict(self):
        return {
            'type': self.event_type,
            'name': self.name,
            'description': self.description,
            'year': self.year,
            'significance': self.significance,
            'participants': self.participants
        }


class LegendsManager:
    """Manage all legends and legendary events"""
    
    def __init__(self):
        self.legends = []
        self.events = []
        self.legendary_threshold = 30  # Notoriety needed to be legendary
    
    def check_agent(self, agent, world_year):
        """Check if agent should become a legend"""
        if not hasattr(agent, 'biography'):
            return
        
        # Calculate notoriety
        notoriety = agent.biography.kills * 10
        notoriety += agent.biography.buildings_built * 5
        notoriety += agent.biography.resources_gathered
        
        if notoriety >= self.legendary_threshold:
            legend = Legend(agent)
            legend.birth_year = world_year - agent.age
            legend.death_year = world_year
            self.add_legend(legend)
            return legend
        
        return None
    
    def add_legend(self, legend):
        self.legends.append(legend)
        # Keep only top 50 legends
        if len(self.legends) > 50:
            self.legends = sorted(self.legends, key=lambda l: l.notoriety, reverse=True)[:50]
    
    def add_event(self, event):
        self.events.append(event)
        # Keep only top 100 events
        if len(self.events) > 100:
            self.events = sorted(self.events, key=lambda e: e.significance, reverse=True)[:100]
    
    def create_battle_legend(self, winner, loser, world_year):
        """Create a legendary battle event"""
        event = LegendaryEvent(
            'battle',
            f"Battle of {loser.biography.name}",
            f"{winner.biography.name} defeated {loser.biography.name}",
            world_year,
            significance=min(10, winner.biography.kills + 5)
        )
        event.add_participant(winner)
        event.add_participant(loser)
        self.add_event(event)
        return event
    
    def get_top_legends(self, count=5):
        """Get most famous legends"""
        return sorted(self.legends, key=lambda l: l.notoriety, reverse=True)[:count]
    
    def get_recent_events(self, count=10):
        """Get recent legendary events"""
        return sorted(self.events, key=lambda e: e.year, reverse=True)[:count]
    
    def to_dict(self):
        return {
            'legends': [l.to_dict() for l in self.get_top_legends()],
            'events': [e.to_dict() for e in self.get_recent_events()],
            'total_legends': len(self.legends),
            'total_events': len(self.events)
        }
