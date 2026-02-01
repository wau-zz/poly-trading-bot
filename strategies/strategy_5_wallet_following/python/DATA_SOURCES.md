# Data Sources for Wallet Basket Strategy

## Overview

The wallet basket strategy requires access to PolyMarket trade data. This document outlines the available data sources and how to configure them.

## Data Sources

### 1. The Graph Subgraph (Recommended)

**What it provides:**
- On-chain trade data
- Wallet transaction history
- Market trading activity
- Historical data

**Endpoint:**
```
https://api.thegraph.com/subgraphs/name/polymarket/polymarket
```

**Alternative (with API key):**
```
https://gateway.thegraph.com/api/[api-key]/subgraphs/id/[subgraph-id]
```

**How to use:**
1. Get a free API key from [The Graph](https://thegraph.com/)
2. Add to `.env`:
   ```env
   POLYMARKET_SUBGRAPH_URL=https://gateway.thegraph.com/api/[your-key]/subgraphs/id/[subgraph-id]
   ```

**GraphQL Schema:**
The subgraph provides queries for:
- `trades` - All trades with filters (wallet, market, timestamp)
- `users` - Wallet statistics and rankings
- `conditions` - Market/condition data

### 2. PolyMarket Gamma API

**What it provides:**
- Market data
- Market categorization
- Current prices

**Endpoint:**
```
https://gamma-api.polymarket.com
```

**Usage:**
Already integrated in `shared/python/polymarket_client.py`

### 3. PolyMarket CLOB API

**What it provides:**
- Order book data
- Market details
- Trading endpoints

**Endpoint:**
```
https://clob.polymarket.com
```

**Usage:**
Already integrated via `py-clob-client`

## Configuration

### Environment Variables

Add to your `.env` file:

```env
# The Graph Subgraph (optional - uses public endpoint if not set)
POLYMARKET_SUBGRAPH_URL=https://gateway.thegraph.com/api/[key]/subgraphs/id/[id]

# Polygon RPC (for blockchain queries)
POLYGON_RPC_URL=https://polygon-rpc.com

# Or use a provider like Alchemy, Infura, etc.
# POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/[key]
```

## GraphQL Query Examples

### Get Wallet Trades

```graphql
query GetWalletTrades($wallet: String!, $since: BigInt) {
  trades(
    where: {
      user: $wallet,
      timestamp_gte: $since
    }
    orderBy: timestamp
    orderDirection: desc
    first: 1000
  ) {
    id
    user
    conditionId
    outcomeIndex
    price
    amount
    timestamp
    txHash
  }
}
```

### Get Top Traders

```graphql
query GetTopTraders($limit: Int) {
  users(
    orderBy: totalVolume
    orderDirection: desc
    first: $limit
  ) {
    id
    totalVolume
    tradeCount
  }
}
```

### Get Market Trades

```graphql
query GetMarketTrades($conditionId: String!) {
  trades(
    where: {
      conditionId: $conditionId
    }
    orderBy: timestamp
    orderDirection: desc
    first: 1000
  ) {
    id
    user
    conditionId
    outcomeIndex
    price
    amount
    timestamp
  }
}
```

## Data Fetching Flow

```
1. Fetch top traders from subgraph
   ↓
2. For each wallet, fetch trade history
   ↓
3. Calculate wallet statistics
   ↓
4. Filter by topic specialization
   ↓
5. Build wallet basket
   ↓
6. Monitor for consensus signals
```

## Rate Limits

**The Graph:**
- Free tier: 1000 requests/day
- Paid tier: Higher limits available

**Recommendations:**
- Cache wallet stats
- Batch queries when possible
- Use pagination for large datasets

## Troubleshooting

### Subgraph Not Available

If The Graph subgraph is down or unavailable:
1. Check subgraph status: https://thegraph.com/explorer
2. Use alternative RPC endpoint
3. Fall back to PolyMarket API (if available)

### Missing Trade Data

Some trades may not appear in subgraph:
- Check if subgraph is fully synced
- Verify wallet address format (lowercase)
- Check timestamp filters

### Performance Issues

For large-scale wallet scanning:
- Use pagination
- Implement caching
- Process in batches
- Consider using a database for storage

## Next Steps

1. **Get The Graph API Key** (optional but recommended)
2. **Test subgraph queries** with sample wallet addresses
3. **Verify data quality** before building baskets
4. **Implement caching** for performance
5. **Set up monitoring** for data source availability

## Resources

- [The Graph Documentation](https://thegraph.com/docs/)
- [PolyMarket API Docs](https://docs.polymarket.com/)
- [GraphQL Tutorial](https://graphql.org/learn/)










