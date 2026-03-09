"""
Configuration for The World simulation
"""

# World settings
WORLD_WIDTH = 1200
WORLD_HEIGHT = 800
INITIAL_AGENTS = 10

# Simulation
TICK_RATE = 60  # Ticks per second
EVENT_CHANCE = 0.0005  # Base event chance per tick (reduced from 0.001)

# Needs
MAX_NEED = 100
HUNGER_RATE = 0.04  # Slightly reduced (was 0.05)
THIRST_RATE = 0.06  # Slightly reduced (was 0.07)
SHELTER_BONUS = 15  # Increased (was 10)
HAPPINESS_DECAY = 0.015  # Reduced (was 0.02)

# Jobs
JOBS = ['gatherer', 'builder', 'hunter', 'farmer', 'trader', 'guard', 
        'woodcutter', 'miner', 'fisher', 'teacher', 'healer', 'researcher', 'diplomat']

# Resources
RESOURCE_TYPES = ['food', 'wood', 'stone', 'ore', 'herbs']
SPAWN_RATES = {
    'food': 0.025,  # Increased (was 0.02)
    'wood': 0.02,   # Increased (was 0.015)
    'stone': 0.012,  # Increased (was 0.01)
    'ore': 0.006,   # Increased (was 0.005)
    'herbs': 0.01,  # New - for healers
}

# Buildings
BUILDING_TYPES = ['shelter', 'farm', 'workshop']
BUILDING_COSTS = {
    'shelter': {'wood': 5},
    'farm': {'wood': 10},
    'workshop': {'wood': 15, 'stone': 5}
}

# Events
EVENT_TYPES = [
    'raiders', 'wanderer', 'discovery', 
    'plague', 'good_harvest', 'trade_caravan', 
    'attack', 'heroic_death', 'disaster'
]

# Biomes
BIOMES = ['grassland', 'forest', 'desert', 'tundra', 'snow', 'jungle', 'swamp', 'savanna']

# Server
HOST = "0.0.0.0"
PORT = 8080
