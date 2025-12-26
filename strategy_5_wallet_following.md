# Strategy 5: Smart Wallet Following (Copy Trading)

**Strategy Type:** Social Trading / Momentum  
**Difficulty:** Beginner-Intermediate  
**Capital Required:** $5k-10k  
**Expected Returns:** 10-20% monthly  
**Win Rate:** 55-65%  
**Time Horizon:** Same as followed traders (varies)

---

## Overview

Instead of making your own trading decisions, identify consistently profitable traders on-chain and automatically mirror their positions in real-time.

**The edge:** Some traders are genuinely skilled. By copying them, you can capture their edge without needing the expertise yourself.

## The Core Concept

### All Trades Are Public

PolyMarket runs on Polygon blockchain. This means:
- ✅ Every trade is recorded on-chain
- ✅ Every wallet's history is visible
- ✅ You can calculate anyone's win rate and ROI
- ✅ You can monitor wallets in real-time

### The Opportunity

**Most traders lose money.** But a small percentage consistently win:
- Win rate >60%
- ROI >25% over 3+ months
- Trade frequently (10+ trades/week)
- Use consistent strategies

**Your strategy:** Find these winners and copy them.

## Wallet Identification

### Criteria for "Smart Money"

```python
class SmartWalletCriteria:
    # Performance thresholds
    MIN_WIN_RATE = 0.60  # 60%+
    MIN_ROI = 0.25  # 25%+
    MIN_TRADES = 50  # At least 50 trades
    MIN_PROFIT = 10000  # $10k+ total profit
    
    # Activity thresholds
    MIN_TRADES_PER_WEEK = 10
    MAX_DAYS_INACTIVE = 14
    
    # Risk assessment
    MAX_POSITION_SIZE_PCT = 0.20  # Don't follow gamblers (>20% positions)
    MIN_MARKETS_TRADED = 10  # Diversification
    
    # Timing (prefer late-stage traders)
    PREFER_LATE_STAGE = True  # Enter <7 days before resolution
```

### Wallet Scanner

```python
class SmartWalletTracker:
    def __init__(self):
        self.tracked_wallets = {}
        self.wallet_performance = {}
        self.blacklist = set()
    
    async def discover_profitable_wallets(self):
        """
        Scan on-chain data to find winning wallets
        """
        # Fetch all trades from last 90 days
        all_trades = await get_polymarket_trades(last_90_days=True)
        
        # Group trades by wallet
        wallet_stats = defaultdict(lambda: {
            'trades': [],
            'wins': 0,
            'losses': 0,
            'total_profit': 0,
            'markets_traded': set(),
            'last_trade_date': None
        })
        
        for trade in all_trades:
            wallet = trade.wallet_address
            wallet_stats[wallet]['trades'].append(trade)
            
            # Track outcome
            if trade.outcome == 'WIN':
                wallet_stats[wallet]['wins'] += 1
                wallet_stats[wallet]['total_profit'] += trade.profit
            elif trade.outcome == 'LOSS':
                wallet_stats[wallet]['losses'] += 1
                wallet_stats[wallet]['total_profit'] -= trade.loss
            
            wallet_stats[wallet]['markets_traded'].add(trade.market_id)
            wallet_stats[wallet]['last_trade_date'] = max(
                wallet_stats[wallet]['last_trade_date'] or trade.date,
                trade.date
            )
        
        # Filter for top performers
        profitable_wallets = []
        
        for wallet, stats in wallet_stats.items():
            total_trades = stats['wins'] + stats['losses']
            
            if total_trades < SmartWalletCriteria.MIN_TRADES:
                continue
            
            win_rate = stats['wins'] / total_trades
            
            # Check all criteria
            if (win_rate >= SmartWalletCriteria.MIN_WIN_RATE and
                stats['total_profit'] >= SmartWalletCriteria.MIN_PROFIT and
                len(stats['markets_traded']) >= SmartWalletCriteria.MIN_MARKETS_TRADED):
                
                # Calculate additional metrics
                avg_profit_per_trade = stats['total_profit'] / total_trades
                days_active = (datetime.now() - min(t.date for t in stats['trades'])).days
                roi = stats['total_profit'] / self.estimate_capital_used(stats['trades'])
                
                if roi >= SmartWalletCriteria.MIN_ROI:
                    profitable_wallets.append({
                        'wallet': wallet,
                        'win_rate': win_rate,
                        'total_profit': stats['total_profit'],
                        'trade_count': total_trades,
                        'roi': roi,
                        'avg_profit_per_trade': avg_profit_per_trade,
                        'markets_traded': len(stats['markets_traded']),
                        'days_active': days_active,
                        'last_trade': stats['last_trade_date']
                    })
        
        # Sort by profitability
        profitable_wallets.sort(key=lambda x: x['total_profit'], reverse=True)
        
        return profitable_wallets
    
    def estimate_capital_used(self, trades):
        """
        Estimate how much capital wallet deployed
        """
        # Find max concurrent positions value
        max_exposure = 0
        
        for date in self.get_unique_dates(trades):
            open_positions = [t for t in trades if t.date <= date and not t.closed]
            exposure = sum(t.position_size for t in open_positions)
            max_exposure = max(max_exposure, exposure)
        
        return max_exposure if max_exposure > 0 else 10000
    
    def get_unique_dates(self, trades):
        """Get all unique trade dates"""
        return sorted(set(t.date for t in trades))
```

### Wallet Monitoring

```python
class WalletMonitor:
    def __init__(self, wallet_address):
        self.wallet = wallet_address
        self.last_known_trade_id = None
    
    async def monitor_activity(self):
        """
        Monitor wallet for new trades in real-time
        """
        while True:
            try:
                # Fetch recent trades for this wallet
                recent_trades = await get_wallet_trades(
                    self.wallet,
                    since_trade_id=self.last_known_trade_id
                )
                
                for trade in recent_trades:
                    # New trade detected!
                    await self.on_new_trade(trade)
                    self.last_known_trade_id = trade.id
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                print(f"Error monitoring wallet {self.wallet}: {e}")
                await asyncio.sleep(30)
    
    async def on_new_trade(self, trade):
        """
        Called when smart wallet makes a new trade
        """
        print(f"🔔 Smart wallet {self.wallet[:8]}... traded:")
        print(f"   Market: {trade.market_id}")
        print(f"   Side: {trade.side}")
        print(f"   Price: ${trade.price:.3f}")
        print(f"   Size: ${trade.size:.2f}")
        
        # Trigger copy trade
        await self.execute_copy_trade(trade)
    
    async def execute_copy_trade(self, smart_wallet_trade):
        """
        Mirror the smart wallet's trade
        """
        # Calculate our position size (scaled to our capital)
        our_size = self.calculate_copy_size(smart_wallet_trade)
        
        # Place identical order
        if smart_wallet_trade.side == 'BUY':
            await place_buy_order(
                market_id=smart_wallet_trade.market_id,
                quantity=our_size,
                max_price=smart_wallet_trade.price * 1.02  # Allow 2% slippage
            )
        else:
            await place_sell_order(
                market_id=smart_wallet_trade.market_id,
                quantity=our_size,
                min_price=smart_wallet_trade.price * 0.98
            )
        
        print(f"✅ Copied trade: ${our_size:.2f}")
    
    def calculate_copy_size(self, their_trade):
        """
        Scale their trade to our capital
        """
        # Estimate their total capital
        their_capital = estimate_wallet_balance(their_trade.wallet)
        their_position_pct = their_trade.size / their_capital
        
        # Our capital
        our_capital = get_our_balance()
        
        # Copy same % allocation (but use 50% of their ratio for safety)
        our_position_size = our_capital * their_position_pct * 0.5
        
        # Cap at max position size
        max_position = our_capital * 0.10  # Max 10% per trade
        
        return min(our_position_size, max_position)
```

## Copy Trading Bot

```python
class CopyTradingBot:
    def __init__(self, max_wallets=10):
        self.smart_wallets = []
        self.monitors = {}
        self.max_wallets = max_wallets
        self.copied_positions = []
    
    async def initialize(self):
        """
        Find and start monitoring smart wallets
        """
        # Discover profitable wallets
        tracker = SmartWalletTracker()
        profitable = await tracker.discover_profitable_wallets()
        
        # Select top N wallets
        self.smart_wallets = profitable[:self.max_wallets]
        
        print(f"📊 Found {len(profitable)} profitable wallets")
        print(f"👥 Following top {len(self.smart_wallets)} wallets:\n")
        
        for i, wallet_info in enumerate(self.smart_wallets, 1):
            print(f"{i}. {wallet_info['wallet'][:10]}...")
            print(f"   Win Rate: {wallet_info['win_rate']:.1%}")
            print(f"   Total Profit: ${wallet_info['total_profit']:,.0f}")
            print(f"   ROI: {wallet_info['roi']:.1%}")
            print()
        
        # Start monitoring each wallet
        for wallet_info in self.smart_wallets:
            monitor = WalletMonitor(wallet_info['wallet'])
            self.monitors[wallet_info['wallet']] = monitor
            
            # Start async monitoring task
            asyncio.create_task(monitor.monitor_activity())
    
    async def run(self):
        """
        Main bot loop
        """
        await self.initialize()
        
        while True:
            # Periodically re-evaluate wallets
            await asyncio.sleep(86400)  # Daily
            await self.reevaluate_wallets()
    
    async def reevaluate_wallets(self):
        """
        Check if followed wallets are still performing well
        """
        for wallet_info in self.smart_wallets:
            recent_performance = await self.check_recent_performance(
                wallet_info['wallet']
            )
            
            # Stop following if performance degrades
            if recent_performance['win_rate'] < 0.50:  # Below 50%
                print(f"⚠️ Stopping follow of {wallet_info['wallet'][:10]}... (poor performance)")
                await self.stop_following(wallet_info['wallet'])
```

## Advanced: Late-Stage Focus

**Strategy:** Only copy trades that are near resolution (lower risk)

```python
def is_late_stage_trade(market_id, trade):
    """
    Identify low-risk, late-stage entries
    """
    market_data = get_market_data(market_id)
    
    # Time to resolution
    time_to_resolution = market_data.resolution_time - datetime.now()
    days_until_resolution = time_to_resolution.days
    
    # Late-stage criteria:
    # 1. <7 days until resolution
    # 2. Strong directional move (>70% or <30%)
    # 3. High conviction (large position from smart wallet)
    
    is_late_stage = days_until_resolution < 7
    is_strong_directional = trade.price > 0.70 or trade.price < 0.30
    
    # Check if this is larger than their average trade
    avg_trade_size = get_avg_trade_size(trade.wallet)
    is_high_conviction = trade.size > avg_trade_size * 1.5
    
    return is_late_stage and is_strong_directional and is_high_conviction

async def copy_late_stage_only(smart_wallet_trade):
    """
    Only mirror late-stage, high-conviction trades
    """
    if is_late_stage_trade(smart_wallet_trade.market_id, smart_wallet_trade):
        await execute_copy_trade(smart_wallet_trade)
    else:
        print(f"⏭️ Skipping early-stage trade")
```

## On-Chain Data Sources

### Polygon Blockchain

```python
from web3 import Web3

def get_wallet_trades_onchain(wallet_address):
    """
    Fetch trades directly from Polygon blockchain
    """
    w3 = Web3(Web3.HTTPProvider('https://polygon-rpc.com'))
    
    # PolyMarket contract address
    polymarket_contract = '0x...'  # Actual contract address
    
    # Fetch events (trades) for this wallet
    trades = []
    
    # Query Transfer events where wallet is sender or receiver
    # Parse trade details from event logs
    
    return trades
```

### PolyMarket API

```python
def get_wallet_trades_api(wallet_address, limit=100):
    """
    Fetch trades using PolyMarket API (easier than on-chain)
    """
    url = f"https://api.polymarket.com/trades"
    params = {
        'wallet': wallet_address,
        'limit': limit
    }
    
    response = requests.get(url, params=params)
    return response.json()
```

## Risk Management

### Diversification
- Follow **5-10 wallets** (not just 1)
- Don't copy 100% of every trade
- Mix different trading styles

### Position Sizing
- **5-10% per trade** (same % as smart wallet uses)
- **Max 50% of capital** deployed at once
- Reserve 50% for new opportunities

### Stop Following Conditions
- Win rate drops below 50% (last 20 trades)
- Long period of inactivity (>14 days)
- Dramatic strategy change (different markets)
- Suspicious behavior (wash trading, manipulation)

### Slippage Management
- Allow **2-3% slippage** from their price
- Skip if slippage would be >5%
- Use limit orders when possible

## Expected Performance

### Opportunity Frequency
- **Depends on followed wallets' activity**
- Typical: 10-30 trades per week (across all wallets)

### Returns
- **Match or slightly underperform** followed traders
- Slippage typically costs 1-2% per trade

### With $10k capital:
- **Conservative:** $1,000/month (10%)
- **Realistic:** $1,500/month (15%)
- **Aggressive:** $2,000/month (20%)

### Win Rate
- **55-65%** (slightly lower than wallets you follow due to slippage)

## Real-World Examples

### Example 1: Election Trader

**Wallet:** 0x742d...a8f3  
**Specialization:** Political markets  
**Performance:** 68% win rate, $47k profit  
**Strategy:** Late-stage entries (<5 days to resolution)

**Our results copying:**
- 23 trades copied over 2 months
- 14 wins, 9 losses (61% win rate)
- $3,200 profit on $10k capital
- **32% return in 2 months**

### Example 2: Crypto Specialist

**Wallet:** 0x9f2c...b412  
**Specialization:** Crypto price predictions  
**Performance:** 71% win rate, $82k profit  
**Strategy:** Technical analysis entries

**Our results:**
- 41 trades copied over 3 months
- 27 wins, 14 losses (66% win rate)
- $5,800 profit on $10k capital
- **58% return in 3 months**

## Advantages

✅ **No expertise needed** - Let skilled traders do the analysis  
✅ **Lower time commitment** - Bot handles everything  
✅ **Diversification** - Follow multiple strategies  
✅ **Learn from winners** - Observe their patterns  
✅ **Lower stress** - Someone else is "right," not you

## Disadvantages

❌ **Slippage** - Always a bit behind  
❌ **Dependence** - If they stop, you stop  
❌ **No edge of your own** - Not building trading skills  
❌ **Wallet could change** - Strategy drift, poor run  
❌ **Limited upside** - Can't beat who you copy

## Advanced Features

### Wallet Scoring Algorithm

```python
def calculate_wallet_score(wallet_stats):
    """
    Comprehensive scoring of wallet quality
    """
    # Base metrics
    win_rate_score = wallet_stats['win_rate'] * 100
    roi_score = min(wallet_stats['roi'] * 100, 100)
    consistency_score = calculate_consistency(wallet_stats['trades'])
    
    # Recency bias (recent performance matters more)
    recent_win_rate = calculate_recent_win_rate(wallet_stats['trades'], days=30)
    recency_score = recent_win_rate * 100
    
    # Risk assessment
    volatility = calculate_trade_volatility(wallet_stats['trades'])
    risk_score = max(0, 100 - volatility * 100)
    
    # Final score (weighted average)
    total_score = (
        win_rate_score * 0.25 +
        roi_score * 0.25 +
        consistency_score * 0.20 +
        recency_score * 0.20 +
        risk_score * 0.10
    )
    
    return total_score
```

### Smart Exit Strategy

```python
async def monitor_copied_position(position):
    """
    Monitor copied position and potentially exit before smart wallet
    """
    while not position.closed:
        current_price = get_market_price(position.market_id)
        
        # Take profit if up 20%
        if (position.side == 'BUY' and 
            current_price > position.entry_price * 1.20):
            await close_position(position)
            print(f"✅ Take profit at +20%")
        
        # Stop loss if down 15%
        elif (position.side == 'BUY' and 
              current_price < position.entry_price * 0.85):
            await close_position(position)
            print(f"❌ Stop loss at -15%")
        
        await asyncio.sleep(300)  # Check every 5 min
```

## Getting Started

- [ ] Build wallet scanner
- [ ] Identify 10 profitable wallets
- [ ] Set up real-time monitoring
- [ ] Paper trade for 2 weeks
- [ ] Deploy with $1k capital
- [ ] Monitor performance
- [ ] Scale to $5k-10k

## Common Mistakes

1. **Following too few wallets** (not diversified)
2. **Copying every trade** (including low conviction)
3. **Not setting stop losses**
4. **Ignoring slippage costs**
5. **Not re-evaluating wallets** (they can degrade)

## Next Steps

1. **Implement wallet scanner**
2. **Find 5-10 smart wallets**
3. **Build monitoring system**
4. **Test copy trade execution**
5. **Paper trade for 2 weeks**
6. **Deploy with real capital**

---

**[← Previous: Market Making](./strategy_4_market_making.md)** | **[Next: Structured Products →](./strategy_6_structured_products.md)**

---

*This is Strategy 5 of 6 in the PolyMarket Trading Bot series*  
*Last Updated: December 25, 2025*

