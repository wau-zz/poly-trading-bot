# PolyMarket Subgraph Queries

## Available Subgraphs

PolyMarket uses Goldsky-hosted subgraphs. Here are the available endpoints:

### 1. Activity Subgraph (Recommended for Trades)
```
https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/activity-subgraph/0.0.4/gn
```

**Use for:**
- Trade history
- Wallet activity
- Transaction data

### 2. Orderbook Subgraph
```
https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/orderbook-subgraph/0.0.1/gn
```

**Use for:**
- Order data
- Market orders
- Order book state

### 3. Positions Subgraph
```
https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/positions-subgraph/0.0.7/gn
```

**Use for:**
- User positions
- Open positions
- Position history

### 4. Open Interest Subgraph
```
https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/oi-subgraph/0.0.6/gn
```

**Use for:**
- Open interest metrics
- Market liquidity

### 5. PNL Subgraph
```
https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/pnl-subgraph/0.0.14/gn
```

**Use for:**
- Profit and loss data
- Wallet performance

## Example Queries

### Get Wallet Trades

```graphql
query GetWalletTrades($wallet: String!) {
  trades(
    where: { user: $wallet }
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

**Variables:**
```json
{
  "wallet": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
}
```

### Get Market Trades

```graphql
query GetMarketTrades($conditionId: String!) {
  trades(
    where: { conditionId: $conditionId }
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

### Get Top Traders (from Positions Subgraph)

```graphql
query GetTopTraders {
  positions(
    orderBy: size
    orderDirection: desc
    first: 100
  ) {
    user
    size
    conditionId
  }
}
```

## Testing Queries

You can test queries in the GraphQL Playground:

1. **Activity Subgraph:** https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/activity-subgraph/0.0.4/gn
2. **Positions Subgraph:** https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/positions-subgraph/0.0.7/gn

## Schema Notes

**Important:** The actual GraphQL schema may differ from these examples. Always check the schema in the GraphQL Playground before using queries in production.

**Common Fields:**
- `id`: Unique identifier
- `user`: Wallet address
- `conditionId`: Market condition ID
- `outcomeIndex`: 0 for YES, 1 for NO
- `price`: Price (may be in wei, need to divide by 1e18)
- `amount`: Trade amount (may be in wei)
- `timestamp`: Unix timestamp

## Rate Limits

Goldsky subgraphs are public but may have rate limits:
- Free tier: ~1000 requests/day
- Consider caching results
- Batch queries when possible

## Error Handling

If a query fails:
1. Check the GraphQL Playground to verify schema
2. Verify field names match actual schema
3. Check rate limits
4. Try alternative subgraph if available

## Resources

- [PolyMarket Subgraph Docs](https://docs.polymarket.com/developers/subgraph/overview)
- [GraphQL Playgrounds](https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/)
- [PolyMarket GitHub](https://github.com/Polymarket/polymarket-subgraph)










