# CRITICAL BUG FIX: Pullback Counting System

## Date: October 16, 2025

## Problem Summary
**0 pullbacks detected in 12 hours** - Extremely suspicious and confirmed a critical bug in the pullback counting logic.

## Root Cause Analysis

### Bug 1: Global Invalidation Too Aggressive
**Location**: All 6 strategy files, `~line 1551-1582` (varies by file)

**Problem**: Global Invalidation was checking BOTH:
- Candle direction (bearish/bullish)
- EMA crossover (opposing trend)

**Why This Was Wrong**: 
- Pullback candles are SUPPOSED to be opposite direction
- For LONG setup: pullback candles SHOULD be red (bearish)
- For SHORT setup: pullback candles SHOULD be green (bullish)
- By checking candle direction, we were invalidating LEGITIMATE pullbacks!

**Before (BUGGY)**:
```python
if prev_bear and (cross_fast or cross_medium or cross_slow):
    opposing_signal = "SHORT"
```

**After (FIXED)**:
```python
# Don't check candle color - bearish candles are EXPECTED in pullbacks!
if (cross_fast or cross_medium or cross_slow):
    opposing_signal = "SHORT"
```

### Bug 2: Pullback Reset Logic Too Aggressive
**Location**: 
- All 6 strategy files: `_phase2_confirm_pullback()` function
- GUI file: `advanced_mt5_monitor_gui.py` lines ~1511-1530

**Problem**: Code was resetting to SCANNING state on EVERY non-pullback candle

**Why This Was Wrong**:
Consider this scenario for ARMED_LONG (waiting for 3 bearish pullback candles):
```
Time    Candle   Buggy Behavior              Correct Behavior
18:25   Signal   ARMED_LONG, count=0         ARMED_LONG, count=0
18:30   GREEN    Reset to SCANNING! count=0  ARMED_LONG, count=0 (WAIT)
18:35   RED      (missed, was in SCANNING)   count=1 (increment!)
18:40   RED      (missed)                    count=2 (increment!)
18:45   GREEN    (missed)                    count=2 (WAIT)
18:50   RED      (missed)                    count=3 → WINDOW_OPEN!
```

The bug prevented ANY pullback from ever being counted because the first non-pullback candle would immediately reset everything!

**Before (BUGGY - Strategy Files)**:
```python
if is_pullback_candle:
    self.pullback_candle_count += 1
    if self.pullback_candle_count >= max_candles:
        return True
else:
    # ❌ BUG: Resets on EVERY non-pullback candle!
    print(f"PULLBACK INVALIDATED...")
    self._reset_entry_state()
return False
```

**After (FIXED - Strategy Files)**:
```python
if is_pullback_candle:
    self.pullback_candle_count += 1
    if self.pullback_candle_count >= max_candles:
        return True
# If not a pullback candle, just wait - don't reset!
# Only Global Invalidation (opposing EMA crossover) should reset the state
# Non-pullback candles are normal - we're waiting for pullback candles to accumulate
return False
```

**Before (BUGGY - GUI File)**:
```python
else:
    # Non-pullback candle - GLOBAL INVALIDATION RULE
    self.terminal_log(f"⚠️ {symbol}: Non-pullback candle! Reset to SCANNING")
    self._reset_entry_state(symbol)
    entry_state = 'SCANNING'
```

**After (FIXED - GUI File)**:
```python
else:
    # Non-pullback candle - just wait, don't reset!
    # Only Global Invalidation (opposing EMA crossover) should reset the state
    candle_type = "Bullish" if current_close > current_open else "Bearish"
    self.terminal_log(f">> WAITING: {symbol} {armed_direction} non-pullback ({candle_type})")
```

## Files Modified

### Strategy Files (All 6)
1. ✅ `strategies/sunrise_ogle_xauusd.py`
   - Bug 1 fix: Lines ~1551-1582
   - Bug 2 fix: Lines ~1312-1345
   - Added debug logging

2. ✅ `strategies/sunrise_ogle_gbpusd.py`
   - Bug 1 fix: Lines ~1366-1397
   - Bug 2 fix: Lines ~1105-1135

3. ✅ `strategies/sunrise_ogle_eurusd.py`
   - Bug 1 fix: Lines ~1359-1390
   - Bug 2 fix: Lines ~1098-1128

4. ✅ `strategies/sunrise_ogle_audusd.py`
   - Bug 1 fix: Lines ~1589-1620
   - Bug 2 fix: Lines ~1328-1358

5. ✅ `strategies/sunrise_ogle_xagusd.py`
   - Bug 1 fix: Lines ~1589-1620
   - Bug 2 fix: Lines ~1328-1358

6. ✅ `strategies/sunrise_ogle_usdchf.py`
   - Bug 1 fix: Lines ~1551-1582
   - Bug 2 fix: Lines ~1290-1320

### GUI File
✅ `advanced_mt5_monitor_gui.py`
- Bug 2 fix: Lines ~1511-1535
- Added detailed OHLC debug logging (lines ~1476-1492, ~1526-1532)

## Testing Verification

### Evidence of Bug
- **12 hours of monitoring**: 0 pullbacks detected
- **Multiple ARMED signals**: All failed to count pullback candles
- **User observation**: Clear red pullback candles visible on XAUUSD chart but count remained at 0

### Expected Behavior After Fix
When a symbol enters ARMED_LONG state:
1. ✅ RED candles (close < open) should increment pullback_candle_count
2. ✅ GREEN candles should NOT reset, just wait
3. ✅ Count should accumulate: 0 → 1 → 2 → 3 → WINDOW_OPEN
4. ✅ Only opposing EMA crossover should trigger Global Invalidation

### Debug Output Added
```
>> PULLBACK CANDLE: XAUUSD ARMED_LONG #1/3 | BEARISH (Red) | O:4196.48 H:4197.82 L:4195.12 C:4195.65
>> WAITING: XAUUSD ARMED_LONG non-pullback (Bullish/GREEN) count=1/3 | O:4195.65 H:4196.88 L:4195.01 C:4196.45
>> PULLBACK CANDLE: XAUUSD ARMED_LONG #2/3 | BEARISH (Red) | O:4196.45 H:4196.90 L:4194.23 C:4194.88
>> PULLBACK CANDLE: XAUUSD ARMED_LONG #3/3 | BEARISH (Red) | O:4194.88 H:4195.12 L:4193.45 C:4193.92
>> PULLBACK CONFIRMED: ARMED_LONG pullback complete (3 candles)
```

## Impact Assessment

### Before Fix (BROKEN)
- **Pullback Success Rate**: 0% (impossible to complete pullback phase)
- **Entry Opportunities**: 0 (strategy couldn't progress past ARMED state)
- **False Resets**: Every non-pullback candle triggered reset
- **Strategy Effectiveness**: Completely broken

### After Fix (WORKING)
- **Pullback Success Rate**: Expected ~normal market behavior
- **Entry Opportunities**: Should match strategy parameters
- **False Resets**: Only on legitimate Global Invalidation (opposing EMA crossover)
- **Strategy Effectiveness**: Restored to design specification

## Backtrader State Machine (Correct Flow)

```
SCANNING
    ↓ (EMA crossover + bullish candle)
ARMED_LONG (pullback_count = 0)
    ↓ (red candle)
ARMED_LONG (pullback_count = 1)
    ↓ (green candle - WAIT, don't reset!)
ARMED_LONG (pullback_count = 1)
    ↓ (red candle)
ARMED_LONG (pullback_count = 2)
    ↓ (red candle)
ARMED_LONG (pullback_count = 3)
    ↓ (pullback confirmed)
WINDOW_OPEN
    ↓ (price breaks window top)
ENTRY EXECUTED
```

## Known Issues (Minor)

### Unicode Encoding Errors
- **Issue**: Emoji characters (✅, 🔍, 📊, etc.) cause encoding errors in Windows PowerShell logging
- **Impact**: Visual only - does not affect functionality
- **Status**: Non-critical, can be fixed later by removing emojis or configuring UTF-8 encoding

## Next Steps

1. ✅ **COMPLETED**: Fix Bug 1 (Global Invalidation) in all 6 strategy files
2. ✅ **COMPLETED**: Fix Bug 2 (Pullback Reset) in all 6 strategy files  
3. ✅ **COMPLETED**: Fix Bug 2 in GUI monitoring file
4. ✅ **COMPLETED**: Add comprehensive debug logging
5. ⏳ **PENDING**: Monitor live trading for 24-48 hours to verify fix
6. ⏳ **PENDING**: Document pullback statistics (success rate, timing, etc.)
7. ⏳ **PENDING**: Fix Unicode encoding issues (optional)

## Verification Checklist

- [ ] Wait for next ARMED signal
- [ ] Verify pullback candles are counted correctly
- [ ] Verify non-pullback candles don't cause reset
- [ ] Verify Global Invalidation still works (opposing EMA crossover)
- [ ] Verify WINDOW_OPEN state is reached
- [ ] Verify breakout entry executes
- [ ] Document first successful pullback sequence
- [ ] Compare pullback rate to historical data

## Conclusion

This was a **CRITICAL BUG** that completely disabled the pullback counting mechanism. The fix restores the strategy to its intended design where:

1. **ARMED state persists** through non-pullback candles
2. **Pullback candles accumulate** properly
3. **Only legitimate market conditions** (opposing EMA crossover) trigger state reset
4. **Strategy can progress** through all phases: SCANNING → ARMED → WINDOW → ENTRY

The 12-hour period with 0 pullbacks was definitive proof of this bug. After the fix, we expect to see normal pullback activity matching market volatility patterns.

---

**Fixed by**: GitHub Copilot + User (Iván)  
**Date**: October 16, 2025  
**Severity**: CRITICAL (P0)  
**Status**: FIXED, awaiting live verification
