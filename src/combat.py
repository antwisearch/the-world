"""
Combat System for The World
- Weapons and armor
- Combat calculations
- Agent vs agent combat
- Raids and battles
"""

import random
from dataclasses import dataclass
from typing import Optional, Dict, List


# Weapon types with damage and attributes
WEAPONS = {
    "fists": {"damage": 5, "range": "melee", "skill": "unarmed"},
    "dagger": {"damage": 10, "range": "melee", "skill": "sword"},
    "sword": {"damage": 20, "range": "melee", "skill": "sword"},
    "axe": {"damage": 25, "range": "melee", "skill": "axe"},
    "spear": {"damage": 15, "range": "melee", "skill": "spear"},
    "bow": {"damage": 20, "range": "ranged", "skill": "bow"},
    "crossbow": {"damage": 30, "range": "ranged", "skill": "bow"},
    "mace": {"damage": 22, "range": "melee", "skill": "mace"},
}

# Armor types with defense values
ARMOR = {
    "leather": {"defense": 5, "slot": "body"},
    "chainmail": {"defense": 15, "slot": "body"},
    "plate": {"defense": 25, "slot": "body"},
    "shield": {"defense": 10, "slot": "offhand"},
    "helm": {"defense": 5, "slot": "head"},
    "boots": {"defense": 3, "slot": "feet"},
}

# Full set of combat items for trading
COMBAT_ITEMS = {
    # Weapons
    "dagger": {"value": 15, "category": "weapon", "biomes": []},
    "sword": {"value": 30, "category": "weapon", "biomes": []},
    "axe": {"value": 25, "category": "weapon", "biomes": []},
    "spear": {"value": 20, "category": "weapon", "biomes": []},
    "bow": {"value": 25, "category": "weapon", "biomes": []},
    "crossbow": {"value": 40, "category": "weapon", "biomes": []},
    "mace": {"value": 28, "category": "weapon", "biomes": []},
    # Armor
    "leather_armor": {"value": 20, "category": "armor", "biomes": []},
    "chainmail": {"value": 50, "category": "armor", "biomes": []},
    "plate_armor": {"value": 100, "category": "armor", "biomes": []},
    "shield": {"value": 15, "category": "armor", "biomes": []},
    "helm": {"value": 10, "category": "armor", "biomes": []},
    "boots": {"value": 8, "category": "armor", "biomes": []},
}


@dataclass
class CombatStats:
    """Combat statistics for an agent"""
    health: float = 100.0
    max_health: float = 100.0
    weapon: Optional[str] = None
    armor: Dict[str, str] = None
    
    def __post_init__(self):
        if self.armor is None:
            self.armor = {}


def calculate_defense(armor: Dict[str, str]) -> int:
    """Calculate total defense from armor pieces"""
    total = 0
    for slot, armor_type in armor.items():
        if armor_type in ARMOR:
            total += ARMOR[armor_type]['defense']
    return total


def calculate_damage(attacker_skill: int, weapon: Optional[str], target_defense: int) -> float:
    """Calculate damage for an attack"""
    base_damage = 5  # Reduced from 10
    
    # Weapon damage
    if weapon and weapon in WEAPONS:
        base_damage = WEAPONS[weapon]['damage'] * 0.7  # Reduce weapon damage by 30%
    
    # Skill modifier (0-100 skill = 0.5x to 1.5x multiplier) - reduced from 2x
    skill_multiplier = 0.5 + (attacker_skill / 200)  # Changed from /100
    
    # Random variance (0.7 to 1.3) - more variance
    variance = random.uniform(0.7, 1.3)
    
    damage = base_damage * skill_multiplier * variance
    
    # Apply defense (reduced effectiveness)
    damage = max(1, damage - (target_defense * 0.5))  # Defense only 50% effective
    
    return round(damage, 1)


def combat_round(attacker, defender, attacker_weapon=None, defender_weapon=None) -> Dict:
    """Process a single combat round between two agents"""
    # Get defense
    defender_defense = 0
    if hasattr(defender, 'combat_stats'):
        defender_defense = calculate_defense(defender.combat_stats.armor)
    
    # Calculate damage
    attacker_skill = attacker.skills.get('combat', 10)
    damage = calculate_damage(attacker_skill, attacker_weapon, defender_defense)
    
    # Apply damage
    if hasattr(defender, 'combat_stats'):
        defender.combat_stats.health -= damage
    else:
        # Fallback: damage needs/happiness
        defender.needs['happiness'] -= damage
    
    # Gain combat skill
    attacker.skills['combat'] = min(100, attacker.skills.get('combat', 10) + 1)
    
    return {
        'damage': damage,
        'attacker_skill': attacker_skill,
        'defender_defense': defender_defense,
        'defender_alive': True
    }


def agent_attack(attacker, defender, world=None) -> str:
    """Agent initiates an attack on another agent"""
    # Get weapons
    attacker_weapon = None
    if hasattr(attacker, 'combat_stats') and attacker.combat_stats.weapon:
        attacker_weapon = attacker.combat_stats.weapon
    
    # Check distance (simple proximity check)
    dx = abs(attacker.x - defender.x)
    dy = abs(attacker.y - defender.y)
    distance = (dx**2 + dy**2) ** 0.5
    
    # Weapons have different range limits
    max_range = 5  # melee default
    if attacker_weapon and attacker_weapon in WEAPONS:
        if WEAPONS[attacker_weapon]['range'] == 'ranged':
            max_range = 50
    
    if distance > max_range:
        return f"{attacker.biography.name} is too far to attack!"
    
    # Combat round
    result = combat_round(attacker, defender, attacker_weapon)
    
    # Check if defender died
    if hasattr(defender, 'combat_stats'):
        if defender.combat_stats.health <= 0:
            defender.alive = False
            defender.biography.record_death(f"killed in combat by {attacker.biography.name}")
            if world:
                world.log_event(f"☠️ {defender.biography.name} was slain by {attacker.biography.name}!")
            return f"{attacker.biography.name} killed {defender.biography.name}!"
    
    return f"{attacker.biography.name} attacks {defender.biography.name} for {result['damage']} damage!"


def raid(world, raider_count=5):
    """Process a raid event"""
    from src.agent import Agent
    
    if not world.agents:
        return "No agents to defend!"
    
    # Spawn raiders
    raiders = []
    for i in range(raider_count):
        raider = Agent(random.randint(100, 1100), random.randint(100, 700))
        raider.job = 'raider'
        raider.combat_stats = CombatStats(
            health=80,
            weapon=random.choice(['sword', 'axe', 'bow'])
        )
        raiders.append(raider)
    
    # Get defenders
    defenders = [a for a in world.agents if a.job == 'guard'][:3]
    if not defenders:
        defenders = world.agents[:2]
    
    # Combat!
    results = []
    for raider in raiders:
        if not defenders:
            break
        defender = random.choice(defenders)
        result = agent_attack(raider, defender, world)
        results.append(result)
        
        # Remove dead raiders
        if not raider.alive:
            raiders.remove(raider)
    
    # Looting if raiders won
    if len(raiders) > len(defenders):
        loot_amount = random.randint(50, 200)
        if hasattr(world, 'economy'):
            world.economy.remove_wealth(loot_amount)
        world.log_event(f"⚔️ Raiders escaped with {loot_amount} gold!")
        results.append(f"Raiders stole {loot_amount} gold!")
    
    return " | ".join(results[:3])


def equip_weapon(agent, weapon: str) -> bool:
    """Equip a weapon to an agent"""
    if weapon not in WEAPONS:
        return False
    
    if not hasattr(agent, 'combat_stats'):
        agent.combat_stats = CombatStats()
    
    # Check if agent has the weapon
    if agent.inventory.get(weapon, 0) > 0:
        agent.combat_stats.weapon = weapon
        return True
    
    return False


def equip_armor(agent, armor_type: str, slot: str) -> bool:
    """Equip armor to an agent"""
    if armor_type not in ARMOR:
        return False
    
    if not hasattr(agent, 'combat_stats'):
        agent.combat_stats = CombatStats()
    
    # Check if agent has the armor
    if agent.inventory.get(armor_type, 0) > 0:
        agent.combat_stats.armor[slot] = armor_type
        return True
    
    return False


def craft_weapon(agent, weapon_type: str) -> bool:
    """Craft a weapon (requires materials and skill)"""
    if weapon_type not in WEAPONS:
        return False
    
    # Check materials
    materials = {
        'dagger': {'iron': 2, 'wood': 1},
        'sword': {'iron': 5, 'wood': 2},
        'axe': {'iron': 3, 'wood': 3},
        'spear': {'wood': 4},
        'bow': {'wood': 5},
        'crossbow': {'wood': 6, 'iron': 2},
        'mace': {'iron': 4, 'wood': 2},
    }
    
    required = materials.get(weapon_type, {})
    for material, amount in required.items():
        if agent.inventory.get(material, 0) < amount:
            return False
    
    # Consume materials
    for material, amount in required.items():
        agent.inventory[material] -= amount
    
    # Add weapon
    agent.inventory[weapon_type] = agent.inventory.get(weapon_type, 0) + 1
    
    # Gain crafting skill
    agent.skills['building'] = min(100, agent.skills.get('building', 10) + 2)
    
    return True


def craft_armor(agent, armor_type: str) -> bool:
    """Craft armor (requires materials and skill)"""
    materials = {
        'leather_armor': {'wood': 2, 'stone': 1},
        'chainmail': {'iron': 8},
        'plate_armor': {'iron': 15, 'stone': 5},
        'shield': {'wood': 4, 'iron': 2},
        'helm': {'iron': 3},
        'boots': {'leather': 2, 'iron': 1},
    }
    
    required = materials.get(armor_type, {})
    for material, amount in required.items():
        if agent.inventory.get(material, 0) < amount:
            return False
    
    # Consume materials
    for material, amount in required.items():
        agent.inventory[material] -= amount
    
    # Add armor
    agent.inventory[armor_type] = agent.inventory.get(armor_type, 0) + 1
    agent.skills['building'] = min(100, agent.skills.get('building', 10) + 2)
    
    return True
