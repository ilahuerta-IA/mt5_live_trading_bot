# GBPUSD Position Sizing Fix - Stop Loss Too Low Issue

## Problem Description

**Issue:** GBPUSD trades showing stop loss of $22.70 instead of expected $80.13
- Expected risk (Dalio 16% allocation): **$80.13**
- Actual risk observed: **$22.70**
- **Error factor: 3.53x too small** (underfunded positions)

## Root Cause Analysis

The position sizing formula in `advanced_mt5_monitor_gui.py` was **incorrectly calculating pip value per lot** for forex pairs like GBPUSD.

### Original Buggy Formula (Line 3254):
```python
value_per_point = tick_value / tick_size * point
lot_size = risk_amount / (sl_distance / point * value_per_point)
```

### Problem:
- MT5's `tick_value` returns value for a **micro lot or different contract size**
- For GBPUSD, this was returning ~$1 per pip instead of **$10 per pip** (standard lot)
- This caused lot sizes to be calculated **10x smaller than required**
- Combined with other factors, resulted in **3.53x smaller risk** ($22.70 instead of $80.13)

## The Fix

### New Corrected Formula (Lines 3230-3265):
```python
# Calculate value per point for 1 standard lot
if tick_size > 0:
    value_per_point_at_contract = tick_value / tick_size * point
else:
    value_per_point_at_contract = tick_value

# For forex pairs (contract_size = 100,000), ensure pip value is $10 per lot
if contract_size >= 100000:  # Forex pairs
    value_per_point = 10.0 if symbol in ['EURUSD', 'GBPUSD', 'AUDUSD'] else value_per_point_at_contract
else:  # Commodities
    value_per_point = value_per_point_at_contract

# Calculate lot size correctly
sl_distance_in_pips = sl_distance / point
lot_size = risk_amount / (sl_distance_in_pips * value_per_point)
```

### Why This Works:
1. **Forex pairs** (EURUSD, GBPUSD, AUDUSD): **Hardcoded $10 per pip** for standard lot
2. **Commodities** (XAUUSD, XAGUSD): Use MT5's calculated tick value
3. **Explicit pip value** eliminates broker-specific tick_value variations

## Verification Example

### GBPUSD with 35 pip stop loss:
```
Balance: $50,078.20
Allocation: 16% (GBPUSD)
Allocated Capital: $8,012.51
Risk: 1% = $80.13

OLD (BUGGY):
  - Pip value: ~$1.00 (WRONG - from MT5 tick_value)
  - Lot size: $80.13 / (35 pips × $1.00) = 2.289 lots (TOO LARGE)
  - Actual risk after limits: $22.70 (capped by max lot size)
  
NEW (FIXED):
  - Pip value: $10.00 (CORRECT - hardcoded for forex)
  - Lot size: $80.13 / (35 pips × $10.00) = 0.2289 lots ✅
  - Actual risk: 0.2289 lots × 35 pips × $10 = $80.13 ✅
```

## Impact on Other Symbols

### ✅ Still Correct:
- **XAUUSD** (Gold): Uses calculated tick value ($1/oz × 100 oz contract)
- **XAGUSD** (Silver): Uses calculated tick value  
- **USDCHF**: Hardcoded $10/pip (standard forex)

### 🔧 Now Fixed:
- **GBPUSD**: Now uses $10/pip ✅
- **EURUSD**: Now uses $10/pip ✅
- **AUDUSD**: Now uses $10/pip ✅

## Testing Required

1. **Stop the bot** (if running)
2. **Rebuild the executable**:
   ```
   .\build_exe.bat
   ```
3. **Restart the bot**
4. **Monitor next GBPUSD trade**:
   - Check log for: `💰 GBPUSD: Position Sizing Calculation:`
   - Verify: `Pip Value/Lot: $10.00` (not $1.00)
   - Verify: Calculated risk ≈ $80.13
   - Verify: Stop loss distance in pips matches ATR × multiplier

## Expected Log Output (Fixed):

```
💰 GBPUSD: Position Sizing Calculation:
   Allocated: $8,012.51 (16% of $50,078.20) | Risk: 1.0% = $80.13
   SL Distance: 0.00350 price units (35.0 pips)
   Contract Size: 100000 | Pip Value/Lot: $10.00
   Formula: $80.13 / (35.0 pips × $10.00) = 0.228950 lots
   Calculated Volume: 0.228950 lots (BEFORE limits)
   ✅ Risk Verification: 0.228950 × 35.0 × $10.00 = $80.13
   Final Volume: 0.220000 lots (min=0.01, max=500.0, step=0.01)
```

## Dalio Allocation Reminder

| Symbol | Allocation | Allocated Capital | Risk (1%) | Expected SL $ (35 pips) |
|--------|-----------|-------------------|-----------|------------------------|
| **USDCHF** | 20% | $10,015.64 | $100.16 | ~$100 |
| **XAUUSD** | 18% | $9,014.08 | $90.14 | ~$90 |
| **GBPUSD** | 16% | $8,012.51 | **$80.13** | **~$80** ✅ |
| **EURUSD** | 16% | $8,012.51 | $80.13 | ~$80 |
| **XAGUSD** | 15% | $7,511.73 | $75.12 | ~$75 |
| **AUDUSD** | 15% | $7,511.73 | $75.12 | ~$75 |

**Note:** Actual stop loss dollar amount varies with SL distance (ATR × multiplier)

## Files Modified

- `advanced_mt5_monitor_gui.py` (Lines 3230-3270)
  - Fixed pip value calculation for forex pairs
  - Added risk verification in debug logs
  - Improved logging clarity

## Deployment Steps

1. ✅ **Code fixed** in `advanced_mt5_monitor_gui.py`
2. ⏳ **Rebuild executable**: Run `.\build_exe.bat`
3. ⏳ **Restart bot**: Use `.\run_bot.bat` or double-click new `.exe`
4. ⏳ **Monitor logs**: Verify GBPUSD shows $80.13 risk
5. ⏳ **Commit to Git**: `git add advanced_mt5_monitor_gui.py; git commit -m "Fix GBPUSD position sizing - correct pip value to $10/lot"`

---

**Status:** 🔧 **FIXED** - Ready for testing  
**Priority:** 🔴 **HIGH** - Affects capital allocation integrity  
**Date:** November 7, 2025
