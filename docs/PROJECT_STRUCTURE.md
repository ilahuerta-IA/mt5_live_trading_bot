# MT5 Live Trading Bot - Project Structure

## 📁 Directory Organization

```
mt5_live_trading_bot/
│
├── 📁 src/                              # Core source code
│   ├── mt5_live_trading_connector.py    # MT5 connection manager
│   ├── sunrise_signal_adapter.py        # Strategy signal adapter
│   ├── sunrise_signal_adapter.pyi       # Type hints
│   └── __init__.py                      # Package initialization
│
├── 📁 strategies/                       # Trading strategies
│   ├── sunrise_ogle_audusd.py          # AUD/USD strategy
│   ├── sunrise_ogle_eurusd.py          # EUR/USD strategy
│   ├── sunrise_ogle_gbpusd.py          # GBP/USD strategy
│   ├── sunrise_ogle_usdchf.py          # USD/CHF strategy
│   ├── sunrise_ogle_xagusd.py          # XAG/USD strategy (Silver)
│   ├── sunrise_ogle_xauusd.py          # XAU/USD strategy (Gold)
│   └── __init__.py                      # Strategies package
│
├── 📁 testing/                          # Test files
│   ├── deep_stress_test.py             # Comprehensive system test
│   ├── test_monitor_components.py       # Component unit tests
│   ├── test_setup.py                   # Setup validation tests
│   └── test_signal_detection.py        # Signal detection tests
│
├── 📁 docs/                             # Documentation
│   ├── ADVANCED_GUI_COMPLETE.md        # Advanced GUI documentation
│   ├── DEEP_TEST_RESULTS.md            # Test results documentation
│   ├── README.md                       # Original README
│   └── README_NEW.md                   # Updated README
│
├── 📁 config/                           # Configuration files
│   └── (strategy configuration files)
│
├── 📁 logs/                             # Log files
│   └── (application logs)
│
├── 📁 .vscode/                          # VS Code settings
│   ├── settings.json                   # Python interpreter & settings
│   └── launch.json                     # Debug configurations
│
├── 📁 venv/                             # Virtual environment
│   └── (Python virtual environment)
│
├── 🔧 Main Application Files
│   ├── advanced_mt5_monitor_gui.py     # Advanced monitoring GUI ⭐
│   ├── basic_mt5_monitor_gui.py        # Basic monitoring GUI
│   ├── launch_advanced_monitor.py      # Professional launcher ⭐
│   └── start_advanced_monitor.py       # Simple launcher
│
├── 📋 Configuration & Setup
│   ├── requirements.txt                # Python dependencies ✅
│   ├── pyproject.toml                  # Project metadata
│   ├── setup.ps1                      # PowerShell setup script
│   ├── .gitignore                      # Git ignore rules
│   └── PROJECT_STRUCTURE.md            # This file
│
└── 📖 Documentation
    └── README.md                       # Main project README
```

## 🚀 Quick Start

### 1. Environment Setup
```powershell
# Navigate to project directory
cd "c:\Iván\Yosoybuendesarrollador\Python\Portafolio\mt5_live_trading_bot"

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch Advanced Monitor
```powershell
# Professional launcher with dependency checks
python launch_advanced_monitor.py

# OR simple launcher
python start_advanced_monitor.py
```

### 3. Run Tests
```powershell
# Navigate to testing directory
cd testing

# Run comprehensive tests
python deep_stress_test.py

# Run component tests
python test_monitor_components.py
```

## ✨ Key Features

### 🎯 Advanced Monitor GUI (`advanced_mt5_monitor_gui.py`)
- **Strategy Phase Tracking**: NORMAL → PULLBACK → BREAKOUT
- **Asset-Specific EMA Configurations**: Dynamic parameter loading
- **Professional Candlestick Charts**: mplfinance integration
- **Real-Time Indicator Display**: EMA, RSI, MACD with live updates
- **Multi-Asset Support**: 6 major currency pairs + precious metals

### 🔌 Professional Launcher (`launch_advanced_monitor.py`)
- **Dependency Validation**: Automatic package installation
- **Dynamic Imports**: Resolves VS Code import warnings
- **Error Handling**: Graceful degradation and user feedback
- **VS Code Integration**: Optimized for development environment

### 📊 Core Components
- **MT5 Connector**: Reliable MetaTrader 5 integration
- **Signal Adapter**: Strategy-specific parameter management
- **Strategy Suite**: Complete trading strategies for 6+ assets
- **Test Suite**: Comprehensive validation and stress testing

## 🛠️ Development Workflow

1. **Code Changes**: Edit files in `src/` or root directory
2. **Testing**: Run tests from `testing/` directory
3. **Documentation**: Update docs in `docs/` directory
4. **Strategies**: Modify trading logic in `strategies/` directory
5. **Configuration**: Adjust settings in `config/` directory

## 📈 Production Ready

✅ **Clean Architecture**: Organized directory structure  
✅ **Comprehensive Testing**: Full test coverage  
✅ **Professional Documentation**: Complete user guides  
✅ **VS Code Integration**: Optimized development environment  
✅ **Dependency Management**: Clean requirements.txt  
✅ **Error Handling**: Robust exception management  

---
*Last Updated: September 2025 - Project successfully organized and cleaned* 🎉