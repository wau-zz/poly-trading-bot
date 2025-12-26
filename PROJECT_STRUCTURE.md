# Project Structure Guide

This document outlines the recommended repository structure for implementing PolyMarket trading strategies.

---

## Recommended Structure

```
poly-trading-bot/
│
├── docs/                          # Documentation
│   ├── OVERVIEW.md
│   ├── strategy_1_arbitrage.md
│   ├── strategy_2_pairs_trading.md
│   ├── strategy_3_probability_models.md
│   ├── strategy_4_market_making.md
│   ├── strategy_5_wallet_following.md
│   ├── strategy_6_structured_products.md
│   ├── strategy_7_cross_market_arbitrage.md
│   └── PROJECT_STRUCTURE.md       # This file
│
├── shared/                        # Shared code across strategies
│   ├── python/
│   │   ├── __init__.py
│   │   ├── polymarket_client.py   # PolyMarket API wrapper
│   │   ├── data_collector.py      # Market data fetching
│   │   ├── order_executor.py      # Order placement/cancellation
│   │   ├── risk_manager.py        # Risk management utilities
│   │   ├── database.py            # Database connections
│   │   └── utils.py               # Common utilities
│   │
│   ├── typescript/
│   │   ├── src/
│   │   │   ├── polymarket-client.ts
│   │   │   ├── data-collector.ts
│   │   │   ├── order-executor.ts
│   │   │   ├── risk-manager.ts
│   │   │   └── utils.ts
│   │   └── package.json
│   │
│   └── config/                    # Shared configuration
│       ├── config.example.yaml
│       └── markets.yaml            # Market definitions
│
├── strategies/                    # Individual strategy implementations
│   ├── strategy_1_arbitrage/
│   │   ├── python/
│   │   │   ├── __init__.py
│   │   │   ├── detector.py        # Arbitrage detection
│   │   │   ├── executor.py         # Execution logic
│   │   │   ├── bot.py             # Main bot class
│   │   │   └── requirements.txt
│   │   │
│   │   ├── typescript/
│   │   │   ├── src/
│   │   │   │   ├── detector.ts
│   │   │   │   ├── executor.ts
│   │   │   │   └── bot.ts
│   │   │   └── package.json
│   │   │
│   │   └── README.md              # Strategy-specific docs
│   │
│   ├── strategy_2_pairs_trading/
│   │   ├── python/
│   │   │   ├── __init__.py
│   │   │   ├── pair_finder.py
│   │   │   ├── spread_analyzer.py
│   │   │   ├── bot.py
│   │   │   └── requirements.txt
│   │   │
│   │   └── README.md
│   │
│   ├── strategy_3_probability_models/
│   │   ├── python/
│   │   │   ├── __init__.py
│   │   │   ├── models/
│   │   │   │   ├── news_model.py
│   │   │   │   ├── polling_model.py
│   │   │   │   ├── sentiment_model.py
│   │   │   │   └── ensemble.py
│   │   │   ├── data_sources/
│   │   │   │   ├── news_api.py
│   │   │   │   ├── twitter_api.py
│   │   │   │   └── polling_api.py
│   │   │   ├── bot.py
│   │   │   └── requirements.txt
│   │   │
│   │   └── README.md
│   │
│   ├── strategy_4_market_making/
│   │   ├── python/
│   │   │   ├── __init__.py
│   │   │   ├── market_maker.py
│   │   │   ├── quote_calculator.py
│   │   │   ├── inventory_manager.py
│   │   │   ├── bot.py
│   │   │   └── requirements.txt
│   │   │
│   │   └── README.md
│   │
│   ├── strategy_5_wallet_following/
│   │   ├── python/
│   │   │   ├── __init__.py
│   │   │   ├── wallet_scanner.py
│   │   │   ├── wallet_monitor.py
│   │   │   ├── copy_trader.py
│   │   │   ├── bot.py
│   │   │   └── requirements.txt
│   │   │
│   │   └── README.md
│   │
│   ├── strategy_6_structured_products/
│   │   ├── python/
│   │   │   ├── __init__.py
│   │   │   ├── spread_trader.py
│   │   │   ├── straddle_trader.py
│   │   │   ├── arbitrage_finder.py
│   │   │   ├── bot.py
│   │   │   └── requirements.txt
│   │   │
│   │   └── README.md
│   │
│   └── strategy_7_cross_market_arbitrage/
│       ├── python/
│       │   ├── __init__.py
│       │   ├── fair_value_calculator.py
│       │   ├── volatility_estimator.py
│       │   ├── hedge_manager.py
│       │   ├── bot.py
│       │   └── requirements.txt
│       │
│       └── README.md
│
├── infrastructure/               # Deployment & infrastructure
│   ├── docker/
│   │   ├── Dockerfile.python
│   │   ├── Dockerfile.typescript
│   │   └── docker-compose.yml
│   │
│   ├── kubernetes/               # If using K8s
│   │   └── deployments/
│   │
│   └── monitoring/
│       ├── prometheus/
│       └── grafana/
│
├── tests/                        # Tests
│   ├── shared/
│   ├── strategies/
│   │   ├── test_strategy_1.py
│   │   └── ...
│   └── integration/
│
├── scripts/                      # Utility scripts
│   ├── setup.sh
│   ├── deploy.sh
│   └── backtest.py
│
├── data/                        # Data storage (gitignored)
│   ├── historical/
│   ├── logs/
│   └── models/
│
├── .env.example                 # Environment variable template
├── .gitignore
├── README.md                    # Main project README
├── requirements.txt             # Root Python requirements (shared)
├── package.json                 # Root TypeScript package (shared)
└── pyproject.toml              # Python project config
```

---

## Design Principles

### 1. **Separation of Concerns**
- **Shared code** in `shared/` - reusable across all strategies
- **Strategy-specific** code in `strategies/strategy_X/`
- **Documentation** in `docs/` - separate from implementation

### 2. **Language Flexibility**
- Each strategy can have **both Python and TypeScript** implementations
- Or choose **one language per strategy** based on needs
- Shared utilities available in both languages

### 3. **Modularity**
- Each strategy is **self-contained** with its own dependencies
- Can run strategies **independently** or together
- Easy to **add/remove** strategies

### 4. **Scalability**
- Structure supports **multiple bots** running simultaneously
- Easy to **scale horizontally** (Docker, K8s)
- **Monitoring** and **logging** built-in

---

## Implementation Examples

### Example 1: Python-Only Strategy

```
strategies/strategy_1_arbitrage/
├── python/
│   ├── bot.py
│   ├── detector.py
│   └── requirements.txt
└── README.md
```

**Usage:**
```bash
cd strategies/strategy_1_arbitrage/python
pip install -r requirements.txt
python bot.py
```

### Example 2: TypeScript-Only Strategy

```
strategies/strategy_4_market_making/
├── typescript/
│   ├── src/
│   │   └── bot.ts
│   └── package.json
└── README.md
```

**Usage:**
```bash
cd strategies/strategy_4_market_making/typescript
npm install
npm run start
```

### Example 3: Both Languages

```
strategies/strategy_1_arbitrage/
├── python/
│   └── ...
├── typescript/
│   └── ...
└── README.md
```

**Choose based on:**
- Speed requirements (TypeScript for HFT)
- ML needs (Python for models)
- Team preference

---

## Shared Code Structure

### Python Shared Module

```python
# shared/python/polymarket_client.py
from py_clob_client.client import ClobClient
import os

class PolyMarketClient:
    def __init__(self):
        self.client = ClobClient(
            host="https://clob.polymarket.com",
            key=os.getenv("POLYMARKET_API_KEY"),
            secret=os.getenv("POLYMARKET_API_SECRET"),
            chain_id=137
        )
    
    def get_market(self, market_id):
        # Implementation
        pass
    
    def place_order(self, market_id, side, price, size):
        # Implementation
        pass
```

### Strategy Usage

```python
# strategies/strategy_1_arbitrage/python/bot.py
import sys
sys.path.append('../../../shared/python')

from polymarket_client import PolyMarketClient
from detector import ArbitrageDetector

class ArbitrageBot:
    def __init__(self):
        self.client = PolyMarketClient()
        self.detector = ArbitrageDetector(self.client)
```

---

## Configuration Management

### Environment Variables

```bash
# .env.example
POLYMARKET_API_KEY=your_key_here
POLYMARKET_API_SECRET=your_secret_here
POLYMARKET_PASSPHRASE=your_passphrase_here

# Strategy-specific
STRATEGY_1_ENABLED=true
STRATEGY_1_CAPITAL=10000
STRATEGY_1_MIN_PROFIT=0.01

STRATEGY_2_ENABLED=false
STRATEGY_2_CAPITAL=0
```

### YAML Config (Optional)

```yaml
# shared/config/config.yaml
strategies:
  strategy_1_arbitrage:
    enabled: true
    capital: 10000
    min_profit_margin: 0.01
    max_positions: 5
  
  strategy_2_pairs_trading:
    enabled: true
    capital: 15000
    min_z_score: 2.0
    max_pairs: 10
```

---

## Running Multiple Strategies

### Option 1: Separate Processes

```bash
# Terminal 1
cd strategies/strategy_1_arbitrage/python
python bot.py

# Terminal 2
cd strategies/strategy_2_pairs_trading/python
python bot.py
```

### Option 2: Orchestrator

```python
# scripts/orchestrator.py
import asyncio
from strategies.strategy_1_arbitrage.python.bot import ArbitrageBot
from strategies.strategy_2_pairs_trading.python.bot import PairsBot

async def main():
    bots = [
        ArbitrageBot(),
        PairsBot(),
    ]
    
    await asyncio.gather(*[bot.run() for bot in bots])

if __name__ == "__main__":
    asyncio.run(main())
```

### Option 3: Docker Compose

```yaml
# infrastructure/docker/docker-compose.yml
version: '3.8'

services:
  arbitrage-bot:
    build: ./strategies/strategy_1_arbitrage/python
    environment:
      - STRATEGY_1_ENABLED=true
    
  pairs-bot:
    build: ./strategies/strategy_2_pairs_trading/python
    environment:
      - STRATEGY_2_ENABLED=true
```

---

## Testing Structure

```
tests/
├── shared/
│   ├── test_polymarket_client.py
│   └── test_risk_manager.py
│
├── strategies/
│   ├── strategy_1_arbitrage/
│   │   ├── test_detector.py
│   │   └── test_executor.py
│   └── ...
│
└── integration/
    ├── test_multiple_strategies.py
    └── test_end_to_end.py
```

---

## Deployment Structure

### Development
```bash
# Run locally
python strategies/strategy_1_arbitrage/python/bot.py
```

### Production
```bash
# Docker
docker-compose up -d

# Or Kubernetes
kubectl apply -f infrastructure/kubernetes/
```

---

## Recommended Approach

### **Start Simple:**

1. **Phase 1:** Implement 1-2 strategies in Python
   ```
   strategies/
   ├── strategy_1_arbitrage/
   │   └── python/
   └── strategy_2_pairs_trading/
       └── python/
   ```

2. **Phase 2:** Add shared utilities
   ```
   shared/
   └── python/
       ├── polymarket_client.py
       └── utils.py
   ```

3. **Phase 3:** Add more strategies as needed
   ```
   strategies/
   ├── strategy_1_arbitrage/
   ├── strategy_2_pairs_trading/
   ├── strategy_3_probability_models/
   └── ...
   ```

4. **Phase 4:** Add TypeScript for speed-critical strategies
   ```
   strategies/
   ├── strategy_1_arbitrage/
   │   ├── python/  # For analysis
   │   └── typescript/  # For execution
   ```

---

## Quick Start Commands

```bash
# Setup
git clone <repo>
cd poly-trading-bot
cp .env.example .env
# Edit .env with your API keys

# Install shared dependencies
pip install -r requirements.txt

# Run a strategy
cd strategies/strategy_1_arbitrage/python
pip install -r requirements.txt
python bot.py

# Run all strategies
python scripts/orchestrator.py
```

---

## Benefits of This Structure

✅ **Modular** - Each strategy is independent  
✅ **Reusable** - Shared code prevents duplication  
✅ **Flexible** - Choose language per strategy  
✅ **Scalable** - Easy to add new strategies  
✅ **Testable** - Clear separation for testing  
✅ **Deployable** - Ready for Docker/K8s  
✅ **Maintainable** - Easy to find and update code  

---

*This structure can evolve as your needs grow. Start simple, add complexity as needed.*

