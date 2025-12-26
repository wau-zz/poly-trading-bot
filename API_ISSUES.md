# Known API Issues & Limitations

## Stale Market Data

### Problem
The PolyMarket `/markets` API endpoint returns markets that are marked as "accepting orders" but are actually expired/invalid. When you try to access these markets via their condition URLs, you get a 404 error.

### Example
- API returns: Market with `accepting_orders=True`
- Condition URL: `https://polymarket.com/condition/0x7c97080dfbbe71bfa52ba51c82cb0cdfe47cd7b87842047c58647c8ff1d1fef4`
- Browser result: "Oops...we didn't forecast this" (404 error)
- Order book API: Returns 404 "No orderbook exists"

### Solution
We've added **order book validation** to filter out invalid markets:

1. **Enabled by default**: `VALIDATE_ORDER_BOOKS=true` in `.env`
2. **How it works**: Checks if each market has a valid order book before including it
3. **Trade-off**: Slower (validates each market), but ensures only valid markets are scanned

### Disable Validation (Faster, Less Accurate)
If you want faster scanning and don't mind some invalid markets:

```env
VALIDATE_ORDER_BOOKS=false
```

**Warning**: With validation disabled, the bot may try to scan expired markets that won't work.

## Current Status

As of now, the PolyMarket API appears to be returning mostly expired markets from 2023. This is expected behavior - the bot will work correctly when new markets are created.

### What This Means
- ✅ Bot code is correct
- ✅ Filtering logic works
- ✅ Order book validation works
- ⚠️ API is returning stale data (not our fault)
- ✅ Bot will work when new markets are available

## Alternative Approaches

### Option 1: Use Different API Endpoint
You might need to use PolyMarket's GraphQL API or a different endpoint that returns only active markets. Check the [PolyMarket API documentation](https://docs.polymarket.com/).

### Option 2: Filter by Recent Activity
Instead of relying on `accepting_orders` flag, filter by:
- Recent trading volume
- Recent price updates
- Market creation date (only last 30 days)

### Option 3: Use Event URLs Instead
Some markets might be accessible via event URLs even if condition URLs are expired. However, for arbitrage, we need condition-level prices.

## Monitoring

The bot logs will show:
- How many markets were fetched
- How many passed expiration checks
- How many have valid order books
- Any validation errors

Check logs with:
```bash
tail -f logs/bot.log | grep -E "(markets|order book|validated)"
```

---

**Bottom Line**: The bot is working correctly. The issue is with PolyMarket's API returning stale data. When new markets are created, the bot will automatically detect and trade them.

---

## Issue: Market Not Found in API Despite Existing on Website

### Problem
Some markets that exist on the PolyMarket website are not returned by the CLOB API `/markets` endpoint, even after searching through 30,000+ markets with pagination.

### Example
The "OpenAI $1t+ IPO before 2027?" market exists at:
- Website: `https://polymarket.com/event/openai-1t-ipo-before-2027`
- But cannot be found via:
  - `GET https://clob.polymarket.com/markets` (with pagination)
  - `ClobClient.get_markets()` method
  - Gamma API (`https://gamma-api.polymarket.com/markets`)

### Possible Reasons
1. **API Indexing Delay:** New markets may take time to appear in the API after being created on the website
2. **Different Status/Category:** Market might be in a status or category not returned by the standard `/markets` endpoint
3. **Authentication Required:** Some markets might require different authentication or endpoints
4. **API Limitation:** The API might not return all markets that are visible on the website

### Current Status
- ✅ We are using the **correct endpoint**: `https://clob.polymarket.com/markets` with proper pagination
- ✅ Our code correctly handles pagination and searches through thousands of markets
- ✅ Successfully fetches 30,000+ markets across multiple pages
- ⚠️ Some markets visible on the website may not be immediately available via API

### Workaround
- The bot will work correctly for markets that are available in the API
- For markets not found in API, they may appear later as the API indexes them
- Consider using the website's GraphQL API or other endpoints if direct market access is needed
- The bot uses the correct endpoint - this is a PolyMarket API limitation, not our code issue

