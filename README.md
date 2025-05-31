# 🤖 AlpacaBot Trading Bot

A sophisticated automated trading bot that implements a "buy the dip" strategy using real-time market data and the Alpaca trading API.

![Trading Bot Dashboard](https://img.shields.io/badge/Dashboard-Live-brightgreen) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Alpaca](https://img.shields.io/badge/Alpaca-API-orange)

## 📈 Strategy Overview

The bot implements a systematic approach to buying market dips and capitalizing on recoveries:

- **Universe**: S&P 500 stocks with price > $50
- **Trigger**: Add to watchlist when stock drops ≥30% in the past week
- **Entry**: Buy 1 share when price stabilizes (immediate entry in current implementation)
- **Exit**: Sell when profit reaches ≥10%

## 🎯 Key Features

### 🖥️ Web Dashboard
- **Real-time Portfolio Tracking**: Live P&L, holdings value, and performance metrics
- **Watchlist Monitoring**: Stocks being monitored for potential entry
- **Trade History**: Complete log of buy/sell transactions
- **Manual Controls**: Trigger trading cycles manually
- **Responsive Design**: Works on desktop and mobile devices

### 🔄 Automated Trading
- **Drop Detection**: Scans S&P 500 for significant price drops
- **Risk Management**: Position sizing and profit targets
- **Paper Trading**: Safe testing environment before live trading
- **Error Handling**: Robust error handling and logging

### 📊 Data Sources
- **Primary**: Alpaca Markets API (real-time data)
- **Fallback**: Yahoo Finance (free alternative)
- **Reliability**: Automatic failover between data sources

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd alpacaBot

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the project root:

```bash
# Copy the example environment file
cp env_example.txt .env
```

Edit `.env` with your credentials:

```env
# Alpaca API Credentials (required for live trading)
APCA_API_KEY_ID=your_alpaca_api_key_here
APCA_API_SECRET_KEY=your_alpaca_secret_key_here

# Trading Mode
PAPER_TRADING=True  # Set to False for live trading

# Dashboard Settings
FLASK_SECRET_KEY=your_secret_key_here
FLASK_DEBUG=True
FLASK_PORT=5000
```

### 3. Get Alpaca API Keys

1. Sign up at [Alpaca Markets](https://alpaca.markets/)
2. Create a paper trading account (free)
3. Generate API keys from the dashboard
4. Add keys to your `.env` file

> **Note**: The bot will work in demo mode without API keys, using Yahoo Finance for price data.

### 4. Run the Bot

**Option 1: Web Dashboard (Recommended)**
```bash
python run_bot.py dashboard
```
Then open http://localhost:5000 in your browser.

**Option 2: Single Trading Cycle**
```bash
python run_bot.py single
```

**Option 3: Continuous Trading**
```bash
python run_bot.py continuous
```

## 📱 Dashboard Features

### Portfolio Summary
- **Total Value**: Current value of all holdings
- **Profit/Loss**: Unrealized gains/losses with percentage
- **Holdings Count**: Number of stocks currently held
- **Watchlist Count**: Stocks being monitored

### Holdings Table
- Stock symbol and quantity
- Buy price vs current price
- Real-time profit/loss calculation
- Current market value

### Watchlist Table
- Stocks that triggered the drop criteria
- Entry price when added to watchlist
- Current price and additional drops
- Status tracking

### Trade History
- Chronological list of all trades
- Buy/sell actions with timestamps
- Price and quantity information
- Performance tracking

## ⚙️ Configuration

### Trading Parameters

Edit `config.py` to customize the strategy:

```python
# Strategy Parameters
MIN_STOCK_PRICE = 50        # Minimum stock price to consider
DROP_THRESHOLD = 0.30       # 30% drop threshold
PROFIT_TARGET = 0.10        # 10% profit target
LOOKBACK_DAYS = 7           # Look back 7 days for drop detection
```

### Stock Universe

The bot monitors a curated list of S&P 500 stocks. You can modify the list in `config.py`:

```python
SP500_SYMBOLS = [
    'AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'TSLA'
    # Add more symbols as needed
]
```

## 🔒 Safety Features

### Paper Trading Mode
- **Default**: All trading is simulated by default
- **Safe Testing**: Test strategies without real money
- **Full Functionality**: All features work in paper mode

### Risk Management
- **Position Sizing**: Fixed 1 share per position (customizable)
- **Stop Conditions**: Automatic selling at profit targets
- **Error Handling**: Graceful handling of API failures

### Data Redundancy
- **Primary Source**: Alpaca Markets API
- **Backup Source**: Yahoo Finance
- **Automatic Failover**: Seamless switching between sources

## 📊 File Structure

```
alpacaBot/
├── config.py              # Configuration and strategy parameters
├── trading_bot.py          # Core trading logic and algorithms
├── dashboard.py            # Flask web application
├── run_bot.py             # Main runner script
├── requirements.txt        # Python dependencies
├── env_example.txt        # Environment variables template
├── data/                  # Data storage
│   ├── watchlist.json     # Stocks being monitored
│   ├── holdings.json      # Current positions
│   └── trades.json        # Trade history
└── templates/
    └── dashboard.html     # Web dashboard template
```

## 🔄 Trading Workflow

1. **Scanning Phase**
   - Monitor S&P 500 stocks above $50
   - Calculate 7-day price performance
   - Identify stocks with ≥30% drops

2. **Watchlist Phase**
   - Add qualifying stocks to watchlist
   - Track current prices vs entry signals
   - Monitor for buying opportunities

3. **Entry Phase**
   - Execute buy orders for watchlist stocks
   - Move stocks from watchlist to holdings
   - Log trade transactions

4. **Exit Phase**
   - Monitor holdings for profit targets
   - Execute sell orders at ≥10% profit
   - Remove from holdings and log trades

## 🛠️ Advanced Usage

### Customizing Entry Logic

Modify the `try_to_buy()` method in `trading_bot.py` to add more sophisticated entry criteria:

```python
def try_to_buy(self):
    # Add custom entry logic here
    # Examples:
    # - Volume confirmation
    # - Technical indicators
    # - Market conditions
    pass
```

### Adding More Stocks

Update the `SP500_SYMBOLS` list in `config.py` or create a dynamic stock screener.

### Scheduling

Use cron jobs or task schedulers to run trading cycles automatically:

```bash
# Run every hour during market hours
0 9-16 * * 1-5 /usr/bin/python3 /path/to/alpacaBot/run_bot.py single
```

## 🐛 Troubleshooting

### Common Issues

**1. "Alpaca API credentials not found"**
- Solution: Create `.env` file with valid API keys
- Alternative: Run in demo mode (uses Yahoo Finance)

**2. "Error getting price for [SYMBOL]"**
- Cause: Network issues or API rate limits
- Solution: Check internet connection, try again later

**3. "Flask app won't start"**
- Cause: Port already in use
- Solution: Change `FLASK_PORT` in `.env` or stop other applications

**4. "No stocks added to watchlist"**
- Cause: No stocks meet the drop criteria currently
- Solution: Normal operation, check during volatile market periods

### Logs and Debugging

The bot provides detailed logging:

```bash
# Run with verbose logging
python run_bot.py single
```

Check the console output for detailed information about:
- Stock scanning results
- Entry/exit decisions
- API call status
- Error messages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly in paper trading mode
5. Submit a pull request

## ⚠️ Disclaimer

This trading bot is for educational and research purposes. Always:

- **Start with paper trading**
- **Test thoroughly before live trading**
- **Understand the risks involved**
- **Never invest more than you can afford to lose**
- **Comply with your local financial regulations**

Trading stocks involves substantial risk and may not be suitable for all investors.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

For questions, issues, or contributions:

1. Check the troubleshooting section
2. Review existing GitHub issues
3. Create a new issue with detailed information
4. Include logs and configuration details

---

**Happy Trading! 🚀📈** 