# Environment Variables Setup Guide

## Quick Setup

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your actual credentials:
```bash
nano .env
```

## Required Variables

### PolyMarket API Credentials

You can use **either** naming convention:

**Option 1 (Recommended):**
```env
POLYMARKET_API_KEY=your_api_key_here
POLYMARKET_API_SECRET=your_secret_here
POLYMARKET_PASSPHRASE=your_passphrase_here
```

**Option 2 (PolyMarket's exact names):**
```env
apiKey=your_api_key_here
secret=your_secret_here
passphrase=your_passphrase_here
```

Both work! The code supports both naming conventions.

## About Passphrase

**Is passphrase required?**

- **Optional but recommended** - If PolyMarket generated a passphrase for you, include it
- The code will work without it (uses empty string if not provided)
- Some API operations may require it for security
- **Best practice:** Include it if you have it

## Your Credentials

Based on what you provided, your `.env` file should look like:

```env
# Option 1: Use descriptive names
POLYMARKET_API_KEY=019b59f6-4088-7f3f-b1b5-960f1400a6d3
POLYMARKET_API_SECRET=JAfWT402Ym4kFFO20Re0gZn9vrH7y4SRQTaxxX5Mfvg=
POLYMARKET_PASSPHRASE=your_passphrase_if_you_have_one

# OR Option 2: Use PolyMarket's exact names
apiKey=019b59f6-4088-7f3f-b1b5-960f1400a6d3
secret=JAfWT402Ym4kFFO20Re0gZn9vrH7y4SRQTaxxX5Mfvg=
passphrase=your_passphrase_if_you_have_one
```

## Security Notes

⚠️ **IMPORTANT:**
- Never commit your `.env` file to git (it's in .gitignore)
- Never share your API keys publicly
- If keys are compromised, revoke them immediately in PolyMarket settings
- Use `.env.example` as a template (it has no real credentials)

## Testing

After setting up your `.env` file, test the connection:

```bash
cd strategies/strategy_1_arbitrage/python
python test_connection.py
```

This will verify your credentials work correctly.

