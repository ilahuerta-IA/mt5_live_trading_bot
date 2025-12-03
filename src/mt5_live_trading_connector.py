"""MT5 Live Trading Connector - Sunrise Strategy Integration
=========================================================
DEMO FIRST: This script connects Python strategies to MetaTrader 5 for live trading.
ALWAYS test thoroughly on DEMO account before switching to real money.

This connector bridges the gap between Backtrader strategy signals and MT5 execution:
1. Connects to MT5 terminal
2. Monitors strategy signals 
3. Executes trades via MT5 API
4. Manages risk and position sizing
5. Provides comprehensive logging and monitoring

SAFETY FEATURES:
- Demo account enforcement (must manually enable real trading)
- Position size limits and risk management
- Comprehensive error handling and logging
- Manual trade confirmation modes
- Emergency stop functionality

REQUIREMENTS:
- MetaTrader 5 terminal installed and running
- MT5 Python package: pip install MetaTrader5
- Valid MT5 demo/live account
- Strategy classes with signal generation

DISCLAIMER
----------
Live trading involves substantial risk of loss. This is educational code.
Test extensively on demo accounts. Never risk more than you can afford to lose.
Past performance does not guarantee future results.
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging
import json
from pathlib import Path
import sys
from typing import Dict, Optional, Tuple, List
import threading
import signal
import os

# Add strategies directory to path for importing our strategies
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
STRATEGIES_DIR = PROJECT_ROOT / "strategies"

# Path to local strategies (completely independent from quant_bot_project)
LOCAL_STRATEGIES_DIR = PROJECT_ROOT / "strategies"

# Add local strategies directory to Python path
sys.path.insert(0, str(LOCAL_STRATEGIES_DIR))

# Import our trading strategies from local strategies folder
# Verify path exists before importing
if not LOCAL_STRATEGIES_DIR.exists():
    print(f"Warning: Local strategies directory not found: {LOCAL_STRATEGIES_DIR}")
    print("Please ensure strategies are copied to the local strategies folder")

# Strategy imports with comprehensive error handling
strategy_imports = {}
strategies_to_import = [
    ('sunrise_ogle_eurusd', 'SunriseOgle', 'EURUSD'),
    ('sunrise_ogle_gbpusd', 'SunriseOgle', 'GBPUSD'),
    ('sunrise_ogle_xauusd', 'SunriseOgle', 'XAUUSD'),
    ('sunrise_ogle_audusd', 'SunriseOgle', 'AUDUSD'),
    ('sunrise_ogle_xagusd', 'SunriseOgle', 'XAGUSD'),
    ('sunrise_ogle_usdchf', 'SunriseOgle', 'USDCHF'),
    ('sunrise_ogle_eurjpy', 'SunriseOgle', 'EURJPY'),
    ('sunrise_ogle_usdjpy', 'SunriseOgleUSDJPY', 'USDJPY'),
]

for module_name, class_name, symbol in strategies_to_import:
    try:
        module = __import__(module_name)
        strategy_class = getattr(module, class_name)
        strategy_imports[symbol] = strategy_class
        print(f"✅ {symbol}: Strategy imported successfully")
    except ImportError as e:
        print(f"⚠️  {symbol}: Could not import strategy from {module_name}: {e}")
    except AttributeError as e:
        print(f"⚠️  {symbol}: Could not find class {class_name} in {module_name}: {e}")
    except Exception as e:
        print(f"❌ {symbol}: Unexpected error importing strategy: {e}")

print(f"Successfully imported {len(strategy_imports)} strategy classes")

# =============================================================
# CONFIGURATION PARAMETERS
# =============================================================

# === SAFETY SETTINGS ===
DEMO_MODE_ONLY = True                    # SAFETY: Set False only for real trading
MAX_RISK_PER_TRADE = 0.01               # Maximum 1% risk per trade
MAX_DAILY_TRADES = 10                   # Maximum trades per day
MAX_POSITION_SIZE = 0.1                 # Maximum lot size (0.1 = 0.1 standard lots)
ENABLE_TRADE_CONFIRMATION = True        # Require manual confirmation for each trade

# === MT5 CONNECTION SETTINGS ===
MT5_LOGIN = None                         # Your MT5 account number (set via config file)
MT5_PASSWORD = None                      # Your MT5 password (set via config file)
MT5_SERVER = None                        # Your MT5 server (set via config file)
MT5_TIMEOUT = 60000                      # Connection timeout in milliseconds

# === TRADING SETTINGS ===
SYMBOLS_TO_TRADE = ['EURUSD']            # Start with single symbol for testing
DEFAULT_TIMEFRAME = mt5.TIMEFRAME_M5     # 5-minute timeframe
SIGNAL_CHECK_INTERVAL = 30               # Check for signals every 30 seconds
MAX_SPREAD_PIPS = 3                      # Maximum allowed spread in pips

# === LOGGING SETTINGS ===
LOG_LEVEL = logging.INFO
LOG_FILE = PROJECT_ROOT / 'logs' / 'mt5_trading.log'
TRADE_LOG_FILE = PROJECT_ROOT / 'logs' / 'mt5_trades.log'

# === CONFIGURATION FILE ===
CONFIG_FILE = PROJECT_ROOT / 'config' / 'mt5_credentials.json'

# =============================================================
# UTILITY CLASSES
# =============================================================

class TradingLogger:
    """Enhanced logging for MT5 trading operations"""
    
    def __init__(self, log_file: Path, trade_log_file: Path):
        self.log_file = log_file
        self.trade_log_file = trade_log_file
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        # Create log directories if they don't exist
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.trade_log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Main logger
        self.logger = logging.getLogger('MT5Trader')
        self.logger.setLevel(LOG_LEVEL)
        
        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(LOG_LEVEL)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(LOG_LEVEL)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
        
        # Trade-specific logger
        self.trade_logger = logging.getLogger('MT5Trades')
        self.trade_logger.setLevel(logging.INFO)
        
        trade_handler = logging.FileHandler(self.trade_log_file)
        trade_handler.setFormatter(formatter)
        if not self.trade_logger.handlers:
            self.trade_logger.addHandler(trade_handler)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def log_trade(self, trade_data: Dict):
        """Log trade-specific information"""
        self.trade_logger.info(f"TRADE: {json.dumps(trade_data, default=str)}")

class MT5Connection:
    """Handles MT5 connection and basic operations"""
    
    def __init__(self, logger: TradingLogger):
        self.logger = logger
        self.connected = False
        self.account_info = None
        
    def load_credentials(self) -> bool:
        """Load MT5 credentials from config file"""
        try:
            if not CONFIG_FILE.exists():
                self.logger.error(f"Config file not found: {CONFIG_FILE}")
                self.create_sample_config()
                return False
            
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            
            global MT5_LOGIN, MT5_PASSWORD, MT5_SERVER
            MT5_LOGIN = config.get('login')
            MT5_PASSWORD = config.get('password')
            MT5_SERVER = config.get('server')
            
            if not all([MT5_LOGIN, MT5_PASSWORD, MT5_SERVER]):
                self.logger.error("Incomplete credentials in config file")
                return False
            
            self.logger.info("Credentials loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading credentials: {e}")
            return False
    
    def create_sample_config(self):
        """Create sample configuration file"""
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        sample_config = {
            "login": "YOUR_MT5_ACCOUNT_NUMBER",
            "password": "YOUR_MT5_PASSWORD", 
            "server": "YOUR_BROKER_SERVER",
            "note": "Replace with your actual MT5 credentials"
        }
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(sample_config, f, indent=4)
        
        self.logger.info(f"Sample config created at: {CONFIG_FILE}")
        self.logger.info("Please update with your MT5 credentials")
    
    def connect(self) -> bool:
        """Connect to MT5 terminal"""
        try:
            # Load credentials
            if not self.load_credentials():
                return False
            
            # Initialize MT5
            if not mt5.initialize():
                self.logger.error(f"MT5 initialization failed: {mt5.last_error()}")
                return False
            
            # Login to account
            if not mt5.login(MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER):
                self.logger.error(f"MT5 login failed: {mt5.last_error()}")
                mt5.shutdown()
                return False
            
            # Get account info
            self.account_info = mt5.account_info()
            if self.account_info is None:
                self.logger.error("Failed to get account info")
                return False
            
            self.connected = True
            self.logger.info(f"Connected to MT5 - Account: {self.account_info.login}")
            self.logger.info(f"Account Balance: {self.account_info.balance}")
            self.logger.info(f"Account Currency: {self.account_info.currency}")
            
            # Safety check for demo account
            if DEMO_MODE_ONLY and self.account_info.trade_mode != mt5.ACCOUNT_TRADE_MODE_DEMO:
                self.logger.error("SAFETY: Demo mode enforced but connected to real account!")
                self.disconnect()
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MT5"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            self.logger.info("Disconnected from MT5")
    
    def is_market_open(self, symbol: str) -> bool:
        """Check if market is open for trading"""
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return False
            
            # Check if symbol is available for trading
            if not symbol_info.visible:
                # Try to enable symbol
                if not mt5.symbol_select(symbol, True):
                    return False
            
            # Get current server time
            server_time = datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)
            
            # Check trading session (basic check - can be enhanced)
            current_hour = server_time.hour
            
            # Forex markets typically trade 24/5, avoid weekends
            weekday = server_time.weekday()
            if weekday >= 5:  # Saturday = 5, Sunday = 6
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking market status for {symbol}: {e}")
            return False

class PositionManager:
    """Manages positions and risk for live trading"""
    
    def __init__(self, logger: TradingLogger):
        self.logger = logger
        self.daily_trades = 0
        self.last_trade_date = None
        
    def reset_daily_counter(self):
        """Reset daily trade counter"""
        current_date = datetime.now().date()
        if self.last_trade_date != current_date:
            self.daily_trades = 0
            self.last_trade_date = current_date
            self.logger.info("Daily trade counter reset")
    
    def can_open_position(self, symbol: str) -> Tuple[bool, str]:
        """Check if we can open a new position"""
        self.reset_daily_counter()
        
        # Check daily trade limit
        if self.daily_trades >= MAX_DAILY_TRADES:
            return False, f"Daily trade limit reached: {self.daily_trades}/{MAX_DAILY_TRADES}"
        
        # Check existing positions
        positions = mt5.positions_get(symbol=symbol)
        if positions is not None and len(positions) > 0:
            return False, f"Position already exists for {symbol}"
        
        # Check spread
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return False, f"Cannot get tick data for {symbol}"
        
        symbol_info = mt5.symbol_info(symbol)
        spread_pips = (tick.ask - tick.bid) / symbol_info.point / 10
        
        if spread_pips > MAX_SPREAD_PIPS:
            return False, f"Spread too high: {spread_pips:.1f} pips > {MAX_SPREAD_PIPS}"
        
        return True, "OK"
    
    def calculate_position_size(self, symbol: str, risk_amount: float, stop_loss_pips: float) -> float:
        """Calculate position size based on risk management"""
        try:
            symbol_info = mt5.symbol_info(symbol)
            account_info = mt5.account_info()
            
            if symbol_info is None or account_info is None:
                return 0.0
            
            # Calculate pip value for 1 lot
            if symbol.endswith('JPY'):
                pip_value = symbol_info.trade_contract_size * 0.01
            else:
                pip_value = symbol_info.trade_contract_size * 0.0001
            
            # Convert pip value to account currency if needed
            if account_info.currency != 'USD':
                # Simplified conversion - in real implementation, use proper currency conversion
                pass
            
            # Calculate lot size
            lot_size = risk_amount / (stop_loss_pips * pip_value)
            
            # Apply maximum position size limit
            lot_size = min(lot_size, MAX_POSITION_SIZE)
            
            # Round to broker's lot step
            lot_step = symbol_info.volume_step
            lot_size = round(lot_size / lot_step) * lot_step
            
            # Ensure minimum lot size
            lot_size = max(lot_size, symbol_info.volume_min)
            
            return lot_size
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return 0.0

# =============================================================
# MAIN TRADING ENGINE
# =============================================================

class SunriseMT5Trader:
    """Main trading engine that connects Sunrise strategies to MT5"""
    
    def __init__(self):
        self.logger = TradingLogger(LOG_FILE, TRADE_LOG_FILE)
        self.mt5_connection = MT5Connection(self.logger)
        self.position_manager = PositionManager(self.logger)
        self.running = False
        self.strategies = {}
        
        # Emergency stop flag
        self.emergency_stop = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.emergency_stop = True
        self.stop()
    
    def initialize(self) -> bool:
        """Initialize the trading system"""
        self.logger.info("🚀 Initializing Sunrise MT5 Trading System...")
        
        # Safety check
        if DEMO_MODE_ONLY:
            self.logger.info("⚠️  DEMO MODE ENFORCED - Safe testing environment")
        else:
            self.logger.warning("🔴 REAL TRADING MODE - Use with extreme caution!")
        
        # Connect to MT5
        if not self.mt5_connection.connect():
            self.logger.error("Failed to connect to MT5")
            return False
        
        # Initialize strategies for each symbol
        for symbol in SYMBOLS_TO_TRADE:
            self.logger.info(f"Initializing strategy for {symbol}")
            # Note: Strategy initialization will be enhanced in next steps
            self.strategies[symbol] = None
        
        self.logger.info("✅ Trading system initialized successfully")
        return True
    
    def start_trading(self):
        """Start the main trading loop"""
        if not self.initialize():
            return
        
        self.running = True
        self.logger.info("🎯 Starting live trading loop...")
        
        try:
            while self.running and not self.emergency_stop:
                # Check each symbol
                for symbol in SYMBOLS_TO_TRADE:
                    if self.emergency_stop:
                        break
                    
                    try:
                        self.process_symbol(symbol)
                    except Exception as e:
                        self.logger.error(f"Error processing {symbol}: {e}")
                
                # Wait before next check
                if not self.emergency_stop:
                    time.sleep(SIGNAL_CHECK_INTERVAL)
                    
        except KeyboardInterrupt:
            self.logger.info("Trading interrupted by user")
        except Exception as e:
            self.logger.error(f"Trading loop error: {e}")
        finally:
            self.stop()
    
    def process_symbol(self, symbol: str):
        """Process trading signals for a specific symbol"""
        # Check if market is open
        if not self.mt5_connection.is_market_open(symbol):
            return
        
        # Get latest data
        rates = mt5.copy_rates_from_pos(symbol, DEFAULT_TIMEFRAME, 0, 100)
        if rates is None or len(rates) == 0:
            self.logger.warning(f"No data available for {symbol}")
            return
        
        # TODO: Generate signals from strategy
        # This will be implemented in the next development phase
        signal = self.generate_signal(symbol, rates)
        
        if signal:
            self.execute_signal(symbol, signal)
    
    def generate_signal(self, symbol: str, rates) -> Optional[Dict]:
        """Generate trading signal from strategy"""
        # PLACEHOLDER: This will be replaced with actual strategy logic
        # For now, return None (no signals)
        return None
    
    def execute_signal(self, symbol: str, signal: Dict):
        """Execute a trading signal"""
        try:
            # Check if we can open position
            can_trade, reason = self.position_manager.can_open_position(symbol)
            if not can_trade:
                self.logger.info(f"Cannot trade {symbol}: {reason}")
                return
            
            # Manual confirmation if enabled
            if ENABLE_TRADE_CONFIRMATION:
                if not self.confirm_trade(symbol, signal):
                    self.logger.info(f"Trade cancelled by user for {symbol}")
                    return
            
            # Execute the trade
            self.place_order(symbol, signal)
            
        except Exception as e:
            self.logger.error(f"Error executing signal for {symbol}: {e}")
    
    def confirm_trade(self, symbol: str, signal: Dict) -> bool:
        """Request manual confirmation for trade"""
        print(f"\n{'='*50}")
        print(f"TRADE CONFIRMATION REQUIRED")
        print(f"{'='*50}")
        print(f"Symbol: {symbol}")
        print(f"Signal: {signal}")
        print(f"{'='*50}")
        
        while True:
            response = input("Execute this trade? (y/n/q): ").lower().strip()
            if response == 'y':
                return True
            elif response == 'n':
                return False
            elif response == 'q':
                self.emergency_stop = True
                return False
            else:
                print("Please enter 'y' for yes, 'n' for no, or 'q' to quit")
    
    def place_order(self, symbol: str, signal: Dict):
        """Place order in MT5"""
        # PLACEHOLDER: Implement actual order placement
        self.logger.info(f"PLACEHOLDER: Would place order for {symbol} with signal {signal}")
        
        # Increment daily trade counter
        self.position_manager.daily_trades += 1
        
        # Log trade
        trade_data = {
            'timestamp': datetime.now(),
            'symbol': symbol,
            'signal': signal,
            'status': 'PLACEHOLDER_ORDER'
        }
        self.logger.log_trade(trade_data)
    
    def stop(self):
        """Stop the trading system"""
        self.running = False
        self.logger.info("🛑 Stopping trading system...")
        
        # Close any open positions if needed (implement as safety feature)
        # self.close_all_positions()
        
        # Disconnect from MT5
        self.mt5_connection.disconnect()
        
        self.logger.info("✅ Trading system stopped safely")

# =============================================================
# STEP-BY-STEP SETUP FUNCTIONS
# =============================================================

def setup_mt5_environment():
    """Step 1: Setup MT5 environment and check requirements"""
    print("🔧 STEP 1: Setting up MT5 environment...")
    
    try:
        import MetaTrader5 as mt5
        print("✅ MetaTrader5 package installed")
    except ImportError:
        print("❌ MetaTrader5 package not found")
        print("📥 Install with: pip install MetaTrader5")
        return False
    
    # Check if MT5 terminal is running
    if not mt5.initialize():
        print("❌ MT5 terminal not found or not running")
        print("🔧 Please ensure MetaTrader 5 is installed and running")
        return False
    
    print("✅ MT5 terminal is accessible")
    mt5.shutdown()
    return True

def create_config_files():
    """Step 2: Create configuration files"""
    print("\n🔧 STEP 2: Creating configuration files...")
    
    # Create directories
    config_dir = PROJECT_ROOT / 'config'
    logs_dir = PROJECT_ROOT / 'logs'
    
    config_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Created config directory: {config_dir}")
    print(f"✅ Created logs directory: {logs_dir}")
    
    # Create sample credential file if it doesn't exist
    if not CONFIG_FILE.exists():
        sample_config = {
            "login": "YOUR_MT5_ACCOUNT_NUMBER",
            "password": "YOUR_MT5_PASSWORD", 
            "server": "YOUR_BROKER_SERVER",
            "note": "Replace with your actual MT5 credentials"
        }
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(sample_config, f, indent=4)
        
        print(f"✅ Created sample config file: {CONFIG_FILE}")
        print("⚠️  Please update this file with your MT5 credentials")
    else:
        print(f"✅ Config file already exists: {CONFIG_FILE}")
    
    return True

def test_connection():
    """Step 3: Test MT5 connection"""
    print("\n🔧 STEP 3: Testing MT5 connection...")
    
    logger = TradingLogger(LOG_FILE, TRADE_LOG_FILE)
    connection = MT5Connection(logger)
    
    if connection.connect():
        print("✅ MT5 connection successful!")
        print(f"📊 Account: {connection.account_info.login}")
        print(f"💰 Balance: {connection.account_info.balance}")
        print(f"💱 Currency: {connection.account_info.currency}")
        connection.disconnect()
        return True
    else:
        print("❌ MT5 connection failed")
        print("🔧 Please check your credentials and try again")
        return False

# =============================================================
# MAIN EXECUTION
# =============================================================

def main():
    """Main execution function"""
    print("🌅 SUNRISE MT5 LIVE TRADING CONNECTOR")
    print("=" * 50)
    print("⚠️  DEMO TRADING MODE ENFORCED")
    print("🎯 Step-by-step setup and testing")
    print("=" * 50)
    
    # Step-by-step setup
    if not setup_mt5_environment():
        return
    
    if not create_config_files():
        return
    
    if not test_connection():
        return
    
    print("\n🎉 SETUP COMPLETE!")
    print("=" * 50)
    print("📝 NEXT STEPS:")
    print("1. Update config/mt5_credentials.json with your MT5 login details")
    print("2. Test on demo account first")
    print("3. Implement strategy signal generation")
    print("4. Add proper order management")
    print("5. Enhance risk management")
    print("=" * 50)
    
    # Optional: Start trading loop (currently in placeholder mode)
    start_trading = input("\nStart trading loop? (y/n): ").lower().strip()
    if start_trading == 'y':
        trader = SunriseMT5Trader()
        trader.start_trading()

if __name__ == "__main__":
    main()