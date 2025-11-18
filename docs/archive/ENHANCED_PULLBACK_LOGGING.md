# ENHANCED TERMINAL LOGGING FOR PULLBACK ANALYSIS

**Date:** October 17, 2025  
**Purpose:** Added comprehensive logging to track every candle checked in ARMED state  
**Export:** All messages logged to `terminal_log_YYYYMMDD_HHMMSS.txt` file

---

## New Logging Messages Added

### 1. **Entering ARMED State**
When a crossover is detected and system enters ARMED state:

```
🎯 EURUSD: LONG CROSSOVER - State: SCANNING → ARMED_LONG | Price: 1.17052
📋 EURUSD: NOW MONITORING for 2 BEARISH (Red) pullback candles...
```

**Information shown:**
- Symbol
- Direction (LONG/SHORT)
- Current price
- Number of pullback candles required
- Type of candles needed (BEARISH for LONG, BULLISH for SHORT)

---

### 2. **Every Candle Checked**
For EVERY closed candle that arrives while in ARMED state:

```
🔍 CHECKING CANDLE: EURUSD ARMED_LONG | Time: 2025-10-17 06:25:00 | O:1.17050 H:1.17055 L:1.17045 C:1.17048 | Count: 0/2
```

**Information shown:**
- Symbol and armed direction
- Candle close time (exact timestamp)
- OHLC values (Open, High, Low, Close)
- Current pullback count / Total needed

---

### 3. **Pullback Candle Detected**
When a valid pullback candle is found:

```
>> PULLBACK CANDLE: EURUSD LONG #1/2 | BEARISH (Red) | O:1.17050 H:1.17055 L:1.17045 C:1.17048
📉 EURUSD: Bearish pullback #1/2 detected (need 1 more)
```

**Information shown:**
- Symbol and direction
- Pullback count (1/2, 2/2, etc.)
- Candle type (BEARISH/BULLISH)
- OHLC values
- How many more pullbacks needed

---

### 4. **Non-Pullback Candle**
When a candle does NOT qualify as a pullback:

```
❌ NON-PULLBACK: EURUSD ARMED_LONG | Bullish GREEN candle | NOT BEARISH (Close 1.17055 >= Open 1.17050) | Count: 0/2
```

**Information shown:**
- Symbol and armed direction
- Candle type (Bullish/Bearish/Doji)
- Candle color (GREEN/RED/NEUTRAL)
- **Exact reason** why it's not a pullback
- Current pullback count

---

### 5. **Pullback Complete**
When all required pullbacks are counted:

```
>> PULLBACK CANDLE: EURUSD LONG #2/2 | BEARISH (Red) | O:1.17045 H:1.17050 L:1.17040 C:1.17042
✅ EURUSD: Pullback CONFIRMED (2/2) - Window OPENING
```

**Information shown:**
- Final pullback candle details
- Confirmation message
- State transition to WINDOW_OPEN

---

## Complete Example Flow

Here's what you'll see in the terminal for a complete ARMED → PULLBACK → WINDOW sequence:

```
[06:20:03] 🎯 EURUSD: LONG CROSSOVER - State: SCANNING → ARMED_LONG | Price: 1.17052
[06:20:03] 📋 EURUSD: NOW MONITORING for 2 BEARISH (Red) pullback candles...

[06:25:02] 🔍 CHECKING CANDLE: EURUSD ARMED_LONG | Time: 2025-10-17 06:25:00 | O:1.17055 H:1.17060 L:1.17050 C:1.17048 | Count: 0/2
[06:25:02] >> PULLBACK CANDLE: EURUSD LONG #1/2 | BEARISH (Red) | O:1.17055 H:1.17060 L:1.17050 C:1.17048
[06:25:02] 📉 EURUSD: Bearish pullback #1/2 detected (need 1 more)

[06:30:01] 🔍 CHECKING CANDLE: EURUSD ARMED_LONG | Time: 2025-10-17 06:30:00 | O:1.17050 H:1.17055 L:1.17045 C:1.17052 | Count: 1/2
[06:30:01] ❌ NON-PULLBACK: EURUSD ARMED_LONG | Bullish GREEN candle | NOT BEARISH (Close 1.17052 >= Open 1.17050) | Count: 1/2

[06:35:01] 🔍 CHECKING CANDLE: EURUSD ARMED_LONG | Time: 2025-10-17 06:35:00 | O:1.17050 H:1.17052 L:1.17040 C:1.17042 | Count: 1/2
[06:35:01] >> PULLBACK CANDLE: EURUSD LONG #2/2 | BEARISH (Red) | O:1.17050 H:1.17052 L:1.17040 C:1.17042
[06:35:01] ✅ EURUSD: Pullback CONFIRMED (2/2) - Window OPENING
```

---

## How to Export Terminal Log

### Method 1: Direct File Access
The terminal log is automatically saved to:
```
terminal_log_YYYYMMDD_HHMMSS.txt
```

Example: `terminal_log_20251017_062003.txt`

### Method 2: PowerShell Command
To find the most recent log file:
```powershell
Get-ChildItem -Path . -Filter "terminal_log_*.txt" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
```

To copy the log to your desktop:
```powershell
$latest = Get-ChildItem -Path . -Filter "terminal_log_*.txt" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Copy-Item $latest.FullName -Destination "$env:USERPROFILE\Desktop\pullback_analysis.txt"
```

### Method 3: Export Specific Symbol
To filter logs for a specific symbol (e.g., EURUSD):
```powershell
$latest = Get-ChildItem -Path . -Filter "terminal_log_*.txt" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Get-Content $latest.FullName | Select-String "EURUSD" | Out-File "$env:USERPROFILE\Desktop\eurusd_pullback_analysis.txt"
```

---

## Analysis Points to Watch

When analyzing the exported log, look for:

### ✅ **Successful Pullback Detection**
- `🔍 CHECKING CANDLE` appears for every new candle
- `>> PULLBACK CANDLE` appears when pullback is valid
- Count increments: 0/2 → 1/2 → 2/2
- `✅ Pullback CONFIRMED` appears when complete

### ❌ **Failed Pullback Detection (Old Bug)**
- No `🔍 CHECKING CANDLE` messages (code not running)
- No pullback messages despite red candles on chart
- Count stuck at 0/2 forever

### ⚠️ **Non-Pullback Candles**
- `❌ NON-PULLBACK` appears with reason
- Shows exact OHLC values
- Explains why candle doesn't qualify
- Count remains same (doesn't reset)

### 🚫 **Global Invalidation**
- `⚠️ GLOBAL INVALIDATION` message
- Bearish crossover detected while ARMED_LONG
- Or bullish crossover while ARMED_SHORT
- State resets to SCANNING

---

## Key Debugging Information

Each log entry includes:

1. **Timestamp:** Exact time the candle closed
2. **OHLC Values:** Open, High, Low, Close prices
3. **Candle Color:** RED (bearish) or GREEN (bullish)
4. **Close vs Open Comparison:** Shows the exact calculation
5. **Current Count:** Shows progress (0/2, 1/2, 2/2)
6. **Reason:** Explains why candle is/isn't a pullback

---

## Expected Behavior After Fix

With the double candle removal bug fixed (October 17, 2025), you should now see:

✅ `🔍 CHECKING CANDLE` for EVERY 5-minute candle close  
✅ Correct OHLC values matching MT5 platform  
✅ Pullbacks counted when red candles appear (for LONG)  
✅ Count increments properly: 0 → 1 → 2  
✅ Window opens after 2 pullback candles  

---

## Summary

All pullback-related activity is now logged with:
- ✅ Candle timestamps
- ✅ OHLC values
- ✅ Pullback count progress
- ✅ Exact reason for each decision
- ✅ All logged to file for export and analysis

You can now export the `terminal_log_*.txt` file and see EXACTLY what the bot is doing for every candle in ARMED state!

---

**Files Modified:**
- `advanced_mt5_monitor_gui.py` (lines 1420-1558)

**New Log Markers:**
- 🎯 Crossover detected
- 📋 Monitoring started
- 🔍 Checking candle
- >> Pullback candle found
- 📉 Pullback progress
- ❌ Non-pullback candle
- ✅ Pullback confirmed
