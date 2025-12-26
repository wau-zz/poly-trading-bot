# Quick Start Guide

## macOS Setup (Python 3)

On macOS, use `python3` and `pip3` instead of `python` and `pip`.

### 1. Verify Python 3 Installation

```bash
python3 --version
# Should show: Python 3.9.x or higher
```

If not installed:
```bash
# Install via Homebrew
brew install python3

# Or download from python.org
```

### 2. Install Dependencies

```bash
cd strategies/strategy_1_arbitrage/python
pip3 install -r requirements.txt
```

### 3. Test Connection

```bash
python3 test_connection.py
```

### 4. Run Bot (Paper Trading Mode)

```bash
# Make sure PAPER_TRADING=true in .env
python3 bot.py
```

### 5. Run Bot (Live Trading)

```bash
# Set PAPER_TRADING=false in .env
python3 bot.py
```

## Common Issues

### "command not found: python"
**Solution:** Use `python3` instead of `python`

### "command not found: pip"
**Solution:** Use `pip3` instead of `pip`

### "No module named 'py_clob_client'"
**Solution:**
```bash
pip3 install py-clob-client
```

### "Permission denied" when installing packages
**Solution:**
```bash
pip3 install --user -r requirements.txt
```

## All Commands (macOS)

```bash
# Install dependencies
pip3 install -r requirements.txt

# Test connection
python3 test_connection.py

# Run tests
python3 -m pytest tests/ -v

# Run bot (paper trading)
PAPER_TRADING=true python3 bot.py

# Run bot (live trading)
python3 bot.py
```

---

**Note:** All documentation has been updated to use `python3` and `pip3` for macOS compatibility.

