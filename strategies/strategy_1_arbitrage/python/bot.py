#!/usr/bin/env python3
"""
PolyMarket Arbitrage Bot - Strategy 1
Continuously scans markets for risk-free arbitrage opportunities
"""
import asyncio
import logging
import signal
import sys
import os
import time
from datetime import datetime
from typing import List, Dict, Optional

# Add shared modules to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
shared_python_path = os.path.join(project_root, 'shared', 'python')
if os.path.exists(shared_python_path) and shared_python_path not in sys.path:
    sys.path.insert(0, shared_python_path)

from dotenv import load_dotenv
from polymarket_client import PolyMarketClient
from utils import setup_logging, format_currency, format_percentage
from detector import ArbitrageDetector
from executor import ArbitrageExecutor

# Paper trading import (optional - only if paper_trading.py exists)
try:
    from paper_trading import PaperTradingClient
    PAPER_TRADING_AVAILABLE = True
except ImportError:
    PAPER_TRADING_AVAILABLE = False

# Load environment variables from project root
env_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=env_path)

# Setup logging
setup_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_file=os.getenv("LOG_FILE", "logs/arbitrage_bot.log")
)

logger = logging.getLogger(__name__)


class ArbitrageBot:
    """Main arbitrage trading bot"""
    
    def __init__(self, paper_trading: bool = False):
        """
        Initialize the arbitrage bot
        
        Args:
            paper_trading: If True, use paper trading mode (no real trades)
        """
        self.running = True
        self.paper_trading = paper_trading or os.getenv("PAPER_TRADING", "false").lower() == "true"
        self.client = None
        self.detector = None
        self.executor = None
        self.scan_interval = float(os.getenv("ARBITRAGE_SCAN_INTERVAL", "0.1"))  # 100ms
        self.min_profit_pct = float(os.getenv("STRATEGY_1_MIN_PROFIT_MARGIN", "0.01"))
        self.max_position_size = float(os.getenv("STRATEGY_1_MAX_POSITION_SIZE", "1000.0"))
        
        # Statistics
        self.stats = {
            'scans': 0,
            'opportunities_found': 0,
            'trades_executed': 0,
            'total_profit': 0.0,
            'start_time': datetime.now(),
            'paper_trading': self.paper_trading
        }
    
    def initialize(self):
        """Initialize API client and components"""
        try:
            if self.paper_trading:
                if not PAPER_TRADING_AVAILABLE:
                    raise ImportError("Paper trading module not available. Make sure paper_trading.py exists.")
                
                logger.info("=" * 60)
                logger.info("🧪 PAPER TRADING MODE - No real trades will be executed")
                logger.info("=" * 60)
                
                # Use paper trading client
                initial_balance = float(os.getenv("PAPER_TRADING_BALANCE", "10000.0"))
                self.client = PaperTradingClient(initial_balance=initial_balance)
            else:
                logger.info("Initializing PolyMarket Arbitrage Bot (LIVE TRADING)...")
                logger.warning("⚠️  REAL MONEY MODE - Trades will be executed on PolyMarket!")
                
                # Use real client
                self.client = PolyMarketClient()
            
            # Initialize detector
            self.detector = ArbitrageDetector(
                client=self.client,
                min_profit_pct=self.min_profit_pct
            )
            
            # Initialize executor
            self.executor = ArbitrageExecutor(
                client=self.client,
                max_position_size=self.max_position_size
            )
            
            # Check balance
            balance = self.client.get_balance()
            logger.info(f"Available balance: {format_currency(balance)}")
            
            if not self.paper_trading and balance < 100:
                logger.warning("Low balance! Minimum $100 recommended for trading.")
            
            logger.info("Bot initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}", exc_info=True)
            raise
    
    async def scan_for_arbitrage(self):
        """Continuously scan markets for arbitrage opportunities"""
        logger.info("Starting arbitrage scan loop...")
        
        while self.running:
            try:
                # Get all active markets
                markets = self.client.get_markets(active=True)
                
                if not markets:
                    logger.warning("No markets found")
                    await asyncio.sleep(5)
                    continue
                
                # Scan for arbitrage
                opportunities = self.detector.scan_markets(markets)
                
                self.stats['scans'] += 1
                
                if opportunities:
                    self.stats['opportunities_found'] += len(opportunities)
                    logger.info(f"Found {len(opportunities)} arbitrage opportunity(ies)")
                    
                    # Execute best opportunity
                    best_opportunity = opportunities[0]
                    logger.info(f"Best opportunity: {format_percentage(best_opportunity['profit_margin'])} profit")
                    
                    result = self.executor.execute_arbitrage(best_opportunity)
                    
                    if result:
                        self.stats['trades_executed'] += 1
                        self.stats['total_profit'] += result['expected_profit']
                        
                        if self.paper_trading:
                            logger.info(f"📝 PAPER TRADE executed! Expected profit: {format_currency(result['expected_profit'])}")
                        else:
                            logger.info(f"✅ LIVE TRADE executed! Expected profit: {format_currency(result['expected_profit'])}")
                
                # Log stats periodically
                if self.stats['scans'] % 100 == 0:
                    self.log_stats()
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(self.scan_interval)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                self.shutdown()
                break
                
            except Exception as e:
                logger.error(f"Error in arbitrage scan: {e}", exc_info=True)
                await asyncio.sleep(5)  # Wait longer on error
    
    def log_stats(self):
        """Log current statistics"""
        runtime = datetime.now() - self.stats['start_time']
        mode = "🧪 PAPER TRADING" if self.paper_trading else "💰 LIVE TRADING"
        
        logger.info("=" * 50)
        logger.info(f"Bot Statistics ({mode}):")
        logger.info(f"  Runtime: {runtime}")
        logger.info(f"  Scans: {self.stats['scans']}")
        logger.info(f"  Opportunities found: {self.stats['opportunities_found']}")
        logger.info(f"  Trades executed: {self.stats['trades_executed']}")
        logger.info(f"  Total expected profit: {format_currency(self.stats['total_profit'])}")
        
        if self.paper_trading and hasattr(self.client, 'get_statistics'):
            stats = self.client.get_statistics()
            logger.info(f"  Current balance: {format_currency(stats['current_balance'])}")
            logger.info(f"  Completed trades: {stats['completed_trades']}")
            if stats['total_invested'] > 0:
                logger.info(f"  ROI: {stats['roi']:.2f}%")
        
        logger.info("=" * 50)
    
    def shutdown(self, signum=None, frame=None):
        """Graceful shutdown"""
        logger.info("Shutting down bot...")
        self.running = False
        self.log_stats()
    
    async def run(self):
        """Main bot loop"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        
        # Initialize
        self.initialize()
        
        # Start scanning
        await self.scan_for_arbitrage()


def main():
    """Entry point"""
    # Check for paper trading mode
    paper_trading = os.getenv("PAPER_TRADING", "false").lower() == "true"
    
    if paper_trading:
        logger.info("Starting bot in PAPER TRADING mode")
    else:
        logger.warning("Starting bot in LIVE TRADING mode - real money at risk!")
        response = input("Continue with live trading? (yes/no): ")
        if response.lower() != 'yes':
            logger.info("Aborted by user")
            sys.exit(0)
    
    bot = ArbitrageBot(paper_trading=paper_trading)
    
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

