"""
Evolution engine - handles natural selection and reproduction
"""

import random
from src.creature import Creature


class EvolutionEngine:
    """
    Manages evolution simulation
    """
    
    def __init__(self, environment, generation_time=30, population_size=20):
        self.env = environment
        self.generation_time = generation_time  # seconds per generation
        self.population_size = population_size
        self.generation = 1
        self.time_in_generation = 0
        self.best_creature = None
        self.generation_stats = []
    
    def spawn_initial_population(self, count=None):
        """Spawn initial random population"""
        count = count or self.population_size
        
        for _ in range(count):
            x = random.uniform(100, self.env.width - 100)
            y = random.uniform(self.env.height / 2, self.env.height - 100)
            creature = Creature(x, y)
            self.env.add_creature(creature)
    
    def update(self, dt=1/60):
        """Update evolution (call each frame)"""
        self.time_in_generation += dt
        
        # Check for dead creatures
        for creature in self.env.creatures:
            if creature.alive and creature.nodes[0].health <= 0:
                creature.alive = False
        
        # Check if generation should end
        alive_count = sum(1 for c in self.env.creatures if c.alive)
        
        if self.time_in_generation >= self.generation_time or alive_count == 0:
            self.end_generation()
    
    def end_generation(self):
        """End current generation, select survivors, reproduce"""
        print(f"\n=== Generation {self.generation} Complete ===")
        
        # Get surviving creatures
        survivors = [c for c in self.env.creatures if c.alive]
        
        # Track stats
        stats = {
            'generation': self.generation,
            'survivors': len(survivors),
            'avg_fitness': sum(c.fitness for c in survivors) / max(1, len(survivors)),
            'max_fitness': max((c.fitness for c in survivors), default=0),
            'avg_food': sum(c.food_eaten for c in survivors) / max(1, len(survivors)),
            'avg_age': sum(c.age for c in survivors) / max(1, len(survivors))
        }
        self.generation_stats.append(stats)
        
        print(f"Survivors: {stats['survivors']}")
        print(f"Max Fitness: {stats['max_fitness']:.1f}")
        print(f"Avg Food: {stats['avg_food']:.1f}")
        
        # Select best creatures for reproduction
        if survivors:
            # Sort by fitness
            survivors.sort(key=lambda c: c.fitness, reverse=True)
            
            # Keep top performers
            elite_count = max(2, len(survivors) // 4)
            elites = survivors[:elite_count]
            
            # Track best
            self.best_creature = elites[0]
            print(f"Best fitness: {self.best_creature.fitness:.1f}")
            print(f"Best genome: {self.best_creature.genome}")
            
            # Create next generation
            self.create_next_generation(elites)
        else:
            # All died - restart with new random population
            print("All creatures died! Starting fresh...")
            self.env.reset()
            self.spawn_initial_population()
        
        # Reset generation timer
        self.time_in_generation = 0
        self.generation += 1
    
    def create_next_generation(self, elites):
        """Create next generation from elite survivors"""
        # Clear old creatures
        self.env.creatures = []
        
        # Create new population
        new_creatures = []
        
        # Keep some elites unchanged (elitism)
        elite_kept = min(2, len(elites))
        for elite in elites[:elite_kept]:
            new_creature = elite.clone()
            new_creature.generation = self.generation
            new_creatures.append(new_creature)
        
        # Fill rest with mutated offspring
        while len(new_creatures) < self.population_size:
            # Select parent (weighted towards better fitness)
            parent = random.choice(elites)
            
            # Create mutated offspring
            offspring = Creature(
                random.uniform(100, self.env.width - 100),
                random.uniform(self.env.height / 2, self.env.height - 100),
                parent.mutate(rate=0.3, magnitude=0.3)
            )
            offspring.generation = self.generation
            new_creatures.append(offspring)
        
        # Add to environment
        for creature in new_creatures:
            self.env.add_creature(creature)
        
        print(f"Created {len(new_creatures)} new creatures")
    
    def get_stats_summary(self):
        """Get summary of evolution stats"""
        if not self.generation_stats:
            return "No statistics yet"
        
        latest = self.generation_stats[-1]
        return f"""
Generation {latest['generation']}:
- Survivors: {latest['survivors']}
- Max Fitness: {latest['max_fitness']:.1f}
- Avg Fitness: {latest['avg_fitness']:.1f}
- Avg Food Eaten: {latest['avg_food']:.1f}
- Avg Age: {latest['avg_age']:.1f}s
"""
