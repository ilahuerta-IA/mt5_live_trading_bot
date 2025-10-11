# 🚀 MetaTrader 5 Advanced Trading Monitor

**Professional-grade live trading system with real-time strategy monitoring, advanced GUI, and comprehensive risk management.**

## 📊 Overview

This system provides advanced monitoring and analysis capabilities for MetaTrader 5 trading strategies, featuring real-time phase tracking, professional candlestick charts, and comprehensive configuration management.

## ✨ Key Features

### 🎯 **Advanced Strategy Monitor**
- **Real-time Phase Tracking**: Monitor strategy states (NORMAL → PULLBACK → BREAKOUT)
- **Live Candlestick Charts**: Professional charts with technical indicators overlay
- **Asset-specific Configuration**: Individual EMA periods and parameters per symbol
- **Terminal-style Logging**: Comprehensive phase transitions and strategy events

### 📈 **Technical Analysis**
- **Multi-timeframe EMA Analysis**: Fast, Medium, Slow, and Filter EMAs
- **ATR-based Risk Management**: Dynamic TP/SL calculations
- **Trend Direction Detection**: Real-time trend analysis and confirmation
- **Window Breakout Detection**: Precision entry point identification

### 🎛️ **Professional GUI**
- **Strategy Phase Dashboard**: Visual overview of all monitored assets
- **Configuration Parameter Display**: Complete strategy settings viewer
- **Live Chart Integration**: matplotlib/mplfinance professional charts
- **Multi-asset Monitoring**: Simultaneous tracking of 6+ currency pairs

## 📁 Project Structure

```
mt5_live_trading_bot/
├── 📄 README.md                    # Project documentation
├── 📄 requirements.txt             # Python dependencies
├── 📄 pyproject.toml               # Project configuration
├── 📄 .gitignore                   # Git ignore rules
│
├── 🚀 launch_advanced_monitor.py   # Main GUI launcher (RECOMMENDED)
├── 🎛️ advanced_mt5_monitor_gui.py  # Advanced monitoring GUI
├── 📊 start_advanced_monitor.py    # Quick start script
│
├── 🧪 testing/
│   ├── test_setup.py               # Installation verification
│   ├── test_monitor_components.py  # Component testing
│   ├── test_signal_detection.py    # Signal testing
│   └── deep_stress_test.py         # Comprehensive testing
│
├── 🏗️ src/                         # Core source code
│   ├── mt5_live_trading_connector.py
│   ├── sunrise_signal_adapter.py
│   └── __init__.py
│
├── 🎯 strategies/                  # Trading strategies
│   ├── sunrise_ogle_eurusd.py     # EURUSD strategy
│   ├── sunrise_ogle_gbpusd.py     # GBPUSD strategy
│   ├── sunrise_ogle_xauusd.py     # XAUUSD strategy
│   ├── sunrise_ogle_audusd.py     # AUDUSD strategy
│   ├── sunrise_ogle_xagusd.py     # XAGUSD strategy
│   ├── sunrise_ogle_usdchf.py     # USDCHF strategy
│   └── __init__.py
│
├── ⚙️ config/                      # Configuration files
├── 📝 logs/                        # Application logs
├── 🔧 .vscode/                     # VS Code settings
├── 🐍 venv/                        # Virtual environment
└── 📚 docs/                        # Documentation files
    ├── ADVANCED_GUI_COMPLETE.md
    └── DEEP_TEST_RESULTS.md
```

## 🚀 Quick Start

### Method 1: Advanced GUI (Recommended)
```bash
# 1. Navigate to project directory
cd mt5_live_trading_bot

# 2. Launch the advanced monitor
python launch_advanced_monitor.py
```

### Method 2: Quick Start
```bash
# Alternative quick start
python start_advanced_monitor.py
```

## 🔧 Installation

### Prerequisites
- Python 3.8+
- MetaTrader 5 terminal installed
- MT5 account (demo recommended for testing)

### Automated Setup
```powershell
# Run the automated setup script
./setup.ps1
```

### Manual Installation
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Verify installation
python test_setup.py

# 3. Test components
python test_monitor_components.py
```

## 📊 Supported Assets

| Asset    | Type         | Strategy File              |
|----------|--------------|----------------------------|
| EURUSD   | Forex        | sunrise_ogle_eurusd.py     |
| GBPUSD   | Forex        | sunrise_ogle_gbpusd.py     |
| XAUUSD   | Precious     | sunrise_ogle_xauusd.py     |
| AUDUSD   | Forex        | sunrise_ogle_audusd.py     |
| XAGUSD   | Precious     | sunrise_ogle_xagusd.py     |
| USDCHF   | Forex        | sunrise_ogle_usdchf.py     |

## 🎛️ GUI Features

### Strategy Phase Tracker
- **NORMAL Phase**: Monitoring for trend signals
- **WAITING_PULLBACK**: Scanning for pullback patterns
- **WAITING_BREAKOUT**: Monitoring for breakout entries
- **Visual Indicators**: Color-coded phase status

### Live Charts
- **Candlestick Charts**: Professional mplfinance charts
- **Technical Indicators**: EMA overlays with asset-specific periods
- **TP/SL Levels**: Visual risk management levels
- **Real-time Updates**: Live price data from MT5

### Configuration Viewer
- **Strategy Parameters**: Complete configuration display
- **Risk Management**: TP/SL multipliers and ATR settings
- **Entry Filters**: Time ranges, volatility filters, angle filters
- **Asset-specific Settings**: Individual parameters per symbol

## 🔍 Monitoring & Logging

### Terminal Output
```
📊 STRATEGY PHASE SUMMARY - ALL ASSETS
============================================================
⚪ NORMAL (3 assets):
   EURUSD: 1.16850 | BULLISH | Scanning pullback
   GBPUSD: 1.32450 | SIDEWAYS | Monitoring trend
   USDCHF: 0.91200 | BEARISH | Filter check

🟡 WAITING_PULLBACK (2 assets):
   XAUUSD: 1985.50 | BULLISH | Pullback: 0 | Window: CLOSED
   AUDUSD: 0.65420 | BULLISH | Pullback: 1 | Window: CLOSED

🟠 WAITING_BREAKOUT (1 assets):
   XAGUSD: 24.850 | BULLISH | Pullback: 2 | Window: OPEN
============================================================
```

### Log Files
- `logs/mt5_trading.log` - Main application log
- `logs/mt5_trades.log` - Trading activity log
- `logs/archive/` - Historical log files

## 🧪 Testing

### Component Testing
```bash
# Test all components
python test_monitor_components.py

# Test signal detection
python test_signal_detection.py

# Comprehensive stress test
python deep_stress_test.py
```

### Verification Steps
1. **Connection Test**: Verify MT5 connectivity
2. **Strategy Loading**: Test all strategy configurations
3. **GUI Components**: Test all interface elements
4. **Chart Rendering**: Verify matplotlib/mplfinance integration
5. **Data Processing**: Test indicator calculations

## ⚠️ Important Notes

### Safety First
- **Demo Trading**: Always test on demo accounts first
- **Risk Management**: Never risk more than you can afford to lose
- **Position Sizing**: Start with minimum position sizes
- **Understanding**: Fully understand the system before live trading

### System Requirements
- **Windows**: Recommended (MT5 native support)
- **Python 3.8+**: Required for all features
- **MT5 Terminal**: Must be running and logged in
- **Internet Connection**: Required for real-time data

### Performance Tips
- **Close Unused Applications**: For optimal MT5 performance
- **Monitor Resource Usage**: Check CPU and memory usage
- **Regular Backups**: Keep logs and configuration backed up
- **Update Regularly**: Keep dependencies updated

## 📚 Documentation

- **ADVANCED_GUI_COMPLETE.md**: Complete GUI documentation
- **DEEP_TEST_RESULTS.md**: Testing results and benchmarks
- **Strategy Documentation**: Individual strategy explanations

## 🤝 Support

For issues, questions, or contributions:
1. Check the documentation files
2. Review log files for error details
3. Test on demo accounts first
4. Verify system requirements

## 📄 License

This project is for educational purposes. Please ensure compliance with your broker's terms of service and local regulations when using automated trading systems.

---

**⚡ Ready to monitor your trading strategies with professional-grade tools!**