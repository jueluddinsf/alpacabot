import json
import os
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from config import Config
from cache_manager import CacheManager
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self):
        self.config = Config()
        self.simulation_mode = False  # Use real Alpaca data
        
        # Initialize cache manager
        self.cache = CacheManager(self.config)
        
        # Initialize Alpaca clients
        if self.config.API_KEY and self.config.SECRET_KEY:
            try:
                self.data_client = StockHistoricalDataClient(
                    self.config.API_KEY, 
                    self.config.SECRET_KEY
                )
                self.trading_client = TradingClient(
                    self.config.API_KEY, 
                    self.config.SECRET_KEY, 
                    paper=self.config.PAPER_TRADING
                )
                logger.info(f"🚀 Alpaca clients initialized (Paper Trading: {self.config.PAPER_TRADING})")
                logger.info(f"🔍 Ready to scan {len(self.config.SP500_SYMBOLS)} stocks for real market opportunities")
            except Exception as e:
                logger.warning(f"Alpaca API connection issue: {e}")
                logger.info("⚠️ Some API calls may fail, but continuing with available data...")
                self.data_client = StockHistoricalDataClient(
                    self.config.API_KEY, 
                    self.config.SECRET_KEY
                ) if self.config.API_KEY else None
                self.trading_client = None
        else:
            logger.error("❌ Alpaca API credentials not found. Please check your .env file")
            self.data_client = None
            self.trading_client = None
            
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
    
    def load_json_file(self, filepath: str) -> Dict:
        """Load JSON file, return empty dict if file doesn't exist"""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                logger.error(f"Error loading {filepath}")
                return {}
        return {}
    
    def save_json_file(self, filepath: str, data: Dict):
        """Save data to JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving {filepath}: {e}")
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current stock price using Alpaca with caching"""
        # Check cache first
        cache_key = self.cache.get_cache_key("price", symbol)
        cached_price = self.cache.get(cache_key, "price")
        if cached_price is not None:
            return cached_price
        
        try:
            if not self.data_client:
                return None
                
            # Get latest available data from Alpaca
            end_time = datetime.now()
            start_time = end_time - timedelta(days=7)  # Look back a week for latest data
            
            bars = self.data_client.get_stock_bars(StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Day,
                start=start_time,
                end=end_time
            )).df
            
            if not bars.empty:
                latest_price = float(bars['close'].iloc[-1])
                
                # Cache the result
                self.cache.set(cache_key, latest_price)
                
                return latest_price
            else:
                return None
                
        except Exception as e:
            # Silently fail for individual stocks to continue scanning
            return None
    
    def get_price_history(self, symbol: str, days: int = 7) -> Optional[pd.DataFrame]:
        """Get price history for a symbol using Alpaca with caching"""
        # Check cache first
        cache_key = self.cache.get_cache_key("history", symbol, f"days_{days}")
        cached_history = self.cache.get(cache_key, "history")
        if cached_history is not None:
            # Convert back to DataFrame
            return pd.DataFrame(cached_history)
        
        try:
            if not self.data_client:
                return None
                
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days+10)  # Get extra days for analysis
            
            bars = self.data_client.get_stock_bars(StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Day,
                start=start_time,
                end=end_time
            )).df
            
            if not bars.empty and len(bars) >= 2:
                # Cache the result (convert DataFrame to dict for JSON serialization)
                self.cache.set(cache_key, bars.to_dict('records'))
                return bars
            else:
                return None
                
        except Exception as e:
            # Silently fail for individual stocks to continue scanning
            return None
    
    def filter_stocks_above_price(self, symbols: List[str]) -> List[str]:
        """Filter stocks that are above minimum price threshold with caching"""
        # Check if we have a recent cached result for the full filter
        filter_key = self.cache.get_cache_key("filter", f"above_{self.config.MIN_STOCK_PRICE}")
        cached_result = self.cache.get(filter_key, "filter")
        if cached_result is not None:
            logger.info(f"📋 Using cached stock filter results: {len(cached_result)} stocks above ${self.config.MIN_STOCK_PRICE}")
            return cached_result
        
        filtered = []
        logger.info(f"💰 Filtering {len(symbols)} stocks above ${self.config.MIN_STOCK_PRICE}...")
        
        successful_checks = 0
        failed_checks = 0
        
        for i, symbol in enumerate(symbols):
            try:
                price = self.get_current_price(symbol)  # This now uses caching
                if price and price > self.config.MIN_STOCK_PRICE:
                    filtered.append(symbol)
                    successful_checks += 1
                elif price:
                    successful_checks += 1
                else:
                    failed_checks += 1
                    
                # Progress update every 50 stocks
                if (i + 1) % 50 == 0:
                    cache_stats = self.cache.get_cache_stats()
                    logger.info(f"📊 Progress: {i + 1}/{len(symbols)} stocks checked | Found: {len(filtered)} | Success rate: {successful_checks/(successful_checks+failed_checks)*100:.1f}% | Cache: {cache_stats['price_entries']} entries")
                    
            except Exception as e:
                failed_checks += 1
        
        # Cache the filtered result
        self.cache.set(filter_key, filtered)
        
        logger.info(f"✅ Filtering complete: {len(filtered)} stocks above ${self.config.MIN_STOCK_PRICE} | Success rate: {successful_checks/(successful_checks+failed_checks)*100:.1f}%")
        return filtered
    
    def check_drop_criteria(self, symbol: str) -> tuple[bool, Dict]:
        """Check if stock dropped 30% or more in the past week with detailed analysis"""
        try:
            hist = self.get_price_history(symbol, self.config.LOOKBACK_DAYS)
            if hist is None or len(hist) < 2:
                return False, {"error": "Insufficient data"}
            
            # Calculate the drop from the highest point in the lookback period to current
            highest_price = hist['high'].max()
            latest_price = hist['close'].iloc[-1]
            
            # Also check from the start of period
            start_price = hist['close'].iloc[0]
            
            # Calculate drops
            drop_from_high = (highest_price - latest_price) / highest_price
            drop_from_start = (start_price - latest_price) / start_price
            
            analysis = {
                "symbol": symbol,
                "highest_price": highest_price,
                "start_price": start_price,
                "latest_price": latest_price,
                "drop_from_high": drop_from_high * 100,
                "drop_from_start": drop_from_start * 100,
                "days_analyzed": len(hist),
                "meets_criteria": drop_from_high >= self.config.DROP_THRESHOLD
            }
            
            # Debug output for any significant drops (15%+)
            if drop_from_high > 0.15:  # 15% or more
                logger.info(f"🔍 {symbol} ANALYSIS: {drop_from_high:.1%} drop from high ${highest_price:.2f} to ${latest_price:.2f} (threshold: {self.config.DROP_THRESHOLD:.1%})")
            
            if analysis["meets_criteria"]:
                logger.info(f"🔻 {symbol} DROP DETECTED: {drop_from_high:.1%} from high ${highest_price:.2f} to ${latest_price:.2f}")
            
            return analysis["meets_criteria"], analysis
            
        except Exception as e:
            logger.error(f"Error checking drop criteria for {symbol}: {e}")
            return False, {"error": str(e)}
    
    def analyze_entry_signal(self, symbol: str, drop_analysis: Dict) -> tuple[bool, str]:
        """Analyze if this is a good entry point beyond just the drop"""
        try:
            # Get recent price history for entry analysis
            hist = self.get_price_history(symbol, 5)  # Last 5 days
            if hist is None or len(hist) < 3:
                return False, "Insufficient recent data"
            
            current_price = hist['close'].iloc[-1]
            prev_close = hist['close'].iloc[-2]
            volume = hist['volume'].iloc[-1] if 'volume' in hist.columns else 0
            avg_volume = hist['volume'].mean() if 'volume' in hist.columns else 0
            
            # Entry criteria
            reasons = []
            
            # 1. Price stabilization - not falling too rapidly
            daily_change = (current_price - prev_close) / prev_close
            if daily_change > -0.05:  # Not dropping more than 5% today
                reasons.append("price_stabilizing")
            
            # 2. Volume analysis (if available)
            if avg_volume > 0 and volume > avg_volume * 0.5:
                reasons.append("decent_volume")
            
            # 3. Not at 52-week low risk (basic check)
            lowest_recent = hist['low'].min()
            if current_price > lowest_recent * 1.02:  # At least 2% above recent low
                reasons.append("above_recent_low")
            
            # Simple entry decision: if we have at least 2 positive signals
            enter = len(reasons) >= 2
            reason_text = f"Entry signals: {', '.join(reasons)}" if enter else f"Waiting: only {len(reasons)} signals"
            
            if enter:
                logger.info(f"📈 {symbol} ENTRY SIGNAL: {reason_text}")
            else:
                logger.debug(f"⏳ {symbol} WAITING: {reason_text}")
                
            return enter, reason_text
            
        except Exception as e:
            logger.error(f"Error analyzing entry for {symbol}: {e}")
            return False, f"Analysis error: {e}"
    
    def update_watchlist(self):
        """Scan for new stocks that meet drop criteria and add to watchlist"""
        logger.info("🔍 Scanning for new drop opportunities...")
        
        watchlist = self.load_json_file(self.config.WATCHLIST_FILE)
        eligible_stocks = self.filter_stocks_above_price(self.config.SP500_SYMBOLS)
        
        logger.info(f"📊 Analyzing {len(eligible_stocks)} eligible stocks for 30% drops...")
        
        new_additions = 0
        analyzed_count = 0
        
        for symbol in eligible_stocks:
            if symbol not in watchlist:
                meets_criteria, analysis = self.check_drop_criteria(symbol)
                analyzed_count += 1
                
                if meets_criteria:
                    current_price = self.get_current_price(symbol)
                    watchlist[symbol] = {
                        "added_date": datetime.now().isoformat(),
                        "drop_detected_price": current_price,
                        "status": "watching",
                        "analysis": analysis
                    }
                    logger.info(f"➕ Added {symbol} to watchlist: {analysis['drop_from_high']:.1f}% drop")
                    new_additions += 1
                
                # Progress update every 25 stocks analyzed
                if analyzed_count % 25 == 0:
                    logger.info(f"📈 Drop analysis progress: {analyzed_count}/{len(eligible_stocks)} stocks analyzed | Found: {new_additions} drops")
        
        if new_additions > 0:
            self.save_json_file(self.config.WATCHLIST_FILE, watchlist)
            logger.info(f"✅ Added {new_additions} new stocks to watchlist")
        else:
            logger.info(f"ℹ️  No stocks with 30%+ drops found out of {analyzed_count} analyzed")
            logger.info("💡 Try lowering the drop threshold if you want to test with smaller drops")
    
    def execute_buy_order(self, symbol: str, price: float) -> bool:
        """Execute buy order for 1 share"""
        try:
            if self.trading_client:
                order = MarketOrderRequest(
                    symbol=symbol,
                    qty=1,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.GTC
                )
                response = self.trading_client.submit_order(order)
                logger.info(f"🟢 BUY ORDER SUBMITTED for {symbol}: Order ID {response.id}")
                return True
            else:
                logger.info(f"📝 [PAPER TRADE] Would buy 1 share of {symbol} at ${price:.2f}")
                return True
        except Exception as e:
            logger.error(f"❌ Error executing buy order for {symbol}: {e}")
            return False
    
    def execute_sell_order(self, symbol: str, price: float) -> bool:
        """Execute sell order for 1 share"""
        try:
            if self.trading_client:
                order = MarketOrderRequest(
                    symbol=symbol,
                    qty=1,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.GTC
                )
                response = self.trading_client.submit_order(order)
                logger.info(f"🔴 SELL ORDER SUBMITTED for {symbol}: Order ID {response.id}")
                return True
            else:
                logger.info(f"📝 [PAPER TRADE] Would sell 1 share of {symbol} at ${price:.2f}")
                return True
        except Exception as e:
            logger.error(f"❌ Error executing sell order for {symbol}: {e}")
            return False
    
    def try_to_buy(self):
        """Check watchlist and buy stocks that are ready with proper entry analysis"""
        watchlist = self.load_json_file(self.config.WATCHLIST_FILE)
        holdings = self.load_json_file(self.config.HOLDINGS_FILE)
        
        if not watchlist:
            logger.info("📋 Watchlist is empty")
            return
        
        logger.info(f"🔍 Analyzing {len(watchlist)} stocks for entry signals...")
        
        bought_count = 0
        skipped_existing = 0
        
        for symbol, info in list(watchlist.items()):
            if info["status"] == "watching":
                # ✅ CHECK: Skip if we already hold this stock
                if symbol in holdings:
                    logger.info(f"⏭️ Skipping {symbol} - Already holding (focusing on sell opportunities)")
                    skipped_existing += 1
                    continue
                
                current_price = self.get_current_price(symbol)
                if current_price:
                    # Enhanced entry analysis
                    enter, reason = self.analyze_entry_signal(symbol, info.get("analysis", {}))
                    
                    if enter and self.execute_buy_order(symbol, current_price):
                        # Move from watchlist to holdings
                        holdings[symbol] = {
                            "buy_price": current_price,
                            "buy_date": datetime.now().isoformat(),
                            "quantity": 1,
                            "status": "holding",
                            "entry_reason": reason,
                            "original_analysis": info.get("analysis", {})
                        }
                        del watchlist[symbol]
                        bought_count += 1
                        
                        # Log trade
                        self.log_trade(symbol, "BUY", current_price, 1)
                        logger.info(f"✅ BOUGHT {symbol} at ${current_price:.2f} - {reason}")
        
        if bought_count > 0:
            self.save_json_file(self.config.WATCHLIST_FILE, watchlist)
            self.save_json_file(self.config.HOLDINGS_FILE, holdings)
            logger.info(f"🛒 Executed {bought_count} buy orders")
        
        if skipped_existing > 0:
            logger.info(f"⏭️ Skipped {skipped_existing} stocks already in holdings")
            
        if bought_count == 0 and skipped_existing == 0:
            logger.info("⏳ No stocks ready for entry yet")
    
    def try_to_sell(self):
        """Check holdings and sell if profit target is reached"""
        holdings = self.load_json_file(self.config.HOLDINGS_FILE)
        
        if not holdings:
            logger.info("💼 No current holdings")
            return
        
        logger.info(f"📊 Checking {len(holdings)} holdings for profit targets...")
        
        sold_count = 0
        for symbol, info in list(holdings.items()):
            if info["status"] == "holding":
                current_price = self.get_current_price(symbol)
                if current_price:
                    buy_price = info["buy_price"]
                    profit_pct = (current_price - buy_price) / buy_price
                    profit_amount = (current_price - buy_price) * info["quantity"]
                    
                    logger.debug(f"{symbol}: ${current_price:.2f} vs ${buy_price:.2f} = {profit_pct:.1%} profit")
                    
                    if profit_pct >= self.config.PROFIT_TARGET:
                        if self.execute_sell_order(symbol, current_price):
                            logger.info(f"💰 SOLD {symbol} for ${profit_amount:.2f} profit ({profit_pct:.1%})")
                            
                            # Log trade
                            self.log_trade(symbol, "SELL", current_price, info["quantity"])
                            
                            # Remove from holdings
                            del holdings[symbol]
                            sold_count += 1
        
        if sold_count > 0:
            self.save_json_file(self.config.HOLDINGS_FILE, holdings)
            logger.info(f"💸 Executed {sold_count} sell orders")
        else:
            logger.info("🎯 No holdings ready for profit-taking yet")
    
    def log_trade(self, symbol: str, action: str, price: float, quantity: int):
        """Log trade to trades file"""
        trades = self.load_json_file(self.config.TRADES_FILE)
        if 'trades' not in trades:
            trades['trades'] = []
        
        trade = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "action": action,
            "price": price,
            "quantity": quantity
        }
        trades['trades'].append(trade)
        self.save_json_file(self.config.TRADES_FILE, trades)
    
    def get_portfolio_summary(self) -> Dict:
        """Get current portfolio summary"""
        holdings = self.load_json_file(self.config.HOLDINGS_FILE)
        watchlist = self.load_json_file(self.config.WATCHLIST_FILE)
        
        total_value = 0
        total_cost = 0
        
        # Calculate current holdings value
        for symbol, info in holdings.items():
            current_price = self.get_current_price(symbol)
            if current_price:
                total_value += current_price * info["quantity"]
                total_cost += info["buy_price"] * info["quantity"]
        
        profit_loss = total_value - total_cost
        profit_loss_pct = (profit_loss / total_cost * 100) if total_cost > 0 else 0
        
        return {
            "total_value": total_value,
            "total_cost": total_cost,
            "profit_loss": profit_loss,
            "profit_loss_pct": profit_loss_pct,
            "holdings_count": len(holdings),
            "watchlist_count": len(watchlist)
        }
    
    def run_cycle(self):
        """Run one complete trading cycle"""
        logger.info("🚀 Starting trading cycle...")
        
        # Clean up expired cache entries at the start of each cycle
        cleared = self.cache.clear_expired()
        
        try:
            self.update_watchlist()
            self.try_to_buy()
            self.try_to_sell()
            
            summary = self.get_portfolio_summary()
            cache_stats = self.cache.get_cache_stats()
            
            logger.info(f"📊 Portfolio Summary: ${summary['total_value']:.2f} "
                       f"(P&L: ${summary['profit_loss']:.2f}, {summary['profit_loss_pct']:.1f}%) "
                       f"| Holdings: {summary['holdings_count']} | Watchlist: {summary['watchlist_count']}")
            
            logger.info(f"🗄️ Cache Stats: {cache_stats['total_entries']} entries "
                       f"({cache_stats['price_entries']} prices, {cache_stats['history_entries']} history) "
                       f"| Size: {cache_stats['cache_size_mb']}MB | Market: {'Open' if cache_stats['market_open'] else 'Closed'}")
            
        except Exception as e:
            logger.error(f"❌ Error in trading cycle: {e}")
        
        logger.info("✅ Trading cycle completed")
    
    def get_cache_status(self) -> Dict:
        """Get cache status for dashboard"""
        return {
            "enabled": True,
            "stats": self.cache.get_cache_stats()
        }
    
    def clear_cache(self, symbol: str = None) -> None:
        """Clear cache (all or for specific symbol)"""
        if symbol:
            self.cache.clear_symbol(symbol)
        else:
            self.cache.clear_all()

if __name__ == "__main__":
    bot = TradingBot()
    
    # Run one cycle for testing
    bot.run_cycle()
    
    # For continuous operation, uncomment the following:
    # while True:
    #     bot.run_cycle()
    #     time.sleep(3600)  # Wait 1 hour between cycles 