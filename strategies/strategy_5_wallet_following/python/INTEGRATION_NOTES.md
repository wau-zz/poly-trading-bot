# Data Integration Notes

## Current Status

✅ **Core structure complete** - All components built  
✅ **Subgraph client implemented** - Ready to query PolyMarket data  
✅ **API client implemented** - Market topic detection working  
⚠️ **Schema verification needed** - GraphQL queries may need adjustment  

## What's Implemented

### 1. Data Fetcher (`data_fetcher.py`)
- ✅ `PolyMarketSubgraphClient` - GraphQL client for subgraph queries
- ✅ `PolyMarketAPIClient` - REST client for market data
- ✅ `WalletDataFetcher` - Unified interface for wallet data

### 2. Integration Points
- ✅ Wallet scanner uses data fetcher
- ✅ Consensus detector uses data fetcher
- ✅ Wallet monitor uses data fetcher
- ✅ Bot uses data fetcher for basket building

## What Needs Verification

### 1. GraphQL Schema
The actual PolyMarket subgraph schema may differ from our queries. You need to:

1. **Check the GraphQL Playground:**
   - Activity Subgraph: https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/activity-subgraph/0.0.4/gn
   - Verify field names match our queries

2. **Test queries:**
   ```bash
   python test_data_fetcher.py
   ```

3. **Adjust if needed:**
   - Update queries in `data_fetcher.py`
   - Match actual schema fields

### 2. Win/Loss Calculation
Currently, win rates are placeholders because we need:
- Resolved market data
- Outcome matching
- PNL calculation

**Solution:** Use PNL subgraph to get actual win/loss data:
```
https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/pnl-subgraph/0.0.14/gn
```

### 3. Market Topic Categorization
Current implementation uses simple keyword matching. Can be improved with:
- ML-based classification
- Tag-based categorization
- Market metadata analysis

## Testing Steps

1. **Test subgraph connection:**
   ```bash
   python test_data_fetcher.py
   ```

2. **Verify queries work:**
   - Check GraphQL Playground
   - Test with sample wallet addresses
   - Verify response format

3. **Test wallet basket building:**
   ```bash
   python bot.py --topic geopolitics --paper
   ```

4. **Monitor for errors:**
   - Check logs for schema mismatches
   - Verify data format
   - Adjust queries as needed

## Known Limitations

1. **Schema Differences:**
   - GraphQL schema may differ from our queries
   - Field names may be different
   - Need to verify in Playground

2. **Rate Limits:**
   - Goldsky subgraphs may have rate limits
   - Consider caching
   - Batch queries when possible

3. **Data Completeness:**
   - Some trades may not appear in subgraph
   - Check subgraph sync status
   - May need to combine multiple sources

## Next Steps

1. ✅ **Test subgraph connection** - Run `test_data_fetcher.py`
2. ⏳ **Verify schema** - Check GraphQL Playground
3. ⏳ **Adjust queries** - Match actual schema
4. ⏳ **Test with real data** - Use sample wallets
5. ⏳ **Build basket** - Test basket construction
6. ⏳ **Monitor consensus** - Test signal detection

## Resources

- [PolyMarket Subgraph Docs](https://docs.polymarket.com/developers/subgraph/overview)
- [GraphQL Playgrounds](https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/)
- [SUBGRAPH_QUERIES.md](./SUBGRAPH_QUERIES.md) - Query examples
- [DATA_SOURCES.md](./DATA_SOURCES.md) - Data source overview










