"""
The World - Dwarf Fortress Style Colony Simulation

A procedural colony sim where AI agents live, work, and create emergent stories.
"""

__version__ = "0.2.0"

# Core
from src.world import World
from src.agent import Agent
from src.civilization import Civilization

# AI
from src.utility_ai import BehaviorTree, UtilityScore
from src.goap import GOAPAgent, plan_for_goal

# Generation
from src.terrain import TerrainGenerator, Biome
from src.biomes import BiomeResourceManager
from src.pathfinding import Pathfinder

# Systems
from src.history import WorldHistory
from src.legends import LegendsManager
from src.relationships import RelationshipManager
from src.artifacts import ArtifactManager
from src.economy import Economy

__all__ = [
    'World', 'Agent', 'Civilization',
    'BehaviorTree', 'UtilityScore',
    'GOAPAgent', 'plan_for_goal',
    'TerrainGenerator', 'Biome', 'BiomeResourceManager', 'Pathfinder',
    'WorldHistory', 'LegendsManager', 'RelationshipManager', 'ArtifactManager',
    'Economy'
]
