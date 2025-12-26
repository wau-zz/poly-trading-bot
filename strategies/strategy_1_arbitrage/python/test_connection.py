#!/usr/bin/env python3
"""
Test script to verify PolyMarket API connection
Run this before starting the bot to ensure everything is configured correctly
"""
import os
import sys
from dotenv import load_dotenv

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..', 'shared', 'python'))

load_dotenv()

def test_connection():
    """Test PolyMarket API connection"""
    print("Testing PolyMarket API connection...")
    print("-" * 50)
    
    # Check environment variables
    api_key = os.getenv("POLYMARKET_API_KEY")
    api_secret = os.getenv("POLYMARKET_API_SECRET")
    
    if not api_key or not api_secret:
        print("❌ ERROR: API credentials not found!")
        print("Please set POLYMARKET_API_KEY and POLYMARKET_API_SECRET in .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    print(f"✅ API Secret found: {'*' * 20}")
    
    # Test client initialization
    try:
        from polymarket_client import PolyMarketClient
        
        print("\nInitializing client...")
        client = PolyMarketClient()
        print("✅ Client initialized successfully")
        
        # Test balance
        print("\nFetching balance...")
        balance = client.get_balance()
        print(f"✅ Balance: ${balance:,.2f}")
        
        if balance < 100:
            print("⚠️  WARNING: Low balance! Minimum $100 recommended for trading.")
        
        # Test market fetching
        print("\nFetching markets...")
        markets = client.get_markets(active=True)
        
        if markets:
            print(f"✅ Found {len(markets)} active markets")
            print(f"   Sample market: {markets[0].get('description', 'N/A')[:50]}...")
        else:
            print("⚠️  WARNING: No markets found. This might be normal if API is down.")
        
        print("\n" + "=" * 50)
        print("✅ All tests passed! You're ready to run the bot.")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nTroubleshooting:")
        print("1. Check your API keys are correct")
        print("2. Verify you have internet connection")
        print("3. Check PolyMarket API status")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

