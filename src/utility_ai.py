"""
Utility AI - Score-based decision making for agents
"""

class UtilityScore:
    """Calculate utility scores for different actions"""
    
    @staticmethod
    def score_needs(agent):
        """Score needs - lower is more urgent"""
        return {
            'food': max(0, 100 - agent.needs['food']),
            'water': max(0, 100 - agent.needs['water']),
            'shelter': max(0, 100 - agent.needs['shelter']),
            'happiness': max(0, 100 - agent.needs['happiness']),
            'rest': max(0, 100 - agent.needs.get('energy', 50))
        }
    
    @staticmethod
    def score_job_benefit(agent, job_type):
        """How beneficial is this job?"""
        skill = agent.skills.get(job_type, 10)
        return skill * 2  # Higher skill = more benefit
    
    @staticmethod
    def get_best_action(agent):
        """Get the best action based on utility scores"""
        # Score needs
        needs = UtilityScore.score_needs(agent)
        
        # Find most urgent need
        urgent_need = max(needs, key=needs.get)
        urgent_score = needs[urgent_need]
        
        # Decision thresholds
        CRITICAL = 80
        IMPORTANT = 50
        MODERATE = 30
        
        if urgent_score >= CRITICAL:
            return urgent_need, urgent_score
        
        return 'job', 20


class BehaviorTree:
    """Simple behavior tree for agents"""
    
    @staticmethod
    def evaluate(agent, world):
        """Evaluate agent behavior"""
        # Priority 1: Critical needs
        if agent.needs['food'] < 20:
            return 'find_food', 'critical'
        
        if agent.needs['water'] < 20:
            return 'find_water', 'critical'
        
        # Priority 2: Low happiness from no shelter
        if agent.needs['shelter'] < 20 and not agent.home:
            return 'build_shelter', 'important'
        
        # Priority 3: Do job
        return 'do_job', 'normal'
    
    @staticmethod
    def get_job_priority(agent):
        """Get which job to do based on needs"""
        needs = agent.needs
        
        # If low on food, gathering/hunting is priority
        if needs['food'] < 40:
            return 'gatherer'
        
        # If no home, building is priority
        if not agent.home and needs['shelter'] < 40:
            return 'builder'
        
        # Otherwise use assigned job
        return agent.job
