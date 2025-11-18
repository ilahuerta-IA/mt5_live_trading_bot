# 🔧 Pullback Detection Diagnostic - Action Summary
**Date:** October 22, 2025  
**Issue:** USDCHF (and all symbols) show ARMED but pullback_count stuck at 0, no pullback logging

---

## 🐛 Problem Description

### User Report:
- **USDCHF** in `ARMED_LONG` state (screenshot 11:51:19)
- **Pullback Count:** 0 (should be counting bearish candles)
- **Window Active:** No
- **Terminal Log:** NO pullback detection messages after arming

### Expected Behavior:
After symbol enters ARMED state, EVERY closed candle should produce logging:
- `🔍 CHECKING CANDLE:` - Candle being analyzed
- `>> PULLBACK CANDLE:` - Valid pullback detected  
- `❌ NON-PULLBACK:` - Not a pullback candle
- `>> WAITING:` - Waiting for next candle

### Actual Behavior:
**ZERO pullback logs** appear after arming. Pullback count never increments.

---

## ✅ Diagnostic Code Implemented

### 1. State Machine Entry Diagnostic (Line ~1344)
```python
if entry_state in ['ARMED_LONG', 'ARMED_SHORT']:
    pullback_count = current_state.get('pullback_candle_count', 0)
    self.terminal_log(f"🔧 STATE: {symbol} processing | state={entry_state} | pullback_count={pullback_count} | df_len={len(df)}", 
                    "DEBUG", critical=True)
```

**Purpose:** Verify symbol reaches state machine processing with ARMED state

**If Missing:** Symbol not being processed in monitoring loop

---

### 2. ARMED Handler Entry Diagnostic (Line ~1451)
```python
self.terminal_log(f"🔧 DEBUG: {symbol} entered ARMED pullback check | armed_direction={armed_direction} | df_len={len(df)}", 
                "DEBUG", critical=True)
```

**Purpose:** Confirm code enters ARMED_LONG/ARMED_SHORT handler block

**If Missing:** 
- Time filter blocking (`_is_in_trading_time_range` returns False)
- SHORT disabled check triggering
- State variable mismatch

---

### 3. Candle Comparison Diagnostic (Line ~1467)
```python
last_checked = current_state.get('last_pullback_check_candle', 'NONE')
self.terminal_log(f"🔧 DEBUG: {symbol} pullback candle check | last_closed={last_closed_candle_time} | last_checked={last_checked} | Same? {last_closed_candle_time == last_checked}", 
                "DEBUG", critical=True)
```

**Purpose:** Show if candle skipped due to "already processed" logic

**If Missing:**
- DataFrame empty (`len(df) < 1`)
- df.index[-1] invalid

---

## 🎯 Testing Protocol

### Step 1: Restart Monitor
```bash
python start_advanced_monitor.py
```

### Step 2: Wait for ARMED State
- Monitor terminal for any symbol to go ARMED
- Focus on USDCHF if possible (next crossover)

### Step 3: Collect Diagnostic Output
Look for debug messages in this order:
1. `🔧 STATE:` - Symbol processing 
2. `🔧 DEBUG:` - ARMED handler entry
3. `🔧 DEBUG:` - Candle comparison
4. `🔍 CHECKING CANDLE:` - Pullback detection

### Step 4: Identify Break Point
**First missing message indicates root cause:**

| Missing Message | Root Cause | Fix Location |
|----------------|-----------|--------------|
| `🔧 STATE:` | Symbol not processed | Monitoring loop filter |
| `🔧 DEBUG:` (handler) | Time filter / state check | Lines 1324-1330 or 1447-1452 |
| `🔧 DEBUG:` (candle) | Empty DataFrame | Data fetching logic |
| `🔍 CHECKING CANDLE:` | Already processed logic | Line 1458 condition |

---

## 🔍 Root Cause Candidates

### Candidate 1: Time Filter Blocking (Likely 40%)
**Code:** Lines 1324-1330
```python
if not self._is_in_trading_time_range(current_dt, config):
    return entry_state
```

**Symptom:** 
- `🔧 STATE:` appears
- `🔧 DEBUG:` (handler) missing
- `⏰ Outside trading hours` log appears

**Fix:** Adjust time range in strategy config or disable filter

---

### Candidate 2: DataFrame Empty After Arming (Likely 30%)
**Code:** Lines 1457
```python
elif len(df) >= 1:
```

**Symptom:**
- `🔧 STATE:` appears
- `🔧 DEBUG:` (handler) appears  
- `🔧 DEBUG:` (candle) missing

**Fix:** Investigate data fetching after arming event

---

### Candidate 3: Already Processed Logic Bug (Likely 20%)
**Code:** Line 1458
```python
if 'last_pullback_check_candle' in current_state and current_state['last_pullback_check_candle'] == last_closed_candle_time:
```

**Symptom:**
- All `🔧 DEBUG:` appear
- `🔍 CHECKING CANDLE:` missing
- Only `>> WAITING:` appears continuously

**Fix:** Logic error in timestamp comparison

---

### Candidate 4: State Variable Corruption (Likely 10%)
**Code:** Lines 1447-1451
```python
elif entry_state in ['ARMED_LONG', 'ARMED_SHORT']:
```

**Symptom:**
- `🔧 STATE:` shows different state than expected
- Handler never entered

**Fix:** Track where `entry_state` is modified

---

## 📝 Diagnostic Output Examples

### Expected WORKING Output:
```
[11:51:20] 🔧 STATE: USDCHF processing | state=ARMED_LONG | pullback_count=0 | df_len=100
[11:51:20] 🔧 DEBUG: USDCHF entered ARMED pullback check | armed_direction=LONG | df_len=100
[11:51:20] 🔧 DEBUG: USDCHF pullback candle check | last_closed=2025-10-22 12:50:00 | last_checked=2025-10-22 12:45:00 | Same? False
[11:51:20] 🔍 CHECKING CANDLE: USDCHF LONG | Time: 2025-10-22 12:50:00 | O:0.79610 H:0.79615 L:0.79605 C:0.79612 | Count: 0/2
[11:51:20] >> PULLBACK CANDLE: USDCHF LONG #1/2 | BEARISH (Red) | O:0.79615 H:0.79618 L:0.79608 C:0.79610
[11:51:20] 📉 USDCHF: Bearish pullback #1/2 detected (need 1 more)
```

### If Time Filter Blocking:
```
[11:51:20] 🔧 STATE: USDCHF processing | state=ARMED_LONG | pullback_count=0 | df_len=100
[11:51:20] ⏰ USDCHF: Outside trading hours - state machine paused (Current: ARMED_LONG)
```

### If DataFrame Empty:
```
[11:51:20] 🔧 STATE: USDCHF processing | state=ARMED_LONG | pullback_count=0 | df_len=0
```
(No handler entry log)

### If Already Processed Bug:
```
[11:51:20] 🔧 STATE: USDCHF processing | state=ARMED_LONG | pullback_count=0 | df_len=100
[11:51:20] 🔧 DEBUG: USDCHF entered ARMED pullback check | armed_direction=LONG | df_len=100
[11:51:20] 🔧 DEBUG: USDCHF pullback candle check | last_closed=2025-10-22 12:50:00 | last_checked=2025-10-22 12:50:00 | Same? True
[11:51:20] >> WAITING: USDCHF LONG waiting for next Bearish candle | count=0/2
```

---

## 📊 Files Modified

### `advanced_mt5_monitor_gui.py`
- **Line ~1344:** Added state processing diagnostic
- **Line ~1451:** Added ARMED handler entry diagnostic  
- **Line ~1467:** Added candle comparison diagnostic

### `docs/PULLBACK_DETECTION_BUG_DIAGNOSTIC.md`
- Full technical analysis
- Code location references
- Testing protocols

### `docs/DIAGNOSTIC_ACTION_SUMMARY.md` (this file)
- Quick reference for debugging
- Expected outputs
- Next steps

---

## 🚀 Next Actions

1. ✅ **Diagnostic code added** (3 log points)
2. ⏳ **Restart monitor** - Get fresh state
3. ⏳ **Wait for ARMED** - Any symbol entering ARMED state
4. ⏳ **Collect diagnostics** - Check which messages appear
5. ⏳ **Identify root cause** - First missing message
6. ⏳ **Apply fix** - Based on root cause analysis
7. ⏳ **Verify fix** - Confirm pullback counting works
8. ⏳ **Clean up** - Remove diagnostic code

---

## ⚠️ Critical Reminders

- **DO NOT** modify `strategies/*.py` files (backtrader source of truth)
- All fixes in `advanced_mt5_monitor_gui.py` only
- Keep diagnostic logs at `critical=True` for visibility
- Test with LIVE data, not replay
- Monitor for at least 2-3 candle closes after arming

---

**Status:** ⏳ Ready for diagnostic test  
**Priority:** 🔴 CRITICAL - Pullback detection completely broken  
**Impact:** ALL symbols affected, no pullback counting working
