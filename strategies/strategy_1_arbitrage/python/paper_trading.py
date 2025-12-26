"""
Paper Trading Module
Simulates trades without actually executing them on PolyMarket
Perfect for testing strategies before deploying with real money
"""
import logging
from typing import Dict, Optional
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)


class PaperTradingClient:
    """
    Mock PolyMarket client for paper trading
    Simulates all operations without real API calls
    """
    
    def __init__(self, initial_balance: float = 10000.0):
        """
        Initialize paper trading client
        
        Args:
            initial_balance: Starting balance in USD
        """
        self.balance = initial_balance
        self.orders = []
        self.positions = []
        self.trades = []
        self.markets = {}
        
        logger.info(f"Paper trading initialized with ${initial_balance:,.2f}")
    
    def get_markets(self, active: bool = True) -> list:
        """
        Get markets (in paper trading, returns mock data)
        
        In real testing, you'd load historical market data
        """
        # For paper trading, you can:
        # 1. Load historical market data
        # 2. Use mock markets
        # 3. Connect to real API but don't execute
        
        # Placeholder - returns empty list
        # In practice, load from historical data or use real API read-only
        return []
    
    def get_market(self, market_id: str) -> Optional[Dict]:
        """Get market data (mock)"""
        return self.markets.get(market_id)
    
    def get_market_prices(self, market_id: str) -> Optional[Dict]:
        """Get current prices (mock)"""
        market = self.get_market(market_id)
        if market:
            return {
                'yes_price': market.get('yes_price', 0.5),
                'no_price': market.get('no_price', 0.5),
                'market_id': market_id
            }
        return None
    
    def place_order(
        self,
        market_id: str,
        side: str,
        price: float,
        size: float,
        order_type: str = "LIMIT"
    ) -> Dict:
        """
        Simulate placing an order (doesn't actually execute)
        
        Returns a mock order response
        """
        cost = price * size
        
        if cost > self.balance:
            logger.warning(f"❌ Insufficient balance: Need ${cost:.2f}, have ${self.balance:.2f}")
            return None
        
        # Simulate order
        order = {
            'id': f"paper_order_{len(self.orders)}",
            'market_id': market_id,
            'side': side,
            'price': price,
            'size': size,
            'cost': cost,
            'status': 'FILLED',  # In paper trading, assume immediate fill
            'timestamp': datetime.now().isoformat()
        }
        
        self.orders.append(order)
        self.balance -= cost
        
        logger.info(f"📝 PAPER TRADE: {side} {size:.2f} shares @ ${price:.4f} = ${cost:.2f}")
        logger.info(f"   Remaining balance: ${self.balance:,.2f}")
        
        return order
    
    def cancel_order(self, order_id: str) -> bool:
        """Simulate canceling an order"""
        logger.info(f"📝 PAPER TRADE: Cancelled order {order_id}")
        return True
    
    def get_balance(self) -> float:
        """Get current balance"""
        return self.balance
    
    def simulate_market_resolution(self, market_id: str, winning_side: str):
        """
        Simulate market resolution for paper trading
        
        Args:
            market_id: Market that resolved
            winning_side: 'YES' or 'NO'
        """
        # Find all positions in this market
        market_positions = [p for p in self.positions if p['market_id'] == market_id]
        
        for position in market_positions:
            if position['side'] == winning_side:
                # Winning position pays $1 per share
                payout = position['shares'] * 1.0
                profit = payout - position['cost']
                self.balance += payout
                
                logger.info(f"📝 PAPER TRADE: Market {market_id} resolved - {winning_side} won")
                logger.info(f"   Payout: ${payout:.2f}, Profit: ${profit:.2f}")
                
                # Record trade
                trade = {
                    'market_id': market_id,
                    'position': position,
                    'winning_side': winning_side,
                    'payout': payout,
                    'profit': profit,
                    'timestamp': datetime.now().isoformat()
                }
                self.trades.append(trade)
    
    def get_statistics(self) -> Dict:
        """Get paper trading statistics"""
        total_invested = sum(p['cost'] for p in self.positions)
        total_payout = sum(t['payout'] for t in self.trades)
        total_profit = sum(t['profit'] for t in self.trades)
        
        return {
            'current_balance': self.balance,
            'total_orders': len(self.orders),
            'active_positions': len(self.positions),
            'completed_trades': len(self.trades),
            'total_invested': total_invested,
            'total_payout': total_payout,
            'total_profit': total_profit,
            'roi': (total_profit / total_invested * 100) if total_invested > 0 else 0
        }

