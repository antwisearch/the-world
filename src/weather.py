"""
Weather system - tied to seasons
"""

import random

class Weather:
    """Weather types"""
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    SNOW = "snow"
    STORM = "storm"


class WeatherManager:
    """Manage weather based on season"""
    
    def __init__(self):
        self.weather = Weather.CLEAR
        self.intensity = 0.5
    
    def update(self, season):
        """Update weather based on season"""
        from src.seasons import Season
        
        weather_chances = {
            Season.SPRING: {Weather.CLEAR: 0.4, Weather.CLOUDY: 0.3, Weather.RAIN: 0.3},
            Season.SUMMER: {Weather.CLEAR: 0.6, Weather.CLOUDY: 0.3, Weather.RAIN: 0.1},
            Season.AUTUMN: {Weather.CLOUDY: 0.4, Weather.RAIN: 0.4, Weather.STORM: 0.2},
            Season.WINTER: {Weather.CLOUDY: 0.3, Weather.SNOW: 0.5, Weather.CLEAR: 0.2},
        }
        
        chances = weather_chances.get(season, weather_chances[Season.SPRING])
        r = random.random()
        cumulative = 0
        for w, chance in chances.items():
            cumulative += chance
            if r < cumulative:
                self.weather = w
                break
        
        self.intensity = random.uniform(0.3, 0.8)
    
    def get_effects(self):
        """Get weather effects on agents"""
        effects = {
            'happiness': 0,
            'food_growth': 1.0,
            'movement': 1.0
        }
        
        if self.weather == Weather.RAIN:
            effects['happiness'] = 5
            effects['food_growth'] = 1.2
        elif self.weather == Weather.SNOW:
            effects['happiness'] = -10
            effects['food_growth'] = 0.5
            effects['movement'] = 0.7
        elif self.weather == Weather.STORM:
            effects['happiness'] = -15
            effects['movement'] = 0.5
        elif self.weather == Weather.CLEAR:
            effects['happiness'] = 10
        
        return effects
    
    def to_dict(self):
        return {
            'weather': self.weather,
            'intensity': self.intensity,
            'effects': self.get_effects()
        }
