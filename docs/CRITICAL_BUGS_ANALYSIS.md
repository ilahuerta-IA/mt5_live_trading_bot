# CRITICAL BUGS FOUND - ANALYSIS & FIX

## Issue Summary
After reviewing terminal log `terminal_log_20251009_204442.txt`, TWO CRITICAL BUGS identified:

### Bug 1: Pullback Count Still Incrementing Uncontrolled
**Evidence:**
```
[19:42:44.998] 🟢 GBPUSD: Pullback CONFIRMED (29/2) - Window OPENING
[19:42:49.262] 🟢 GBPUSD: Pullback CONFIRMED (30/2) - Window OPENING
[19:42:53.503] 🟢 GBPUSD: Pullback CONFIRMED (31/2) - Window OPENING
...
[19:44:44.266] 🟢 GBPUSD: Pullback CONFIRMED (57/2) - Window OPENING
```

```
[20:20:12.043] 📊 EURUSD: WAITING_BREAKOUT → WINDOW_OPEN
[20:20:16.216] 🟢 EURUSD: Pullback CONFIRMED (3/2) - Window OPENING
[20:20:20.437] 🟢 EURUSD: Pullback CONFIRMED (4/2) - Window OPENING
...
[20:24:24.344] 🟢 EURUSD: Pullback CONFIRMED (62/2) - Window OPENING
```

**Root Cause:**
Previous fix updated `current_state['entry_state'] = 'WINDOW_OPEN'` when pullback confirmed, BUT when window expires, code returns to ARMED state **WITHOUT resetting pullback count**:

```python
elif breakout_status == 'EXPIRED':
    # Return to ARMED state to search for more pullback
    current_state['entry_state'] = f"ARMED_{armed_direction}"  # ✅ State reset
    current_state['phase'] = 'WAITING_PULLBACK'
    current_state['window_active'] = False
    entry_state = f"ARMED_{armed_direction}"
    # ❌ pullback_candle_count NOT reset!
```

So the cycle becomes:
1. Pullback 2/2 → Window opens
2. Window expires → Return to ARMED_LONG  
3. Next pullback detected → Count increments to 3/2 (should be reset to 1!)
4. 3/2 >= 2 → Window opens again
5. Repeat forever...

### Bug 2: Windows Expire Too Fast (2 Seconds!)
**Evidence:**
```
[20:20:12.043] 📊 EURUSD: WAITING_BREAKOUT → WINDOW_OPEN | Price: 1.15588
[20:20:14.115] ⏱️ EURUSD: Window EXPIRED - Returning to pullback search
```
Window opens and expires **2 seconds later** instead of lasting multiple bars!

**Root Cause:**
Line ~1074 in determine_strategy_phase():
```python
# Increment bar counter
current_state['current_bar'] += 1
current_bar = current_state['current_bar']
```

This increments `current_bar` **every monitoring loop** (~2 seconds), NOT per candle!

In original strategy, `current_bar` increments once per **NEW CANDLE** (e.g., H1 = 1 hour, M15 = 15 minutes).

**Impact:**
- Window set to expire at `window_start_bar + window_periods` (e.g., bar 100 + 1 = 101)
- 2 seconds later → `current_bar` = 101 → Window expired!
- Original intention: Window lasts 1 candle period (H1 = 1 hour, not 2 seconds)

## Original Strategy Bar Counting

In Backtrader (original strategy):
- **Bar counter increments once per new candle**
- H1 chart: Bar 1 = 1st hour, Bar 2 = 2nd hour
- Each `next()` call = new candle completed
- Time-based, not tick-based

In GUI Monitor (current buggy implementation):
- **Bar counter increments every monitoring loop** (~2 seconds)
- Bar 100 at 20:20:12
- Bar 101 at 20:20:14 (2 seconds later)
- Completely wrong - not tracking actual candles!

## The Fix

### Fix 1: Reset Pullback Count When Window Expires

**Location:** Line ~1283 in `determine_strategy_phase()`

**Before:**
```python
elif breakout_status == 'EXPIRED':
    self.terminal_log(f"⏱️ {symbol}: Window EXPIRED - Returning to pullback search", 
                    "WARNING", critical=True)
    # Return to ARMED state to search for more pullback
    current_state['entry_state'] = f"ARMED_{armed_direction}"
    current_state['phase'] = 'WAITING_PULLBACK'
    current_state['window_active'] = False
    entry_state = f"ARMED_{armed_direction}"
```

**After:**
```python
elif breakout_status == 'EXPIRED':
    self.terminal_log(f"⏱️ {symbol}: Window EXPIRED - Returning to pullback search", 
                    "WARNING", critical=True)
    # Return to ARMED state to search for more pullback
    current_state['entry_state'] = f"ARMED_{armed_direction}"
    current_state['phase'] = 'WAITING_PULLBACK'
    current_state['window_active'] = False
    current_state['pullback_candle_count'] = 0  # ✅ RESET pullback count!
    entry_state = f"ARMED_{armed_direction}"
```

**Same fix needed for 'FAILURE' case** (Line ~1292).

### Fix 2: Bar Counter Should Track Candles, Not Ticks

This is **MUCH more complex**. The bar counter should only increment when a new candle forms, not on every monitoring loop.

**Options:**

#### Option A: Track candle timestamps (RECOMMENDED)
Store last candle timestamp and only increment when new candle detected:

```python
# At start of determine_strategy_phase()
if len(df) > 0:
    current_candle_time = df.index[-1]
    
    # Check if this is a new candle
    if 'last_candle_time' not in current_state or current_state['last_candle_time'] != current_candle_time:
        current_state['current_bar'] += 1
        current_state['last_candle_time'] = current_candle_time
    
    current_bar = current_state['current_bar']
```

#### Option B: Use actual bar count from dataframe
Simply use the length of the dataframe:

```python
current_bar = len(df)
```

**Problem with Option B:** If dataframe is constantly growing, bar numbers keep increasing indefinitely and never reset.

#### Option C: Use relative bar counting from window start
Instead of absolute bar numbers, track bars relative to window opening:

```python
# When window opens:
state['window_start_bar'] = 0
state['window_expiry_bar'] = window_periods

# When monitoring:
bars_since_window_open = <calculate based on candle timestamps>
if bars_since_window_open >= state['window_expiry_bar']:
    return 'EXPIRED'
```

## Recommended Implementation

### Step 1: Fix Pullback Count Reset (IMMEDIATE)
Add `current_state['pullback_candle_count'] = 0` when window expires or fails.

### Step 2: Fix Bar Counting (REQUIRES CAREFUL IMPLEMENTATION)
Use Option A - track candle timestamps to detect new candles.

## Testing Requirements

After fixes:
1. **Pullback count should reset:**
   ```
   [Time 1] Pullback CONFIRMED (2/2) - Window OPENING
   [Time 2] Window EXPIRED - Returning to pullback search
   [Time 3] Pullback counting (1/2)  ← Should be 1/2, not 3/2
   [Time 4] Pullback CONFIRMED (2/2) - Window OPENING
   ```

2. **Window should last for configured periods (e.g., 1 H1 candle = 1 hour):**
   ```
   [20:20:00] Window OPENING (Bar 100, expires at 101)
   [20:20:02] Still monitoring (Bar 100 - same candle)
   [20:30:00] Still monitoring (Bar 100 - same candle)
   [21:00:00] New candle → Bar 101 → Window EXPIRED
   ```

## Priority

**CRITICAL - BOTH BUGS BREAK STRATEGY COMPLETELY**

1. Bug 1 (pullback count): Causes infinite pullback confirmations
2. Bug 2 (bar counting): Windows expire in 2 seconds instead of hours

Both must be fixed for monitor to work correctly.
