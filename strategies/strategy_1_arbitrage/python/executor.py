"""
Order Execution Module
Handles execution of arbitrage trades
"""
import logging
import asyncio
from typing import Dict, Optional, Tuple
from datetime import datetime
import sys
import os

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..', 'shared', 'python'))

from polymarket_client import PolyMarketClient
from utils import format_currency, format_percentage, log_trade

logger = logging.getLogger(__name__)


class ArbitrageExecutor:
    """Executes arbitrage trades"""
    
    def __init__(
        self, 
        client: PolyMarketClient,
        max_position_size: float = 1000.0,
        max_slippage_pct: float = 0.02
    ):
        """
        Initialize arbitrage executor
        
        Args:
            client: PolyMarket API client
            max_position_size: Maximum position size per trade (in USD)
            max_slippage_pct: Maximum acceptable slippage (default 2%)
        """
        self.client = client
        self.max_position_size = max_position_size
        self.max_slippage_pct = max_slippage_pct
        self.executed_trades = []
    
    def calculate_position_size(self, opportunity: Dict, available_capital: float) -> float:
        """
        Calculate position size for arbitrage trade
        
        Args:
            opportunity: Arbitrage opportunity dict
            available_capital: Available capital in USD
            
        Returns:
            Position size in USD
        """
        # Base position size
        base_size = min(self.max_position_size, available_capital * 0.1)  # Max 10% of capital
        
        # Scale up for better opportunities
        profit_margin = opportunity['profit_margin']
        scaled_size = base_size * (1 + profit_margin * 10)
        
        # Cap at max position size
        position_size = min(scaled_size, self.max_position_size, available_capital * 0.2)
        
        return max(position_size, 100.0)  # Minimum $100
    
    def execute_arbitrage(self, opportunity: Dict) -> Optional[Dict]:
        """
        Execute arbitrage trade by buying both YES and NO shares
        
        Args:
            opportunity: Arbitrage opportunity dict
            
        Returns:
            Trade result dict or None
        """
        try:
            # Get available balance
            balance = self.client.get_balance()
            
            if balance < 100:
                logger.warning(f"Insufficient balance: {format_currency(balance)}")
                return None
            
            # Calculate position size
            position_size = self.calculate_position_size(opportunity, balance)
            
            # Calculate number of shares
            total_cost = opportunity['total_cost']
            shares = position_size / total_cost
            
            logger.info(f"Executing arbitrage:")
            logger.info(f"  Market: {opportunity['market_description']}")
            logger.info(f"  YES price: ${opportunity['yes_price']:.4f}")
            logger.info(f"  NO price: ${opportunity['no_price']:.4f}")
            logger.info(f"  Position size: {format_currency(position_size)}")
            logger.info(f"  Shares: {shares:.2f}")
            logger.info(f"  Expected profit: {format_percentage(opportunity['profit_margin'])}")
            
            # Place both orders simultaneously
            yes_order = self.client.place_order(
                market_id=opportunity['market_id'],
                side='BUY',
                price=opportunity['yes_price'] * (1 + self.max_slippage_pct),  # Allow slippage
                size=shares,
                order_type='LIMIT'
            )
            
            no_order = self.client.place_order(
                market_id=opportunity['market_id'],
                side='BUY',
                price=opportunity['no_price'] * (1 + self.max_slippage_pct),  # Allow slippage
                size=shares,
                order_type='LIMIT'
            )
            
            if not yes_order or not no_order:
                logger.error("Failed to place one or both orders")
                # Cancel the other order if one failed
                if yes_order:
                    self.client.cancel_order(yes_order.get('id'))
                if no_order:
                    self.client.cancel_order(no_order.get('id'))
                return None
            
            # Record trade
            trade_result = {
                'type': 'arbitrage',
                'market_id': opportunity['market_id'],
                'market_description': opportunity['market_description'],
                'yes_order_id': yes_order.get('id'),
                'no_order_id': no_order.get('id'),
                'yes_price': opportunity['yes_price'],
                'no_price': opportunity['no_price'],
                'shares': shares,
                'position_size': position_size,
                'expected_profit': position_size * opportunity['profit_margin'],
                'profit_margin': opportunity['profit_margin'],
                'timestamp': datetime.now().isoformat(),
                'status': 'executed'
            }
            
            self.executed_trades.append(trade_result)
            
            # Log trade
            log_trade(trade_result)
            
            logger.info(f"✅ Arbitrage executed successfully!")
            logger.info(f"  Expected profit: {format_currency(trade_result['expected_profit'])}")
            
            return trade_result
            
        except Exception as e:
            logger.error(f"Error executing arbitrage: {e}", exc_info=True)
            return None
    
    def get_trade_history(self) -> list[Dict]:
        """Get history of executed trades"""
        return self.executed_trades.copy()

