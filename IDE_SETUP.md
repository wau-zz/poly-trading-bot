# IDE Setup Guide

If you're seeing import errors like:
- `Import "py_clob_client.client" could not be resolved`
- `Import "polymarket_client" could not be resolved`

This is an IDE configuration issue, not a code problem. The code runs fine - your IDE just needs to know where to find things.

## Quick Fix

### For VS Code / Cursor:

1. **Select the correct Python interpreter:**
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Type: `Python: Select Interpreter`
   - Choose: `./venv/bin/python` (the virtual environment)

2. **Reload the window:**
   - Press `Cmd+Shift+P` / `Ctrl+Shift+P`
   - Type: `Developer: Reload Window`

3. **The `.vscode/settings.json` file is already configured** with:
   - Correct Python interpreter path
   - Extra import paths
   - Type checking settings

### For PyCharm:

1. Go to `File` → `Settings` → `Project` → `Python Interpreter`
2. Select: `./venv/bin/python`
3. Click `Apply`

### For Other IDEs:

Make sure your IDE is using the virtual environment's Python interpreter:
```bash
# Path to use:
/Users/willau/Documents/GitHub/poly-trading-bot/venv/bin/python
```

## Verify It's Working

After selecting the interpreter, the import errors should disappear. If they don't:

1. **Restart your IDE**
2. **Check the Python interpreter** is set to `venv/bin/python`
3. **Verify the project is installed** (we installed it with `pip install -e .`)

## Why This Happens

- Your IDE's Python language server needs to know which Python to use
- It needs to know where your packages are installed
- The virtual environment has all the packages, but the IDE wasn't looking there

## Test It Works

Run this in your IDE's terminal:
```bash
source venv/bin/activate
python -c "from py_clob_client.client import ClobClient; print('✅ Import works!')"
```

If that works, your IDE should also recognize the imports after selecting the correct interpreter.

---

**Note:** The code runs fine from the command line - this is purely an IDE display issue. Your bot works correctly! 🚀

