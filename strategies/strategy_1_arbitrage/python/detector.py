"""
Arbitrage Detection Module
Detects risk-free arbitrage opportunities in PolyMarket
"""
import logging
from typing import Optional, Dict
import sys
import os

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..', 'shared', 'python'))

from polymarket_client import PolyMarketClient
from utils import calculate_profit_margin

logger = logging.getLogger(__name__)


class ArbitrageDetector:
    """Detects arbitrage opportunities in PolyMarket"""
    
    def __init__(self, client: PolyMarketClient, min_profit_pct: float = 0.01, fee_rate: float = 0.02):
        """
        Initialize arbitrage detector
        
        Args:
            client: PolyMarket API client
            min_profit_pct: Minimum profit percentage required (default 1%)
            fee_rate: Trading fee rate (default 2%)
        """
        self.client = client
        self.min_profit_pct = min_profit_pct
        self.fee_rate = fee_rate
    
    def detect_arbitrage(self, market: Dict) -> Optional[Dict]:
        """
        Detect if a market presents an arbitrage opportunity
        
        Args:
            market: Market dictionary with price information
            
        Returns:
            Arbitrage opportunity dict or None
        """
        try:
            # Get prices
            yes_price = market.get('yes_price', 0.0)
            no_price = market.get('no_price', 0.0)
            
            if yes_price <= 0 or no_price <= 0:
                return None
            
            # Check if profitable after fees
            is_profitable, profit_margin = calculate_profit_margin(
                yes_price, 
                no_price, 
                self.fee_rate
            )
            
            if not is_profitable:
                return None
            
            # Check if profit margin meets minimum threshold
            if profit_margin < self.min_profit_pct:
                return None
            
            # Calculate expected profit
            total_cost = yes_price + no_price
            shares_per_dollar = 1.0 / total_cost
            profit_per_dollar = profit_margin
            
            return {
                'market_id': market.get('id') or market.get('market_id'),
                'market_description': market.get('description', 'Unknown'),
                'yes_price': yes_price,
                'no_price': no_price,
                'total_cost': total_cost,
                'profit_margin': profit_margin,
                'profit_pct': profit_margin * 100,
                'shares_per_dollar': shares_per_dollar,
                'profit_per_dollar': profit_per_dollar,
                'is_arbitrage': True
            }
            
        except Exception as e:
            logger.error(f"Error detecting arbitrage for market {market.get('id')}: {e}")
            return None
    
    def scan_markets(self, markets: List[Dict]) -> List[Dict]:
        """
        Scan multiple markets for arbitrage opportunities
        
        Args:
            markets: List of market dictionaries
            
        Returns:
            List of arbitrage opportunities
        """
        opportunities = []
        
        for market in markets:
            opportunity = self.detect_arbitrage(market)
            if opportunity:
                opportunities.append(opportunity)
        
        # Sort by profit margin (highest first)
        opportunities.sort(key=lambda x: x['profit_margin'], reverse=True)
        
        return opportunities
    
    def get_market_prices(self, market_id: str) -> Optional[Dict]:
        """
        Get current prices for a market and check for arbitrage
        
        Args:
            market_id: Market identifier
            
        Returns:
            Arbitrage opportunity or None
        """
        prices = self.client.get_market_prices(market_id)
        if not prices:
            return None
        
        market = {
            'id': market_id,
            'yes_price': prices['yes_price'],
            'no_price': prices['no_price']
        }
        
        return self.detect_arbitrage(market)

