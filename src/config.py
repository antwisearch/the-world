"""
Configuration for The World simulation
"""

# World settings
WORLD_WIDTH = 1200
WORLD_HEIGHT = 800
INITIAL_AGENTS = 10

# Simulation
TICK_RATE = 60  # Ticks per second
EVENT_CHANCE = 0.001  # Base event chance per tick

# Needs
MAX_NEED = 100
HUNGER_RATE = 0.05
THIRST_RATE = 0.07
SHELTER_BONUS = 10
HAPPINESS_DECAY = 0.02

# Jobs
JOBS = ['gatherer', 'builder', 'hunter', 'farmer', 'trader', 'guard']

# Resources
RESOURCE_TYPES = ['food', 'wood', 'stone', 'ore']
SPAWN_RATES = {
    'food': 0.02,
    'wood': 0.015,
    'stone': 0.01,
    'ore': 0.005
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
