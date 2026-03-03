"""
Biological Chaos - Soft-body evolution simulation for AI agents
Entry point - no human controls
"""

from src.environment import Environment
from src.renderer import Renderer
from src.evolution import EvolutionEngine
import pygame
import sys
import json
import time


class AgentServer:
    """
    API server for AI agents to interact with the simulation
    Agents can observe environment and send actions
    """
    
    def __init__(self, port=8080):
        self.port = port
        self.env = None
        self.evolution = None
        self.running = False
        
        # Agent registry
        self.agents = {}  # agent_id -> creature
    
    def start(self, port=8080):
        """Start the simulation server"""
        pygame.init()
        
        # Create environment
        self.env = Environment(width=1200, height=800)
        
        # Create evolution engine (auto-runs)
        self.evolution = EvolutionEngine(self.env)
        
        # Initial population
        self.evolution.spawn_initial_population(20)
        
        self.running = True
        self.port = port
        
        print(f"🌱 Biological Chaos Server started on port {port}")
        print(f"📡 API endpoint: http://localhost:{port}")
        print(f"🔗 WebSocket: ws://localhost:{port}/ws")
        print("\n📋 Endpoints:")
        print(f"  GET  /status          - Get simulation status")
        print(f"  GET  /state           - Get full environment state")
        print(f"  POST /agent/register  - Register new agent")
        print(f"  POST /agent/<id>/act - Send action to agent's creature")
        print(f"  GET  /agent/<id>/see  - Get what agent sees")
        print("\n🧬 Evolution runs automatically every 30 seconds")
        
        # Start main loop (headless or with renderer)
        self.run()
    
    def get_state(self):
        """Get current environment state for agents"""
        state = {
            'generation': self.evolution.generation,
            'time_in_generation': self.evolution.time_in_generation,
            'population': len(self.env.creatures),
            'alive': sum(1 for c in self.env.creatures if c.alive),
            'food': len(self.env.food),
            'best_fitness': self.evolution.best_creature.fitness if self.evolution.best_creature else 0,
            'creatures': []
        }
        
        for creature in self.env.creatures:
            creature_data = {
                'id': id(creature),
                'alive': creature.alive,
                'age': creature.age,
                'fitness': creature.fitness,
                'food_eaten': creature.food_eaten,
                'genome': creature.genome,
                'center': {
                    'x': creature.get_center().x,
                    'y': creature.get_center().y
                },
                'radius': creature.get_radius(),
                'nodes': [
                    {'x': n.position.x, 'y': n.position.y, 'health': n.health}
                    for n in creature.nodes
                ]
            }
            state['creatures'].append(creature_data)
        
        return state
    
    def register_agent(self, agent_id):
        """Register a new agent, assign a creature"""
        if agent_id in self.agents:
            return {'error': 'Agent already registered'}
        
        # Find unassigned alive creature
        available = [c for c in self.env.creatures if c.alive and c not in self.agents.values()]
        
        if not available:
            return {'error': 'No available creatures'}
        
        creature = available[0]
        self.agents[agent_id] = creature
        
        return {
            'success': True,
            'agent_id': agent_id,
            'creature_id': id(creature),
            'genome': creature.genome
        }
    
    def agent_see(self, agent_id):
        """Get what an agent perceives"""
        if agent_id not in self.agents:
            return {'error': 'Agent not registered'}
        
        creature = self.agents[agent_id]
        if not creature.alive:
            return {'error': 'Creature dead'}
        
        center = creature.get_center()
        perception_radius = 30
        
        # Find nearby food
        nearby_food = []
        for food in self.env.food:
            dist = center.Distance(food.position)
            if dist < perception_radius:
                nearby_food.append({
                    'x': food.position.x,
                    'y': food.position.y,
                    'distance': dist,
                    'nutrition': food.nutrition
                })
        
        # Find nearby threats
        nearby_threats = []
        for other in self.env.creatures:
            if other == creature or not other.alive:
                continue
            dist = center.Distance(other.get_center())
            if dist < perception_radius * 2:
                nearby_threats.append({
                    'x': other.get_center().x,
                    'y': other.get_center().y,
                    'distance': dist,
                    'size': other.get_radius()
                })
        
        # Get body state
        body_state = {
            'health': creature.nodes[0].health,
            'age': creature.age,
            'fitness': creature.fitness,
            'energy': sum(n.health for n in creature.nodes) / len(creature.nodes)
        }
        
        return {
            'creature_id': id(creature),
            'position': {'x': center.x, 'y': center.y},
            'perception_radius': perception_radius,
            'nearby_food': nearby_food,
            'nearby_threats': nearby_threats,
            'body_state': body_state,
            'genome': creature.genome
        }
    
    def agent_act(self, agent_id, action):
        """
        Apply agent's action to their creature
        Action: {'thrust': (x, y), 'contract': float 0-1}
        """
        if agent_id not in self.agents:
            return {'error': 'Agent not registered'}
        
        creature = self.agents[agent_id]
        if not creature.alive:
            return {'error': 'Creature dead'}
        
        thrust = action.get('thrust', (0, 0))
        contract = action.get('contract', 0.0)
        
        creature.apply_input(thrust, contract)
        
        return {'success': True}
    
    def run(self):
        """Main simulation loop"""
        clock = pygame.time.Clock()
        
        while self.running:
            # Update physics
            self.env.step()
            
            # Update evolution
            self.evolution.update()
            
            # Render (optional - can disable for headless)
            # renderer.render()
            
            # Cap at 60 FPS
            clock.tick(60)
            
            # Check for quit
            # (in server mode, no pygame window, so no events)
    
    def stop(self):
        """Stop the server"""
        self.running = False
        pygame.quit()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Biological Chaos - AI Evolution Simulator')
    parser.add_argument('--port', type=int, default=8080, help='Server port')
    parser.add_argument('--headless', action='store_true', help='Run without renderer')
    parser.add_argument('--population', type=int, default=20, help='Initial population size')
    parser.add_argument('--generation-time', type=float, default=30, help='Seconds per generation')
    
    args = parser.parse_args()
    
    # Create server
    server = AgentServer(args.port)
    
    # Configure
    if args.headless:
        # Disable pygame display
        import os
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
    
    # Start
    server.start(args.port)


if __name__ == "__main__":
    main()
