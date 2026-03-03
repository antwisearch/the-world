"""
Soft-body creature implementation using Box2D
"""

import numpy as np
import random
import box2d
from box2d import (b2Vec2, b2Body, b2CircleShape, b2PolygonShape, 
                   b2BodyDef, b2DynamicBody, b2FixtureDef, b2DistanceJointDef)


class Node:
    """A single node in a soft body creature"""
    
    def __init__(self, x, y, mass=1.0, radius=0.3):
        self.position = b2Vec2(x, y)
        self.velocity = b2Vec2(0, 0)
        self.mass = mass
        self.radius = radius
        self.force = b2Vec2(0, 0)
        self.health = 100.0
        self.age = 0


class Spring:
    """Connection between two nodes"""
    
    def __init__(self, node_a, node_b, stiffness=50.0, damping=5.0, rest_length=None):
        self.node_a = node_a
        self.node_b = node_b
        self.stiffness = stiffness
        self.damping = damping
        self.rest_length = rest_length if rest_length is not None else node_a.position.Distance(node_b.position)
        self.rest_length = max(self.rest_length, 0.1)  # Minimum length


class Creature:
    """
    Soft-body creature made of nodes connected by springs
    """
    
    def __init__(self, x, y, genome=None):
        self.nodes = []
        self.springs = []
        self.age = 0
        self.fitness = 0
        self.food_eaten = 0
        self.alive = True
        self.generation = 0
        
        # Use genome or create random one
        if genome is None:
            self.genome = self.random_genome()
        else:
            self.genome = genome.copy()
        
        # Build body from genome
        self.build_body(x, y)
    
    def random_genome(self):
        """Generate random genome"""
        return {
            'num_nodes': random.randint(4, 12),
            'node_radius': random.uniform(0.2, 0.6),
            'node_mass': random.uniform(0.5, 2.0),
            'spring_stiffness': random.uniform(20, 100),
            'spring_damping': random.uniform(1, 10),
            'shape_type': random.choice(['circle', 'star', 'chain', 'blob']),
            'color': (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255)
            ),
            'brain': self.random_brain()
        }
    
    def random_brain(self):
        """Generate random brain structure"""
        return {
            'hidden_size': random.randint(4, 16),
            'speed': random.uniform(1, 5),
            'aggression': random.uniform(0, 1),
            'curiosity': random.uniform(0, 1)
        }
    
    def build_body(self, x, y):
        """Build the soft body from genome"""
        genome = self.genome
        num_nodes = genome['num_nodes']
        radius = genome['node_radius']
        shape = genome['shape_type']
        
        # Create nodes based on shape
        if shape == 'circle':
            # Circular arrangement
            for i in range(num_nodes):
                angle = (2 * np.pi * i) / num_nodes
                nx = x + radius * 2 * np.cos(angle)
                ny = y + radius * 2 * np.sin(angle)
                node = Node(nx, ny, genome['node_mass'], radius)
                self.nodes.append(node)
        
        elif shape == 'star':
            # Star shape with center
            center = Node(x, y, genome['node_mass'], radius * 1.5)
            self.nodes.append(center)
            for i in range(num_nodes - 1):
                angle = (2 * np.pi * i) / (num_nodes - 1)
                nx = x + radius * 3 * np.cos(angle)
                ny = y + radius * 3 * np.sin(angle)
                node = Node(nx, ny, genome['node_mass'] * 0.7, radius * 0.7)
                self.nodes.append(node)
        
        elif shape == 'chain':
            # Chain/line
            for i in range(num_nodes):
                nx = x + i * radius * 1.5 - (num_nodes * radius * 1.5 / 2)
                ny = y
                node = Node(nx, ny, genome['node_mass'], radius)
                self.nodes.append(node)
        
        else:  # blob
            # Random blob
            for i in range(num_nodes):
                angle = random.uniform(0, 2 * np.pi)
                dist = random.uniform(0, radius * 2)
                nx = x + dist * np.cos(angle)
                ny = y + dist * np.sin(angle)
                node = Node(nx, ny, genome['node_mass'], radius)
                self.nodes.append(node)
        
        # Create springs (connections between nodes)
        stiffness = genome['spring_stiffness']
        damping = genome['spring_damping']
        
        # Connect each node to nearby nodes
        for i, node_a in enumerate(self.nodes):
            for j, node_b in enumerate(self.nodes):
                if i < j:  # Avoid duplicates
                    dist = node_a.position.Distance(node_b.position)
                    if dist < radius * 5:  # Connect close nodes
                        spring = Spring(node_a, node_b, stiffness, damping)
                        self.springs.append(spring)
        
        # Also connect to closest nodes to maintain structure
        if len(self.nodes) > 2:
            # Connect to form a more stable structure
            for i in range(len(self.nodes)):
                # Find 2 closest other nodes
                distances = [(j, self.nodes[i].position.Distance(self.nodes[j].position)) 
                           for j in range(len(self.nodes)) if j != i]
                distances.sort(key=lambda x: x[1])
                
                for j, _ in distances[:2]:
                    # Check if connection already exists
                    exists = any(
                        (s.node_a == self.nodes[i] and s.node_b == self.nodes[j]) or
                        (s.node_a == self.nodes[j] and s.node_b == self.nodes[i])
                        for s in self.springs
                    )
                    if not exists:
                        spring = Spring(self.nodes[i], self.nodes[j], stiffness, damping)
                        self.springs.append(spring)
    
    def apply_forces(self):
        """Apply internal spring forces"""
        for spring in self.springs:
            # Get positions
            pos_a = spring.node_a.position
            pos_b = spring.node_b.position
            
            # Calculate distance
            delta = pos_b - pos_a
            distance = delta.Length()
            if distance < 0.001:
                continue
            
            # Spring force (Hooke's law)
            displacement = distance - spring.rest_length
            force_magnitude = spring.stiffness * displacement
            
            # Damping force
            vel_a = spring.node_a.velocity
            vel_b = spring.node_b.velocity
            relative_velocity = vel_b - vel_a
            damping_force = relative_velocity.Normalize() * spring.damping * relative_velocity.Length()
            
            # Apply forces
            direction = delta / distance
            force = direction * force_magnitude + damping_force
            
            spring.node_a.force += force
            spring.node_b.force -= force
    
    def apply_input(self, thrust_direction, contraction=0.0):
        """Apply user/thrust input to move creature"""
        for node in self.nodes:
            # Apply thrust in direction
            node.velocity += b2Vec2(thrust_direction[0], thrust_direction[1]) * self.genome['brain']['speed']
            
            # Apply contraction (pull nodes together)
            if contraction > 0:
                # Find center
                center = self.get_center()
                for node in self.nodes:
                    to_center = center - node.position
                    dist = to_center.Length()
                    if dist > 0.1:
                        node.velocity += to_center.Normalize() * contraction * 2
    
    def get_center(self):
        """Get center of mass"""
        if not self.nodes:
            return b2Vec2(0, 0)
        
        total = b2Vec2(0, 0)
        for node in self.nodes:
            total += node.position
        return total / len(self.nodes)
    
    def get_radius(self):
        """Get approximate radius of creature"""
        if not self.nodes:
            return 0
        
        center = self.get_center()
        max_dist = 0
        for node in self.nodes:
            dist = node.position.Distance(center)
            max_dist = max(max_dist, dist)
        return max_dist
    
    def update(self, dt):
        """Update creature state"""
        if not self.alive:
            return
        
        self.age += dt
        self.fitness += dt  # Base fitness is survival time
        
        # Apply internal forces
        self.apply_forces()
        
        # Update velocities (Euler integration)
        gravity = b2Vec2(0, -10)  # Gravity
        for node in self.nodes:
            node.velocity += gravity * dt
            node.velocity += node.force / node.mass * dt
            node.position += node.velocity * dt
            node.force = b2Vec2(0, 0)  # Reset forces
            
            # Damping
            node.velocity *= 0.99
        
        # Health decreases over time (metabolism)
        self.nodes[0].health -= dt * 0.5 * len(self.nodes)
        if self.nodes[0].health <= 0:
            self.alive = False
    
    def mutate(self, rate=0.1, magnitude=0.2):
        """Create mutated copy of genome"""
        new_genome = self.genome.copy()
        
        # Mutate numeric values
        for key in ['num_nodes', 'node_radius', 'node_mass', 'spring_stiffness', 
                   'spring_damping', 'brain']:
            if key in new_genome and isinstance(new_genome[key], (int, float)):
                if random.random() < rate:
                    new_genome[key] *= random.uniform(1 - magnitude, 1 + magnitude)
                    new_genome[key] = max(0.1, new_genome[key])  # Keep positive
        
        # Mutate color
        if random.random() < rate:
            color = list(new_genome['color'])
            for i in range(3):
                if random.random() < 0.3:
                    color[i] = max(0, min(255, color[i] + random.randint(-30, 30)))
            new_genome['color'] = tuple(color)
        
        # Mutate brain
        if 'brain' in new_genome:
            brain = new_genome['brain']
            for key in brain:
                if random.random() < rate:
                    brain[key] += random.uniform(-magnitude, magnitude)
                    brain[key] = max(0, min(1, brain[key]))
        
        # Occasionally change shape
        if random.random() < rate * 0.5:
            new_genome['shape_type'] = random.choice(['circle', 'star', 'chain', 'blob'])
        
        return new_genome
    
    def clone(self):
        """Create exact copy"""
        return Creature(self.get_center().x, self.get_center().y, self.genome.copy())
