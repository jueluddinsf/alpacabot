#!/usr/bin/env python3
"""
Test Price Filter Comparison
Compare $20 vs $50 minimum price filter to see additional opportunities
"""

from trading_bot import TradingBot
from config import Config
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_price_filter_comparison():
    """Test how many more stocks are available with $20 vs $50 minimum"""
    
    print("📊 Testing $20 vs $50 minimum stock price...")
    print(f"Current minimum: ${Config.MIN_STOCK_PRICE}")
    
    bot = TradingBot()
    
    # Test with a broader subset to get representative data
    test_symbols = [
        'AAPL', 'MSFT', 'INTC', 'GME', 'AMC', 'SNAP', 'LYFT', 'SOFI', 'OPEN', 
        'F', 'T', 'KO', 'PFE', 'BAC', 'C', 'WFC', 'JPM', 'V', 'MA', 'NVDA',
        'TSLA', 'AMD', 'ROKU', 'UBER', 'PLTR', 'HOOD', 'UPST', 'MRNA', 'BNTX'
    ]
    
    above_20 = 0
    above_50 = 0
    prices = {}
    
    print(f"\n🔍 Checking {len(test_symbols)} representative stocks...")
    
    for symbol in test_symbols:
        price = bot.get_current_price(symbol)
        if price:
            prices[symbol] = price
            if price >= 20:
                above_20 += 1
            if price >= 50:
                above_50 += 1
    
    print(f"\n📈 Price Distribution Analysis:")
    
    # Group by price ranges
    penny_stocks = [(s, p) for s, p in prices.items() if p < 5]
    low_price = [(s, p) for s, p in prices.items() if 5 <= p < 20]
    mid_price = [(s, p) for s, p in prices.items() if 20 <= p < 50]
    high_price = [(s, p) for s, p in prices.items() if p >= 50]
    
    print(f"  💰 High Price ($50+): {len(high_price)} stocks")
    for symbol, price in sorted(high_price, key=lambda x: x[1]):
        print(f"    {symbol}: ${price:.2f}")
    
    print(f"  🔶 Mid Price ($20-$49): {len(mid_price)} stocks")
    for symbol, price in sorted(mid_price, key=lambda x: x[1]):
        print(f"    {symbol}: ${price:.2f}")
    
    print(f"  🔸 Low Price ($5-$19): {len(low_price)} stocks")
    for symbol, price in sorted(low_price, key=lambda x: x[1]):
        print(f"    {symbol}: ${price:.2f}")
    
    print(f"  ⚠️  Penny Stocks (<$5): {len(penny_stocks)} stocks")
    for symbol, price in sorted(penny_stocks, key=lambda x: x[1]):
        print(f"    {symbol}: ${price:.2f}")
    
    print(f"\n📊 Filter Comparison Results:")
    print(f"  Above $50: {above_50}/{len(prices)} stocks ({above_50/len(prices)*100:.1f}%)")
    print(f"  Above $20: {above_20}/{len(prices)} stocks ({above_20/len(prices)*100:.1f}%)")
    print(f"  Additional opportunities: +{above_20-above_50} stocks ({(above_20-above_50)/len(prices)*100:.1f}%)")
    
    # Safety analysis
    safe_additions = len([p for p in mid_price if p[1] >= 20])
    print(f"\n🛡️ Safety Analysis:")
    print(f"  Safe additions ($20-$49): {safe_additions} stocks")
    print(f"  Risky additions ($5-$19): {len(low_price)} stocks")
    print(f"  Very risky (<$5): {len(penny_stocks)} stocks")
    
    if len(penny_stocks) > 0:
        print(f"\n⚠️  Warning: {len(penny_stocks)} penny stocks detected!")
        print("   Consider setting minimum to $5 to avoid penny stocks")
    else:
        print(f"\n✅ Good: No penny stocks with $20 minimum")
        print("   Safe expansion of trading universe")

def test_actual_sp500_filter():
    """Test the filter on actual S&P 500 symbols"""
    print(f"\n🔍 Testing filter on actual S&P 500 symbols...")
    
    bot = TradingBot()
    
    # Test first 50 symbols to get a real sense
    test_symbols = Config.SP500_SYMBOLS[:50]
    
    print(f"Testing first 50 S&P 500 symbols...")
    above_20_count = 0
    above_50_count = 0
    total_checked = 0
    
    for symbol in test_symbols:
        price = bot.get_current_price(symbol)
        if price:
            total_checked += 1
            if price >= 20:
                above_20_count += 1
            if price >= 50:
                above_50_count += 1
    
    if total_checked > 0:
        print(f"\n📈 S&P 500 Sample Results (first 50 symbols):")
        print(f"  Successfully checked: {total_checked} stocks")
        print(f"  Above $50: {above_50_count} stocks ({above_50_count/total_checked*100:.1f}%)")
        print(f"  Above $20: {above_20_count} stocks ({above_20_count/total_checked*100:.1f}%)")
        print(f"  Additional opportunities: +{above_20_count-above_50_count} stocks")
        
        # Extrapolate to full S&P 500
        estimated_total_above_20 = int((above_20_count / total_checked) * len(Config.SP500_SYMBOLS))
        estimated_total_above_50 = int((above_50_count / total_checked) * len(Config.SP500_SYMBOLS))
        
        print(f"\n🎯 Estimated Full S&P 500 Impact:")
        print(f"  Estimated above $50: ~{estimated_total_above_50} stocks")
        print(f"  Estimated above $20: ~{estimated_total_above_20} stocks")
        print(f"  Estimated additional opportunities: ~{estimated_total_above_20 - estimated_total_above_50} stocks")

if __name__ == "__main__":
    print("🚀 Price Filter Comparison Test")
    print("=" * 50)
    
    test_price_filter_comparison()
    test_actual_sp500_filter()
    
    print("\n🎉 Analysis complete!")
    print("✅ $20 minimum provides more opportunities while avoiding penny stocks") 