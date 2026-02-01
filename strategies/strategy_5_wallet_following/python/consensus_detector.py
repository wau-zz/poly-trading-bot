"""
Consensus Signal Detector
Detects when wallet basket reaches consensus (80%+ agreement)
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import sys
import os

# Add shared modules to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
shared_python_path = os.path.join(project_root, 'shared', 'python')
if os.path.exists(shared_python_path) and shared_python_path not in sys.path:
    sys.path.insert(0, shared_python_path)

logger = logging.getLogger(__name__)


class ConsensusSignalDetector:
    """
    Detects when wallet basket reaches consensus (80%+ agreement)
    """
    
    CONSENSUS_THRESHOLD = 0.80  # 80%+ of basket must agree
    PRICE_BAND_TOLERANCE = 0.02  # All buying within 2% price band
    MAX_SPREAD_COOKED = 0.05  # Don't trade if spread already moved >5%
    MIN_BASKET_PARTICIPATION = 0.50  # Need at least 50% of basket to have traded
    
    def __init__(self, basket: List[Dict]):
        """
        Initialize consensus detector
        
        Args:
            basket: List of wallet dicts in the basket
        """
        self.basket = basket
        self.basket_wallets = {w['wallet'] for w in basket}
    
    def get_basket_trades(self, market_id: str, since: Optional[datetime] = None) -> List[Dict]:
        """
        Get all recent trades from basket wallets for a market
        
        Args:
            market_id: Market condition_id
            since: Only get trades since this date
            
        Returns:
            List of trade dicts from basket wallets
        """
        try:
            from data_fetcher import WalletDataFetcher
            fetcher = WalletDataFetcher()
            
            # Get all trades for this market
            all_trades = fetcher.fetch_market_trades(market_id, since=since)
            
            # Filter to only basket wallets
            basket_trades = [
                t for t in all_trades
                if t.get('wallet', '').lower() in self.basket_wallets
            ]
            
            return basket_trades
            
        except ImportError:
            logger.warning("data_fetcher not available, returning empty list")
            return []
    
    def detect_consensus(self, market_id: str, get_market_price_func=None) -> Optional[Dict]:
        """
        Check if basket has reached consensus on a market
        
        Args:
            market_id: Market condition_id
            get_market_price_func: Function to get current market price
            
        Returns:
            Consensus signal dict or None if no consensus
        """
        # Get all recent trades from basket wallets for this market
        since = datetime.now() - timedelta(days=7)  # Last 7 days
        basket_trades = self.get_basket_trades(market_id, since=since)
        
        if not basket_trades:
            return None
        
        # Need at least 50% of basket to have traded
        unique_wallets = {t['wallet'] for t in basket_trades}
        participation_pct = len(unique_wallets) / len(self.basket)
        
        if participation_pct < self.MIN_BASKET_PARTICIPATION:
            logger.debug(f"Market {market_id[:20]}...: Low participation ({participation_pct:.1%})")
            return None
        
        # Group by outcome (YES or NO)
        yes_trades = [t for t in basket_trades if t.get('outcome') == 'YES']
        no_trades = [t for t in basket_trades if t.get('outcome') == 'NO']
        
        total_trades = len(basket_trades)
        yes_pct = len(yes_trades) / total_trades
        no_pct = len(no_trades) / total_trades
        
        # Check if consensus reached
        if yes_pct >= self.CONSENSUS_THRESHOLD:
            outcome = 'YES'
            consensus_trades = yes_trades
            consensus_pct = yes_pct
        elif no_pct >= self.CONSENSUS_THRESHOLD:
            outcome = 'NO'
            consensus_trades = no_trades
            consensus_pct = no_pct
        else:
            logger.debug(f"Market {market_id[:20]}...: No consensus (YES: {yes_pct:.1%}, NO: {no_pct:.1%})")
            return None  # No consensus
        
        # Check price band (all buying within tight price range)
        prices = [t['price'] for t in consensus_trades if t.get('price')]
        if not prices:
            return None
        
        price_range = max(prices) - min(prices)
        avg_price = sum(prices) / len(prices)
        
        if avg_price > 0:
            price_band_pct = price_range / avg_price
            if price_band_pct > self.PRICE_BAND_TOLERANCE:
                logger.debug(f"Market {market_id[:20]}...: Prices too spread out ({price_band_pct:.1%})")
                return None  # Prices too spread out
        
        # Check if spread is "cooked" (already moved too much)
        if get_market_price_func:
            try:
                current_mid_price = get_market_price_func(market_id)
                if current_mid_price:
                    price_movement = abs(current_mid_price - avg_price) / avg_price
                    
                    if price_movement > self.MAX_SPREAD_COOKED:
                        logger.debug(f"Market {market_id[:20]}...: Spread already cooked ({price_movement:.1%} movement)")
                        return None  # Spread already moved, too late
            except Exception as e:
                logger.warning(f"Error checking market price: {e}")
        
        # Consensus signal detected!
        signal = {
            'market_id': market_id,
            'outcome': outcome,
            'consensus_pct': consensus_pct,
            'avg_entry_price': avg_price,
            'current_price': get_market_price_func(market_id) if get_market_price_func else avg_price,
            'basket_size': len(self.basket),
            'trades_count': len(consensus_trades),
            'unique_wallets': len(unique_wallets),
            'participation_pct': participation_pct,
            'price_band_pct': price_band_pct if avg_price > 0 else 0.0,
            'signal_strength': self.calculate_signal_strength(consensus_trades),
            'timestamp': datetime.now()
        }
        
        logger.info(f"🎯 CONSENSUS SIGNAL: {outcome} ({consensus_pct:.1%} consensus)")
        
        return signal
    
    def calculate_signal_strength(self, consensus_trades: List[Dict]) -> float:
        """
        Calculate signal strength based on:
        - Consensus percentage
        - Quality of wallets in consensus
        - Recency of trades
        
        Args:
            consensus_trades: List of trades that form consensus
            
        Returns:
            Signal strength (0.0 to 1.0)
        """
        if not consensus_trades:
            return 0.0
        
        # Consensus percentage
        consensus_pct = len(consensus_trades) / len(self.basket)
        
        # Weight by wallet quality (higher quality wallets = stronger signal)
        wallet_scores = []
        for trade in consensus_trades:
            wallet = trade.get('wallet')
            # Find wallet in basket
            basket_wallet = next((w for w in self.basket if w['wallet'] == wallet), None)
            if basket_wallet:
                wallet_scores.append(basket_wallet.get('weighted_win_rate', 0.5))
        
        avg_wallet_quality = sum(wallet_scores) / len(wallet_scores) if wallet_scores else 0.5
        
        # Recency (more recent = stronger)
        most_recent_trade = max(
            (t.get('timestamp', datetime.now()) for t in consensus_trades),
            default=datetime.now()
        )
        hours_ago = (datetime.now() - most_recent_trade).total_seconds() / 3600
        recency_score = max(0, 1 - (hours_ago / 24))  # Decay over 24 hours
        
        # Composite signal strength
        signal_strength = (
            min(consensus_pct, 1.0) * 0.40 +  # Consensus (capped at 1.0)
            avg_wallet_quality * 0.40 +       # Wallet quality
            recency_score * 0.20              # Recency
        )
        
        return min(1.0, signal_strength)  # Cap at 1.0

