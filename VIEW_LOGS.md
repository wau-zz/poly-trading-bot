# How to View Test Output and Logs

## Log File Location

All bot output is saved to:
```
logs/bot.log
```

## View Logs

### 1. View Recent Logs (Last 50 lines)
```bash
tail -50 logs/bot.log
```

### 2. View All Logs
```bash
cat logs/bot.log
```

### 3. Watch Logs in Real-Time (Live Monitoring)
```bash
tail -f logs/bot.log
```
Press `Ctrl+C` to stop watching.

### 4. Search Logs for Specific Terms
```bash
# Find all errors
grep ERROR logs/bot.log

# Find all trades
grep "TRADE" logs/bot.log

# Find all opportunities
grep "opportunity" logs/bot.log
```

### 5. View Last N Lines
```bash
tail -n 100 logs/bot.log  # Last 100 lines
```

## Test Output Locations

### Connection Test Output
When you run:
```bash
python strategies/strategy_1_arbitrage/python/test_connection.py
```

The output goes to **terminal/stdout** (not a log file). You'll see:
```
✅ API Key found: ...
✅ Client initialized successfully
✅ Balance: $1,000.00
✅ Found 936 active markets
✅ All tests passed!
```

### Bot Test Output
When you run:
```bash
python strategies/strategy_1_arbitrage/python/bot.py
```

The output goes to:
1. **Terminal** (stdout) - Real-time output
2. **logs/bot.log** - Saved log file

### Unit Test Output
When you run:
```bash
pytest tests/ -v
```

The output goes to **terminal/stdout**. You'll see:
```
test_arbitrage_detector.py::TestArbitrageDetector::test_profitable_arbitrage PASSED
test_arbitrage_detector.py::TestArbitrageDetector::test_no_arbitrage PASSED
...
```

## View Logs in Your IDE

### VS Code / Cursor
1. Open `logs/bot.log` in the editor
2. The file will auto-update as the bot runs
3. Or use the integrated terminal: `tail -f logs/bot.log`

### PyCharm
1. Right-click `logs/bot.log`
2. Select "Open in Editor"
3. Or use terminal: `tail -f logs/bot.log`

## Log File Format

Each log entry includes:
```
TIMESTAMP - MODULE - LEVEL - MESSAGE
```

Example:
```
2025-12-26 02:29:46,701 - __main__ - INFO - Bot initialized successfully
2025-12-26 02:29:46,701 - __main__ - INFO - Starting arbitrage scan loop...
```

## Log Levels

- **INFO**: Normal operation
- **WARNING**: Something to be aware of
- **ERROR**: Something went wrong
- **DEBUG**: Detailed debugging info (if enabled)

## Enable Debug Logging

To see more detailed output, set in `.env`:
```env
LOG_LEVEL=DEBUG
```

## Clear Logs

```bash
# Clear the log file
> logs/bot.log

# Or delete and recreate
rm logs/bot.log
touch logs/bot.log
```

---

**Quick Reference:**
- **View logs**: `tail -f logs/bot.log`
- **Search logs**: `grep "keyword" logs/bot.log`
- **Last 50 lines**: `tail -50 logs/bot.log`

