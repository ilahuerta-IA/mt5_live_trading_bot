# MT5 Live Trading Bot

> **Institutional-grade automated trading system implementing Ray Dalio's All-Weather Portfolio allocation**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MetaTrader 5](https://img.shields.io/badge/MetaTrader-5-green.svg)](https://www.metatrader5.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![MT5 Advanced Monitor GUI](docs/Advanced%20MT5%20Monitor.png)

---

## 🎯 What This Bot Does

**Automated trading system** for MetaTrader 5 with:
- 📊 **Ray Dalio Portfolio Allocation** - Economic scenario-based position sizing (20% USDCHF, 18% XAUUSD, 16% GBPUSD/EURUSD, 15% XAGUSD/AUDUSD)
- 🛡️ **6-Layer Entry Filters** - Validates ATR, Angle, Price, Candle Direction, EMA Ordering, and Time before every trade
- 🎨 **Real-Time GUI** - Live charts, EMA overlays, strategy states, and comprehensive monitoring
- 📈 **4-Phase State Machine** - SCANNING → ARMED → WINDOW_OPEN → ENTRY with pullback confirmation
- 💰 **MT5 Broker Integration** - Dynamic position sizing using broker-specific tick values (not hardcoded pip values)

**Trading Assets:** EURUSD, GBPUSD, XAUUSD, AUDUSD, XAGUSD, USDCHF (M5 timeframe)

---

## 🚀 Quick Start

### 1. Installation

```powershell
# Clone repository
git clone https://github.com/yourusername/mt5_live_trading_bot.git
cd mt5_live_trading_bot

# Automated setup (Windows PowerShell - Recommended)
.\setup.ps1

# OR Manual setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy MT5 credentials template
copy config\mt5_credentials_template.json config\mt5_credentials.json

# Edit with your MT5 account details
# (account number, password, server)
```

### 3. Launch

```bash
# Start the trading bot
python advanced_mt5_monitor_gui.py

# OR run executable (Windows)
dist\MT5_Trading_Bot.exe
```

---

## 📊 System Architecture

### Ray Dalio All-Weather Portfolio Allocation

**Economic scenario-based position sizing** protecting against inflation, deflation, growth, and recession:

| Asset | Allocation | Economic Role | Example Risk* |
|-------|-----------|---------------|---------------|
| **USDCHF** | 20% | Deflation hedge (safe haven) | $100.16 |
| **XAUUSD** | 18% | Inflation hedge (gold) | $90.14 |
| **GBPUSD** | 16% | Balanced growth | $80.13 |
| **EURUSD** | 16% | Balanced growth | $80.13 |
| **XAGUSD** | 15% | Commodity exposure | $75.12 |
| **AUDUSD** | 15% | Commodity currency | $75.12 |

*Based on $50,078 portfolio with 1% risk per allocation

**Key Benefit:** Maximum 1% total portfolio risk even if all 6 assets signal simultaneously (vs 6% with equal weighting)

📖 **Full Documentation:** [DALIO_ALLOCATION_SYSTEM.md](DALIO_ALLOCATION_SYSTEM.md)

---

### 6-Layer Entry Filter Cascade

Every signal must pass **ALL** filters to prevent false entries:

```
EMA Crossover Detected
    ↓
✅ [1] ATR Filter      → Volatility in valid range?
✅ [2] Angle Filter    → EMA slope meets requirements?
✅ [3] Price Filter    → Price aligned with trend?
✅ [4] Candle Filter   → Previous candle confirms momentum?
✅ [5] EMA Ordering    → Multi-EMA sequence correct?
✅ [6] Time Filter     → Within trading hours?
    ↓
ALL PASSED → ARMED State → Pullback → Window → Entry
ANY FAILED → REJECTED (stay in SCANNING)
```

**Impact:** Reduces entries from ~240/month to ~2-3/month per asset (matches backtesting)

📊 **Filter Configuration:** [FILTER_CONFIGURATION.md](docs/archive/FILTER_CONFIGURATION.md)

---

### 4-Phase State Machine

```
┌─────────────────────────────────────────────────────────────┐
│ SCANNING → Monitoring for valid crossovers (6-layer check) │
└─────────────────────────────────────────────────────────────┘
                          ↓ All filters pass
┌─────────────────────────────────────────────────────────────┐
│ ARMED → Waiting for pullback confirmation (1-3 candles)    │
│   ⚠️ Global invalidation: Counter-crossover resets state   │
└─────────────────────────────────────────────────────────────┘
                          ↓ Pullback complete
┌─────────────────────────────────────────────────────────────┐
│ WINDOW_OPEN → 2-sided breakout window active (1-20 bars)   │
│   Success boundary → Execute trade                          │
│   Failure boundary → Reset to SCANNING                      │
└─────────────────────────────────────────────────────────────┘
                          ↓ Breakout detected
┌─────────────────────────────────────────────────────────────┐
│ ENTRY → Trade executed with ATR-based SL/TP                │
└─────────────────────────────────────────────────────────────┘
```

📚 **Case Studies:** [COMPREHENSIVE_STRATEGY_VERIFICATION.md](docs/archive/COMPREHENSIVE_STRATEGY_VERIFICATION.md)

---

## 🔧 Critical Features & Fixes

### ✅ Position Sizing Fix (v2.1.0 - November 10, 2025)

**CRITICAL BUG FIXED:** Now uses MT5 broker-specific tick values instead of hardcoded pip values

**Before (BROKEN):**
```python
# Hardcoded standard lot assumptions
GBPUSD: Risk $22.70 instead of $80.13 (3.53x too small) ❌
XAGUSD: Risk $0.46 instead of $75.12 (163x too small!) ❌
```

**After (FIXED):**
```python
# Dynamic broker-specific calculation
tick_value = mt5.symbol_info(symbol).trade_tick_value  # Real broker specs
value_per_point = tick_value × (point / tick_size)
lot_size = risk_amount / (sl_distance × value_per_point)  ✅
```

**Enhanced Logging:** Every trade now shows 5 sections:
1. 📋 Broker specifications (contract size, tick value, digits)
2. 💰 Dalio allocation (balance, asset %, risk amount)
3. 🎯 Stop loss (SL distance in points, ATR multiplier)
4. 🧮 Lot size calculation (step-by-step formula)
5. ✅ Risk verification (confirms calculated risk matches expected)

📖 **Technical Details:** [POSITION_SIZING_FIX_V2.md](docs/archive/POSITION_SIZING_FIX_V2.md)

---

### ✅ Pullback System Fix (v2.0.1 - November 11, 2025)

**CRITICAL BUG FIXED:** Bot was ignoring `LONG_USE_PULLBACK_ENTRY` configuration flag

**Impact:**
- EURUSD: Should enter immediately on crossover (flag = False) but was forced into pullback mode ❌
- XAUUSD: Showing 2 pullback candles when config requires 3 ❌

**Solution:**
- Added flag check with branching logic (STANDARD vs PULLBACK mode)
- Created `_execute_entry()` method for immediate entries
- Enhanced configuration logging at startup

📖 **Full Analysis:** [PULLBACK_SYSTEM_FIX.md](docs/PULLBACK_SYSTEM_FIX.md)

---

### ✅ ATR Filter Implementation (v1.1.0 - October 31, 2025)

**CRITICAL BUG FIXED:** ATR filter was not validating entries due to missing dataframe integration

**Impact:** Reduced entries from ~240/month to ~2-3/month per asset (matches backtesting)

📖 **Details:** [docs/ATR_FILTER_FIX.md](docs/ATR_FILTER_FIX.md)

---

## 📁 Project Structure

```
mt5_live_trading_bot/
├── advanced_mt5_monitor_gui.py    # Main bot (3,500+ lines)
├── requirements.txt               # Python dependencies
├── setup.ps1                      # Automated setup
├── build_exe.bat                  # Build Windows executable
│
├── config/                        # Configuration
│   ├── mt5_credentials_template.json
│   └── mt5_credentials.json       # (your credentials - gitignored)
│
├── strategies/                    # Asset-specific parameters
│   ├── sunrise_ogle_eurusd.py     # EURUSD strategy (READ-ONLY)
│   ├── sunrise_ogle_gbpusd.py     # GBPUSD strategy (READ-ONLY)
│   ├── sunrise_ogle_xauusd.py     # XAUUSD strategy (READ-ONLY)
│   ├── sunrise_ogle_audusd.py     # AUDUSD strategy (READ-ONLY)
│   ├── sunrise_ogle_xagusd.py     # XAGUSD strategy (READ-ONLY)
│   └── sunrise_ogle_usdchf.py     # USDCHF strategy (READ-ONLY)
│
├── testing/                       # Test suite
│   ├── test_setup.py              # Verify installation
│   ├── test_monitor_components.py # GUI tests
│   ├── test_mt5_order.py          # Order execution test
│   ├── check_broker_specs.py      # Broker verification
│   ├── test_position_sizing.py    # Position sizing tests
│   └── verify_all_symbols.py      # Symbol configuration check
│
├── docs/                          # Documentation
│   ├── README.md                  # Documentation index
│   ├── START_TESTING_HERE.md      # Quick start guide
│   └── archive/                   # Historical docs
│
└── logs/                          # Application logs (gitignored)
```

---

## 📚 Documentation

### 🎯 Essential Reading (Start Here)

1. **[DALIO_QUICK_REFERENCE.md](DALIO_QUICK_REFERENCE.md)** - Position sizing quick reference
2. **[FILTER_CONFIGURATION.md](docs/archive/FILTER_CONFIGURATION.md)** - Entry filter matrix
3. **[docs/START_TESTING_HERE.md](docs/START_TESTING_HERE.md)** - Testing guide

### 📖 Core Documentation

4. **[DALIO_ALLOCATION_SYSTEM.md](DALIO_ALLOCATION_SYSTEM.md)** - Complete Ray Dalio implementation
5. **[COMPREHENSIVE_STRATEGY_VERIFICATION.md](docs/archive/COMPREHENSIVE_STRATEGY_VERIFICATION.md)** - 1,500+ line verification (MT5 vs Backtrader)
6. **[STRATEGY_FILES_POLICY.md](STRATEGY_FILES_POLICY.md)** - READ-ONLY policy for strategy files

### 🔧 Technical Documentation

7. **[POSITION_SIZING_FIX_V2.md](docs/archive/POSITION_SIZING_FIX_V2.md)** - Position sizing fix (MT5 tick value integration)
8. **[PULLBACK_SYSTEM_FIX.md](docs/PULLBACK_SYSTEM_FIX.md)** - Pullback flag check implementation
9. **[DEEP_STRATEGY_ANALYSIS_NOV14.md](docs/DEEP_STRATEGY_ANALYSIS_NOV14.md)** - 25-page session analysis
10. **[docs/](docs/)** - Additional guides (EMA setup, pullback fixes, etc.)

---

## 🧪 Testing

### Quick Verification

```bash
# 1. Installation check
cd testing
python test_setup.py

# 2. Broker specifications
python check_broker_specs.py

# 3. Position sizing validation
python test_position_sizing.py

# 4. Symbol configuration check
python verify_all_symbols.py
```

### Order Execution Test (⚠️ Places Real Orders)

```bash
cd testing
python test_mt5_order.py  # Basic order test
```

**Always use demo accounts for testing!**

---

## ⚙️ Configuration

### MT5 Credentials (`config/mt5_credentials.json`)

```json
{
  "account": 12345678,
  "password": "YourPassword",
  "server": "YourBroker-Demo"
}
```

### Strategy Parameters

Each strategy file in `strategies/` contains:
- EMA periods (Fast, Medium, Slow, Filter)
- ATR multipliers (SL: 4.5x, TP: 6.5x default)
- Pullback requirements (1-3 candles)
- Window duration (1-20 bars)
- Trading hours (UTC)
- Filter thresholds (ATR, Angle, etc.)

**⚠️ IMPORTANT:** Strategy files are **READ-ONLY** to preserve backtesting integrity. See [STRATEGY_FILES_POLICY.md](STRATEGY_FILES_POLICY.md)

---

## 🛡️ Risk Management

### Safety Features

- ✅ **Ray Dalio Allocation** - Maximum 1% portfolio risk across all assets
- ✅ **6-Layer Filters** - Validates every signal before entry
- ✅ **ATR-Based SL/TP** - Dynamic stop loss (4.5x ATR) and take profit (6.5x ATR)
- ✅ **MT5 Broker Integration** - Uses actual tick values (not hardcoded)
- ✅ **Global Invalidation** - Counter-trend crossovers reset armed states
- ✅ **Duplicate Prevention** - Checks existing positions before entry
- ✅ **Time Filters** - Trading hour restrictions per asset

### Warnings

⚠️ **Never risk more than you can afford to lose**  
⚠️ **Understand the system completely before live trading**  
⚠️ **Start with minimum position sizes on demo accounts**  
⚠️ **Keep detailed logs of all trading activity**  
⚠️ **Strategy files are READ-ONLY** - Preserve backtesting integrity

---

## 🎨 GUI Features

### Real-Time Monitoring

- **Asset Dashboard** - Price, state, pullback count, window status
- **Live Charts** - Candlesticks with EMA overlays (Fast, Medium, Slow, Filter)
- **Strategy States** - Color-coded phase indicators (SCANNING, ARMED, WINDOW_OPEN)
- **Configuration Viewer** - Complete strategy parameters and filter details
- **Terminal Logging** - Real-time event log with timestamps

### Chart Controls

- **Symbol Selection** - Switch between 6 monitored assets
- **Timeframe** - M5 (5-minute candles)
- **Indicators** - EMA overlays, volume bars
- **Window Markers** - Shows breakout boundaries when window active

---

## 🔍 Troubleshooting

### MT5 Connection Failed

```
✓ Ensure MT5 terminal is running and logged in
✓ Verify credentials in config/mt5_credentials.json
✓ Check MetaTrader5 Python package installed
✓ Restart MT5 terminal
```

### No Signals Detected

```
✓ Confirm market is open for selected assets
✓ Check if price data streaming (see logs/)
✓ Review filter thresholds (may be too strict)
✓ Verify strategy files loaded (check terminal)
```

### Position Sizing Issues

```
✓ Run testing/check_broker_specs.py
✓ Verify MT5 account balance fetched correctly
✓ Check logs for broker specifications section
✓ Confirm tick_value matches broker's contract specs
```

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. **Read [STRATEGY_FILES_POLICY.md](STRATEGY_FILES_POLICY.md)** - Strategy files are READ-ONLY
4. Test on demo account thoroughly
5. Document changes and include test results
6. Submit Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## ⚖️ Disclaimer

**This software is for educational purposes only.**

Trading financial instruments carries high risk and may not be suitable for all investors. No representation is made that any account will achieve profits or losses similar to those shown. Past performance is not indicative of future results.

**The developers assume no responsibility for your trading results. Use at your own risk.**

---

## 🙏 Acknowledgments

- MetaTrader 5 Python API
- Ray Dalio's All-Weather Portfolio principles
- mplfinance for financial charts
- Backtrader for strategy development

---

**⚡ Happy Trading! Trade with institutional-grade risk management!**
