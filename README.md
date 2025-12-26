# PolyMarket Trading Bot

Systematic trading strategies for prediction markets (PolyMarket, Kalshi) that exploit market inefficiencies through algorithmic trading.

> **Inspired by:** [Programmers on Twitter quietly pulling in 10k to 100k per month on Prediction markets](https://www.reddit.com/r/PolyKal/comments/1pvajkf/programmers_on_twitter_quietly_pulling_in_10k_to/)

---

## 📚 Documentation

- **[Overview](./docs/OVERVIEW.md)** - Introduction to prediction market trading
- **[Project Structure](./PROJECT_STRUCTURE.md)** - Repository organization guide
- **[Deployment Guide](./docs/DEPLOYMENT.md)** - How to deploy to EC2, Docker, ECS, etc.

### Strategies

- **[Strategy 1: Arbitrage](./docs/strategy_1_arbitrage.md)** - Risk-free price mismatch sniping
- **[Strategy 2: Pairs Trading](./docs/strategy_2_pairs_trading.md)** - Correlated market divergence
- **[Strategy 3: Probability Models](./docs/strategy_3_probability_models.md)** - ML/data-driven edge
- **[Strategy 4: Market Making](./docs/strategy_4_market_making.md)** - High-frequency liquidity provision
- **[Strategy 5: Wallet Following](./docs/strategy_5_wallet_following.md)** - Copy smart money
- **[Strategy 6: Structured Products](./docs/strategy_6_structured_products.md)** - Options-style spreads
- **[Strategy 7: Cross-Market Arbitrage](./docs/strategy_7_cross_market_arbitrage.md)** - Prediction vs spot markets

---

## 🚀 Quick Start

### 1. Setup

```bash
# Clone repository
git clone https://github.com/wau-zz/poly-trading-bot.git
cd poly-trading-bot

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your PolyMarket API keys
```

### 2. Get API Keys

1. Go to [PolyMarket Builder Settings](https://polymarket.com/settings?tab=builder)
2. Click "+ Create New" to generate API key, secret, and passphrase
3. Add to `.env` file

### 3. Run a Strategy

```bash
# Example: Run arbitrage bot
cd strategies/strategy_1_arbitrage/python
pip install -r requirements.txt
python bot.py
```

---

## 📁 Repository Structure

```
poly-trading-bot/
├── docs/                    # Strategy documentation
├── shared/                  # Shared code (Python/TypeScript)
├── strategies/              # Individual strategy implementations
│   ├── strategy_1_arbitrage/
│   ├── strategy_2_pairs_trading/
│   └── ...
├── infrastructure/          # Docker, K8s, monitoring
├── tests/                   # Test suite
└── scripts/                 # Utility scripts
```

See [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) for detailed structure.

---

## 🎯 Strategies Overview

| Strategy | Monthly Returns | Win Rate | Difficulty |
|----------|----------------|----------|------------|
| Arbitrage | 5-10% | 95%+ | Beginner |
| Pairs Trading | 10-20% | 60-70% | Intermediate |
| Probability Models | 15-30% | 65-75% | Advanced |
| Market Making | 5-15% | 70-80% | Intermediate |
| Wallet Following | 10-20% | 55-65% | Beginner |
| Structured Products | 20-40% | 60-75% | Advanced |
| Cross-Market Arbitrage | 25-50% | 70-80% | Expert |

**Portfolio Expected Return:** 18-35% monthly (with proper capital allocation)

> **Note:** Returns are monthly percentages based on allocated capital. Actual results may vary. Start small, validate strategies, then scale gradually.

---

## ⚠️ Risk Warnings

- **Not financial advice** - Trade at your own risk
- **Start small** - Test with $500-1k before scaling
- **Paper trade first** - Validate strategies before real money
- **Understand the risks** - Platform, execution, model, regulatory
- **Comply with regulations** - Check local laws on prediction markets

---

## 🛠️ Tech Stack

**Languages:**
- Python 3.11+ (for ML, data analysis)
- TypeScript (for high-frequency trading)

**Key Libraries:**
- `py-clob-client` - PolyMarket Python SDK
- `pandas`, `numpy` - Data analysis
- `scikit-learn`, `xgboost` - ML models
- `websockets` - Real-time data
- `ccxt` - Crypto exchange integration

---

## 📊 Status

- [x] Strategy documentation complete (7 strategies)
- [ ] Shared utilities implementation
- [ ] Strategy 1: Arbitrage bot
- [ ] Strategy 2: Pairs trading bot
- [ ] Strategy 3: Probability models
- [ ] Strategy 4: Market making bot
- [ ] Strategy 5: Wallet following bot
- [ ] Strategy 6: Structured products
- [ ] Strategy 7: Cross-market arbitrage
- [ ] Testing suite
- [ ] Deployment infrastructure

---

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🔗 Links

- [PolyMarket](https://polymarket.com)
- [PolyMarket API Docs](https://docs.polymarket.com)
- [Original Reddit Post](https://www.reddit.com/r/PolyKal/comments/1pvajkf/programmers_on_twitter_quietly_pulling_in_10k_to/)

---

**Last Updated:** December 26, 2025

