import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Alpaca API Configuration
    API_KEY = os.getenv("APCA_API_KEY_ID")
    SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
    PAPER_TRADING = os.getenv("PAPER_TRADING", "True").lower() == "true"
    
    # Flask Configuration
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-key-change-in-production")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
    
    # Trading Strategy Parameters
    MIN_STOCK_PRICE = 5.0  # Minimum stock price to consider ($5+ avoids penny stocks)
    DROP_THRESHOLD = 0.30  # 30% drop to add to watchlist
    PROFIT_TARGET = 0.10   # 10% profit to sell
    LOOKBACK_DAYS = 7      # Days to look back for drop calculation
    
    # Cache Configuration - Optimized for 5-minute scanning
    ENABLE_CACHING = os.getenv("ENABLE_CACHING", "True").lower() == "true"
    CACHE_PRICE_EXPIRY = int(os.getenv("CACHE_PRICE_EXPIRY", 120))  # 2 minutes (shorter for 5-min scans)
    CACHE_HISTORY_EXPIRY = int(os.getenv("CACHE_HISTORY_EXPIRY", 1800))  # 30 minutes
    CACHE_FILTER_EXPIRY = int(os.getenv("CACHE_FILTER_EXPIRY", 600))  # 10 minutes (shorter for 5-min scans)
    CACHE_MARKET_CLOSED_MULTIPLIER = int(os.getenv("CACHE_MARKET_CLOSED_MULTIPLIER", 6))  # 6x longer when market closed
    
    # File paths
    WATCHLIST_FILE = 'data/watchlist.json'
    HOLDINGS_FILE = 'data/holdings.json'
    TRADES_FILE = 'data/trades.json'
    CACHE_FILE = 'data/cache.json'
    
    # Extended S&P 500 symbols for broader scanning
    SP500_SYMBOLS = [
        # Major Tech
        'AAPL', 'MSFT', 'NVDA', 'GOOGL', 'GOOG', 'AMZN', 'META', 'TSLA', 'AVGO', 'ORCL',
        'CRM', 'NFLX', 'ADBE', 'AMD', 'INTC', 'CSCO', 'QCOM', 'TXN', 'MU', 'AMAT',
        
        # Financial
        'BRK.B', 'JPM', 'V', 'MA', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'SPGI', 'BLK',
        'SCHW', 'CB', 'MMC', 'PGR', 'AON', 'CME', 'ICE', 'COF',
        
        # Healthcare
        'UNH', 'JNJ', 'PFE', 'ABT', 'TMO', 'MRK', 'DHR', 'BMY', 'ABBV', 'CVS',
        'MDT', 'CI', 'GILD', 'ISRG', 'REGN', 'VRTX', 'ZTS', 'DXCM', 'HUM', 'BIIB',
        
        # Consumer
        'AMZN', 'TSLA', 'HD', 'MCD', 'DIS', 'NKE', 'SBUX', 'TGT', 'LOW', 'TJX',
        'COST', 'WMT', 'PG', 'KO', 'PEP', 'PM', 'MO', 'CL', 'KMB', 'GIS',
        
        # Industrial  
        'CAT', 'BA', 'UNP', 'HON', 'UPS', 'LMT', 'RTX', 'GE', 'MMM', 'DE',
        'NOC', 'FDX', 'WM', 'EMR', 'ETN', 'PH', 'ITW', 'CSX', 'NSC', 'GD',
        
        # Energy
        'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PSX', 'VLO', 'MPC', 'OXY', 'BKR',
        'HAL', 'DVN', 'FANG', 'EQT', 'APA', 'MRO', 'HES', 'CTRA', 'WMB', 'KMI',
        
        # Materials
        'LIN', 'APD', 'ECL', 'SHW', 'FCX', 'NEM', 'DOW', 'DD', 'PPG', 'IFF',
        'ALB', 'CE', 'FMC', 'NUE', 'VMC', 'MLM', 'PKG', 'AMCR', 'IP', 'CF',
        
        # Utilities
        'NEE', 'SO', 'DUK', 'AEP', 'SRE', 'D', 'PEG', 'EXC', 'XEL', 'WEC',
        'ED', 'EIX', 'ETR', 'ES', 'FE', 'AEE', 'DTE', 'PPL', 'CMS', 'NI',
        
        # Real Estate
        'PLD', 'AMT', 'CCI', 'EQIX', 'PSA', 'SPG', 'O', 'SBAC', 'DLR', 'AVB',
        'EQR', 'WELL', 'MAA', 'ARE', 'PEAK', 'ESS', 'VTR', 'UDR', 'CPT', 'REG',
        
        # Telecom
        'VZ', 'T', 'TMUS', 'CHTR', 'CMCSA', 'DIS', 'NFLX', 'FOXA', 'FOX', 'PARA',
        
        # Additional High-Volume Stocks
        'ROKU', 'SQ', 'PYPL', 'SHOP', 'SNAP', 'TWTR', 'UBER', 'LYFT', 'SPOT', 'ZM',
        'DOCU', 'CRM', 'WDAY', 'SNOW', 'PLTR', 'COIN', 'RBLX', 'U', 'NET', 'DDOG',
        
        # More Traditional Companies
        'IBM', 'ORCL', 'HPQ', 'DELL', 'CRM', 'NOW', 'PANW', 'CRWD', 'ZS', 'OKTA',
        'MRVL', 'LRCX', 'KLAC', 'CDNS', 'SNPS', 'FTNT', 'INTU', 'CTSH', 'GLW', 'HPE',
        
        # Biotech & Pharma  
        'MRNA', 'BNTX', 'NVAX', 'PFE', 'JNJ', 'ABBV', 'GILD', 'AMGN', 'CELG', 'BIIB',
        'REGN', 'VRTX', 'ILMN', 'BMRN', 'ALXN', 'INCY', 'EXAS', 'MYGN', 'TECH', 'SGEN',
        
        # Energy & Commodities
        'XOM', 'CVX', 'COP', 'EOG', 'PXD', 'FANG', 'DVN', 'APA', 'MRO', 'OVV',
        'CLR', 'CTRA', 'SM', 'MGY', 'RRC', 'AR', 'WLL', 'NOG', 'MTDR', 'VNOM',
        
        # REITs
        'O', 'STOR', 'WPC', 'STAG', 'ADC', 'LTC', 'OHI', 'MPW', 'GOOD', 'GMRE',
        
        # Small/Mid Cap with volatility
        'AMC', 'GME', 'BB', 'NOK', 'CLOV', 'WISH', 'SOFI', 'HOOD', 'OPEN', 'UPST'
    ] 