"""
A* Pathfinding for agents
"""

import math
import heapq

class PathNode:
    """Node for A* pathfinding"""
    
    def __init__(self, x, y, parent=None):
        self.x = x
        self.y = y
        self.parent = parent
        self.g = 0  # Cost from start
        self.h = 0  # Heuristic to end
        self.f = 0  # Total cost
    
    def __lt__(self, other):
        return self.f < other.f
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))


class Pathfinder:
    """A* pathfinding implementation"""
    
    def __init__(self, world):
        self.world = world
        self.width = world.width
        self.height = world.height
    
    def heuristic(self, a, b):
        """Manhattan distance heuristic"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def get_neighbors(self, node):
        """Get valid neighbors"""
        neighbors = []
        directions = [
            (0, 1), (0, -1), (1, 0), (-1, 0),  # Cardinal
            (1, 1), (1, -1), (-1, 1), (-1, -1)  # Diagonal
        ]
        
        for dx, dy in directions:
            nx, ny = node.x + dx, node.y + dy
            
            # Check bounds
            if 0 <= nx < self.width and 0 <= ny < self.height:
                # Check for obstacles (simplified - check water)
                if not self._is_obstacle(nx, ny):
                    neighbors.append((nx, ny))
        
        return neighbors
    
    def _is_obstacle(self, x, y):
        """Check if position is an obstacle"""
        # Check water sources
        for water in self.world.water_sources:
            dist = math.sqrt((water['x'] - x)**2 + (water['y'] - y)**2)
            if dist < water.get('radius', 30):
                return True
        return False
    
    def find_path(self, start_x, start_y, end_x, end_y, max_steps=1000):
        """Find path from start to end"""
        start = PathNode(start_x, start_y)
        end = (end_x, end_y)
        
        open_set = [start]
        closed_set = set()
        
        iterations = 0
        
        while open_set and iterations < max_steps:
            iterations += 1
            
            # Get node with lowest f score
            current = heapq.heappop(open_set)
            
            # Check if reached goal
            if (abs(current.x - end_x) < 5 and abs(current.y - end_y) < 5):
                return self._reconstruct_path(current)
            
            # Add to closed set
            closed_set.add((current.x, current.y))
            
            # Check neighbors
            for nx, ny in self.get_neighbors(current):
                if (nx, ny) in closed_set:
                    continue
                
                # Calculate costs
                dx = abs(nx - current.x)
                dy = abs(ny - current.y)
                move_cost = 1.414 if (dx + dy) == 2 else 1  # Diagonal is longer
                
                g = current.g + move_cost
                h = self.heuristic((nx, ny), end)
                f = g + h
                
                # Check if already in open set
                existing = None
                for node in open_set:
                    if node.x == nx and node.y == ny:
                        existing = node
                        break
                
                if existing is None or g < existing.g:
                    new_node = PathNode(nx, ny, current)
                    new_node.g = g
                    new_node.h = h
                    new_node.f = f
                    
                    if existing:
                        open_set.remove(existing)
                    
                    heapq.heappush(open_set, new_node)
        
        # No path found
        return None
    
    def _reconstruct_path(self, node):
        """Reconstruct path from end to start"""
        path = []
        current = node
        
        while current:
            path.append((current.x, current.y))
            current = current.parent
        
        return list(reversed(path))


def find_path_to_resource(agent, world, resource_type):
    """Helper to find path to a specific resource type"""
    pathfinder = Pathfinder(world)
    
    # Find nearest resource of type
    nearest = None
    nearest_dist = float('inf')
    
    for resource in world.resources:
        if resource.get('type') == resource_type:
            dist = math.sqrt((resource['x'] - agent.x)**2 + (resource['y'] - agent.y)**2)
            if dist < nearest_dist:
                nearest_dist = dist
                nearest = resource
    
    if nearest:
        return pathfinder.find_path(agent.x, agent.y, nearest['x'], nearest['y'])
    
    return None
