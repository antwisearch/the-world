"""
Biological Chaos - Evolution Simulator

Soft-body creatures that evolve through natural selection.
"""

__version__ = "0.1.0"

from src.creature import Creature, Node, Spring
from src.environment import Environment, Food
from src.evolution import EvolutionEngine
from src.brain import Brain
from src.renderer import Renderer

__all__ = [
    'Creature',
    'Node', 
    'Spring',
    'Environment',
    'Food',
    'EvolutionEngine',
    'Brain',
    'Renderer',
]
