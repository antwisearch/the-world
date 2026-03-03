"""
The World - Co-evolution simulator for AI agents
Entry point
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="The World - AI Agent Evolution Simulator")
    parser.add_argument('--port', type=int, default=8080, help='API server port')
    parser.add_argument('--population', type=int, default=20, help='Initial population')
    parser.add_argument('--generation-time', type=float, default=30, help='Seconds per generation')
    parser.add_argument('--headless', action='store_true', help='Run without API (just sim)')
    
    args = parser.parse_args()
    
    if args.headless:
        # Just run simulation without API
        from src.world import World
        from src.evolution import EvolutionEngine
        from src.environment import World as PhysWorld
        import time
        
        print("[*] Initializing The World...")
        world = World()
        phys_world = PhysWorld(world.width, world.height)
        evolution = EvolutionEngine(world, args.population, args.generation_time)
        evolution.phys_world = phys_world
        evolution.spawn_initial_population()
        
        print(f"Population: {args.population}")
        print(f"Generation time: {args.generation_time}s")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                # Need dummy agent list for now
                world.update([], 1/60)
                
                # Check collisions (eating food, creature-creature)
                # Re-syncing food with physics world food
                world.food = [{'x': f.position.x, 'y': f.position.y, 'radius': f.radius, 'nutrition': f.nutrition} 
                              for f in phys_world.food if f.alive]
                
                all_creatures = [c for c in evolution.creatures if c.alive]
                world.check_collisions(all_creatures)
                world.apply_weather_effects(all_creatures)
                world.apply_structure_effects(all_creatures)
                
                phys_world.step(1/60)
                evolution.update(1/60)
                time.sleep(1/60)
        except KeyboardInterrupt:
            print("\n[*] World stopped")
    else:
        # Run API server
        from src.api import run_server
        print(f"[*] Starting API server on port {args.port}")
        run_server(port=args.port)


if __name__ == "__main__":
    main()
