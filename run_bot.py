#!/usr/bin/env python3
"""
AlpacaBot Trading Bot Runner

This script provides different ways to run the trading bot:
1. Dashboard mode - Run the web dashboard
2. Single cycle - Run one trading cycle 
3. Continuous mode - Run continuous trading cycles
"""

import argparse
import sys
import time
import threading
from trading_bot import TradingBot
from dashboard import app, socketio
from config import Config

def run_dashboard():
    """Run the web dashboard"""
    print("🚀 Starting AlpacaBot Dashboard...")
    print(f"Dashboard will be available at: http://localhost:{Config.FLASK_PORT}")
    print("📊 Features:")
    print("  - Real-time portfolio tracking")
    print("  - Watchlist monitoring")
    print("  - Trade history")
    print("  - Manual trading cycle execution")
    print()
    
    if not Config.API_KEY or not Config.SECRET_KEY:
        print("⚠️  WARNING: Alpaca API credentials not found.")
        print("   The bot will run in demo mode using Yahoo Finance data.")
        print("   To use live trading, set your credentials in a .env file.")
        print()
    
    socketio.run(app, debug=Config.FLASK_DEBUG, port=Config.FLASK_PORT, host='0.0.0.0')

def run_single_cycle():
    """Run a single trading cycle"""
    print("🔄 Running single trading cycle...")
    bot = TradingBot()
    bot.run_cycle()
    print("✅ Single cycle completed")

def run_continuous():
    """Run continuous trading cycles"""
    print("🔁 Starting continuous trading mode...")
    print("⚠️  This will run trading cycles every 5 minutes. Press Ctrl+C to stop.")
    
    bot = TradingBot()
    
    try:
        while True:
            print(f"\n📈 Starting trading cycle at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            bot.run_cycle()
            print(f"⏰ Waiting 5 minutes until next cycle...")
            time.sleep(300)  # Wait 5 minutes (300 seconds)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping continuous trading mode...")
        print("✅ Bot stopped safely")

def main():
    parser = argparse.ArgumentParser(
        description="AlpacaBot Trading Bot - Automated trading based on drop patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_bot.py dashboard          # Run web dashboard (recommended)
  python run_bot.py single             # Run one trading cycle
  python run_bot.py continuous         # Run continuous trading (advanced)

Strategy Summary:
  • Monitors S&P 500 stocks above $50
  • Adds stocks to watchlist when they drop ≥30% in 7 days  
  • Buys 1 share when price stabilizes
  • Sells when profit reaches ≥10%
        """
    )
    
    parser.add_argument(
        'mode',
        choices=['dashboard', 'single', 'continuous'],
        help='Bot operation mode'
    )
    
    args = parser.parse_args()
    
    # Print header
    print("=" * 60)
    print("🤖 AlpacaBot Trading Bot")
    print("=" * 60)
    print(f"Mode: {args.mode.title()}")
    print(f"Paper Trading: {'Yes' if Config.PAPER_TRADING else 'No (LIVE TRADING)'}")
    print(f"Strategy: Drop ≥{Config.DROP_THRESHOLD*100}% → Buy → Sell at +{Config.PROFIT_TARGET*100}%")
    print("=" * 60)
    
    if args.mode == 'dashboard':
        run_dashboard()
    elif args.mode == 'single':
        run_single_cycle()
    elif args.mode == 'continuous':
        run_continuous()

if __name__ == "__main__":
    main() 