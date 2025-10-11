"""
MT5 Live Trading Bot - Sunrise Strategies
==========================================

This module contains independent copies of the Sunrise trading strategies
for use with the MT5 live trading system.

These strategies are completely independent from the original quant_bot_project
development environment and can be used for live trading without external dependencies.

Available Strategies:
- sunrise_ogle_eurusd: EUR/USD trading strategy
- sunrise_ogle_gbpusd: GBP/USD trading strategy  
- sunrise_ogle_xauusd: Gold (XAU/USD) trading strategy
- sunrise_ogle_audusd: AUD/USD trading strategy
- sunrise_ogle_xagusd: Silver (XAG/USD) trading strategy
- sunrise_ogle_usdchf: USD/CHF trading strategy
"""

# Import all strategies for easier access
try:
    from .sunrise_ogle_eurusd import SunriseOgle as SunriseOgleEURUSD
except ImportError:
    SunriseOgleEURUSD = None

try:
    from .sunrise_ogle_gbpusd import SunriseOgle as SunriseOgleGBPUSD
except ImportError:
    SunriseOgleGBPUSD = None

try:
    from .sunrise_ogle_xauusd import SunriseOgle as SunriseOgleXAUUSD
except ImportError:
    SunriseOgleXAUUSD = None

try:
    from .sunrise_ogle_audusd import SunriseOgle as SunriseOgleAUDUSD
except ImportError:
    SunriseOgleAUDUSD = None

try:
    from .sunrise_ogle_xagusd import SunriseOgle as SunriseOgleXAGUSD
except ImportError:
    SunriseOgleXAGUSD = None

try:
    from .sunrise_ogle_usdchf import SunriseOgle as SunriseOgleUSDCHF
except ImportError:
    SunriseOgleUSDCHF = None

# Export all available strategies
__all__ = [
    'SunriseOgleEURUSD',
    'SunriseOgleGBPUSD', 
    'SunriseOgleXAUUSD',
    'SunriseOgleAUDUSD',
    'SunriseOgleXAGUSD',
    'SunriseOgleUSDCHF'
]

# Strategy mapping for easy access
STRATEGY_CLASSES = {
    'EURUSD': SunriseOgleEURUSD,
    'GBPUSD': SunriseOgleGBPUSD,
    'XAUUSD': SunriseOgleXAUUSD,
    'AUDUSD': SunriseOgleAUDUSD,
    'XAGUSD': SunriseOgleXAGUSD,
    'USDCHF': SunriseOgleUSDCHF
}