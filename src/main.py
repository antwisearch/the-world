"""
Biological Chaos - Soft-body evolution simulation
Entry point
"""

from src.environment import Environment
from src.renderer import Renderer
from src.evolution import EvolutionEngine
import pygame
import sys


def main():
    # Initialize pygame
    pygame.init()
    
    # Create environment
    env = Environment(width=1200, height=800)
    
    # Create renderer
    renderer = Renderer(env)
    
    # Create evolution engine
    evolution = EvolutionEngine(env)
    
    # Initial population
    evolution.spawn_initial_population(20)
    
    # Main loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    evolution.spawn_initial_population(20)
                elif event.key == pygame.K_r:
                    # Reset simulation
                    env.reset()
                    evolution.spawn_initial_population(20)
        
        # Update physics
        env.step()
        
        # Update evolution (check for generation end)
        evolution.update()
        
        # Render
        renderer.render()
        
        # Cap at 60 FPS
        clock.tick(60)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
