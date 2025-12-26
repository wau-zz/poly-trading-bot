"""
Integration tests for Strategy 1
Tests the full bot workflow end-to-end
"""
import unittest
import sys
import os
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared', 'python'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'strategies', 'strategy_1_arbitrage', 'python'))

from bot import ArbitrageBot
from paper_trading import PaperTradingClient


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_bot_initialization_paper_trading(self):
        """Test bot initializes correctly in paper trading mode"""
        bot = ArbitrageBot(paper_trading=True)
        
        self.assertTrue(bot.paper_trading)
        self.assertIsNotNone(bot.detector)
        self.assertIsNotNone(bot.executor)
    
    def test_detection_and_execution_flow(self):
        """Test complete flow: detection -> execution"""
        client = PaperTradingClient(initial_balance=10000.0)
        
        from detector import ArbitrageDetector
        from executor import ArbitrageExecutor
        
        detector = ArbitrageDetector(client=client, min_profit_pct=0.01)
        executor = ArbitrageExecutor(client=client, max_position_size=1000.0)
        
        # Create test market with arbitrage
        market = {
            'id': 'test_market',
            'yes_price': 0.52,
            'no_price': 0.46,
            'description': 'Test market'
        }
        
        # Detect
        opportunity = detector.detect_arbitrage(market)
        self.assertIsNotNone(opportunity)
        
        # Execute
        result = executor.execute_arbitrage(opportunity)
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()

