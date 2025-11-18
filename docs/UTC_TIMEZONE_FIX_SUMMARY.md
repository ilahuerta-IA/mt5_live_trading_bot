# UTC TIMEZONE FIX - IMPLEMENTATION SUMMARY

## ✅ COMPLETED - GUI Changes

### 1. Added UTC Offset Selector to GUI
**File**: `advanced_mt5_monitor_gui.py`

**Changes Made**:
- Added UTC offset dropdown in Monitoring Controls panel
- Options: "UTC+1" (winter) and "UTC+2" (summer)
- Default: UTC+1 (loaded from config file)

**Features**:
- Saves selection to `config/broker_timezone.json`
- Loads previous selection on startup
- Shows user-friendly messages when changed

### 2. Created Broker Timezone Config File
**File**: `config/broker_timezone.json`

**Contents**:
```json
{
    "utc_offset": 1,
    "description": "Broker timezone offset from UTC",
    "last_updated": "2025-11-18"
}
```

---

## ⏳ PENDING - Strategy File Changes

The following function needs to be added to **4 strategy files** (assets with time filter enabled):
- `strategies/sunrise_ogle_eurusd.py`
- `strategies/sunrise_ogle_audusd.py`
- `strategies/sunrise_ogle_xagusd.py`
- `strategies/sunrise_ogle_usdchf.py`

### Function to Add:

```python
def _is_in_trading_time_range(self, dt):
    """Check if current time is within configured trading hours
    
    Converts broker time to UTC using offset from config file before checking.
    This ensures time filter works correctly regardless of broker timezone.
    
    Args:
        dt: datetime object from broker (in broker's local time)
        
    Returns:
        bool: True if within trading hours, False otherwise
    """
    if not self.p.use_time_range_filter:
        return True
    
    # Load UTC offset from config file
    utc_offset = 1  # Default
    try:
        import os
        import json
        config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'broker_timezone.json')
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                utc_offset = config_data.get('utc_offset', 1)
    except Exception as e:
        # If config file doesn't exist or can't be read, use default UTC+1
        pass
    
    # Convert broker time to UTC by subtracting offset
    from datetime import timedelta
    utc_time = dt - timedelta(hours=utc_offset)
    
    current_hour = utc_time.hour
    current_minute = utc_time.minute
    
    start_hour = self.p.entry_start_hour
    start_minute = self.p.entry_start_minute
    end_hour = self.p.entry_end_hour
    end_minute = self.p.entry_end_minute
    
    # Convert times to minutes since midnight for easier comparison
    current_time_minutes = current_hour * 60 + current_minute
    start_time_minutes = start_hour * 60 + start_minute
    end_time_minutes = end_hour * 60 + end_minute
    
    # Handle overnight ranges (e.g., 21:00 to 03:00)
    if start_time_minutes > end_time_minutes:
        # Trading window crosses midnight
        return current_time_minutes >= start_time_minutes or current_time_minutes <= end_time_minutes
    else:
        # Normal trading window (same day)
        return start_time_minutes <= current_time_minutes <= end_time_minutes
```

### Where to Add:

Add this function in the "Helper methods" section of each strategy file, around line 2000-2100, near other filter validation functions like `_validate_all_entry_filters()`.

---

## 🎯 HOW IT WORKS

### Example: EURUSD (21:00-03:00 UTC desired)

**Winter (UTC+1)**:
- GUI set to: UTC+1
- Broker time: 22:00 Madrid
- Function converts: 22:00 - 1 = 21:00 UTC ✅
- Check: Is 21:00 UTC between 21:00-03:00? YES → Allow trade

**Summer (UTC+2)**:
- GUI set to: UTC+2  
- Broker time: 23:00 Madrid
- Function converts: 23:00 - 2 = 21:00 UTC ✅
- Check: Is 21:00 UTC between 21:00-03:00? YES → Allow trade

**Outside hours**:
- Broker time: 20:00 Madrid (winter UTC+1)
- Function converts: 20:00 - 1 = 19:00 UTC ❌
- Check: Is 19:00 UTC between 21:00-03:00? NO → Block trade

---

## 📋 NEXT STEPS

1. **Add the function** to the 4 strategy files listed above
2. **Rebuild the executable**: Run `setup.ps1` or manually run PyInstaller
3. **Test with MT5**: 
   - Change UTC offset in GUI
   - Verify config file updates
   - Check that time filter correctly blocks/allows trades

---

## ✅ VERIFICATION CHECKLIST

After implementation:

- [ ] GUI shows UTC offset dropdown
- [ ] Changing offset updates `config/broker_timezone.json`
- [ ] Config file persists between restarts
- [ ] EURUSD blocks trades outside 21:00-03:00 UTC (converted)
- [ ] AUDUSD blocks trades outside 23:00-07:30 UTC (converted)
- [ ] XAGUSD blocks trades outside 00:00-08:30 UTC (converted)
- [ ] USDCHF blocks trades outside 07:00-13:00 UTC (converted)
- [ ] Logs still show broker time (not converted)
- [ ] GBPUSD and XAUUSD unaffected (no time filter)

---

## 🔧 MANUAL TESTING PROCEDURE

1. Set GUI to UTC+1
2. Set system time to 22:00 Madrid time
3. Verify EURUSD allows trade (22:00-1=21:00 UTC ✅)
4. Set system time to 20:00 Madrid time  
5. Verify EURUSD blocks trade (20:00-1=19:00 UTC ❌)
6. Change GUI to UTC+2
7. Set system time to 23:00 Madrid time
8. Verify EURUSD allows trade (23:00-2=21:00 UTC ✅)

---

**Created**: 2025-11-18
**Status**: GUI Complete, Strategy Functions Pending
