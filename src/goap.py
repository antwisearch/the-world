"""
GOAP - Goal-Oriented Action Planning for agents
"""

import random
from collections import deque
from typing import List, Dict, Optional, Tuple


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


class AgentMemory:
    """Agent's memory of past events and decisions"""
    
    def __init__(self, max_size=50):
        self.memories = deque(maxlen=max_size)
        self.learned_paths = {}  # Location -> successful actions
        self.failed_plans = []  # Plans that didn't work
        self.successful_goals = []  # Goals that were achieved
    
    def add_memory(self, event: str, location: Tuple[int, int] = None):
        """Add an event to memory"""
        self.memories.append({
            'event': event,
            'location': location,
            'time': len(self.memories)
        })
    
    def remember_location(self, location: Tuple[int, int], result: str):
        """Remember outcome from a location"""
        loc_str = f"{location[0]},{location[1]}"
        if loc_str not in self.learned_paths:
            self.learned_paths[loc_str] = []
        self.learned_paths[loc_str].append(result)
    
    def get_best_location(self, resource_type: str) -> Optional[Tuple[int, int]]:
        """Get best known location for a resource"""
        # Simple implementation - could be enhanced
        for loc_str, results in self.learned_paths.items():
            if resource_type in str(results):
                x, y = loc_str.split(',')
                return (int(x), int(y))
        return None
    
    def learn_from_failure(self, plan: List[str], reason: str):
        """Learn from a failed plan"""
        self.failed_plans.append({
            'plan': plan,
            'reason': reason,
            'attempts': 1
        })
    
    def learn_from_success(self, plan: List[str], goal: str):
        """Learn from a successful plan"""
        self.successful_goals.append({
            'plan': plan,
            'goal': goal,
            'effectiveness': 1.0
        })


class ImprovedGOAPAgent:
    """Enhanced GOAP agent with learning"""
    
    def __init__(self, agent, world):
        self.agent = agent
        self.world = world
        self.actions = self._get_available_actions()
        self.memory = AgentMemory()
        self.current_plan = []
        self.plan_success_rate = 0.5
    
    def _get_available_actions(self):
        """Get actions available to this agent"""
        return [
            GOAPAction("find_food", {}, {'food': 10}, cost=3),
            GOAPAction("find_wood", {}, {'wood': 5}, cost=2),
            GOAPAction("find_stone", {}, {'stone': 5}, cost=3),
            GOAPAction("find_ore", {}, {'ore': 3}, cost=5),
            GOAPAction("rest", {'energy': 50}, {'energy': 30, 'happiness': 5}, cost=2),
            GOAPAction("build_shelter", {'wood': 10}, {'shelter': 1}, cost=5),
            GOAPAction("trade", {'gold': 10}, {'items': 1}, cost=2),
            GOAPAction("heal", {'herbs': 1}, {'health': 20}, cost=2),
        ]
    
    def get_current_state(self) -> Dict:
        """Get current world state from agent"""
        return {
            'food': self.agent.needs.get('food', 0),
            'water': self.agent.needs.get('water', 0),
            'happiness': self.agent.needs.get('happiness', 0),
            'shelter': self.agent.needs.get('shelter', 0),
            'energy': self.agent.needs.get('energy', 100),
            'health': getattr(self.agent, 'health', 100),
            'gold': self.agent.wealth,
            'wood': self.agent.inventory.get('wood', 0),
            'stone': self.agent.inventory.get('stone', 0),
        }
    
    def get_goal(self) -> Dict:
        """Determine current goal based on needs"""
        needs = self.agent.needs
        
        # Priority: survival first
        if needs.get('food', 0) < 20:
            return {'food': 50, 'priority': 10}
        if needs.get('water', 0) < 20:
            return {'water': 50, 'priority': 10}
        if needs.get('happiness', 0) < 20:
            return {'happiness': 50, 'priority': 5}
        
        # Then comfort
        if needs.get('shelter', 0) < 30:
            return {'shelter': 50, 'priority': 3}
        
        # Then wealth building
        return {'gold': 50, 'priority': 1}
    
    def plan(self) -> List[GOAPAction]:
        """Create a plan to achieve goal using A* search"""
        goal = self.get_goal()
        start_state = self.get_current_state()
        
        # Simple greedy approach with look-ahead
        plan = []
        current_state = start_state.copy()
        
        for _ in range(5):  # Max 5 actions in plan
            best_action = None
            best_score = -float('inf')
            
            for action in self.actions:
                if action.is_valid(current_state):
                    # Score based on goal relevance + efficiency
                    score = self._score_action(action, goal, current_state)
                    if score > best_score:
                        best_score = score
                        best_action = action
            
            if best_action:
                plan.append(best_action)
                current_state = best_action.apply(current_state)
                
                # Check if goal reached
                if self._goal_reached(current_state, goal):
                    break
            else:
                break
        
        self.current_plan = plan
        return plan
    
    def _score_action(self, action: GOAPAction, goal: Dict, state: Dict) -> float:
        """Score an action based on how well it meets the goal"""
        score = 0
        
        # Does this action help with the goal?
        for key, target in goal.items():
            if key in action.effects:
                current = state.get(key, 0)
                needed = target - current
                if needed > 0:
                    score += min(needed, action.effects[key]) * goal.get('priority', 1)
        
        # Efficiency: lower cost = better
        score -= action.cost
        
        # Bonus for learned successful actions
        if action.name in [m.get('event', '') for m in list(self.memory.memories)[-10:]]:
            score *= 1.2
        
        return score
    
    def _goal_reached(self, state: Dict, goal: Dict) -> bool:
        """Check if goal is reached"""
        for key, target in goal.items():
            if key in ['priority']:
                continue
            if state.get(key, 0) < target:
                return False
        return True
    
    def execute_plan(self) -> str:
        """Execute the current plan"""
        if not self.current_plan:
            self.plan()
        
        if not self.current_plan:
            return "No plan possible"
        
        action = self.current_plan.pop(0)
        
        # Execute action
        result = self._execute_action(action)
        
        # Learn from result
        if result:
            self.memory.add_memory(f"executed {action.name}", (self.agent.x, self.agent.y))
            self.plan_success_rate = min(1.0, self.plan_success_rate + 0.05)
        else:
            self.memory.learn_from_failure([action.name], "action failed")
            self.plan_success_rate = max(0.1, self.plan_success_rate - 0.1)
        
        return result
    
    def _execute_action(self, action: GOAPAction) -> bool:
        """Execute a single action"""
        if action.name == "find_food":
            # Look for food
            from src.resources import spawn_resource
            self.agent.inventory['food'] = self.agent.inventory.get('food', 0) + action.effects.get('food', 0)
            return True
        
        elif action.name == "find_wood":
            self.agent.inventory['wood'] = self.agent.inventory.get('wood', 0) + action.effects.get('wood', 0)
            return True
        
        elif action.name == "rest":
            self.agent.needs['happiness'] = min(100, self.agent.needs.get('happiness', 0) + action.effects.get('happiness', 0))
            return True
        
        # Default: assume success
        return True


# Keep original for compatibility
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
