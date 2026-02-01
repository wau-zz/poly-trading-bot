"""
Wallet Basket Builder
Builds baskets of wallets by topic/specialization with sophisticated filtering
"""
import logging
from typing import Dict, List, Optional, Set
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


class WalletBasketCriteria:
    """
    Filtering criteria for wallet baskets
    Based on analysis of 1.3M+ wallets
    """
    
    # Age requirement
    MIN_WALLET_AGE_DAYS = 180  # 6+ months old
    
    # Bot detection
    MAX_MICRO_TRADES = 1000  # Filter out wallets doing thousands of micro-trades
    MIN_AVG_TRADE_SIZE = 10.0  # Average trade must be >= $10
    
    # Performance weighting (recent > all-time)
    RECENT_WIN_RATE_WEIGHT = 0.70  # 70% weight on recent performance
    ALL_TIME_WIN_RATE_WEIGHT = 0.30  # 30% weight on all-time
    
    # Minimum performance thresholds
    MIN_WIN_RATE_ALL_TIME = 0.55  # 55% minimum all-time win rate
    MIN_WIN_RATE_RECENT = 0.50  # 50% minimum recent win rate
    MIN_TOTAL_TRADES = 20  # At least 20 trades
    
    # Copycat detection
    FILTER_COPYCAT_CLUSTERS = True  # Ignore wallets that copy each other
    
    def passes(self, wallet: Dict) -> bool:
        """
        Check if wallet passes all filters
        
        Args:
            wallet: Wallet statistics dict
            
        Returns:
            True if wallet passes all criteria
        """
        # Age check
        if wallet.get('first_trade_date'):
            wallet_age = (datetime.now() - wallet['first_trade_date']).days
            if wallet_age < self.MIN_WALLET_AGE_DAYS:
                logger.debug(f"Wallet {wallet['wallet'][:10]}... too new ({wallet_age} days)")
                return False
        
        # Bot detection
        total_trades = wallet.get('total_trades', 0)
        if total_trades > self.MAX_MICRO_TRADES:
            # Check if they're doing micro-trades (likely a bot)
            total_volume = wallet.get('total_volume', 0)
            if total_volume > 0:
                avg_trade_size = total_volume / total_trades
                if avg_trade_size < self.MIN_AVG_TRADE_SIZE:
                    logger.debug(f"Wallet {wallet['wallet'][:10]}... likely bot (avg trade: ${avg_trade_size:.2f})")
                    return False
        
        # Minimum trades check
        if total_trades < self.MIN_TOTAL_TRADES:
            logger.debug(f"Wallet {wallet['wallet'][:10]}... too few trades ({total_trades})")
            return False
        
        # Performance check
        win_rate_all_time = wallet.get('win_rate_all_time', 0.0)
        if win_rate_all_time < self.MIN_WIN_RATE_ALL_TIME:
            logger.debug(f"Wallet {wallet['wallet'][:10]}... low all-time win rate ({win_rate_all_time:.1%})")
            return False
        
        win_rate_recent = wallet.get('win_rate_30d', wallet.get('win_rate_7d', 0.0))
        if win_rate_recent < self.MIN_WIN_RATE_RECENT:
            logger.debug(f"Wallet {wallet['wallet'][:10]}... low recent win rate ({win_rate_recent:.1%})")
            return False
        
        # Copycat detection (placeholder - would need correlation analysis)
        if self.FILTER_COPYCAT_CLUSTERS:
            if self._is_copycat(wallet):
                logger.debug(f"Wallet {wallet['wallet'][:10]}... detected as copycat")
                return False
        
        return True
    
    def _is_copycat(self, wallet: Dict) -> bool:
        """
        Detect if wallet is part of a copycat cluster
        Placeholder - would need actual correlation analysis
        
        Args:
            wallet: Wallet statistics dict
            
        Returns:
            True if likely a copycat
        """
        # TODO: Implement correlation analysis
        # Check if wallet's trades correlate too highly with other wallets
        # This would require comparing trade timing and markets
        return False
    
    def calculate_weighted_win_rate(self, wallet: Dict) -> float:
        """
        Calculate win rate with recency bias
        Recent performance weighted more heavily than all-time
        
        Args:
            wallet: Wallet statistics dict
            
        Returns:
            Weighted win rate (0.0 to 1.0)
        """
        recent_7d_win_rate = wallet.get('win_rate_7d', 0.0)
        recent_30d_win_rate = wallet.get('win_rate_30d', 0.0)
        all_time_win_rate = wallet.get('win_rate_all_time', 0.0)
        
        # Weight recent performance more
        # If 7d available, use 60% 7d + 40% 30d
        # Otherwise use 30d
        if recent_7d_win_rate > 0:
            recent_win_rate = (recent_7d_win_rate * 0.6 + recent_30d_win_rate * 0.4)
        else:
            recent_win_rate = recent_30d_win_rate if recent_30d_win_rate > 0 else all_time_win_rate
        
        # Weighted average
        weighted = (
            recent_win_rate * self.RECENT_WIN_RATE_WEIGHT +
            all_time_win_rate * self.ALL_TIME_WIN_RATE_WEIGHT
        )
        
        return weighted
    
    def calculate_entry_vs_final_score(self, wallet: Dict) -> float:
        """
        Calculate score based on avg entry vs final price
        Best wallets enter at better prices relative to final outcome
        
        Args:
            wallet: Wallet statistics dict
            
        Returns:
            Score (higher is better)
        """
        # This measures how well wallets time their entries
        # Higher score = better entry timing
        
        avg_entry_vs_final = wallet.get('avg_entry_vs_final', 0.0)
        
        # Normalize to 0-1 scale
        # Positive = entered at better price than final
        # Negative = entered at worse price than final
        score = (avg_entry_vs_final + 1.0) / 2.0  # Normalize to 0-1
        
        return max(0.0, min(1.0, score))  # Clamp to 0-1


class WalletBasketBuilder:
    """
    Builds baskets of wallets by topic/specialization
    """
    
    def __init__(self, topic: str, criteria: Optional[WalletBasketCriteria] = None):
        """
        Initialize basket builder
        
        Args:
            topic: Topic/specialization (e.g., 'geopolitics', 'crypto', 'sports')
            criteria: Filtering criteria (uses default if None)
        """
        self.topic = topic.lower()
        self.criteria = criteria or WalletBasketCriteria()
        self.wallets = []
    
    def is_topic_specialist(self, wallet: Dict) -> bool:
        """
        Check if wallet specializes in this topic
        
        Args:
            wallet: Wallet statistics dict
            
        Returns:
            True if wallet is a topic specialist
        """
        # Check if wallet's trades are primarily in this topic
        topics = wallet.get('topics', [])
        
        if not topics:
            return False
        
        # Count trades by topic
        topic_counts = {}
        for trade in wallet.get('trades', []):
            trade_topic = trade.get('market_topic', '').lower()
            topic_counts[trade_topic] = topic_counts.get(trade_topic, 0) + 1
        
        # Check if this topic is dominant (>= 50% of trades)
        total_trades = sum(topic_counts.values())
        if total_trades == 0:
            return False
        
        topic_pct = topic_counts.get(self.topic, 0) / total_trades
        
        return topic_pct >= 0.50  # At least 50% of trades in this topic
    
    def build_basket(self, all_wallets: List[Dict], max_wallets: int = 100) -> List[Dict]:
        """
        Filter and rank wallets for this topic basket
        
        Args:
            all_wallets: List of all wallet statistics dicts
            max_wallets: Maximum number of wallets in basket
            
        Returns:
            Ranked list of wallet dicts
        """
        logger.info(f"Building {self.topic} basket from {len(all_wallets)} wallets...")
        
        filtered = []
        
        for wallet in all_wallets:
            # Filter by topic specialization
            if not self.is_topic_specialist(wallet):
                continue
            
            # Apply filtering criteria
            if not self.criteria.passes(wallet):
                continue
            
            # Calculate weighted metrics
            wallet['weighted_win_rate'] = self.criteria.calculate_weighted_win_rate(wallet)
            wallet['entry_vs_final_score'] = self.criteria.calculate_entry_vs_final_score(wallet)
            
            filtered.append(wallet)
        
        logger.info(f"Filtered to {len(filtered)} wallets matching criteria")
        
        # Rank wallets
        ranked = self.rank_wallets(filtered)
        
        # Take top N
        basket = ranked[:max_wallets]
        
        logger.info(f"Built {self.topic} basket with {len(basket)} wallets")
        
        return basket
    
    def rank_wallets(self, wallets: List[Dict]) -> List[Dict]:
        """
        Rank wallets by performance metrics
        
        Args:
            wallets: List of wallet dicts
            
        Returns:
            Ranked list (best first)
        """
        # Calculate composite score for each wallet
        for wallet in wallets:
            # Composite score combines:
            # - Weighted win rate (40%)
            # - Entry vs final score (30%)
            # - Total profit (20%)
            # - Trade count (10%)
            
            weighted_win_rate = wallet.get('weighted_win_rate', 0.0)
            entry_score = wallet.get('entry_vs_final_score', 0.0)
            total_profit = wallet.get('total_profit', 0.0)
            total_trades = wallet.get('total_trades', 0)
            
            # Normalize profit (assume max $100k for normalization)
            normalized_profit = min(total_profit / 100000.0, 1.0)
            
            # Normalize trade count (assume max 1000 trades)
            normalized_trades = min(total_trades / 1000.0, 1.0)
            
            # Composite score
            composite_score = (
                weighted_win_rate * 0.40 +
                entry_score * 0.30 +
                normalized_profit * 0.20 +
                normalized_trades * 0.10
            )
            
            wallet['composite_score'] = composite_score
        
        # Sort by composite score (highest first)
        ranked = sorted(wallets, key=lambda w: w.get('composite_score', 0.0), reverse=True)
        
        return ranked










