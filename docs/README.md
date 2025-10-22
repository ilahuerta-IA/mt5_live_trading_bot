# MT5 Live Trading Bot - Documentation

**Last Updated:** October 22, 2025

## 📚 Current Documentation

This folder contains the **essential documentation** for the MT5 Live Trading Bot. Historical and intermediate fix documentation has been moved to the `archive/` subfolder.

---

## 🚀 Getting Started

- **[START_TESTING_HERE.md](START_TESTING_HERE.md)** - Quick start guide for testing the bot
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Project organization and file structure

---

## 🔧 Critical Fixes (Current)

### Pullback Detection
- **[PULLBACK_FIX_SUMMARY.md](PULLBACK_FIX_SUMMARY.md)** - Complete summary of all 7 pullback bugs fixed
- **[CRITICAL_BUG_DOUBLE_CANDLE_REMOVAL_FIX.md](CRITICAL_BUG_DOUBLE_CANDLE_REMOVAL_FIX.md)** - Root cause fix (Bug 6)
- **[ENHANCED_PULLBACK_LOGGING.md](ENHANCED_PULLBACK_LOGGING.md)** - Export-ready logging system

### EMA Calculations
- **[EMA_STABILITY_FIX_CRITICAL.md](EMA_STABILITY_FIX_CRITICAL.md)** - 500 bars + adjust=False fix
- **[EMA_CHART_VISUALIZATION_FIX.md](EMA_CHART_VISUALIZATION_FIX.md)** - Chart stabilization periods
- **[EMA_DISPLAY_PRECISION_FIX.md](EMA_DISPLAY_PRECISION_FIX.md)** - Dynamic symbol precision

### Other Improvements
- **[TIME_FILTER_AND_CHART_IMPROVEMENTS.md](TIME_FILTER_AND_CHART_IMPROVEMENTS.md)** - Backtrader compliance + Plotly-style navigation
- **[TYPE_CHECKING_FIXES_COMPLETE.md](TYPE_CHECKING_FIXES_COMPLETE.md)** - Resolved 29 type errors

---

## 📖 Setup Guides

### MT5 Configuration
- **[MT5_EMA_QUICK_SETUP.md](MT5_EMA_QUICK_SETUP.md)** - 5-minute EMA setup for MT5
- **[MT5_EMA_SETUP_GUIDE.md](MT5_EMA_SETUP_GUIDE.md)** - Detailed EMA configuration guide
- **[MT5_HISTORICAL_DATA_SETUP.md](MT5_HISTORICAL_DATA_SETUP.md)** - Historical data configuration

---

## 🤝 Contributing

- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[PRE_UPLOAD_CHECKLIST.md](PRE_UPLOAD_CHECKLIST.md)** - Pre-commit checklist
- **[GITHUB_UPLOAD_GUIDE.md](GITHUB_UPLOAD_GUIDE.md)** - GitHub upload instructions

---

## 📦 Archived Documentation

Old documentation, intermediate fixes, and historical testing results have been moved to the **`archive/`** subfolder to keep the main docs folder clean and focused on current, essential information.

### Archived Files (29 files)
- Old README versions and cleanup documentation (5 files)
- Intermediate pullback bug fixes (8 files)
- Testing results and guides (3 files)
- Intermediate fix documentation (7 files)
- Verification/completion status files (6 files)

These files are preserved for historical reference but are not needed for day-to-day use.

---

## 📊 Documentation Structure

```
docs/
├── README.md (this file)
├── START_TESTING_HERE.md
├── PROJECT_STRUCTURE.md
│
├── Critical Fixes/
│   ├── PULLBACK_FIX_SUMMARY.md
│   ├── CRITICAL_BUG_DOUBLE_CANDLE_REMOVAL_FIX.md
│   ├── ENHANCED_PULLBACK_LOGGING.md
│   ├── EMA_STABILITY_FIX_CRITICAL.md
│   ├── EMA_CHART_VISUALIZATION_FIX.md
│   ├── EMA_DISPLAY_PRECISION_FIX.md
│   ├── TIME_FILTER_AND_CHART_IMPROVEMENTS.md
│   └── TYPE_CHECKING_FIXES_COMPLETE.md
│
├── Setup Guides/
│   ├── MT5_EMA_QUICK_SETUP.md
│   ├── MT5_EMA_SETUP_GUIDE.md
│   └── MT5_HISTORICAL_DATA_SETUP.md
│
├── Contributing/
│   ├── CONTRIBUTING.md
│   ├── PRE_UPLOAD_CHECKLIST.md
│   └── GITHUB_UPLOAD_GUIDE.md
│
└── archive/ (29 historical files)
    ├── README_OLD.md
    ├── PULLBACK_DETECTION_FIX.md
    ├── TESTING_RESULTS_20251015.md
    └── ... (26 more files)
```

---

## ✅ What's Working

After all fixes (as of October 22, 2025):

- ✅ **Pullback Detection:** All 7 bugs fixed, root cause eliminated
- ✅ **EMA Calculations:** Stable, accurate, MT5-aligned
- ✅ **Chart Navigation:** Plotly-style interactive controls
- ✅ **Type Safety:** 29 errors resolved
- ✅ **Logging:** Export-ready terminal logs with OHLC data
- ✅ **State Machine:** Full progression (SCANNING → ARMED → WINDOW → ENTRY)

---

## 🎯 Key Files for New Users

1. **[START_TESTING_HERE.md](START_TESTING_HERE.md)** - Begin here
2. **[PULLBACK_FIX_SUMMARY.md](PULLBACK_FIX_SUMMARY.md)** - Understand the fixes
3. **[MT5_EMA_QUICK_SETUP.md](MT5_EMA_QUICK_SETUP.md)** - Set up MT5
4. **[ENHANCED_PULLBACK_LOGGING.md](ENHANCED_PULLBACK_LOGGING.md)** - Export logs for analysis

---

**Repository:** [mt5_live_trading_bot](https://github.com/ilahuerta-IA/mt5_live_trading_bot)  
**Owner:** ilahuerta-IA  
**License:** See LICENSE file
