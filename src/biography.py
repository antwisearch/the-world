"""
Biography - Agent life stories, death records, family
"""

import random
from src.names import generate_full_name

class Biography:
    """Agent biography - life story"""
    
    def __init__(self, birthplace_x, birthplace_y, generation=1):
        self.name = generate_full_name()
        self.birth_time = 0
        self.birthplace = {'x': birthplace_x, 'y': birthplace_y}
        self.death_time = None
        self.death_cause = None
        self.death_location = None
        self.generation = generation
        
        # Life events (stored as they happen)
        self.life_events = []
        
        # Family
        self.parents = []
        self.children = []
        self.spouse = None
        
        # Relationships (other agents)
        self.friends = []
        self.enemies = []
        
        # What they're known for
        self.achievements = []
        self.kills = 0
        self.buildings_built = 0
        self.resources_gathered = 0
        
        # Personality (for stories)
        self.personality_traits = random.sample([
            "brave", "cowardly", "greedy", "generous", 
            "angry", "calm", "curious", "lazy", 
            "ambitious", "content", "hardworking", "messy"
        ], 3)
    
    def add_event(self, event_type, description):
        """Add a life event"""
        self.life_events.append({
            'time': self.birth_time,  # Will be set by agent age
            'type': event_type,
            'description': description
        })
    
    def record_death(self, age, cause, location):
        """Record death with cause"""
        self.death_time = age
        self.death_cause = cause
        self.death_location = location
    
    def get_occupation(self):
        """Get famous occupation"""
        if self.kills > 5:
            return "warrior"
        elif self.buildings_built > 10:
            return "master builder"
        elif self.resources_gathered > 100:
            return "legendary gatherer"
        elif self.achievements:
            return self.achievements[0]
        return "worker"
    
    def generate_obituary(self):
        """Generate Dwarf Fortress style obituary"""
        if not self.death_time:
            return None
        
        cause_desc = {
            'starvation': "died of starvation",
            'dehydration': "died of dehydration", 
            'violence': "was killed in combat",
            'age': "died of old age",
            'unknown': "passed away"
        }
        
        cause = cause_desc.get(self.death_cause, self.death_cause or "died")
        
        # Famous for
        famous = ""
        if self.achievements:
            famous = f" Known for: {', '.join(self.achievements[:2])}."
        
        return (f"💀 {self.name} {cause} at age {self.death_time:.1f}. "
                f"{self.get_occupation()}.{famous}")
    
    def to_dict(self):
        return {
            'name': self.name,
            'birth_time': self.birth_time,
            'birthplace': self.birthplace,
            'death_time': self.death_time,
            'death_cause': self.death_cause,
            'generation': self.generation,
            'personality': self.personality_traits,
            'achievements': self.achievements,
            'kills': self.kills,
            'life_events': self.life_events
        }


class DeathRecord:
    """Record of a death - for world history"""
    
    def __init__(self, agent, cause, location, time):
        self.agent_name = agent.biography.name if hasattr(agent, 'biography') else "Unknown"
        self.cause = cause
        self.location = location
        self.time = time
        self.generation = agent.generation
        self.job = agent.job
    
    def to_dict(self):
        return {
            'name': self.agent_name,
            'cause': self.cause,
            'location': self.location,
            'time': self.time,
            'generation': self.generation,
            'job': self.job
        }
