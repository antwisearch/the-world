"""
Creature - Soft body with full genome for co-evolution
"""

import random
import math
import Box2D as box2d
from Box2D import b2Vec2


class Node:
    """A single node in a soft body creature"""
    
    def __init__(self, x, y, phys_world, mass=1.0, radius=0.3):
        self.phys_world = phys_world
        
        # Create Box2D body
        body_def = box2d.b2BodyDef(
            type=box2d.b2_dynamicBody,
            position=b2Vec2(x, y),
            linearDamping=0.5,
            angularDamping=0.5
        )
        self.body = self.phys_world.world.CreateBody(body_def)
        
        # Create Fixture
        fixture_def = box2d.b2FixtureDef(
            shape=box2d.b2CircleShape(radius=radius),
            density=mass / (math.pi * radius * radius),
            friction=0.3,
            restitution=0.2
        )
        self.body.CreateFixture(fixture_def)
        
        # Properties
        self.mass = mass
        self.radius = radius
        self.health = 100.0
        self.age = 0
    
    @property
    def position(self):
        return self.body.position
    
    @position.setter
    def position(self, value):
        self.body.position = value
        
    @property
    def velocity(self):
        return self.body.linearVelocity
        
    @velocity.setter
    def velocity(self, value):
        self.body.linearVelocity = value


class Spring:
    """Connection between two nodes"""
    
    def __init__(self, node_a, node_b, stiffness=50.0, damping=5.0, rest_length=None):
        self.node_a = node_a
        self.node_b = node_b
        self.stiffness = stiffness
        self.damping = damping
        self.rest_length = rest_length if rest_length is not None else (node_a.position - node_b.position).length
        self.rest_length = max(self.rest_length, 0.1)


class Creature:
    """
    Soft-body creature with full genome for world-guided evolution
    """
    
    def __init__(self, x, y, phys_world=None, genome=None):
        self.phys_world = phys_world
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
        if self.phys_world:
            self.build_body(x, y)
    
    def random_genome(self):
        """Generate random genome with all traits"""
        return {
            'body': {
                'size': random.uniform(0.5, 2.0),
                'shape': random.choice(['blob', 'circle', 'star', 'chain']),
                'nodes': random.randint(4, 12),
                'flexibility': random.uniform(0.2, 0.8),
                'skin_thickness': random.uniform(0.3, 0.7),
                'color': (
                    random.randint(50, 255),
                    random.randint(50, 255),
                    random.randint(50, 255)
                ),
                'fire_resistance': random.uniform(0, 0.3),
                'optimal_temp': random.uniform(10, 30),
            },
            'physiology': {
                'metabolism': random.uniform(0.3, 0.8),
                'temp_tolerance': random.uniform(0.2, 0.6),
                'speed': random.uniform(0.3, 0.8),
                'strength': random.uniform(0.3, 0.8),
                'sensory_range': random.uniform(15, 40),
                'healing': random.uniform(0.2, 0.6),
                'water_efficiency': random.uniform(0.3, 0.7),
            },
            'brain': {
                'curiosity': random.uniform(0.2, 0.7),
                'aggression': random.uniform(0.1, 0.5),
                'social': random.uniform(0.1, 0.4),
                'memory': random.uniform(0.2, 0.6),
                'spatial': random.uniform(0.2, 0.6),
            }
        }
    
    def build_body(self, x, y):
        """Build the soft body from genome"""
        genome = self.genome
        body = genome['body']
        
        num_nodes = body['nodes']
        radius = body['size'] * 0.4
        shape = body['shape']
        
        # Create nodes based on shape
        if shape == 'circle':
            for i in range(num_nodes):
                angle = (2 * math.pi * i) / num_nodes
                nx = x + radius * 2 * math.cos(angle)
                ny = y + radius * 2 * math.sin(angle)
                node = Node(nx, ny, self.phys_world, body.get('mass', 1.0), radius)
                self.nodes.append(node)
        
        elif shape == 'star':
            center = Node(x, y, self.phys_world, body.get('mass', 1.0), radius * 1.5)
            self.nodes.append(center)
            for i in range(num_nodes - 1):
                angle = (2 * math.pi * i) / (num_nodes - 1)
                nx = x + radius * 3 * math.cos(angle)
                ny = y + radius * 3 * math.sin(angle)
                node = Node(nx, ny, self.phys_world, body.get('mass', 1.0) * 0.7, radius * 0.7)
                self.nodes.append(node)
        
        elif shape == 'chain':
            for i in range(num_nodes):
                nx = x + i * radius * 1.5 - (num_nodes * radius * 1.5 / 2)
                ny = y
                node = Node(nx, ny, self.phys_world, body.get('mass', 1.0), radius)
                self.nodes.append(node)
        
        else:  # blob
            for i in range(num_nodes):
                angle = random.uniform(0, 2 * math.pi)
                dist = random.uniform(0, radius * 2)
                nx = x + dist * math.cos(angle)
                ny = y + dist * math.sin(angle)
                node = Node(nx, ny, self.phys_world, body.get('mass', 1.0), radius)
                self.nodes.append(node)
        
        # Create springs based on flexibility
        stiffness = 20 + (1 - body['flexibility']) * 80
        damping = body['flexibility'] * 10
        
        for i, node_a in enumerate(self.nodes):
            for j, node_b in enumerate(self.nodes):
                if i < j:
                    dist = (node_a.position - node_b.position).length
                    if dist < radius * 5:
                        spring = Spring(node_a, node_b, stiffness, damping)
                        self.springs.append(spring)
        
        # Ensure structural integrity
        if len(self.nodes) > 2:
            for i in range(len(self.nodes)):
                distances = [(j, (self.nodes[i].position - self.nodes[j].position).length) 
                           for j in range(len(self.nodes)) if j != i]
                distances.sort(key=lambda x: x[1])
                
                for j, _ in distances[:2]:
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
            pos_a = spring.node_a.position
            pos_b = spring.node_b.position
            
            delta = pos_b - pos_a
            distance = delta.length
            if distance < 0.001:
                continue
            
            # Spring force (Hooke's law)
            displacement = distance - spring.rest_length
            force_magnitude = spring.stiffness * displacement
            
            # Damping force
            vel_a = spring.node_a.velocity
            vel_b = spring.node_b.velocity
            relative_velocity = vel_b - vel_a
            damping_force = relative_velocity * spring.damping
            
            # Apply forces directly to Box2D bodies
            direction = delta / distance
            force = direction * force_magnitude + damping_force
            
            spring.node_a.body.ApplyForceToCenter(force, wake=True)
            spring.node_b.body.ApplyForceToCenter(-force, wake=True)
    
    def apply_input(self, thrust_direction, contraction=0.0):
        """Apply user/thrust input to move creature"""
        speed = self.genome['physiology']['speed']
        
        force = b2Vec2(
            thrust_direction[0], 
            thrust_direction[1]
        ) * speed * 200
        
        for node in self.nodes:
            node.body.ApplyForceToCenter(force, wake=True)
            
            # Apply contraction
            if contraction > 0:
                center = self.get_center()
                to_center = center - node.position
                dist = to_center.length
                if dist > 0.1:
                    contract_force = (to_center / dist) * contraction * 100
                    node.body.ApplyForceToCenter(contract_force, wake=True)
    
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
            dist = (node.position - center).length
            max_dist = max(max_dist, dist)
        return max_dist
    
    def update(self, dt, world_state=None):
        """Update creature state"""
        if not self.alive:
            return
        
        self.age += dt
        self.fitness += dt * 10  # Base fitness is survival
        
        # Apply internal forces
        self.apply_forces()
        
        # Metabolism - health decreases based on rate
        metabolism = self.genome['physiology']['metabolism']
        health_loss = dt * 0.5 * metabolism * len(self.nodes)
        
        # Temperature stress
        if world_state:
            temp = world_state.get('temperature', 20)
            optimal = self.genome['body'].get('optimal_temp', 20)
            tolerance = self.genome['physiology'].get('temp_tolerance', 0.3) * 30
            
            temp_stress = abs(temp - optimal) - tolerance
            if temp_stress > 0:
                health_loss += dt * temp_stress * 2
        
        # Apply health loss
        for node in self.nodes:
            node.health -= health_loss
        
        # Check death
        if not self.nodes:
            self.die()
            return

        avg_health = sum(n.health for n in self.nodes) / len(self.nodes)
        if avg_health <= 0:
            self.die()
    
    def die(self):
        """Handle death and clean up physics bodies"""
        self.alive = False
        for node in self.nodes:
            if node.body:
                self.phys_world.world.DestroyBody(node.body)
                node.body = None
    
    def calculate_adaptation_bonus(self, world_state) -> float:
        """Calculate fitness bonus based on adaptation to world state"""
        if not world_state:
            return 1.0
        
        bonus = 1.0
        
        # Temperature adaptation
        temp = world_state.get('temperature', 20)
        optimal = self.genome['body'].get('optimal_temp', 20)
        tolerance = self.genome['physiology'].get('temp_tolerance', 0.3) * 30
        
        if abs(temp - optimal) < tolerance:
            bonus *= 1.5  # In comfort zone
        
        # Era-specific bonuses
        era = world_state.get('era', 'primordial')
        
        if era == 'age_of_fire':
            fire_res = self.genome['body'].get('fire_resistance', 0)
            bonus *= (1 + fire_res)
        
        elif era == 'ice_age':
            # Cold tolerance
            tolerance = self.genome['physiology'].get('temp_tolerance', 0.3)
            bonus *= (1 + tolerance)
        
        elif era == 'urban':
            # Spatial intelligence
            spatial = self.genome['brain'].get('spatial', 0.3)
            bonus *= (1 + spatial)
        
        elif era == 'collapse':
            # Efficiency
            efficiency = 1 - self.genome['physiology'].get('metabolism', 0.5)
            bonus *= (1 + efficiency * 0.5)
        
        return bonus
    
    def mutate(self, rate=0.3, magnitude=0.3, world_state=None):
        """Create mutated copy of genome, guided by world state"""
        new_genome = {
            'body': self.genome['body'].copy(),
            'physiology': self.genome['physiology'].copy(),
            'brain': self.genome['brain'].copy()
        }
        
        # Mutate body traits
        for key in new_genome['body']:
            if isinstance(new_genome['body'][key], (int, float)):
                if random.random() < rate:
                    new_genome['body'][key] *= random.uniform(1 - magnitude, 1 + magnitude)
                    new_genome['body'][key] = max(0.1, new_genome['body'][key])
        
        # Mutate physiology
        for key in new_genome['physiology']:
            if isinstance(new_genome['physiology'][key], (int, float)):
                if random.random() < rate:
                    new_genome['physiology'][key] += random.uniform(-magnitude, magnitude)
                    new_genome['physiology'][key] = max(0, min(1, new_genome['physiology'][key]))
        
        # Mutate brain
        for key in new_genome['brain']:
            if isinstance(new_genome['brain'][key], (int, float)):
                if random.random() < rate:
                    new_genome['brain'][key] += random.uniform(-magnitude, magnitude)
                    new_genome['brain'][key] = max(0, min(1, new_genome['brain'][key]))
        
        # Mutate color
        if random.random() < rate:
            color = list(new_genome['body']['color'])
            for i in range(3):
                if random.random() < 0.3:
                    color[i] = max(0, min(255, color[i] + random.randint(-30, 30)))
            new_genome['body']['color'] = tuple(color)
        
        # World-guided mutations (倾向)
        if world_state:
            era = world_state.get('era', 'primordial')
            temp = world_state.get('temperature', 20)
            
            if era == 'age_of_fire' or temp > 35:
                # Favor fire resistance
                new_genome['body']['fire_resistance'] = min(1,
                    new_genome['body'].get('fire_resistance', 0) + random.uniform(0, 0.1))
            
            if era == 'ice_age' or temp < 5:
                # Favor cold tolerance
                new_genome['body']['optimal_temp'] = max(-10,
                    new_genome['body'].get('optimal_temp', 20) - random.uniform(0, 2))
                new_genome['physiology']['temp_tolerance'] = min(1,
                    new_genome['physiology'].get('temp_tolerance', 0.3) + random.uniform(0, 0.05))
            
            if world_state.get('weather') == 'drought':
                # Favor water efficiency
                new_genome['physiology']['water_efficiency'] = min(1,
                    new_genome['physiology'].get('water_efficiency', 0.5) + random.uniform(0, 0.1))
            
            structures = world_state.get('terrain', {}).get('structures', [])
            if len(structures) > 10:
                # Favor spatial intelligence
                new_genome['brain']['spatial'] = min(1,
                    new_genome['brain'].get('spatial', 0.3) + random.uniform(0, 0.1))
        
        return new_genome
    
    def clone(self):
        """Create exact copy"""
        return Creature(self.get_center().x, self.get_center().y, self.phys_world, self.genome.copy())
