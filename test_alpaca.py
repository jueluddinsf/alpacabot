#!/usr/bin/env python3
"""
Test Alpaca API functionality directly
"""
import os
from datetime import datetime, timedelta
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from config import Config

def test_alpaca_connection():
    """Test direct Alpaca API connection"""
    config = Config()
    
    print(f"API Key exists: {bool(config.API_KEY)}")
    print(f"Secret Key exists: {bool(config.SECRET_KEY)}")
    
    if not config.API_KEY or not config.SECRET_KEY:
        print("❌ No API credentials found")
        return
    
    try:
        # Initialize data client
        data_client = StockHistoricalDataClient(
            config.API_KEY, 
            config.SECRET_KEY
        )
        print("✅ Data client initialized")
        
        # Test with a simple symbol
        symbol = "AAPL"
        end_time = datetime.now()
        start_time = end_time - timedelta(days=10)
        
        print(f"📊 Testing data fetch for {symbol}...")
        print(f"Date range: {start_time.date()} to {end_time.date()}")
        
        bars = data_client.get_stock_bars(StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=start_time,
            end=end_time
        ))
        
        df = bars.df
        print(f"✅ Got {len(df)} bars of data")
        
        if not df.empty:
            latest_price = float(df['close'].iloc[-1])
            print(f"💰 Latest {symbol} price: ${latest_price:.2f}")
            print(f"📈 Data columns: {list(df.columns)}")
            print(f"📅 Date range in data: {df.index[0]} to {df.index[-1]}")
        else:
            print("❌ No data returned")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_alpaca_connection() 