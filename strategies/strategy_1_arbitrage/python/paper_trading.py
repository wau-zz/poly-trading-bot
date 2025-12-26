"""
Paper Trading Module
Simulates trades without actually executing them on PolyMarket
Perfect for testing strategies before deploying with real money
"""
import logging
from typing import Dict, Optional, List
from datetime import datetime
import json
import os
import sys

# Add shared modules to path for real API access
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
shared_python_path = os.path.join(project_root, 'shared', 'python')
if os.path.exists(shared_python_path) and shared_python_path not in sys.path:
    sys.path.insert(0, shared_python_path)

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
        
        # Initialize real API client for market data (read-only)
        # This allows us to get real market data but simulate trades
        try:
            from polymarket_client import PolyMarketClient
            self.real_client = PolyMarketClient()
            logger.info("Real API client initialized for market data (read-only)")
        except Exception as e:
            logger.warning(f"Could not initialize real API client: {e}")
            logger.warning("Paper trading will use mock data only")
            self.real_client = None
        
        logger.info(f"Paper trading initialized with ${initial_balance:,.2f}")
    
    def get_markets(self, active: bool = True) -> List[Dict]:
        """
        Get markets from real API (read-only)
        In paper trading, we fetch real market data but simulate trades
        """
        if self.real_client:
            try:
                # Fetch real markets from API
                markets = self.real_client.get_markets(active=active)
                if markets:
                    logger.debug(f"Fetched {len(markets)} markets from real API (paper trading mode)")
                else:
                    logger.warning(f"Fetched 0 markets from real API (active={active})")
                return markets
            except Exception as e:
                logger.error(f"Error fetching markets from real API: {e}", exc_info=True)
                return []
        else:
            logger.warning("No real API client available, returning empty market list")
            return []
    
    def get_market(self, market_id: str) -> Optional[Dict]:
        """Get market data from real API (read-only)"""
        if self.real_client:
            try:
                return self.real_client.get_market(market_id)
            except Exception as e:
                logger.error(f"Error fetching market {market_id}: {e}")
                return None
        return self.markets.get(market_id)
    
    def get_market_prices(self, market_id: str) -> Optional[Dict]:
        """Get current prices from real API (read-only)"""
        if self.real_client:
            try:
                return self.real_client.get_market_prices(market_id)
            except Exception as e:
                logger.error(f"Error fetching prices for {market_id}: {e}")
                return None
        
        # Fallback to mock if no real client
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

