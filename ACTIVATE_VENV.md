# Using the Virtual Environment

Python 3.12.12 has been installed and a virtual environment has been created.

## Quick Start

### Activate the Virtual Environment

```bash
# From project root
source venv/bin/activate
```

You'll see `(venv)` in your terminal prompt when activated.

### Run Commands

Once activated, use `python` (not `python3`):

```bash
# Test connection
python strategies/strategy_1_arbitrage/python/test_connection.py

# Run bot
python strategies/strategy_1_arbitrage/python/bot.py

# Run tests
python -m pytest tests/ -v
```

### Deactivate

When done:
```bash
deactivate
```

## What's Installed

- **Python 3.12.12** (latest stable)
- All project dependencies in isolated environment
- No conflicts with system Python

## Why Virtual Environment?

- ✅ Isolated dependencies (won't affect system Python)
- ✅ Reproducible environment
- ✅ Easy to recreate on other machines
- ✅ Best practice for Python projects

## Quick Reference

```bash
# Activate
source venv/bin/activate

# Verify Python version
python --version  # Should show: Python 3.12.12

# Run bot (paper trading)
python strategies/strategy_1_arbitrage/python/bot.py

# Deactivate when done
deactivate
```

---

**Note:** Always activate the virtual environment before running the bot!

