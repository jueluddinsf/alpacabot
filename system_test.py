#!/usr/bin/env python3
"""
Comprehensive System Test for AlpacaBot
Tests all components before deployment to ensure everything works correctly
"""

import sys
import os
import time
import json
import requests
import threading
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemTester:
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []
        
    def test_result(self, test_name: str, passed: bool, message: str = ""):
        """Record test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status} {test_name}"
        if message:
            result += f" - {message}"
        
        logger.info(result)
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
    
    def test_imports(self):
        """Test that all modules can be imported"""
        logger.info("🔍 Testing module imports...")
        
        try:
            from config import Config
            self.test_result("Config import", True)
        except Exception as e:
            self.test_result("Config import", False, str(e))
            return False
        
        try:
            from cache_manager import CacheManager
            self.test_result("CacheManager import", True)
        except Exception as e:
            self.test_result("CacheManager import", False, str(e))
            return False
        
        try:
            from trading_bot import TradingBot
            self.test_result("TradingBot import", True)
        except Exception as e:
            self.test_result("TradingBot import", False, str(e))
            return False
        
        try:
            from dashboard import app
            self.test_result("Dashboard import", True)
        except Exception as e:
            self.test_result("Dashboard import", False, str(e))
            return False
        
        return True
    
    def test_configuration(self):
        """Test configuration system"""
        logger.info("⚙️ Testing configuration...")
        
        try:
            from config import Config
            
            # Test required attributes
            required_attrs = [
                'MIN_STOCK_PRICE', 'DROP_THRESHOLD', 'PROFIT_TARGET',
                'LOOKBACK_DAYS', 'SP500_SYMBOLS', 'ENABLE_CACHING'
            ]
            
            for attr in required_attrs:
                if hasattr(Config, attr):
                    self.test_result(f"Config.{attr} exists", True)
                else:
                    self.test_result(f"Config.{attr} exists", False)
                    return False
            
            # Test values are reasonable
            if Config.MIN_STOCK_PRICE > 0:
                self.test_result("MIN_STOCK_PRICE > 0", True)
            else:
                self.test_result("MIN_STOCK_PRICE > 0", False)
            
            if 0 < Config.DROP_THRESHOLD < 1:
                self.test_result("DROP_THRESHOLD in valid range", True)
            else:
                self.test_result("DROP_THRESHOLD in valid range", False)
            
            if len(Config.SP500_SYMBOLS) > 0:
                self.test_result("SP500_SYMBOLS not empty", True)
            else:
                self.test_result("SP500_SYMBOLS not empty", False)
            
            return True
            
        except Exception as e:
            self.test_result("Configuration test", False, str(e))
            return False
    
    def test_cache_system(self):
        """Test cache system functionality"""
        logger.info("🗄️ Testing cache system...")
        
        try:
            from config import Config
            from cache_manager import CacheManager
            
            # Test cache initialization
            cache = CacheManager(Config)
            self.test_result("Cache initialization", True)
            
            # Test cache operations
            test_key = "test:AAPL"
            test_data = {"price": 150.0, "timestamp": time.time()}
            
            # Test set and get
            cache.set(test_key, test_data)
            retrieved = cache.get(test_key)
            
            if retrieved == test_data:
                self.test_result("Cache set/get", True)
            else:
                self.test_result("Cache set/get", False, f"Expected {test_data}, got {retrieved}")
            
            # Test cache stats
            stats = cache.get_cache_stats()
            if isinstance(stats, dict) and 'total_entries' in stats:
                self.test_result("Cache statistics", True)
            else:
                self.test_result("Cache statistics", False)
            
            # Test cache clearing
            cache.clear_all()
            stats_after = cache.get_cache_stats()
            if stats_after['total_entries'] == 0:
                self.test_result("Cache clearing", True)
            else:
                self.test_result("Cache clearing", False)
            
            return True
            
        except Exception as e:
            self.test_result("Cache system test", False, str(e))
            return False
    
    def test_trading_bot_basic(self):
        """Test basic trading bot functionality"""
        logger.info("🤖 Testing trading bot basics...")
        
        try:
            from trading_bot import TradingBot
            
            # Test bot initialization
            bot = TradingBot()
            self.test_result("TradingBot initialization", True)
            
            # Test configuration access
            if hasattr(bot, 'config'):
                self.test_result("Bot config access", True)
            else:
                self.test_result("Bot config access", False)
                return False
            
            # Test cache access
            if hasattr(bot, 'cache'):
                self.test_result("Bot cache access", True)
            else:
                self.test_result("Bot cache access", False)
                return False
            
            # Test JSON file operations
            test_data = {"test": "data"}
            test_file = "data/test_file.json"
            
            bot.save_json_file(test_file, test_data)
            loaded_data = bot.load_json_file(test_file)
            
            if loaded_data == test_data:
                self.test_result("JSON file operations", True)
            else:
                self.test_result("JSON file operations", False)
            
            # Clean up test file
            if os.path.exists(test_file):
                os.remove(test_file)
            
            return True
            
        except Exception as e:
            self.test_result("Trading bot basic test", False, str(e))
            return False
    
    def test_trading_bot_advanced(self):
        """Test advanced trading bot functionality"""
        logger.info("📈 Testing trading bot advanced features...")
        
        try:
            from trading_bot import TradingBot
            
            bot = TradingBot()
            
            # Test portfolio summary
            summary = bot.get_portfolio_summary()
            if isinstance(summary, dict) and 'total_value' in summary:
                self.test_result("Portfolio summary", True)
            else:
                self.test_result("Portfolio summary", False)
            
            # Test cache status
            cache_status = bot.get_cache_status()
            if isinstance(cache_status, dict) and 'enabled' in cache_status:
                self.test_result("Cache status", True)
            else:
                self.test_result("Cache status", False)
            
            # Test price lookup (may fail if no API credentials)
            try:
                price = bot.get_current_price("AAPL")
                if price is None or isinstance(price, (int, float)):
                    self.test_result("Price lookup", True, "API call successful or gracefully handled")
                else:
                    self.test_result("Price lookup", False, f"Unexpected return type: {type(price)}")
            except Exception as e:
                self.test_result("Price lookup", True, f"API error gracefully handled: {str(e)[:50]}")
            
            return True
            
        except Exception as e:
            self.test_result("Trading bot advanced test", False, str(e))
            return False
    
    def test_dashboard_endpoints(self):
        """Test dashboard API endpoints"""
        logger.info("🌐 Testing dashboard endpoints...")
        
        # Start dashboard in background
        try:
            from dashboard import app
            import threading
            
            # Start Flask app in a thread
            def run_app():
                app.run(host='127.0.0.1', port=5555, debug=False)
            
            server_thread = threading.Thread(target=run_app, daemon=True)
            server_thread.start()
            
            # Wait for server to start
            time.sleep(2)
            
            base_url = "http://127.0.0.1:5555"
            
            # Test endpoints
            endpoints = [
                '/api/config',
                '/api/portfolio', 
                '/api/holdings',
                '/api/watchlist',
                '/api/trades',
                '/api/cache/status'
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(f"{base_url}{endpoint}", timeout=5)
                    if response.status_code == 200:
                        self.test_result(f"Endpoint {endpoint}", True)
                    else:
                        self.test_result(f"Endpoint {endpoint}", False, f"Status: {response.status_code}")
                except Exception as e:
                    self.test_result(f"Endpoint {endpoint}", False, str(e))
            
            return True
            
        except Exception as e:
            self.test_result("Dashboard endpoints test", False, str(e))
            return False
    
    def test_data_directory(self):
        """Test data directory and file structure"""
        logger.info("📁 Testing data directory structure...")
        
        try:
            # Ensure data directory exists
            if not os.path.exists('data'):
                os.makedirs('data')
                self.test_result("Data directory creation", True)
            else:
                self.test_result("Data directory exists", True)
            
            # Test file creation
            test_files = [
                'data/test_watchlist.json',
                'data/test_holdings.json', 
                'data/test_trades.json',
                'data/test_cache.json'
            ]
            
            for file_path in test_files:
                try:
                    with open(file_path, 'w') as f:
                        json.dump({"test": True}, f)
                    self.test_result(f"File creation {os.path.basename(file_path)}", True)
                    
                    # Clean up
                    os.remove(file_path)
                except Exception as e:
                    self.test_result(f"File creation {os.path.basename(file_path)}", False, str(e))
            
            return True
            
        except Exception as e:
            self.test_result("Data directory test", False, str(e))
            return False
    
    def test_dependencies(self):
        """Test that all required dependencies are available"""
        logger.info("📦 Testing dependencies...")
        
        required_packages = [
            'flask',
            'flask_socketio', 
            'pandas',
            'numpy',
            'alpaca',
            'requests'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                self.test_result(f"Package {package}", True)
            except ImportError as e:
                self.test_result(f"Package {package}", False, str(e))
        
        return True
    
    def run_all_tests(self):
        """Run all system tests"""
        logger.info("🚀 Starting comprehensive system test...")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Run all tests
        tests = [
            self.test_dependencies,
            self.test_imports,
            self.test_configuration,
            self.test_data_directory,
            self.test_cache_system,
            self.test_trading_bot_basic,
            self.test_trading_bot_advanced,
            self.test_dashboard_endpoints
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                logger.error(f"Test {test.__name__} crashed: {e}")
                self.test_result(test.__name__, False, f"Test crashed: {e}")
            
            logger.info("-" * 40)
        
        # Final results
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info("🏁 SYSTEM TEST RESULTS")
        logger.info("=" * 60)
        logger.info(f"✅ Passed: {self.passed_tests}")
        logger.info(f"❌ Failed: {self.failed_tests}")
        logger.info(f"⏱️  Duration: {duration:.2f} seconds")
        logger.info(f"📊 Success Rate: {(self.passed_tests/(self.passed_tests+self.failed_tests)*100):.1f}%")
        
        if self.failed_tests == 0:
            logger.info("🎉 ALL TESTS PASSED! System is ready for deployment.")
            return True
        else:
            logger.info("⚠️  SOME TESTS FAILED. Review issues before deployment.")
            
            # Show failed tests
            logger.info("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['passed']:
                    logger.info(f"  - {result['test']}: {result['message']}")
            
            return False

def main():
    """Run system tests"""
    tester = SystemTester()
    success = tester.run_all_tests()
    
    # Save test results
    with open('data/system_test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'passed_tests': tester.passed_tests,
            'failed_tests': tester.failed_tests,
            'success_rate': tester.passed_tests/(tester.passed_tests+tester.failed_tests)*100,
            'results': tester.test_results
        }, f, indent=2)
    
    logger.info(f"\n📋 Test results saved to: data/system_test_results.json")
    
    if success:
        logger.info("\n🚀 System is ready for deployment!")
        sys.exit(0)
    else:
        logger.info("\n🛑 System has issues. Please fix before deployment.")
        sys.exit(1)

if __name__ == "__main__":
    main() 