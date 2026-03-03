"""
Evolution Engine - World-guided natural selection
"""

import random
from src.creature import Creature


class EvolutionEngine:
    """
    Manages evolution based on world state
    """
    
    def __init__(self, world, population_size=20, generation_time=30):
        self.world = world
        self.population_size = population_size
        self.generation_time = generation_time
        self.generation = 1
        self.time_in_generation = 0
        self.best_creature = None
        self.generation_stats = []
        self.creatures = []
    
    def spawn_initial_population(self, count=None):
        """Spawn initial random population"""
        count = count or self.population_size
        
        for _ in range(count):
            x = random.uniform(100, self.world.width - 100)
            y = random.uniform(self.world.height / 2, self.world.height - 100)
            creature = Creature(x, y)
            creature.generation = self.generation
            self.creatures.append(creature)
    
    def update(self, dt=1/60):
        """Update evolution"""
        self.time_in_generation += dt
        
        # Update creatures
        for creature in self.creatures:
            if creature.alive:
                # Get world state at creature position
                world_state = self._get_world_state_for_creature(creature)
                creature.update(dt, world_state)
                
                # Apply adaptation bonus
                bonus = creature.calculate_adaptation_bonus(world_state)
                creature.fitness += dt * 10 * bonus
        
        # Check for dead creatures
        for creature in self.creatures:
            if creature.alive and self._is_dead(creature):
                creature.alive = False
        
        # Check if generation should end
        alive_count = sum(1 for c in self.creatures if c.alive)
        
        if self.time_in_generation >= self.generation_time or alive_count == 0:
            self.end_generation()
    
    def _get_world_state_for_creature(self, creature):
        """Get world state at creature's position"""
        center = creature.get_center()
        zone = self.world.get_zone_at(center.x)
        temp = self.world.get_temperature_at(center.x, center.y)
        
        return {
            'era': self.world.era,
            'climate': zone.name,
            'temperature': temp,
            'weather': self.world.get_weather_at(center.x, center.y),
            'global_temp': self.world.global_temp,
            'terrain': {
                'structures': self.world.terrain.structures,
                'elevation': self.world.terrain.get_elevation(center.x, center.y)
            }
        }
    
    def _is_dead(self, creature) -> bool:
        """Check if creature should die"""
        # Health-based death
        avg_health = sum(n.health for n in creature.nodes) / len(creature.nodes)
        if avg_health <= 0:
            return True
        
        # Out of bounds
        center = creature.get_center()
        if center.x < 0 or center.x > self.world.width:
            return True
        if center.y < 0 or center.y > self.world.height:
            return True
        
        # Fire damage
        if self.world.get_weather_at(center.x, center.y) == 'fire':
            skin = creature.genome['body'].get('skin_thickness', 0.5)
            fire_res = creature.genome['body'].get('fire_resistance', 0)
            damage = 5 * (1 - skin) * (1 - fire_res)
            for node in creature.nodes:
                node.health -= damage
        
        return False
    
    def end_generation(self):
        """End generation, select survivors, reproduce"""
        print(f"\n{'='*50}")
        print(f"🌍 GENERATION {self.generation} - ERA: {self.world.era.upper()}")
        print(f"{'='*50}")
        
        # Get surviving creatures
        survivors = [c for c in self.creatures if c.alive]
        
        # Track stats
        stats = {
            'generation': self.generation,
            'era': self.world.era,
            'survivors': len(survivors),
            'avg_fitness': sum(c.fitness for c in survivors) / max(1, len(survivors)),
            'max_fitness': max((c.fitness for c in survivors), default=0),
            'avg_food': sum(c.food_eaten for c in survivors) / max(1, len(survivors)),
            'avg_age': sum(c.age for c in survivors) / max(1, len(survivors))
        }
        
        # Analyze evolved traits
        if survivors:
            stats['avg_size'] = sum(c.genome['body']['size'] for c in survivors) / len(survivors)
            stats['avg_fire_resistance'] = sum(c.genome['body'].get('fire_resistance', 0) for c in survivors) / len(survivors)
            stats['avg_temp_tolerance'] = sum(c.genome['physiology']['temp_tolerance'] for c in survivors) / len(survivors)
            stats['avg_spatial'] = sum(c.genome['brain'].get('spatial', 0.3) for c in survivors) / len(survivors)
        
        self.generation_stats.append(stats)
        
        print(f"Survivors: {stats['survivors']}")
        print(f"Max Fitness: {stats['max_fitness']:.1f}")
        if 'avg_size' in stats:
            print(f"Avg Size: {stats['avg_size']:.2f}")
            print(f"Avg Fire Resistance: {stats['avg_fire_resistance']:.2f}")
            print(f"Avg Temp Tolerance: {stats['avg_temp_tolerance']:.2f}")
            print(f"Avg Spatial IQ: {stats['avg_spatial']:.2f}")
        
        # Select best creatures for reproduction
        if survivors:
            survivors.sort(key=lambda c: c.fitness, reverse=True)
            elites = survivors[:max(2, len(survivors) // 4)]
            self.best_creature = elites[0]
            self.create_next_generation(elites)
        else:
            print("All died! Starting fresh...")
            self.creatures = []
            self.spawn_initial_population()
        
        self.time_in_generation = 0
        self.generation += 1
    
    def create_next_generation(self, elites):
        """Create next generation from elite survivors"""
        self.creatures = []
        
        # Get world state for mutation guidance
        world_state = self.world.to_dict()
        
        # Keep some elites unchanged (elitism)
        elite_kept = min(2, len(elites))
        for elite in elites[:elite_kept]:
            new_creature = elite.clone()
            new_creature.generation = self.generation
            self.creatures.append(new_creature)
        
        # Fill rest with mutated offspring
        while len(self.creatures) < self.population_size:
            parent = random.choice(elites)
            
            # Get world state at spawn position for mutation guidance
            spawn_x = random.uniform(100, self.world.width - 100)
            spawn_y = random.uniform(self.world.height / 2, self.world.height - 100)
            
            # Add position-specific world state
            spawn_state = world_state.copy()
            spawn_state['temperature'] = self.world.get_temperature_at(spawn_x, spawn_y)
            spawn_state['climate'] = self.world.get_zone_at(spawn_x).name
            
            offspring = Creature(
                spawn_x,
                spawn_y,
                parent.mutate(rate=0.3, magnitude=0.3, world_state=spawn_state)
            )
            offspring.generation = self.generation
            self.creatures.append(offspring)
        
        print(f"Created {len(self.creatures)} creatures for generation {self.generation}")
    
    def get_era_stats(self):
        """Get stats about era transitions"""
        era_counts = {}
        for stat in self.generation_stats:
            era = stat.get('era', 'unknown')
            era_counts[era] = era_counts.get(era, 0) + 1
        return era_counts
    
    def get_stats_summary(self):
        """Get evolution stats summary"""
        if not self.generation_stats:
            return "No statistics yet"
        
        latest = self.generation_stats[-1]
        summary = f"""
Generation {latest['generation']} ({latest['era']}):
- Survivors: {latest['survivors']}
- Max Fitness: {latest['max_fitness']:.1f}
- Avg Fitness: {latest['avg_fitness']:.1f}
- Avg Food: {latest['avg_food']:.1f}
"""
        if 'avg_size' in latest:
            summary += f"- Avg Size: {latest['avg_size']:.2f}\n"
            summary += f"- Avg Fire Resistance: {latest['avg_fire_resistance']:.2f}\n"
        
        return summary
