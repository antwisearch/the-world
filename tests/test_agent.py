"""
Test agent behavior
"""

import sys
sys.path.insert(0, '.')

from src.agent import Agent


class TestAgentCreation:
    """Test agent initialization"""
    
    def test_agent_created_with_defaults(self):
        agent = Agent(100, 100)
        assert agent.x == 100
        assert agent.y == 100
        assert agent.alive is True
        assert agent.generation == 1
    
    def test_agent_has_needs(self):
        agent = Agent(100, 100)
        assert 'food' in agent.needs
        assert 'water' in agent.needs
        assert 'shelter' in agent.needs
        assert 'happiness' in agent.needs
        assert agent.needs['food'] == 80  # Initial value
        assert agent.needs['water'] == 80
    
    def test_agent_has_job(self):
        agent = Agent(100, 100)
        assert agent.job is not None
        assert isinstance(agent.job, str)
    
    def test_agent_has_skills(self):
        agent = Agent(100, 100)
        assert 'gathering' in agent.skills
        assert 'building' in agent.skills
        assert 'farming' in agent.skills
        assert 'combat' in agent.skills
        assert 'teaching' in agent.skills
        assert 'healing' in agent.skills
        assert 'research' in agent.skills
        assert 'diplomacy' in agent.skills
    
    def test_agent_has_inventory(self):
        agent = Agent(100, 100)
        assert 'food' in agent.inventory
        assert 'wood' in agent.inventory
        assert 'stone' in agent.inventory
        assert 'ore' in agent.inventory
        assert 'herbs' in agent.inventory
    
    def test_agent_has_genome(self):
        agent = Agent(100, 100)
        assert agent.genome is not None
        assert 'body_size' in agent.genome
        assert 'metabolism' in agent.genome
        assert 0.8 <= agent.genome['body_size'] <= 1.5


class TestAgentNeeds:
    """Test agent needs system"""
    
    def test_needs_decrease_over_time(self):
        agent = Agent(100, 100)
        initial_food = agent.needs['food']
        initial_water = agent.needs['water']
        
        agent.update_needs(1.0)
        
        assert agent.needs['food'] < initial_food
        assert agent.needs['water'] < initial_water
    
    def test_needs_clamped_to_zero(self):
        agent = Agent(100, 100)
        agent.needs['food'] = 5
        agent.needs['water'] = 5
        
        agent.update_needs(10.0)
        
        assert agent.needs['food'] >= 0
        assert agent.needs['water'] >= 0
    
    def test_metabolism_affects_needs(self):
        agent1 = Agent(100, 100)
        agent1.genome['metabolism'] = 0.3
        
        agent2 = Agent(100, 100)
        agent2.genome['metabolism'] = 0.8
        
        food1_before = agent1.needs['food']
        food2_before = agent2.needs['food']
        
        agent1.update_needs(1.0)
        agent2.update_needs(1.0)
        
        # Higher metabolism should decrease needs more
        assert (food1_before - agent1.needs['food']) < (food2_before - agent2.needs['food'])


class TestAgentInventory:
    """Test agent inventory"""
    
    def test_add_to_inventory(self):
        agent = Agent(100, 100)
        initial_wood = agent.inventory.get('wood', 0)
        
        agent.inventory['wood'] = initial_wood + 10
        
        assert agent.inventory['wood'] == 10
    
    def test_remove_from_inventory(self):
        agent = Agent(100, 100)
        agent.inventory['food'] = 20
        agent.inventory['food'] -= 5
        
        assert agent.inventory['food'] == 15


class TestAgentJobs:
    """Test agent job assignment"""
    
    def test_valid_jobs_list(self):
        from src.jobs import JOBS
        agent = Agent(100, 100)
        
        assert agent.job in JOBS


class TestAgentState:
    """Test agent state export"""
    
    def test_get_state(self):
        agent = Agent(100, 100)
        state = agent.get_state()
        
        assert 'name' in state
        assert 'job' in state
        assert 'needs' in state
        assert 'position' in state
        assert 'skills' in state
        assert 'inventory' in state


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
