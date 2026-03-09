"""
Trading System for The World
- Trader NPCs that visit
- Shops (blacksmith, general store, etc.)
- Biome-based pricing
"""

import random
import secrets
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime


# Tradeable items with base values and biome sources
ITEMS = {
    # Food (cheap in forests/farms, expensive in deserts/tundra)
    "meat": {"value": 8, "category": "food", "biomes": ["forest", "grassland", "savanna"]},
    "fish": {"value": 6, "category": "food", "biomes": ["swamp", "grassland"]},
    "fruit": {"value": 4, "category": "food", "biomes": ["forest", "jungle", "savanna"]},
    "vegetables": {"value": 4, "category": "food", "biomes": ["grassland", "savanna"]},
    "grain": {"value": 2, "category": "food", "biomes": ["grassland", "savanna"]},
    
    # Materials (cheap where abundant)
    "wood": {"value": 4, "category": "material", "biomes": ["forest", "jungle"]},
    "stone": {"value": 4, "category": "material", "biomes": ["mountain", "tundra", "desert"]},
    "iron": {"value": 12, "category": "material", "biomes": ["mountain", "tundra"]},
    "gold": {"value": 40, "category": "material", "biomes": ["mountain"]},
    "cloth": {"value": 6, "category": "material", "biomes": ["grassland", "savanna"]},
    "fur": {"value": 10, "category": "material", "biomes": ["tundra", "snow"]},
    
    # Tools/Weapons (balanced values)
    "axe": {"value": 18, "category": "tool", "biomes": ["forest"]},
    "sword": {"value": 25, "category": "weapon", "biomes": ["grassland"]},
    "pickaxe": {"value": 18, "category": "tool", "biomes": ["mountain"]},
    "spear": {"value": 12, "category": "weapon", "biomes": ["grassland", "savanna"]},
    "bow": {"value": 20, "category": "weapon", "biomes": ["forest", "jungle"]},
    
    # Luxuries (expensive everywhere)
    "jewelry": {"value": 80, "category": "luxury", "biomes": ["mountain"]},
    "wine": {"value": 20, "category": "luxury", "biomes": ["grassland"]},
    "silk": {"value": 35, "category": "luxury", "biomes": ["jungle", "savanna"]},
    "spices": {"value": 30, "category": "luxury", "biomes": ["desert", "savanna"]},
    "gems": {"value": 60, "category": "luxury", "biomes": ["mountain", "desert"]},
    
    # Medicine
    "herbs": {"value": 6, "category": "medicine", "biomes": ["forest", "jungle", "swamp"]},
    "potions": {"value": 25, "category": "medicine", "biomes": []},
    
    # Weapons (balanced)
    "dagger": {"value": 12, "category": "weapon", "biomes": []},
    "sword": {"value": 25, "category": "weapon", "biomes": []},
    "axe": {"value": 20, "category": "weapon", "biomes": []},
    "spear": {"value": 15, "category": "weapon", "biomes": []},
    "bow": {"value": 20, "category": "weapon", "biomes": []},
    "crossbow": {"value": 35, "category": "weapon", "biomes": []},
    "mace": {"value": 22, "category": "weapon", "biomes": []},
    
    # Armor (balanced)
    "leather_armor": {"value": 18, "category": "armor", "biomes": []},
    "chainmail": {"value": 40, "category": "armor", "biomes": []},
    "plate_armor": {"value": 80, "category": "armor", "biomes": []},
    "shield": {"value": 12, "category": "armor", "biomes": []},
    "helm": {"value": 8, "category": "armor", "biomes": []},
    "boots": {"value": 6, "category": "armor", "biomes": []},
}


# Shop types
SHOP_TYPES = {
    "general_store": {
        "name": "General Store",
        "sells": ["food", "material"],
        "buys": ["food", "material"],
        "markup": 1.2,
        "markdown": 0.8
    },
    "blacksmith": {
        "name": "Blacksmith",
        "sells": ["tool", "weapon", "armor"],
        "buys": ["tool", "weapon", "armor", "material"],
        "markup": 1.5,
        "markdown": 0.6
    },
    "trader": {
        "name": "Trader",
        "sells": ["luxury", "food", "material"],
        "buys": ["luxury", "food", "material"],
        "markup": 1.3,
        "markdown": 0.7
    },
    "apothecary": {
        "name": "Apothecary",
        "sells": ["medicine"],
        "buys": ["medicine", "food"],
        "markup": 1.4,
        "markdown": 0.6
    }
}


@dataclass
class Trader:
    """A wandering trader NPC"""
    id: str
    name: str
    shop_type: str
    inventory: Dict[str, int]
    gold: int
    location: Optional[tuple] = None
    arrival_day: int = 0
    stay_days: int = 3


@dataclass
class Shop:
    """A building that operates as a shop"""
    id: str
    name: str
    shop_type: str
    owner_id: Optional[str]
    inventory: Dict[str, int]
    gold: int
    x: int
    y: int


@dataclass
class TradeOffer:
    id: str
    seller: str
    seller_id: str
    items_offering: Dict[str, int]
    items_wanted: Dict[str, int]
    gold_offering: int = 0
    gold_wanted: int = 0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    expires_at: Optional[str] = None


@dataclass
class Trade:
    id: str
    buyer: str
    seller: str
    items: Dict[str, int]
    gold: int
    timestamp: str


class TradeManager:
    def __init__(self):
        self.offers: List[TradeOffer] = []
        self.trade_history: List[Trade] = []
        self.market_prices: Dict[str, float] = {}
        self.traders: List[Trader] = []
        self.shops: List[Shop] = []
        
        self._init_prices()
    
    def _init_prices(self):
        """Initialize market prices"""
        for item, data in ITEMS.items():
            self.market_prices[item] = data["value"]
    
    def get_base_price(self, item: str) -> float:
        """Get base price of an item"""
        return ITEMS.get(item, {}).get("value", 10)
    
    def get_biome_price_modifier(self, item: str, biome: str) -> float:
        """
        Get price modifier based on biome.
        Items are cheaper where they're abundant (their biome).
        """
        item_biomes = ITEMS.get(item, {}).get("biomes", [])
        
        if not item_biomes:
            return 1.0  # No modifier for items without biome
        
        if biome in item_biomes:
            return 0.6  # 40% cheaper where abundant
        else:
            return 1.4  # 40% more expensive where scarce
    
    def get_price(self, item: str, biome: str = "grassland") -> float:
        """Get adjusted price for an item in a biome"""
        base = self.market_prices.get(item, self.get_base_price(item))
        modifier = self.get_biome_price_modifier(item, biome)
        return base * modifier
    
    def update_market_prices(self, season: str = "spring"):
        """Update market prices with seasonal variation"""
        for item in self.market_prices:
            base = ITEMS[item]["value"]
            
            # Season modifier
            season_mod = 1.0
            if season == "winter":
                if ITEMS[item]["category"] == "food":
                    season_mod = 1.3  # Food expensive in winter
                elif ITEMS[item]["category"] == "material":
                    season_mod = 0.9
            elif season == "summer":
                if ITEMS[item]["category"] == "luxury":
                    season_mod = 1.2  # Luxuries sell for more in summer
            
            # Random fluctuation ±15%
            fluctuation = random.uniform(0.85, 1.15)
            
            self.market_prices[item] = base * season_mod * fluctuation
    
    def create_offer(self, seller_id: str, seller_name: str,
                     items_offering: Dict[str, int],
                     items_wanted: Dict[str, int],
                     gold_offering: int = 0, gold_wanted: int = 0) -> TradeOffer:
        offer = TradeOffer(
            id=secrets.token_hex(8),
            seller=seller_name,
            seller_id=seller_id,
            items_offering=items_offering,
            items_wanted=items_wanted,
            gold_offering=gold_offering,
            gold_wanted=gold_wanted
        )
        self.offers.append(offer)
        return offer
    
    def accept_offer(self, offer_id: str, buyer_id: str, buyer_name: str,
                     buyer_inventory: Dict[str, int], buyer_gold: int) -> Optional[Trade]:
        offer = next((o for o in self.offers if o.id == offer_id), None)
        if not offer:
            return None
        
        # Verify buyer has what offer wants
        for item, qty in offer.items_wanted.items():
            if buyer_inventory.get(item, 0) < qty:
                return None
        if buyer_gold < offer.gold_wanted:
            return None
        
        trade = Trade(
            id=secrets.token_hex(8),
            buyer=buyer_name,
            seller=offer.seller,
            items=offer.items_offering.copy(),
            gold=offer.gold_wanted
        )
        
        self.trade_history.append(trade)
        self.offers.remove(offer)
        return trade
    
    def get_available_offers(self, category: str = None) -> List[TradeOffer]:
        if category:
            filtered = []
            for offer in self.offers:
                for item in offer.items_offering:
                    if ITEMS.get(item, {}).get("category") == category:
                        filtered.append(offer)
                        break
            return filtered
        return self.offers
    
    def get_trade_history(self, limit: int = 20) -> List[Trade]:
        return self.trade_history[-limit:]
    
    # === Trader System ===
    
    def spawn_trader(self, biome: str = None) -> Trader:
        """Spawn a wandering trader"""
        if biome is None:
            biome = random.choice(["grassland", "forest", "desert", "savanna"])
        
        trader_names = [
            "Baron Freshpipes", "Mara Silkroad", "Grimjaw Caravan",
            "Solomon the Fair", "Trader Jin", "Wandering Will",
            "Merchant Mary", "Old Garrett", "Nina Fastfeet"
        ]
        
        shop_types = list(SHOP_TYPES.keys())
        shop_type = random.choice(shop_types)
        
        # Generate inventory based on shop type
        inventory = {}
        shop = SHOP_TYPES[shop_type]
        
        for cat in shop["sells"]:
            for item, data in ITEMS.items():
                if data["category"] == cat:
                    if random.random() < 0.4:  # 40% chance
                        inventory[item] = random.randint(3, 15)
        
        trader = Trader(
            id=secrets.token_hex(8),
            name=random.choice(trader_names),
            shop_type=shop_type,
            inventory=inventory,
            gold=random.randint(100, 500),
            arrival_day=0,
            stay_days=random.randint(2, 5)
        )
        
        self.traders.append(trader)
        return trader
    
    def update_traders(self, current_day: int, world) -> List[dict]:
        """Update trader status, spawn new ones, handle departures"""
        events = []
        
        # Check for departing traders
        traders_to_remove = []
        for trader in self.traders:
            if current_day - trader.arrival_day >= trader.stay_days:
                traders_to_remove.append(trader)
                events.append({
                    "type": "trader_departed",
                    "trader": trader.name,
                    "shop": SHOP_TYPES[trader.shop_type]["name"]
                })
        
        for trader in traders_to_remove:
            self.traders.remove(trader)
        
        # Spawn new traders occasionally
        if len(self.traders) < 3 and random.random() < 0.2:
            new_trader = self.spawn_trader()
            events.append({
                "type": "trader_arrived",
                "trader": new_trader.name,
                "shop": SHOP_TYPES[new_trader.shop_type]["name"],
                "inventory": len(new_trader.inventory)
            })
        
        return events
    
    def get_active_traders(self) -> List[dict]:
        """Get list of active traders"""
        result = []
        for trader in self.traders:
            result.append({
                "id": trader.id,
                "name": trader.name,
                "shop_type": trader.shop_type,
                "shop_name": SHOP_TYPES[trader.shop_type]["name"],
                "inventory": trader.inventory,
                "gold": trader.gold,
                "staying": trader.stay_days - (0 if trader.arrival_day == 0 else 1)
            })
        return result
    
    def trade_with_trader(self, trader_id: str, item: str, quantity: int, 
                          buying: bool, buyer_gold: int, buyer_inventory: Dict[str, int]) -> Optional[dict]:
        """Trade with a trader NPC"""
        trader = next((t for t in self.traders if t.id == trader_id), None)
        if not trader:
            return None
        
        item_price = int(self.get_price(item) * SHOP_TYPES[trader.shop_type]["markup"])
        
        if buying:
            # Player buying from trader
            if item not in trader.inventory or trader.inventory[item] < quantity:
                return {"error": "Trader doesn't have enough"}
            if buyer_gold < item_price * quantity:
                return {"error": "Not enough gold"}
            
            # Complete trade
            trader.inventory[item] -= quantity
            trader.gold += item_price * quantity
            
            if item not in buyer_inventory:
                buyer_inventory[item] = 0
            buyer_inventory[item] += quantity
            
            return {
                "success": True,
                "item": item,
                "quantity": quantity,
                "total": item_price * quantity,
                "buyer_gold_spent": item_price * quantity
            }
        else:
            # Player selling to trader
            sell_price = int(self.get_price(item) * SHOP_TYPES[trader.shop_type]["markdown"])
            
            if buyer_inventory.get(item, 0) < quantity:
                return {"error": "You don't have enough"}
            if trader.gold < sell_price * quantity:
                return {"error": "Trader doesn't have enough gold"}
            
            # Complete trade
            buyer_inventory[item] -= quantity
            buyer_gold -= sell_price * quantity
            
            if item not in trader.inventory:
                trader.inventory[item] = 0
            trader.inventory[item] += quantity
            trader.gold -= sell_price * quantity
            
            return {
                "success": True,
                "item": item,
                "quantity": quantity,
                "total": sell_price * quantity,
                "gold_earned": sell_price * quantity
            }
    
    # === Shop System ===
    
    def create_shop(self, name: str, shop_type: str, x: int, y: int, 
                    owner_id: str = None) -> Shop:
        """Create a shop building"""
        shop = Shop(
            id=secrets.token_hex(8),
            name=name,
            shop_type=shop_type,
            owner_id=owner_id,
            inventory={},
            gold=200,
            x=x,
            y=y
        )
        
        # Stock the shop
        for cat in SHOP_TYPES[shop_type]["sells"]:
            for item, data in ITEMS.items():
                if data["category"] == cat:
                    if random.random() < 0.5:
                        shop.inventory[item] = random.randint(5, 20)
        
        self.shops.append(shop)
        return shop
    
    def get_shops(self) -> List[dict]:
        """Get all shops"""
        return [{
            "id": s.id,
            "name": s.name,
            "shop_type": s.shop_type,
            "shop_name": SHOP_TYPES[s.shop_type]["name"],
            "inventory": s.inventory,
            "gold": s.gold,
            "x": s.x,
            "y": s.y
        } for s in self.shops]
    
    def get_shops_near(self, x: int, y: int, radius: int = 100) -> List[dict]:
        """Get shops near a location"""
        nearby = []
        for shop in self.shops:
            dist = ((shop.x - x) ** 2 + (shop.y - y) ** 2) ** 0.5
            if dist <= radius:
                nearby.append({
                    "id": shop.id,
                    "name": shop.name,
                    "shop_name": SHOP_TYPES[shop.shop_type]["name"],
                    "distance": int(dist),
                    "inventory": shop.inventory
                })
        return nearby


# Global instance
trade_manager = TradeManager()
