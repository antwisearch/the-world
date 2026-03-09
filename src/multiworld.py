"""
Multi-world Support for The World
- Connect multiple servers
- Trade between worlds
- World identification and communication
"""

import random
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class WorldInfo:
    """Information about a connected world"""
    world_id: str
    name: str
    host: str
    port: int
    population: int = 0
    biome: str = "grassland"
    connected_at: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    trust_level: int = 1  # 1-5, affects trade
    
    def to_dict(self):
        return {
            'world_id': self.world_id,
            'name': self.name,
            'host': self.host,
            'port': self.port,
            'population': self.population,
            'biome': self.biome,
            'trust_level': self.trust_level,
        }


class MultiWorldManager:
    """Manages connections between multiple game worlds"""
    
    def __init__(self, world_id: str, world_name: str, host: str = "localhost", port: int = 8080):
        self.world_id = world_id
        self.world_name = world_name
        self.host = host
        self.port = port
        self.connected_worlds: Dict[str, WorldInfo] = {}
        self.pending_trades: List[Dict] = []
        
    def register_world(self, world_info: WorldInfo) -> bool:
        """Register a connected world"""
        if world_info.world_id == self.world_id:
            return False  # Can't connect to self
        
        self.connected_worlds[world_info.world_id] = world_info
        return True
    
    def unregister_world(self, world_id: str) -> bool:
        """Disconnect from a world"""
        if world_id in self.connected_worlds:
            del self.connected_worlds[world_id]
            return True
        return False
    
    def get_world(self, world_id: str) -> Optional[WorldInfo]:
        """Get info about a connected world"""
        return self.connected_worlds.get(world_id)
    
    def list_worlds(self) -> List[WorldInfo]:
        """List all connected worlds"""
        return list(self.connected_worlds.values())
    
    def update_world_status(self, world_id: str, population: int = None, biome: str = None):
        """Update a world's status"""
        if world_id in self.connected_worlds:
            world = self.connected_worlds[world_id]
            if population is not None:
                world.population = population
            if biome is not None:
                world.biome = biome
            world.last_seen = datetime.now()
    
    def initiate_trade(self, target_world_id: str, offering: Dict, requesting: Dict) -> Optional[str]:
        """Initiate trade with another world"""
        target = self.get_world(target_world_id)
        if not target:
            return None
        
        trade_id = hashlib.md5(f"{self.world_id}{target_world_id}{random.randint(0,9999)}".encode()).hexdigest()[:8]
        
        trade = {
            'trade_id': trade_id,
            'source_world': self.world_id,
            'target_world': target_world_id,
            'offering': offering,  # {item: quantity}
            'requesting': requesting,  # {item: quantity}
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
        }
        
        self.pending_trades.append(trade)
        return trade_id
    
    def accept_trade(self, trade_id: str) -> bool:
        """Accept an incoming trade"""
        for trade in self.pending_trades:
            if trade['trade_id'] == trade_id and trade['target_world'] == self.world_id:
                trade['status'] = 'accepted'
                return True
        return False
    
    def complete_trade(self, trade_id: str) -> Optional[Dict]:
        """Complete a trade"""
        for i, trade in enumerate(self.pending_trades):
            if trade['trade_id'] == trade_id:
                completed = self.pending_trades.pop(i)
                completed['status'] = 'completed'
                completed['completed_at'] = datetime.now().isoformat()
                return completed
        return None
    
    def get_trade_routes(self) -> List[Dict]:
        """Get information about possible trade routes"""
        routes = []
        for world in self.connected_worlds.values():
            # Calculate trade potential based on biomes
            biome_advantages = self._calculate_biome_advantages(world.biome)
            routes.append({
                'world_id': world.world_id,
                'name': world.name,
                'biome': world.biome,
                'population': world.population,
                'trust': world.trust_level,
                'advantages': biome_advantages,
            })
        return routes
    
    def _calculate_biome_advantages(self, biome: str) -> List[str]:
        """Calculate what a world might have based on biome"""
        advantages = {
            'grassland': ['food', 'grain', 'cloth'],
            'forest': ['wood', 'herbs', 'fur'],
            'desert': ['spices', 'gems', 'gold'],
            'jungle': ['wood', 'herbs', 'silk'],
            'mountain': ['ore', 'stone', 'gems', 'iron'],
            'tundra': ['fur', 'ice', 'ore'],
            'swamp': ['herbs', 'food'],
            'savanna': ['food', 'cloth', 'spices'],
        }
        return advantages.get(biome, [])
    
    def get_world_summary(self) -> Dict:
        """Get summary of this world for other worlds"""
        return {
            'world_id': self.world_id,
            'name': self.world_name,
            'host': self.host,
            'port': self.port,
            'features': ['combat', 'disease', 'trading', 'events'],
            'version': '0.3.0',
        }


def generate_world_id(name: str) -> str:
    """Generate a unique world ID from name"""
    timestamp = datetime.now().strftime('%Y%m%d')
    hash_input = f"{name}{timestamp}{random.randint(0,999)}".encode()
    return hashlib.md5(hash_input).hexdigest()[:12]
