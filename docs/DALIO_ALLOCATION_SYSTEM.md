# Ray Dalio All-Weather Portfolio Allocation System

## Overview

This document explains the implementation of Ray Dalio's All-Weather Portfolio allocation principles in the MT5 Live Trading Bot. The system replaces the previous equal-risk approach with **asset-specific allocations** based on economic scenario hedging.

---

## 📊 Allocation Strategy

### Economic Scenario-Based Allocation

The All-Weather Portfolio is designed to perform well across different economic environments by allocating capital to assets that thrive in specific conditions:

| **Asset Class** | **Symbol** | **Allocation** | **Economic Scenario** | **Purpose** |
|-----------------|------------|----------------|----------------------|-------------|
| **Deflation Hedge** | USDCHF | **20%** | Deflationary environment | Safe haven currency, capital preservation |
| **Inflation Hedge** | XAUUSD | **18%** | Inflationary environment | Gold standard, monetary debasement protection |
| **Standard Forex** | GBPUSD | **16%** | Balanced conditions | Standard risk/reward, liquid markets |
| **Standard Forex** | EURUSD | **16%** | Balanced conditions | Standard risk/reward, liquid markets |
| **Commodity** | XAGUSD | **15%** | Industrial growth + inflation | Silver/industrial metal exposure |
| **Commodity Currency** | AUDUSD | **15%** | Commodity boom | Resource-driven economy exposure |

**Total Portfolio Coverage:** 100% (20% + 18% + 16% + 16% + 15% + 15%)

---

## 💰 Position Sizing Formula

### Previous System (Equal Risk)
```python
# OLD: All assets risked 1% of total portfolio
balance = $50,078.20
risk_percent = 1%
risk_amount = $50,078.20 × 1% = $500.78  # Same for ALL assets ❌
```

**Problem:** This treats all assets equally, ignoring economic scenario diversification. XAGUSD showed disproportionately small lot sizes (1.0 vs 0.1 for forex).

---

### New System (Dalio Allocation)
```python
# NEW: Each asset risks 1% of its ALLOCATED capital
balance = $50,078.20

# Example for USDCHF (20% allocation):
allocated_capital = $50,078.20 × 20% = $10,015.64
risk_percent = 1% (configurable)
risk_amount = $10,015.64 × 1% = $100.16  ✅

# Example for XAGUSD (15% allocation):
allocated_capital = $50,078.20 × 15% = $7,511.73
risk_percent = 1% (configurable)
risk_amount = $7,511.73 × 1% = $75.12  ✅
```

---

## 📈 Example Calculations (Current Balance: $50,078.20)

| **Symbol** | **Allocation** | **Allocated Capital** | **Risk (1%)** | **Expected Lot Size Impact** |
|------------|----------------|----------------------|---------------|------------------------------|
| **USDCHF** | 20% | $10,015.64 | $100.16 | Largest positions (deflation hedge) |
| **XAUUSD** | 18% | $9,014.08 | $90.14 | Large gold positions (inflation) |
| **GBPUSD** | 16% | $8,012.51 | $80.13 | Standard forex exposure |
| **EURUSD** | 16% | $8,012.51 | $80.13 | Standard forex exposure |
| **XAGUSD** | 15% | $7,511.73 | $75.12 | Commodity exposure (silver) |
| **AUDUSD** | 15% | $7,511.73 | $75.12 | Commodity currency exposure |

---

## 🔧 Implementation Details

### 1. Constants Definition (Lines 79-109)

```python
# ═══════════════════════════════════════════════════════════════════
# RAY DALIO ALL-WEATHER PORTFOLIO ALLOCATION SYSTEM
# ═══════════════════════════════════════════════════════════════════

ASSET_ALLOCATIONS = {
    'USDCHF': 0.20,   # 20% - Deflation hedge (safe haven currency)
    'XAUUSD': 0.18,   # 18% - Inflation hedge (gold standard)
    'GBPUSD': 0.16,   # 16% - Standard forex exposure
    'EURUSD': 0.16,   # 16% - Standard forex exposure
    'XAGUSD': 0.15,   # 15% - Commodity/industrial metal
    'AUDUSD': 0.15,   # 15% - Commodity currency
}

# Default risk percentage per trade (% of allocated capital, not total portfolio)
DEFAULT_RISK_PERCENT = 0.01  # 1% of allocated capital (configurable)
```

### 2. Position Sizing Calculation (Lines 3161-3187)

```python
# Get real-time account balance from MT5
balance = account_info.balance

# Get asset-specific allocation (default 16% if symbol not in allocations)
allocation_percent = ASSET_ALLOCATIONS.get(symbol, 0.16)
allocated_capital = balance * allocation_percent

# Get risk percentage (configurable per strategy, default 1%)
# This is % of ALLOCATED capital, not total portfolio
risk_percent = config.get('RISK_PER_TRADE', DEFAULT_RISK_PERCENT)

# Calculate risk amount based on allocated capital
risk_amount = allocated_capital * risk_percent
```

### 3. Logging Output

The system provides transparent logging of all allocation calculations:

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

---

## 🎯 Benefits of Dalio Allocation System

### 1. **Economic Diversification**
- Protects against inflation (XAUUSD, XAGUSD)
- Protects against deflation (USDCHF)
- Maintains standard forex exposure (GBPUSD, EURUSD)
- Captures commodity trends (XAGUSD, AUDUSD)

### 2. **Risk Balance**
- No single asset dominates the portfolio
- Risk scales proportionally to economic role
- Natural position sizing emerges from allocation

### 3. **XAGUSD Lot Size Fix**
- **Before:** Equal 1% risk → tiny 1.0 lot (insufficient exposure)
- **After:** 15% allocation → properly sized lots based on $7,511.73 allocated capital

### 4. **Portfolio Theory Alignment**
- Follows Dalio's principles of uncorrelated asset allocation
- Automatically rebalances risk as account grows/shrinks
- Real-time balance fetching ensures accuracy

---

## ⚙️ Configuration

### Per-Asset Risk Override (Optional)

You can override the default 1% risk per asset in strategy config files:

```python
# In strategies/sunrise_ogle_xauusd.py (for example)
class Config:
    # ... other settings ...
    RISK_PER_TRADE = 0.015  # 1.5% risk for gold (higher conviction)
```

**Note:** This is still 1.5% of the **allocated 18% capital**, not total portfolio.

### Changing Allocation Percentages

To adjust allocations, edit the `ASSET_ALLOCATIONS` dictionary in `advanced_mt5_monitor_gui.py`:

```python
ASSET_ALLOCATIONS = {
    'USDCHF': 0.25,   # Increase deflation hedge to 25%
    'XAUUSD': 0.15,   # Reduce gold to 15%
    # ... etc
}
```

**Important:** Ensure total allocations sum to 100% (or close to it) for proper diversification.

---

## 📊 Comparison: Old vs New System

### Scenario: $50,078.20 Balance, All Assets Signal Entry Simultaneously

| **Symbol** | **OLD Risk** | **NEW Risk** | **Change** | **Reason** |
|------------|-------------|-------------|-----------|------------|
| USDCHF | $500.78 | $100.16 | -80% | Prevents over-concentration |
| XAUUSD | $500.78 | $90.14 | -82% | Inflation hedge gets proper weight |
| GBPUSD | $500.78 | $80.13 | -84% | Standard forex exposure |
| EURUSD | $500.78 | $80.13 | -84% | Standard forex exposure |
| XAGUSD | $500.78 | $75.12 | -85% | Commodity gets proper allocation |
| AUDUSD | $500.78 | $75.12 | -85% | Commodity currency allocation |
| **TOTAL** | **$3,004.68** (6% of portfolio) | **$500.80** (1% of portfolio) | -83% | Proper diversification |

**Key Insight:** Old system could theoretically risk 6% of portfolio if all assets signaled at once. New system maintains true 1% portfolio risk with economic diversification.

---

## 🧪 Testing the System

### Manual Calculation Verification

Use this formula to verify lot size calculations:

```python
# Example for USDCHF at current balance
balance = 50_078.20
allocation = 0.20  # 20%
risk_pct = 0.01    # 1%

allocated_capital = balance × allocation = 50_078.20 × 0.20 = 10_015.64
risk_amount = allocated_capital × risk_pct = 10_015.64 × 0.01 = 100.16

# If SL distance = 45 pips (0.00450), pip value = $10 (standard lot)
lot_size = risk_amount / (sl_distance_pips × pip_value)
lot_size = 100.16 / (45 × 10) = 0.0223 lots
# After rounding to step (0.01): 0.02 lots ✅
```

### Monitor Logs

When a trade executes, you'll see:

```
💰 XAGUSD: Dalio Allocation System
   Portfolio Balance: $50,078.20
   Asset Allocation: 15% = $7,511.73
   Risk Per Trade: 1.0% of allocated = $75.12
```

Compare `$75.12` risk vs old system's `$500.78` — this is **working as intended**.

---

## 📝 Strategy Files Policy Compliance

**IMPORTANT:** This implementation modifies **ONLY** `advanced_mt5_monitor_gui.py`. 

**Strategy files in `strategies/` remain UNCHANGED** to preserve backtesting integrity per `STRATEGY_FILES_POLICY.md`.

The allocation system is applied at **execution time** in the live monitor, not in the strategy backtesting logic.

---

## 🚀 Deployment Checklist

- [x] Add `ASSET_ALLOCATIONS` dictionary to `advanced_mt5_monitor_gui.py`
- [x] Add `DEFAULT_RISK_PERCENT` constant (1%)
- [x] Modify position sizing calculation in `execute_trade()` method
- [x] Update logging to show allocation details
- [x] Verify no syntax errors (`get_errors()`)
- [x] Preserve strategy files (no modifications)
- [ ] Test on demo account with current balance
- [ ] Verify lot sizes match expected calculations
- [ ] Monitor first 5 trades for accuracy
- [ ] Commit changes to GitHub

---

## 📚 References

- **Ray Dalio's All-Weather Portfolio**: [Bridgewater Associates](https://www.bridgewater.com)
- **Economic Scenarios**: Inflation, Deflation, Growth, Recession
- **Asset Correlation Theory**: Modern Portfolio Theory (Harry Markowitz)

---

## 💡 Future Enhancements

1. **Dynamic Rebalancing**: Adjust allocations based on market regime detection
2. **Risk Scaling**: Increase/decrease DEFAULT_RISK_PERCENT based on portfolio drawdown
3. **Correlation Monitoring**: Track actual asset correlations vs expected
4. **Allocation UI**: Add GUI controls to adjust allocations without editing code
5. **Backtesting Integration**: Simulate Dalio system on historical data

---

**Implementation Date:** November 5, 2025  
**Version:** 1.0  
**Status:** ✅ IMPLEMENTED - Ready for testing

**Current Balance:** $50,078.20  
**Next Step:** Deploy and monitor first trades for verification
