"""
Biome-based resource generation
"""

from src.terrain import TerrainGenerator, Biome


# Resources that spawn in different biomes
BIOME_RESOURCES = {
    Biome.DESERT: ['cactus', 'sand', 'rare_gem'],
    Biome.GRASSLAND: ['food', 'wood', 'herbs'],
    Biome.FOREST: ['wood', 'food', 'herbs', 'mushroom'],
    Biome.JUNGLE: ['wood', 'food', 'exotic_fruit', 'herbs'],
    Biome.TUNDRA: ['ice', 'frozen_berry', 'fish'],
    Biome.SNOW: ['ice', 'frozen_berry', 'stone'],
    Biome.SWAMP: ['food', 'herbs', 'fish', 'reed'],
    Biome.SAVANNA: ['food', 'wood', 'ivory'],
}


# Resource properties
RESOURCE_PROPERTIES = {
    'food': {'edible': True, 'value': 1},
    'wood': {'buildable': True, 'value': 1},
    'stone': {'buildable': True, 'value': 2},
    'ore': {'value': 5},
    'rare_gem': {'value': 20},
    'herbs': {'value': 3},
    'mushroom': {'edible': True, 'value': 2},
    'exotic_fruit': {'edible': True, 'value': 4},
    'frozen_berry': {'edible': True, 'value': 2},
    'fish': {'edible': True, 'value': 3},
    'reed': {'value': 1},
    'cactus': {'value': 1},
    'sand': {'value': 1},
    'ice': {'value': 1},
    'ivory': {'value': 10},
}


class BiomeResourceManager:
    """Manage resources based on biomes"""
    
    def __init__(self, world):
        self.world = world
        self.terrain = TerrainGenerator(world.width, world.height)
        self.initialized_biomes = set()
    
    def spawn_biome_resources(self):
        """Spawn resources based on biomes"""
        # Initialize biomes for each agent area
        for agent in self.world.agents:
            if not hasattr(agent, '_biome_initialized'):
                biome = self.terrain.get_biome_at(agent.x, agent.y)
                agent.biome = biome
                agent._biome_initialized = True
                
                # Spawn initial resources for this biome
                if biome not in self.initialized_biomes:
                    self._spawn_biome_resources(biome)
                    self.initialized_biomes.add(biome)
    
    def _spawn_biome_resources(self, biome):
        """Spawn resources typical for a biome"""
        resources = BIOME_RESOURCES.get(biome, ['food', 'wood'])
        
        # Spawn multiple resource nodes
        for _ in range(10):
            res_type = resources[min(len(resources)-1, int(random.random() * len(resources)))]
            
            x = random.uniform(50, self.world.width - 50)
            y = random.uniform(50, self.world.height - 50)
            
            # Check biome matches
            if self.terrain.get_biome_at(x, y) == biome:
                self.world.resources.append({
                    'type': res_type,
                    'x': x,
                    'y': y,
                    'amount': random.randint(1, 10)
                })
    
    def get_biome_at(self, x, y):
        """Get biome at position"""
        return self.terrain.get_biome_at(x, y)
    
    def get_terrain_at(self, x, y):
        """Get terrain type at position"""
        return self.terrain.get_terrain_type(x, y)


# Quest system
class Quest:
    """A quest that can be given to agents"""
    
    def __init__(self, quest_type, target, reward, difficulty=1):
        self.quest_type = quest_type  # 'gather', 'build', 'rescue', 'hunt'
        self.target = target  # What to gather/build
        self.reward = reward
        self.difficulty = difficulty
        self.completed = False
        self.description = self._generate_description()
    
    def _generate_description(self):
        """Generate quest description"""
        templates = {
            'gather': f"Gather {self.target}",
            'build': f"Build a {self.target}",
            'rescue': f"Rescue {self.target}",
            'hunt': f"Hunt {self.target}",
        }
        return templates.get(self.quest_type, "Unknown quest")


class QuestGenerator:
    """Generate random quests"""
    
    QUEST_TYPES = ['gather', 'build', 'hunt']
    
    BUILDINGS = ['shelter', 'workshop', 'watchtower', 'farm']
    HUNT_TARGETS = ['deer', 'boar', 'wolf', 'bear']
    
    @staticmethod
    def generate_random():
        """Generate a random quest"""
        quest_type = random.choice(QuestGenerator.QUEST_TYPES)
        
        if quest_type == 'gather':
            target = random.choice(['food', 'wood', 'stone', 'ore'])
            reward = random.randint(10, 50)
            return Quest('gather', target, reward)
        
        elif quest_type == 'build':
            target = random.choice(QuestGenerator.BUILDINGS)
            reward = random.randint(20, 100)
            return Quest('build', target, reward)
        
        else:  # hunt
            target = random.choice(QuestGenerator.HUNT_TARGETS)
            reward = random.randint(15, 40)
            return Quest('hunt', target, reward)
    
    @staticmethod
    def assign_quest_to_agent(agent):
        """Assign a random quest to an agent"""
        quest = QuestGenerator.generate_random()
        agent.current_quest = quest
        return quest
