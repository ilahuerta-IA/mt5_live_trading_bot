# PULLBACK DETECTION FIX - TESTING GUIDE

## 🧪 How to Test the Fix

### Step 1: Restart the Monitor

1. **Stop** the current monitor (if running)
2. **Start** the monitor with the fixed code:
   ```powershell
   python advanced_mt5_monitor_gui.py
   ```

### Step 2: What to Watch For

#### ✅ **CORRECT BEHAVIOR** (After Fix):

```
[TIME] 🎯 USDCHF: LONG CROSSOVER - State: SCANNING → ARMED_LONG | Price: 0.80298
[TIME] ⏳ USDCHF: Waiting for candle close... Forming candle: ✓ Pullback-type | Pullback count: 0/2
[TIME] 📉 USDCHF: Bearish pullback #1/2 detected (need 1 more)
[TIME] ⏳ USDCHF: Waiting for candle close... Forming candle: ✓ Pullback-type | Pullback count: 1/2
[TIME] 📉 USDCHF: Bearish pullback #2/2 detected (need 0 more)
[TIME] ✅ USDCHF: Pullback CONFIRMED (2/2) - Window OPENING
[TIME] 🪟 USDCHF: Window OPENED - Monitoring breakout...
```

#### ❌ **OLD BEHAVIOR** (Bug - should NOT see this anymore):

```
[TIME] 🎯 USDCHF: LONG CROSSOVER - State: SCANNING → ARMED_LONG | Price: 0.80298
[TIME] ⚠️ USDCHF: Non-pullback candle! Expected: Bearish, Got: Bullish - Reset to SCANNING
```

---

## 🔍 Detailed Monitoring Checklist

### Phase 1: Crossover Detection ✅
- [ ] Crossovers are detected normally
- [ ] Strategy transitions to ARMED_LONG or ARMED_SHORT
- [ ] Log shows: "🎯 [SYMBOL]: LONG/SHORT CROSSOVER - State: SCANNING → ARMED_*"

### Phase 2: Pullback Detection (THE FIX) ✅
- [ ] After arming, monitor does NOT immediately reset
- [ ] Log shows: "⏳ [SYMBOL]: Waiting for candle close..." (periodically)
- [ ] First pullback detected on NEXT candle after arming (not arming candle)
- [ ] Log shows: "📉 [SYMBOL]: Bearish/Bullish pullback #1/X detected"
- [ ] Counter increments: #1/2, #2/2, etc.

### Phase 3: Window Opening ✅
- [ ] After required pullback count reached
- [ ] Log shows: "✅ [SYMBOL]: Pullback CONFIRMED (X/X) - Window OPENING"
- [ ] State transitions to WINDOW_OPEN
- [ ] Log shows: "🪟 [SYMBOL]: Window OPENED - Monitoring breakout..."

### Phase 4: Breakout Detection ✅
- [ ] Monitor tracks price vs. window boundaries
- [ ] Log shows periodic updates: "📊 [SYMBOL]: Monitoring window..."
- [ ] On success: "✅ [SYMBOL]: BREAKOUT detected - Entry conditions met!"
- [ ] On expiry: "⏱️ [SYMBOL]: Window EXPIRED - Returning to pullback search"
- [ ] On failure: "❌ [SYMBOL]: Failure boundary broken - Returning to pullback search"

---

## 📊 Expected Metrics

### Hourly Summary Should Show:

**BEFORE FIX** (Broken):
```
📊 HOURLY SUMMARY (XX:36)
   🔄 Crossovers: 10 | 🎯 Armed: 5 | 📉 Pullbacks: 0    ← ZERO!
   🪟 Windows: 0 | 🚀 Breakouts: 0 | ⚠️ Invalidations: 0 | 💰 Trades: 0
```

**AFTER FIX** (Working):
```
📊 HOURLY SUMMARY (XX:36)
   🔄 Crossovers: 10 | 🎯 Armed: 5 | 📉 Pullbacks: 3-5    ← NOW WORKING!
   🪟 Windows: 2-4 | 🚀 Breakouts: 1-2 | ⚠️ Invalidations: 1 | 💰 Trades: 0-1
```

---

## 🎯 Focus on USDCHF

Since the log showed issues with USDCHF specifically:

1. **Watch USDCHF closely** for the next crossover
2. **Verify no immediate reset** after arming
3. **Confirm pullback detection** on subsequent candles
4. **Check window opening** after pullback confirmation

---

## 🐛 Known Scenarios

### Scenario A: Clean Progression (Expected)
```
SCANNING → ARMED_LONG → Pullback #1 → Pullback #2 → WINDOW_OPEN → SUCCESS/EXPIRED
```

### Scenario B: Global Invalidation (Expected)
```
SCANNING → ARMED_LONG → [Bearish crossover detected] → SCANNING
Log: "⚠️ GLOBAL INVALIDATION - Bearish crossover detected in ARMED_LONG"
```

### Scenario C: Non-Pullback Interruption (Expected)
```
SCANNING → ARMED_LONG → Pullback #1 → [Bullish candle] → SCANNING
Log: "⚠️ Non-pullback candle! Expected: Bearish, Got: Bullish - Reset"
```

**Important**: Scenario C should only happen AFTER at least one valid pullback attempt, NOT immediately after arming!

---

## ⏱️ Time-Based Monitoring

### First 15 Minutes
- [ ] At least 1-2 crossovers should occur
- [ ] No immediate resets after arming
- [ ] "Waiting for candle close" messages appear

### First 30 Minutes
- [ ] At least 1 pullback confirmation should occur
- [ ] At least 1 window should open
- [ ] Hourly summary counters are non-zero

### First Hour
- [ ] Multiple complete state machine cycles
- [ ] Hourly summary shows healthy metrics
- [ ] Compare with backtrader results

---

## 🔧 If Issues Persist

### Debug Steps:

1. **Check arming candle timestamp**:
   - Look for: "last_pullback_check_candle" in state
   - Should match arming candle timestamp

2. **Verify candle progression**:
   - Each closed candle should have unique timestamp
   - Pullback checks should skip arming candle

3. **Enable verbose logging** (if needed):
   - Uncomment debug lines in code
   - Check `last_pullback_check_candle` vs `current_closed_candle_time`

4. **Compare with backtrader**:
   - Run same time period in backtrader
   - Verify pullback counts match

---

## 📝 Testing Report Template

After testing, document:

```markdown
## Testing Results - Pullback Detection Fix

**Date**: [Date]
**Time Range**: [Start] - [End]
**Duration**: [Duration]

### Metrics:
- Crossovers Detected: [Count]
- Armed States: [Count]
- Pullbacks Confirmed: [Count] ← KEY METRIC!
- Windows Opened: [Count]
- Breakouts: [Count]

### USDCHF Specific:
- USDCHF Crossovers: [Count]
- USDCHF Armed: [Count]
- USDCHF Pullbacks: [Count]
- USDCHF Windows: [Count]

### Issues Encountered:
- [ ] None - all working as expected ✅
- [ ] [Describe any issues]

### Sample Log Excerpt:
[Paste relevant log lines showing pullback progression]

### Conclusion:
[Pass/Fail] - [Brief summary]
```

---

## ✅ Success Criteria

The fix is **SUCCESSFUL** if:

1. ✅ No immediate resets after arming (most critical!)
2. ✅ Pullback count progresses: 0 → 1 → 2 → ...
3. ✅ Windows open after pullback confirmation
4. ✅ Hourly summary shows non-zero pullback counts
5. ✅ State machine completes full cycles
6. ✅ Behavior matches backtrader strategy

---

**Happy Testing!** 🚀

Remember: The key indicator of success is seeing **"📉 Pullback #1/2 detected"** messages, NOT immediate resets after arming.
