"""
Physics environment using Box2D
"""

import Box2D as box2d
from Box2D import (b2Vec2, b2AABB, b2CircleShape, b2PolygonShape,
                   b2BodyDef, b2DynamicBody, b2StaticBody, b2FixtureDef,
                   b2Circle, b2Polygon)
import random


class Food:
    """Food source that creatures can eat"""
    
    def __init__(self, x, y):
        self.position = b2Vec2(x, y)
        self.radius = 0.3
        self.nutrition = 20
        self.alive = True


class World:
    """
    Physics simulation environment
    """
    
    def __init__(self, width=1200, height=800, gravity=-10):
        self.width = width
        self.height = height
        self.gravity = b2Vec2(0, gravity)
        
        # Create Box2D world
        self.world = box2d.b2World(self.gravity)
        
        # Entities
        self.creatures = []
        self.food = []
        
        # Arena boundaries
        self.create_boundaries()
        
        # Spawn initial food
        for _ in range(30):
            self.spawn_food()
    
    def create_boundaries(self):
        """Create arena walls"""
        wall_thickness = 1.0
        
        # Ground
        ground = self.world.CreateBody(b2BodyDef(position=b2Vec2(self.width/2, -wall_thickness/2)))
        ground.CreateFixture(b2PolygonShape(box=b2Vec2(self.width/2, wall_thickness/2)), friction=0.5)
        
        # Left wall
        left = self.world.CreateBody(b2BodyDef(position=b2Vec2(-wall_thickness/2, self.height/2)))
        left.CreateFixture(b2PolygonShape(box=b2Vec2(wall_thickness/2, self.height/2)), friction=0.5)
        
        # Right wall
        right = self.world.CreateBody(b2BodyDef(position=b2Vec2(self.width + wall_thickness/2, self.height/2)))
        right.CreateFixture(b2PolygonShape(box=b2Vec2(wall_thickness/2, self.height/2)), friction=0.5)
        
        # Ceiling
        ceiling = self.world.CreateBody(b2BodyDef(position=b2Vec2(self.width/2, self.height + wall_thickness/2)))
        ceiling.CreateFixture(b2PolygonShape(box=b2Vec2(self.width/2, wall_thickness/2)), friction=0.5)
    
    def spawn_food(self):
        """Spawn food at random position"""
        x = random.uniform(50, self.width - 50)
        y = random.uniform(50, self.height - 50)
        food = Food(x, y)
        self.food.append(food)
    
    def add_creature(self, creature):
        """Add creature to environment"""
        self.creatures.append(creature)
    
    def remove_creature(self, creature):
        """Remove creature from environment"""
        if creature in self.creatures:
            self.creatures.remove(creature)
    
    def check_collisions(self):
        """Check and handle collisions"""
        for creature in self.creatures:
            if not creature.alive:
                continue
            
            # Check food collision
            for food in self.food:
                if not food.alive:
                    continue
                
                for node in creature.nodes:
                    dist = (node.position - food.position).length
                    if dist < node.radius + food.radius:
                        # Eat food
                        food.alive = False
                        creature.food_eaten += 1
                        creature.fitness += food.nutrition * 10
                        # Restore some health
                        for n in creature.nodes:
                            n.health = min(100, n.health + food.nutrition)
            
            # Check creature collision
            for other in self.creatures:
                if other == creature or not other.alive:
                    continue
                
                # Simple collision - push apart
                center_a = creature.get_center()
                center_b = other.get_center()
                delta = center_a - center_b
                dist = delta.length
                min_dist = creature.get_radius() + other.get_radius()
                
                if dist < min_dist and dist > 0.1:
                    # Push apart
                    overlap = min_dist - dist
                    push = (delta / dist if dist > 0 else box2d.b2Vec2(1,0)) * overlap * 0.5
                    for node in creature.nodes:
                        node.position += push
                    for node in other.nodes:
                        node.position -= push
    
    def step(self, dt=1/60):
        """Step the physics simulation"""
        # Update creatures
        for creature in self.creatures:
            if creature.alive:
                creature.update(dt)
                
                # Keep in bounds
                for node in creature.nodes:
                    node.position.x = max(1, min(self.width - 1, node.position.x))
                    node.position.y = max(1, min(self.height - 1, node.position.y))
        
        # Check collisions
        self.check_collisions()
        
        # Remove dead food
        self.food = [f for f in self.food if f.alive]
        
        # Spawn new food periodically
        if len(self.food) < 20 and random.random() < 0.1:
            self.spawn_food()
        
        # Step Box2D world
        self.world.Step(dt, velocityIterations=8, positionIterations=3)
    
    def reset(self):
        """Reset the environment"""
        self.creatures = []
        self.food = []
        
        # Recreate boundaries
        for body in self.world.bodies:
            self.world.DestroyBody(body)
        
        self.create_boundaries()
        
        # Spawn initial food
        for _ in range(30):
            self.spawn_food()
