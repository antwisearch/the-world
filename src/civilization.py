"""
Civilization - Population management, events, trading
"""

import random


class Civilization:
    """Manages the agent population and events"""
    
    def __init__(self, world):
        self.world = world
        self.generation = 1
        self.time = 0
    
    def update(self, dt):
        """Update civilization"""
        self.time += dt
        
        # Check for births
        self.check_births()
        
        # Check for new agents joining
        self.check_immigration()
    
    def check_births(self):
        """Check if any agents should reproduce"""
        for agent in self.world.agents:
            if not agent.alive:
                continue
            
            # High happiness + enough food = baby
            if (agent.needs['happiness'] > 70 and 
                agent.needs['food'] > 50 and 
                agent.inventory.get('food', 0) > 20 and
                random.random() < 0.001):  # Small chance per tick
                
                # Create baby
                baby_x = agent.x + random.uniform(-5, 5)
                baby_y = agent.y + random.uniform(-5, 5)
                
                # Inherit some traits
                baby_genome = agent.genome.copy()
                # Slight mutation
                baby_genome['body_size'] *= random.uniform(0.9, 1.1)
                
                from src.agent import Agent
                baby = Agent(baby_x, baby_y, baby_genome)
                baby.generation = agent.generation + 1
                
                # Take food from parent
                agent.inventory['food'] -= 10
                
                self.world.add_agent(baby)
                self.world.log_event(f"Born! Agent {len(self.world.agents)} (generation {baby.generation})")
    
    def check_immigration(self):
        """New agents join the settlement"""
        # If population is low, new agents arrive
        alive = len([a for a in self.world.agents if a.alive])
        
        if alive < 5 and random.random() < 0.01:
            from src.agent import Agent
            new_agent = Agent(
                random.uniform(100, self.world.width - 100),
                random.uniform(100, self.world.height - 100)
            )
            new_agent.needs['food'] = 50
            new_agent.needs['happiness'] = 60
            self.world.add_agent(new_agent)
            self.world.log_event(f"New arrival! Agent {len(self.world.agents)}")
    
    def check_deaths(self):
        """Log deaths"""
        pass  # Handled in world.update
    
    def get_stats(self):
        """Get civilization stats"""
        alive = [a for a in self.world.agents if a.alive]
        
        if not alive:
            return {'population': 0}
        
        # Calculate averages
        avg_happiness = sum(a.needs['happiness'] for a in alive) / len(alive)
        avg_food = sum(a.inventory.get('food', 0) for a in alive) / len(alive)
        
        # Job distribution
        jobs = {}
        for agent in alive:
            jobs[agent.job] = jobs.get(agent.job, 0) + 1
        
        # Top skills
        all_skills = {}
        for agent in alive:
            for skill, value in agent.skills.items():
                all_skills[skill] = all_skills.get(skill, 0) + value
        
        return {
            'generation': self.generation,
            'population': len(alive),
            'avg_happiness': avg_happiness,
            'avg_food': avg_food,
            'jobs': jobs,
            'total_jobs_done': sum(a.jobs_done for a in alive),
            'top_skills': sorted(all_skills.items(), key=lambda x: x[1], reverse=True)[:5]
        }
