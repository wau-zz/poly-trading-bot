"""
Common utility functions
"""
import logging
from datetime import datetime
from typing import Dict, Any
import json

logger = logging.getLogger(__name__)


def setup_logging(log_level: str = "INFO", log_file: str = None):
    """
    Setup logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for logging
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            *([logging.FileHandler(log_file)] if log_file else [])
        ]
    )


def calculate_profit_margin(yes_price: float, no_price: float, fee_rate: float = 0.02) -> tuple:
    """
    Calculate if arbitrage is profitable after fees
    
    Args:
        yes_price: Price of YES shares
        no_price: Price of NO shares
        fee_rate: Trading fee rate (default 2%)
        
    Returns:
        Tuple of (is_profitable, profit_margin)
    """
    total_cost = yes_price + no_price
    fees = total_cost * fee_rate
    total_cost_with_fees = total_cost + fees
    
    # Need at least 1% profit after fees to be worthwhile
    min_profit_threshold = 0.01
    
    if total_cost_with_fees < (1.0 - min_profit_threshold):
        profit_margin = 1.0 - total_cost_with_fees
        return True, profit_margin
    
    return False, 0.0


def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"${amount:,.2f}"


def format_percentage(value: float) -> str:
    """Format value as percentage"""
    return f"{value * 100:.2f}%"


def log_trade(trade_data: Dict[str, Any], log_file: str = "trades.json"):
    """
    Log trade to file
    
    Args:
        trade_data: Dictionary containing trade information
        log_file: File path to log to
    """
    trade_data['timestamp'] = datetime.now().isoformat()
    
    try:
        # Read existing trades
        try:
            with open(log_file, 'r') as f:
                trades = json.load(f)
        except FileNotFoundError:
            trades = []
        
        # Append new trade
        trades.append(trade_data)
        
        # Write back
        with open(log_file, 'w') as f:
            json.dump(trades, f, indent=2)
            
    except Exception as e:
        logger.error(f"Error logging trade: {e}")

