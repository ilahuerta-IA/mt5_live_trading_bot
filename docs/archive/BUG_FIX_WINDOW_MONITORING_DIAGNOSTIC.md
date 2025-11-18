# 🐛 BUG FIX: AUDUSD WINDOW_OPEN Monitoring Diagnostic
**Date**: October 22, 2025  
**Issue**: AUDUSD stuck in WINDOW_OPEN phase with no monitoring  
**Status**: ✅ DIAGNOSTIC LOGGING ADDED

---

## 🔍 PROBLEM IDENTIFICATION

### User Report
- **Screenshot Time**: 16:12:00
- **AUDUSD State**: WINDOW_OPEN (Pullback Count: 2)
- **Issue**: No window monitoring happening after window opened

### Log Analysis
```
15:50:04.193 | ✅ AUDUSD: Pullback CONFIRMED (2/2) - Window OPENING
15:50:04.193 | 📊 AUDUSD: WAITING_BREAKOUT → WINDOW_OPEN
[SILENCE - NO LOGS AFTER THIS]
```

### Comparison with Working Assets
| Asset | Window Opened | Next Event | Time Gap | Status |
|-------|---------------|------------|----------|--------|
| **EURUSD** | 15:55:04 | BREAKOUT 16:00 | 5 min | ✅ Working |
| **GBPUSD** | 15:50:04 | BREAKOUT 16:05 | 15 min | ✅ Working |
| **XAUUSD** | 16:00:04 | FAILURE 16:05 | 5 min | ✅ Working |
| **AUDUSD** | 15:50:04 | NO LOGS | 22+ min | ❌ STUCK |

---

## 🔎 ROOT CAUSE ANALYSIS

### Missing Diagnostic Logs
**File**: `advanced_mt5_monitor_gui.py`  
**Lines**: 1364-1366

```python
# ❌ PROBLEM: Only ARMED states have diagnostic logging
if entry_state in ['ARMED_LONG', 'ARMED_SHORT']:
    pullback_count = current_state.get('pullback_candle_count', 0)
    self.terminal_log(f"🔧 STATE: {symbol} processing | state={entry_state}...", 
                    "DEBUG", critical=True)
# ❌ NO DIAGNOSTIC LOG FOR WINDOW_OPEN!
```

### Phase 4 Monitor Logic Exists
**File**: `advanced_mt5_monitor_gui.py`  
**Lines**: 1600-1630

```python
# ✅ Window monitoring code EXISTS
elif entry_state == 'WINDOW_OPEN':
    armed_direction = current_state['armed_direction']
    breakout_status = self._phase4_monitor_window(symbol, df, armed_direction, ...)
    
    if breakout_status == 'SUCCESS':
        self.terminal_log(f"✅ {symbol}: BREAKOUT detected...", "SUCCESS", critical=True)
```

### Hypothesis
**The window monitoring code EXISTS and SHOULD be running**, but there's NO diagnostic logging to confirm:
1. ✅ Code path is being executed
2. ✅ _phase4_monitor_window is being called
3. ✅ Breakout checks are happening

Without diagnostic logs, we cannot verify if:
- AUDUSD is being processed in the monitoring loop
- Window boundaries are being checked
- Price data is being compared correctly

---

## 🛠️ FIX IMPLEMENTED

### Added WINDOW_OPEN Diagnostic Logging
**File**: `advanced_mt5_monitor_gui.py`  
**Lines**: 1364-1371 (NEW)

```python
try:
    # ✅ DIAGNOSTIC: Log state machine processing
    if entry_state in ['ARMED_LONG', 'ARMED_SHORT']:
        pullback_count = current_state.get('pullback_candle_count', 0)
        self.terminal_log(f"🔧 STATE: {symbol} processing | state={entry_state} | pullback_count={pullback_count} | df_len={len(df)}", 
                        "DEBUG", critical=True)
    elif entry_state == 'WINDOW_OPEN':
        # ⚠️ CRITICAL: Add diagnostic logging for WINDOW_OPEN phase
        window_active = current_state.get('window_active', False)
        armed_direction = current_state.get('armed_direction', 'Unknown')
        self.terminal_log(f"🔧 WINDOW: {symbol} monitoring | state={entry_state} | direction={armed_direction} | active={window_active} | df_len={len(df)}", 
                        "DEBUG", critical=True)
```

---

## 🧪 TESTING PLAN

### Expected Log Output (Next Run)
When AUDUSD enters WINDOW_OPEN phase, we should see:
```
15:55:00 | 🔧 WINDOW: AUDUSD monitoring | state=WINDOW_OPEN | direction=LONG | active=True | df_len=500
16:00:00 | 🔧 WINDOW: AUDUSD monitoring | state=WINDOW_OPEN | direction=LONG | active=True | df_len=500
16:05:00 | 🔧 WINDOW: AUDUSD monitoring | state=WINDOW_OPEN | direction=LONG | active=True | df_len=500
```

### Verification Checklist
- [ ] AUDUSD shows "🔧 WINDOW:" logs every 5 minutes
- [ ] Window boundaries are being checked
- [ ] Breakout or failure events are detected
- [ ] If NO logs appear → monitoring loop NOT processing WINDOW_OPEN assets

### Next Steps If Still Silent
If AUDUSD still shows NO logs after this fix:
1. **Check monitoring loop** (line 731): Verify all symbols are processed
2. **Check determine_strategy_phase** (line 1330): Verify WINDOW_OPEN path
3. **Check _phase4_monitor_window** (line 1260): Add internal diagnostic logs

---

## 📊 BACKTRADER STRATEGY VERIFICATION

### Original Strategy Behavior (Line 1170-1220)
```python
def _phase4_monitor_window(self, armed_direction):
    """PHASE 4: Monitor for breakout or failure"""
    
    if armed_direction == 'LONG':
        # Check SUCCESS condition (break above top_limit)
        if current_high >= self.window_top_limit:
            print(f"SUCCESS BREAKOUT (LONG)...")
            return 'SUCCESS'
        
        # Check FAILURE condition (break below bottom_limit)
        elif current_low <= self.window_bottom_limit:
            print(f"FAILURE BREAKOUT (LONG): Instability detected.")
            self.entry_state = "ARMED_LONG"  # Return to pullback search
            self.pullback_candle_count = 0
            return None
```

### MT5 Monitor Implementation (Line 1260-1310)
```python
def _phase4_monitor_window(self, symbol, df, armed_direction, current_bar, current_dt, config):
    """Phase 4: Monitor breakout window"""
    state = self.strategy_states[symbol]
    
    # Check window active
    if current_bar < state['window_bar_start']:
        return 'PENDING'
    
    # Check window expiry
    if current_bar > state['window_expiry_bar']:
        return 'EXPIRED'
    
    # Monitor breakouts
    if armed_direction == 'LONG':
        if current_high >= state['window_top_limit']:
            return 'SUCCESS'
        elif current_low <= state['window_bottom_limit']:
            return 'FAILURE'
```

**✅ VERDICT**: Implementation matches original strategy

---

## 🎯 SUCCESS CRITERIA

### Diagnostic Success
- [x] WINDOW_OPEN diagnostic logging added
- [ ] Logs appear for AUDUSD in WINDOW_OPEN phase
- [ ] Can trace execution flow through Phase 4

### Functional Success
- [ ] AUDUSD window monitoring processes each candle
- [ ] Breakout detection works correctly
- [ ] Failure boundary detection works correctly
- [ ] Window timeout detection works correctly

---

## 📝 NOTES

**Key Insight**: The absence of diagnostic logs doesn't mean the code isn't running - it just means we can't SEE it running. This fix adds visibility to the WINDOW_OPEN phase, which is critical for debugging why AUDUSD appears stuck.

**Next Investigation**: If logs still don't appear, the issue is likely in the monitoring loop itself (line 731) not iterating through symbols in WINDOW_OPEN state, OR the `determine_strategy_phase` function returning early for some reason.

---

**COMMIT MESSAGE**:
```
fix: Add diagnostic logging for WINDOW_OPEN phase monitoring

- Add 🔧 WINDOW diagnostic logs for assets in WINDOW_OPEN state
- Match existing ARMED state logging format
- Shows direction, active status, and df length
- Helps debug AUDUSD stuck in WINDOW_OPEN issue
- Lines 1364-1371 in advanced_mt5_monitor_gui.py
```
