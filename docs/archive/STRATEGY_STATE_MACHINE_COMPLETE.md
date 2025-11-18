# ORIGINAL STRATEGY STATE MACHINE - Complete Documentation
**Date:** 2025-10-08  
**Source:** sunrise_ogle_audusd.py (and all other strategy files)

## 🎯 STATE MACHINE OVERVIEW

The strategy uses a **4-PHASE VOLATILITY EXPANSION CHANNEL** system:

```
SCANNING → ARMED_LONG/SHORT → WINDOW_OPEN → Entry/Reset
```

## 📊 STATE DEFINITIONS

### State 1: SCANNING
- **Purpose:** Monitor for initial EMA crossover signals
- **Transitions To:** ARMED_LONG or ARMED_SHORT
- **Reset Conditions:** None (always active when no setup)

### State 2: ARMED_LONG / ARMED_SHORT  
- **Purpose:** Wait for pullback confirmation
- **Pullback Counting:** Consecutive candles of opposite color
  - LONG: Requires `long_pullback_max_candles` BEARISH candles (close < open)
  - SHORT: Requires `short_pullback_max_candles` BULLISH candles (close > open)
- **Transitions To:** WINDOW_OPEN (when pullback complete)
- **Reset Conditions:** 
  - Non-pullback candle detected → SCANNING (Global Invalidation Rule)
  - Opposing signal detected → SCANNING (Global Invalidation Rule)

### State 3: WINDOW_OPEN
- **Purpose:** Monitor breakout window for entry trigger
- **Duration:** `long_entry_window_periods` or `short_entry_window_periods` bars
- **Window Calculation:**
  ```python
  # Time offset (optional)
  if use_window_time_offset:
      time_offset = pullback_candle_count * window_offset_multiplier
      window_start_bar = current_bar + time_offset
  
  # Price channel
  candle_range = last_pullback_high - last_pullback_low
  price_offset = candle_range * window_price_offset_multiplier
  window_top_limit = last_pullback_high + price_offset
  window_bottom_limit = last_pullback_low - price_offset
  ```
- **Transitions To:** 
  - Entry executed → Position opened
  - Window expires → ARMED_LONG/SHORT (return to pullback search)
  - Failure boundary broken → ARMED_LONG/SHORT (instability detected)
- **Reset Conditions:**
  - Window expires without breakout
  - Failure boundary broken
  - Time filter violation

## 🔄 PHASE LOGIC DETAILS

### PHASE 1: Scan for Signal (_phase1_scan_for_signal)
**Checks:**
1. EMA crossover detected (confirm vs fast/medium/slow)
2. Previous candle direction filter (optional)
3. EMA ordering condition (optional)
4. Price filter EMA (optional)
5. Angle filter (optional)
6. ATR volatility filter (optional)
7. **Time range filter (CRITICAL!)**

**Output:** 'LONG', 'SHORT', or None

**State Transition:**
```python
if signal_direction:
    entry_state = f"ARMED_{signal_direction}"
    armed_direction = signal_direction
    pullback_candle_count = 0
    # Store trigger candle for later validation
    signal_trigger_candle = {
        'open': data.open[-1],
        'close': data.close[-1],
        'datetime': data.datetime.datetime(-1),
        'is_bullish': data.close[-1] > data.open[-1],
        'is_bearish': data.close[-1] < data.open[-1]
    }
```

### PHASE 2: Confirm Pullback (_phase2_confirm_pullback)
**Logic:**
```python
def _phase2_confirm_pullback(armed_direction):
    # Check current candle is pullback type
    if armed_direction == 'LONG':
        is_pullback_candle = data.close[0] < data.open[0]  # Bearish
    else:  # SHORT
        is_pullback_candle = data.close[0] > data.open[0]  # Bullish
    
    if is_pullback_candle:
        pullback_candle_count += 1
        
        max_candles = (long_pullback_max_candles if armed_direction == 'LONG' 
                      else short_pullback_max_candles)
        
        if pullback_candle_count >= max_candles:
            # Store last pullback candle data
            last_pullback_candle_high = data.high[0]
            last_pullback_candle_low = data.low[0]
            return True  # Pullback complete
    else:
        # GLOBAL INVALIDATION RULE
        _reset_entry_state()  # Back to SCANNING
        
    return False
```

**Key Points:**
- ✅ Counts CONSECUTIVE pullback candles only
- ✅ Resets to SCANNING if non-pullback candle appears
- ✅ Uses current candle `[0]` not previous `[-1]`

### PHASE 3: Open Breakout Window (_phase3_open_breakout_window)
**Logic:**
```python
def _phase3_open_breakout_window(armed_direction):
    current_bar = len(self)
    
    # 1. Calculate window start (with optional time offset)
    window_start_bar = current_bar
    if use_window_time_offset:
        time_offset = int(pullback_candle_count * window_offset_multiplier)
        window_start_bar = current_bar + time_offset
    
    window_bar_start = window_start_bar
    
    # 2. Set window duration
    window_periods = (long_entry_window_periods if armed_direction == 'LONG' 
                     else short_entry_window_periods)
    window_expiry_bar = window_start_bar + window_periods
    
    # 3. Calculate price channel
    last_high = last_pullback_candle_high
    last_low = last_pullback_candle_low
    candle_range = last_high - last_low
    price_offset = candle_range * window_price_offset_multiplier
    
    window_top_limit = last_high + price_offset
    window_bottom_limit = last_low - price_offset
    
    # 4. Transition to WINDOW_OPEN
    entry_state = "WINDOW_OPEN"
```

### PHASE 4: Monitor Window (_phase4_monitor_window)
**Logic:**
```python
def _phase4_monitor_window(armed_direction):
    current_bar = len(self)
    
    # Check window active (time offset)
    if current_bar < window_bar_start:
        return 'PENDING'  # Not yet active
    
    # Check window expiry
    if current_bar >= window_expiry_bar:
        entry_state = f"ARMED_{armed_direction}"  # Return to pullback search
        return 'EXPIRED'
    
    # Monitor breakouts
    if armed_direction == 'LONG':
        # SUCCESS: Price breaks above top limit
        if data.high[0] > window_top_limit:
            return 'SUCCESS'
        # FAILURE: Price breaks below bottom limit (instability)
        elif data.low[0] < window_bottom_limit:
            entry_state = "ARMED_LONG"  # Return to pullback search
            return 'FAILURE'
    else:  # SHORT
        # SUCCESS: Price breaks below bottom limit
        if data.low[0] < window_bottom_limit:
            return 'SUCCESS'
        # FAILURE: Price breaks above top limit (instability)
        elif data.high[0] > window_top_limit:
            entry_state = "ARMED_SHORT"  # Return to pullback search
            return 'FAILURE'
    
    return None  # Still monitoring
```

## ⚠️ GLOBAL INVALIDATION RULE

**Applies to:** ARMED_LONG and ARMED_SHORT states

**Logic:**
```python
if entry_state in ["ARMED_LONG", "ARMED_SHORT"]:
    opposing_signal = None
    
    if entry_state == "ARMED_LONG":
        # Check for bearish crossover
        prev_bear = data.close[-1] < data.open[-1]
        cross_below = (confirm crosses below fast/medium/slow)
        if prev_bear and cross_below:
            opposing_signal = "SHORT"
    
    elif entry_state == "ARMED_SHORT":
        # Check for bullish crossover
        prev_bull = data.close[-1] > data.open[-1]
        cross_above = (confirm crosses above fast/medium/slow)
        if prev_bull and cross_above:
            opposing_signal = "LONG"
    
    if opposing_signal:
        _reset_entry_state()  # Back to SCANNING
```

## 🕐 TIME RANGE FILTER

**Critical:** Applied in TWO places:

### 1. PHASE 1 (Signal Detection)
```python
def _phase1_scan_for_signal():
    # ... other checks ...
    
    if use_time_range_filter:
        if not _is_in_trading_time_range(dt):
            return None  # Reject signal outside hours
    
    return signal_direction
```

### 2. PHASE 4 (Entry Execution)
```python
def _phase4_monitor_window():
    if breakout_status == 'SUCCESS':
        # Final time check before entry
        if not _is_in_trading_time_range(dt):
            _reset_entry_state()
            return
        
        # Execute entry...
```

**Time Check Logic:**
```python
def _is_in_trading_time_range(dt):
    current_time_minutes = dt.hour * 60 + dt.minute
    start_time_minutes = entry_start_hour * 60 + entry_start_minute
    end_time_minutes = entry_end_hour * 60 + entry_end_minute
    
    if start_time_minutes <= end_time_minutes:
        # Normal range (e.g., 09:00-17:00)
        return start_time_minutes <= current_time_minutes <= end_time_minutes
    else:
        # Overnight range (e.g., 23:00-16:00)
        return current_time_minutes >= start_time_minutes or current_time_minutes <= end_time_minutes
```

## 📝 KEY CONFIGURATION PARAMETERS

### AUDUSD Specific:
```python
# Direction
ENABLE_LONG_TRADES = True
ENABLE_SHORT_TRADES = False  # LONG-ONLY

# Pullback
LONG_USE_PULLBACK_ENTRY = True
LONG_PULLBACK_MAX_CANDLES = 2  # Requires 2 consecutive bearish candles
LONG_ENTRY_WINDOW_PERIODS = 1  # Monitor for 1 bar after pullback

# Time Range
USE_TIME_RANGE_FILTER = True
ENTRY_START_HOUR = 23  # UTC
ENTRY_END_HOUR = 16    # UTC
# This creates overnight range: 23:00 UTC → 16:00 UTC (next day)
```

## 🔍 COMMON MISTAKES TO AVOID

1. ❌ **Using `[-1]` instead of `[0]` for current candle**
   - Strategy uses `[0]` for current candle being formed
   - `[-1]` is the previous closed candle

2. ❌ **Not tracking consecutive pullback candles**
   - Must reset count if non-pullback candle appears
   - Can't just accumulate forever

3. ❌ **Ignoring time range filter**
   - Must check BOTH at signal detection AND entry execution

4. ❌ **Not implementing Global Invalidation Rule**
   - Opposing signals must reset armed states

5. ❌ **Showing SHORT logic when ENABLE_SHORT_TRADES = False**
   - Must check this setting before ANY SHORT processing

## ✅ GUI IMPLEMENTATION CHECKLIST

For `advanced_mt5_monitor_gui.py`:

- [ ] Read `ENABLE_SHORT_TRADES` from strategy configs
- [ ] Implement proper 4-phase state machine
- [ ] Track consecutive pullback candles correctly
- [ ] Reset on non-pullback candles (Global Invalidation)
- [ ] Check time range filter for signal detection
- [ ] Check time range filter before entry execution
- [ ] Use current candle `[0]` not previous `[-1]`
- [ ] Don't show SHORT indicators when SHORT disabled
- [ ] Implement window time offset logic
- [ ] Implement window expiry and failure boundary logic

---
**Status:** Documentation Complete - Ready for GUI Implementation  
**Next Step:** Rewrite `determine_strategy_phase()` function to match this exact logic
