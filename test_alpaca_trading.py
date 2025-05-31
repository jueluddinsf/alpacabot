#!/usr/bin/env python3
"""
Test Alpaca Trading API functionality
"""
from alpaca.trading.client import TradingClient
from config import Config

def test_alpaca_trading():
    """Test Alpaca Trading API access"""
    config = Config()
    
    print(f"API Key exists: {bool(config.API_KEY)}")
    print(f"Secret Key exists: {bool(config.SECRET_KEY)}")
    print(f"Paper Trading: {config.PAPER_TRADING}")
    
    if not config.API_KEY or not config.SECRET_KEY:
        print("❌ No API credentials found")
        return
    
    try:
        # Initialize trading client
        trading_client = TradingClient(
            config.API_KEY, 
            config.SECRET_KEY, 
            paper=config.PAPER_TRADING
        )
        print("✅ Trading client initialized")
        
        # Test account access
        print("\n📊 Testing account access...")
        account = trading_client.get_account()
        print(f"✅ Account ID: {account.id}")
        print(f"💰 Buying Power: ${float(account.buying_power):,.2f}")
        print(f"💼 Portfolio Value: ${float(account.portfolio_value):,.2f}")
        print(f"📈 Day Trade Buying Power: ${float(account.daytrading_buying_power):,.2f}")
        print(f"🔒 Pattern Day Trader: {account.pattern_day_trader}")
        
        # Test positions
        print("\n📋 Current positions...")
        positions = trading_client.get_all_positions()
        if positions:
            for pos in positions:
                print(f"  {pos.symbol}: {pos.qty} shares @ ${pos.avg_cost} = ${float(pos.market_value):,.2f}")
        else:
            print("  No current positions")
        
        # Test orders
        print("\n📝 Recent orders...")
        orders = trading_client.get_orders(limit=5)
        if orders:
            for order in orders:
                print(f"  {order.symbol}: {order.side} {order.qty} @ {order.order_type} - {order.status}")
        else:
            print("  No recent orders")
            
        print("\n✅ Trading API access confirmed!")
        return True
            
    except Exception as e:
        print(f"❌ Trading API Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_alpaca_trading() 