"""
Relationship System - Friends, enemies, families
"""

import random

class Relationship:
    """Relationship between two agents"""
    
    def __init__(self, agent1_id, agent2_id, relation_type):
        self.agent1_id = agent1_id
        self.agent2_id = agent2_id
        self.relation_type = relation_type  # 'family', 'friend', 'enemy', 'rival'
        self.strength = 50  # 0-100
        self.history = []
    
    def add_event(self, event_type):
        """Add interaction event"""
        self.history.append({
            'type': event_type,
            'strength_change': random.randint(-10, 10)
        })
        self.strength = max(0, min(100, self.strength + self.history[-1]['strength_change']))


class RelationshipManager:
    """Manage all agent relationships"""
    
    def __init__(self):
        self.relationships = []
        self.family_trees = {}
    
    def add_relationship(self, agent1, agent2, relation_type):
        """Add a relationship between agents"""
        rel = Relationship(
            agent1.biography.name,
            agent2.biography.name,
            relation_type
        )
        self.relationships.append(rel)
        
        # If family, update family tree
        if relation_type == 'family':
            self._update_family_tree(agent1, agent2)
        
        return rel
    
    def _update_family_tree(self, parent, child):
        """Update family tree"""
        parent_name = parent.biography.name
        child_name = child.biography.name
        
        if parent_name not in self.family_trees:
            self.family_trees[parent_name] = {'parents': [], 'children': []}
        
        self.family_trees[parent_name]['children'].append(child_name)
    
    def get_relations(self, agent_name):
        """Get all relationships for an agent"""
        return [r for r in self.relationships 
                if r.agent1_id == agent_name or r.agent2_id == agent_name]
    
    def get_family(self, agent_name):
        """Get family members"""
        return self.family_trees.get(agent_name, {}).get('children', [])
    
    def get_friends(self, agent_name):
        """Get friends"""
        return [r.agent2_id if r.agent1_id == agent_name else r.agent1_id
                for r in self.get_relations(agent_name) if r.relation_type == 'friend' and r.strength > 30]
    
    def get_enemies(self, agent_name):
        """Get enemies"""
        return [r.agent2_id if r.agent1_id == agent_name else r.agent1_id
                for r in self.get_relations(agent_name) if r.relation_type == 'enemy' and r.strength > 30]
    
    def add_interaction(self, agent1, agent2, event_type):
        """Add interaction between two agents"""
        # Find existing relationship
        for rel in self.relationships:
            if (rel.agent1_id == agent1.biography.name and rel.agent2_id == agent2.biography.name) or \
               (rel.agent1_id == agent2.biography.name and rel.agent2_id == agent1.biography.name):
                rel.add_event(event_type)
                return rel
        
        # Create new relationship
        return self.add_relationship(agent1, agent2, 'friend' if random.random() > 0.3 else 'enemy')
    
    def to_dict(self):
        return {
            'total_relationships': len(self.relationships),
            'families': len(self.family_trees)
        }
