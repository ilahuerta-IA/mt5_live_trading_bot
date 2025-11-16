# MT5 Live Trading Bot - Documentation Index

> **Complete documentation library for the automated trading system**

**Last Updated:** November 16, 2025

---

## 🎯 Quick Navigation

### 🚀 Getting Started (Start Here)

1. **[START_TESTING_HERE.md](START_TESTING_HERE.md)** - Your first stop for system verification
2. **[MT5_EMA_QUICK_SETUP.md](MT5_EMA_QUICK_SETUP.md)** - Add EMAs to MT5 charts (2 minutes)
3. **[MT5_EMA_SETUP_GUIDE.md](MT5_EMA_SETUP_GUIDE.md)** - Detailed EMA configuration

### 📊 Core Strategy Documentation

4. **[DEEP_STRATEGY_ANALYSIS_NOV14.md](DEEP_STRATEGY_ANALYSIS_NOV14.md)** ⭐ - 25-page comprehensive analysis (4+ hour session, 54 crossovers analyzed)
5. **[ENTRY_CONDITIONS_VERIFICATION.md](ENTRY_CONDITIONS_VERIFICATION.md)** - 6-layer filter validation (590 lines)
6. **[PULLBACK_SYSTEM_FIX.md](PULLBACK_SYSTEM_FIX.md)** - Critical pullback flag fix (Nov 11, 2025)

---

## 🔧 Critical Fixes & Updates

### ⚠️ Must-Read Fixes (Production-Critical)

- **[ATR_BUG_FIX_COMPLETE.md](ATR_BUG_FIX_COMPLETE.md)** - ATR filter implementation (Oct 31, 2025)
  - **Impact:** Reduced entries from ~240/month to ~2-3/month per asset
  
- **[CRITICAL_FIXES_OCT24_2025.md](CRITICAL_FIXES_OCT24_2025.md)** - Position sizing corrections
  - **Impact:** Fixed GBPUSD 3.53x sizing error, XAGUSD 163x sizing error

- **[POSITION_SIZING_FIX_CRITICAL.md](POSITION_SIZING_FIX_CRITICAL.md)** - MT5 tick value integration
  - **Impact:** Now uses broker-specific specs (not hardcoded pip values)

- **[PULLBACK_COUNT_BUG_FIX.md](PULLBACK_COUNT_BUG_FIX.md)** - Pullback counting logic
  - **Impact:** Corrected pullback validation timing

- **[DUPLICATE_ENTRY_FIX.md](DUPLICATE_ENTRY_FIX.md)** - Prevented duplicate trades
  - **Impact:** Added position check before order placement

---

## 📚 System Architecture

### Code Organization

- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Codebase organization and file purposes
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contributing guidelines (includes READ-ONLY strategy policy)

### MT5 Integration

- **[MT5_HISTORICAL_DATA_SETUP.md](MT5_HISTORICAL_DATA_SETUP.md)** - Loading historical data in MT5
- **[MT5_EMA_SETUP_GUIDE.md](MT5_EMA_SETUP_GUIDE.md)** - EMA indicator configuration

---

## 🚀 Deployment & Maintenance

### Pre-Deployment

- **[PRE_UPLOAD_CHECKLIST.md](PRE_UPLOAD_CHECKLIST.md)** - Complete checklist before deployment
- **[GITHUB_UPLOAD_GUIDE.md](GITHUB_UPLOAD_GUIDE.md)** - GitHub upload instructions
- **[CLEANUP_OCTOBER_2025.md](CLEANUP_OCTOBER_2025.md)** - Repository cleanup notes

### Testing Guides

- **[START_TESTING_HERE.md](START_TESTING_HERE.md)** - Systematic testing procedure
  - Installation verification
  - Broker specification checks
  - Position sizing validation
  - Order execution tests

---

## 📖 Documentation Reading Order

### For New Users:
1. **../README.md** (root) - System overview
2. **../DALIO_QUICK_REFERENCE.md** (root) - Position sizing quick reference
3. **START_TESTING_HERE.md** - Verify installation
4. **MT5_EMA_QUICK_SETUP.md** - Configure charts

### For Developers:
1. **PROJECT_STRUCTURE.md** - Understand codebase
2. **CONTRIBUTING.md** - Development guidelines
3. **../STRATEGY_FILES_POLICY.md** (root) - READ-ONLY policy
4. **ATR_BUG_FIX_COMPLETE.md** - Key implementation details

### For Troubleshooting:
1. **CRITICAL_FIXES_OCT24_2025.md** - Known issues and fixes
2. **PULLBACK_SYSTEM_FIX.md** - Entry system debugging
3. **POSITION_SIZING_FIX_CRITICAL.md** - Position sizing issues
4. **DUPLICATE_ENTRY_FIX.md** - Duplicate trade prevention

### For Strategy Analysis:
1. **DEEP_STRATEGY_ANALYSIS_NOV14.md** ⭐ - Comprehensive 4-hour session analysis
2. **ENTRY_CONDITIONS_VERIFICATION.md** - Filter validation results
3. **PULLBACK_COUNT_BUG_FIX.md** - Pullback timing analysis

---

## 🔍 Find Specific Information

| Topic | Document |
|-------|----------|
| **System Overview** | ../README.md (root) |
| **Position Sizing** | ../DALIO_ALLOCATION_SYSTEM.md (root) |
| **Entry Filters** | ENTRY_CONDITIONS_VERIFICATION.md |
| **Pullback System** | PULLBACK_SYSTEM_FIX.md |
| **ATR Implementation** | ATR_BUG_FIX_COMPLETE.md |
| **Testing Suite** | START_TESTING_HERE.md |
| **MT5 Setup** | MT5_EMA_QUICK_SETUP.md |
| **Project Structure** | PROJECT_STRUCTURE.md |
| **Contributing** | CONTRIBUTING.md |
| **Deployment** | PRE_UPLOAD_CHECKLIST.md |
| **Strategy Analysis** | DEEP_STRATEGY_ANALYSIS_NOV14.md ⭐ |

---

## 📁 Documentation Archive

Historical documentation available in `docs/archive/`:
- Old README versions
- Superseded fix documentation
- Intermediate development notes
- Position sizing fix history

---

## 📊 Current Files in docs/

```
docs/
├── README.md (this file)                      # Documentation index
├── START_TESTING_HERE.md                      # Quick start guide
├── PROJECT_STRUCTURE.md                       # Codebase organization
│
├── Strategy Analysis/
│   ├── DEEP_STRATEGY_ANALYSIS_NOV14.md ⭐    # 25-page 4+ hour analysis
│   ├── ENTRY_CONDITIONS_VERIFICATION.md       # 6-layer filter validation
│   └── PULLBACK_SYSTEM_FIX.md                 # Pullback flag fix
│
├── Critical Fixes/
│   ├── ATR_BUG_FIX_COMPLETE.md                # ATR filter implementation
│   ├── CRITICAL_FIXES_OCT24_2025.md           # Position sizing fixes
│   ├── POSITION_SIZING_FIX_CRITICAL.md        # MT5 tick value integration
│   ├── PULLBACK_COUNT_BUG_FIX.md              # Pullback timing fix
│   └── DUPLICATE_ENTRY_FIX.md                 # Duplicate trade prevention
│
├── MT5 Setup/
│   ├── MT5_EMA_QUICK_SETUP.md                 # 2-minute EMA setup
│   ├── MT5_EMA_SETUP_GUIDE.md                 # Detailed EMA guide
│   └── MT5_HISTORICAL_DATA_SETUP.md           # Historical data config
│
├── Deployment/
│   ├── PRE_UPLOAD_CHECKLIST.md                # Pre-deployment checklist
│   ├── GITHUB_UPLOAD_GUIDE.md                 # GitHub upload guide
│   └── CLEANUP_OCTOBER_2025.md                # Repository cleanup notes
│
├── Contributing/
│   └── CONTRIBUTING.md                         # Development guidelines
│
└── archive/ (30+ files)                       # Historical documentation
    ├── README_OLD_OCT2025.md
    ├── README_OLD_VERBOSE.md
    ├── POSITION_SIZING_FIX_V2.md
    └── ... (27 more files)
```

---

## ✅ What's Working (as of November 16, 2025)

After all critical fixes:

- ✅ **Position Sizing:** MT5 broker-specific tick values (GBPUSD, XAGUSD fixed)
- ✅ **Pullback System:** Flag check enforced (STANDARD vs PULLBACK mode)
- ✅ **ATR Filter:** Properly integrated (entries reduced from 240/mo to 2-3/mo)
- ✅ **6-Layer Filters:** 100% validated (54 crossovers analyzed, 29 rejections justified)
- ✅ **State Machine:** Full progression (SCANNING → ARMED → WINDOW → ENTRY)
- ✅ **EMA Calculations:** Stable, accurate, MT5-aligned
- ✅ **Chart Navigation:** Plotly-style interactive controls
- ✅ **Logging:** Export-ready terminal logs with OHLC data

**System Health Rating:** 9.5/10 (based on DEEP_STRATEGY_ANALYSIS_NOV14.md)

---

## 🎯 Key Files for New Users

1. **[START_TESTING_HERE.md](START_TESTING_HERE.md)** - Begin here
2. **[DEEP_STRATEGY_ANALYSIS_NOV14.md](DEEP_STRATEGY_ANALYSIS_NOV14.md)** ⭐ - Understand the system behavior
3. **[MT5_EMA_QUICK_SETUP.md](MT5_EMA_QUICK_SETUP.md)** - Set up MT5
4. **[PULLBACK_SYSTEM_FIX.md](PULLBACK_SYSTEM_FIX.md)** - Critical fix explanation

---

## ⚡ Quick Links

- **Back to Main README:** [../README.md](../README.md)
- **Quick Start Guide:** [../QUICK_START.md](../QUICK_START.md)
- **Dalio Quick Reference:** [../DALIO_QUICK_REFERENCE.md](../DALIO_QUICK_REFERENCE.md)
- **Strategy Policy:** [../STRATEGY_FILES_POLICY.md](../STRATEGY_FILES_POLICY.md)
- **Deployment Guide:** [../DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md)

---

**📝 Note:** Documentation is continuously updated. Check commit history for latest changes.

**Repository:** [mt5_live_trading_bot](https://github.com/ilahuerta-IA/mt5_live_trading_bot)  
**License:** See LICENSE file
