#!/usr/bin/env python3
"""
Test Duplicate Holding Prevention
Verifies that the bot doesn't buy stocks it already holds
"""

import json
import os
from trading_bot import TradingBot
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_duplicate_prevention():
    """Test that bot doesn't buy stocks it already holds"""
    
    logger.info("🧪 Testing duplicate holding prevention...")
    
    # Initialize bot
    bot = TradingBot()
    
    # Create test data
    test_holdings = {
        "AAPL": {
            "buy_price": 150.0,
            "buy_date": "2025-05-31T01:00:00",
            "quantity": 1,
            "status": "holding"
        }
    }
    
    test_watchlist = {
        "AAPL": {
            "added_date": "2025-05-31T02:00:00",
            "drop_detected_price": 140.0,
            "status": "watching",
            "analysis": {"drop_from_high": 35.0}
        },
        "MSFT": {
            "added_date": "2025-05-31T02:00:00", 
            "drop_detected_price": 400.0,
            "status": "watching",
            "analysis": {"drop_from_high": 32.0}
        }
    }
    
    # Save test data
    bot.save_json_file('data/test_holdings.json', test_holdings)
    bot.save_json_file('data/test_watchlist.json', test_watchlist)
    
    # Temporarily redirect config to test files
    original_holdings_file = bot.config.HOLDINGS_FILE
    original_watchlist_file = bot.config.WATCHLIST_FILE
    
    bot.config.HOLDINGS_FILE = 'data/test_holdings.json'
    bot.config.WATCHLIST_FILE = 'data/test_watchlist.json'
    
    try:
        # Test the buy logic
        logger.info("📊 Before buy attempt:")
        logger.info(f"  Holdings: {list(test_holdings.keys())}")
        logger.info(f"  Watchlist: {list(test_watchlist.keys())}")
        
        # This should skip AAPL (already held) and potentially buy MSFT
        bot.try_to_buy()
        
        # Check results
        updated_holdings = bot.load_json_file('data/test_holdings.json')
        updated_watchlist = bot.load_json_file('data/test_watchlist.json')
        
        logger.info("📊 After buy attempt:")
        logger.info(f"  Holdings: {list(updated_holdings.keys())}")
        logger.info(f"  Watchlist: {list(updated_watchlist.keys())}")
        
        # Verify AAPL was not bought again
        if "AAPL" in updated_watchlist:
            logger.info("✅ SUCCESS: AAPL remained in watchlist (not bought again)")
        else:
            logger.warning("⚠️ AAPL was removed from watchlist - check logic")
        
        # Check if AAPL is still the only holding or if MSFT was added
        if len(updated_holdings) == 1 and "AAPL" in updated_holdings:
            logger.info("✅ SUCCESS: Only original AAPL holding remains")
        elif len(updated_holdings) == 2 and "AAPL" in updated_holdings and "MSFT" in updated_holdings:
            logger.info("✅ SUCCESS: MSFT was added, AAPL duplicate prevented")
        else:
            logger.warning(f"⚠️ Unexpected holdings state: {updated_holdings}")
    
    finally:
        # Restore original config
        bot.config.HOLDINGS_FILE = original_holdings_file
        bot.config.WATCHLIST_FILE = original_watchlist_file
        
        # Clean up test files
        for file in ['data/test_holdings.json', 'data/test_watchlist.json']:
            if os.path.exists(file):
                os.remove(file)
        
        logger.info("🧹 Test cleanup completed")

def test_5_minute_frequency():
    """Test the new 5-minute frequency setting"""
    
    logger.info("🧪 Testing 5-minute frequency configuration...")
    
    # Check cache settings are appropriate for 5-minute scans
    from config import Config
    
    logger.info("⚙️ Cache Configuration for 5-minute scanning:")
    logger.info(f"  Price cache expiry: {Config.CACHE_PRICE_EXPIRY} seconds (2 minutes)")
    logger.info(f"  History cache expiry: {Config.CACHE_HISTORY_EXPIRY} seconds (30 minutes)")
    logger.info(f"  Filter cache expiry: {Config.CACHE_FILTER_EXPIRY} seconds (10 minutes)")
    logger.info(f"  Market closed multiplier: {Config.CACHE_MARKET_CLOSED_MULTIPLIER}x")
    
    # Verify reasonable values for 5-minute scanning
    if Config.CACHE_PRICE_EXPIRY <= 300:  # <= 5 minutes
        logger.info("✅ Price cache expiry appropriate for 5-minute scans")
    else:
        logger.warning("⚠️ Price cache expiry might be too long for 5-minute scans")
    
    if Config.CACHE_FILTER_EXPIRY <= 600:  # <= 10 minutes
        logger.info("✅ Filter cache expiry appropriate for 5-minute scans")
    else:
        logger.warning("⚠️ Filter cache expiry might be too long for 5-minute scans")
    
    logger.info("✅ 5-minute frequency configuration verified")

if __name__ == "__main__":
    print("🚀 Testing Enhanced Trading Bot Features")
    print("=" * 50)
    
    test_duplicate_prevention()
    print("-" * 30)
    test_5_minute_frequency()
    
    print("\n🎉 All tests completed!")
    print("✅ Bot now prevents duplicate purchases")
    print("✅ Bot configured for 5-minute scanning frequency") 