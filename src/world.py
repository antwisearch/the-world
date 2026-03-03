"""
The World - Co-evolution simulation
World state, climate, terrain, and era management
"""

import random
from typing import Dict, List, Tuple, Optional


class ClimateZone:
    """A zone in the world with specific climate conditions"""
    
    def __init__(self, name: str, temp: float, x_range: Tuple[float, float]):
        self.name = name
        self.temp = temp
        self.x_range = x_range
        self.humidity = random.uniform(0.3, 0.7)
        self.danger_level = 0.0
    
    def to_dict(self):
        return {
            'name': self.name,
            'temperature': self.temp,
            'x_range': self.x_range,
            'humidity': self.humidity,
            'danger_level': self.danger_level
        }


class Terrain:
    """World terrain - elevation and structures"""
    
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
        self.elevation = [[0 for _ in range(100)] for _ in range(100)]
        self.structures = []  # Agent-built
        self.water_sources = []
        
        # Generate initial terrain
        self._generate_terrain()
    
    def _generate_terrain(self):
        """Generate simple terrain with hills and valleys"""
        import noise
        import numpy as np
        
        # Use Perlin noise for natural terrain
        for x in range(100):
            for y in range(100):
                wx = x / 100.0
                wy = y / 100.0
                # Simple noise-like function
                self.elevation[x][y] = (
                    np.sin(wx * 4) * 0.3 + 
                    np.cos(wy * 3) * 0.2 +
                    np.sin(wx * wy * 2) * 0.1
                )
        
        # Add water sources
        self.water_sources = [
            {'x': 300 + random.uniform(-50, 50), 'y': 200, 'radius': 80},
            {'x': 900 + random.uniform(-50, 50), 'y': 600, 'radius': 100}
        ]
    
    def get_elevation(self, x: float, y: float) -> float:
        """Get elevation at position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            ix = int(x / self.width * 99)
            iy = int(y / self.height * 99)
            return self.elevation[ix][iy]
        return 0
    
    def add_structure(self, x: float, y: float, structure_type: str):
        """Add a structure built by an agent"""
        self.structures.append({
            'type': structure_type,
            'x': x,
            'y': y,
            'size': random.uniform(5, 15)
        })
    
    def to_dict(self):
        return {
            'elevation': self.elevation,
            'structures': self.structures,
            'water': self.water_sources
        }


class World:
    """
    The World - manages climate, terrain, era, and agent impact
    """
    
    ERAS = ['primordial', 'age_of_fire', 'ice_age', 'urban', 'ocean', 'collapse']
    
    def __init__(self, width=1200, height=800):
        self.width = width
        self.height = height
        
        # Climate
        self.global_temp = 20  # Celsius
        self.climate_zones = []
        self.weather = 'none'  # none, rain, drought, fire, flood
        self.humidity = 0.5
        
        # Initialize zones
        self._init_climate_zones()
        
        # Terrain
        self.terrain = Terrain(width, height)
        
        # Era system
        self.era = 'primordial'
        self.era_progress = 0
        
        # Agent impact tracking
        self.impact = {
            'structures_built': 0,
            'fires_started': 0,
            'water_channeled': 0,
            'terrain_modified': 0,
            'creatures_killed': 0,
            'food_created': 0
        }
        
        # Food
        self.food = []
        
        # Time
        self.time = 0
        self.day_night_cycle = 0
        
        # Spawn initial food
        for _ in range(50):
            self.spawn_food()
    
    def _init_climate_zones(self):
        """Initialize climate zones"""
        self.climate_zones = [
            ClimateZone('scorched', 45, (0, 400)),
            ClimateZone('temperate', 20, (400, 800)),
            ClimateZone('frozen', -10, (800, 1200))
        ]
    
    def get_zone_at(self, x: float) -> ClimateZone:
        """Get climate zone at x position"""
        for zone in self.climate_zones:
            if zone.x_range[0] <= x <= zone.x_range[1]:
                return zone
        return self.climate_zones[1]  # Default to temperate
    
    def get_weather_at(self, x: float, y: float) -> str:
        """Get weather at position (influenced by terrain/climate)"""
        zone = self.get_zone_at(x)
        
        # Fire zone has fire weather
        if zone.name == 'scorched' and self.weather != 'rain':
            if random.random() < 0.001:  # Spontaneous fire
                return 'fire'
        
        return self.weather
    
    def update(self, agents: List, dt: float):
        """Update world based on agent actions and time"""
        self.time += dt
        self.day_night_cycle = (self.day_night_cycle + dt / 10) % 1
        
        # Update climate zones based on era
        self._update_climate()
        
        # Check for era transitions
        self._check_era_transition()
        
        # Random weather events
        self._update_weather()
    
    def _update_climate(self):
        """Update climate based on era"""
        base_temps = {
            'primordial': 25,
            'age_of_fire': 40,
            'ice_age': -15,
            'urban': 22,
            'ocean': 18,
            'collapse': 35
        }
        
        target_temp = base_temps.get(self.era, 20)
        self.global_temp += (target_temp - self.global_temp) * 0.01
        
        # Update zone temperatures
        for zone in self.climate_zones:
            if zone.name == 'scorched':
                zone.temp = self.global_temp + random.uniform(10, 20)
            elif zone.name == 'frozen':
                zone.temp = self.global_temp - random.uniform(5, 15)
            else:
                zone.temp = self.global_temp + random.uniform(-5, 5)
    
    def _check_era_transition(self):
        """Check if we should transition to a new era"""
        fires = self.impact['fires_started']
        structures = self.impact['structures_built']
        
        if self.era == 'primordial':
            if fires > 50:
                self.era = 'age_of_fire'
                print(f"\n🌍 ERA CHANGE: PRIMORDIAL → AGE OF FIRE")
        
        elif self.era == 'age_of_fire':
            if fires > 200:
                self.era = 'collapse'
                print(f"\n🌍 ERA CHANGE: AGE OF FIRE → COLLAPSE")
            elif self.global_temp < 5:
                self.era = 'ice_age'
                print(f"\n🌍 ERA CHANGE: AGE OF FIRE → ICE AGE")
        
        elif self.era == 'ice_age':
            if self.global_temp > 10:
                self.era = 'primordial'
                print(f"\n🌍 ERA CHANGE: ICE AGE → PRIMORDIAL")
        
        elif self.era == 'urban':
            if fires > 150:
                self.era = 'collapse'
                print(f"\n🌍 ERA CHANGE: URBAN → COLLAPSE")
    
    def _update_weather(self):
        """Random weather events"""
        if random.random() < 0.0001:  # Very rare
            self.weather = random.choice(['rain', 'drought', 'flood'])
        
        # Clear weather after a while
        if self.weather != 'none' and random.random() < 0.001:
            self.weather = 'none'
        
        # Fire spreads in hot zones
        if self.global_temp > 30 and self.weather != 'rain':
            if random.random() < 0.0005:
                self.weather = 'fire'
    
    def record_action(self, action_type: str):
        """Record an agent action for impact tracking"""
        if action_type in self.impact:
            self.impact[action_type] += 1
    
    def get_food_spawn_rate(self) -> float:
        """Get food spawn rate based on world state"""
        rate = 1.0
        
        # Drought reduces food
        if self.weather == 'drought':
            rate *= 0.3
        # Rain increases food
        elif self.weather == 'rain':
            rate *= 1.5
        # Fire is bad
        elif self.weather == 'fire':
            rate *= 0.5
        
        # Era effects
        if self.era == 'collapse':
            rate *= 0.4
        elif self.era == 'ice_age':
            rate *= 0.6
        
        return rate
    
    def get_temperature_at(self, x: float, y: float) -> float:
        """Get temperature at position"""
        zone = self.get_zone_at(x)
        
        # Elevation affects temp
        elevation = self.terrain.get_elevation(x, y)
        temp = zone.temp - elevation * 10
        
        # Day/night cycle
        temp += (self.day_night_cycle - 0.5) * 5
        
        return temp
    
    def spawn_food(self):
        """Spawn food based on world conditions"""
        import random
        
        # Spawn in temperate zones more often
        zone = random.choice(self.climate_zones)
        x = random.uniform(zone.x_range[0], zone.x_range[1])
        y = random.uniform(100, self.height - 100)
        
        food = {
            'x': x,
            'y': y,
            'radius': random.uniform(0.2, 0.4),
            'nutrition': random.randint(15, 30)
        }
        self.food.append(food)
    
    def to_dict(self) -> dict:
        """Get world state as dict"""
        return {
            'width': self.width,
            'height': self.height,
            'era': self.era,
            'global_temp': self.global_temp,
            'weather': self.weather,
            'humidity': self.humidity,
            'climate_zones': [z.to_dict() for z in self.climate_zones],
            'terrain': self.terrain.to_dict(),
            'impact': self.impact,
            'time': self.time
        }
