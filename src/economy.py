"""
Economy System - Trade, wealth, resources
"""

import random

class TradeGood:
    """A tradeable item"""
    
    def __init__(self, name, base_value, category):
        self.name = name
        self.base_value = base_value
        self.category = category  # 'food', 'material', 'luxury', 'weapon'


class Market:
    """Trading market"""
    
    # Trade goods with values
    GOODS = {
        'food': TradeGood('food', 1, 'food'),
        'wood': TradeGood('wood', 2, 'material'),
        'stone': TradeGood('stone', 3, 'material'),
        'ore': TradeGood('ore', 5, 'material'),
        'iron': TradeGood('iron', 10, 'material'),
        'gems': TradeGood('gems', 20, 'luxury'),
        'jewelry': TradeGood('jewelry', 30, 'luxury'),
        'weapon': TradeGood('weapon', 15, 'weapon'),
        'armor': TradeGood('armor', 20, 'weapon'),
        'goods': TradeGood('goods', 5, 'material'),
    }
    
    def __init__(self):
        self.prices = {}
        self.update_prices()
    
    def update_prices(self):
        """Update prices based on supply/demand"""
        for name, good in self.GOODS.items():
            # Base price with some variation
            variance = random.uniform(0.8, 1.2)
            self.prices[name] = int(good.base_value * variance)
    
    def get_price(self, item):
        """Get current price of item"""
        return self.prices.get(item, 1)
    
    def buy(self, buyer, item, quantity=1):
        """Buy item from market"""
        cost = self.get_price(item) * quantity
        if buyer.wealth >= cost:
            buyer.wealth -= cost
            buyer.inventory[item] = buyer.inventory.get(item, 0) + quantity
            return True, cost
        return False, cost
    
    def sell(self, seller, item, quantity=1):
        """Sell item to market"""
        if seller.inventory.get(item, 0) >= quantity:
            revenue = self.get_price(item) * quantity
            seller.inventory[item] -= quantity
            seller.wealth += revenue
            return True, revenue
        return False, 0


class Economy:
    """Main economy system"""
    
    def __init__(self, world):
        self.world = world
        self.market = Market()
        self.trades = []  # Trade history
    
    def tick(self):
        """Update economy"""
        # Update prices occasionally
        if random.random() < 0.01:
            self.market.update_prices()
        
        # Process trades
        self._process_trades()
    
    def _process_trades(self):
        """Process trade between agents"""
        traders = [a for a in self.world.agents if a.alive and a.job == 'trader']
        
        for trader in traders:
            if random.random() < 0.05:  # 5% chance per tick
                # Find another agent to trade with
                others = [a for a in self.world.agents if a.alive and a != trader]
                if others:
                    partner = random.choice(others)
                    self._trade(trader, partner)
    
    def _trade(self, trader, partner):
        """Trade between two agents"""
        # Find items to trade
        trader_sell = [item for item, qty in trader.inventory.items() if qty > 1]
        partner_sell = [item for item, qty in partner.inventory.items() if qty > 1]
        
        if not trader_sell or not partner_sell:
            return
        
        # Simple barter
        trader_item = random.choice(trader_sell)
        partner_item = random.choice(partner_sell)
        
        trader_value = self.market.get_price(trader_item)
        partner_value = self.market.get_price(partner_item)
        
        # Swap if roughly equal
        if abs(trader_value - partner_value) < 5:
            trader.inventory[trader_item] -= 1
            partner.inventory[trader_item] = partner.inventory.get(trader_item, 0) + 1
            
            partner.inventory[partner_item] -= 1
            trader.inventory[partner_item] = trader.inventory.get(partner_item, 0) + 1
            
            self.trades.append({
                'type': 'barter',
                'from': trader.biography.name if hasattr(trader, 'biography') else 'trader',
                'to': partner.biography.name if hasattr(partner, 'biography') else 'partner',
                'items': (trader_item, partner_item)
            })
    
    def get_stats(self):
        """Get economy statistics"""
        total_wealth = sum(
            a.inventory.get('wealth', 0) 
            for a in self.world.agents if a.alive
        )
        
        return {
            'total_wealth': total_wealth,
            'trades_today': len(self.trades[-100:]),
            'prices': dict(list(self.market.prices.items())[:5])
        }
    
    def to_dict(self):
        return self.get_stats()
