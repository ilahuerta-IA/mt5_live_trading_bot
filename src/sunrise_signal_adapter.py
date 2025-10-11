"""Sunrise Strategy MT5 Signal Adapter
=====================================
Bridges Backtrader strategy signals to MT5 trading operations.
This adapter processes signals from our Sunrise strategies and converts them 
to MT5-compatible trading instructions.

Development Phase: Signal Integration
Previous Phase: Basic MT5 Connection ✅
Current Phase: Strategy Signal Processing 
Next Phase: Order Management and Risk Control
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import MetaTrader5 as mt5
from typing import Dict, Optional, Tuple, List
import logging
from pathlib import Path
import sys
import json

# Add strategies directory to path
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

# Path to local strategies (completely independent from quant_bot_project)
LOCAL_STRATEGIES_DIR = PROJECT_ROOT / "strategies"

# Add local strategies directory to Python path
sys.path.insert(0, str(LOCAL_STRATEGIES_DIR))

# Import our existing strategies from local strategies folder
# Verify path exists before importing
if not LOCAL_STRATEGIES_DIR.exists():
    print(f"Warning: Local strategies directory not found: {LOCAL_STRATEGIES_DIR}")
    print("Please ensure strategies are copied to the local strategies folder")

# Import strategies with individual error handling using dynamic imports
strategy_classes = {}
strategies_to_import = [
    ('sunrise_ogle_eurusd', 'SunriseOgle', 'EURUSD'),
    ('sunrise_ogle_gbpusd', 'SunriseOgle', 'GBPUSD'),
    ('sunrise_ogle_xauusd', 'SunriseOgle', 'XAUUSD'),
    ('sunrise_ogle_audusd', 'SunriseOgle', 'AUDUSD'),
    ('sunrise_ogle_xagusd', 'SunriseOgle', 'XAGUSD'),
    ('sunrise_ogle_usdchf', 'SunriseOgle', 'USDCHF')
]

for module_name, class_name, symbol in strategies_to_import:
    try:
        module = __import__(module_name)
        strategy_class = getattr(module, class_name)
        strategy_classes[symbol] = strategy_class
        print(f"✅ {symbol}: Strategy class imported successfully")
    except ImportError as e:
        print(f"⚠️  {symbol}: Could not import strategy from {module_name}: {e}")
    except AttributeError as e:
        print(f"⚠️  {symbol}: Could not find class {class_name} in {module_name}: {e}")
    except Exception as e:
        print(f"❌ {symbol}: Unexpected error importing strategy: {e}")

class SignalType:
    """Signal types for trading operations"""
    BUY = "BUY"
    SELL = "SELL"
    CLOSE_BUY = "CLOSE_BUY"
    CLOSE_SELL = "CLOSE_SELL"
    HOLD = "HOLD"

class TradingSignal:
    """Container for trading signals"""
    
    def __init__(self, 
                 symbol: str,
                 signal_type: str,
                 confidence: float,
                 entry_price: float = None,
                 stop_loss: float = None,
                 take_profit: float = None,
                 position_size: float = None,
                 timestamp: datetime = None,
                 metadata: Dict = None):
        
        self.symbol = symbol
        self.signal_type = signal_type
        self.confidence = confidence
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.position_size = position_size
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict:
        """Convert signal to dictionary"""
        return {
            'symbol': self.symbol,
            'signal_type': self.signal_type,
            'confidence': self.confidence,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'position_size': self.position_size,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }
    
    def __str__(self):
        return f"Signal({self.symbol}, {self.signal_type}, conf={self.confidence:.2f})"

class SunriseSignalGenerator:
    """Generates trading signals from Sunrise strategy logic"""
    
    def __init__(self, symbol: str, strategy_class, logger=None):
        self.symbol = symbol
        self.strategy_class = strategy_class
        self.logger = logger or logging.getLogger(__name__)
        self.last_signal = None
        self.data_buffer = []
        self.buffer_size = 100  # Keep last 100 bars for analysis
        
    def update_data(self, rates: np.ndarray):
        """Update market data for signal generation"""
        try:
            # Convert MT5 rates to pandas DataFrame
            df = pd.DataFrame(rates)
            df['datetime'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('datetime', inplace=True)
            
            # Update buffer
            self.data_buffer = df.tail(self.buffer_size).copy()
            
            self.logger.debug(f"Updated data buffer for {self.symbol}: {len(self.data_buffer)} bars")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating data for {self.symbol}: {e}")
            return False
    
    def calculate_indicators(self) -> Dict:
        """Calculate technical indicators needed for signal generation"""
        if len(self.data_buffer) < 50:  # Need minimum data
            return {}
        
        try:
            df = self.data_buffer.copy()
            indicators = {}
            
            # Calculate EMAs (matching Sunrise strategy)
            indicators['ema_21'] = df['close'].ewm(span=21).mean()
            indicators['ema_50'] = df['close'].ewm(span=50).mean()
            indicators['ema_100'] = df['close'].ewm(span=100).mean()
            
            # Calculate RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators['rsi'] = 100 - (100 / (1 + rs))
            
            # Calculate MACD
            ema_12 = df['close'].ewm(span=12).mean()
            ema_26 = df['close'].ewm(span=26).mean()
            indicators['macd'] = ema_12 - ema_26
            indicators['macd_signal'] = indicators['macd'].ewm(span=9).mean()
            indicators['macd_histogram'] = indicators['macd'] - indicators['macd_signal']
            
            # Bollinger Bands
            bb_period = 20
            bb_std = 2
            sma_20 = df['close'].rolling(window=bb_period).mean()
            std_20 = df['close'].rolling(window=bb_period).std()
            indicators['bb_upper'] = sma_20 + (std_20 * bb_std)
            indicators['bb_lower'] = sma_20 - (std_20 * bb_std)
            indicators['bb_middle'] = sma_20
            
            # Volume indicators (if available)
            if 'tick_volume' in df.columns:
                indicators['volume_sma'] = df['tick_volume'].rolling(window=20).mean()
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"Error calculating indicators for {self.symbol}: {e}")
            return {}
    
    def generate_signal(self) -> Optional[TradingSignal]:
        """Generate trading signal based on Sunrise strategy logic"""
        try:
            if len(self.data_buffer) < 50:
                return None
            
            # Calculate indicators
            indicators = self.calculate_indicators()
            if not indicators:
                return None
            
            # Get current market data
            current_data = self.data_buffer.iloc[-1]
            current_price = current_data['close']
            current_time = self.data_buffer.index[-1]
            
            # Get latest indicator values
            latest_indicators = {}
            for key, series in indicators.items():
                if len(series) > 0:
                    latest_indicators[key] = series.iloc[-1]
            
            # Apply Sunrise strategy logic
            signal = self._apply_sunrise_logic(current_price, latest_indicators, current_data)
            
            if signal:
                signal.timestamp = current_time
                self.last_signal = signal
                self.logger.info(f"Generated signal for {self.symbol}: {signal}")
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Error generating signal for {self.symbol}: {e}")
            return None
    
    def _apply_sunrise_logic(self, price: float, indicators: Dict, market_data: Dict) -> Optional[TradingSignal]:
        """Apply Sunrise strategy trading logic"""
        try:
            # Basic Sunrise strategy conditions (simplified version)
            # This is a placeholder implementation - replace with actual strategy logic
            
            # Get key indicators
            ema_21 = indicators.get('ema_21')
            ema_50 = indicators.get('ema_50')
            rsi = indicators.get('rsi')
            macd = indicators.get('macd')
            macd_signal = indicators.get('macd_signal')
            
            if None in [ema_21, ema_50, rsi, macd, macd_signal]:
                return None
            
            # Initialize signal parameters
            signal_type = SignalType.HOLD
            confidence = 0.0
            stop_loss = None
            take_profit = None
            
            # Bull trend conditions
            if (ema_21 > ema_50 and 
                price > ema_21 and 
                rsi > 30 and rsi < 70 and
                macd > macd_signal):
                
                signal_type = SignalType.BUY
                confidence = 0.7
                
                # Calculate stop loss and take profit
                stop_loss = price - (price * 0.01)  # 1% stop loss
                take_profit = price + (price * 0.02)  # 2% take profit
            
            # Bear trend conditions
            elif (ema_21 < ema_50 and 
                  price < ema_21 and 
                  rsi > 30 and rsi < 70 and
                  macd < macd_signal):
                
                signal_type = SignalType.SELL
                confidence = 0.7
                
                # Calculate stop loss and take profit
                stop_loss = price + (price * 0.01)  # 1% stop loss
                take_profit = price - (price * 0.02)  # 2% take profit
            
            # Only generate signal if confidence is above threshold
            if confidence >= 0.6:
                return TradingSignal(
                    symbol=self.symbol,
                    signal_type=signal_type,
                    confidence=confidence,
                    entry_price=price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    metadata={
                        'ema_21': ema_21,
                        'ema_50': ema_50,
                        'rsi': rsi,
                        'macd': macd,
                        'macd_signal': macd_signal
                    }
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error applying Sunrise logic for {self.symbol}: {e}")
            return None

class MultiSymbolSignalManager:
    """Manages signal generation for multiple symbols"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.signal_generators = {}
        # Use the dynamically imported strategy classes
        self.symbol_strategies = strategy_classes
    
    def add_symbol(self, symbol: str):
        """Add symbol for signal generation"""
        try:
            if symbol in self.symbol_strategies:
                strategy_class = self.symbol_strategies[symbol]
                self.signal_generators[symbol] = SunriseSignalGenerator(
                    symbol=symbol,
                    strategy_class=strategy_class,
                    logger=self.logger
                )
                self.logger.info(f"Added signal generator for {symbol}")
                return True
            else:
                self.logger.warning(f"No strategy available for {symbol}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error adding symbol {symbol}: {e}")
            return False
    
    def update_market_data(self, symbol: str, rates: np.ndarray):
        """Update market data for specific symbol"""
        if symbol in self.signal_generators:
            return self.signal_generators[symbol].update_data(rates)
        return False
    
    def get_signals(self) -> List[TradingSignal]:
        """Generate signals for all symbols"""
        signals = []
        
        for symbol, generator in self.signal_generators.items():
            try:
                signal = generator.generate_signal()
                if signal:
                    signals.append(signal)
            except Exception as e:
                self.logger.error(f"Error generating signal for {symbol}: {e}")
        
        return signals
    
    def get_signal(self, symbol: str) -> Optional[TradingSignal]:
        """Generate signal for specific symbol"""
        if symbol in self.signal_generators:
            return self.signal_generators[symbol].generate_signal()
        return None

# =============================================================
# MT5 DATA INTEGRATION
# =============================================================

class MT5DataProvider:
    """Provides real-time data from MT5 for signal generation"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to MT5 for data access"""
        try:
            if not mt5.initialize():
                self.logger.error(f"MT5 initialization failed: {mt5.last_error()}")
                return False
            
            self.connected = True
            self.logger.info("Connected to MT5 for data access")
            return True
            
        except Exception as e:
            self.logger.error(f"Error connecting to MT5: {e}")
            return False
    
    def get_rates(self, symbol: str, timeframe: int, count: int = 100) -> Optional[np.ndarray]:
        """Get historical rates for symbol"""
        try:
            if not self.connected:
                return None
            
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
            if rates is None:
                self.logger.warning(f"No rates available for {symbol}")
                return None
            
            return rates
            
        except Exception as e:
            self.logger.error(f"Error getting rates for {symbol}: {e}")
            return None
    
    def get_tick(self, symbol: str) -> Optional[Dict]:
        """Get current tick for symbol"""
        try:
            if not self.connected:
                return None
            
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                return None
            
            return {
                'time': tick.time,
                'bid': tick.bid,
                'ask': tick.ask,
                'spread': tick.ask - tick.bid
            }
            
        except Exception as e:
            self.logger.error(f"Error getting tick for {symbol}: {e}")
            return None
    
    def disconnect(self):
        """Disconnect from MT5"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            self.logger.info("Disconnected from MT5")

# =============================================================
# TESTING AND VALIDATION
# =============================================================

def test_signal_generation():
    """Test signal generation with sample data"""
    print("🧪 Testing Sunrise Signal Generation")
    print("=" * 40)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Initialize signal manager
    signal_manager = MultiSymbolSignalManager(logger)
    
    # Add test symbol
    symbol = 'EURUSD'
    if signal_manager.add_symbol(symbol):
        print(f"✅ Added {symbol} for testing")
    else:
        print(f"❌ Failed to add {symbol}")
        return False
    
    # Initialize MT5 data provider
    data_provider = MT5DataProvider(logger)
    
    if not data_provider.connect():
        print("❌ Cannot connect to MT5 for testing")
        print("💡 Make sure MT5 terminal is running")
        return False
    
    # Get sample data
    rates = data_provider.get_rates(symbol, mt5.TIMEFRAME_M5, 100)
    if rates is None:
        print(f"❌ Cannot get data for {symbol}")
        data_provider.disconnect()
        return False
    
    print(f"✅ Retrieved {len(rates)} bars for {symbol}")
    
    # Update signal generator with data
    if signal_manager.update_market_data(symbol, rates):
        print("✅ Updated market data")
    else:
        print("❌ Failed to update market data")
        data_provider.disconnect()
        return False
    
    # Generate signal
    signal = signal_manager.get_signal(symbol)
    
    if signal:
        print(f"✅ Generated signal: {signal}")
        print(f"   Entry Price: {signal.entry_price}")
        print(f"   Stop Loss: {signal.stop_loss}")
        print(f"   Take Profit: {signal.take_profit}")
        print(f"   Confidence: {signal.confidence:.2f}")
    else:
        print("ℹ️  No signal generated (normal - strategy may not see opportunity)")
    
    # Test current tick
    tick = data_provider.get_tick(symbol)
    if tick:
        print(f"✅ Current {symbol} tick: Bid={tick['bid']}, Ask={tick['ask']}")
    
    # Cleanup
    data_provider.disconnect()
    
    print("\n🎉 Signal generation test completed")
    return True

if __name__ == "__main__":
    # Run signal generation test
    test_signal_generation()