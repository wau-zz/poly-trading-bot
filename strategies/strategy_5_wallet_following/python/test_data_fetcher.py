#!/usr/bin/env python3
"""
Test script for data fetcher integration
Tests PolyMarket subgraph and API connectivity
"""
import sys
import os
from dotenv import load_dotenv

# Add shared modules to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
shared_python_path = os.path.join(project_root, 'shared', 'python')
if os.path.exists(shared_python_path) and shared_python_path not in sys.path:
    sys.path.insert(0, shared_python_path)

# Load environment variables
env_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=env_path)

from data_fetcher import PolyMarketSubgraphClient, PolyMarketAPIClient, WalletDataFetcher
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_subgraph_connection():
    """Test subgraph connection"""
    print("=" * 80)
    print("Testing PolyMarket Subgraph Connection")
    print("=" * 80)
    
    client = PolyMarketSubgraphClient()
    
    # Test query - get recent redemptions (completed trades)
    query = """
    query {
        redemptions(
            orderBy: timestamp
            orderDirection: desc
            first: 5
        ) {
            id
            redeemer
            condition
            payout
            timestamp
        }
    }
    """
    
    print(f"Querying subgraph: {client.subgraph_url}")
    data = client.query(query)
    
    if data:
        print("✅ Subgraph connection successful!")
        redemptions = data.get('redemptions', [])
        print(f"   Found {len(redemptions)} recent redemptions")
        if redemptions:
            print(f"   Sample redemption: {redemptions[0]}")
    else:
        print("❌ Subgraph connection failed")
        print("   Note: Schema may differ - check SUBGRAPH_QUERIES.md")
    
    print()


def test_api_connection():
    """Test API connection"""
    print("=" * 80)
    print("Testing PolyMarket API Connection")
    print("=" * 80)
    
    client = PolyMarketAPIClient()
    
    # Test market topic detection
    # Use a known market
    test_market_id = "0xd8b9ff369452daebce1ac8cb6a29d6817903e85168356c72812317f38e317613"
    
    print(f"Testing market topic detection for: {test_market_id[:20]}...")
    topic = client.get_market_topic(test_market_id)
    
    if topic:
        print(f"✅ Market topic detected: {topic}")
    else:
        print("⚠️  Could not determine market topic (may need to check API)")
    
    print()


def test_wallet_fetcher():
    """Test wallet data fetcher"""
    print("=" * 80)
    print("Testing Wallet Data Fetcher")
    print("=" * 80)
    
    fetcher = WalletDataFetcher()
    
    # Test fetching top traders
    print("Fetching top traders...")
    top_traders = fetcher.fetch_top_traders(limit=10)
    
    if top_traders:
        print(f"✅ Found {len(top_traders)} top traders")
        print(f"   Sample wallets: {top_traders[:3]}")
        
        # Test fetching stats for one wallet
        if top_traders:
            test_wallet = top_traders[0]
            print(f"\nFetching stats for wallet: {test_wallet[:10]}...")
            stats = fetcher.fetch_wallet_stats(test_wallet)
            
            if stats:
                print("✅ Wallet stats fetched!")
                print(f"   Total trades: {stats.get('total_trades', 0)}")
                print(f"   Win rate: {stats.get('win_rate_all_time', 0):.1%}")
                print(f"   Primary topic: {stats.get('primary_topic', 'N/A')}")
            else:
                print("⚠️  Could not fetch wallet stats (may need schema adjustment)")
    else:
        print("⚠️  Could not fetch top traders (may need schema adjustment)")
        print("   Check SUBGRAPH_QUERIES.md for correct query format")
    
    print()


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("PolyMarket Data Fetcher Integration Tests")
    print("=" * 80 + "\n")
    
    try:
        test_subgraph_connection()
        test_api_connection()
        test_wallet_fetcher()
        
        print("=" * 80)
        print("Testing Complete")
        print("=" * 80)
        print("\nNext Steps:")
        print("1. Verify subgraph queries match actual schema")
        print("2. Test with real wallet addresses")
        print("3. Adjust queries in data_fetcher.py if needed")
        print("4. See SUBGRAPH_QUERIES.md for query examples")
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        print("\n⚠️  Some tests may have failed - this is expected if:")
        print("   - Subgraph schema differs from expected")
        print("   - API endpoints have changed")
        print("   - Network issues")
        print("\nCheck SUBGRAPH_QUERIES.md for correct query formats")


if __name__ == "__main__":
    main()

