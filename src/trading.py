"""
Trading System for The World
"""

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime


# Tradeable items with base values
ITEMS = {
    # Food
    "meat": {"value": 10, "category": "food"},
    "fish": {"value": 8, "category": "food"},
    "fruit": {"value": 5, "category": "food"},
    "vegetables": {"value": 5, "category": "food"},
    "grain": {"value": 3, "category": "food"},
    
    # Materials
    "wood": {"value": 5, "category": "material"},
    "stone": {"value": 5, "category": "material"},
    "iron": {"value": 15, "category": "material"},
    "gold": {"value": 50, "category": "material"},
    "cloth": {"value": 8, "category": "material"},
    
    # Tools/Weapons
    "axe": {"value": 20, "category": "tool"},
    "sword": {"value": 30, "category": "weapon"},
    "pickaxe": {"value": 20, "category": "tool"},
    "spear": {"value": 15, "category": "weapon"},
    
    # Luxuries
    "jewelry": {"value": 100, "category": "luxury"},
    "wine": {"value": 25, "category": "luxury"},
    "silk": {"value": 40, "category": "luxury"},
}


@dataclass
class TradeOffer:
    """A trade offer from one agent to another or to a market"""
    id: str
    seller: str  # Agent name
    seller_id: str
    items_offering: Dict[str, int]  # {item: quantity}
    items_wanted: Dict[str, int]   # {item: quantity}
    gold_offering: int = 0
    gold_wanted: int = 0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    expires_at: Optional[str] = None


@dataclass
class Trade:
    """A completed trade"""
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
        self.trader_visits: Dict[str, int] = {}  # How often traders visit
        
        # Initialize market prices with slight variation
        for item, data in ITEMS.items():
            self.market_prices[item] = data["value"]
    
    def update_market_prices(self):
        """Randomly fluctuate market prices"""
        for item in self.market_prices:
            base = ITEMS[item]["value"]
            # ±20% fluctuation
            self.market_prices[item] = base * random.uniform(0.8, 1.2)
    
    def create_offer(self, seller_id: str, seller_name: str, 
                     items_offering: Dict[str, int],
                     items_wanted: Dict[str, int],
                     gold_offering: int = 0, gold_wanted: int = 0) -> TradeOffer:
        """Create a new trade offer"""
        import secrets
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
        """Accept a trade offer"""
        offer = next((o for o in self.offers if o.id == offer_id), None)
        if not offer:
            return None
        
        # Verify buyer has what offer wants
        for item, qty in offer.items_wanted.items():
            if buyer_inventory.get(item, 0) < qty:
                return None
        if buyer_gold < offer.gold_wanted:
            return None
        
        # Complete trade
        import secrets
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
    
    def create_market_listing(self, seller_id: str, seller_name: str,
                              items: Dict[str, int], price_multiplier: float = 1.0) -> List[TradeOffer]:
        """List items on the market at current prices"""
        offers = []
        
        for item, qty in items.items():
            if item in ITEMS:
                value = int(self.market_prices.get(item, ITEMS[item]["value"]) * price_multiplier)
                offer = self.create_offer(
                    seller_id, seller_name,
                    items_offering={item: qty},
                    items_wanted={},
                    gold_wanted=value * qty
                )
                offers.append(offer)
        
        return offers
    
    def get_available_offers(self, category: str = None) -> List[TradeOffer]:
        """Get all available offers, optionally filtered by category"""
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
        """Get recent trades"""
        return self.trade_history[-limit:]
    
    def simulate_trader_visit(self, world):
        """External traders visit periodically"""
        import secrets
        
        trader_types = ["merchant", "peddler", "caravan"]
        trader_type = random.choice(trader_types)
        
        # Trader brings goods
        items = {}
        for _ in range(random.randint(3, 8)):
            item = random.choice(list(ITEMS.keys()))
            items[item] = random.randint(2, 10)
        
        # Create offers from trader
        trader_name = f"Trader {secrets.token_hex(4)}"
        
        for item, qty in items.items():
            value = int(self.market_prices[item] * 0.8)  # Traders sell cheaper
            self.create_offer(
                seller_id="trader",
                seller_name=trader_name,
                items_offering={item: qty},
                items_wanted={},
                gold_wanted=value * qty
            )
        
        return {
            "type": "trader_visit",
            "trader": trader_name,
            "trader_type": trader_type,
            "items": items
        }


# Global instance
trade_manager = TradeManager()
