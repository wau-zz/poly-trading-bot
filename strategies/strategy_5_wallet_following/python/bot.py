#!/usr/bin/env python3
"""
Wallet Basket Trading Bot - Strategy 5
Trades on consensus signals from wallet baskets by topic
"""
import asyncio
import logging
import signal
import sys
import os
from typing import Dict, List, Optional
from datetime import datetime

# Add shared modules to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
shared_python_path = os.path.join(project_root, 'shared', 'python')
if os.path.exists(shared_python_path) and shared_python_path not in sys.path:
    sys.path.insert(0, shared_python_path)

from dotenv import load_dotenv
from polymarket_client import PolyMarketClient
from utils import setup_logging, format_currency, format_percentage

from wallet_scanner import WalletScanner
from data_fetcher import WalletDataFetcher
from wallet_basket_builder import WalletBasketBuilder, WalletBasketCriteria
from consensus_detector import ConsensusSignalDetector
from wallet_monitor import BasketMonitor

# Load environment variables
env_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=env_path)

# Setup logging
setup_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_file=os.getenv("LOG_FILE", "logs/wallet_basket_bot.log")
)

logger = logging.getLogger(__name__)


class WalletBasketBot:
    """
    Main bot that trades on consensus signals from wallet baskets
    """
    
    def __init__(self, topic: str, paper_trading: bool = False):
        """
        Initialize wallet basket bot
        
        Args:
            topic: Topic/specialization (e.g., 'geopolitics', 'crypto', 'sports')
            paper_trading: If True, use paper trading mode
        """
        self.topic = topic
        self.paper_trading = paper_trading or os.getenv("PAPER_TRADING", "false").lower() == "true"
        self.running = True
        
        # Components
        self.scanner = WalletScanner()
        self.data_fetcher = WalletDataFetcher()
        self.basket_builder = WalletBasketBuilder(topic)
        self.basket = []
        self.consensus_detector = None
        self.basket_monitor = None
        self.client = None
        
        # Statistics
        self.stats = {
            'signals_detected': 0,
            'trades_executed': 0,
            'total_profit': 0.0,
            'start_time': datetime.now(),
            'paper_trading': self.paper_trading
        }
    
    def initialize(self):
        """Initialize API client and components"""
        try:
            if self.paper_trading:
                logger.info("=" * 60)
                logger.info("🧪 PAPER TRADING MODE - No real trades will be executed")
                logger.info("=" * 60)
                # Use paper trading client if available
                try:
                    from paper_trading import PaperTradingClient
                    self.client = PaperTradingClient()
                except ImportError:
                    logger.warning("Paper trading client not available, using real client in read-only mode")
                    self.client = PolyMarketClient()
            else:
                logger.info("Initializing Wallet Basket Bot (LIVE TRADING)...")
                logger.warning("⚠️  REAL MONEY MODE - Trades will be executed on PolyMarket!")
                self.client = PolyMarketClient()
            
            logger.info("Bot initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}", exc_info=True)
            raise
    
    async def build_basket(self, max_wallets: int = 100):
        """
        Build wallet basket for the topic
        
        Args:
            max_wallets: Maximum number of wallets in basket
        """
        logger.info(f"Building {self.topic} wallet basket...")
        
        # Fetch top traders from subgraph
        logger.info("Fetching top traders from subgraph...")
        wallet_addresses = self.data_fetcher.fetch_top_traders(limit=5000)
        
        if not wallet_addresses:
            logger.error("No wallets found from subgraph!")
            return
        
        logger.info(f"Found {len(wallet_addresses)} wallet addresses, calculating stats...")
        
        # Fetch stats for each wallet
        all_wallets = []
        for i, address in enumerate(wallet_addresses):
            if (i + 1) % 100 == 0:
                logger.info(f"Processed {i + 1}/{len(wallet_addresses)} wallets...")
            
            wallet_stats = self.data_fetcher.fetch_wallet_stats(address)
            if wallet_stats:
                all_wallets.append(wallet_stats)
        
        if not all_wallets:
            logger.error("No wallets found! Cannot build basket.")
            return
        
        logger.info(f"Found {len(all_wallets)} wallets, building {self.topic} basket...")
        
        # Build basket
        self.basket = self.basket_builder.build_basket(all_wallets, max_wallets=max_wallets)
        
        if not self.basket:
            logger.error(f"No wallets passed filtering criteria for {self.topic} topic!")
            return
        
        logger.info(f"✅ Built {self.topic} basket with {len(self.basket)} wallets")
        logger.info(f"   Top wallet: {self.basket[0]['wallet'][:10]}... (score: {self.basket[0].get('composite_score', 0):.3f})")
        
        # Initialize consensus detector
        self.consensus_detector = ConsensusSignalDetector(self.basket)
        
        # Initialize basket monitor
        self.basket_monitor = BasketMonitor(self.basket, self.consensus_detector)
    
    async def monitor_consensus(self):
        """
        Continuously monitor for consensus signals
        """
        logger.info("Starting consensus monitoring...")
        
        # Start monitoring basket wallets
        if self.basket_monitor:
            await self.basket_monitor.start_monitoring()
        
        check_interval = int(os.getenv("CONSENSUS_CHECK_INTERVAL", "300"))  # 5 minutes default
        
        while self.running:
            try:
                # Get all active markets in this topic
                markets = self.client.get_markets(active=True)
                
                # Filter by topic (would need market categorization)
                topic_markets = self.filter_markets_by_topic(markets, self.topic)
                
                logger.debug(f"Checking {len(topic_markets)} {self.topic} markets for consensus...")
                
                for market in topic_markets:
                    market_id = market.get('condition_id')
                    if not market_id:
                        continue
                    
                    # Check for consensus signal
                    signal = self.consensus_detector.detect_consensus(
                        market_id,
                        get_market_price_func=lambda mid: self.get_market_mid_price(mid)
                    )
                    
                    if signal:
                        self.stats['signals_detected'] += 1
                        
                        logger.info("=" * 80)
                        logger.info("🎯 CONSENSUS SIGNAL DETECTED!")
                        logger.info(f"   Market: {market.get('question', 'N/A')[:60]}")
                        logger.info(f"   Outcome: {signal['outcome']}")
                        logger.info(f"   Consensus: {signal['consensus_pct']:.1%} of basket")
                        logger.info(f"   Signal Strength: {signal['signal_strength']:.2f}")
                        logger.info(f"   Avg Entry: ${signal['avg_entry_price']:.4f}")
                        logger.info(f"   Current: ${signal['current_price']:.4f}")
                        logger.info(f"   Participation: {signal['participation_pct']:.1%}")
                        logger.info("=" * 80)
                        
                        # Execute trade
                        await self.execute_consensus_trade(signal, market)
                
                # Log stats periodically
                if self.stats['signals_detected'] % 10 == 0 and self.stats['signals_detected'] > 0:
                    self.log_stats()
                
                await asyncio.sleep(check_interval)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                self.shutdown()
                break
                
            except Exception as e:
                logger.error(f"Error in consensus monitoring: {e}", exc_info=True)
                await asyncio.sleep(check_interval)
    
    def filter_markets_by_topic(self, markets: List[Dict], topic: str) -> List[Dict]:
        """
        Filter markets by topic
        
        Args:
            markets: List of market dicts
            topic: Topic to filter by
            
        Returns:
            Filtered list of markets
        """
        from data_fetcher import PolyMarketAPIClient
        api_client = PolyMarketAPIClient()
        
        topic_markets = []
        for market in markets:
            market_id = market.get('condition_id')
            if not market_id:
                continue
            
            # Get market topic
            market_topic = api_client.get_market_topic(market_id)
            
            # Also check if topic is in question/tags
            question = market.get('question', '').lower()
            tags = market.get('tags', [])
            all_text = (question + ' ' + ' '.join(tags)).lower()
            
            # Match topic
            if market_topic == topic.lower() or topic.lower() in all_text:
                topic_markets.append(market)
        
        return topic_markets
    
    def get_market_mid_price(self, market_id: str) -> Optional[float]:
        """
        Get current mid price for a market
        
        Args:
            market_id: Market condition_id
            
        Returns:
            Mid price or None
        """
        try:
            market = self.client.get_market(market_id)
            if not market:
                return None
            
            # Get prices from market data
            tokens = market.get('tokens', [])
            if len(tokens) >= 2:
                yes_price = float(tokens[0].get('price', 0))
                no_price = float(tokens[1].get('price', 0))
                mid_price = (yes_price + no_price) / 2.0
                return mid_price
            
            return None
        except Exception as e:
            logger.debug(f"Error getting market price: {e}")
            return None
    
    async def execute_consensus_trade(self, signal: Dict, market: Dict):
        """
        Execute trade based on consensus signal
        
        Args:
            signal: Consensus signal dict
            market: Market dict
        """
        try:
            # Calculate position size based on signal strength
            base_size = float(os.getenv("CONSENSUS_BASE_SIZE", "1000.0"))  # Base $1000
            size = base_size * signal['signal_strength']
            
            # Get token_ids
            condition_id = signal['market_id']
            token_ids = self.client.get_token_ids(condition_id)
            
            if not token_ids:
                logger.error(f"Could not get token_ids for {condition_id}")
                return
            
            # Place order
            if signal['outcome'] == 'YES':
                token_id = token_ids['yes_token_id']
                price = signal['current_price'] * 1.01  # Allow 1% slippage
            else:
                token_id = token_ids['no_token_id']
                price = signal['current_price'] * 0.99
            
            logger.info(f"Executing consensus trade: {signal['outcome']} ${size:.2f} @ ${price:.4f}")
            
            order = self.client.place_order(
                market_id=token_id,
                side='BUY',
                price=price,
                size=size / price,  # Convert to shares
                order_type='LIMIT'
            )
            
            if order:
                self.stats['trades_executed'] += 1
                logger.info(f"✅ Trade executed: Order ID {order.get('id', 'N/A')}")
            else:
                logger.error("❌ Trade execution failed")
                
        except Exception as e:
            logger.error(f"Error executing consensus trade: {e}", exc_info=True)
    
    def log_stats(self):
        """Log current statistics"""
        runtime = datetime.now() - self.stats['start_time']
        mode = "🧪 PAPER TRADING" if self.paper_trading else "💰 LIVE TRADING"
        
        logger.info("=" * 50)
        logger.info(f"Bot Statistics ({mode}):")
        logger.info(f"  Topic: {self.topic}")
        logger.info(f"  Basket Size: {len(self.basket)}")
        logger.info(f"  Runtime: {runtime}")
        logger.info(f"  Signals Detected: {self.stats['signals_detected']}")
        logger.info(f"  Trades Executed: {self.stats['trades_executed']}")
        logger.info(f"  Total Profit: {format_currency(self.stats['total_profit'])}")
        logger.info("=" * 50)
    
    def shutdown(self, signum=None, frame=None):
        """Graceful shutdown"""
        logger.info("Shutting down bot...")
        self.running = False
        
        if self.basket_monitor:
            self.basket_monitor.stop()
        
        self.log_stats()
    
    async def run(self):
        """Main bot loop"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        
        # Initialize
        self.initialize()
        
        # Build basket
        await self.build_basket()
        
        if not self.basket:
            logger.error("Cannot run bot without a basket!")
            return
        
        # Start monitoring
        await self.monitor_consensus()


def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Wallet Basket Trading Bot')
    parser.add_argument('--topic', type=str, default='geopolitics',
                       help='Topic/specialization (e.g., geopolitics, crypto, sports)')
    parser.add_argument('--paper', action='store_true',
                       help='Enable paper trading mode')
    
    args = parser.parse_args()
    
    paper_trading = args.paper or os.getenv("PAPER_TRADING", "false").lower() == "true"
    
    if paper_trading:
        logger.info("Starting bot in PAPER TRADING mode")
    else:
        logger.warning("Starting bot in LIVE TRADING mode - real money at risk!")
        response = input("Continue with live trading? (yes/no): ")
        if response.lower() != 'yes':
            logger.info("Aborted by user")
            sys.exit(0)
    
    bot = WalletBasketBot(topic=args.topic, paper_trading=paper_trading)
    
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

