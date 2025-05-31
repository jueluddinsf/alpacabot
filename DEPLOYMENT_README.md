# 🚀 AlpacaBot Deployment Guide

## Quick Deploy to Replit

### 1. Create Replit Account
- Go to [replit.com](https://replit.com) and create an account
- Click "Create Repl" → "Import from GitHub"

### 2. Upload Code
Upload all the following files to your Repl:
```
alpacaBot/
├── main.py                  # Main entry point
├── config.py               # Configuration
├── trading_bot.py          # Core trading logic
├── cache_manager.py        # Caching system
├── dashboard.py            # Web dashboard
├── requirements.txt        # Dependencies
├── .replit                # Replit config
├── replit.nix             # Nix environment
├── templates/             # HTML templates
│   └── dashboard.html
└── data/                  # Data directory (auto-created)
```

### 3. Set Environment Variables (Secrets)
In Replit, go to **Tools → Secrets** and add:

**Required for Live Trading:**
```
APCA_API_KEY_ID = "your_alpaca_api_key"
APCA_API_SECRET_KEY = "your_alpaca_secret_key"
PAPER_TRADING = "True"  # Set to "False" for live trading
```

**Optional Configuration:**
```
MIN_STOCK_PRICE = "50.0"
DROP_THRESHOLD = "0.30"
PROFIT_TARGET = "0.10"
ENABLE_CACHING = "True"
FLASK_PORT = "5000"
```

### 4. Install Dependencies
Run in the Replit console:
```bash
pip install -r requirements.txt
```

### 5. Start the Bot
Click the **Run** button or execute:
```bash
python3 main.py
```

### 6. Access Dashboard
- The web dashboard will be available in the Replit web viewer
- URL format: `https://your-repl-name.your-username.repl.co`

## 🎯 Strategy Configuration

The bot implements a "buy the dip" strategy:

| Parameter | Default | Description |
|-----------|---------|-------------|
| **Stock Universe** | S&P 500 | Monitors 290+ major stocks |
| **Price Filter** | $5+ | Avoids penny stocks, includes quality companies |
| **Drop Threshold** | 30% | Adds to watchlist on 30%+ drop |
| **Entry Analysis** | Multi-factor | Smart entry timing |
| **Position Size** | 1 share | Buys 1 share per stock |
| **Profit Target** | 10% | Sells at 10% profit |
| **Lookback Period** | 7 days | Analyzes 1 week of data |

## ⚙️ Configuration Options

### Trading Parameters
```python
# In config.py or environment variables
MIN_STOCK_PRICE = 5.0       # Minimum stock price to avoid penny stocks
DROP_THRESHOLD = 0.30       # 30% drop to add to watchlist  
PROFIT_TARGET = 0.10        # 10% profit target
LOOKBACK_DAYS = 7           # Days to analyze for drops
```

### Cache Settings
```python
ENABLE_CACHING = True       # Enable/disable caching
CACHE_PRICE_EXPIRY = 300    # Price cache: 5 minutes
CACHE_HISTORY_EXPIRY = 3600 # History cache: 1 hour
CACHE_FILTER_EXPIRY = 1800  # Filter cache: 30 minutes
```

### Safety Features
```python
PAPER_TRADING = True        # Paper trading mode (recommended)
```

## 📊 Dashboard Features

The web dashboard provides:

- **📈 Portfolio Overview**: Current value, P&L, holdings count
- **👁️ Watchlist Monitoring**: Stocks being watched for entry
- **💼 Holdings Management**: Current positions and performance  
- **📜 Trade History**: Complete transaction log
- **🗄️ Cache Statistics**: Performance and memory usage
- **🔄 Manual Controls**: Trigger trading cycles manually

## 🔧 Operational Modes

### 1. Dashboard Mode (Recommended)
```bash
python3 main.py
```
- Runs web interface
- Manual trading cycle execution
- Real-time monitoring
- Perfect for Replit

### 2. Single Cycle Mode
```bash
python3 run_bot.py single
```
- Runs one trading cycle
- Good for testing
- Shows immediate results

### 3. Continuous Mode
```bash
python3 run_bot.py continuous
```
- Runs trading cycles every 5 minutes
- Fully automated
- Requires stable hosting

## 🛡️ Safety & Risk Management

### Paper Trading (Recommended)
- Set `PAPER_TRADING = True`
- No real money at risk
- Full functionality testing
- Perfect for learning

### Position Sizing
- Fixed 1 share per stock
- Low capital requirements
- Controlled risk exposure

### Entry Analysis
The bot uses sophisticated entry criteria:
- Price stabilization detection
- Volume analysis
- Recent low avoidance
- Multi-factor scoring

## 📈 Performance Optimization

### Caching System
- **Price Cache**: 5-minute expiry (market open) / 1-hour (closed)
- **History Cache**: 1-hour expiry (market open) / 12-hour (closed)
- **Filter Cache**: 30-minute expiry (market open) / 6-hour (closed)
- **Speed Improvement**: Up to 400x faster repeated operations

### Market-Aware Optimization
- Longer cache times when market is closed
- Reduced API calls during off-hours
- Smart resource management

## 🔍 Monitoring & Debugging

### Log Messages
```
🚀 Alpaca clients initialized (Paper Trading: True)
💰 Filtering 290 stocks above $50.0...
🔻 AAPL DROP DETECTED: 32.1% from high $180.00 to $122.18
📈 AAPL ENTRY SIGNAL: Entry signals: price_stabilizing, decent_volume
✅ BOUGHT AAPL at $122.50 - Entry signals: price_stabilizing, decent_volume
💰 SOLD AAPL for $12.25 profit (10.0%)
```

### Dashboard Monitoring
- Real-time portfolio updates
- Cache performance metrics
- API call success rates
- Error tracking

## 🚨 Troubleshooting

### Common Issues

**1. Alpaca API Errors**
```
Solution: Check API credentials in Replit Secrets
Verify: APCA_API_KEY_ID and APCA_API_SECRET_KEY
```

**2. No Stocks Found**
```
Solution: Lower DROP_THRESHOLD temporarily for testing
Current market may not have 30%+ drops
```

**3. Dashboard Not Loading**
```
Solution: Check Replit port configuration
Ensure .replit file has correct port settings
```

**4. Cache Issues**
```
Solution: Clear cache or disable temporarily
Set ENABLE_CACHING = False for debugging
```

### Testing Commands
```bash
# Test system components
python3 system_test.py

# Test cache performance  
python3 test_cache_performance.py

# Quick market scan
python3 quick_scan.py

# Single trading cycle
python3 run_bot.py single
```

## 📋 Pre-Deployment Checklist

- [ ] All files uploaded to Replit
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Environment variables set in Replit Secrets
- [ ] Paper trading mode enabled (`PAPER_TRADING = True`)
- [ ] System test passed (`python3 system_test.py`)
- [ ] Dashboard accessible via Replit web viewer
- [ ] API credentials working (if using live data)

## 🎉 Success Metrics

When properly deployed, you should see:
- ✅ 100% system test pass rate
- 📊 Active cache with 400x+ speed improvements
- 🌐 Responsive web dashboard
- 📈 Real-time market data (with API credentials)
- 🤖 Automated drop detection and entry analysis
- 📋 Complete trade logging and portfolio tracking

## 💡 Tips for Success

1. **Start with Paper Trading**: Always test with `PAPER_TRADING = True`
2. **Monitor Logs**: Watch the console for trading signals and errors
3. **Use Dashboard**: The web interface is the best way to monitor
4. **Adjust Thresholds**: Lower `DROP_THRESHOLD` if market is stable
5. **Check Cache**: Monitor cache performance for optimization
6. **Regular Testing**: Run `system_test.py` after changes

Your AlpacaBot is now ready for deployment and continuous operation! 🚀 