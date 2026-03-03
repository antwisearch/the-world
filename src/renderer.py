"""
Renderer using Pygame
"""

import pygame
from src.creature import Creature
from src.environment import Food


class Renderer:
    """
    Renders the evolution simulation
    """
    
    def __init__(self, environment, scale=20):
        self.env = environment
        self.scale = scale  # pixels per meter
        
        # Screen size
        self.width = int(environment.width * scale)
        self.height = int(environment.height * scale)
        
        # Create screen
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Biological Chaos - Evolution Simulator")
        
        # Colors
        self.bg_color = (20, 20, 30)
        self.food_color = (50, 200, 50)
        self.wall_color = (100, 100, 120)
        
        # Fonts
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 36)
    
    def render(self):
        """Render one frame"""
        # Clear screen
        self.screen.fill(self.bg_color)
        
        # Draw boundaries
        self.draw_boundaries()
        
        # Draw food
        for food in self.env.food:
            self.draw_food(food)
        
        # Draw creatures
        for creature in self.env.creatures:
            if creature.alive:
                self.draw_creature(creature)
        
        # Draw UI
        self.draw_ui()
        
        # Flip display
        pygame.display.flip()
    
    def draw_boundaries(self):
        """Draw arena boundaries"""
        thickness = 10
        
        # Ground
        pygame.draw.rect(self.screen, self.wall_color, 
                        (0, self.env.height * self.scale - thickness,
                         self.width, thickness))
        
        # Left
        pygame.draw.rect(self.screen, self.wall_color,
                        (0, 0, thickness, self.height))
        
        # Right
        pygame.draw.rect(self.screen, self.wall_color,
                        (self.width - thickness, 0, thickness, self.height))
        
        # Top
        pygame.draw.rect(self.screen, self.wall_color,
                        (0, 0, self.width, thickness))
    
    def draw_food(self, food: Food):
        """Draw food item"""
        x = int(food.position.x * self.scale)
        y = int((self.env.height - food.position.y) * self.scale)
        radius = int(food.radius * self.scale)
        
        pygame.draw.circle(self.screen, self.food_color, (x, y), radius)
    
    def draw_creature(self, creature: Creature):
        """Draw soft body creature"""
        # Get color from genome
        color = creature.genome['color']
        
        # Draw springs (connections)
        for spring in creature.springs:
            x1 = int(spring.node_a.position.x * self.scale)
            y1 = int((self.env.height - spring.node_a.position.y) * self.scale)
            x2 = int(spring.node_b.position.x * self.scale)
            y2 = int((self.env.height - spring.node_b.position.y) * self.scale)
            
            # Color based on stress
            stress = abs(spring.rest_length - spring.node_a.position.Distance(spring.node_b.position))
            stress_color = min(255, int(stress * 50))
            line_color = (min(255, color[0] + stress_color),
                         min(255, color[1] + stress_color),
                         min(255, color[2] + stress_color))
            
            pygame.draw.line(self.screen, line_color, (x1, y1), (x2, y2), 2)
        
        # Draw nodes
        for node in creature.nodes:
            x = int(node.position.x * self.scale)
            y = int((self.env.height - node.position.y) * self.scale)
            radius = int(node.radius * self.scale)
            
            # Health affects brightness
            health_factor = max(0.3, node.health / 100)
            node_color = (int(color[0] * health_factor),
                         int(color[1] * health_factor),
                         int(color[2] * health_factor))
            
            pygame.draw.circle(self.screen, node_color, (x, y), radius)
            pygame.draw.circle(self.screen, (255, 255, 255), (x, y), radius, 1)
    
    def draw_ui(self):
        """Draw UI overlay"""
        # Generation info
        gen_text = self.big_font.render(f"Generation: {self.generation}", True, (255, 255, 255))
        self.screen.blit(gen_text, (20, 20))
        
        # Time in generation
        time_text = self.font.render(f"Time: {self.time_in_generation:.1f}s / {self.generation_time}s", True, (200, 200, 200))
        self.screen.blit(time_text, (20, 60))
        
        # Population info
        alive = sum(1 for c in self.env.creatures if c.alive)
        pop_text = self.font.render(f"Alive: {alive} / {len(self.env.creatures)}", True, (200, 200, 200))
        self.screen.blit(pop_text, (20, 90))
        
        # Food count
        food_text = self.font.render(f"Food: {len(self.env.food)}", True, (150, 200, 150))
        self.screen.blit(food_text, (20, 120))
        
        # Best fitness
        if self.best_creature:
            best_text = self.font.render(f"Best Fitness: {self.best_creature.fitness:.1f}", True, (255, 200, 100))
            self.screen.blit(best_text, (20, 150))
        
        # Controls
        controls = [
            "SPACE: Reset simulation",
            "R: Restart",
            "ESC: Quit"
        ]
        for i, control in enumerate(controls):
            ctrl_text = self.font.render(control, True, (100, 100, 100))
            self.screen.blit(ctrl_text, (20, self.height - 80 + i * 20))
    
    @property
    def generation(self):
        return self.evolution.generation if hasattr(self, 'evolution') else 0
    
    @generation.setter
    def generation(self, value):
        if hasattr(self, 'evolution'):
            self.evolution.generation = value
    
    @property
    def time_in_generation(self):
        return self.evolution.time_in_generation if hasattr(self, 'evolution') else 0
    
    @time_in_generation.setter
    def time_in_generation(self, value):
        if hasattr(self, 'evolution'):
            self.evolution.time_in_generation = value
    
    @property
    def generation_time(self):
        return self.evolution.generation_time if hasattr(self, 'evolution') else 30
    
    @generation_time.setter
    def generation_time(self, value):
        if hasattr(self, 'evolution'):
            self.evolution.generation_time = value
    
    @property
    def best_creature(self):
        return self.evolution.best_creature if hasattr(self, 'evolution') else None
    
    @best_creature.setter
    def best_creature(self, value):
        if hasattr(self, 'evolution'):
            self.evolution.best_creature = value
