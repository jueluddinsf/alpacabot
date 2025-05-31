from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import json
from datetime import datetime
from config import Config
import threading
import time

app = Flask(__name__)
app.secret_key = Config.FLASK_SECRET_KEY
socketio = SocketIO(app, cors_allowed_origins="*")

# Lazy-load the bot to avoid import issues
_bot = None

def get_bot():
    """Get or create the trading bot instance"""
    global _bot
    if _bot is None:
        from trading_bot import TradingBot
        _bot = TradingBot()
    return _bot

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/portfolio')
def get_portfolio():
    """Get portfolio summary"""
    try:
        bot = get_bot()
        summary = bot.get_portfolio_summary()
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/holdings')
def get_holdings():
    """Get current holdings with real-time prices"""
    try:
        bot = get_bot()
        holdings = bot.load_json_file(bot.config.HOLDINGS_FILE)
        enriched_holdings = []
        
        for symbol, info in holdings.items():
            current_price = bot.get_current_price(symbol)
            if current_price:
                profit_loss = (current_price - info["buy_price"]) * info["quantity"]
                profit_loss_pct = (current_price - info["buy_price"]) / info["buy_price"] * 100
                
                enriched_holdings.append({
                    "symbol": symbol,
                    "quantity": info["quantity"],
                    "buy_price": info["buy_price"],
                    "current_price": current_price,
                    "profit_loss": profit_loss,
                    "profit_loss_pct": profit_loss_pct,
                    "buy_date": info["buy_date"],
                    "market_value": current_price * info["quantity"]
                })
        
        return jsonify(enriched_holdings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/watchlist')
def get_watchlist():
    """Get current watchlist with real-time prices"""
    try:
        bot = get_bot()
        watchlist = bot.load_json_file(bot.config.WATCHLIST_FILE)
        enriched_watchlist = []
        
        for symbol, info in watchlist.items():
            current_price = bot.get_current_price(symbol)
            if current_price:
                drop_from_detected = (info["drop_detected_price"] - current_price) / info["drop_detected_price"] * 100
                
                enriched_watchlist.append({
                    "symbol": symbol,
                    "added_date": info["added_date"],
                    "drop_detected_price": info["drop_detected_price"],
                    "current_price": current_price,
                    "additional_drop_pct": drop_from_detected,
                    "status": info["status"]
                })
        
        return jsonify(enriched_watchlist)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/trades')
def get_trades():
    """Get trade history"""
    try:
        bot = get_bot()
        trades_data = bot.load_json_file(bot.config.TRADES_FILE)
        trades = trades_data.get('trades', [])
        
        # Sort by timestamp, most recent first
        trades.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify(trades)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/run-cycle', methods=['POST'])
def run_cycle():
    """Manually trigger a trading cycle"""
    try:
        bot = get_bot()
        bot.run_cycle()
        return jsonify({"status": "success", "message": "Trading cycle completed"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/config')
def get_config():
    """Get current configuration"""
    bot = get_bot()
    return jsonify({
        "min_stock_price": bot.config.MIN_STOCK_PRICE,
        "drop_threshold": bot.config.DROP_THRESHOLD * 100,
        "profit_target": bot.config.PROFIT_TARGET * 100,
        "lookback_days": bot.config.LOOKBACK_DAYS,
        "paper_trading": bot.config.PAPER_TRADING,
        "total_symbols": len(bot.config.SP500_SYMBOLS),
        "caching_enabled": bot.config.ENABLE_CACHING
    })

@app.route('/api/cache/status')
def get_cache_status():
    """Get cache statistics and status"""
    try:
        bot = get_bot()
        cache_status = bot.get_cache_status()
        return jsonify(cache_status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear cache (all or specific symbol)"""
    try:
        bot = get_bot()
        data = request.get_json() or {}
        symbol = data.get('symbol')
        
        bot.clear_cache(symbol)
        
        if symbol:
            message = f"Cache cleared for {symbol}"
        else:
            message = "All cache cleared"
            
        return jsonify({"status": "success", "message": message})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def run_scheduled_cycle():
    """Run trading cycle every hour and emit updates via WebSocket"""
    while True:
        try:
            bot = get_bot()
            bot.run_cycle()
            
            # Emit updates to connected clients
            portfolio = bot.get_portfolio_summary()
            socketio.emit('portfolio_update', portfolio)
            
            time.sleep(3600)  # Wait 1 hour
        except Exception as e:
            print(f"Error in scheduled cycle: {e}")
            time.sleep(60)  # Wait 1 minute before retrying

if __name__ == '__main__':
    # Start background trading cycle in a separate thread
    # trading_thread = threading.Thread(target=run_scheduled_cycle, daemon=True)
    # trading_thread.start()
    
    # For development, comment out the automatic trading thread
    print("Dashboard starting in development mode...")
    print("Automatic trading disabled. Use 'Run Cycle' button to manually trigger trades.")
    
    socketio.run(app, debug=Config.FLASK_DEBUG, port=Config.FLASK_PORT, host='0.0.0.0') 