"""
GOAP - Goal-Oriented Action Planning for agents
"""

import random

class GOAPAction:
    """A single action that can be performed"""
    
    def __init__(self, name, preconditions, effects, cost=1):
        self.name = name
        self.preconditions = preconditions  # Dict of required world state
        self.effects = effects  # Dict of what this action achieves
        self.cost = cost
    
    def is_valid(self, state):
        """Check if action can be performed"""
        for key, value in self.preconditions.items():
            if state.get(key, 0) < value:
                return False
        return True
    
    def apply(self, state):
        """Apply action effects to state"""
        new_state = state.copy()
        for key, value in self.effects.items():
            new_state[key] = new_state.get(key, 0) + value
        return new_state


class GOAPAgent:
    """Agent that uses GOAP for planning"""
    
    def __init__(self, agent, world):
        self.agent = agent
        self.world = world
        self.actions = self._get_available_actions()
    
    def _get_available_actions(self):
        """Get actions available to this agent"""
        return [
            # Gathering actions
            GOAPAction(
                "find_food",
                preconditions={},
                effects={'food': 10},
                cost=3
            ),
            GOAPAction(
                "find_wood",
                preconditions={},
                effects={'wood': 5},
                cost=2
            ),
            GOAPAction(
                "find_stone",
                preconditions={},
                effects={'stone': 3},
                cost=4
            ),
            GOAPAction(
                "find_ore",
                preconditions={},
                effects={'ore': 1},
                cost=5
            ),
            
            # Building actions
            GOAPAction(
                "build_shelter",
                preconditions={'wood': 5},
                effects={'shelter': 1},
                cost=5
            ),
            GOAPAction(
                "build_farm",
                preconditions={'wood': 10},
                effects={'farm': 1},
                cost=8
            ),
            
            # Combat actions
            GOAPAction(
                "hunt",
                preconditions={'weapon': 1},
                effects={'food': 15, 'skill': 2},
                cost=4
            ),
            GOAPAction(
                "defend",
                preconditions={'weapon': 1},
                effects={'safety': 10, 'skill': 3},
                cost=3
            ),
            
            # Trading
            GOAPAction(
                "trade",
                preconditions={'goods': 5},
                effects={'wealth': 10},
                cost=2
            ),
        ]
    
    def get_world_state(self):
        """Get current world state from agent"""
        return {
            'food': self.agent.inventory.get('food', 0),
            'wood': self.agent.inventory.get('wood', 0),
            'stone': self.agent.inventory.get('stone', 0),
            'ore': self.agent.inventory.get('ore', 0),
            'goods': self.agent.inventory.get('goods', 0),
            'wealth': self.agent.inventory.get('wealth', 0),
            'weapon': 1 if self.agent.inventory.get('weapon') else 0,
            'shelter': 1 if self.agent.home else 0,
            'farm': 1 if hasattr(self.agent, 'farm') and self.agent.farm else 0,
        }
    
    def plan(self, goal):
        """Find sequence of actions to achieve goal"""
        start_state = self.get_world_state()
        
        # Simple BFS-like plan finding
        def find_plan(state, goal, depth=0, max_depth=5):
            if depth > max_depth:
                return []
            
            # Check if goal met
            for key, value in goal.items():
                if state.get(key, 0) < value:
                    break
            else:
                return []  # Goal achieved
            
            # Try each action
            best_plan = None
            best_cost = float('inf')
            
            for action in self.actions:
                if action.is_valid(state):
                    new_state = action.apply(state)
                    sub_plan = find_plan(new_state, goal, depth + 1, max_depth)
                    total_cost = action.cost + (len(sub_plan) * 2)
                    
                    if total_cost < best_cost:
                        best_cost = total_cost
                        best_plan = [action.name] + sub_plan
            
            return best_plan if best_plan else []
        
        return find_plan(start_state, goal)
    
    def execute_plan(self, plan):
        """Execute a plan"""
        for action_name in plan:
            # Find action and execute
            for action in self.actions:
                if action.name == action_name:
                    # Execute the action
                    self._execute_action(action)
                    break
    
    def _execute_action(self, action):
        """Execute a single action"""
        if action.name == "find_food":
            for r in self.world.resources:
                if r['type'] == 'food':
                    self.agent.move_towards(r['x'], r['y'], self.world)
                    if ((self.agent.x - r['x'])**2 + (self.agent.y - r['y'])**2) ** 0.5 < 5:
                        self.agent.inventory['food'] = self.agent.inventory.get('food', 0) + r.get('amount', 1)
                        self.world.resources.remove(r)
                        break
                        
        elif action.name == "find_wood":
            self.agent.job = 'gatherer'
            
        elif action.name == "hunt":
            self.agent.job = 'hunter'
            
        elif action.name == "build_shelter":
            self.agent.job = 'builder'
            
        elif action.name == "trade":
            self.agent.job = 'trader'


def plan_for_goal(agent, world, goal):
    """Helper to create a plan for an agent"""
    goap = GOAPAgent(agent, world)
    plan = goap.plan(goal)
    return plan
