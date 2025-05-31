import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self, config, cache_file: str = None):
        self.config = config
        self.cache_file = cache_file or config.CACHE_FILE
        self.cache = {}
        self.enabled = config.ENABLE_CACHING
        
        if self.enabled:
            self.load_cache()
            
            # Cache expiry times from config
            self.PRICE_CACHE_EXPIRY = config.CACHE_PRICE_EXPIRY
            self.HISTORY_CACHE_EXPIRY = config.CACHE_HISTORY_EXPIRY
            self.FILTER_CACHE_EXPIRY = config.CACHE_FILTER_EXPIRY
            self.MARKET_CLOSED_MULTIPLIER = config.CACHE_MARKET_CLOSED_MULTIPLIER
            
            logger.info(f"🗄️ Cache manager initialized (enabled: {self.enabled})")
            logger.info(f"⏰ Cache expiry: Price {self.PRICE_CACHE_EXPIRY}s, History {self.HISTORY_CACHE_EXPIRY}s, Filter {self.FILTER_CACHE_EXPIRY}s")
        else:
            logger.info("🚫 Cache manager disabled")
    
    def is_market_hours(self) -> bool:
        """Check if market is currently open (simplified US market hours)"""
        now = datetime.now()
        # Market is open Monday-Friday, 9:30 AM - 4:00 PM ET
        # This is a simplified check - you might want to use a proper market hours library
        if now.weekday() >= 5:  # Weekend
            return False
        
        # Rough market hours check (doesn't account for holidays/timezone perfectly)
        hour = now.hour
        return 9 <= hour < 16
    
    def get_cache_key(self, prefix: str, symbol: str = "", params: str = "") -> str:
        """Generate a cache key"""
        return f"{prefix}:{symbol}:{params}".strip(":")
    
    def is_expired(self, timestamp: float, cache_type: str) -> bool:
        """Check if cache entry is expired"""
        if not self.enabled:
            return True
            
        now = time.time()
        
        if cache_type == "price":
            expiry = self.PRICE_CACHE_EXPIRY
        elif cache_type == "history":
            expiry = self.HISTORY_CACHE_EXPIRY
        elif cache_type == "filter":
            expiry = self.FILTER_CACHE_EXPIRY
        else:
            expiry = self.PRICE_CACHE_EXPIRY
        
        # Extend cache time when market is closed
        if not self.is_market_hours():
            expiry *= self.MARKET_CLOSED_MULTIPLIER
        
        return (now - timestamp) > expiry
    
    def get(self, key: str, cache_type: str = "price") -> Optional[Any]:
        """Get item from cache if not expired"""
        if not self.enabled:
            return None
            
        if key in self.cache:
            entry = self.cache[key]
            if not self.is_expired(entry['timestamp'], cache_type):
                logger.debug(f"📋 Cache HIT: {key}")
                return entry['data']
            else:
                logger.debug(f"⏰ Cache EXPIRED: {key}")
                del self.cache[key]
        
        logger.debug(f"❌ Cache MISS: {key}")
        return None
    
    def set(self, key: str, data: Any) -> None:
        """Store item in cache"""
        if not self.enabled:
            return
            
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
        logger.debug(f"💾 Cache SET: {key}")
        
        # Periodically save to disk (every 10 entries)
        if len(self.cache) % 10 == 0:
            self.save_cache()
    
    def clear_expired(self) -> int:
        """Clear all expired entries and return count cleared"""
        cleared = 0
        expired_keys = []
        
        for key, entry in self.cache.items():
            # Determine cache type from key prefix
            cache_type = "price"
            if key.startswith("history:"):
                cache_type = "history"
            elif key.startswith("filter:"):
                cache_type = "filter"
            
            if self.is_expired(entry['timestamp'], cache_type):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
            cleared += 1
        
        if cleared > 0:
            logger.info(f"🧹 Cleared {cleared} expired cache entries")
        
        return cleared
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self.cache)
        
        # Count by type
        price_entries = len([k for k in self.cache.keys() if k.startswith("price:")])
        history_entries = len([k for k in self.cache.keys() if k.startswith("history:")])
        filter_entries = len([k for k in self.cache.keys() if k.startswith("filter:")])
        other_entries = total_entries - price_entries - history_entries - filter_entries
        
        # Calculate cache size (rough estimate)
        cache_size_mb = len(str(self.cache)) / (1024 * 1024)
        
        return {
            "total_entries": total_entries,
            "price_entries": price_entries,
            "history_entries": history_entries,
            "filter_entries": filter_entries,
            "other_entries": other_entries,
            "cache_size_mb": round(cache_size_mb, 2),
            "market_open": self.is_market_hours()
        }
    
    def load_cache(self) -> None:
        """Load cache from disk"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
                logger.info(f"📂 Loaded {len(self.cache)} cache entries from disk")
            else:
                self.cache = {}
                # Ensure data directory exists
                os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        except Exception as e:
            logger.warning(f"⚠️ Error loading cache: {e}")
            self.cache = {}
    
    def save_cache(self) -> None:
        """Save cache to disk"""
        if not self.enabled:
            return
            
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
            logger.debug(f"💾 Saved {len(self.cache)} cache entries to disk")
        except Exception as e:
            logger.warning(f"⚠️ Error saving cache: {e}")
    
    def clear_all(self) -> None:
        """Clear all cache entries"""
        count = len(self.cache)
        self.cache = {}
        self.save_cache()
        logger.info(f"🗑️ Cleared all {count} cache entries")
    
    def clear_symbol(self, symbol: str) -> None:
        """Clear all cache entries for a specific symbol"""
        cleared = 0
        keys_to_remove = [k for k in self.cache.keys() if symbol in k]
        
        for key in keys_to_remove:
            del self.cache[key]
            cleared += 1
        
        if cleared > 0:
            logger.info(f"🗑️ Cleared {cleared} cache entries for {symbol}")
    
    def __del__(self):
        """Save cache when object is destroyed"""
        try:
            self.save_cache()
        except:
            pass  # Ignore errors during cleanup 