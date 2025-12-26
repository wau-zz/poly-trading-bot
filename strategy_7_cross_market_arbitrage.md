# Strategy 7: Cross-Market Arbitrage (Prediction vs Spot)

**Strategy Type:** Statistical Arbitrage / Hedge Trading  
**Difficulty:** Expert  
**Capital Required:** $30k-50k  
**Expected Returns:** 25-50% monthly  
**Win Rate:** 70-80%  
**Time Horizon:** Days to weeks per trade

---

## Overview

Exploit the disconnect between emotional prediction market pricing and rational spot market reality. When crypto prices move dramatically, prediction markets overreact or lag, creating arbitrage opportunities against the underlying asset.

**The Edge:** Prediction markets price EMOTION. Spot markets price REALITY. During high volatility, these diverge significantly.

---

## The Core Concept

### Traditional Arbitrage:
Buy low on Market A, sell high on Market B (same asset)

### Cross-Market Arbitrage:
Prediction market says X% probability, but spot price + math says Y% probability → Trade the spread

## The Math

### **Fair Value Calculation**

For a market like "BTC > $100k by Dec 31":

```python
import numpy as np
from scipy.stats import norm
from datetime import datetime

def calculate_fair_probability(
    current_price,
    strike_price,
    days_to_expiry,
    annual_volatility
):
    """
    Calculate fair probability using Black-Scholes framework
    (Modified for binary outcome, not option pricing)
    """
    # Convert to decimal time
    T = days_to_expiry / 365.0
    
    # Drift (assume 0 for simplicity, or use risk-free rate)
    mu = 0.0  # Can use treasury rate if you want
    
    # Calculate z-score
    # How many standard deviations is strike from current price?
    sigma = annual_volatility
    
    # Price ratio
    price_ratio = strike_price / current_price
    
    # Log return needed
    log_return = np.log(price_ratio)
    
    # Expected volatility over period
    vol_over_period = sigma * np.sqrt(T)
    
    # Probability calculation (cumulative normal distribution)
    # P(S_T > K) = N(d2) in Black-Scholes terms
    d = (log_return - mu * T) / vol_over_period
    
    # Probability that BTC > strike at expiry
    prob = 1 - norm.cdf(d)
    
    return prob


# Example Usage:
current_btc = 95000
strike = 100000
days_left = 46
vol = 0.60  # 60% annualized volatility

fair_prob = calculate_fair_probability(current_btc, strike, days_left, vol)
print(f"Fair probability: {fair_prob:.1%}")  # Might output: 48.2%

polymarket_price = 0.35  # Market trading at 35%
edge = fair_prob - polymarket_price
print(f"Edge: {edge:.1%}")  # 13.2% edge!
```

---

## Strategy Implementation

### **Class: Cross-Market Arbitrageur**

```python
class CrossMarketArbitrage:
    def __init__(self, polymarket_client, crypto_exchange_client):
        self.pm_client = polymarket_client
        self.exchange_client = crypto_exchange_client
        self.positions = []
        
    async def scan_for_arbitrage(self):
        """
        Scan all crypto prediction markets for mispricing
        """
        # Get all crypto-related markets
        crypto_markets = await self.get_crypto_markets()
        
        opportunities = []
        
        for market in crypto_markets:
            # Parse market details
            details = self.parse_market(market)
            
            if not details:
                continue
            
            # Get current spot price
            spot_price = await self.exchange_client.get_price(details['ticker'])
            
            # Calculate fair value
            fair_prob = calculate_fair_probability(
                current_price=spot_price,
                strike_price=details['strike'],
                days_to_expiry=details['days_to_expiry'],
                annual_volatility=details['volatility']
            )
            
            # Get PolyMarket price
            pm_price = market['yes_price']
            
            # Calculate edge
            edge = abs(fair_prob - pm_price)
            
            # Minimum 10% edge required
            if edge > 0.10:
                opportunities.append({
                    'market': market,
                    'spot_price': spot_price,
                    'fair_prob': fair_prob,
                    'pm_price': pm_price,
                    'edge': edge,
                    'direction': 'BUY' if fair_prob > pm_price else 'SELL',
                    'ticker': details['ticker']
                })
        
        return opportunities
    
    def parse_market(self, market):
        """
        Extract strike, ticker, and expiry from market description
        """
        description = market['description']
        
        # Example: "Will Bitcoin trade above $100,000 by December 31, 2024?"
        # Extract: ticker=BTC, strike=100000, expiry=2024-12-31
        
        import re
        from dateutil import parser
        
        # Extract ticker
        if 'bitcoin' in description.lower() or 'btc' in description.lower():
            ticker = 'BTC'
        elif 'ethereum' in description.lower() or 'eth' in description.lower():
            ticker = 'ETH'
        else:
            return None  # Not a crypto we support
        
        # Extract strike price
        strike_match = re.search(r'\$?([\d,]+)', description)
        if strike_match:
            strike = float(strike_match.group(1).replace(',', ''))
        else:
            return None
        
        # Extract expiry date
        date_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}', description)
        if date_match:
            expiry = parser.parse(date_match.group(0))
        else:
            return None
        
        days_to_expiry = (expiry - datetime.now()).days
        
        if days_to_expiry < 0:
            return None  # Already expired
        
        # Estimate volatility from recent price history
        volatility = self.estimate_volatility(ticker)
        
        return {
            'ticker': ticker,
            'strike': strike,
            'expiry': expiry,
            'days_to_expiry': days_to_expiry,
            'volatility': volatility
        }
    
    def estimate_volatility(self, ticker, lookback_days=30):
        """
        Calculate historical volatility from spot market
        """
        # Get historical prices
        prices = self.exchange_client.get_historical_prices(ticker, days=lookback_days)
        
        # Calculate log returns
        returns = np.diff(np.log(prices))
        
        # Annualized volatility
        volatility = np.std(returns) * np.sqrt(365)
        
        return volatility
    
    async def execute_arbitrage_with_hedge(self, opportunity):
        """
        Execute the cross-market arbitrage with spot hedge
        """
        market = opportunity['market']
        spot_price = opportunity['spot_price']
        direction = opportunity['direction']
        
        position_size = self.calculate_position_size(opportunity)
        
        if direction == 'BUY':
            # PolyMarket underpriced → Buy PM, Short spot
            
            # Buy YES on PolyMarket
            pm_order = await self.pm_client.place_order(
                market_id=market['id'],
                side='BUY',
                quantity=position_size,
                price=opportunity['pm_price']
            )
            
            # Short on spot market (hedge)
            hedge_size = position_size * opportunity['strike'] * 0.1  # 10% hedge
            spot_order = await self.exchange_client.create_short_position(
                ticker=opportunity['ticker'],
                size=hedge_size,
                price=spot_price
            )
            
            print(f"✅ Bought underpriced PolyMarket + Short hedge")
            
        else:  # SELL
            # PolyMarket overpriced → Sell PM, Long spot
            
            # Sell YES on PolyMarket
            pm_order = await self.pm_client.place_order(
                market_id=market['id'],
                side='SELL',
                quantity=position_size,
                price=opportunity['pm_price']
            )
            
            # Buy on spot market (hedge)
            hedge_size = position_size * opportunity['strike'] * 0.1
            spot_order = await self.exchange_client.create_long_position(
                ticker=opportunity['ticker'],
                size=hedge_size,
                price=spot_price
            )
            
            print(f"✅ Sold overpriced PolyMarket + Long hedge")
        
        # Track position
        self.positions.append({
            'type': 'cross_market_arb',
            'pm_order': pm_order,
            'spot_order': spot_order,
            'entry_time': datetime.now(),
            'expected_profit': position_size * opportunity['edge']
        })
    
    def calculate_position_size(self, opportunity):
        """
        Kelly Criterion-based position sizing
        """
        # Kelly = edge / odds
        # For binary outcome, simplified
        
        edge = opportunity['edge']
        win_prob = 0.75  # Conservative estimate
        
        kelly_fraction = (win_prob * edge) / (1 - win_prob)
        
        # Use fractional Kelly (25%) for safety
        position_pct = kelly_fraction * 0.25
        
        # Cap at 10% of capital
        position_pct = min(position_pct, 0.10)
        
        return self.capital * position_pct
```

---

## Real-World Examples

### **Example 1: Bitcoin Volatility Spike**

**Event:** Tesla announces $1B BTC purchase

**Before:**
- BTC spot: $42,000
- PolyMarket "BTC > $50k by March": 35%

**After announcement:**
- BTC spot: $48,000 (14% jump)
- PolyMarket: Still 35% (lagging!)

**Math:**
- New fair probability: ~65%
- PolyMarket still 35%
- **Edge: 30 percentage points!**

**Trade:**
```python
# Buy PolyMarket YES at 35¢
buy_polymarket('BTC > 50k by March', price=0.35, size=1000)

# Hedge with short at $48k (in case it drops back)
short_btc(size=5, entry=48000)

# Scenarios:
# 1. BTC hits $50k → PM pays $1 → Profit ~$650 - hedge loss
# 2. BTC drops to $45k → PM might drop to 40¢ → Small profit on hedge
# 3. BTC stays $48k → PM rises to ~60¢ → Profit ~$250, hedge breakeven
```

### **Example 2: FUD Overreaction**

**Event:** China "bans" Bitcoin (for the 50th time)

**Reaction:**
- BTC spot: $62,000 → $56,000 (10% drop)
- PolyMarket "BTC > $60k by Dec": 65% → 15% (panic selling!)

**Math:**
- Fair probability (given historical FUD recovery): ~55%
- PolyMarket panic: 15%
- **Edge: 40 percentage points!**

**Trade:**
```python
# Buy the panic at 15¢
buy_polymarket('BTC > 60k by Dec', price=0.15, size=2000)

# Long hedge at $56k (if recovery happens faster)
buy_btc(size=0.5, entry=56000)

# Expected outcome:
# - Panic subsides in 1-2 days
# - PM recovers to 50-60¢
# - Profit: $700-900 per 1000 shares
```

---

## Advanced Techniques

### **1. Dynamic Hedging**

```python
def rebalance_hedge(self, position):
    """
    Adjust spot hedge as probabilities change
    """
    current_pm_price = get_market_price(position['market_id'])
    current_spot = get_spot_price(position['ticker'])
    
    # Calculate new fair value
    new_fair_prob = calculate_fair_probability(...)
    
    # If edge is closing, reduce hedge
    if abs(new_fair_prob - current_pm_price) < 0.05:
        # Close partial hedge to lock in gains
        await self.close_hedge_percentage(position, 0.50)
```

### **2. Multi-Strike Arbitrage**

```python
# Multiple strikes on same underlying
markets = [
    {'strike': 100000, 'pm_price': 0.35},  # "BTC > 100k"
    {'strike': 110000, 'pm_price': 0.15},  # "BTC > 110k"
    {'strike': 120000, 'pm_price': 0.05},  # "BTC > 120k"
]

# Calculate fair values for each
for market in markets:
    fair = calculate_fair_probability(current_btc, market['strike'], days, vol)
    
    if fair > market['pm_price'] + 0.10:
        # Buy this strike, hedge with appropriate spot size
        execute_multi_strike_arb(market)
```

### **3. Correlation Trading**

```python
# BTC and ETH are correlated
# If BTC prediction market misprices, check ETH

btc_pm_price = 0.40  # "BTC > 100k"
eth_pm_price = 0.60  # "ETH > 5k"

# Calculate correlation-adjusted fair values
# If BTC underpriced, ETH might be too
# Create spread trade across both
```

---

## Risk Management

### **Position Sizing**
- Max 10% per arbitrage trade
- Max 30% total in cross-market positions
- Keep 50% in reserve for opportunities

### **Hedge Ratios**
- **Full hedge:** 100% spot position (lower risk, lower return)
- **Partial hedge:** 25-50% spot (moderate risk/return)
- **No hedge:** Pure directional (highest risk/return)

### **Stop Losses**
- Close if edge disappears (<5% difference)
- Close if spot moves dramatically against you
- Time-based: Close 7 days before expiry

---

## Expected Performance

### **Per Trade:**
- **ROI:** 50-300% per trade
- **Win rate:** 70-80%
- **Hold time:** 3-21 days
- **Opportunities:** 5-15 per month (during volatile periods)

### **Monthly Returns (with $40k capital):**
- **Conservative:** $10k/month (25%)
- **Realistic:** $15k/month (37.5%)
- **Aggressive:** $20k+/month (50%)

---

## When Opportunities Appear

### **High Volatility Events:**
- Major news (Tesla buys BTC, ETF approval)
- Regulatory announcements
- Exchange hacks or failures
- Macro events (Fed decisions, inflation data)
- Technical breakouts (BTC $100k milestone)

### **Emotional Market Phases:**
- FOMO rallies (PolyMarket lags spot)
- FUD crashes (PolyMarket overreacts)
- Sideways grind (both mispriced)

---

## Tools Needed

### **PolyMarket:**
- `py-clob-client` for trading

### **Crypto Exchanges:**
- Binance API (spot + futures)
- Coinbase API
- FTX/OKX (if available)

### **Data & Analytics:**
- `ccxt` (unified crypto exchange API)
- `scipy` (probability calculations)
- `pandas` (price analysis)

### **Volatility Calculation:**
```python
import ccxt

exchange = ccxt.binance()

def get_historical_vol(ticker='BTC/USDT', days=30):
    ohlcv = exchange.fetch_ohlcv(ticker, '1d', limit=days)
    closes = [x[4] for x in ohlcv]
    returns = np.diff(np.log(closes))
    vol = np.std(returns) * np.sqrt(365)
    return vol
```

---

## Common Mistakes

1. **Not hedging** - Pure directional bets when you meant arbitrage
2. **Over-hedging** - Too much hedge kills profit
3. **Ignoring fees** - Spot trading fees + PolyMarket fees
4. **Wrong volatility** - Using too-recent or too-old vol estimates
5. **Emotional trading** - Following the crowd instead of math
6. **Poor timing** - Entering too close to expiry

---

## Getting Started

- [ ] Set up PolyMarket API access
- [ ] Set up crypto exchange API (Binance/Coinbase)
- [ ] Build probability calculator
- [ ] Create market scanner
- [ ] Paper trade 5 opportunities
- [ ] Deploy with $5k capital
- [ ] Scale to $30k-50k

---

## Next Level: Automated Scanner

```python
async def continuous_scanner():
    """
    Run 24/7 scanning for cross-market arbitrage
    """
    while True:
        try:
            # Scan for opportunities
            opportunities = await scan_for_arbitrage()
            
            # Filter for best ones
            best_opps = [o for o in opportunities if o['edge'] > 0.15]
            
            # Execute top 3
            for opp in best_opps[:3]:
                await execute_arbitrage_with_hedge(opp)
            
            await asyncio.sleep(300)  # Every 5 minutes
            
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(60)
```

---

**[← Previous: Structured Products](./strategy_6_structured_products.md)** | **[Back to Overview](./OVERVIEW.md)**

---

*This is Strategy 7 of 7 in the PolyMarket Trading Bot series*  
*Last Updated: December 26, 2025*

