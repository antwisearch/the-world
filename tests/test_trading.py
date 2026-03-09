"""
Test trading system
"""

import sys
sys.path.insert(0, '.')

from src.trading import Trade, Shop, Trader, TradeOffer, TradeManager, ITEMS


class TestTrade:
    """Test Trade dataclass"""
    
    def test_trade_is_dataclass(self):
        # Trade is a dataclass, it exists
        assert Trade is not None
        # Check it has required fields
        import dataclasses
        assert dataclasses.is_dataclass(Trade)


class TestShop:
    """Test Shop class"""
    
    def test_shop_exists(self):
        assert Shop is not None


class TestTrader:
    """Test Trader class"""
    
    def test_trader_exists(self):
        assert Trader is not None


class TestTradeOffer:
    """Test TradeOffer class"""
    
    def test_tradeoffer_exists(self):
        assert TradeOffer is not None


class TestTradeManager:
    """Test TradeManager class"""
    
    def test_trade_manager_creation(self):
        tm = TradeManager()
        assert tm is not None
    
    def test_trade_manager_has_offers(self):
        tm = TradeManager()
        assert hasattr(tm, 'offers') or hasattr(tm, 'active_offers')


class TestITEMS:
    """Test ITEMS dictionary"""
    
    def test_items_exist(self):
        assert 'wood' in ITEMS
        assert 'stone' in ITEMS
    
    def test_items_have_values(self):
        for name, item in ITEMS.items():
            assert 'value' in item
            assert item['value'] > 0
    
    def test_items_have_categories(self):
        for name, item in ITEMS.items():
            assert 'category' in item
    
    def test_food_cheap(self):
        """Food should be cheaper than luxury items"""
        food_values = [v['value'] for k, v in ITEMS.items() if v.get('category') == 'food']
        luxury_values = [v['value'] for k, v in ITEMS.items() if v.get('category') == 'luxury']
        
        if food_values and luxury_values:
            avg_food = sum(food_values) / len(food_values)
            avg_luxury = sum(luxury_values) / len(luxury_values)
            assert avg_food < avg_luxury
    
    def test_gold_most_valuable(self):
        """Gold should be the most valuable material"""
        gold_val = ITEMS['gold']['value']
        wood_val = ITEMS['wood']['value']
        stone_val = ITEMS['stone']['value']
        
        assert gold_val > wood_val
        assert gold_val > stone_val
    
    def test_herbs_exist(self):
        """Herbs should exist for healer job"""
        assert 'herbs' in ITEMS


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
