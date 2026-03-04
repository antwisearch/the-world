"""
Artifacts - Items dropped by dead agents, found objects
"""

import random

class Artifact:
    """An artifact - item with history"""
    
    def __init__(self, name, item_type, description, value=1):
        self.name = name
        self.item_type = item_type  # 'weapon', 'tool', 'journal', 'treasure'
        self.description = description
        self.value = value
        self.found = False
        self.found_by = None
        self.found_year = None
        self.original_owner = None
    
    def to_dict(self):
        return {
            'name': self.name,
            'type': self.item_type,
            'description': self.description,
            'value': self.value,
            'found': self.found,
            'found_by': self.found_by,
            'original_owner': self.original_owner
        }


# Item templates
WEAPONS = [
    ("Rusty Sword", "A weathered sword", 5),
    ("Battle Axe", "A worn battle axe", 8),
    ("Hunter's Bow", "A hunter's bow", 6),
    ("Iron Spear", "A iron-tipped spear", 7),
]

TOOLS = [
    ("Pickaxe", "A miner's pickaxe", 3),
    ("Hammer", "A builder's hammer", 2),
    ("Farming Tool", "A rusty farm tool", 2),
    ("Cooking Pot", "A dented pot", 1),
]

JOURNALS = [
    ("Journal: Day 1", "A weathered journal", 10),
    ("Map of Surroundings", "A hand-drawn map", 15),
    ("Recipe Book", "A collection of recipes", 12),
    ("Letter to Family", "An unsent letter", 8),
    ("Research Notes", "Scribbled notes", 10),
]

TREASURES = [
    ("Gold Ring", "A simple gold ring", 20),
    ("Gemstone", "A polished gem", 25),
    ("Silver Coin", "An ancient coin", 15),
    ("Family Heirloom", "A treasured keepsake", 30),
]


class ArtifactGenerator:
    """Generate artifacts from dead agents"""
    
    @staticmethod
    def generate_from_agent(agent):
        """Generate artifacts from a dead agent"""
        artifacts = []
        
        if not hasattr(agent, 'biography'):
            return artifacts
        
        # Chance to drop items based on job
        if random.random() < 0.3:  # 30% chance
            if agent.job == 'hunter':
                name, desc, val = random.choice(WEAPONS[:2])
            elif agent.job == 'builder':
                name, desc, val = random.choice(TOOLS[:2])
            else:
                name, desc, val = random.choice(TOOLS)
            
            artifact = Artifact(
                name=name,
                item_type='tool',
                description=desc,
                value=val
            )
            artifact.original_owner = agent.biography.name
            artifacts.append(artifact)
        
        # Chance for journal/diary (especially notable agents)
        if (random.random() < 0.2 or 
            agent.biography.achievements or 
            agent.biography.kills > 3):
            
            name, desc, val = random.choice(JOURNALS)
            artifact = Artifact(
                name=name,
                item_type='journal',
                description=desc,
                value=val
            )
            artifact.original_owner = agent.biography.name
            artifacts.append(artifact)
        
        # Rare treasure chance
        if random.random() < 0.05:  # 5% chance
            name, desc, val = random.choice(TREASURES)
            artifact = Artifact(
                name=name,
                item_type='treasure',
                description=desc,
                value=val
            )
            artifact.original_owner = agent.biography.name
            artifacts.append(artifact)
        
        return artifacts
    
    @staticmethod
    def generate_found_item(world):
        """Generate a found item (discovery event)"""
        if random.random() < 0.3:
            name, desc, val = random.choice(TREASURES)
            artifact = Artifact(
                name=name,
                item_type='treasure',
                description=desc,
                value=val
            )
            artifact.found = True
            return artifact
        return None


class ArtifactManager:
    """Manage all artifacts"""
    
    def __init__(self):
        self.artifacts = []
        self.found_artifacts = []
    
    def add_artifact(self, artifact):
        """Add an artifact"""
        self.artifacts.append(artifact)
    
    def add_found(self, artifact):
        """Add a found artifact"""
        artifact.found = True
        self.found_artifacts.append(artifact)
    
    def get_all(self):
        """Get all artifacts"""
        return [a.to_dict() for a in self.artifacts]
    
    def get_found(self):
        """Get found artifacts"""
        return [a.to_dict() for a in self.found_artifacts]
    
    def to_dict(self):
        return {
            'total': len(self.artifacts),
            'found': len(self.found_artifacts),
            'items': self.get_found()[:10]
        }
