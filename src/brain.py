"""
Brain - Agent decision making for creatures
"""

import random
import math
from Box2D import b2Vec2


class Brain:
    """
    Simple brain for creature decision making
    Uses reactive rules based on environment perception
    """
    
    def __init__(self, genome):
        self.genome = genome.get('brain', {})
        self.hidden_size = self.genome.get('hidden_size', 8)
        self.speed = self.genome.get('speed', 2)
        self.aggression = self.genome.get('aggression', 0.5)
        self.curiosity = self.genome.get('curiosity', 0.5)
        
        # Internal state
        self.target = None
        self.state = 'wander'  # wander, hunt, flee, eat
    
    def think(self, creature, environment):
        """
        Decide creature's next action based on environment
        Returns: (thrust_direction, contraction)
        """
        # Find nearest food
        nearest_food = None
        nearest_food_dist = float('inf')
        
        for food in environment.food:
            dist = (creature.get_center() - food.position).length
            if dist < nearest_food_dist:
                nearest_food_dist = dist
                nearest_food = food
        
        # Find nearest threat (other creatures)
        nearest_threat = None
        nearest_threat_dist = float('inf')
        
        for other in environment.creatures:
            if other == creature or not other.alive:
                continue
            
            dist = (creature.get_center() - other.get_center()).length
            if dist < nearest_threat_dist:
                nearest_threat_dist = dist
                nearest_threat = other
        
        # Decision making
        direction = b2Vec2(0, 0)
        contraction = 0.0
        
        # Check health - if low, prioritize food
        if creature.nodes[0].health < 30:
            self.state = 'hunt'
        
        # Fear response - flee from threats
        if nearest_threat and nearest_threat_dist < creature.get_radius() * 4:
            # Flee from threat
            flee_dir = creature.get_center() - nearest_threat.get_center()
            if flee_dir.length > 0:
                direction = flee_dir / flee_dir.length
            self.state = 'flee'
        
        # Hunt for food
        elif nearest_food and nearest_food_dist < 50:
            # Move towards food
            food_dir = nearest_food.position - creature.get_center()
            if food_dir.length > 0:
                direction = food_dir / food_dir.length
            
            # Contract when close to grab
            if nearest_food_dist < creature.get_radius() * 2:
                contraction = 0.5
            
            self.state = 'hunt'
        
        # Wander if nothing interesting nearby
        else:
            # Random wander with some persistence
            if self.target is None or random.random() < 0.02:
                angle = random.uniform(0, 2 * math.pi)
                self.target = b2Vec2(
                    math.cos(angle),
                    math.sin(angle)
                )
            
            if self.target:
                direction = self.target
                # Occasionally change target
                if random.random() < 0.05:
                    self.target = None
            
            self.state = 'wander'
        
        # Apply brain personality modifiers
        # Curious creatures explore more
        if self.curiosity > 0.7:
            if random.random() < 0.1:
                angle = random.uniform(0, 2 * math.pi)
                direction = b2Vec2(math.cos(angle), math.sin(angle))
        
        # Aggressive creatures might chase others
        if self.aggression > 0.6 and nearest_threat and nearest_threat_dist < 20:
            # Chase instead of flee
            chase_dir = nearest_threat.get_center() - creature.get_center()
            if chase_dir.length > 0:
                direction = chase_dir / chase_dir.length
        
        return (direction.x, direction.y), contraction
    
    def mutate(self, rate=0.1, magnitude=0.2):
        """Create mutated brain"""
        new_brain = self.genome.copy()
        
        for key in new_brain:
            if random.random() < rate:
                new_brain[key] += random.uniform(-magnitude, magnitude)
                new_brain[key] = max(0, min(1, new_brain[key]))
        
        return new_brain
