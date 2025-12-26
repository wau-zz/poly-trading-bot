# Strategy 4: High-Frequency Market Making

**Strategy Type:** Liquidity Provision / Scalping  
**Difficulty:** Intermediate-Advanced  
**Capital Required:** $10k-15k  
**Expected Returns:** 5-15% monthly  
**Win Rate:** 70-80%  
**Time Horizon:** Minutes to hours per trade

---

## Overview

Market making involves continuously posting buy and sell orders with a small spread, profiting from the difference. You become the middleman, earning from other traders' transactions.

**Simple concept:** Buy at $0.50, sell at $0.51 → $0.01 profit per share. Repeat 1,000 times daily = $10/day/market.

## The Core Concept

### Traditional Market Structure

Every market has an **order book**:

**Asks (Sell Orders):**
- $0.53 - 200 shares
- $0.52 - 500 shares  
- $0.51 - 300 shares ← Best ask

**Bids (Buy Orders):**
- $0.49 - 400 shares ← Best bid
- $0.48 - 600 shares
- $0.47 - 300 shares

**Bid-Ask Spread:** $0.51 - $0.49 = $0.02 (2¢)

### Your Opportunity

You place orders inside the spread:

**Your Orders:**
- **Buy at $0.495** (beat existing $0.49 bid)
- **Sell at $0.505** (beat existing $0.51 ask)

**Your spread:** $0.505 - $0.495 = $0.01 (1¢ profit per share)

### The Trade Cycle

1. Someone sells to you at $0.495 → You're long 100 shares
2. Someone buys from you at $0.505 → You're flat
3. **Profit: $1.00** (100 shares × $0.01 spread)
4. Repeat continuously

## Implementation

### Basic Market Maker

```python
class MarketMaker:
    def __init__(self, market_id, spread_bps=100, inventory_limit=1000):
        self.market_id = market_id
        self.spread_bps = spread_bps  # 100 basis points = 1%
        self.inventory = 0  # Current position
        self.inventory_limit = inventory_limit
        self.target_inventory = 0  # Ideal = 0 (market neutral)
        self.active_orders = {'buy': None, 'sell': None}
    
    def calculate_quotes(self):
        """
        Calculate bid/ask quotes
        """
        # Get current mid price
        mid_price = get_market_mid_price(self.market_id)
        
        # Get market volatility
        volatility = estimate_volatility(self.market_id)
        
        # Base spread (wider in volatile markets)
        base_spread = self.spread_bps / 10000
        volatility_adjustment = volatility * 0.5
        spread = base_spread * (1 + volatility_adjustment)
        
        # Inventory skew (push prices to reduce inventory)
        inventory_pct = self.inventory / self.inventory_limit
        inventory_skew = inventory_pct * 0.02  # Up to 2% skew
        
        # Calculate quotes
        bid_price = mid_price - (spread / 2) - inventory_skew
        ask_price = mid_price + (spread / 2) - inventory_skew
        
        # Ensure valid prices (0 to 1.0)
        bid_price = max(0.01, min(0.99, bid_price))
        ask_price = max(0.01, min(0.99, ask_price))
        
        return bid_price, ask_price
    
    def manage_inventory(self):
        """
        Prevent building too much one-sided exposure
        """
        inventory_pct = abs(self.inventory) / self.inventory_limit
        
        if inventory_pct > 0.8:
            # Critical: Aggressively reduce inventory
            if self.inventory > 0:
                return 'AGGRESSIVE_SELL'
            else:
                return 'AGGRESSIVE_BUY'
        
        elif inventory_pct > 0.5:
            # Warning: Moderately reduce inventory
            if self.inventory > 0:
                return 'MODERATE_SELL'
            else:
                return 'MODERATE_BUY'
        
        return 'NEUTRAL'
    
    async def update_orders(self):
        """
        Continuously update bid/ask orders
        """
        # Calculate new quotes
        bid, ask = self.calculate_quotes()
        inventory_action = self.manage_inventory()
        
        # Cancel existing orders
        await self.cancel_all_orders()
        
        # Adjust for inventory management
        if inventory_action == 'AGGRESSIVE_SELL':
            # We're too long, sell aggressively
            await self.place_order('SELL', ask - 0.005, size=200)
            await self.place_order('BUY', bid, size=25)  # Reduce buying
            
        elif inventory_action == 'AGGRESSIVE_BUY':
            # We're too short, buy aggressively
            await self.place_order('BUY', bid + 0.005, size=200)
            await self.place_order('SELL', ask, size=25)  # Reduce selling
            
        elif inventory_action == 'MODERATE_SELL':
            await self.place_order('SELL', ask, size=100)
            await self.place_order('BUY', bid, size=50)
            
        elif inventory_action == 'MODERATE_BUY':
            await self.place_order('BUY', bid, size=100)
            await self.place_order('SELL', ask, size=50)
            
        else:  # NEUTRAL
            # Balanced quotes
            await self.place_order('BUY', bid, size=100)
            await self.place_order('SELL', ask, size=100)
    
    async def place_order(self, side, price, size):
        """
        Place limit order
        """
        order = await api_client.place_limit_order(
            market_id=self.market_id,
            side=side,
            price=price,
            quantity=size
        )
        
        self.active_orders[side.lower()] = order
        return order
    
    async def cancel_all_orders(self):
        """
        Cancel existing orders before posting new ones
        """
        for side, order in self.active_orders.items():
            if order:
                await api_client.cancel_order(order['id'])
        
        self.active_orders = {'buy': None, 'sell': None}
    
    async def on_order_filled(self, order):
        """
        Update inventory when order fills
        """
        if order['side'] == 'BUY':
            self.inventory += order['filled_quantity']
            print(f"✅ Bought {order['filled_quantity']} @ ${order['price']:.3f}")
        else:
            self.inventory -= order['filled_quantity']
            print(f"✅ Sold {order['filled_quantity']} @ ${order['price']:.3f}")
        
        # Update quotes after fill
        await self.update_orders()
    
    async def run(self):
        """
        Main market making loop
        """
        while True:
            try:
                # Update quotes every 5 seconds
                await self.update_orders()
                await asyncio.sleep(5)
                
            except Exception as e:
                print(f"Error in market making: {e}")
                await asyncio.sleep(10)
```

### Multi-Market Market Maker

```python
class MultiMarketMaker:
    def __init__(self, target_markets_count=10):
        self.makers = {}
        self.target_count = target_markets_count
        self.total_capital = 15000
    
    async def select_markets(self):
        """
        Choose best markets for market making
        """
        all_markets = await get_all_markets()
        
        # Filter for good market making candidates
        candidates = []
        for market in all_markets:
            score = self.score_market(market)
            if score > 0.7:
                candidates.append({
                    'market': market,
                    'score': score
                })
        
        # Select top N markets
        candidates.sort(key=lambda x: x['score'], reverse=True)
        selected = candidates[:self.target_count]
        
        return [c['market'] for c in selected]
    
    def score_market(self, market):
        """
        Score market for market making potential
        """
        # Criteria:
        # 1. High volume (more trades = more opportunities)
        # 2. Narrow spread (easier to compete)
        # 3. Moderate volatility (not too wild)
        # 4. Clear outcome (less risk)
        
        volume_score = min(market['volume_24h'] / 1000000, 1.0)  # $1M+ = 1.0
        
        spread = market['ask'] - market['bid']
        spread_score = 1.0 - min(spread / 0.10, 1.0)  # Prefer <10% spreads
        
        volatility = estimate_market_volatility(market)
        volatility_score = 1.0 - min(volatility / 0.20, 1.0)  # Prefer <20% vol
        
        # Weighted score
        total_score = (
            volume_score * 0.4 +
            spread_score * 0.3 +
            volatility_score * 0.3
        )
        
        return total_score
    
    async def run(self):
        """
        Run market making on multiple markets
        """
        # Select markets
        markets = await self.select_markets()
        
        # Allocate capital per market
        capital_per_market = self.total_capital / len(markets)
        
        # Start makers
        for market in markets:
            maker = MarketMaker(
                market_id=market['id'],
                spread_bps=100,
                inventory_limit=capital_per_market * 0.5
            )
            
            self.makers[market['id']] = maker
            asyncio.create_task(maker.run())
        
        # Monitor and rebalance
        while True:
            await self.monitor_performance()
            await asyncio.sleep(300)  # Check every 5 minutes
    
    async def monitor_performance(self):
        """
        Monitor each maker's performance
        """
        for market_id, maker in self.makers.items():
            # Check if market is still good
            # Replace underperforming markets
            pass
```

## Cross-Platform Arbitrage

Market making across multiple platforms (PolyMarket, Kalshi, etc.):

```python
async def cross_platform_market_making():
    """
    Buy on cheap platform, sell on expensive platform
    """
    # Get prices from both platforms
    polymarket_bid = get_polymarket_bid(event_id)
    polymarket_ask = get_polymarket_ask(event_id)
    
    kalshi_bid = get_kalshi_bid(equivalent_event_id)
    kalshi_ask = get_kalshi_ask(equivalent_event_id)
    
    # Account for fees (2% per platform = 4% total)
    total_fees = 0.04
    
    # Opportunity 1: Buy on PolyMarket, sell on Kalshi
    if polymarket_ask < kalshi_bid - total_fees:
        profit = kalshi_bid - polymarket_ask - total_fees
        
        if profit > 0.02:  # >2% profit
            await buy_polymarket(event_id, polymarket_ask, size=100)
            await sell_kalshi(equivalent_event_id, kalshi_bid, size=100)
            print(f"✅ Cross-platform arb: ${profit * 100:.2f}")
    
    # Opportunity 2: Buy on Kalshi, sell on PolyMarket
    elif kalshi_ask < polymarket_bid - total_fees:
        profit = polymarket_bid - kalshi_ask - total_fees
        
        if profit > 0.02:
            await buy_kalshi(equivalent_event_id, kalshi_ask, size=100)
            await sell_polymarket(event_id, polymarket_bid, size=100)
            print(f"✅ Cross-platform arb: ${profit * 100:.2f}")
```

## Best Markets for Market Making

### High Volume Markets
- **$1M+ daily volume**
- More traders = more fills
- Tighter spreads = more competition

### Clear Outcomes
- Binary yes/no
- Objective resolution
- No dispute risk

### Examples
- **Crypto prices** ("BTC above $100k by Dec 31")
- **Sports** (game outcomes, player stats)
- **Elections** (clear winners)
- **Economic data** (CPI, jobs report)

### Avoid
- ❌ Subjective outcomes
- ❌ Low liquidity (<$100k volume)
- ❌ Extremely volatile (>50% daily swings)
- ❌ Long-dated (>90 days to resolution)

## Risk Management

### Inventory Risk
**Problem:** Get stuck with large one-sided position  
**Solution:** 
- Set inventory limits (50% of capital max)
- Skew quotes to reduce inventory
- Aggressively exit at 80% of limit

### Adverse Selection
**Problem:** Smart traders pick you off  
**Solution:**
- Widen spreads during news events
- Cancel orders during high volatility
- Monitor trade flow patterns

### Event Risk
**Problem:** Market resolves unexpectedly  
**Solution:**
- Reduce inventory before resolution
- Avoid markets <24 hours from resolution
- Hedge large positions

## Expected Performance

### Daily Metrics
- **100-1,000 trades per day**
- **Average profit:** 0.5-2% per round-trip
- **Win rate:** 70-80%

### Monthly Returns
With $15k capital across 10 markets:
- **Conservative:** $750/month (5%)
- **Realistic:** $1,500/month (10%)
- **Aggressive:** $2,250/month (15%)

### Sharpe Ratio
- **2-4** (consistent small wins)

## Infrastructure Requirements

### Low Latency
- **WebSocket connections** for real-time prices
- **< 100ms execution** from signal to order
- **VPS near exchange** (if possible)

### Order Management
- Fast order placement/cancellation
- Track multiple markets simultaneously
- Handle fills in real-time

### Monitoring
- P&L tracking per market
- Inventory monitoring
- Alert on large fills or errors

## Advanced Techniques

### Dynamic Spread Adjustment

```python
def calculate_optimal_spread(market):
    """
    Adjust spread based on market conditions
    """
    base_spread = 0.01  # 1%
    
    # Widen during volatility
    volatility = estimate_volatility(market)
    vol_adjustment = volatility * 0.5
    
    # Widen near resolution
    days_to_resolution = get_days_until_resolution(market)
    if days_to_resolution < 7:
        time_adjustment = (7 - days_to_resolution) / 7 * 0.02
    else:
        time_adjustment = 0
    
    # Narrow in high volume (more competition)
    volume_adjustment = -min(market['volume_24h'] / 2000000, 0.005)
    
    optimal_spread = base_spread + vol_adjustment + time_adjustment + volume_adjustment
    
    return max(0.005, optimal_spread)  # Minimum 0.5% spread
```

### Order Book Analysis

```python
def analyze_order_book(market_id):
    """
    Analyze depth to optimize quote placement
    """
    order_book = get_order_book(market_id)
    
    # Calculate total liquidity
    bid_depth = sum(order['size'] for order in order_book['bids'][:10])
    ask_depth = sum(order['size'] for order in order_book['asks'][:10])
    
    # Imbalance suggests direction
    imbalance = (bid_depth - ask_depth) / (bid_depth + ask_depth)
    
    # Place orders where liquidity is thin
    return imbalance
```

## Real Trader Results

**Trader A:** "Market making on 15 markets. $12k capital. Averaging $80-120/day. Sharpe ratio 3.2. Completely automated."

**Trader B:** "Run MM bot on high-volume crypto markets only. 200-400 trades/day. 5-8% monthly returns. Low stress, consistent."

**Trader C:** "Cross-platform MM between PolyMarket and Kalshi. Best strategy during major events. Made $3k during election week."

## Getting Started

- [ ] Choose 3-5 high-volume markets
- [ ] Build basic market maker
- [ ] Paper trade for 1 week
- [ ] Deploy with $500 per market
- [ ] Monitor and optimize
- [ ] Scale to 10+ markets

## Common Mistakes

1. **Too wide spreads** - No fills
2. **Too narrow spreads** - No profit
3. **Ignoring inventory** - Get stuck long/short
4. **Not canceling fast enough** - Get picked off
5. **Trading illiquid markets** - Can't exit
6. **Market making near resolution** - Too risky

## Next Steps

1. **Implement basic market maker** on 1 market
2. **Test inventory management**
3. **Add monitoring and alerts**
4. **Scale to 5-10 markets**
5. **Optimize spreads dynamically**

---

**[← Previous: Probability Models](./strategy_3_probability_models.md)** | **[Next: Wallet Following →](./strategy_5_wallet_following.md)**

---

*This is Strategy 4 of 7 in the PolyMarket Trading Bot series*  
*Last Updated: December 25, 2025*

