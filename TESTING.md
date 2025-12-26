# Testing Guide

This guide covers all testing approaches for the PolyMarket trading bot, from paper trading to unit tests to backtesting.

---

## Testing Strategy Overview

```
Development → Paper Trading → Unit Tests → Integration Tests → Backtesting → Production
```

---

## 1. Paper Trading (Recommended First Step)

**Paper trading** simulates trades without using real money. Perfect for validating your strategy before risking capital.

### Enable Paper Trading

**Option 1: Environment Variable**
```bash
# In your .env file
PAPER_TRADING=true
PAPER_TRADING_BALANCE=10000.0  # Starting balance for simulation
```

**Option 2: Command Line**
```python
# In bot.py, change:
bot = ArbitrageBot(paper_trading=True)
```

### Run Paper Trading

```bash
cd strategies/strategy_1_arbitrage/python
python bot.py
```

You'll see:
```
🧪 PAPER TRADING MODE - No real trades will be executed
📝 PAPER TRADE: BUY 100.00 shares @ $0.5200 = $52.00
```

### What Paper Trading Does

✅ **Simulates:**
- Order placement
- Balance tracking
- Position management
- Profit/loss calculation

❌ **Does NOT:**
- Make real API calls to PolyMarket
- Execute real trades
- Risk real money

### Paper Trading Features

- **Real-time simulation** - Uses actual market data
- **Balance tracking** - Tracks simulated balance
- **Trade logging** - Logs all simulated trades
- **Statistics** - Shows ROI, win rate, etc.

---

## 2. Unit Tests

Test individual components in isolation.

### Run Unit Tests

```bash
# From project root
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_arbitrage_detector.py

# Run with verbose output
python -m pytest tests/ -v
```

### Test Coverage

```bash
# Install coverage tool
pip install pytest-cov

# Run tests with coverage
pytest --cov=strategies/strategy_1_arbitrage/python --cov=shared/python tests/
```

### What's Tested

- ✅ Arbitrage detection logic
- ✅ Profit margin calculations
- ✅ Position sizing
- ✅ Order execution (simulated)
- ✅ Error handling

---

## 3. Integration Tests

Test the complete workflow end-to-end.

### Run Integration Tests

```bash
python -m pytest tests/test_integration.py -v
```

### What's Tested

- ✅ Bot initialization
- ✅ Detection → Execution flow
- ✅ Paper trading workflow
- ✅ Error recovery

---

## 4. Backtesting

Test your strategy against historical market data.

### Create Backtest Script

```python
# tests/backtest_strategy1.py
import sys
import os
from datetime import datetime, timedelta

sys.path.append('shared/python')
sys.path.append('strategies/strategy_1_arbitrage/python')

from paper_trading import PaperTradingClient
from detector import ArbitrageDetector
from executor import ArbitrageExecutor

def backtest_arbitrage(historical_data):
    """
    Backtest arbitrage strategy on historical data
    
    Args:
        historical_data: List of historical market snapshots
    """
    client = PaperTradingClient(initial_balance=10000.0)
    detector = ArbitrageDetector(client=client, min_profit_pct=0.01)
    executor = ArbitrageExecutor(client=client, max_position_size=1000.0)
    
    opportunities_found = 0
    trades_executed = 0
    total_profit = 0.0
    
    for market_snapshot in historical_data:
        # Check for arbitrage
        opportunity = detector.detect_arbitrage(market_snapshot)
        
        if opportunity:
            opportunities_found += 1
            
            # Execute trade
            result = executor.execute_arbitrage(opportunity)
            if result:
                trades_executed += 1
                total_profit += result['expected_profit']
    
    # Print results
    print(f"Backtest Results:")
    print(f"  Opportunities found: {opportunities_found}")
    print(f"  Trades executed: {trades_executed}")
    print(f"  Total profit: ${total_profit:,.2f}")
    print(f"  ROI: {(total_profit / 10000.0) * 100:.2f}%")
    
    return {
        'opportunities': opportunities_found,
        'trades': trades_executed,
        'profit': total_profit,
        'roi': (total_profit / 10000.0) * 100
    }
```

### Run Backtest

```bash
python tests/backtest_strategy1.py
```

---

## 5. Manual Testing Checklist

Before deploying to production, manually test:

- [ ] **API Connection**
  ```bash
  python strategies/strategy_1_arbitrage/python/test_connection.py
  ```

- [ ] **Paper Trading (24 hours)**
  - Run bot in paper trading mode
  - Monitor for 24-48 hours
  - Verify detection logic works
  - Check that no real trades execute

- [ ] **Small Capital Test ($100-500)**
  - Deploy with minimal capital
  - Run for 1 week
  - Monitor all trades
  - Verify profit calculations

- [ ] **Error Handling**
  - Test with invalid API keys
  - Test with insufficient balance
  - Test with network disconnection
  - Verify graceful recovery

- [ ] **Logging**
  - Verify all trades are logged
  - Check log file rotation
  - Confirm statistics are accurate

---

## 6. Production Deployment Testing

### Pre-Production Checklist

- [ ] Paper trading successful for 48+ hours
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Manual testing complete
- [ ] Logging and monitoring set up
- [ ] Error alerts configured
- [ ] Backup/restore procedures tested

### Gradual Rollout

1. **Week 1:** Paper trading only
2. **Week 2:** $100-500 real capital
3. **Week 3:** $500-1,000 capital
4. **Week 4+:** Scale up gradually

---

## 7. Continuous Testing

### Automated Testing

Set up CI/CD to run tests automatically:

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest tests/
```

### Daily Monitoring

- Check logs daily
- Verify trades executed correctly
- Monitor balance changes
- Review statistics

---

## Testing Best Practices

### 1. **Always Paper Trade First**
Never deploy a new strategy without paper trading for at least 24-48 hours.

### 2. **Start Small**
Begin with $100-500, not your full capital.

### 3. **Test Edge Cases**
- What happens if API is down?
- What if balance runs out?
- What if market resolves unexpectedly?

### 4. **Monitor Closely**
Watch the bot for the first week, don't just set and forget.

### 5. **Keep Logs**
Save all logs for analysis and debugging.

---

## Quick Test Commands

```bash
# Test API connection
python strategies/strategy_1_arbitrage/python/test_connection.py

# Run unit tests
pytest tests/test_arbitrage_detector.py -v

# Run all tests
pytest tests/ -v

# Paper trading mode
PAPER_TRADING=true python strategies/strategy_1_arbitrage/python/bot.py

# Live trading (after testing)
python strategies/strategy_1_arbitrage/python/bot.py
```

---

## Troubleshooting Tests

**Tests fail with import errors:**
```bash
# Make sure you're in the project root
cd /path/to/poly-trading-bot
export PYTHONPATH=$PWD:$PYTHONPATH
pytest tests/
```

**Paper trading not working:**
- Check `PAPER_TRADING=true` in `.env`
- Verify paper_trading.py is in the correct location

**Can't connect to API:**
- Verify API keys in `.env`
- Check internet connection
- Test with `test_connection.py`

---

**Remember: Test thoroughly before risking real money!** 🧪💰

