"""
Procedural Generation - Noise functions and terrain
"""

import random
import math

# Permutation table for Perlin noise
_permutation = list(range(256))
random.shuffle(_permutation)
_permutation = _permutation * 2


def _fade(t):
    """Fade function for smooth interpolation"""
    return t * t * t * (t * (t * 6 - 15) + 10)


def _lerp(a, b, t):
    """Linear interpolation"""
    return a + t * (b - a)


def _grad(hash_val, x, y):
    """Calculate gradient"""
    h = hash_val & 3
    if h == 0: return x + y
    if h == 1: return -x + y
    if h == 2: return x - y
    return -x - y


def perlin(x, y):
    """2D Perlin noise"""
    # Find unit grid cell
    xi = int(x) & 255
    yi = int(y) & 255
    
    # Relative position in cell
    xf = x - int(x)
    yf = y - int(y)
    
    # Fade curves
    u = _fade(xf)
    v = _fade(yf)
    
    # Hash coordinates
    aa = _permutation[_permutation[xi] + yi]
    ab = _permutation[_permutation[xi] + yi + 1]
    ba = _permutation[_permutation[xi + 1] + yi]
    bb = _permutation[_permutation[xi + 1] + yi + 1]
    
    # Interpolate
    x1 = _lerp(_grad(aa, xf, yf), _grad(ba, xf - 1, yf), u)
    x2 = _lerp(_grad(ab, xf, yf - 1), _grad(bb, xf - 1, yf - 1), u)
    
    return _lerp(x1, x2, v)


def fbm(x, y, octaves=4):
    """Fractal Brownian Motion - layered noise"""
    value = 0
    amplitude = 1
    frequency = 1
    max_value = 0
    
    for _ in range(octaves):
        value += amplitude * perlin(x * frequency, y * frequency)
        max_value += amplitude
        amplitude *= 0.5
        frequency *= 2
    
    return value / max_value


class Biome:
    """Biome types based on temperature and rainfall"""
    
    DESERT = 'desert'
    GRASSLAND = 'grassland'
    FOREST = 'forest'
    JUNGLE = 'jungle'
    TUNDRA = 'tundra'
    SNOW = 'snow'
    SWAMP = 'swamp'
    SAVANNA = 'savanna'
    
    @classmethod
    def get(cls, temp, rainfall):
        """Get biome from temperature and rainfall (0-1)"""
        if temp < 0.3:
            return cls.SNOW if rainfall < 0.4 else cls.TUNDRA
        elif temp < 0.5:
            return cls.TUNDRA if rainfall < 0.3 else cls.FOREST
        elif temp < 0.7:
            if rainfall < 0.3: return cls.GRASSLAND
            if rainfall < 0.6: return cls.FOREST
            return cls.SWAMP
        else:
            if rainfall < 0.3: return cls.DESERT
            if rainfall < 0.5: return cls.GRASSLAND
            if rainfall < 0.7: return cls.SAVANNA
            return cls.JUNGLE


class TerrainGenerator:
    """Generate terrain using noise"""
    
    def __init__(self, width, height, seed=None):
        self.width = width
        self.height = height
        if seed is not None:
            random.seed(seed)
            # Generate permutation table
            global _permutation
            _permutation = list(range(256))
            random.shuffle(_permutation)
            _permutation = _permutation * 2
    
    def generate_temperature(self, x, y):
        """Generate temperature at position (latitude-based + noise)"""
        # Latitude: colder at top
        base_temp = 1.0 - (y / self.height)
        # Add noise variation
        noise = fbm(x * 0.01, y * 0.01, 3)
        return max(0, min(1, base_temp * 0.7 + noise * 0.3 + 0.15))
    
    def generate_rainfall(self, x, y):
        """Generate rainfall at position"""
        noise = fbm(x * 0.01 + 100, y * 0.01 + 100, 3)
        return max(0, min(1, noise * 0.5 + 0.25))
    
    def generate_elevation(self, x, y):
        """Generate elevation at position"""
        # Base continent shape
        elevation = fbm(x * 0.005, y * 0.005, 4)
        # Add detail
        elevation += fbm(x * 0.02, y * 0.02, 2) * 0.2
        return (elevation + 1) / 2  # Normalize to 0-1
    
    def get_biome_at(self, x, y):
        """Get biome at position"""
        temp = self.generate_temperature(x, y)
        rainfall = self.generate_rainfall(x, y)
        return Biome.get(temp, rainfall)
    
    def get_terrain_type(self, x, y):
        """Get terrain type (water, land, mountain)"""
        elevation = self.generate_elevation(x, y)
        
        if elevation < 0.3:
            return 'deep_water'
        elif elevation < 0.4:
            return 'water'
        elif elevation < 0.45:
            return 'sand'
        elif elevation < 0.7:
            return 'grass'
        elif elevation < 0.85:
            return 'rock'
        else:
            return 'mountain'
    
    def generate_world_map(self):
        """Generate full world map"""
        biome_map = []
        terrain_map = []
        
        for y in range(0, self.height, 10):  # Sample every 10 pixels
            biome_row = []
            terrain_row = []
            for x in range(0, self.width, 10):
                biome_row.append(self.get_biome_at(x, y))
                terrain_row.append(self.get_terrain_type(x, y))
            biome_map.append(biome_row)
            terrain_map.append(terrain_row)
        
        return biome_map, terrain_map


# Cellular Automata for caves
class CaveGenerator:
    """Generate caves using cellular automata"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def generate(self, fill_prob=0.45, iterations=5):
        """Generate cave system"""
        # Initialize random grid
        grid = [[random.random() < fill_prob for _ in range(self.width)] 
                for _ in range(self.height)]
        
        # Apply cellular automata rules
        for _ in range(iterations):
            grid = self._smooth(grid)
        
        return grid
    
    def _smooth(self, grid):
        """Smooth the grid"""
        new_grid = [[False] * self.width for _ in range(self.height)]
        
        for y in range(self.height):
            for x in range(self.width):
                neighbors = self._count_neighbors(grid, x, y)
                
                if neighbors > 4:
                    new_grid[y][x] = True
                elif neighbors < 4:
                    new_grid[y][x] = False
                else:
                    new_grid[y][x] = grid[y][x]
        
        return new_grid
    
    def _count_neighbors(self, grid, x, y):
        """Count wall neighbors"""
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if grid[ny][nx]:
                        count += 1
        return count
