"""
Data Fetcher for Wallet Basket Strategy
Fetches wallet data from PolyMarket subgraph and API
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import requests
import sys
import os

# Add shared modules to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
shared_python_path = os.path.join(project_root, 'shared', 'python')
if os.path.exists(shared_python_path) and shared_python_path not in sys.path:
    sys.path.insert(0, shared_python_path)

logger = logging.getLogger(__name__)


class PolyMarketSubgraphClient:
    """
    Client for PolyMarket's The Graph subgraph
    Provides access to on-chain trade data
    
    PolyMarket uses Goldsky-hosted subgraphs:
    - Orders Subgraph: orderbook-subgraph
    - Positions Subgraph: positions-subgraph
    - Activity Subgraph: activity-subgraph
    - Open Interest Subgraph: oi-subgraph
    - PNL Subgraph: pnl-subgraph
    """
    
    # Goldsky-hosted PolyMarket subgraphs
    BASE_URL = "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs"
    
    # Default to activity subgraph (has trade data)
    ACTIVITY_SUBGRAPH = f"{BASE_URL}/activity-subgraph/0.0.4/gn"
    ORDERBOOK_SUBGRAPH = f"{BASE_URL}/orderbook-subgraph/0.0.1/gn"
    POSITIONS_SUBGRAPH = f"{BASE_URL}/positions-subgraph/0.0.7/gn"
    
    # Default subgraph URL
    SUBGRAPH_URL = ACTIVITY_SUBGRAPH
    
    def __init__(self, subgraph_url: Optional[str] = None):
        """
        Initialize subgraph client
        
        Args:
            subgraph_url: Custom subgraph URL (optional)
        """
        self.subgraph_url = subgraph_url or os.getenv("POLYMARKET_SUBGRAPH_URL", self.SUBGRAPH_URL)
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
        })
    
    def query(self, query: str, variables: Optional[Dict] = None) -> Optional[Dict]:
        """
        Execute GraphQL query
        
        Args:
            query: GraphQL query string
            variables: Query variables
            
        Returns:
            Query response dict or None
        """
        try:
            payload = {
                'query': query,
                'variables': variables or {}
            }
            
            response = self.session.post(
                self.subgraph_url,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'errors' in data:
                    logger.error(f"GraphQL errors: {data['errors']}")
                    return None
                return data.get('data')
            else:
                logger.error(f"Subgraph query failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error executing subgraph query: {e}", exc_info=True)
            return None
    
    def get_wallet_trades(
        self,
        wallet_address: str,
        since: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict]:
        """
        Get trades for a wallet using redemptions (completed trades)
        
        Args:
            wallet_address: Wallet address
            since: Only get trades since this date
            limit: Maximum number of trades to return
            
        Returns:
            List of trade dicts
        """
        # Use redemptions to get wallet trading activity
        # Redemptions represent completed trades where wallet redeemed shares
        if since:
            # Query with timestamp filter
            query = """
            query GetWalletRedemptions($wallet: String!, $since: BigInt, $limit: Int) {
                redemptions(
                    where: {
                        redeemer: $wallet,
                        timestamp_gte: $since
                    }
                    orderBy: timestamp
                    orderDirection: desc
                    first: $limit
                ) {
                    id
                    redeemer
                    condition
                    payout
                    timestamp
                }
            }
            """
            variables = {
                'wallet': wallet_address.lower(),
                'limit': limit,
                'since': int(since.timestamp())
            }
        else:
            # Query without timestamp filter
            query = """
            query GetWalletRedemptions($wallet: String!, $limit: Int) {
                redemptions(
                    where: {
                        redeemer: $wallet
                    }
                    orderBy: timestamp
                    orderDirection: desc
                    first: $limit
                ) {
                    id
                    redeemer
                    condition
                    payout
                    timestamp
                }
            }
            """
            variables = {
                'wallet': wallet_address.lower(),
                'limit': limit
            }
        
        data = self.query(query, variables)
        
        if not data or 'redemptions' not in data:
            return []
        
        trades = []
        for redemption in data['redemptions']:
            # Extract outcome from redemption ID (format: txHash_outcomeIndex)
            redemption_id = redemption.get('id', '')
            outcome_index = None
            if '_' in redemption_id:
                try:
                    outcome_index = int(redemption_id.split('_')[-1], 16)  # Hex to int
                except:
                    pass
            
            trades.append({
                'id': redemption.get('id'),
                'wallet': redemption.get('redeemer', '').lower(),
                'market_id': redemption.get('condition', ''),  # Condition ID
                'outcome': 'YES' if outcome_index == 0 else 'NO' if outcome_index == 1 else 'UNKNOWN',
                'outcome_index': outcome_index,
                'price': None,  # Not available in redemptions
                'size': float(redemption.get('payout', 0)) / 1e18 if redemption.get('payout') else 0.0,  # Payout in wei
                'timestamp': datetime.fromtimestamp(int(redemption.get('timestamp', 0))),
                'tx_hash': redemption_id.split('_')[0] if '_' in redemption_id else None,
                'market_topic': None,  # Will be enriched later
                'payout': float(redemption.get('payout', 0)) / 1e18  # Payout in USDC
            })
        
        return trades
    
    def get_top_traders(self, limit: int = 1000, min_trades: int = 20) -> List[str]:
        """
        Get list of top traders by redemption count (completed trades)
        
        Args:
            limit: Maximum number of traders
            min_trades: Minimum number of trades required
            
        Returns:
            List of wallet addresses
        """
        # Get redemptions and aggregate by wallet
        # This gives us wallets with most completed trades
        query = """
        query GetTopTraders($limit: Int) {
            redemptions(
                orderBy: timestamp
                orderDirection: desc
                first: $limit
            ) {
                redeemer
            }
        }
        """
        
        variables = {
            'limit': min(limit * 10, 10000)  # Get more to find top traders
        }
        
        data = self.query(query, variables)
        
        if not data or 'redemptions' not in data:
            return []
        
        # Count redemptions per wallet
        from collections import Counter
        wallet_counts = Counter(r['redeemer'].lower() for r in data['redemptions'])
        
        # Filter by min_trades and return top wallets
        top_wallets = [
            wallet for wallet, count in wallet_counts.most_common(limit)
            if count >= min_trades
        ]
        
        return top_wallets
    
    def get_market_trades(
        self,
        market_id: str,
        since: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict]:
        """
        Get all trades (redemptions) for a market
        
        Args:
            market_id: Market condition_id
            since: Only get trades since this date
            limit: Maximum number of trades
            
        Returns:
            List of trade dicts
        """
        query = """
        query GetMarketRedemptions($condition: String!, $since: BigInt, $limit: Int) {
            redemptions(
                where: {
                    condition: $condition,
                    timestamp_gte: $since
                }
                orderBy: timestamp
                orderDirection: desc
                first: $limit
            ) {
                id
                redeemer
                condition
                payout
                timestamp
            }
        }
        """
        
        variables = {
            'condition': market_id.lower(),
            'limit': limit
        }
        
        if since:
            variables['since'] = int(since.timestamp())
        
        data = self.query(query, variables)
        
        if not data or 'redemptions' not in data:
            return []
        
        trades = []
        for redemption in data['redemptions']:
            # Extract outcome from redemption ID
            redemption_id = redemption.get('id', '')
            outcome_index = None
            if '_' in redemption_id:
                try:
                    outcome_index = int(redemption_id.split('_')[-1], 16)
                except:
                    pass
            
            trades.append({
                'id': redemption.get('id'),
                'wallet': redemption.get('redeemer', '').lower(),
                'market_id': redemption.get('condition', ''),
                'outcome': 'YES' if outcome_index == 0 else 'NO' if outcome_index == 1 else 'UNKNOWN',
                'price': None,
                'size': float(redemption.get('payout', 0)) / 1e18,
                'timestamp': datetime.fromtimestamp(int(redemption.get('timestamp', 0))),
                'tx_hash': redemption_id.split('_')[0] if '_' in redemption_id else None,
                'payout': float(redemption.get('payout', 0)) / 1e18
            })
        
        return trades


class PolyMarketAPIClient:
    """
    Client for PolyMarket REST API
    Provides access to market and wallet data
    """
    
    API_BASE = "https://api.polymarket.com"  # Placeholder - actual API may differ
    GAMMA_API_BASE = "https://gamma-api.polymarket.com"
    
    def __init__(self):
        """Initialize API client"""
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
        })
    
    def get_wallet_stats(self, wallet_address: str) -> Optional[Dict]:
        """
        Get wallet statistics from API
        
        Args:
            wallet_address: Wallet address
            
        Returns:
            Wallet stats dict or None
        """
        # PolyMarket may have a wallet stats endpoint
        # This is a placeholder - actual endpoint may differ
        try:
            url = f"{self.API_BASE}/wallets/{wallet_address.lower()}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.debug(f"Wallet stats not available for {wallet_address[:10]}...")
                return None
                
        except Exception as e:
            logger.debug(f"Error fetching wallet stats: {e}")
            return None
    
    def get_market_topic(self, market_id: str) -> Optional[str]:
        """
        Determine market topic/category
        
        Args:
            market_id: Market condition_id
            
        Returns:
            Topic string (e.g., 'geopolitics', 'crypto', 'sports') or None
        """
        try:
            # Use Gamma API to get market details
            url = f"{self.GAMMA_API_BASE}/markets"
            params = {'conditionId': market_id}
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                markets = response.json()
                if markets and isinstance(markets, list) and len(markets) > 0:
                    market = markets[0]
                    
                    # Determine topic from question/tags
                    question = market.get('question', '').lower()
                    tags = market.get('tags', [])
                    
                    # Simple topic detection (can be improved with ML)
                    topic = self._classify_topic(question, tags)
                    return topic
            
            return None
            
        except Exception as e:
            logger.debug(f"Error determining market topic: {e}")
            return None
    
    def _classify_topic(self, question: str, tags: List[str]) -> str:
        """
        Classify market topic from question and tags
        
        Args:
            question: Market question text
            tags: Market tags
            
        Returns:
            Topic string
        """
        # Simple keyword-based classification
        # Can be improved with ML/NLP
        
        geopolitics_keywords = [
            'election', 'president', 'war', 'ukraine', 'russia', 'china', 'taiwan',
            'congress', 'senate', 'house', 'trump', 'biden', 'political', 'geopolitical'
        ]
        
        crypto_keywords = [
            'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'cryptocurrency',
            'price', 'market cap', 'defi', 'nft'
        ]
        
        sports_keywords = [
            'nfl', 'nba', 'mlb', 'soccer', 'football', 'basketball', 'baseball',
            'championship', 'super bowl', 'world cup', 'playoff'
        ]
        
        all_text = (question + ' ' + ' '.join(tags)).lower()
        
        if any(keyword in all_text for keyword in geopolitics_keywords):
            return 'geopolitics'
        elif any(keyword in all_text for keyword in crypto_keywords):
            return 'crypto'
        elif any(keyword in all_text for keyword in sports_keywords):
            return 'sports'
        else:
            return 'general'


class WalletDataFetcher:
    """
    Unified data fetcher that uses both subgraph and API
    """
    
    def __init__(self):
        """Initialize data fetcher"""
        self.subgraph = PolyMarketSubgraphClient()
        self.api = PolyMarketAPIClient()
    
    def fetch_wallet_trades(
        self,
        wallet_address: str,
        since: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Fetch trades for a wallet
        
        Args:
            wallet_address: Wallet address
            since: Only get trades since this date
            
        Returns:
            List of trade dicts
        """
        # Try subgraph first (more comprehensive)
        trades = self.subgraph.get_wallet_trades(wallet_address, since=since)
        
        # Enrich with market topics (batch for efficiency)
        market_ids = {t.get('market_id') for t in trades if t.get('market_id') and not t.get('market_topic')}
        market_topics = {}
        
        for market_id in market_ids:
            topic = self.api.get_market_topic(market_id)
            if topic:
                market_topics[market_id] = topic
        
        # Add topics to trades
        for trade in trades:
            market_id = trade.get('market_id')
            if market_id and market_id in market_topics:
                trade['market_topic'] = market_topics[market_id]
        
        return trades
    
    def fetch_wallet_stats(self, wallet_address: str) -> Optional[Dict]:
        """
        Fetch comprehensive wallet statistics
        
        Args:
            wallet_address: Wallet address
            
        Returns:
            Wallet stats dict
        """
        # Get trades
        trades = self.fetch_wallet_trades(wallet_address)
        
        if not trades:
            return None
        
        # Calculate statistics
        stats = self._calculate_wallet_stats(wallet_address, trades)
        
        # Try to get additional stats from API
        api_stats = self.api.get_wallet_stats(wallet_address)
        if api_stats:
            stats.update(api_stats)
        
        return stats
    
    def _calculate_wallet_stats(self, wallet_address: str, trades: List[Dict]) -> Dict:
        """
        Calculate wallet statistics from trades
        
        Args:
            wallet_address: Wallet address
            trades: List of trade dicts
            
        Returns:
            Wallet stats dict
        """
        if not trades:
            return {}
        
        # Sort by timestamp
        trades_sorted = sorted(trades, key=lambda t: t.get('timestamp', datetime.min))
        
        first_trade_date = trades_sorted[0].get('timestamp')
        last_trade_date = trades_sorted[-1].get('timestamp')
        
        # Calculate totals
        total_trades = len(trades)
        # For redemptions, use payout as volume (price is not available)
        total_volume = sum(
            (t.get('size', 0) * t.get('price', 0)) if t.get('price') else t.get('payout', 0)
            for t in trades
        )
        
        # Group by topic
        topics = {}
        for trade in trades:
            topic = trade.get('market_topic', 'general')
            topics[topic] = topics.get(topic, 0) + 1
        
        # Determine primary topic
        primary_topic = max(topics.items(), key=lambda x: x[1])[0] if topics else None
        
        # Calculate win/loss (would need resolved markets)
        # TODO: Query resolved markets to determine wins/losses
        # For now, we can't calculate actual win rates without resolution data
        # This would require:
        # 1. Getting list of resolved markets
        # 2. Matching trades to resolved outcomes
        # 3. Calculating profit/loss
        
        wins = 0
        losses = 0
        total_profit = 0.0
        
        # Calculate win rates by time period
        now = datetime.now()
        trades_7d = [t for t in trades if t.get('timestamp') and (now - t['timestamp']).days <= 7]
        trades_30d = [t for t in trades if t.get('timestamp') and (now - t['timestamp']).days <= 30]
        
        # Placeholder win rates (would need actual resolution data from PNL subgraph)
        # Alternative: Use PNL subgraph to get actual win/loss data
        win_rate_all_time = wins / total_trades if total_trades > 0 else 0.0
        win_rate_7d = wins / len(trades_7d) if trades_7d else 0.0
        win_rate_30d = wins / len(trades_30d) if trades_30d else 0.0
        
        return {
            'wallet': wallet_address.lower(),
            'first_trade_date': first_trade_date,
            'last_trade_date': last_trade_date,
            'total_trades': total_trades,
            'total_volume': total_volume,
            'wins': wins,
            'losses': losses,
            'win_rate_all_time': win_rate_all_time,
            'win_rate_7d': win_rate_7d,
            'win_rate_30d': win_rate_30d,
            'total_profit': total_profit,
            'markets_traded': len(set(t.get('market_id') for t in trades)),
            'topics': list(topics.keys()),
            'primary_topic': primary_topic,
            'trades': trades
        }
    
    def fetch_top_traders(self, limit: int = 1000, min_trades: int = 5) -> List[str]:
        """
        Fetch top traders by redemption count
        
        Args:
            limit: Number of traders to fetch
            min_trades: Minimum number of trades required
            
        Returns:
            List of wallet addresses
        """
        return self.subgraph.get_top_traders(limit=limit, min_trades=min_trades)
    
    def fetch_market_trades(
        self,
        market_id: str,
        since: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Fetch all trades for a market
        
        Args:
            market_id: Market condition_id
            since: Only get trades since this date
            
        Returns:
            List of trade dicts
        """
        trades = self.subgraph.get_market_trades(market_id, since=since)
        
        # Add market topic
        topic = self.api.get_market_topic(market_id)
        for trade in trades:
            trade['market_topic'] = topic
        
        return trades

