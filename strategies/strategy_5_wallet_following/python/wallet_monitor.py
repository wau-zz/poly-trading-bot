"""
Wallet Monitor
Monitors wallet activity in real-time for consensus detection
"""
import logging
import asyncio
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import sys
import os

# Add shared modules to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
shared_python_path = os.path.join(project_root, 'shared', 'python')
if os.path.exists(shared_python_path) and shared_python_path not in sys.path:
    sys.path.insert(0, shared_python_path)

logger = logging.getLogger(__name__)


class WalletMonitor:
    """
    Monitors wallet activity in real-time
    """
    
    def __init__(self, wallet_address: str, on_new_trade: Optional[Callable] = None):
        """
        Initialize wallet monitor
        
        Args:
            wallet_address: Wallet address to monitor
            on_new_trade: Callback function when new trade detected
        """
        self.wallet = wallet_address.lower()
        self.on_new_trade = on_new_trade
        self.last_known_trade_id = None
        self.last_check_time = None
        self.running = False
    
    async def monitor_activity(self, check_interval: int = 60):
        """
        Monitor wallet for new trades in real-time
        
        Args:
            check_interval: Seconds between checks
        """
        self.running = True
        logger.info(f"Monitoring wallet {self.wallet[:10]}...")
        
        while self.running:
            try:
                # Fetch recent trades for this wallet
                recent_trades = await self.fetch_recent_trades()
                
                for trade in recent_trades:
                    # New trade detected!
                    if self.on_new_trade:
                        await self.on_new_trade(trade)
                    
                    # Update last known trade
                    if trade.get('id'):
                        self.last_known_trade_id = trade['id']
                
                self.last_check_time = datetime.now()
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Error monitoring wallet {self.wallet}: {e}", exc_info=True)
                await asyncio.sleep(check_interval * 2)  # Wait longer on error
    
    async def fetch_recent_trades(self) -> List[Dict]:
        """
        Fetch recent trades for this wallet
        
        Returns:
            List of trade dicts
        """
        try:
            from data_fetcher import WalletDataFetcher
            fetcher = WalletDataFetcher()
            
            # Get trades since last check (or last 24 hours if first check)
            since = self.last_check_time or (datetime.now() - timedelta(hours=24))
            
            trades = fetcher.fetch_wallet_trades(self.wallet, since=since)
            
            # Filter to only new trades (after last known trade)
            if self.last_known_trade_id:
                trades = [t for t in trades if t.get('id') != self.last_known_trade_id]
            
            return trades
            
        except ImportError:
            logger.warning("data_fetcher not available, returning empty list")
            return []
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        logger.info(f"Stopped monitoring wallet {self.wallet[:10]}...")


class BasketMonitor:
    """
    Monitors entire wallet basket for consensus signals
    """
    
    def __init__(self, basket: List[Dict], consensus_detector):
        """
        Initialize basket monitor
        
        Args:
            basket: List of wallet dicts in basket
            consensus_detector: ConsensusSignalDetector instance
        """
        self.basket = basket
        self.consensus_detector = consensus_detector
        self.monitors = {}
        self.active_markets = set()
        self.running = False
    
    async def start_monitoring(self):
        """Start monitoring all wallets in basket"""
        self.running = True
        
        # Create monitor for each wallet
        for wallet in self.basket:
            wallet_address = wallet['wallet']
            monitor = WalletMonitor(
                wallet_address,
                on_new_trade=self.on_basket_trade
            )
            self.monitors[wallet_address] = monitor
            
            # Start monitoring (non-blocking)
            asyncio.create_task(monitor.monitor_activity())
        
        logger.info(f"Started monitoring {len(self.monitors)} wallets in basket")
    
    async def on_basket_trade(self, trade: Dict):
        """
        Called when any wallet in basket makes a trade
        
        Args:
            trade: Trade dict
        """
        market_id = trade.get('market_id')
        if market_id:
            self.active_markets.add(market_id)
            
            # Check for consensus on this market
            # (This would be called periodically, not on every trade)
            logger.debug(f"Basket trade detected: {trade.get('wallet', '')[:10]}... on market {market_id[:20]}...")
    
    async def check_consensus(self, market_id: str, get_market_price_func=None) -> Optional[Dict]:
        """
        Check for consensus signal on a market
        
        Args:
            market_id: Market condition_id
            get_market_price_func: Function to get current market price
            
        Returns:
            Consensus signal dict or None
        """
        return self.consensus_detector.detect_consensus(market_id, get_market_price_func)
    
    def stop(self):
        """Stop monitoring all wallets"""
        self.running = False
        for monitor in self.monitors.values():
            monitor.stop()
        logger.info("Stopped monitoring basket")

