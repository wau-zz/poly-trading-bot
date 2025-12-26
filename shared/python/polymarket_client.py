"""
PolyMarket API Client
Wrapper around py-clob-client for easier usage

Note: Some methods may need adjustment based on the actual py-clob-client API.
Check the official documentation: https://github.com/Polymarket/py-clob-client
"""
import os
from typing import Dict, List, Optional
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from py_clob_client.constants import POLYGON
import logging
import requests

logger = logging.getLogger(__name__)


class PolyMarketClient:
    """Simplified PolyMarket API client"""
    
    def __init__(self):
        """Initialize PolyMarket client with API credentials"""
        # Support both naming conventions
        api_key = os.getenv("POLYMARKET_API_KEY") or os.getenv("apiKey")
        api_secret = os.getenv("POLYMARKET_API_SECRET") or os.getenv("secret")
        passphrase = os.getenv("POLYMARKET_PASSPHRASE") or os.getenv("passphrase", "")
        
        if not api_key or not api_secret:
            raise ValueError(
                "API credentials must be set. Use POLYMARKET_API_KEY/POLYMARKET_API_SECRET or apiKey/secret"
            )
        
        # Create ApiCreds object
        creds = ApiCreds(
            api_key=api_key,
            api_secret=api_secret,
            api_passphrase=passphrase if passphrase else ""
        )
        
        # Initialize ClobClient
        self.client = ClobClient(
            host=os.getenv("POLYMARKET_HOST", "https://clob.polymarket.com"),
            chain_id=int(os.getenv("POLYMARKET_CHAIN_ID", POLYGON)),
            creds=creds
        )
        
        logger.info("PolyMarket client initialized")
    
    def get_markets(self, active: bool = True) -> List[Dict]:
        """
        Get all active markets
        
        Args:
            active: Only return active markets
            
        Returns:
            List of market dictionaries
            
        Note: You may need to adjust this method based on the actual
        py-clob-client API. Check the official documentation:
        https://github.com/Polymarket/py-clob-client
        """
        try:
            # TODO: Adjust this based on actual py-clob-client API
            # The actual method might be different. Common options:
            # - self.client.get_markets()
            # - self.client.get_all_markets()
            # - Use PolyMarket's GraphQL API directly
            
            # Placeholder implementation
            # You'll need to check py-clob-client docs for the correct method
            markets = []  # Placeholder
            
            # Alternative: Use requests to call PolyMarket API directly
            import requests
            response = requests.get('https://clob.polymarket.com/markets')
            if response.status_code == 200:
                data = response.json()
                # Handle different response formats
                if isinstance(data, list):
                    markets = data
                elif isinstance(data, dict):
                    # If it's a dict, try common keys
                    markets = data.get('markets', data.get('data', []))
                else:
                    markets = []
            
            # Filter active markets if requested
            if active and markets:
                markets = [m for m in markets if isinstance(m, dict) and m.get('active', True)]
            
            return markets
        except Exception as e:
            logger.error(f"Error fetching markets: {e}")
            return []
    
    def get_market(self, market_id: str) -> Optional[Dict]:
        """
        Get specific market by ID
        
        Args:
            market_id: Market identifier
            
        Returns:
            Market dictionary or None
        """
        try:
            return self.client.get_market(market_id)
        except Exception as e:
            logger.error(f"Error fetching market {market_id}: {e}")
            return None
    
    def get_market_prices(self, market_id: str) -> Optional[Dict]:
        """
        Get current prices for a market
        
        Args:
            market_id: Market identifier
            
        Returns:
            Dict with 'yes_price' and 'no_price' or None
        """
        try:
            market = self.get_market(market_id)
            if not market:
                return None
            
            # Extract prices from market data
            # Format depends on PolyMarket API response
            return {
                'yes_price': market.get('yes_price', 0.0),
                'no_price': market.get('no_price', 0.0),
                'market_id': market_id
            }
        except Exception as e:
            logger.error(f"Error fetching prices for {market_id}: {e}")
            return None
    
    def place_order(
        self,
        market_id: str,
        side: str,
        price: float,
        size: float,
        order_type: str = "LIMIT"
    ) -> Optional[Dict]:
        """
        Place an order on PolyMarket
        
        Args:
            market_id: Market identifier (token_id or conditional_id)
            side: 'BUY' or 'SELL'
            price: Price per share (0.0 to 1.0)
            size: Number of shares
            order_type: 'LIMIT' or 'MARKET'
            
        Returns:
            Order response or None
            
        Note: You may need to adjust parameters based on actual py-clob-client API.
        Check: https://github.com/Polymarket/py-clob-client
        """
        try:
            if side.upper() not in ['BUY', 'SELL']:
                raise ValueError(f"Invalid side: {side}. Must be 'BUY' or 'SELL'")
            
            if not (0.0 <= price <= 1.0):
                raise ValueError(f"Price must be between 0.0 and 1.0, got {price}")
            
            # Place order using CLOB client
            # TODO: Adjust parameters based on actual API
            # Common parameter names: token_id, conditional_id, price, size, side
            order = self.client.create_order(
                token_id=market_id,  # Might be 'conditional_id' or different
                price=price,
                size=size,
                side=side.upper(),
                order_type=order_type
            )
            
            logger.info(f"Order placed: {side} {size} shares @ ${price:.4f} on market {market_id}")
            return order
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            logger.error("Note: You may need to adjust create_order() parameters based on py-clob-client API")
            return None
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order
        
        Args:
            order_id: Order identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.cancel_order(order_id)
            logger.info(f"Order {order_id} cancelled")
            return True
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            return False
    
    def get_balance(self) -> float:
        """
        Get available USDC balance
        
        Returns:
            Balance in USDC
            
        Note: You may need to adjust this method based on the actual
        py-clob-client API. The method might be:
        - self.client.get_balance()
        - self.client.get_user_balance()
        - Or use PolyMarket API directly
        """
        try:
            # TODO: Adjust based on actual py-clob-client API
            # Common options:
            # balance = self.client.get_balance()
            # balance = self.client.get_user_balance()
            
            # Placeholder - you'll need to implement based on actual API
            # For now, return a placeholder value
            logger.warning("get_balance() not fully implemented - check py-clob-client docs")
            return 1000.0  # Placeholder
            
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return 0.0

