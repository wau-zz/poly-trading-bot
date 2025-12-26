# Strategy 1 Setup Guide

## Prerequisites

1. **Python 3.11+** installed
2. **PolyMarket account** with API keys
3. **USDC balance** in your PolyMarket wallet (minimum $100 recommended)

## Step-by-Step Setup

### 1. Install Dependencies

```bash
cd strategies/strategy_1_arbitrage/python
pip3 install -r requirements.txt
```

### 2. Get API Keys

1. Go to [PolyMarket Builder Settings](https://polymarket.com/settings?tab=builder)
2. Click "+ Create New" to generate:
   - `apiKey`
   - `secret`
   - `passphrase`

### 3. Configure Environment

Create a `.env` file in the **project root** (not in this folder):

```bash
# From project root
cd ../../..
nano .env
```

Add your credentials:

```env
POLYMARKET_API_KEY=your_api_key_here
POLYMARKET_API_SECRET=your_secret_here
POLYMARKET_PASSPHRASE=your_passphrase_here

# Optional: Strategy configuration
STRATEGY_1_MIN_PROFIT_MARGIN=0.01
STRATEGY_1_MAX_POSITION_SIZE=1000.0
ARBITRAGE_SCAN_INTERVAL=0.1
LOG_LEVEL=INFO
```

### 4. Test Connection

Before running the bot, test your API connection:

```bash
python3 test_connection.py
```

You should see:
```
✅ API Key found: ...
✅ Client initialized successfully
✅ Balance: $X,XXX.XX
✅ Found X active markets
✅ All tests passed!
```

### 5. Run the Bot

```bash
python3 bot.py
```

The bot will:
- Scan markets every 100ms
- Detect arbitrage opportunities
- Execute trades automatically
- Log all activity

### 6. Monitor

View logs in real-time:

```bash
tail -f ../../../logs/arbitrage_bot.log
```

## Important Notes

### API Method Adjustments

The `polymarket_client.py` has some placeholder methods that may need adjustment based on the actual `py-clob-client` API. You may need to:

1. Check [py-clob-client documentation](https://github.com/Polymarket/py-clob-client)
2. Adjust method names/parameters in `shared/python/polymarket_client.py`
3. Test with `test_connection.py` after changes

### Paper Trading First

Before using real money:

1. Comment out the `execute_arbitrage()` call in `bot.py`
2. Just log opportunities without executing
3. Run for 24-48 hours to see what opportunities appear
4. Then enable real trading

### Start Small

- Start with $500-1,000 capital
- Monitor for 1 week
- Scale up gradually as you gain confidence

## Troubleshooting

**"ModuleNotFoundError: No module named 'py_clob_client'"**
```bash
pip3 install py-clob-client
```

**"API credentials not found"**
- Make sure `.env` file is in project root
- Check variable names match exactly

**"No markets found"**
- Check internet connection
- Verify PolyMarket API is accessible
- May need to adjust `get_markets()` method

**"Insufficient balance"**
- Deposit USDC to your PolyMarket account
- Minimum $100 recommended

## Next Steps

1. ✅ Test connection
2. ✅ Paper trade (log only, no execution)
3. ✅ Deploy with small capital
4. ✅ Monitor and optimize
5. ✅ Scale up gradually

Good luck! 🚀

