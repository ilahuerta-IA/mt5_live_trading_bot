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
- **🎯 Advanced Entry Filters** - 6-layer validation system (ATR, Angle, Price, Candle, EMA Order, Time)

## 🆕 Recent Updates (November 2025)

### Ray Dalio All-Weather Portfolio Allocation System
**Version:** v2.0.0 | **Date:** November 5, 2025

**Revolutionary position sizing system** implementing Ray Dalio's All-Weather Portfolio principles with asset-specific allocations based on economic scenario hedging.

**Why This Matters:**
The previous equal-risk system (1% of total portfolio per asset) ignored economic diversification principles. The new system allocates capital based on each asset's role in protecting against different economic scenarios.

**Asset Allocations:**
- 🛡️ **USDCHF (20%)** - Deflation hedge (safe haven currency)
- 🥇 **XAUUSD (18%)** - Inflation hedge (gold standard)
- 💱 **GBPUSD/EURUSD (16% each)** - Standard forex exposure
- 🪙 **XAGUSD/AUDUSD (15% each)** - Commodity/commodity currency

**Key Benefits:**
- ✅ **XAGUSD Lot Size Fix**: Proper 15% commodity allocation (was too small with equal risk)
- ✅ **Portfolio Risk Control**: Maximum 1% total risk even if all 6 assets signal simultaneously
- ✅ **Economic Diversification**: Protection against inflation, deflation, growth, and recession
- ✅ **Real-Time Balance**: Fetches current MT5 balance for accurate calculations

**Example with $50,078.20 balance:**
```python
USDCHF: $10,015.64 allocated → $100.16 risk per trade (20%)
XAUUSD: $9,014.08 allocated → $90.14 risk per trade (18%)
GBPUSD: $8,012.51 allocated → $80.13 risk per trade (16%)
XAGUSD: $7,511.73 allocated → $75.12 risk per trade (15%)
```

**Old vs New:**
- **OLD**: All assets risk $500.78 (1% of total) → 6% portfolio risk if all signal
- **NEW**: Assets risk $75-$100 (1% of allocated) → 1% portfolio risk maximum

📖 **Learn More:** 
- [DALIO_ALLOCATION_SYSTEM.md](DALIO_ALLOCATION_SYSTEM.md) - Complete implementation guide
- [DALIO_QUICK_REFERENCE.md](DALIO_QUICK_REFERENCE.md) - Quick reference for live trading

---

### Critical Bug Fix: ATR Filter Implementation
**Version:** v1.1.0 | **Date:** October 31, 2025

A critical issue was identified and fixed where the ATR (Average True Range) volatility filter was not validating entry signals due to missing dataframe column integration. This resulted in significantly more entries than expected.

**What Was Fixed:**
- ✅ ATR column now properly added to validation dataframe
- ✅ ATR filter now correctly rejects high-volatility crossovers
- ✅ Expected reduction in entries from ~10/day to ~0.5/day (per backtesting targets)
- ✅ All 6 entry filters now functioning correctly:
  1. **ATR Filter** - Volatility range validation (NOW WORKING)
  2. **Angle Filter** - EMA slope requirements
  3. **Price Filter** - Trend alignment validation
  4. **Candle Direction** - Momentum confirmation
  5. **EMA Ordering** - EMA sequence validation
  6. **Time Filter** - Trading hours restrictions

**Impact:** Entry rate should now match backtesting results (~2-3 entries/month per asset vs previous 240/month).

**For Users:** Simply pull the latest version and restart the bot. No configuration changes needed.

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

### Ray Dalio All-Weather Portfolio Allocation

This bot implements **economic scenario-based position sizing** following Ray Dalio's All-Weather Portfolio principles:

**Position Sizing Formula:**
```python
# For each asset:
allocated_capital = portfolio_balance × asset_allocation_percentage
risk_per_trade = allocated_capital × risk_percentage (default 1%)
lot_size = risk_per_trade / (stop_loss_distance × pip_value)
```

**Allocation Strategy:**

| Economic Scenario | Assets | Allocation | Purpose |
|------------------|--------|-----------|---------|
| **Deflation** | USDCHF | 20% | Safe haven currency preservation |
| **Inflation** | XAUUSD | 18% | Gold standard protection |
| **Balanced Growth** | GBPUSD, EURUSD | 16% each | Standard forex exposure |
| **Commodity Boom** | XAGUSD, AUDUSD | 15% each | Industrial/resource exposure |

**Maximum Risk Control:**
- If all 6 assets signal simultaneously: **1% total portfolio risk** (vs 6% with equal weighting)
- Real-time MT5 balance fetching ensures accurate calculations
- Configurable risk percentage per asset (default 1% of allocated capital)

📖 **Full Documentation:** [DALIO_ALLOCATION_SYSTEM.md](DALIO_ALLOCATION_SYSTEM.md)

### 6-Layer Entry Filter System

Every potential entry signal must pass **ALL 6 validation filters** to prevent false signals:

| Filter | Purpose | Example Thresholds |
|--------|---------|-------------------|
| **1. ATR Filter** | Volatility range validation | Min: 0.0001, Max: 0.0020 |
| **2. Angle Filter** | EMA slope requirements | Min: 2°, Max: 45° |
| **3. Price Filter** | Trend alignment check | Close > EMA_filter (LONG) |
| **4. Candle Direction** | Momentum confirmation | Previous candle bullish (LONG) |
| **5. EMA Ordering** | Multi-EMA sequence | Confirm > Fast > Med > Slow |
| **6. Time Filter** | Trading hours restriction | UTC 00:00 - 23:59 (configurable) |

**Filter Validation Logic:**
```python
# All filters must return True for entry signal
entry_valid = (
    atr_filter_pass AND
    angle_filter_pass AND
    price_filter_pass AND
    candle_direction_pass AND
    ema_ordering_pass AND
    time_filter_pass
)
```

**Expected Impact:**
- **Without filters**: ~240 entries/month per asset ❌
- **With all 6 filters**: ~2-3 entries/month per asset ✅ (matches backtesting)

📊 **Filter Configuration Matrix:** [FILTER_CONFIGURATION.md](FILTER_CONFIGURATION.md)

### Safety Features
- **Demo Account Testing**: Always test on demo accounts first
- **Position Sizing**: Ray Dalio allocation-based (see above)
- **Stop Loss**: ATR-based dynamic stop loss (4.5x ATR default)
- **Take Profit**: ATR-based targets (6.5x ATR default)
- **Time Filters**: Trading hour restrictions per asset
- **Trend Confirmation**: Multi-EMA validation with 6-layer filtering
- **Duplicate Prevention**: Checks existing positions before entry

### Important Warnings
⚠️ **Never risk more than you can afford to lose**  
⚠️ **Understand the system completely before live trading**  
⚠️ **Start with minimum position sizes**  
⚠️ **Keep detailed logs of all trading activity**  
⚠️ **Regularly review strategy performance**  
⚠️ **Strategy files are READ-ONLY** - See [STRATEGY_FILES_POLICY.md](STRATEGY_FILES_POLICY.md)

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

### 🎯 Essential Reading (Start Here)

**For New Users:**
1. **[START_TESTING_HERE.md](docs/START_TESTING_HERE.md)** - Quick start guide for testing
2. **[DALIO_QUICK_REFERENCE.md](DALIO_QUICK_REFERENCE.md)** - Position sizing quick reference
3. **[FILTER_CONFIGURATION.md](FILTER_CONFIGURATION.md)** - Entry filter matrix and settings

**Understanding the System:**
4. **[DALIO_ALLOCATION_SYSTEM.md](DALIO_ALLOCATION_SYSTEM.md)** - Complete Ray Dalio allocation guide
   - Economic scenario hedging explained
   - Position sizing formulas and examples
   - Old vs new system comparison
   - Testing procedures and verification

5. **[COMPREHENSIVE_STRATEGY_VERIFICATION.md](COMPREHENSIVE_STRATEGY_VERIFICATION.md)** - 1,500+ line deep-dive
   - MT5 vs Backtrader implementation comparison
   - Line-by-line code verification
   - 2 live trade case studies (100% match validation)
   - State machine logic documentation

6. **[STRATEGY_FILES_POLICY.md](STRATEGY_FILES_POLICY.md)** - READ-ONLY policy for strategy files
   - Why strategy files remain unchanged
   - Backtesting integrity preservation
   - Where to make configuration changes

### 🔧 Technical Documentation

**Bug Fixes & Updates:**
- **[PULLBACK_FIX_SUMMARY.md](docs/PULLBACK_FIX_SUMMARY.md)** - Critical bug fixes (October 2025)
- **[EMA_STABILITY_FIX_CRITICAL.md](docs/EMA_STABILITY_FIX_CRITICAL.md)** - EMA calculation improvements
- **[ATR_FILTER_FIX.md](docs/ATR_FILTER_FIX.md)** - ATR validation bug fix (October 31, 2025)
- **[FIXES_SUMMARY.md](FIXES_SUMMARY.md)** - Complete fixes documentation (5 critical improvements)

**System Architecture:**
- **[ENHANCED_PULLBACK_LOGGING.md](docs/ENHANCED_PULLBACK_LOGGING.md)** - Export-ready logging system
- **[docs/README.md](docs/README.md)** - Complete documentation index and navigation
- **Setup Guides** - MT5 configuration and EMA alignment (see docs/)

### 📊 Strategy & Filters

**Entry Validation System:**

The bot uses a **6-layer filter cascade** where signals must pass ALL checks:

```
EMA Crossover Detected
    ↓
[1] ATR Filter → Volatility in range? → ✅/❌
    ↓
[2] Angle Filter → EMA slope valid? → ✅/❌
    ↓
[3] Price Filter → Trend aligned? → ✅/❌
    ↓
[4] Candle Direction → Momentum confirmed? → ✅/❌
    ↓
[5] EMA Ordering → Sequence correct? → ✅/❌
    ↓
[6] Time Filter → Within trading hours? → ✅/❌
    ↓
ALL PASSED → ARMED State (proceed to pullback)
ANY FAILED → REJECTED (stay in SCANNING)
```

**Filter Details:**
- **ATR Filter**: Prevents entries during extreme volatility or dead markets
- **Angle Filter**: Ensures EMA trend strength (2° - 45° range typical)
- **Price Filter**: Confirms price on correct side of filter EMA
- **Candle Direction**: Validates previous candle momentum
- **EMA Ordering**: Checks EMA sequence (Confirm > Fast > Med > Slow for LONG)
- **Time Filter**: Restricts entries to specific UTC hours

**Configuration Files:**
- Each asset has individual filter thresholds in `strategies/sunrise_ogle_*.py`
- Filter matrix visualization: [FILTER_CONFIGURATION.md](FILTER_CONFIGURATION.md)
- Live trades analysis: [COMPREHENSIVE_STRATEGY_VERIFICATION.md](COMPREHENSIVE_STRATEGY_VERIFICATION.md)

### 🎓 Learning Resources

**Understanding Portfolio Theory:**
- Ray Dalio's All-Weather Portfolio: [DALIO_ALLOCATION_SYSTEM.md](DALIO_ALLOCATION_SYSTEM.md#-allocation-strategy)
- Economic scenario hedging: Inflation, Deflation, Growth, Recession protection
- Asset correlation principles: Why USDCHF + XAUUSD + Forex + Commodities

**4-Phase State Machine:**
```
SCANNING → Monitoring for valid EMA crossovers with 6-layer validation
    ↓
ARMED → Crossover passed all filters, waiting for pullback (1-3 candles)
    ↓
WINDOW_OPEN → Pullback confirmed, 2-sided breakout window active
    ↓
ENTRY → Price breaks success boundary → Trade executed
```

**Advanced Topics:**
- Global invalidation: Counter-trend crossovers reset ARMED states
- Window mechanics: Time offset + price offset + duration
- ATR-based SL/TP: Dynamic risk management based on volatility

### 📁 Documentation Structure

```
mt5_live_trading_bot/
├── README.md (you are here)
├── DALIO_ALLOCATION_SYSTEM.md          ⭐ Portfolio allocation guide
├── DALIO_QUICK_REFERENCE.md            ⭐ Quick calculations
├── FILTER_CONFIGURATION.md             ⭐ Filter matrix
├── COMPREHENSIVE_STRATEGY_VERIFICATION.md  ⭐ Deep verification
├── STRATEGY_FILES_POLICY.md            ⭐ READ-ONLY policy
├── FIXES_SUMMARY.md                    Critical fixes log
│
└── docs/
    ├── README.md                       Documentation index
    ├── START_TESTING_HERE.md           Quick start
    ├── PULLBACK_FIX_SUMMARY.md
    ├── EMA_STABILITY_FIX_CRITICAL.md
    ├── ATR_FILTER_FIX.md
    ├── ENHANCED_PULLBACK_LOGGING.md
    └── archive/                        Historical docs
```

**Note:** Historical and intermediate documentation preserved in `docs/archive/` for reference.

## 🧠 Key Concepts for Understanding This Bot

### 1. **Ray Dalio All-Weather Portfolio Philosophy**

This bot doesn't just trade—it applies **institutional-grade portfolio theory** to retail trading:

**The Problem It Solves:**
Traditional equal-risk systems treat all assets the same, ignoring economic cycles. If all 6 assets signal at once with 1% risk each, you're exposed to 6% portfolio risk.

**The Solution:**
Asset-specific allocations based on economic role:
- **20% to deflation protection** (USDCHF - safe haven)
- **18% to inflation protection** (XAUUSD - gold)
- **16% to balanced markets** (GBPUSD, EURUSD - liquid forex)
- **15% to commodity exposure** (XAGUSD, AUDUSD - growth/resources)

**Result:** Maximum 1% portfolio risk even if all assets signal simultaneously, with diversified economic scenario coverage.

📖 **Deep Dive:** [DALIO_ALLOCATION_SYSTEM.md](DALIO_ALLOCATION_SYSTEM.md)

---

### 2. **6-Layer Entry Filter Cascade**

**Why So Many Filters?**
Backtrader (backtesting engine) called `next()` only on **closed candles**. Live trading checks every tick, creating hundreds of false crossovers from recalculating EMAs with forming candle data.

**The Filter Solution:**
Every signal must pass 6 consecutive validation checks:

```python
# Pseudocode logic
if crossover_detected:
    if not atr_valid:      return REJECT  # Filter 1: Volatility
    if not angle_valid:    return REJECT  # Filter 2: EMA slope
    if not price_valid:    return REJECT  # Filter 3: Trend alignment
    if not candle_valid:   return REJECT  # Filter 4: Momentum
    if not ema_order_valid: return REJECT # Filter 5: EMA sequence
    if not time_valid:     return REJECT  # Filter 6: Trading hours
    
    return ARMED_STATE  # All filters passed → Proceed
```

**Impact:**
- Without filters: ~240 entries/month per asset ❌
- With 6-layer cascade: ~2-3 entries/month per asset ✅
- Matches backtesting results exactly

📊 **Filter Matrix:** [FILTER_CONFIGURATION.md](FILTER_CONFIGURATION.md)

---

### 3. **4-Phase State Machine Architecture**

The bot doesn't just detect crossovers—it implements a **sophisticated entry confirmation system**:

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: SCANNING                                               │
│ → Monitoring price for EMA crossovers                           │
│ → Validates against 6-layer filter cascade                      │
│ → If ALL filters pass: Move to ARMED                            │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2: ARMED (LONG or SHORT)                                  │
│ → Crossover confirmed, now waiting for pullback                 │
│ → Counts 1-3 counter-trend candles                              │
│ → Global invalidation: Opposing crossover resets to SCANNING    │
│ → When pullback complete: Open window                           │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3: WINDOW_OPEN                                            │
│ → 2-sided breakout window active (success + failure boundaries) │
│ → Duration: Configurable bars (e.g., 20 candles)                │
│ → Optional time offset before window starts                     │
│ → Monitoring for price breakout                                 │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 4: ENTRY DETECTION                                        │
│ → Price breaks success boundary → EXECUTE TRADE                 │
│ → Price breaks failure boundary → RESET TO SCANNING             │
│ → Window expires → RESET TO SCANNING                            │
└─────────────────────────────────────────────────────────────────┘
```

**Why This Works:**
- **Pullback confirmation** prevents chasing runaway trends
- **Window mechanics** create defined risk zones
- **Global invalidation** adapts to changing market conditions
- **Failure boundaries** exit bad setups early

📚 **Case Studies:** [COMPREHENSIVE_STRATEGY_VERIFICATION.md](COMPREHENSIVE_STRATEGY_VERIFICATION.md)

---

### 4. **Strategy Files Policy: READ-ONLY**

**Critical Rule:** Files in `strategies/sunrise_ogle_*.py` are **NEVER modified** after backtesting.

**Why?**
These files represent **backtested parameter sets** that achieved specific performance metrics. Changing them invalidates backtesting results and makes it impossible to verify if live performance matches expectations.

**Where to Configure:**
- **Position sizing:** Modified in `advanced_mt5_monitor_gui.py` (Ray Dalio allocations)
- **Live monitoring:** Settings in GUI monitor (not strategy files)
- **Risk parameters:** Can override `RISK_PER_TRADE` in strategy config comments

**Exception Handling:**
If strategy file changes are needed (e.g., critical bug fix), use 2-commit approach:
1. Commit WITH changes (document what and why)
2. Immediately commit REVERT to restore originals

📋 **Full Policy:** [STRATEGY_FILES_POLICY.md](STRATEGY_FILES_POLICY.md)

---

### 5. **MT5 vs Backtrader: Implementation Parity**

**The Challenge:**
Backtrader (Python backtesting) and MT5 (C++ live trading) are completely different environments. Ensuring they produce identical signals requires extreme precision.

**Our Solution:**
1,500+ line verification document comparing:
- Line-by-line code logic
- Indicator calculations (EMA, ATR)
- Filter validation sequences
- State transitions
- Entry/exit mechanics

**Validation:**
- ✅ GBPUSD trade: 100% match (price, time, indicators)
- ✅ XAGUSD trade: 100% match (all parameters verified)
- ✅ Both environments produce identical decisions

📊 **Full Verification:** [COMPREHENSIVE_STRATEGY_VERIFICATION.md](COMPREHENSIVE_STRATEGY_VERIFICATION.md)

---

### 6. **Real-Time Balance Integration**

**Important:** The bot fetches **live MT5 account balance** before every trade:

```python
account_info = mt5.account_info()
balance = account_info.balance  # Real-time, not cached

# Calculate with current balance
allocated_capital = balance × asset_allocation
risk_amount = allocated_capital × risk_percentage
```

**Why This Matters:**
- Account grows → Position sizes increase automatically
- Account shrinks → Position sizes decrease (risk control)
- No manual reconfiguration needed
- Always matches current portfolio state

---

### 7. **Understanding the Logs**

When the bot executes a trade, you'll see:

```
💰 USDCHF: Dalio Allocation System
   Portfolio Balance: $50,078.20
   Asset Allocation: 20% = $10,015.64
   Risk Per Trade: 1.0% of allocated = $100.16

💰 USDCHF: Position Sizing Calculation:
   Allocated: $10,015.64 (20% of $50,078.20) | Risk: 1.0% = $100.16
   SL Distance: 0.00450 price units (450.0 points)
   Contract Size: 100000 | Tick Value: $1.00 | Value/Point: $10.00
   Calculated Volume: 0.022258 lots (BEFORE limits)
   Final Volume: 0.020000 lots (min=0.01, max=500.0, step=0.01)
```

**How to Verify:**
1. **Balance check**: Matches MT5 account balance? ✅
2. **Allocation check**: 20% for USDCHF? ✅
3. **Risk check**: $10,015.64 × 1% = $100.16? ✅
4. **Lot size**: Makes sense for SL distance? ✅

📖 **Quick Reference:** [DALIO_QUICK_REFERENCE.md](DALIO_QUICK_REFERENCE.md)

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

**Before Contributing:**
- ✅ Read [STRATEGY_FILES_POLICY.md](STRATEGY_FILES_POLICY.md) - Strategy files are READ-ONLY
- ✅ Review [COMPREHENSIVE_STRATEGY_VERIFICATION.md](COMPREHENSIVE_STRATEGY_VERIFICATION.md) - Understand implementation
- ✅ Test changes on demo account first
- ✅ Document why changes are needed
- ✅ Include test results in PR description

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
