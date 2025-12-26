"""
Unit tests for arbitrage detection
"""
import unittest
import sys
import os

# Add project to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared', 'python'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'strategies', 'strategy_1_arbitrage', 'python'))

from detector import ArbitrageDetector
from paper_trading import PaperTradingClient
from utils import calculate_profit_margin


class TestArbitrageDetector(unittest.TestCase):
    """Test arbitrage detection logic"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = PaperTradingClient()
        self.detector = ArbitrageDetector(
            client=self.client,
            min_profit_pct=0.01,
            fee_rate=0.02
        )
    
    def test_profitable_arbitrage(self):
        """Test detection of profitable arbitrage"""
        market = {
            'id': 'test_market_1',
            'yes_price': 0.52,
            'no_price': 0.46,
            'description': 'Test market'
        }
        
        opportunity = self.detector.detect_arbitrage(market)
        
        self.assertIsNotNone(opportunity, "Should detect arbitrage opportunity")
        self.assertTrue(opportunity['is_arbitrage'])
        self.assertGreater(opportunity['profit_margin'], 0.01)
    
    def test_no_arbitrage(self):
        """Test that non-arbitrage markets are rejected"""
        market = {
            'id': 'test_market_2',
            'yes_price': 0.60,
            'no_price': 0.40,
            'description': 'Test market'
        }
        
        opportunity = self.detector.detect_arbitrage(market)
        
        self.assertIsNone(opportunity, "Should not detect arbitrage")
    
    def test_profit_margin_calculation(self):
        """Test profit margin calculation"""
        # Test case: YES=0.52, NO=0.46, fees=2%
        is_profitable, profit_margin = calculate_profit_margin(0.52, 0.46, 0.02)
        
        self.assertTrue(is_profitable)
        self.assertGreater(profit_margin, 0.0)
        
        # Test case: YES=0.60, NO=0.40, fees=2% (no arbitrage)
        is_profitable, profit_margin = calculate_profit_margin(0.60, 0.40, 0.02)
        
        self.assertFalse(is_profitable)
    
    def test_minimum_profit_threshold(self):
        """Test that minimum profit threshold is enforced"""
        # Very small arbitrage (below 1% threshold)
        market = {
            'id': 'test_market_3',
            'yes_price': 0.505,
            'no_price': 0.495,
            'description': 'Test market'
        }
        
        opportunity = self.detector.detect_arbitrage(market)
        
        # Should be rejected due to small profit margin
        self.assertIsNone(opportunity)


if __name__ == '__main__':
    unittest.main()

