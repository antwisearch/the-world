"""
Seasons - Dynamic world changes based on seasons
"""

import random

class Season:
    """Season types"""
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"
    
    @classmethod
    def get_next(cls, current):
        """Get next season"""
        order = [cls.SPRING, cls.SUMMER, cls.AUTUMN, cls.WINTER]
        idx = order.index(current) if current in order else 0
        return order[(idx + 1) % 4]


class SeasonManager:
    """Manage seasons and their effects"""
    
    SEASON_LENGTH = 100  # Years per season
    
    def __init__(self):
        self.year = 0
        self.season = Season.SPRING
    
    def tick(self):
        """Update season"""
        self.year += 1
        if self.year % self.SEASON_LENGTH == 0:
            self.season = Season.get_next(self.season)
    
    def get_effects(self):
        """Get current season effects"""
        effects = {
            Season.SPRING: {
                'food_spawn_rate': 1.5,
                'happiness': 10,
                'description': 'Spring - time of renewal'
            },
            Season.SUMMER: {
                'food_spawn_rate': 1.2,
                'happiness': 5,
                'description': 'Summer - abundant growth'
            },
            Season.AUTUMN: {
                'food_spawn_rate': 1.0,
                'happiness': 0,
                'description': 'Autumn - harvest time'
            },
            Season.WINTER: {
                'food_spawn_rate': 0.5,
                'happiness': -10,
                'description': 'Winter - scarce resources'
            }
        }
        return effects.get(self.season, effects[Season.SPRING])
    
    def to_dict(self):
        return {
            'year': self.year,
            'season': self.season,
            'effects': self.get_effects()
        }
