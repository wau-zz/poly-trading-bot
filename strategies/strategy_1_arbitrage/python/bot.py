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
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..', 'shared', 'python'))

from dotenv import load_dotenv
from polymarket_client import PolyMarketClient
from utils import setup_logging, format_currency, format_percentage
from detector import ArbitrageDetector
from executor import ArbitrageExecutor

# Load environment variables
load_dotenv()

# Setup logging
setup_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_file=os.getenv("LOG_FILE", "logs/arbitrage_bot.log")
)

logger = logging.getLogger(__name__)


class ArbitrageBot:
    """Main arbitrage trading bot"""
    
    def __init__(self):
        """Initialize the arbitrage bot"""
        self.running = True
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
            'start_time': datetime.now()
        }
    
    def initialize(self):
        """Initialize API client and components"""
        try:
            logger.info("Initializing PolyMarket Arbitrage Bot...")
            
            # Initialize client
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
            
            if balance < 100:
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
                        logger.info(f"✅ Trade executed! Expected profit: {format_currency(result['expected_profit'])}")
                
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
        logger.info("=" * 50)
        logger.info("Bot Statistics:")
        logger.info(f"  Runtime: {runtime}")
        logger.info(f"  Scans: {self.stats['scans']}")
        logger.info(f"  Opportunities found: {self.stats['opportunities_found']}")
        logger.info(f"  Trades executed: {self.stats['trades_executed']}")
        logger.info(f"  Total expected profit: {format_currency(self.stats['total_profit'])}")
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
    bot = ArbitrageBot()
    
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

