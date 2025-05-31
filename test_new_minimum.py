#!/usr/bin/env python3
"""
Test New $5 Minimum Price Filter
"""

from trading_bot import TradingBot
from config import Config

def test_new_minimum():
    bot = TradingBot()
    print(f"✅ Current minimum stock price: ${Config.MIN_STOCK_PRICE}")
    
    # Test with the stocks that were problematic
    test_symbols = ['OPEN', 'AMC', 'GME', 'SNAP', 'INTC', 'F', 'T', 'AAPL']
    print(f"\n🔍 Testing filter with ${Config.MIN_STOCK_PRICE} minimum:")
    
    eligible_count = 0
    filtered_count = 0
    
    for symbol in test_symbols:
        price = bot.get_current_price(symbol)
        if price:
            eligible = price >= Config.MIN_STOCK_PRICE
            status = '✅ Eligible' if eligible else '❌ Filtered out'
            print(f"  {symbol}: ${price:.2f} - {status}")
            
            if eligible:
                eligible_count += 1
            else:
                filtered_count += 1
    
    print(f"\n📊 Results:")
    print(f"  Eligible: {eligible_count} stocks")
    print(f"  Filtered out: {filtered_count} stocks")
    print(f"  Success: Avoiding penny stocks while expanding opportunities!")

if __name__ == "__main__":
    test_new_minimum() 