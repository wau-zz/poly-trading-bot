# Strategy 1: Price Mismatch Sniping (Risk-Free Arbitrage)

**Strategy Type:** Risk-Free Arbitrage  
**Difficulty:** Beginner-Intermediate  
**Capital Required:** $5k-20k  
**Expected Returns:** 5-10% monthly  
**Win Rate:** 95%+  
**Time Horizon:** Instant to days (for settlement)

---

## Overview

Price mismatch sniping exploits momentary pricing errors where both outcomes of a binary market are underpriced simultaneously. This creates **risk-free profit** opportunities.

## The Core Concept

In a binary prediction market, there are two outcomes:
- **YES** (the event happens)
- **NO** (the event doesn't happen)

One of these must pay out $1.00 per share. The other pays out $0.00.

**Normal market pricing:**
- YES: $0.60
- NO: $0.40
- Total: $1.00 ✅ (makes sense)

**Arbitrage opportunity:**
- YES: $0.52
- NO: $0.46
- Total: $0.98 ❌ (pricing error!)

You can buy BOTH sides for $0.98, and you're guaranteed to receive $1.00 when the market resolves.

**Risk-free profit: $0.02 per dollar invested (2% instant return)**

## Real-World Example

**Market:** "Will Bitcoin hit $100,000 by December 31st?"

**Prices at 3:47 PM:**
- YES shares: $0.52
- NO shares: $0.46

**Your action:**
- Buy 100 YES shares = $52
- Buy 100 NO shares = $46
- **Total investment: $98**

**Outcome A - Bitcoin hits $100k:**
- Your YES shares pay: 100 × $1.00 = **$100**
- Your NO shares pay: 100 × $0.00 = $0
- **Profit: $2**

**Outcome B - Bitcoin doesn't hit $100k:**
- Your YES shares pay: 100 × $0.00 = $0
- Your NO shares pay: 100 × $1.00 = **$100**
- **Profit: $2**

**Either way, you make $2 profit.** The outcome doesn't matter!

## Implementation

### Detection Logic

```python
def detect_arbitrage(market):
    """
    Detect risk-free arbitrage opportunities
    """
    outcome_a_price = market.yes_price
    outcome_b_price = market.no_price
    
    total_cost = outcome_a_price + outcome_b_price
    
    # Account for fees (typically 2-3%)
    fee_threshold = 0.03
    profit_margin = 1.00 - total_cost - fee_threshold
    
    if profit_margin > 0:
        return {
            'arbitrage': True,
            'profit_per_dollar': profit_margin,
            'buy_yes': outcome_a_price,
            'buy_no': outcome_b_price,
            'total_investment': total_cost,
            'expected_profit': profit_margin
        }
    
    return None


def is_profitable_arbitrage(yes_price, no_price, fee_rate=0.02):
    """
    Check if arbitrage is profitable after fees
    Include a minimum profit threshold to make it worth the capital lockup
    """
    total_cost = yes_price + no_price
    fees = total_cost * fee_rate
    
    total_cost_with_fees = total_cost + fees
    
    # Need at least 1% profit after fees to be worthwhile
    min_profit_threshold = 0.01
    
    if total_cost_with_fees < (1.0 - min_profit_threshold):
        profit_margin = 1.0 - total_cost_with_fees
        return True, profit_margin
    
    return False, 0
```

### Execution Engine

```python
import asyncio
from datetime import datetime

class ArbitrageBot:
    def __init__(self, api_client, min_profit_pct=0.01):
        self.api_client = api_client
        self.min_profit_pct = min_profit_pct
        self.positions = []
        
    async def scan_markets(self):
        """
        Continuously scan all active markets for arbitrage
        """
        while True:
            try:
                markets = await self.api_client.get_active_markets()
                
                for market in markets:
                    opportunity = self.detect_arbitrage_opportunity(market)
                    
                    if opportunity:
                        await self.execute_arbitrage(market, opportunity)
                
                # Check every 100ms (10 times per second)
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"Error scanning markets: {e}")
                await asyncio.sleep(5)
    
    def detect_arbitrage_opportunity(self, market):
        """
        Check if market presents arbitrage opportunity
        """
        yes_price = market['yes_price']
        no_price = market['no_price']
        
        is_arb, profit_margin = is_profitable_arbitrage(
            yes_price, 
            no_price,
            fee_rate=0.02
        )
        
        if is_arb and profit_margin >= self.min_profit_pct:
            return {
                'market_id': market['id'],
                'yes_price': yes_price,
                'no_price': no_price,
                'profit_margin': profit_margin,
                'total_cost': yes_price + no_price
            }
        
        return None
    
    async def execute_arbitrage(self, market, opportunity):
        """
        Execute both sides of arbitrage trade
        """
        try:
            # Calculate position size
            investment = self.calculate_position_size(
                opportunity['profit_margin']
            )
            
            shares = investment / opportunity['total_cost']
            
            # Execute BOTH sides simultaneously
            yes_order, no_order = await asyncio.gather(
                self.api_client.place_order(
                    market_id=opportunity['market_id'],
                    side='YES',
                    quantity=shares,
                    price=opportunity['yes_price']
                ),
                self.api_client.place_order(
                    market_id=opportunity['market_id'],
                    side='NO',
                    quantity=shares,
                    price=opportunity['no_price']
                )
            )
            
            # Log the trade
            self.log_arbitrage({
                'timestamp': datetime.now(),
                'market_id': opportunity['market_id'],
                'investment': investment,
                'expected_profit': investment * opportunity['profit_margin'],
                'profit_pct': opportunity['profit_margin'] * 100,
                'yes_order_id': yes_order['id'],
                'no_order_id': no_order['id']
            })
            
            print(f"✅ Arbitrage executed! Expected profit: ${investment * opportunity['profit_margin']:.2f}")
            
        except Exception as e:
            print(f"❌ Failed to execute arbitrage: {e}")
    
    def calculate_position_size(self, profit_margin):
        """
        Calculate how much to invest in this opportunity
        Higher profit margins = larger positions
        """
        base_size = 1000  # Base investment per trade
        max_size = 5000   # Maximum per trade
        
        # Scale up for better opportunities
        scaled_size = base_size * (1 + profit_margin * 10)
        
        return min(scaled_size, max_size)
    
    def log_arbitrage(self, trade_data):
        """Log trade for tracking and analysis"""
        self.positions.append(trade_data)
        # Also log to database, file, etc.
```

## Execution Requirements

### Speed is Critical

Arbitrage opportunities often last only **seconds to minutes** before being corrected. You need:

1. **WebSocket connections** (not REST API polling)
   - Real-time price updates
   - Sub-100ms latency
   
2. **Instant execution**
   - Pre-calculated position sizes
   - Orders ready to fire
   - No human approval needed

3. **24/7 monitoring**
   - Bot runs continuously
   - Hosted on reliable server
   - Automatic restarts on errors

### Capital Management

- **Liquidity:** Keep 80%+ in stablecoins ready to deploy
- **Position size:** $500-5,000 per arbitrage
- **Maximum exposure:** 50% of capital in pending settlements
- **Reserve:** 20% for unexpected opportunities

### Best Markets for Arbitrage

Focus on markets with:
- ✅ High volume (>$500k)
- ✅ Fast movement (crypto, sports, breaking news)
- ✅ Clear settlement (objective outcomes)
- ✅ Short duration (<30 days to resolution)

**Examples:**
- Crypto price targets ("BTC above $100k by [date]")
- Sports games (game outcomes, player stats)
- Political events with clear resolution
- Economic data releases (jobs report, CPI)

## Risk Factors

Despite being "risk-free" in theory, practical risks exist:

### 1. Execution Risk
**Problem:** Prices change between detection and execution  
**Solution:** Place both orders simultaneously with max slippage limits

### 2. Fee Risk
**Problem:** Trading fees eat into thin margins  
**Solution:** Only trade when profit > 3× fees

### 3. Liquidity Risk
**Problem:** Can't get filled at displayed price  
**Solution:** Check order book depth before executing

### 4. Platform Risk
**Problem:** Market resolution disputes, platform downtime  
**Solution:** Diversify across platforms, read market rules carefully

### 5. Settlement Risk
**Problem:** Capital locked until market resolves (days to weeks)  
**Solution:** Limit exposure to 50% of capital, prefer faster-resolving markets

## Expected Performance

### Opportunities
- **High volatility days:** 20-50 arbitrages
- **Normal days:** 5-15 arbitrages
- **Slow days:** 1-5 arbitrages

### Profit Per Trade
- **Typical:** 1-3% profit per arbitrage
- **Good:** 3-5% profit
- **Rare:** 5-10% profit (usually errors or breaking news)

### Monthly Returns
With $20k capital deployed:
- **Conservative:** $1,000-1,500/month (5-7.5%)
- **Realistic:** $1,500-2,000/month (7.5-10%)
- **Aggressive:** $2,000+/month (>10%)

### Win Rate
- **Successful execution:** 95%+
- **Failed trades:** 5% (slippage, order failures)
- **Net loss trades:** <1% (platform issues)

## Advanced Techniques

### 1. Multi-Platform Arbitrage

```python
async def cross_platform_arbitrage():
    """
    Find arbitrage across PolyMarket, Kalshi, etc.
    """
    polymarket_yes = 0.53
    kalshi_no = 0.45
    
    total = 0.53 + 0.45
    fees = 0.04  # 2% per platform
    
    if total + fees < 0.99:
        # Buy YES on PolyMarket, NO on Kalshi
        await execute_cross_platform_arb()
```

### 2. Order Book Analysis

```python
def check_liquidity_depth(market):
    """
    Ensure sufficient liquidity before executing
    """
    order_book = get_order_book(market)
    
    yes_liquidity = sum(order['size'] for order in order_book['yes_asks'][:5])
    no_liquidity = sum(order['size'] for order in order_book['no_asks'][:5])
    
    min_required = 1000  # Minimum $1k liquidity
    
    return yes_liquidity > min_required and no_liquidity > min_required
```

### 3. Dynamic Position Sizing

```python
def kelly_criterion_sizing(profit_margin, win_rate=0.95):
    """
    Optimal position sizing using Kelly Criterion
    """
    # Kelly = (Win Rate × Profit) - (Loss Rate / Loss)
    # For arbitrage: very high win rate, small profit
    
    loss_rate = 1 - win_rate
    kelly_pct = (win_rate * profit_margin - loss_rate) / profit_margin
    
    # Use fractional Kelly (e.g., 50%) for safety
    fractional_kelly = kelly_pct * 0.5
    
    return fractional_kelly
```

## Monitoring & Optimization

### Key Metrics to Track

```python
class ArbitrageMetrics:
    def __init__(self):
        self.total_opportunities_detected = 0
        self.successful_executions = 0
        self.failed_executions = 0
        self.total_profit = 0
        self.total_capital_deployed = 0
        self.average_profit_margin = 0
        self.average_hold_time = 0  # Time until settlement
    
    def calculate_roi(self):
        return (self.total_profit / self.total_capital_deployed) * 100
    
    def calculate_win_rate(self):
        total = self.successful_executions + self.failed_executions
        return (self.successful_executions / total) * 100 if total > 0 else 0
```

### Alerts to Set Up

- ✅ Successful arbitrage execution
- ❌ Failed execution (investigate why)
- ⚠️ Unusual arbitrage (>5% profit - might be error)
- 📊 Daily summary (opportunities found, profit made)
- 🚨 API errors or connection issues

## Real Trader Results

Anonymous trader reports from Twitter/Discord:

**Trader A:** "Running arb bot for 3 months, averaging $3-5k/month on $25k capital. Win rate 94%. Most profitable during crypto volatility."

**Trader B:** "Made $47k in arbitrage profits over 6 months. Had to increase capital from $10k to $50k because opportunities outpaced available funds."

**Trader C:** "Arbitrage is my 'risk-free' base. I deploy 30% of capital here for steady income while testing riskier strategies with the rest."

## Getting Started Checklist

- [ ] Set up PolyMarket API access (get API keys)
- [ ] Build market data collection (WebSocket feed)
- [ ] Implement arbitrage detection logic
- [ ] Create order execution module
- [ ] Test on paper trading (log would-be trades)
- [ ] Deploy with $500-1,000 initial capital
- [ ] Monitor for 1 week, verify profitability
- [ ] Scale up to $5k-20k capital
- [ ] Set up automated monitoring and alerts

## Common Mistakes to Avoid

1. **Forgetting fees** - Always account for 2-3% total fees
2. **Ignoring slippage** - Set max slippage tolerance (2-3%)
3. **Oversizing positions** - Start small, scale gradually
4. **Chasing tiny edges** - <1% profit often not worth it
5. **Not checking liquidity** - Can't execute if order book is thin
6. **Missing one side** - MUST execute both sides simultaneously
7. **No error handling** - Bots crash, have automatic restarts

## Next Steps

1. **Implement the detection algorithm** from this document
2. **Connect to PolyMarket API** for real-time data
3. **Paper trade for 1 week** to validate logic
4. **Deploy with $500** to test real execution
5. **Scale to $5k-20k** once proven profitable
6. **Monitor and optimize** based on results

---

**[← Back to Overview](./OVERVIEW.md)** | **[Next Strategy: Pairs Trading →](./strategy_2_pairs_trading.md)**

---

*This is Strategy 1 of 5 in the PolyMarket Trading Bot series*  
*Last Updated: December 25, 2025*

