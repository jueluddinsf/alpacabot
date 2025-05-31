#!/usr/bin/env python3
"""
Cache Performance Test Script
Shows the dramatic performance improvement from caching
"""
import time
from trading_bot import TradingBot
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_cache_performance():
    """Test cache performance with price lookups"""
    bot = TradingBot()
    
    test_symbols = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMD', 'GOOGL', 'AMZN', 'META', 'NFLX', 'ORCL']
    
    logger.info("🧪 Cache Performance Test")
    logger.info("=" * 50)
    
    # Test 1: First run (cold cache)
    logger.info("📈 Test 1: Cold cache (first run)")
    start_time = time.time()
    
    prices_1 = {}
    for symbol in test_symbols:
        price = bot.get_current_price(symbol)
        if price:
            prices_1[symbol] = price
            logger.info(f"  {symbol}: ${price:.2f}")
    
    cold_time = time.time() - start_time
    logger.info(f"⏱️  Cold cache time: {cold_time:.3f} seconds")
    
    # Test 2: Second run (hot cache)
    logger.info("\n📈 Test 2: Hot cache (second run)")
    start_time = time.time()
    
    prices_2 = {}
    for symbol in test_symbols:
        price = bot.get_current_price(symbol)
        if price:
            prices_2[symbol] = price
            logger.info(f"  {symbol}: ${price:.2f}")
    
    hot_time = time.time() - start_time
    logger.info(f"⏱️  Hot cache time: {hot_time:.3f} seconds")
    
    # Results
    logger.info("\n🎯 PERFORMANCE RESULTS")
    logger.info("=" * 50)
    logger.info(f"📊 Cold cache: {cold_time:.3f}s")
    logger.info(f"📊 Hot cache:  {hot_time:.3f}s")
    
    if hot_time > 0:
        speedup = cold_time / hot_time
        logger.info(f"🚀 Speed improvement: {speedup:.1f}x faster!")
        logger.info(f"⏰ Time saved: {cold_time - hot_time:.3f}s ({((cold_time - hot_time) / cold_time * 100):.1f}%)")
    
    # Cache stats
    cache_stats = bot.cache.get_cache_stats()
    logger.info(f"\n🗄️ CACHE STATISTICS")
    logger.info("=" * 50)
    logger.info(f"📈 Total entries: {cache_stats['total_entries']}")
    logger.info(f"💰 Price entries: {cache_stats['price_entries']}")
    logger.info(f"📜 History entries: {cache_stats['history_entries']}")
    logger.info(f"📁 Filter entries: {cache_stats['filter_entries']}")
    logger.info(f"💾 Cache size: {cache_stats['cache_size_mb']}MB")
    logger.info(f"🕒 Market hours: {'Open' if cache_stats['market_open'] else 'Closed'}")
    
    # Verify data consistency
    logger.info(f"\n✅ DATA CONSISTENCY")
    logger.info("=" * 50)
    consistent = prices_1 == prices_2
    logger.info(f"🔍 Cached data matches fresh data: {'✅ Yes' if consistent else '❌ No'}")
    
    if not consistent:
        logger.warning("⚠️ Cache inconsistency detected! This shouldn't happen.")
        for symbol in test_symbols:
            if symbol in prices_1 and symbol in prices_2:
                if prices_1[symbol] != prices_2[symbol]:
                    logger.warning(f"  {symbol}: {prices_1[symbol]} vs {prices_2[symbol]}")

def test_filter_cache():
    """Test the stock filtering cache"""
    bot = TradingBot()
    
    logger.info("\n🧪 Filter Cache Test")
    logger.info("=" * 50)
    
    # Test with smaller symbol set for speed
    test_symbols = bot.config.SP500_SYMBOLS[:50]  # First 50 symbols
    
    # First run
    logger.info("📈 First filter run (cold cache)")
    start_time = time.time()
    filtered_1 = bot.filter_stocks_above_price(test_symbols)
    cold_time = time.time() - start_time
    
    # Second run  
    logger.info("📈 Second filter run (hot cache)")
    start_time = time.time()
    filtered_2 = bot.filter_stocks_above_price(test_symbols)
    hot_time = time.time() - start_time
    
    logger.info(f"\n🎯 FILTER CACHE RESULTS")
    logger.info("=" * 50)
    logger.info(f"📊 Cold cache: {cold_time:.3f}s")
    logger.info(f"📊 Hot cache:  {hot_time:.3f}s")
    
    if hot_time > 0:
        speedup = cold_time / hot_time
        logger.info(f"🚀 Speed improvement: {speedup:.1f}x faster!")
    
    logger.info(f"✅ Consistent results: {'Yes' if filtered_1 == filtered_2 else 'No'}")

if __name__ == "__main__":
    test_cache_performance()
    test_filter_cache() 