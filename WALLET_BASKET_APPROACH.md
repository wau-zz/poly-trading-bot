# Wallet Basket Approach - Strategy 5 Evolution

## The Insight

After analyzing **~1.3M PolyMarket wallets**, a key insight emerged:

> **"Copying one 'smart' trader is fragile. Even the best ones drift."**

**Solution:** Build **wallet baskets by topic** and trade on **consensus signals** rather than following individuals.

## Why Wallet Baskets Work Better

### Individual Copy Trading Problems
- ❌ Single point of failure
- ❌ Even best traders drift
- ❌ Personality bias
- ❌ Fragile strategy

### Wallet Basket Benefits
- ✅ More robust (not dependent on one trader)
- ✅ Consensus signals (80%+ agreement)
- ✅ Handles individual wallet drift
- ✅ Feels like "trading agreement forming in real time"
- ✅ Less like "tailing a personality"

## Wallet Basket Construction

### Filtering Criteria

```python
# 1. Age Requirement
MIN_WALLET_AGE = 6 months  # Only wallets older than 6 months

# 2. Bot Detection
FILTER_BOTS = True  # Filter out wallets doing thousands of micro-trades

# 3. Performance Weighting
RECENT_WEIGHT = 70%  # Recent win rate weighted more than all-time
ALL_TIME_WEIGHT = 30%

# Recent Time Windows
- Last 7 days win rate
- Last 30 days win rate

# 4. Ranking
RANK_BY = "avg entry vs final price"  # Best wallets enter at better prices

# 5. Copycat Detection
FILTER_COPYCATS = True  # Ignore wallets that copy each other
```

### Example: Geopolitics Basket

```
Topic: Geopolitics

Filtering:
→ Only wallets older than 6 months
→ No bots (filtered out wallets doing thousands of micro-trades)
→ Recent win rate weighted more than all-time (last 7 days and last 30 days)
→ Ranked by avg entry vs final price
→ Ignoring copycat clusters

Result: Basket of 50-100 specialized geopolitics traders
```

## Consensus Signal Logic

### Signal Detection

```python
CONSENSUS_THRESHOLD = 80%  # 80%+ of basket must agree

Signal Logic:
1. Wait until 80%+ of basket enters the same outcome
2. Check they're all buying within a tight price band
3. Only trigger if spread isn't "cooked" yet
4. Execute trade based on consensus
```

### Example Signal

```
Market: "Will Russia invade Ukraine by March 2024?"

Basket Analysis:
- Total wallets in basket: 50
- Wallets that traded: 45
- Wallets buying YES: 38 (84% consensus)
- Wallets buying NO: 7

Price Analysis:
- Avg entry price: $0.42
- Price range: $0.40 - $0.44 (tight band ✅)
- Current price: $0.43
- Spread movement: 2% (not cooked ✅)

Signal: ✅ CONSENSUS DETECTED
Action: Buy YES at $0.43
```

## Implementation Steps

### 1. Wallet Scanning
- Scan all PolyMarket wallets (1.3M+)
- Calculate performance metrics
- Identify topic specialization

### 2. Basket Construction
- Filter by topic (geopolitics, crypto, sports, etc.)
- Apply filtering criteria
- Rank by performance

### 3. Real-Time Monitoring
- Monitor basket wallets for new trades
- Track consensus formation
- Detect signals

### 4. Signal Execution
- Wait for 80%+ consensus
- Verify price band tightness
- Check spread hasn't moved
- Execute trade

## Current Status

**MVP Status:** Built and testing quietly

**Testing Approach:**
- Paper trading to avoid bias
- Monitoring signal quality
- Refining filtering criteria

## Key Differences from Individual Copy Trading

| Aspect | Individual Copy | Wallet Basket |
|--------|----------------|---------------|
| **Dependency** | Single trader | Basket of traders |
| **Signal** | One trader's trade | 80%+ consensus |
| **Robustness** | Fragile | More robust |
| **Drift Handling** | Fails if trader drifts | Handles individual drift |
| **Feel** | "Tailing a personality" | "Trading agreement forming" |

## Advantages

✅ **More robust** - Not dependent on single trader  
✅ **Consensus signals** - Trade on agreement, not personality  
✅ **Less fragile** - Basket can handle individual wallet drift  
✅ **Topic specialization** - Baskets by expertise area  
✅ **Real-time agreement** - Feels like "trading agreement forming"  
✅ **Sophisticated filtering** - Age, bot detection, copycat filtering  

## Challenges

❌ **More complex** - Requires basket construction and consensus detection  
❌ **Data intensive** - Need to analyze 1.3M+ wallets  
❌ **Signal delay** - Wait for 80%+ consensus  
❌ **May miss early moves** - Consensus takes time to form  

## Next Steps

1. **Refine filtering criteria** based on testing
2. **Optimize consensus threshold** (maybe 75% vs 80%?)
3. **Build multiple baskets** (geopolitics, crypto, sports, etc.)
4. **Test signal quality** in paper trading
5. **Scale to live trading** once validated

---

**Note:** This approach is currently being tested in paper trading. Results and refinements will be shared as the MVP evolves.










