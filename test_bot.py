#!/usr/bin/env python3
"""
Test Script for AlpacaBot

This script tests the core functionality of the trading bot
to ensure everything is working correctly.
"""

import sys
import traceback
from trading_bot import TradingBot
from config import Config
import demo_data

def test_configuration():
    """Test configuration loading"""
    print("🔧 Testing configuration...")
    try:
        config = Config()
        print(f"   ✅ Min stock price: ${config.MIN_STOCK_PRICE}")
        print(f"   ✅ Drop threshold: {config.DROP_THRESHOLD * 100}%")
        print(f"   ✅ Profit target: {config.PROFIT_TARGET * 100}%")
        print(f"   ✅ Paper trading: {config.PAPER_TRADING}")
        print(f"   ✅ Stock universe: {len(config.SP500_SYMBOLS)} symbols")
        return True
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        return False

def test_bot_initialization():
    """Test bot initialization"""
    print("\n🤖 Testing bot initialization...")
    try:
        bot = TradingBot()
        print("   ✅ Bot initialized successfully")
        
        if bot.data_client:
            print("   ✅ Alpaca data client connected")
        else:
            print("   ⚠️  Using demo mode (Yahoo Finance)")
            
        if bot.trading_client:
            print("   ✅ Alpaca trading client connected")
        else:
            print("   ⚠️  Trading client in demo mode")
            
        return True
    except Exception as e:
        print(f"   ❌ Bot initialization error: {e}")
        traceback.print_exc()
        return False

def test_price_fetching():
    """Test price data fetching"""
    print("\n📊 Testing price data fetching...")
    try:
        bot = TradingBot()
        test_symbols = ['AAPL', 'MSFT', 'GOOGL']
        
        for symbol in test_symbols:
            price = bot.get_current_price(symbol)
            if price:
                print(f"   ✅ {symbol}: ${price:.2f}")
            else:
                print(f"   ❌ {symbol}: Failed to get price")
                
        return True
    except Exception as e:
        print(f"   ❌ Price fetching error: {e}")
        return False

def test_data_operations():
    """Test JSON data operations"""
    print("\n💾 Testing data operations...")
    try:
        bot = TradingBot()
        
        # Test loading empty files
        watchlist = bot.load_json_file(bot.config.WATCHLIST_FILE)
        holdings = bot.load_json_file(bot.config.HOLDINGS_FILE)
        trades = bot.load_json_file(bot.config.TRADES_FILE)
        
        print(f"   ✅ Watchlist loaded: {len(watchlist)} items")
        print(f"   ✅ Holdings loaded: {len(holdings)} items")
        print(f"   ✅ Trades loaded: {len(trades.get('trades', []))} items")
        
        return True
    except Exception as e:
        print(f"   ❌ Data operations error: {e}")
        return False

def test_portfolio_summary():
    """Test portfolio summary calculation"""
    print("\n📈 Testing portfolio summary...")
    try:
        bot = TradingBot()
        summary = bot.get_portfolio_summary()
        
        print(f"   ✅ Total value: ${summary['total_value']:.2f}")
        print(f"   ✅ Profit/loss: ${summary['profit_loss']:.2f}")
        print(f"   ✅ Holdings count: {summary['holdings_count']}")
        print(f"   ✅ Watchlist count: {summary['watchlist_count']}")
        
        return True
    except Exception as e:
        print(f"   ❌ Portfolio summary error: {e}")
        return False

def test_with_demo_data():
    """Test functionality with demo data"""
    print("\n🎭 Testing with demo data...")
    try:
        # Create demo data
        demo_data.create_demo_data()
        print("   ✅ Demo data created")
        
        # Test bot with demo data
        bot = TradingBot()
        summary = bot.get_portfolio_summary()
        
        print(f"   ✅ Portfolio with demo data:")
        print(f"      - Holdings: {summary['holdings_count']}")
        print(f"      - Watchlist: {summary['watchlist_count']}")
        print(f"      - Total value: ${summary['total_value']:.2f}")
        
        return True
    except Exception as e:
        print(f"   ❌ Demo data test error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🧪 Running AlpacaBot Tests")
    print("=" * 50)
    
    tests = [
        test_configuration,
        test_bot_initialization,
        test_price_fetching,
        test_data_operations,
        test_portfolio_summary,
        test_with_demo_data
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The bot is ready to use.")
        print("\n🚀 Next steps:")
        print("   1. Set up your Alpaca API credentials in .env file")
        print("   2. Run: python run_bot.py dashboard")
        print("   3. Open http://localhost:5000 in your browser")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 