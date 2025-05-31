#!/usr/bin/env python3
"""
Demo Data Generator for AlpacaBot

This script creates sample data to demonstrate the dashboard functionality
without needing to run actual trading cycles or have real market data.
"""

import json
import os
from datetime import datetime, timedelta
from config import Config

def create_demo_data():
    """Create demo data files for testing the dashboard"""
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Demo watchlist
    demo_watchlist = {
        "AAPL": {
            "added_date": (datetime.now() - timedelta(days=2)).isoformat(),
            "drop_detected_price": 180.50,
            "status": "watching"
        },
        "NVDA": {
            "added_date": (datetime.now() - timedelta(days=1)).isoformat(),
            "drop_detected_price": 450.75,
            "status": "watching"
        },
        "TSLA": {
            "added_date": datetime.now().isoformat(),
            "drop_detected_price": 195.25,
            "status": "watching"
        }
    }
    
    # Demo holdings
    demo_holdings = {
        "MSFT": {
            "buy_price": 380.25,
            "buy_date": (datetime.now() - timedelta(days=5)).isoformat(),
            "quantity": 1,
            "status": "holding"
        },
        "GOOGL": {
            "buy_price": 135.50,
            "buy_date": (datetime.now() - timedelta(days=3)).isoformat(),
            "quantity": 1,
            "status": "holding"
        }
    }
    
    # Demo trades
    demo_trades = {
        "trades": [
            {
                "timestamp": (datetime.now() - timedelta(days=5)).isoformat(),
                "symbol": "MSFT",
                "action": "BUY",
                "price": 380.25,
                "quantity": 1
            },
            {
                "timestamp": (datetime.now() - timedelta(days=4)).isoformat(),
                "symbol": "AMD",
                "action": "BUY",
                "price": 110.75,
                "quantity": 1
            },
            {
                "timestamp": (datetime.now() - timedelta(days=3, hours=12)).isoformat(),
                "symbol": "GOOGL",
                "action": "BUY",
                "price": 135.50,
                "quantity": 1
            },
            {
                "timestamp": (datetime.now() - timedelta(days=3)).isoformat(),
                "symbol": "AMD",
                "action": "SELL",
                "price": 122.50,
                "quantity": 1
            },
            {
                "timestamp": (datetime.now() - timedelta(days=2)).isoformat(),
                "symbol": "META",
                "action": "BUY",
                "price": 485.00,
                "quantity": 1
            },
            {
                "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
                "symbol": "META",
                "action": "SELL",
                "price": 535.25,
                "quantity": 1
            }
        ]
    }
    
    # Save demo data
    with open(Config.WATCHLIST_FILE, 'w') as f:
        json.dump(demo_watchlist, f, indent=2)
    
    with open(Config.HOLDINGS_FILE, 'w') as f:
        json.dump(demo_holdings, f, indent=2)
    
    with open(Config.TRADES_FILE, 'w') as f:
        json.dump(demo_trades, f, indent=2)
    
    print("✅ Demo data created successfully!")
    print(f"📁 Files created:")
    print(f"   - {Config.WATCHLIST_FILE}")
    print(f"   - {Config.HOLDINGS_FILE}")
    print(f"   - {Config.TRADES_FILE}")
    print()
    print("🚀 You can now run the dashboard to see the demo data:")
    print("   python run_bot.py dashboard")

if __name__ == "__main__":
    create_demo_data() 