"""
PolyMarket API Client
Wrapper around py-clob-client for easier usage

Note: Some methods may need adjustment based on the actual py-clob-client API.
Check the official documentation: https://github.com/Polymarket/py-clob-client
"""
import os
from typing import Dict, List, Optional
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrderArgs
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
    
    def get_market_by_slug(self, slug: str) -> Optional[Dict]:
        """
        Get a specific market by its slug using Gamma API
        
        Args:
            slug: Market slug (e.g., 'openai-1t-ipo-before-2027')
            
        Returns:
            Market dictionary or None if not found
        """
        try:
            import requests
            url = f'https://gamma-api.polymarket.com/markets?slug={slug}'
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                markets = response.json()
                if isinstance(markets, list) and len(markets) > 0:
                    market = markets[0]
                    # Normalize field names
                    if 'conditionId' in market:
                        market['condition_id'] = market.pop('conditionId')
                    if 'slug' in market:
                        market['market_slug'] = market['slug']
                    if 'endDate' in market:
                        market['end_date_iso'] = market['endDate']
                    market['accepting_orders'] = market.get('active', False) and not market.get('closed', False)
                    return market
            return None
        except Exception as e:
            logger.error(f"Error fetching market by slug: {e}")
            return None
    
    def get_markets(self, active: bool = True) -> List[Dict]:
        """
        Get all active markets using Gamma API
        
        Args:
            active: Only return active markets
            
        Returns:
            List of market dictionaries
            
        Uses Gamma API (https://gamma-api.polymarket.com/markets) which is the correct
        endpoint for fetching market information. This API returns markets that exist
        on the PolyMarket website, unlike the CLOB API which may miss some markets.
        """
        try:
            import requests
            
            # Use Gamma API - the correct endpoint for market data
            # Gamma API: Use closed=false to get only active markets
            # Supports pagination with offset parameter to get all markets
            limit = int(os.getenv("GAMMA_API_LIMIT", "500"))  # Max per page is 500
            max_pages = int(os.getenv("GAMMA_API_MAX_PAGES", "10"))  # Default: fetch up to 10 pages (5000 markets)
            
            all_markets = []
            offset = 0
            
            logger.debug(f"Fetching markets using Gamma API with pagination (limit={limit}, max_pages={max_pages})...")
            
            for page in range(max_pages):
                url = f'https://gamma-api.polymarket.com/markets?limit={limit}&closed=false&offset={offset}'
                
                response = requests.get(url, timeout=15)
                if response.status_code == 200:
                    markets = response.json()
                    
                    # Gamma API returns a list directly
                    if not isinstance(markets, list):
                        logger.warning(f"Unexpected response type from Gamma API: {type(markets)}")
                        markets = []
                    
                    if len(markets) == 0:
                        # No more markets available
                        break
                    
                    all_markets.extend(markets)
                    logger.debug(f"Fetched page {page + 1}: {len(markets)} markets (total: {len(all_markets)})")
                    
                    # If we got fewer than limit, we've reached the end
                    if len(markets) < limit:
                        break
                    
                    offset += limit
                else:
                    logger.warning(f"Gamma API returned status {response.status_code} on page {page + 1}")
                    break
            
            # Normalize field names to match CLOB API format for compatibility
            # Gamma API uses: conditionId, slug, endDate, closed, active, acceptingOrders
            # CLOB API uses: condition_id, market_slug, end_date_iso, closed, active, accepting_orders
            normalized_markets = []
            for market in all_markets:
                normalized = market.copy()
                # Map Gamma API fields to CLOB API field names
                if 'conditionId' in normalized:
                    normalized['condition_id'] = normalized.pop('conditionId')
                if 'slug' in normalized:
                    normalized['market_slug'] = normalized['slug']
                if 'endDate' in normalized:
                    normalized['end_date_iso'] = normalized['endDate']
                # Use acceptingOrders from API if available, otherwise infer from active and closed
                if 'acceptingOrders' in normalized:
                    normalized['accepting_orders'] = normalized.pop('acceptingOrders')
                else:
                    # Fallback: infer from active and closed
                    normalized['accepting_orders'] = normalized.get('active', False) and not normalized.get('closed', False)
                normalized_markets.append(normalized)
            
            markets = normalized_markets
            logger.debug(f"Fetched {len(markets)} total markets from Gamma API (across {page + 1} pages)")
            if len(markets) >= max_pages * limit:
                logger.info(f"Note: Fetched maximum pages ({max_pages}). There may be more markets available. Increase GAMMA_API_MAX_PAGES to fetch more.")
            else:
                logger.warning(f"Gamma API returned status {response.status_code}")
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
                # Default to false since order book validation can filter out valid markets
                validated_markets = []
                validate_order_books = os.getenv("VALIDATE_ORDER_BOOKS", "false").lower() == "true"
                
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
        Get specific market by ID (condition_id)
        
        Args:
            market_id: Market identifier (condition_id)
            
        Returns:
            Market dictionary or None
        """
        try:
            return self.client.get_market(market_id)
        except Exception as e:
            logger.error(f"Error fetching market {market_id}: {e}")
            return None
    
    def get_token_ids(self, condition_id: str) -> Optional[Dict[str, str]]:
        """
        Get token_ids for YES and NO outcomes from a condition_id
        
        Args:
            condition_id: Market condition_id
            
        Returns:
            Dict with 'yes_token_id' and 'no_token_id' or None if not found
        """
        try:
            market = self.get_market(condition_id)
            if not market:
                return None
            
            tokens = market.get('tokens', [])
            if not tokens:
                logger.warning(f"No tokens found for condition_id {condition_id}")
                return None
            
            # Extract token_ids for YES and NO outcomes
            yes_token_id = None
            no_token_id = None
            
            for token in tokens:
                outcome = token.get('outcome', '').upper()
                token_id = token.get('token_id')
                
                if outcome == 'YES' and token_id:
                    yes_token_id = str(token_id)  # Convert to string
                elif outcome == 'NO' and token_id:
                    no_token_id = str(token_id)  # Convert to string
            
            if not yes_token_id or not no_token_id:
                logger.warning(f"Could not find both YES and NO token_ids for condition_id {condition_id}")
                logger.debug(f"Found tokens: {[t.get('outcome') for t in tokens]}")
                return None
            
            return {
                'yes_token_id': yes_token_id,
                'no_token_id': no_token_id,
                'condition_id': condition_id
            }
            
        except Exception as e:
            logger.error(f"Error getting token_ids for condition_id {condition_id}: {e}", exc_info=True)
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
            market_id: Token ID (condition_id for YES/NO shares)
            side: 'BUY' or 'SELL'
            price: Price per share (0.0 to 1.0)
            size: Number of shares
            order_type: 'LIMIT' or 'MARKET' (currently only LIMIT is supported)
            
        Returns:
            Order response dict with order_id or None if failed
            
        Note: For binary markets, you need separate token_ids for YES and NO outcomes.
        The market_id should be the token_id for the specific outcome (YES or NO).
        """
        try:
            if side.upper() not in ['BUY', 'SELL']:
                raise ValueError(f"Invalid side: {side}. Must be 'BUY' or 'SELL'")
            
            if not (0.0 <= price <= 1.0):
                raise ValueError(f"Price must be between 0.0 and 1.0, got {price}")
            
            # Create OrderArgs object (required by py-clob-client)
            order_args = OrderArgs(
                token_id=market_id,  # This should be the token_id for YES or NO outcome
                price=price,
                size=size,
                side=side.upper()
            )
            
            # Place order using CLOB client
            # create_order returns the order object, then we need to post it
            order = self.client.create_order(order_args)
            
            # Post the order to the exchange
            posted_order = self.client.post_order(order)
            
            logger.info(f"Order placed: {side} {size} shares @ ${price:.4f} on token {market_id}")
            logger.debug(f"Order ID: {posted_order.get('id', 'N/A')}")
            
            return posted_order
            
        except Exception as e:
            logger.error(f"Error placing order: {e}", exc_info=True)
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
            # py-clob-client uses cancel() method
            result = self.client.cancel(order_id)
            logger.info(f"Order {order_id} cancelled")
            return True
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}", exc_info=True)
            return False
    
    def get_balance(self) -> float:
        """
        Get available USDC balance
        
        Returns:
            Balance in USDC
            
        Note: py-clob-client doesn't have a direct get_balance() method.
        We need to query the blockchain or use the PolyMarket API.
        For now, this is a placeholder that needs implementation.
        """
        try:
            # py-clob-client doesn't have get_balance() method
            # We need to query the collateral token balance from the blockchain
            # or use PolyMarket's API directly
            
            # Option 1: Query blockchain directly using web3
            # Option 2: Use PolyMarket API endpoint
            # Option 3: Check if there's a method in py-clob-client we missed
            
            # For now, return a placeholder - this needs to be implemented
            # based on your specific needs
            logger.warning("get_balance() not fully implemented - needs blockchain query or API call")
            logger.warning("You may need to use web3.py to query USDC balance from your wallet")
            return 0.0  # Return 0 to be safe - prevents accidental trades without balance
            
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return 0.0

