#!/usr/bin/env python3
"""
Quick scan to test Alpaca connection and find stocks with drops
"""
from trading_bot import TradingBot
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def quick_drop_scan():
    """Quick scan for any stocks with 15%+ drops to test algorithm"""
    bot = TradingBot()
    
    if not bot.data_client:
        logger.error("❌ No Alpaca data client available")
        return
    
    logger.info("🔍 Quick scan for stocks with 15%+ drops...")
    
    # Test with a smaller set of volatile stocks first
    test_symbols = [
        'AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMD', 'INTC', 'COIN', 'GME', 'AMC', 'ROKU',
        'SNAP', 'UBER', 'LYFT', 'PLTR', 'SOFI', 'HOOD', 'OPEN', 'UPST', 'MRNA', 'BNTX'
    ]
    
    found_drops = []
    successful_scans = 0
    
    for symbol in test_symbols:
        try:
            # Test price fetching
            current_price = bot.get_current_price(symbol)
            if current_price:
                logger.info(f"✅ {symbol}: ${current_price:.2f}")
                
                # Test drop analysis
                meets_criteria, analysis = bot.check_drop_criteria(symbol)
                successful_scans += 1
                
                if analysis.get('drop_from_high', 0) > 15:  # 15%+ drop
                    found_drops.append({
                        'symbol': symbol,
                        'drop': analysis.get('drop_from_high', 0),
                        'price': current_price,
                        'analysis': analysis
                    })
                    logger.info(f"📉 {symbol}: {analysis.get('drop_from_high', 0):.1f}% drop detected!")
                    
            else:
                logger.warning(f"❌ {symbol}: No price data")
                
        except Exception as e:
            logger.error(f"❌ {symbol}: Error - {e}")
    
    logger.info(f"\n📊 SCAN RESULTS:")
    logger.info(f"✅ Successfully scanned: {successful_scans}/{len(test_symbols)} stocks")
    logger.info(f"📉 Found {len(found_drops)} stocks with 15%+ drops:")
    
    for drop in found_drops:
        logger.info(f"  🔻 {drop['symbol']}: {drop['drop']:.1f}% drop (${drop['price']:.2f})")
    
    if len(found_drops) > 0:
        logger.info("🎯 Algorithm is working! Now we can test with these drops.")
    else:
        logger.info("💡 No major drops found. Market might be stable today.")
        logger.info("💡 To test the bot, you could temporarily lower the drop threshold.")
    
    return found_drops

if __name__ == "__main__":
    quick_drop_scan() 