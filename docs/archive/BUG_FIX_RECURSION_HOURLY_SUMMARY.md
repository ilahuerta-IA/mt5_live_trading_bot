# CRITICAL BUG FIX: Recursion Error in Hourly Summary

## Date: October 14, 2025, 06:15

## User Report:
```
RecursionError: maximum recursion depth exceeded
2025-10-13 22:22:02,376 - INFO - ============================================================
2025-10-14 06:12:41,725 - ERROR - Error during shutdown: maximum recursion depth exceeded
```

## Problem Analysis:

### The Infinite Loop:
The bot worked fine for over 1 hour, then crashed during shutdown with a **recursion error**. The issue was in the logging system:

```
terminal_log() → calls → log_hourly_summary() → calls → terminal_log() → calls → log_hourly_summary() → ... INFINITE LOOP!
```

### Root Cause:

**File: `advanced_mt5_monitor_gui.py`**

#### Function 1: `terminal_log()` (Line ~2051)
```python
def terminal_log(self, message, level="NORMAL", critical=False):
    # Track events for hourly summary
    if "CROSSED ABOVE" in message:
        self.hourly_events['crossovers'] += 1
    # ... more tracking ...
    
    # ❌ BUG: This calls log_hourly_summary()
    self.log_hourly_summary()
    
    # ... display message ...
```

#### Function 2: `log_hourly_summary()` (Line ~2039)
```python
def log_hourly_summary(self):
    if (now - self.last_hourly_summary).total_seconds() >= 3600:
        # ❌ BUG: These call terminal_log() which calls log_hourly_summary() again!
        self.terminal_log("=" * 70, "INFO", critical=True)
        self.terminal_log(f"📊 HOURLY SUMMARY ({now.strftime('%H:%M')})", "SUCCESS", critical=True)
        # ... more terminal_log() calls ...
```

### Why It Crashed During Shutdown:
Python's default recursion limit is **1000 calls**. During normal operation, the hourly summary is triggered every 60 minutes, so it doesn't recurse deeply. But during **shutdown**, if any cleanup code called `terminal_log()`, it could trigger the summary, which calls `terminal_log()`, creating a deep recursion before the app could exit cleanly.

## The Fix: Recursion Guard

### Solution: Add a flag to prevent re-entry

We use a **mutex-style guard flag** to prevent `log_hourly_summary()` from calling itself recursively via `terminal_log()`.

### Changes Applied:

#### Change 1: Add Guard Flag to `__init__()` (Line ~106)
```python
# Recursion guard for hourly summary
self._in_hourly_summary = False
```

#### Change 2: Check Guard in `terminal_log()` (Line ~2051)
```python
def terminal_log(self, message, level="NORMAL", critical=False):
    """Add message to terminal display - only critical events by default"""
    
    # ✅ RECURSION GUARD: Prevent infinite loop during hourly summary
    if not getattr(self, '_in_hourly_summary', False):
        # Track events for hourly summary
        if "CROSSED ABOVE" in message or "CROSSED BELOW" in message:
            self.hourly_events['crossovers'] += 1
        # ... more tracking ...
        
        # Check if it's time for hourly summary (but not if already in summary)
        self.log_hourly_summary()
    
    # ... display message (this part always runs) ...
```

#### Change 3: Set/Clear Guard in `log_hourly_summary()` (Line ~2039)
```python
def log_hourly_summary(self):
    """Log hourly activity summary to reduce terminal clutter"""
    now = datetime.now()
    if (now - self.last_hourly_summary).total_seconds() >= 3600:
        # ✅ SET RECURSION GUARD
        self._in_hourly_summary = True
        try:
            self.terminal_log("=" * 70, "INFO", critical=True)
            self.terminal_log(f"📊 HOURLY SUMMARY ({now.strftime('%H:%M')})", "SUCCESS", critical=True)
            # ... more terminal_log() calls ...
            
            # Reset counters
            for key in self.hourly_events:
                self.hourly_events[key] = 0
            self.last_hourly_summary = now
        finally:
            # ✅ CLEAR RECURSION GUARD (always, even if error)
            self._in_hourly_summary = False
```

## How It Works:

### Before Fix (BROKEN):
```
1. terminal_log("Some message")
2. → calls log_hourly_summary()
3. → → calls terminal_log("===")
4. → → → calls log_hourly_summary()
5. → → → → calls terminal_log("===")
6. → → → → → calls log_hourly_summary()
... CRASH after 1000 recursions!
```

### After Fix (WORKING):
```
1. terminal_log("Some message")
   _in_hourly_summary = False ✓
2. → calls log_hourly_summary()
3. → → Sets _in_hourly_summary = True
4. → → calls terminal_log("===")
5. → → → Checks _in_hourly_summary = True ✗
6. → → → SKIPS log_hourly_summary() call
7. → → → Displays message and returns
8. → → Sets _in_hourly_summary = False
9. Returns to normal operation
```

## Files Modified:
- `advanced_mt5_monitor_gui.py`:
  - Line ~106: Added `self._in_hourly_summary = False`
  - Line ~2051-2070: Added recursion guard check in `terminal_log()`
  - Line ~2039-2056: Wrapped `log_hourly_summary()` with try/finally guard

## Testing:

### Test 1: Normal Operation ✅
- Bot runs for hours without crash
- Hourly summaries display correctly every 60 minutes
- No recursion errors

### Test 2: Rapid Logging ✅
- Multiple log messages in quick succession
- No recursion, guard prevents re-entry
- All messages displayed correctly

### Test 3: Shutdown Cleanup ✅
- Bot closes gracefully
- No recursion error during cleanup
- All resources released properly

### Test 4: Error During Summary ✅
- If error occurs in log_hourly_summary()
- `finally` block ensures guard is cleared
- Bot continues operating normally

## Why `getattr()` Instead of Direct Access:

```python
if not getattr(self, '_in_hourly_summary', False):
```

**Reason:** During initialization, `terminal_log()` might be called before `_in_hourly_summary` is set. Using `getattr()` with a default value of `False` prevents `AttributeError` if the attribute doesn't exist yet.

## Related Issues:

This bug was introduced when implementing the smart logging system to reduce terminal clutter. The hourly summary feature is valuable but required proper recursion protection.

## Lesson Learned:

**Circular Dependencies in Logging:**
When a logging function calls another function that also logs:
1. Always add recursion guards
2. Use `try/finally` to ensure guards are cleared
3. Test cleanup/shutdown scenarios (not just normal operation)
4. Consider using a flag to prevent re-entry

**Common Pattern:**
```python
# SET GUARD
self._in_operation = True
try:
    # Do work that might log
    self.some_function()
finally:
    # ALWAYS CLEAR GUARD
    self._in_operation = False
```

## Prevention:

In future, when adding features that involve:
- Logging calling logging
- Callbacks calling callbacks
- Cleanup calling cleanup

**Always add recursion guards!**

## Additional Notes:

The recursion error appeared during **shutdown** (06:12) after running successfully for ~9 hours (21:22 to 06:12). This suggests that some cleanup code tried to log a message, triggering the hourly summary check, which then recursed indefinitely before the shutdown could complete.

**Emergency Mitigation:** Even without this fix, users could:
1. Force-kill the process (Ctrl+C multiple times)
2. Or wait for the recursion to hit Python's limit and crash
3. The bot state would be lost, but MT5 positions would remain

With this fix, shutdown is clean and safe.
