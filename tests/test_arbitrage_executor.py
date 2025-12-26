"""
Unit tests for arbitrage execution
"""
import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared', 'python'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'strategies', 'strategy_1_arbitrage', 'python'))

from executor import ArbitrageExecutor
from paper_trading import PaperTradingClient


class TestArbitrageExecutor(unittest.TestCase):
    """Test arbitrage execution logic"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = PaperTradingClient(initial_balance=10000.0)
        self.executor = ArbitrageExecutor(
            client=self.client,
            max_position_size=1000.0,
            max_slippage_pct=0.02
        )
    
    def test_position_sizing(self):
        """Test position size calculation"""
        opportunity = {
            'market_id': 'test_market',
            'profit_margin': 0.02,  # 2% profit
            'total_cost': 0.98
        }
        
        position_size = self.executor.calculate_position_size(opportunity, 10000.0)
        
        self.assertGreater(position_size, 0)
        self.assertLessEqual(position_size, 1000.0)  # Should not exceed max
    
    def test_execute_arbitrage(self):
        """Test arbitrage execution"""
        opportunity = {
            'market_id': 'test_market',
            'market_description': 'Test market',
            'yes_price': 0.52,
            'no_price': 0.46,
            'total_cost': 0.98,
            'profit_margin': 0.02,
            'shares_per_dollar': 1.0 / 0.98
        }
        
        result = self.executor.execute_arbitrage(opportunity)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['market_id'], 'test_market')
        self.assertIn('yes_order_id', result)
        self.assertIn('no_order_id', result)
    
    def test_insufficient_balance(self):
        """Test execution with insufficient balance"""
        # Set very low balance
        self.client.balance = 50.0
        
        opportunity = {
            'market_id': 'test_market',
            'market_description': 'Test market',
            'yes_price': 0.52,
            'no_price': 0.46,
            'total_cost': 0.98,
            'profit_margin': 0.02,
            'shares_per_dollar': 1.0 / 0.98
        }
        
        result = self.executor.execute_arbitrage(opportunity)
        
        # Should return None due to insufficient balance
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()

