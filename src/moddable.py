"""
Modding Support for The World
- JSON-based config for new biomes/items
- Scriptable events
- Easy extensibility
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


# Default mod directories
MODS_DIR = Path("mods")
CONFIG_DIR = Path("config")


@dataclass
class ModInfo:
    """Information about a mod"""
    id: str
    name: str
    version: str
    author: str
    description: str
    enabled: bool = True
    
    def to_dict(self):
        return asdict(self)


class ModLoader:
    """Loads and manages mods"""
    
    def __init__(self, mods_path: str = "mods"):
        self.mods_path = Path(mods_path)
        self.mods: Dict[str, ModInfo] = {}
        self.loaded_mods: Dict[str, Dict] = {}
        
    def discover_mods(self) -> List[ModInfo]:
        """Discover available mods"""
        mods = []
        if not self.mods_path.exists():
            self.mods_path.mkdir(parents=True, exist_ok=True)
            return mods
        
        for mod_dir in self.mods_path.iterdir():
            if mod_dir.is_dir():
                mod_json = mod_dir / "mod.json"
                if mod_json.exists():
                    try:
                        with open(mod_json) as f:
                            data = json.load(f)
                            mod = ModInfo(
                                id=data.get('id', mod_dir.name),
                                name=data.get('name', mod_dir.name),
                                version=data.get('version', '1.0.0'),
                                author=data.get('author', 'Unknown'),
                                description=data.get('description', ''),
                            )
                            mods.append(mod)
                            self.mods[mod.id] = mod
                    except Exception as e:
                        print(f"Error loading mod {mod_dir}: {e}")
        
        return mods
    
    def load_mod(self, mod_id: str) -> bool:
        """Load a specific mod"""
        if mod_id not in self.mods:
            return False
        
        mod_dir = self.mods_path / mod_id
        mod_config = mod_dir / "mod.json"
        
        try:
            with open(mod_config) as f:
                data = json.load(f)
                self.loaded_mods[mod_id] = data
                return True
        except Exception as e:
            print(f"Error loading mod {mod_id}: {e}")
            return False
    
    def unload_mod(self, mod_id: str) -> bool:
        """Unload a mod"""
        if mod_id in self.loaded_mods:
            del self.loaded_mods[mod_id]
            return True
        return False
    
    def get_mod_data(self, mod_id: str) -> Optional[Dict]:
        """Get loaded mod data"""
        return self.loaded_mods.get(mod_id)
    
    def apply_mod_biomes(self) -> Dict[str, Any]:
        """Apply biome mods"""
        biomes = {}
        for mod_id, mod_data in self.loaded_mods.items():
            if 'biomes' in mod_data:
                biomes.update(mod_data['biomes'])
        return biomes
    
    def apply_mod_items(self) -> Dict[str, Any]:
        """Apply item mods"""
        items = {}
        for mod_id, mod_data in self.loaded_mods.items():
            if 'items' in mod_data:
                items.update(mod_data['items'])
        return items
    
    def apply_mod_events(self) -> List[Dict]:
        """Apply event mods"""
        events = []
        for mod_id, mod_data in self.loaded_mods.items():
            if 'events' in mod_data:
                events.extend(mod_data['events'])
        return events


class ConfigManager:
    """Manages JSON configuration"""
    
    def __init__(self, config_path: str = "config"):
        self.config_path = Path(config_path)
        self.config: Dict = {}
        
        if not self.config_path.exists():
            self.config_path.mkdir(parents=True, exist_ok=True)
            self._create_default_configs()
    
    def _create_default_configs(self):
        """Create default config files"""
        # World config
        world_config = {
            "world": {
                "width": 1200,
                "height": 800,
                "seed": "random"
            },
            "simulation": {
                "tick_rate": 1.0,
                "event_chance": 0.001,
                "population_cap": 50
            },
            "difficulty": {
                "resource_spawn_rate": 1.0,
                "disease_chance": 0.01,
                "raid_frequency": 0.001
            }
        }
        self.save_config("world", world_config)
        
        # Jobs config
        jobs_config = {
            "jobs": {
                "farmer": {"base_skill": 20, "xp_multiplier": 1.0},
                "hunter": {"base_skill": 20, "xp_multiplier": 1.0},
                "builder": {"base_skill": 15, "xp_multiplier": 1.2},
                "miner": {"base_skill": 15, "xp_multiplier": 1.2},
                "trader": {"base_skill": 25, "xp_multiplier": 1.0},
                "healer": {"base_skill": 20, "xp_multiplier": 1.1}
            }
        }
        self.save_config("jobs", jobs_config)
    
    def load_config(self, name: str) -> Dict:
        """Load a config file"""
        config_file = self.config_path / f"{name}.json"
        
        if config_file.exists():
            with open(config_file) as f:
                return json.load(f)
        return {}
    
    def save_config(self, name: str, config: Dict):
        """Save a config file"""
        config_file = self.config_path / f"{name}.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default


def create_mod_template(mod_id: str, name: str, author: str = "Anonymous"):
    """Create a mod template directory"""
    mod_dir = MODS_DIR / mod_id
    mod_dir.mkdir(parents=True, exist_ok=True)
    
    # Create mod.json
    mod_json = {
        "id": mod_id,
        "name": name,
        "version": "1.0.0",
        "author": author,
        "description": f"{name} mod for The World",
        "biomes": {},
        "items": {},
        "events": [],
        "jobs": {}
    }
    
    with open(mod_dir / "mod.json", 'w') as f:
        json.dump(mod_json, f, indent=2)
    
    # Create readme
    readme = f"""# {name} Mod

## Description
{mod_json['description']}

## Installation
Place this folder in the `mods/` directory.

## Customization
Edit `mod.json` to add:
- New biomes
- Custom items
- Scriptable events
- New jobs
"""
    
    with open(mod_dir / "README.md", 'w') as f:
        f.write(readme)
    
    print(f"Created mod template: {mod_dir}")
    return mod_dir


# Global instances
mod_loader = ModLoader()
config_manager = ConfigManager()
