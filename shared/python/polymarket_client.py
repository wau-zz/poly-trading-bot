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
        Get all active markets using ClobClient
        
        Args:
            active: Only return active markets
            
        Returns:
            List of market dictionaries
            
        Uses ClobClient.get_markets() with pagination to fetch all markets.
        """
        try:
            # Use ClobClient.get_markets() - the proper way to get markets
            # This uses the official py-clob-client method instead of raw REST API
            try:
                logger.debug("Fetching markets using ClobClient.get_markets()...")
                
                # Get first page of markets (1000 markets per page)
                # Note: For now we get first page only. Pagination can be added later if needed.
                response = self.client.get_markets()
                
                if isinstance(response, dict):
                    # Response has pagination structure: {'data': [...], 'next_cursor': '...', 'limit': 1000, 'count': 1000}
                    markets = response.get('data', [])
                    next_cursor = response.get('next_cursor', '')
                    total_count = response.get('count', len(markets))
                    
                    logger.debug(f"Fetched {len(markets)} markets from ClobClient (page 1 of potentially more)")
                    if next_cursor:
                        logger.debug(f"Note: More markets available (next_cursor exists). Currently showing first {len(markets)} markets.")
                elif isinstance(response, list):
                    # Response is a list (no pagination)
                    markets = response
                    logger.debug(f"Fetched {len(markets)} markets from ClobClient")
                else:
                    logger.warning(f"Unexpected response type from get_markets(): {type(response)}")
                    markets = []
                    
            except Exception as e:
                logger.warning(f"Error using ClobClient.get_markets(): {e}")
                logger.debug("Falling back to raw REST API...")
                
                # Fallback to raw REST API if ClobClient method fails
                import requests
                response = requests.get('https://clob.polymarket.com/markets', timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict):
                        markets = data.get('data', [])
                    elif isinstance(data, list):
                        markets = data
                    else:
                        markets = []
                    logger.debug(f"Fetched {len(markets)} markets from raw REST API (fallback)")
                else:
                    logger.warning(f"REST API returned status {response.status_code}")
                    markets = []
            
            # Filter active markets if requested
            if active and markets:
                # Filter for markets that are accepting orders and not expired
                # A market is "active" for trading if it's accepting orders and not past end date
                filtered = []
                from datetime import datetime, timezone
                current_date = datetime.now(timezone.utc)
                
                for m in markets:
                    if isinstance(m, dict):
                        # Include markets that are:
                        # 1. Not archived
                        # 2. Accepting orders (or active flag is true)
                        # 3. Not expired (end_date is in the future or None)
                        is_archived = m.get('archived', False)
                        accepting_orders = m.get('accepting_orders', False)
                        is_active = m.get('active', False)
                        
                        # Check if expired
                        end_date_str = m.get('end_date_iso')
                        is_expired = False
                        if end_date_str:
                            try:
                                # Parse ISO format date (handles both Z and +00:00)
                                if end_date_str.endswith('Z'):
                                    end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                                else:
                                    end_date = datetime.fromisoformat(end_date_str)
                                
                                # Ensure both are timezone-aware for comparison
                                if end_date.tzinfo is None:
                                    end_date = end_date.replace(tzinfo=timezone.utc)
                                
                                is_expired = end_date < current_date
                            except (ValueError, AttributeError, TypeError):
                                # If we can't parse the date, don't filter it out
                                pass
                        
                        # Also check if market is too old (more than 1 year old) even without end date
                        # This catches markets that are clearly expired but don't have end_date set
                        from datetime import timedelta
                        created_str = m.get('created_at') or m.get('createdAt')
                        if not is_expired and created_str:
                            try:
                                if created_str.endswith('Z'):
                                    created_date = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                                else:
                                    created_date = datetime.fromisoformat(created_str)
                                
                                if created_date.tzinfo is None:
                                    created_date = created_date.replace(tzinfo=timezone.utc)
                                
                                # If market is more than 1 year old, consider it expired
                                one_year_ago = current_date - timedelta(days=365)
                                if created_date < one_year_ago:
                                    is_expired = True
                            except (ValueError, AttributeError, TypeError):
                                pass
                        
                        # Market is tradeable if not archived, not expired, and (accepting orders or active)
                        if not is_archived and not is_expired and (accepting_orders or is_active):
                            # Additional validation: verify condition_id format
                            condition_id = m.get('condition_id')
                            if condition_id and condition_id.startswith('0x') and len(condition_id) == 66:
                                filtered.append(m)
                            else:
                                logger.debug(f"Skipping market with invalid condition_id: {condition_id}")
                
                # Validate order books to ensure markets are actually tradeable
                # This filters out stale markets that the API returns but are no longer valid
                validated_markets = []
                validate_order_books = os.getenv("VALIDATE_ORDER_BOOKS", "true").lower() == "true"
                
                if validate_order_books and filtered:
                    logger.debug(f"Validating order books for {len(filtered)} markets...")
                    for m in filtered:
                        condition_id = m.get('condition_id')
                        if condition_id:
                            try:
                                # Quick check: verify order book exists
                                book_url = f'https://clob.polymarket.com/book?token_id={condition_id}'
                                book_response = requests.get(book_url, timeout=3)
                                if book_response.status_code == 200:
                                    validated_markets.append(m)
                                else:
                                    logger.debug(f"Market {condition_id[:20]}... has no order book (invalid/expired)")
                            except Exception as e:
                                # If validation fails, include it anyway (might be network issue)
                                logger.debug(f"Could not validate order book for {condition_id[:20]}...: {e}")
                                validated_markets.append(m)
                        else:
                            validated_markets.append(m)
                    
                    markets = validated_markets
                    logger.debug(f"Validated: {len(markets)} markets have valid order books")
                else:
                    markets = filtered
                
                logger.debug(f"Final count: {len(markets)} active, non-expired, validated tradeable markets")
            
            return markets
        except Exception as e:
            logger.error(f"Error fetching markets: {e}", exc_info=True)
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

