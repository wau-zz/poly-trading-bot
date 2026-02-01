# What is `token_id`?

## Simple Explanation

**`token_id`** is a unique identifier for a **specific outcome** (YES or NO) in a PolyMarket binary market.

Think of it like this:
- **`condition_id`** = The market/event (e.g., "Will Bitcoin reach $1M?")
- **`token_id`** = The specific outcome you're trading (YES or NO)

## Real Example

For the market: **"Will Bitcoin reach $1,000,000 by December 31, 2025?"**

```
Condition ID: 0xd8b9ff369452daebce1ac8cb6a29d6817903e85168356c72812317f38e317613
  ↓
  ├─ YES Token ID: 112540911653160777059655478391259433595972605218365763034134019729862917878641
  └─ NO Token ID:  72957845969259179114974336105989648762775384471357386872640167050913336248574
```

## Why We Need It

When placing an order on PolyMarket, you **cannot** use the `condition_id`. You must use the specific `token_id` for the outcome you want to trade:

- **To BUY YES shares:** Use the YES `token_id`
- **To BUY NO shares:** Use the NO `token_id`

## How to Get Token IDs

The `get_market(condition_id)` method returns a `tokens` array:

```python
market = client.get_market(condition_id)
tokens = market['tokens']

# Find YES token_id
yes_token = next(t for t in tokens if t['outcome'] == 'Yes')
yes_token_id = yes_token['token_id']  # This is what we need!

# Find NO token_id
no_token = next(t for t in tokens if t['outcome'] == 'No')
no_token_id = no_token['token_id']  # This is what we need!
```

## Current Problem in Our Code

**What we're doing now (WRONG):**
```python
# executor.py - line 100-101
yes_order = self.client.place_order(
    market_id=opportunity['market_id'],  # ❌ This is condition_id, not token_id!
    side='BUY',
    ...
)
```

**What we need to do (CORRECT):**
```python
# First, get the market to extract token_ids
market = client.get_market(condition_id)
yes_token_id = next(t['token_id'] for t in market['tokens'] if t['outcome'] == 'Yes')
no_token_id = next(t['token_id'] for t in market['tokens'] if t['outcome'] == 'No')

# Then use the actual token_ids
yes_order = self.client.place_order(
    market_id=yes_token_id,  # ✅ Correct token_id for YES
    side='BUY',
    ...
)

no_order = self.client.place_order(
    market_id=no_token_id,  # ✅ Correct token_id for NO
    side='BUY',
    ...
)
```

## Token ID Format

- **Type:** Large integer (not hex string)
- **Example:** `112540911653160777059655478391259433595972605218365763034134019729862917878641`
- **Length:** ~77 digits
- **Note:** This is different from `condition_id` which is a hex string like `0x...`

## Summary

| Term | What It Is | Example |
|------|------------|---------|
| **condition_id** | Market/event identifier | `0xd8b9ff369452daebce1ac8cb6a29d6817903e85168356c72812317f38e317613` |
| **token_id (YES)** | YES outcome identifier | `112540911653160777059655478391259433595972605218365763034134019729862917878641` |
| **token_id (NO)** | NO outcome identifier | `72957845969259179114974336105989648762775384471357386872640167050913336248574` |

**Bottom line:** We need to fetch the market details and extract the `token_id` from the `tokens` array before placing orders.










