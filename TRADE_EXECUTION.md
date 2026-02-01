# Trade Execution Code Overview

## How Trades Are Executed

### 1. **Detection** (`detector.py`)
The bot scans all markets and detects when:
- YES price + NO price < $0.98 (after 2% fee)
- This creates a risk-free arbitrage opportunity

### 2. **Execution Flow** (`executor.py` → `polymarket_client.py`)

```
Bot detects arbitrage
    ↓
executor.execute_arbitrage(opportunity)
    ↓
client.place_order() - YES shares
client.place_order() - NO shares
    ↓
py-clob-client.create_order(OrderArgs)
py-clob-client.post_order(order)
```

### 3. **Current Implementation**

#### `executor.py` (lines 99-114)
```python
# Place both orders simultaneously
yes_order = self.client.place_order(
    market_id=opportunity['market_id'],  # condition_id
    side='BUY',
    price=opportunity['yes_price'] * (1 + slippage),
    size=shares,
    order_type='LIMIT'
)

no_order = self.client.place_order(
    market_id=opportunity['market_id'],  # condition_id
    side='BUY',
    price=opportunity['no_price'] * (1 + slippage),
    size=shares,
    order_type='LIMIT'
)
```

#### `polymarket_client.py` (lines 316-364)
```python
def place_order(self, market_id, side, price, size, order_type="LIMIT"):
    # Create OrderArgs object
    order_args = OrderArgs(
        token_id=market_id,  # ⚠️ This needs to be the actual token_id for YES/NO
        price=price,
        size=size,
        side=side.upper()
    )
    
    # Create and post order
    order = self.client.create_order(order_args)
    posted_order = self.client.post_order(order)
    return posted_order
```

## ✅ Fixed Issues

### 1. **Token ID Problem** ✅ FIXED
**Previous Issue:** We were passing `condition_id` as `market_id`, but `place_order()` needs the actual **token_id** for YES or NO outcomes.

**Solution Implemented:**
- Added `get_token_ids(condition_id)` method to `PolyMarketClient`
- This method fetches market details and extracts token_ids from the `tokens` array
- Updated `executor.py` to fetch token_ids before placing orders
- Now correctly uses YES and NO token_ids when placing orders

**How it works:**
```python
# In executor.py
token_ids = self.client.get_token_ids(condition_id)
yes_token_id = token_ids['yes_token_id']  # Actual token_id for YES
no_token_id = token_ids['no_token_id']    # Actual token_id for NO

# Place orders with correct token_ids
yes_order = self.client.place_order(market_id=yes_token_id, ...)
no_order = self.client.place_order(market_id=no_token_id, ...)
```

### 2. **Balance Check Not Implemented**
**Current Issue:** `get_balance()` returns `0.0` (placeholder)

**Solution Needed:**
```python
# Need to query USDC balance from blockchain or API
# Options:
# 1. Use web3.py to query ERC20 balance
# 2. Use PolyMarket API endpoint
# 3. Check if py-clob-client has a method we missed
```

### 3. **Order Type Handling**
**Current Issue:** `order_type` parameter is passed but not used in `OrderArgs`

**Note:** py-clob-client's `OrderArgs` doesn't have an `order_type` field. LIMIT orders are the default.

## What Works Now

✅ **Detection:** Fully working - scans 4,917 markets  
✅ **Price Extraction:** Fixed to handle Gamma API format  
✅ **Paper Trading:** Fully implemented for testing  
✅ **Order Structure:** Correctly uses `OrderArgs` and `post_order()`  

## What Needs Implementation

✅ **Token ID Derivation:** FIXED - Now correctly extracts token_ids from market data  
❌ **Balance Query:** Need to implement real balance checking  
❌ **Order Validation:** Need to verify orders are placed correctly  
❌ **Error Handling:** Need better error handling for failed orders  

## Testing Status

- ✅ **Paper Trading:** Works (simulates trades)  
- ✅ **Token ID Extraction:** Tested and working  
- ⚠️ **Live Trading:** Ready to test (token_id fix complete)  
- ⚠️ **Balance Check:** Returns 0 (prevents accidental trades)  

## Next Steps

1. ✅ **Fix Token ID Issue:** COMPLETE
   - ✅ Added `get_token_ids()` method
   - ✅ Updated `executor.py` to use correct token_ids
   - ✅ Tested token_id extraction

2. **Implement Balance Check:**
   - Query USDC balance from blockchain
   - Update `get_balance()` method
   - Test balance retrieval

3. **Test Order Placement:**
   - Test with small amounts in paper trading
   - Verify orders appear in order book
   - Test order cancellation

4. **Add Error Handling:**
   - Handle partial fills
   - Handle order rejections
   - Add retry logic

## Resources

- [py-clob-client GitHub](https://github.com/Polymarket/py-clob-client)
- [PolyMarket API Docs](https://docs.polymarket.com/)
- [PolyMarket Quickstart: First Order](https://docs.polymarket.com/quickstart/orders/first-order)

