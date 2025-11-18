# BUG FIX: Time Filter Infinite Recursion in GBPUSD Strategy

## Date
October 15, 2025

## Problem Description
User reported that pullback counting stops working after 16:00 on GBPUSD. The chart showed "Phase: ARMED_LONG" at 16:00 but no pullback progression after that time.

### Symptoms
- GBPUSD gets ARMED_LONG signal at 16:00
- Pullback count never increases beyond that time
- Time filter is set to 7:00-18:00 UTC (should allow entries)
- Log shows crossovers but no pullback state changes

## Root Cause
Found **duplicate function definition** with wrong name in `sunrise_ogle_gbpusd.py`:

### Line 1823 (INCORRECT - Causing Bug)
```python
def _is_in_trading_time_range(self, dt):
    """SHORT pullback entry state machine logic - 3-phase precise implementation"""
    # Check time range filter first
    if not self._is_in_trading_time_range(dt):  # ⚠️ INFINITE RECURSION!
        ...
    # [190 lines of SHORT pullback logic]
```

### Line 2013 (CORRECT)
```python
def _is_in_trading_time_range(self, dt):
    """Check if current time is within allowed trading hours (UTC)"""
    if not self.p.use_time_range_filter:
        return True
    # [Actual time filter logic]
```

### What Went Wrong
1. Copy-paste error created duplicate function name
2. First definition (line 1823) was actually SHORT pullback logic
3. This function immediately calls itself: `if not self._is_in_trading_time_range(dt)`
4. **Infinite recursion** occurs whenever pullback code checks time filter
5. Python stack limit prevents actual crash, but logic breaks silently
6. Pullback state machine stops progressing

## Impact
- **GBPUSD Strategy**: Broken pullback entry system
- **All Strategies**: Same bug likely exists in other strategy files
- **Time Filter**: Never actually executed (recursion loop)
- **Entries**: Blocked after ARMED state due to time check failure

## Solution
Renamed the duplicate function at line 1823 to prevent it from overriding the correct time filter:

```python
def _handle_short_pullback_entry_REMOVED(self, dt):
    """REMOVED: This was incorrectly named _is_in_trading_time_range causing infinite recursion
    SHORT pullback entry state machine logic - 3-phase precise implementation"""
```

This ensures the correct `_is_in_trading_time_range` at line 2013 is always used.

## Files Changed
1. `strategies/sunrise_ogle_gbpusd.py` - Line 1823 function renamed

## Testing Required
1. ✅ Verify GBPUSD pullback counting works after 16:00
2. ✅ Confirm time filter properly blocks entries outside 7:00-18:00 range
3. ⚠️ Check other strategy files for same bug pattern:
   - `sunrise_ogle_eurusd.py`
   - `sunrise_ogle_audusd.py`
   - `sunrise_ogle_usdchf.py`
   - `sunrise_ogle_xauusd.py`
   - `sunrise_ogle_xagusd.py`

## Expected Behavior After Fix
- Pullback counting continues normally regardless of time
- Time filter only blocks **final entry execution**, not state progression
- ARMED → WAITING_PULLBACK → WAITING_BREAKOUT transitions work 24/7
- Entry execution respects 7:00-18:00 UTC window

## Related Issues
- Time filter placement should only check at entry execution (Phase 4)
- Pullback phases (1-3) should not be time-restricted
- This allows setup detection outside hours, entry only during hours
