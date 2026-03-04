"""
World History - Timeline of events, legendary figures
"""

import random

class HistoryEntry:
    """A historical event"""
    
    def __init__(self, event_type, title, description, importance=1):
        self.event_type = event_type  # 'founding', 'battle', 'death', 'birth', 'disaster'
        self.title = title
        self.description = description
        self.importance = importance  # 1-10
        self.year = 0
    
    def to_dict(self):
        return {
            'type': self.event_type,
            'title': self.title,
            'description': self.description,
            'importance': self.importance,
            'year': self.year
        }


class LegendaryFigure:
    """A famous historical figure"""
    
    def __init__(self, name, title, description, death_year=None):
        self.name = name
        self.title = title  # "the Great", "the Terrible", etc
        self.description = description
        self.birth_year = 0
        self.death_year = death_year
        self.deed = []
    
    def add_deed(self, deed):
        self.deed.append(deed)
    
    def to_dict(self):
        return {
            'name': self.name,
            'title': self.title,
            'description': self.description,
            'birth_year': self.birth_year,
            'death_year': self.death_year,
            'famous_deeds': self.deed
        }


class WorldHistory:
    """World history timeline"""
    
    def __init__(self):
        self.entries = []
        self.legends = []
        self.founding_year = 0
        self.year = 0
        
        # Statistics
        self.total_born = 0
        self.total_died = 0
        self.famous_battles = 0
        self.disasters = 0
    
    def add_entry(self, event_type, title, description, importance=1):
        """Add a historical entry"""
        entry = HistoryEntry(event_type, title, description, importance)
        entry.year = self.year
        self.entries.append(entry)
        
        # Keep only last 200 entries
        if len(self.entries) > 200:
            self.entries = self.entries[-200:]
        
        return entry
    
    def add_legend(self, name, title, description):
        """Add a legendary figure"""
        legend = LegendaryFigure(name, title, description)
        legend.birth_year = self.year
        self.legends.append(legend)
        return legend
    
    def record_birth(self, agent_name):
        """Record a birth"""
        self.total_born += 1
        if self.total_born == 1:
            self.add_entry('founding', 'The Beginning', 
                          f"{agent_name} founded the settlement", 10)
            self.founding_year = self.year
    
    def record_death(self, agent_name, cause, is_legendary=False):
        """Record a death"""
        self.total_died += 1
        
        entry = self.add_entry('death', f"Death of {agent_name}",
                              f"{agent_name} died of {cause}", 
                              5 if is_legendary else 2)
        
        return entry
    
    def record_battle(self, winner_name, loser_name, description):
        """Record a battle"""
        self.famous_battles += 1
        self.add_entry('battle', f"Battle: {winner_name} vs {loser_name}",
                      description, 7)
    
    def record_disaster(self, name, description):
        """Record a disaster"""
        self.disasters += 1
        self.add_entry('disaster', name, description, 8)
    
    def advance_year(self):
        """Advance time"""
        self.year += 1
    
    def get_summary(self):
        """Get history summary"""
        return {
            'year': self.year,
            'founded': self.founding_year,
            'total_born': self.total_born,
            'total_died': self.total_died,
            'famous_battles': self.famous_battles,
            'disasters': self.disasters,
            'legends': len(self.legends)
        }
    
    def get_recent(self, count=10):
        """Get recent history"""
        return [e.to_dict() for e in self.entries[-count:]]
    
    def to_dict(self):
        return {
            'summary': self.get_summary(),
            'recent': self.get_recent(10),
            'legends': [l.to_dict() for l in self.legends[-5:]]
        }
