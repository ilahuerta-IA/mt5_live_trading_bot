# MT5 Live Trading Monitor

> **Professional real-time trading strategy monitor for MetaTrader 5 with advanced GUI and comprehensive risk management.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MetaTrader 5](https://img.shields.io/badge/MetaTrader-5-green.svg)](https://www.metatrader5.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![MT5 Advanced Monitor GUI](Advanced%20MT5%20Monitor.png)

## 🎯 Overview

Advanced monitoring system for live MetaTrader 5 trading strategies featuring real-time strategy state tracking, professional candlestick charts, EMA-based signal detection, and comprehensive logging. Perfect for traders who want to monitor multiple strategies simultaneously with visual feedback and detailed analytics.

### Key Features

- **📊 Real-Time Monitoring** - Live tracking of 6+ currency pairs and precious metals
- **🎨 Professional GUI** - Advanced interface with live candlestick charts and EMA overlays
- **🔍 Strategy State Machine** - 4-phase tracking: SCANNING → ARMED → WINDOW_OPEN → Entry
- **⚙️ Asset-Specific Configuration** - Individual EMA periods and risk parameters per symbol
- **📝 Comprehensive Logging** - Terminal-style logging with phase transitions and critical events
- **🛡️ Risk Management** - ATR-based TP/SL calculations with dynamic position sizing

## 🚀 Quick Start

### Prerequisites

- Windows 10/11 (recommended for MT5 native support)
- Python 3.8 or higher
- MetaTrader 5 terminal installed and running
- MT5 account (demo recommended for testing)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/mt5_live_trading_bot.git
   cd mt5_live_trading_bot
   ```

2. **Run automated setup** (Recommended - Windows PowerShell)
   ```powershell
   .\setup.ps1
   ```

   Or **manual installation**:
   ```bash
   # Create virtual environment
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure MT5 credentials**
   ```bash
   # Copy template and fill in your MT5 credentials
   copy config\mt5_credentials_template.json config\mt5_credentials.json
   # Edit config\mt5_credentials.json with your account details
   ```

4. **Launch the monitor**
   ```bash
   python launch_advanced_monitor.py
   ```

## 📖 Usage

### Starting the Monitor

**Method 1:** Advanced GUI (Recommended)
```bash
python launch_advanced_monitor.py
```

**Method 2:** Quick Start
```bash
python start_advanced_monitor.py
```

**Method 3:** Alternative Launcher
```bash
python launch_advanced_monitor_v2.py
```

### Monitored Assets

| Symbol | Type | Timeframe | EMA Fast | EMA Med | EMA Slow |
|--------|------|-----------|----------|---------|----------|
| EURUSD | Forex | M5 | 10 | 20 | 50 |
| GBPUSD | Forex | M5 | 10 | 20 | 50 |
| XAUUSD | Gold | M5 | 5 | 10 | 20 |
| AUDUSD | Forex | M5 | 10 | 20 | 50 |
| XAGUSD | Silver | M5 | 5 | 10 | 20 |
| USDCHF | Forex | M5 | 10 | 20 | 50 |

### Strategy States

1. **SCANNING** - Monitoring for EMA crossover signals
2. **ARMED** - Crossover detected, waiting for pullback confirmation
3. **WINDOW_OPEN** - Pullback confirmed, monitoring for breakout entry
4. **Entry Detection** - Price breaks window limits, entry signal generated

## 🧪 Testing

### Component Tests
```bash
cd testing
python test_setup.py              # Verify installation
python test_monitor_components.py # Test GUI components
python test_signal_detection.py   # Test strategy signals
python deep_stress_test.py        # Comprehensive stress test
```

### Order Execution Tests
```bash
cd testing
python test_mt5_order.py          # Test basic order execution
python test_real_entry.py         # Simulate real bot entry with ATR/SL/TP
```

**⚠️ Warning:** Order execution tests place REAL orders on your MT5 account. Use demo accounts for testing!

### Expected Test Results
- ✅ MT5 connection successful
- ✅ All 6 strategies loaded correctly
- ✅ GUI components initialized
- ✅ Chart rendering functional
- ✅ EMA calculations accurate
- ✅ Order filling mode detection working
- ✅ ATR-based SL/TP calculation correct

## 📁 Project Structure

```
mt5_live_trading_bot/
├── advanced_mt5_monitor_gui.py    # Main monitor application (102KB)
├── launch_advanced_monitor.py     # Primary launcher
├── start_advanced_monitor.py      # Quick start script
├── requirements.txt               # Python dependencies
├── setup.ps1                      # Automated setup script
├── .gitignore                     # Git ignore rules
│
├── config/                        # Configuration files
│   ├── mt5_credentials_template.json
│   └── mt5_credentials.json       # (gitignored - create from template)
│
├── src/                           # Core source code
│   ├── mt5_live_trading_connector.py
│   ├── sunrise_signal_adapter.py
│   └── __init__.py
│
├── strategies/                    # Asset-specific strategies
│   ├── sunrise_ogle_eurusd.py
│   ├── sunrise_ogle_gbpusd.py
│   ├── sunrise_ogle_xauusd.py
│   ├── sunrise_ogle_audusd.py
│   ├── sunrise_ogle_xagusd.py
│   ├── sunrise_ogle_usdchf.py
│   └── __init__.py
│
├── testing/                       # Test suite
│   ├── test_setup.py              # Installation verification
│   ├── test_monitor_components.py # GUI component tests
│   ├── test_signal_detection.py   # Strategy signal tests
│   ├── deep_stress_test.py        # Stress testing
│   ├── test_mt5_order.py          # Order execution test
│   └── test_real_entry.py         # Real entry simulation
│
├── docs/                          # Documentation
│   ├── README.md                  # Documentation index
│   ├── PULLBACK_FIX_SUMMARY.md
│   ├── EMA_STABILITY_FIX_CRITICAL.md
│   └── [other current docs + archive/]
│
└── logs/                          # Application logs (gitignored)
```

## ⚙️ Configuration

### MT5 Credentials Format
```json
{
  "account": 12345678,
  "password": "YourMT5Password",
  "server": "YourBrokerServer-Demo"
}
```

### Strategy Parameters
Each strategy in `strategies/` folder contains:
- EMA periods (Fast, Medium, Slow, Filter)
- ATR multipliers for TP/SL
- Pullback confirmation candles
- Window duration (bars)
- Trading hours restrictions

## 🛡️ Risk Management

### Safety Features
- **Demo Account Testing**: Always test on demo accounts first
- **Position Sizing**: Configurable risk per trade
- **Stop Loss**: ATR-based dynamic stop loss
- **Take Profit**: Multiple TP levels supported
- **Time Filters**: Trading hour restrictions
- **Trend Confirmation**: Multi-EMA validation

### Important Warnings
⚠️ **Never risk more than you can afford to lose**  
⚠️ **Understand the system completely before live trading**  
⚠️ **Start with minimum position sizes**  
⚠️ **Keep detailed logs of all trading activity**  
⚠️ **Regularly review strategy performance**

## 📊 GUI Features

### Main Interface
- Real-time price display for all assets
- Strategy state indicators (color-coded)
- Pullback counter progress
- Window status (OPEN/CLOSED)
- Last signal timestamp

### Live Charts
- Professional candlestick charts (mplfinance)
- EMA overlays (Fast, Medium, Slow, Filter)
- Volume indicators
- Interactive chart controls

### Configuration Viewer
- Complete strategy parameters
- Risk management settings
- Entry filter details
- Asset-specific configurations

## 🔧 Troubleshooting

### Common Issues

**MT5 Connection Failed**
```
1. Ensure MT5 terminal is running and logged in
2. Verify credentials in config/mt5_credentials.json
3. Check if MetaTrader5 Python package is installed
4. Restart MT5 terminal
```

**GUI Not Displaying Charts**
```
1. Verify matplotlib and mplfinance are installed
2. Check if tkinter is available (built-in with Python)
3. Update graphics drivers
4. Try running with administrator privileges
```

**No Signals Detected**
```
1. Confirm strategies are loaded (check logs/)
2. Verify market is open for selected assets
3. Check if price data is streaming
4. Review strategy parameters in strategies/ folder
```

## 📚 Documentation

Comprehensive documentation available in the `docs/` folder:

- **[docs/README.md](docs/README.md)** - Complete documentation index and navigation
- **[START_TESTING_HERE.md](docs/START_TESTING_HERE.md)** - Quick start guide for testing
- **[PULLBACK_FIX_SUMMARY.md](docs/PULLBACK_FIX_SUMMARY.md)** - Critical bug fixes (October 2025)
- **[EMA_STABILITY_FIX_CRITICAL.md](docs/EMA_STABILITY_FIX_CRITICAL.md)** - EMA calculation improvements
- **[ENHANCED_PULLBACK_LOGGING.md](docs/ENHANCED_PULLBACK_LOGGING.md)** - Export-ready logging system
- **Setup Guides** - MT5 configuration and EMA alignment (see docs/)
- **Contributing Guidelines** - Development and contribution standards

**Note:** Historical and intermediate documentation preserved in `docs/archive/` for reference.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚖️ Disclaimer

**This software is for educational purposes only.** 

Trading financial instruments carries a high level of risk and may not be suitable for all investors. The high degree of leverage can work against you as well as for you. Before deciding to trade, you should carefully consider your investment objectives, level of experience, and risk appetite.

**No representation is being made that any account will or is likely to achieve profits or losses similar to those shown.** Past performance is not indicative of future results.

The developers and contributors of this software assume no responsibility for your trading results. Use at your own risk.

## 🙏 Acknowledgments

- MetaTrader 5 Python API
- mplfinance for professional financial charts
- Pandas for data manipulation
- NumPy for numerical computing

## 📧 Contact

For questions, issues, or suggestions:
- Open an issue on GitHub
- Review existing documentation in `docs/` folder
- Check logs in `logs/` folder for error details

---

**⚡ Happy Trading! Monitor your strategies like a pro!**
