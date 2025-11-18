# PULLBACK COUNT BUG FIX

## Issue Discovered

**Symptom:** Pullback count increments every second without control, continuing to increment even after reaching the required count (e.g., 7/2, 8/2, 9/2... 18/2).

**Terminal Log Evidence:**
```
05:07:23.634 GBPUSD: Pullback CONFIRMED (7/2) - Window OPENING
05:07:27.811 GBPUSD: Pullback CONFIRMED (8/2) - Window OPENING
05:07:32.809 GBPUSD: Pullback CONFIRMED (9/2) - Window OPENING
05:07:36.518 GBPUSD: Pullback CONFIRMED (10/2) - Window OPENING
05:07:40.680 GBPUSD: Pullback CONFIRMED (11/2) - Window OPENING
05:07:44.818 GBPUSD: Pullback CONFIRMED (12/2) - Window OPENING
```

This should only show **once** when count reaches 2/2, then transition to WINDOW_OPEN.

## Root Cause Analysis

### The Bug
In `determine_strategy_phase()` method, when transitioning from ARMED to WINDOW_OPEN:

```python
# Check if pullback complete
if current_state['pullback_candle_count'] >= max_candles:
    # ... window calculation ...
    self._phase3_open_breakout_window(symbol, armed_direction, config, current_bar)
    entry_state = 'WINDOW_OPEN'  # ❌ ONLY updated local variable!
    
    self.terminal_log(f"🟢 {symbol}: Pullback CONFIRMED ...")
```

**Problem:** Only the **local variable** `entry_state` was updated to `'WINDOW_OPEN'`, but the **state dictionary** `current_state['entry_state']` remained as `'ARMED_LONG'` or `'ARMED_SHORT'`.

**Result:** On the next monitoring tick (1 second later):
1. Code reads `entry_state = current_state['entry_state']` → Still `'ARMED_LONG'`
2. Enters Phase 2 logic again: `elif entry_state in ['ARMED_LONG', 'ARMED_SHORT']:`
3. Detects pullback candle (still same bar) → Increments counter again
4. Reaches max count → Logs "Window OPENING" again
5. Updates local `entry_state` to `'WINDOW_OPEN'` but doesn't save it
6. **Loop repeats every second!**

### Original Strategy Behavior

In `sunrise_ogle_audusd.py` (Line 1633-1635):

```python
elif self.entry_state in ["ARMED_LONG", "ARMED_SHORT"]:
    # PHASE 2: Confirm pullback
    if self._phase2_confirm_pullback(self.armed_direction):
        # Transition to WINDOW_OPEN state
        self.entry_state = "WINDOW_OPEN"  # ✅ Updates the instance variable immediately
        self._phase3_open_breakout_window(self.armed_direction)
```

**Key Difference:** Original strategy updates `self.entry_state` **immediately**, so on the next bar the condition `elif self.entry_state in ["ARMED_LONG", "ARMED_SHORT"]:` is **False** and Phase 2 doesn't execute.

## The Fix

Updated code to write to **BOTH** the local variable AND the state dictionary:

```python
# Check if pullback complete
if current_state['pullback_candle_count'] >= max_candles:
    # Store last pullback candle data for window calculation
    current_state['last_pullback_candle_high'] = float(current_high)
    current_state['last_pullback_candle_low'] = float(current_low)
    
    # Transition to WINDOW_OPEN
    self._phase3_open_breakout_window(symbol, armed_direction, config, current_bar)
    
    # ✅ FIX: Update BOTH local variable AND state dictionary
    current_state['entry_state'] = 'WINDOW_OPEN'
    current_state['phase'] = 'WAITING_BREAKOUT'
    entry_state = 'WINDOW_OPEN'
    
    self.terminal_log(f"🟢 {symbol}: Pullback CONFIRMED ({current_state['pullback_candle_count']}/{max_candles}) - Window OPENING", 
                    "SUCCESS", critical=True)
```

## State Variable Synchronization Pattern

Throughout `determine_strategy_phase()`, we must maintain synchronization between:
- **Local variable:** `entry_state` (read at start, used for routing)
- **State dictionary:** `current_state['entry_state']` (persisted between calls)

**Critical Pattern:**
```python
# Read state at start
entry_state = current_state['entry_state']

# ... state machine logic ...

# When transitioning, update BOTH:
current_state['entry_state'] = 'NEW_STATE'
entry_state = 'NEW_STATE'
```

## Why This Matters

### Without Fix (Buggy Behavior)
```
Tick 1: ARMED_LONG → Pullback 1/2 → Still ARMED_LONG
Tick 2: ARMED_LONG → Pullback 2/2 → "Window OPENING" (local only)
Tick 3: ARMED_LONG → Pullback 3/2 → "Window OPENING" (local only)  ❌ WRONG!
Tick 4: ARMED_LONG → Pullback 4/2 → "Window OPENING" (local only)  ❌ WRONG!
... continues forever ...
```

### With Fix (Correct Behavior)
```
Tick 1: ARMED_LONG → Pullback 1/2 → Still ARMED_LONG
Tick 2: ARMED_LONG → Pullback 2/2 → "Window OPENING" → State saved as WINDOW_OPEN
Tick 3: WINDOW_OPEN → Monitor for breakout ✅ CORRECT!
Tick 4: WINDOW_OPEN → Monitor for breakout ✅ CORRECT!
```

## Testing Expected Results

After fix, terminal log should show:
```
05:07:20.000 GBPUSD: Pullback counting (1/2)
05:07:23.000 GBPUSD: Pullback CONFIRMED (2/2) - Window OPENING
05:07:26.000 GBPUSD: WAITING_BREAKOUT → WINDOW_OPEN | Price: 1.34128 | Trend: SIDEWAYS
05:07:29.000 GBPUSD: Window EXPIRED - Returning to pullback search
```

**Key Observations:**
1. "Pullback CONFIRMED" appears **only once** when count reaches 2/2
2. Next tick shows "WAITING_BREAKOUT" (Phase 3/4), NOT another pullback confirmation
3. Pullback count stays at 2, doesn't increment to 3, 4, 5...

## Related Code Locations

**File:** `advanced_mt5_monitor_gui.py`
**Method:** `determine_strategy_phase()`
**Line:** ~1242-1252 (Phase 2 → Phase 3 transition)

**Other State Transitions to Verify:**
- Phase 1 → Phase 2 (SCANNING → ARMED): Line ~1188-1197 ✅ Already correct
- Phase 3 → Phase 1 (WINDOW_OPEN → SCANNING on success): Line ~1277-1279 ✅ Uses `_reset_entry_state()`
- Phase 3 → Phase 2 (WINDOW_OPEN → ARMED on expiry): Line ~1281-1285 ✅ Updates `current_state['entry_state']`
- Phase 3 → Phase 2 (WINDOW_OPEN → ARMED on failure): Line ~1287-1291 ✅ Updates `current_state['entry_state']`

All other transitions correctly update both local and state dictionary variables.

## Implementation Summary

**Change Made:** Added two lines to Phase 2 → Phase 3 transition:
```python
current_state['entry_state'] = 'WINDOW_OPEN'
current_state['phase'] = 'WAITING_BREAKOUT'
```

**Impact:** Ensures state persists between monitoring ticks, preventing Phase 2 from re-executing after pullback confirmation.

**Status:** ✅ Fixed and ready for testing

## Credits

Issue discovered by user reviewing terminal log file:
> "Review the pullback count, see terminal log each 1 second add a pullback without control."

This was a critical bug that would have caused incorrect strategy behavior where the monitor would never properly transition to window monitoring phase.
