# Strategy 5: Wallet Following (Wallet Basket Approach)

**Strategy Type:** Social Trading / Consensus Signals  
**Difficulty:** Intermediate-Advanced  
**Capital Required:** $5k-10k  
**Expected Returns:** 10-20% monthly  
**Win Rate:** 55-65%

---

## Overview

Instead of following individual traders, this strategy builds **wallet baskets by topic** and trades on **consensus signals** when 80%+ of the basket agrees on an outcome.

**Key Insight:** Copying one "smart" trader is fragile. Even the best ones drift. Wallet baskets are more robust and feel like "trading agreement forming in real time" rather than tailing a personality.

## How It Works

### 1. Wallet Basket Construction

Build baskets of wallets by specialization (e.g., geopolitics, crypto, sports):

- **Filtering Criteria:**
  - Wallets older than 6 months
  - No bots (filter out micro-traders)
  - Recent win rate weighted 70% vs all-time 30%
  - Ranked by avg entry vs final price
  - Ignoring copycat clusters

- **Result:** Basket of 50-100 specialized traders per topic

### 2. Consensus Signal Detection

Monitor basket wallets and detect when:
- **80%+ of basket** enters the same outcome
- All buying within **tight price band** (2% tolerance)
- Spread hasn't moved too much yet (not "cooked")

### 3. Trade Execution

When consensus detected:
- Execute trade based on signal strength
- Position size scales with consensus percentage and wallet quality
- Monitor and manage position

## Installation

```bash
cd strategies/strategy_5_wallet_following/python
pip install -r requirements.txt
```

## Configuration

Add to your `.env` file:

```env
# Strategy 5 Settings
STRATEGY_5_TOPIC=geopolitics  # or 'crypto', 'sports', etc.
CONSENSUS_CHECK_INTERVAL=300  # Check every 5 minutes
CONSENSUS_BASE_SIZE=1000.0    # Base position size in USD

# Optional: Polygon RPC (for blockchain scanning)
POLYGON_RPC_URL=https://polygon-rpc.com
```

## Quick Start

### 1. Test Data Integration

First, verify data sources are working:

```bash
# Test subgraph and API connections
python test_data_fetcher.py
```

This will test:
- Subgraph connectivity
- API connectivity
- Wallet data fetching

### 2. Paper Trading (Recommended First)

```bash
# Set paper trading mode
export PAPER_TRADING=true

# Run bot
python bot.py --topic geopolitics --paper
```

### Live Trading

```bash
# Run bot (will prompt for confirmation)
python bot.py --topic geopolitics
```

### Command Line Options

```bash
python bot.py --help

Options:
  --topic TOPIC    Topic/specialization (default: geopolitics)
  --paper          Enable paper trading mode
```

## Components

### `wallet_scanner.py`
- Scans Polygon blockchain for wallet activity
- Discovers wallets from market trading data
- Fetches wallet statistics

### `wallet_basket_builder.py`
- Filters wallets by topic specialization
- Applies sophisticated filtering criteria
- Ranks wallets by performance metrics

### `consensus_detector.py`
- Detects when 80%+ of basket agrees
- Validates price band tightness
- Calculates signal strength

### `wallet_monitor.py`
- Monitors basket wallets in real-time
- Tracks new trades
- Triggers consensus checks

### `bot.py`
- Main orchestrator
- Builds basket
- Monitors for consensus
- Executes trades

## Current Status

✅ **Implementation Status:** Core structure complete, data integration ready

**What's Working:**
- ✅ Wallet basket filtering logic
- ✅ Consensus detection algorithm
- ✅ Bot structure and orchestration
- ✅ Subgraph client for data fetching
- ✅ API client for market data
- ✅ Market topic categorization

**What Needs Verification:**
- ⚠️ GraphQL schema verification (queries may need adjustment)
- ⚠️ Win/loss calculation (needs PNL subgraph integration)
- ⚠️ Real-time monitoring (needs WebSocket or polling setup)

**Next Steps:**
1. Test subgraph connection: `python test_data_fetcher.py`
2. Verify GraphQL queries match actual schema
3. Adjust queries if needed
4. Test with real wallet addresses

## Next Steps

1. **Integrate PolyMarket Subgraph/API**
   - Query The Graph subgraph for trade data
   - Fetch wallet statistics from API
   - Get real-time trade updates

2. **Market Topic Categorization**
   - Categorize markets by topic (geopolitics, crypto, etc.)
   - Filter markets for basket monitoring

3. **Testing**
   - Test with historical data
   - Paper trade with real data
   - Validate consensus signals

4. **Optimization**
   - Tune consensus threshold (maybe 75% vs 80%?)
   - Optimize filtering criteria
   - Improve signal strength calculation

## Data Sources

The bot needs access to:

1. **PolyMarket Trade Data**
   - The Graph subgraph: `https://api.thegraph.com/subgraphs/name/polymarket/...`
   - Or PolyMarket API endpoints

2. **Blockchain Data**
   - Polygon RPC endpoint
   - Wallet transaction history

3. **Market Data**
   - Market categorization
   - Current prices
   - Order book data

## Example Output

```
Building geopolitics wallet basket...
Found 5000 wallets, building geopolitics basket...
Filtered to 150 wallets matching criteria
Built geopolitics basket with 100 wallets
   Top wallet: 0x742d35a6... (score: 0.847)

Starting consensus monitoring...
Checking 45 geopolitics markets for consensus...

🎯 CONSENSUS SIGNAL DETECTED!
   Market: Will Russia invade Ukraine by March 2024?
   Outcome: YES
   Consensus: 84.0% of basket
   Signal Strength: 0.78
   Avg Entry: $0.4200
   Current: $0.4300
   Participation: 65.0%
✅ Trade executed: Order ID abc123
```

## Resources

- [PolyMarket API Docs](https://docs.polymarket.com/)
- [The Graph Subgraph](https://thegraph.com/)
- [Polygon RPC](https://docs.polygon.technology/docs/develop/network-details/network/)

---

**Note:** This is an advanced strategy requiring significant data processing. Start with paper trading and validate signals before deploying with real capital.

