# PULLBACK CHECK TIMING FIX

## Issue Discovered from Log Analysis

### Problem
From log file `terminal_log_20251009_205544.txt`:
```
[21:04:46.026] 📊 XAUUSD: WAITING_PULLBACK → ARMED_LONG | Price: 3959.66000
[21:04:48.111] ⚠️ XAUUSD: Non-pullback candle detected - Reset to SCANNING
```

Strategy gets ARMED but immediately resets 2 seconds later without ever counting pullbacks or opening windows.

### Root Cause

**The monitor was checking for pullback candles EVERY 2 SECONDS on the SAME candle still forming!**

**Example of buggy behavior:**
```
H1 Timeframe (candle closes at 22:00)
21:04:46 → Crossover detected → ARMED_LONG
21:04:48 → Check pullback: Is current candle (still forming until 22:00) bearish?
            → Close: 3959.66, Open: 3959.70 → Bearish at this moment
21:04:50 → Check pullback: Is current candle (still forming) bearish?
            → Close: 3959.72, Open: 3959.70 → NOW BULLISH! → Reset to SCANNING ❌
```

The candle is **still forming** and the close price changes every tick. We're checking a moving target!

### Original Strategy Behavior

In Backtrader's original strategy:
- `next()` method is called **ONLY when a candle CLOSES**
- Each call to `next()` processes ONE COMPLETED candle
- Pullback check happens on **CLOSED candles**, not candles in formation

**Original strategy Line 1310-1315:**
```python
def _phase2_confirm_pullback(self, armed_direction):
    """PHASE 2: Count pullback candles"""
    # Check candle direction for pullback
    is_pullback_candle = False
    
    if armed_direction == 'LONG':
        # For LONG: pullback = bearish candle (close < open)
        is_pullback_candle = self.data.close[0] < self.data.open[0]  # ← CLOSED CANDLE
```

`self.data.close[0]` is the **closing price of the LAST COMPLETED BAR**, not a candle still forming.

### The Fix

**Added candle tracking to only check pullbacks on NEW candles:**

```python
# ⚠️ CRITICAL: Only check pullbacks on NEW CANDLE, not every tick!
# Original strategy checks in next() which is called per closed candle
# Track if we've already processed this candle for pullback
elif len(df) >= 1 and 'last_pullback_check_candle' in current_state and current_state['last_pullback_check_candle'] == current_candle_time:
    # Already processed this candle, skip pullback check until new candle
    pass

# Check for pullback candles (ONLY on new candles)
elif len(df) >= 1:
    # ... pullback detection logic ...
    
    # Mark this candle as processed to avoid re-checking on next tick
    current_state['last_pullback_check_candle'] = current_candle_time
```

### How It Works Now

1. **New candle detected** (timestamp changed)
2. Check if pullback → Process → Mark candle as checked
3. **Same candle, next monitoring tick** (2 seconds later)
4. See we already checked this candle → Skip pullback check → Wait for next candle
5. **New candle appears** → Repeat from step 1

### Expected Behavior After Fix

**H1 Timeframe:**
```
21:00:00 → Candle 1 closes → Crossover detected → ARMED_LONG
21:00:02 → Still on Candle 1 (checked) → Skip pullback check
21:00:04 → Still on Candle 1 (checked) → Skip pullback check
...
22:00:00 → Candle 2 closes → Check pullback: Bearish? YES → Count 1/2
22:00:02 → Still on Candle 2 (checked) → Skip pullback check
...
23:00:00 → Candle 3 closes → Check pullback: Bearish? YES → Count 2/2 → Window OPENING
23:00:02 → Monitoring window (window lasts 1 bar = until 24:00)
24:00:00 → Window expires (no breakout) → Reset to ARMED
```

### Window Duration Verification

Checked original strategies:
- **AUDUSD:** `LONG_ENTRY_WINDOW_PERIODS = 1` (1 bar)
- **XAUUSD:** `LONG_ENTRY_WINDOW_PERIODS = 1` (1 bar)  
- **XAGUSD:** `LONG_ENTRY_WINDOW_PERIODS = 3` (3 bars)

With H1 timeframe:
- 1 bar window = Monitor for 1 hour
- 3 bar window = Monitor for 3 hours

### Files Modified

**File:** `advanced_mt5_monitor_gui.py`
**Lines:** ~1218-1220, ~1245

### Changes Made

1. **Line ~1218:** Added check to skip pullback detection if candle already processed
2. **Line ~1245:** Mark candle as processed after pullback check

### Related Fixes

This fix works together with:
1. **Bar counter fix** (only increment on new candles) - Already implemented
2. **Pullback count reset** (reset on window expiry) - Already implemented
3. **Time filter placement** (check before state machine) - Already implemented

### Testing Checklist

After this fix:
- [ ] Strategy stays ARMED without resetting every 2 seconds
- [ ] Pullback count increments only when NEW candle closes
- [ ] Windows open after required pullback count reached
- [ ] H1 timeframe: Each pullback candle takes ~1 hour (not 2 seconds)
- [ ] Terminal shows "Pullback counting (1/2)", "Pullback counting (2/2)", "Window OPENING"
- [ ] No more immediate "Non-pullback candle detected" resets

### Priority

**CRITICAL** - Without this fix, the strategy cannot progress past ARMED state. It resets every 2 seconds and never reaches window opening or entry.

### Status

✅ **IMPLEMENTED** - Ready for testing
