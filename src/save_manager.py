"""
Save/Load system for The World
"""

import json
import os

class SaveManager:
    """Save and load game state"""
    
    SAVE_DIR = "saves"
    
    @classmethod
    def ensure_save_dir(cls):
        if not os.path.exists(cls.SAVE_DIR):
            os.makedirs(cls.SAVE_DIR)
    
    @classmethod
    def save_game(cls, world, filename="savegame"):
        """Save game state to file"""
        cls.ensure_save_dir()
        
        # Save agents
        agents_data = []
        for agent in world.agents:
            agents_data.append({
                'x': agent.x,
                'y': agent.y,
                'job': agent.job,
                'needs': agent.needs,
                'skills': agent.skills,
                'inventory': agent.inventory,
                'generation': agent.generation,
                'alive': agent.alive,
                'age': agent.age,
                'fitness': agent.fitness,
                'biography': agent.biography.to_dict() if hasattr(agent, 'biography') else {}
            })
        
        # Save resources (simplified)
        resources_data = world.resources[:50]  # Limit
        
        # Save buildings
        buildings_data = []
        for b in world.buildings:
            buildings_data.append({
                'type': getattr(b, 'building_type', 'unknown'),
                'x': getattr(b, 'x', 0),
                'y': getattr(b, 'y', 0),
            })
        
        save_data = {
            'version': '1.0',
            'world': {
                'width': world.width,
                'height': world.height,
                'era': world.era,
                'year': world.history.year,
            },
            'agents': agents_data,
            'resources': resources_data,
            'buildings': buildings_data,
            'events': world.events[-20:],
            'stats': {
                'population': len(agents_data),
                'total_born': world.history.total_born,
                'total_died': world.history.total_died,
            }
        }
        
        filepath = f"{cls.SAVE_DIR}/{filename}.json"
        with open(filepath, 'w') as f:
            json.dump(save_data, f, indent=2)
        
        return filepath
    
    @classmethod
    def load_game(cls, filename="savegame"):
        """Load game state from file"""
        filepath = f"{cls.SAVE_DIR}/{filename}.json"
        
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r') as f:
            save_data = json.load(f)
        
        return save_data
    
    @classmethod
    def list_saves(cls):
        """List all saved games"""
        cls.ensure_save_dir()
        saves = []
        for f in os.listdir(cls.SAVE_DIR):
            if f.endswith('.json'):
                saves.append(f[:-5])
        return saves
