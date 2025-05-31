#!/usr/bin/env python3
"""
AlpacaBot Main Entry Point for Replit Deployment

This file automatically starts the trading bot in dashboard mode for Replit hosting.
The dashboard will be accessible via the Replit web viewer.
"""

import os
import sys
from config import Config

def setup_environment():
    """Setup environment for Replit deployment"""
    print("🚀 Setting up AlpacaBot for Replit deployment...")
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Set Flask environment variables for production
    os.environ['FLASK_ENV'] = 'production'
    
    # Use Replit's default port if available
    if 'REPLIT_PORT' in os.environ:
        os.environ['FLASK_PORT'] = os.environ['REPLIT_PORT']
    
    print(f"📊 Configuration:")
    print(f"  - Paper Trading: {Config.PAPER_TRADING}")
    print(f"  - Drop Threshold: {Config.DROP_THRESHOLD*100}%")
    print(f"  - Min Stock Price: ${Config.MIN_STOCK_PRICE}")
    print(f"  - Caching: {'Enabled' if Config.ENABLE_CACHING else 'Disabled'}")
    print(f"  - Port: {Config.FLASK_PORT}")
    
    if not Config.API_KEY or not Config.SECRET_KEY:
        print("⚠️  WARNING: No Alpaca API credentials found.")
        print("   Set APCA_API_KEY_ID and APCA_API_SECRET_KEY in Replit Secrets")
        print("   The bot will run in limited mode until credentials are added.")
    else:
        print("✅ Alpaca API credentials detected")

def main():
    """Main entry point"""
    setup_environment()
    
    print("\n" + "="*60)
    print("🤖 AlpacaBot Trading Dashboard")
    print("="*60)
    print("📈 Starting web dashboard...")
    print("🌐 Dashboard will be available in the Replit web viewer")
    print("="*60)
    
    # Import and run dashboard
    try:
        from dashboard import app, socketio
        
        # Run with production settings for Replit
        socketio.run(
            app, 
            debug=False,  # Disable debug in production
            port=Config.FLASK_PORT, 
            host='0.0.0.0',
            allow_unsafe_werkzeug=True  # Required for Replit
        )
        
    except KeyboardInterrupt:
        print("\n🛑 AlpacaBot stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting AlpacaBot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 