# Strategy 2: Correlated Market Divergence Trading

**Strategy Type:** Statistical Arbitrage / Mean Reversion  
**Difficulty:** Intermediate-Advanced  
**Capital Required:** $10k-25k  
**Expected Returns:** 10-20% monthly  
**Win Rate:** 60-70%  
**Time Horizon:** 2-14 days per trade

---

## Overview

Correlated market divergence trading exploits the relationship between markets that should move together. When these related markets diverge from their typical spread, you trade the gap closure.

**Unlike arbitrage, this carries directional risk** - but offers much higher returns.

## The Core Concept

Some prediction markets are closely related. They should move in tandem, but sometimes they don't.

**Examples of correlated markets:**

### Political Events
- "Democrats win presidency" ↔ "Democrats control Senate"
- "Candidate X wins primary" ↔ "Candidate X wins general election"
- "Trump wins election" ↔ "Republicans control House"

### Crypto Markets
- "Bitcoin hits $100k" ↔ "Crypto market cap hits $5T"
- "ETH above $5k" ↔ "BTC above $150k"
- "Coinbase stock up 20%" ↔ "Crypto prices rally"

### Economic Events
- "Fed raises rates in March" ↔ "S&P 500 down 10% in Q1"
- "Recession declared" ↔ "Unemployment hits 6%"
- "Inflation above 4%" ↔ "Gold prices rally"

## The Opportunity

**Normal spread:**
- Market A: 65¢
- Market B: 62¢
- Spread: 3¢ (typical)

**Divergence (trading opportunity):**
- Market A: 75¢ (ran up on news)
- Market B: 58¢ (lagged behind)
- Spread: 17¢ (abnormally wide)

**Trade:**
- SELL Market A at 75¢ (overpriced)
- BUY Market B at 58¢ (underpriced)

**Profit when spread normalizes:**
- Market A drops to 68¢
- Market B rises to 65¢
- Spread: 3¢ (back to normal)
- **Profit: 14¢ per share**

## Implementation

### Market Pair Discovery

```python
class CorrelatedPair:
    def __init__(self, market_a_id, market_b_id, correlation_type='positive'):
        self.market_a_id = market_a_id
        self.market_b_id = market_b_id
        self.correlation_type = correlation_type  # 'positive' or 'negative'
        self.historical_spread = []
        self.mean_spread = None
        self.std_spread = None
        self.correlation_coefficient = None
    
    def calculate_statistics(self, lookback_days=30):
        """
        Calculate historical spread statistics
        """
        # Fetch historical price data
        prices_a = get_historical_prices(self.market_a_id, days=lookback_days)
        prices_b = get_historical_prices(self.market_b_id, days=lookback_days)
        
        # Calculate spreads
        spreads = []
        for price_a, price_b in zip(prices_a, prices_b):
            spread = price_a - price_b
            spreads.append(spread)
        
        # Statistical measures
        self.mean_spread = np.mean(spreads)
        self.std_spread = np.std(spreads)
        self.historical_spread = spreads
        
        # Correlation coefficient
        self.correlation_coefficient = np.corrcoef(prices_a, prices_b)[0, 1]
    
    def calculate_z_score(self, current_spread):
        """
        How many standard deviations from normal spread
        """
        if self.std_spread == 0:
            return 0
        
        z_score = (current_spread - self.mean_spread) / self.std_spread
        return z_score
    
    def is_trade_signal(self, threshold=2.0):
        """
        Check if current spread presents trading opportunity
        """
        current_a = get_market_price(self.market_a_id)
        current_b = get_market_price(self.market_b_id)
        spread = current_a - current_b
        
        z_score = self.calculate_z_score(spread)
        
        # Trade when spread is >2 standard deviations from mean
        if abs(z_score) > threshold:
            # Determine trade direction
            if z_score > 0:
                # Spread too wide: A is overpriced or B is underpriced
                action = 'SELL_A_BUY_B'
            else:
                # Spread too narrow: A is underpriced or B is overpriced
                action = 'BUY_A_SELL_B'
            
            return {
                'action': action,
                'z_score': z_score,
                'current_spread': spread,
                'mean_spread': self.mean_spread,
                'confidence': min(abs(z_score) / 4, 1.0)  # Confidence score
            }
        
        return None
```

### Trading Logic

```python
class PairsTradingBot:
    def __init__(self, api_client):
        self.api_client = api_client
        self.pairs = []
        self.active_positions = []
        
    def add_pair(self, market_a_id, market_b_id):
        """
        Add a correlated pair to monitor
        """
        pair = CorrelatedPair(market_a_id, market_b_id)
        pair.calculate_statistics(lookback_days=30)
        
        # Only add if correlation is strong
        if abs(pair.correlation_coefficient) > 0.6:
            self.pairs.append(pair)
            print(f"✅ Added pair with correlation: {pair.correlation_coefficient:.2f}")
        else:
            print(f"❌ Weak correlation: {pair.correlation_coefficient:.2f}")
    
    async def monitor_pairs(self):
        """
        Continuously monitor all pairs for trade signals
        """
        while True:
            try:
                for pair in self.pairs:
                    signal = pair.is_trade_signal(threshold=2.0)
                    
                    if signal and not self.has_open_position(pair):
                        await self.execute_pairs_trade(pair, signal)
                    
                    # Check if we should close existing positions
                    await self.check_exit_conditions(pair)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"Error monitoring pairs: {e}")
                await asyncio.sleep(60)
    
    async def execute_pairs_trade(self, pair, signal):
        """
        Execute the pairs trade
        """
        try:
            # Calculate position size
            position_size = self.calculate_position_size(
                signal['confidence'], 
                base_size=2000
            )
            
            if signal['action'] == 'SELL_A_BUY_B':
                # Sell market A (overpriced)
                # Buy market B (underpriced)
                
                order_a = await self.api_client.place_order(
                    market_id=pair.market_a_id,
                    side='SELL',
                    quantity=position_size,
                    order_type='MARKET'
                )
                
                order_b = await self.api_client.place_order(
                    market_id=pair.market_b_id,
                    side='BUY',
                    quantity=position_size,
                    order_type='MARKET'
                )
                
            else:  # BUY_A_SELL_B
                order_a = await self.api_client.place_order(
                    market_id=pair.market_a_id,
                    side='BUY',
                    quantity=position_size,
                    order_type='MARKET'
                )
                
                order_b = await self.api_client.place_order(
                    market_id=pair.market_b_id,
                    side='SELL',
                    quantity=position_size,
                    order_type='MARKET'
                )
            
            # Track the position
            position = {
                'pair': pair,
                'entry_spread': signal['current_spread'],
                'entry_z_score': signal['z_score'],
                'entry_time': datetime.now(),
                'position_size': position_size,
                'order_a': order_a,
                'order_b': order_b,
                'action': signal['action']
            }
            
            self.active_positions.append(position)
            
            print(f"✅ Pairs trade executed:")
            print(f"   Z-score: {signal['z_score']:.2f}")
            print(f"   Spread: {signal['current_spread']:.4f}")
            print(f"   Size: ${position_size}")
            
        except Exception as e:
            print(f"❌ Failed to execute pairs trade: {e}")
    
    async def check_exit_conditions(self, pair):
        """
        Check if we should close any positions
        """
        for position in self.active_positions:
            if position['pair'] != pair:
                continue
            
            # Get current prices
            current_a = get_market_price(pair.market_a_id)
            current_b = get_market_price(pair.market_b_id)
            current_spread = current_a - current_b
            current_z_score = pair.calculate_z_score(current_spread)
            
            should_exit = False
            exit_reason = ""
            
            # Exit condition 1: Spread normalized (z-score < 0.5)
            if abs(current_z_score) < 0.5:
                should_exit = True
                exit_reason = "Spread normalized"
            
            # Exit condition 2: Time-based (held for >14 days)
            days_held = (datetime.now() - position['entry_time']).days
            if days_held > 14:
                should_exit = True
                exit_reason = "Time limit reached"
            
            # Exit condition 3: Stop loss (spread moved against us)
            if position['action'] == 'SELL_A_BUY_B':
                # We profit if spread narrows
                if current_spread > position['entry_spread'] * 1.5:
                    should_exit = True
                    exit_reason = "Stop loss"
            else:
                # We profit if spread widens
                if current_spread < position['entry_spread'] * 0.5:
                    should_exit = True
                    exit_reason = "Stop loss"
            
            if should_exit:
                await self.close_position(position, exit_reason)
    
    async def close_position(self, position, reason):
        """
        Close out a pairs trade position
        """
        try:
            pair = position['pair']
            
            # Close both sides
            if position['action'] == 'SELL_A_BUY_B':
                # Originally sold A, bought B
                # Now buy back A, sell B
                await self.api_client.place_order(
                    market_id=pair.market_a_id,
                    side='BUY',
                    quantity=position['position_size'],
                    order_type='MARKET'
                )
                
                await self.api_client.place_order(
                    market_id=pair.market_b_id,
                    side='SELL',
                    quantity=position['position_size'],
                    order_type='MARKET'
                )
            else:
                await self.api_client.place_order(
                    market_id=pair.market_a_id,
                    side='SELL',
                    quantity=position['position_size'],
                    order_type='MARKET'
                )
                
                await self.api_client.place_order(
                    market_id=pair.market_b_id,
                    side='BUY',
                    quantity=position['position_size'],
                    order_type='MARKET'
                )
            
            # Calculate P&L
            pnl = self.calculate_pnl(position)
            
            print(f"✅ Position closed: {reason}")
            print(f"   P&L: ${pnl:.2f}")
            print(f"   Hold time: {(datetime.now() - position['entry_time']).days} days")
            
            # Remove from active positions
            self.active_positions.remove(position)
            
        except Exception as e:
            print(f"❌ Failed to close position: {e}")
    
    def calculate_position_size(self, confidence, base_size=2000):
        """
        Scale position size based on signal confidence
        """
        # Higher confidence = larger position
        scaled_size = base_size * confidence
        
        # Cap at max size
        max_size = 5000
        return min(scaled_size, max_size)
    
    def calculate_pnl(self, position):
        """
        Calculate profit/loss for closed position
        """
        # Simplified P&L calculation
        # In production, track exact entry/exit prices
        entry_spread = position['entry_spread']
        current_spread = get_current_spread(position['pair'])
        
        if position['action'] == 'SELL_A_BUY_B':
            # Profit if spread narrowed
            spread_change = entry_spread - current_spread
        else:
            # Profit if spread widened
            spread_change = current_spread - entry_spread
        
        pnl = spread_change * position['position_size']
        return pnl
    
    def has_open_position(self, pair):
        """
        Check if we already have a position in this pair
        """
        for position in self.active_positions:
            if position['pair'] == pair:
                return True
        return False
```

## Finding Correlated Pairs

### Manual Curation

Manually identify related markets by topic:

```python
POLITICAL_PAIRS = [
    ("democrats_win_presidency", "democrats_control_senate"),
    ("trump_wins_2024", "republicans_control_house"),
    ("biden_approval_above_50", "democrats_win_2024")
]

CRYPTO_PAIRS = [
    ("btc_hits_100k", "eth_hits_10k"),
    ("btc_above_100k", "crypto_mcap_5trillion"),
    ("coinbase_stock_up_50pct", "btc_above_150k")
]

ECONOMIC_PAIRS = [
    ("fed_raises_rates_march", "sp500_down_10pct_q1"),
    ("recession_2024", "unemployment_above_6pct"),
    ("inflation_above_4pct", "gold_hits_3000")
]
```

### Automated Discovery Using NLP

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def find_related_markets(all_markets, similarity_threshold=0.7):
    """
    Use NLP to find related markets automatically
    """
    # Extract market descriptions
    descriptions = [m['description'] for m in all_markets]
    
    # Vectorize using TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(descriptions)
    
    # Calculate similarity
    similarity_matrix = cosine_similarity(tfidf_matrix)
    
    # Find pairs with high similarity
    pairs = []
    for i in range(len(all_markets)):
        for j in range(i + 1, len(all_markets)):
            if similarity_matrix[i][j] > similarity_threshold:
                pairs.append({
                    'market_a': all_markets[i],
                    'market_b': all_markets[j],
                    'similarity': similarity_matrix[i][j]
                })
    
    return sorted(pairs, key=lambda x: x['similarity'], reverse=True)
```

## Risk Management

### Position Sizing
- **2-5% of capital per pair**
- Scale with confidence (z-score magnitude)
- Maximum 10 pairs open simultaneously

### Stop Losses
- **Time-based:** Close after 14 days regardless
- **Spread-based:** Close if spread moves 50% against you
- **Fundamental:** Close if correlation breaks down

### Diversification
- Don't overload on one topic (e.g., all politics)
- Mix time horizons (short/medium/long)
- Balance positive and negative correlations

## Expected Performance

### Opportunities
- **5-20 signals per week** (depending on market activity)
- **High confidence trades:** 2-5 per week

### Profit Per Trade
- **Winners:** 5-15% profit
- **Losers:** 3-8% loss
- **Average:** 3-5% per trade (after losses)

### Monthly Returns
With $25k capital:
- **Conservative:** $2,500/month (10%)
- **Realistic:** $3,750/month (15%)
- **Aggressive:** $5,000+/month (20%)

### Win Rate
- **60-70%** (lower than arbitrage, but higher profits)

## Real-World Examples

### Example 1: Election Markets (2024)

**Markets:**
- A: "Trump wins 2024 election"
- B: "Republicans control House in 2024"

**Normal correlation:** 0.75 (strong positive)

**Event:** Trump has bad debate performance
- Market A drops from 58¢ to 45¢ (dropped 13¢)
- Market B only drops from 55¢ to 52¢ (dropped 3¢)

**Analysis:**
- Historical spread: ~3¢
- Current spread: 7¢ (abnormal)
- Z-score: 2.8 (strong signal)

**Trade:**
- BUY Trump market at 45¢
- SELL Republican House at 52¢

**Outcome (3 days later):**
- Trump recovers to 50¢
- Republicans at 53¢
- Spread: 3¢ (normalized)
- **Profit: $0.05 per share = 10% gain**

### Example 2: Crypto Markets

**Markets:**
- A: "Bitcoin above $100k by Dec 31"
- B: "Ethereum above $5k by Dec 31"

**Normal correlation:** 0.85 (very strong)

**Event:** Bitcoin-specific news (ETF approval)
- Bitcoin market jumps to 75¢
- Ethereum lags at 58¢

**Trade:**
- SELL Bitcoin at 75¢
- BUY Ethereum at 58¢

**Outcome:**
- Markets converge over next week
- **Profit: 8% gain**

## Advanced Techniques

### 1. Three-Way Correlation

```python
# Trade triangular relationships
# If A correlates with B and C, but B-C diverge
# Trade B-C while hedging with A
```

### 2. Dynamic Correlation Tracking

```python
# Update correlation coefficients daily
# Adapt to changing market dynamics
```

### 3. Volatility Adjustment

```python
# Widen thresholds during high volatility
# Tighten during stable periods
```

## Common Mistakes

1. **Confusing correlation with causation**
2. **Ignoring fundamental changes**
3. **Overleveraging on high z-scores**
4. **Not setting stop losses**
5. **Holding positions too long**

## Next Steps

1. **Build correlation tracking system**
2. **Identify 10-20 strong pairs**
3. **Paper trade for 2 weeks**
4. **Deploy with $2k per pair**
5. **Monitor and optimize**

---

**[← Previous: Arbitrage](./strategy_1_arbitrage.md)** | **[Next: Probability Models →](./strategy_3_probability_models.md)**

---

*This is Strategy 2 of 5 in the PolyMarket Trading Bot series*  
*Last Updated: December 25, 2025*

