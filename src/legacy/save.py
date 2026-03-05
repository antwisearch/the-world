"""
Save/Load simulation state
"""

import json
import os


def save_state(world, evolution, filepath="save.json"):
    """Save complete simulation state"""
    state = {
        'world': world.to_dict(),
        'evolution': {
            'generation': evolution.generation,
            'time_in_generation': evolution.time_in_generation,
            'best_creature': None,
            'generation_stats': evolution.generation_stats
        },
        'creatures': []
    }
    
    # Save each creature's genome and stats
    for c in evolution.creatures:
        creature_data = {
            'genome': c.genome,
            'age': c.age,
            'fitness': c.fitness,
            'food_eaten': c.food_eaten,
            'generation': c.generation,
            'alive': c.alive
        }
        state['creatures'].append(creature_data)
    
    # Save best creature genome
    if evolution.best_creature:
        state['evolution']['best_creature'] = evolution.best_creature.genome
    
    with open(filepath, 'w') as f:
        json.dump(state, f, indent=2)
    
    return filepath


def load_state(filepath="save.json"):
    """Load simulation state"""
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r') as f:
        state = json.load(f)
    
    return state
