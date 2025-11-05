# 🎯 MT5 Live Trading Bot - Filter Configuration Matrix

**Last Updated:** November 3, 2025  
**Bot Version:** Advanced MT5 Monitor GUI  
**Assets Monitored:** 6 (EURUSD, GBPUSD, XAUUSD, AUDUSD, XAGUSD, USDCHF)

---

## 📊 Quick Reference - Filter Status by Asset

| Filter Type | EURUSD | GBPUSD | XAUUSD | AUDUSD | XAGUSD | USDCHF |
|-------------|:------:|:------:|:------:|:------:|:------:|:------:|
| **ATR Filter** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Angle Filter** | ❌ | ✅ | ❌ | ✅ | ✅ | ❌ |
| **Price Filter EMA** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Candle Direction** | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| **EMA Ordering** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Time Range** | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Pullback Entry** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**Legend:**  
✅ = Enabled & Active  
❌ = Disabled / Not Used

---

## 🔧 ATR VOLATILITY FILTER - Detailed Configuration

All assets use ATR filtering to ensure optimal volatility conditions for entries.

### ATR Range Thresholds

| Asset | Min ATR | Max ATR | ATR Increment | Incr Min | Incr Max |
|-------|---------|---------|:-------------:|----------|----------|
| **EURUSD** | 0.000150 | 0.000600 | ✅ | 0.000050 | 0.000080 |
| **GBPUSD** | 0.000300 | 0.000700 | ❌ | - | - |
| **XAUUSD** | 0.000000 | 2.000000 | ✅ | 0.200000 | 1.600000 |
| **AUDUSD** | 0.000150 | 0.000500 | ❌ | - | - |
| **XAGUSD** | 0.010000 | 0.045000 | ❌ | - | - |
| **USDCHF** | 0.000300 | 0.000700 | ❌ | - | - |

**Notes:**
- **Forex pairs** (EURUSD, GBPUSD, AUDUSD, USDCHF): ATR in pip ranges (0.0001-0.0007)
- **Metals** (XAUUSD, XAGUSD): ATR in dollar/ounce ranges (0.01-2.00)
- **ATR Increment Filter**: Only enabled for EURUSD & XAUUSD
- **ATR Decrement Filter**: Disabled for all assets (optimal performance)

---

## 📐 ANGLE FILTER - EMA Slope Validation

Filters entries based on EMA slope angle to ensure trend strength.

| Asset | Enabled | Min Angle | Max Angle | Scale Factor | Notes |
|-------|:-------:|-----------|-----------|--------------|-------|
| **EURUSD** | ❌ | 35° | 85° | 10000.0 | Disabled - ranging market strategy |
| **GBPUSD** | ✅ | 45° | 95° | 10000.0 | Strong trend required |
| **XAUUSD** | ❌ | 35° | 95° | 10.0 | Disabled - momentum-based entries |
| **AUDUSD** | ✅ | 0° | 30° | 10.0 | Gentle trends only |
| **XAGUSD** | ✅ | 0° | 50° | 10.0 | Moderate trends |
| **USDCHF** | ❌ | 40° | 80° | 10000.0 | Disabled - price action priority |

**Scale Factor Rules:**
- **Forex (4-5 decimals)**: 10000.0 scale factor
- **Metals (2 decimals)**: 10.0 scale factor

**Calculation Formula:**
```python
angle = atan((current_ema - previous_ema) * scale_factor) * 180 / π
```

---

## 💰 PRICE FILTER EMA - Trend Alignment

All assets require price to be on correct side of Filter EMA (default: 70-period).

| Asset | Enabled | Filter EMA Period | Entry Logic |
|-------|:-------:|:-----------------:|-------------|
| **EURUSD** | ✅ | 70 | LONG: close > filter_EMA |
| **GBPUSD** | ✅ | 70 | LONG: close > filter_EMA |
| **XAUUSD** | ✅ | 70 | LONG: close > filter_EMA |
| **AUDUSD** | ✅ | 70 | LONG: close > filter_EMA |
| **XAGUSD** | ✅ | 70 | LONG: close > filter_EMA |
| **USDCHF** | ✅ | 70 | LONG: close > filter_EMA |

**Purpose:** Ensures entries align with broader trend, avoiding counter-trend trades.

---

## 🕯️ CANDLE DIRECTION FILTER

Requires previous candle to match direction (bullish for LONG, bearish for SHORT).

| Asset | Enabled | Logic |
|-------|:-------:|-------|
| **EURUSD** | ❌ | Not required |
| **GBPUSD** | ❌ | Not required |
| **XAUUSD** | ❌ | Not required |
| **AUDUSD** | ✅ | LONG: Previous candle bullish (close[1] > open[1]) |
| **XAGUSD** | ✅ | LONG: Previous candle bullish (close[1] > open[1]) |
| **USDCHF** | ❌ | Not required |

**Note:** Only enabled for AUDUSD & XAGUSD for additional momentum confirmation.

---

## ⏰ TIME RANGE FILTER - Trading Hours

Restricts entries to specific UTC hours for optimal market conditions.

| Asset | Enabled | Start Hour (UTC) | End Hour (UTC) | Trading Window |
|-------|:-------:|:----------------:|:--------------:|----------------|
| **EURUSD** | ❌ | - | - | 24/7 Trading |
| **GBPUSD** | ❌ | - | - | 24/7 Trading |
| **XAUUSD** | ❌ | - | - | 24/7 Trading |
| **AUDUSD** | ✅ | 23:00 | 16:00 | Asian/London/NY Sessions |
| **XAGUSD** | ✅ | 00:00 | 15:00 | London/NY Sessions |
| **USDCHF** | ✅ | 07:00 | 13:00 | London Morning |

**Notes:**
- AUDUSD window: 23:00-16:00 UTC (17 hours, overnight window)
- XAGUSD window: 00:00-15:00 UTC (15 hours)
- USDCHF window: 07:00-13:00 UTC (6 hours, London session)

---

## 🎯 PULLBACK ENTRY SYSTEM - 3-Phase Entry Logic

All assets use the pullback entry system for precise timing.

| Asset | Enabled | Max Pullback Candles | Window Periods | Time Offset | Price Offset |
|-------|:-------:|:--------------------:|:--------------:|:-----------:|:------------:|
| **EURUSD** | ✅ | 2 | 1 | ❌ | 0.001 |
| **GBPUSD** | ✅ | 2 | 1 | ❌ | 0.001 |
| **XAUUSD** | ✅ | 3 | 1 | ❌ | 0.001 |
| **AUDUSD** | ✅ | 2 | 1 | ❌ | 0.001 |
| **XAGUSD** | ✅ | 2 | 3 | ✅ | 0.001 |
| **USDCHF** | ✅ | 2 | 2 | ❌ | 0.001 |

**Pullback Entry Phases:**
1. **Phase 1 - Crossover Detection:** Confirm EMA crosses above Slow EMA
2. **Phase 2 - Pullback Observation:** Wait for 1-3 red candles (pullback)
3. **Phase 3 - Volatility Expansion Channel:** Entry when price breaks channel high

**Window Parameters:**
- **Max Pullback Candles:** Maximum red candles allowed before rejecting signal
- **Window Periods:** Bars to wait for breakout after pullback completes
- **Time Offset:** Delay window opening (only XAGUSD uses this)
- **Price Offset:** Channel expansion multiplier (0.001 = 0.1% of candle range)

**Channel Calculation:**
```python
channel_high = pullback_high + (candle_range * 0.001)
channel_low = pullback_low - (candle_range * 0.001)
# Entry on breakout above channel_high
```

---

## 🔍 EMA ORDERING FILTER

Currently **DISABLED** for all assets to allow more entry opportunities.

| Asset | Enabled | Logic |
|-------|:-------:|-------|
| **All Assets** | ❌ | LONG: confirm_EMA > fast_EMA > medium_EMA > slow_EMA |

**Reason for Disabling:** Testing showed better performance without strict EMA ordering requirement.

---

## 🚨 CRITICAL FIXES APPLIED (Nov 3, 2025)

### Issue 1: EURUSD - Pullback Entry System
- **Before:** `LONG_USE_PULLBACK_ENTRY = False`
- **After:** `LONG_USE_PULLBACK_ENTRY = True` ✅
- **Impact:** Now uses proper 3-phase entry logic

### Issue 2: EURUSD - Window Price Offset
- **Before:** `WINDOW_PRICE_OFFSET_MULTIPLIER = 0.01`
- **After:** `WINDOW_PRICE_OFFSET_MULTIPLIER = 0.001` ✅
- **Impact:** Reduced channel expansion by 10x for tighter entries

### Issue 3: GBPUSD - ATR Filter
- **Before:** `LONG_USE_ATR_FILTER = False`
- **After:** `LONG_USE_ATR_FILTER = True` ✅
- **Impact:** Now filters trades by volatility (0.0003-0.0007 ATR)

### Issue 4: GBPUSD - Window Price Offset
- **Before:** `WINDOW_PRICE_OFFSET_MULTIPLIER = 1.0`
- **After:** `WINDOW_PRICE_OFFSET_MULTIPLIER = 0.001` ✅
- **Impact:** Reduced channel expansion by 1000x (critical fix!)

### Issue 5: USDCHF - Window Price Offset
- **Before:** `WINDOW_PRICE_OFFSET_MULTIPLIER = 0.01`
- **After:** `WINDOW_PRICE_OFFSET_MULTIPLIER = 0.001` ✅
- **Impact:** Reduced channel expansion by 10x for tighter entries

---

## 📈 Filter Validation Logic

All filters are checked **independently** for every crossover:

```python
if bullish_crossover and not crossover_is_stale:
    all_filters_passed = True
    
    # 1. ATR Filter
    atr_passed = validate_atr_filter(symbol, df, 'LONG')
    if not atr_passed:
        all_filters_passed = False
    
    # 2. Angle Filter (if enabled)
    angle_passed = validate_angle_filter(symbol, df, 'LONG')
    if not angle_passed:
        all_filters_passed = False
    
    # 3. Price Filter EMA
    price_passed = validate_price_filter(symbol, df, 'LONG')
    if not price_passed:
        all_filters_passed = False
    
    # 4. Candle Direction (if enabled)
    candle_passed = validate_candle_direction(symbol, df, 'LONG')
    if not candle_passed:
        all_filters_passed = False
    
    # 5. EMA Ordering (if enabled)
    ema_passed = validate_ema_ordering(symbol, df, 'LONG')
    if not ema_passed:
        all_filters_passed = False
    
    # 6. Time Range (if enabled)
    time_passed = validate_time_filter(symbol, 'LONG')
    if not time_passed:
        all_filters_passed = False
    
    # ARM signal only if ALL filters pass
    if all_filters_passed:
        arm_signal(symbol, 'LONG')
    else:
        reject_signal(symbol, 'LONG')
```

**Log Output Format:**
```
🔍 EURUSD: Bullish crossover detected - validating ALL filters...
   📊 EURUSD: ATR filter → ✅ PASS (ATR: 0.000423, range: [0.00015, 0.0006])
   📐 EURUSD: Angle filter → ✅ PASS (DISABLED)
   💰 EURUSD: Price filter → ✅ PASS (Close: 1.0845 > Filter EMA: 1.0832)
   🕯️ EURUSD: Candle Direction → ✅ PASS (DISABLED)
   📈 EURUSD: EMA Ordering → ✅ PASS (DISABLED)
   ⏰ EURUSD: Time filter → ✅ PASS (DISABLED - 24/7 trading)
✅ EURUSD: LONG crossover PASSED ALL FILTERS - Ready to ARM
```

---

## 🎓 Asset Strategy Profiles

### EURUSD - Ranging Market Specialist
- **Style:** ATR-based volatility entries with pullback confirmation
- **Key Filters:** ATR (0.00015-0.0006) + ATR Increment (0.00005-0.00008) + Price EMA
- **Notes:** No angle filter (allows ranging moves), 24/7 trading

### GBPUSD - Strong Trend Rider
- **Style:** High-angle trend following with ATR filtering
- **Key Filters:** Angle (45-95°) + ATR (0.0003-0.0007) + Price EMA
- **Notes:** Requires strong EMA slope, 24/7 trading

### XAUUSD - Momentum Trader
- **Style:** Gold volatility expansion with ATR increment filtering
- **Key Filters:** ATR (0-2.0) + ATR Increment (0.2-1.6) + Price EMA
- **Notes:** No angle filter (price action priority), 3-candle pullback max, 24/7 trading

### AUDUSD - Gentle Trend Follower
- **Style:** Low-angle trends with strict filtering
- **Key Filters:** Angle (0-30°) + ATR (0.00015-0.0005) + Price EMA + Candle Direction + Time (23:00-16:00 UTC)
- **Notes:** Most restrictive filters, Asian/London/NY sessions only

### XAGUSD - Moderate Trend + Momentum
- **Style:** Silver moderate trends with timing
- **Key Filters:** Angle (0-50°) + ATR (0.01-0.045) + Price EMA + Candle Direction + Time (00:00-15:00 UTC)
- **Notes:** Uses window time offset, 3-period window, London/NY sessions

### USDCHF - London Session Specialist
- **Style:** Price action with time restriction
- **Key Filters:** ATR (0.0003-0.0007) + Price EMA + Time (07:00-13:00 UTC)
- **Notes:** No angle/candle filters, London morning only (6 hours)

---

## 🔄 Filter Update History

| Date | Asset | Change | Reason |
|------|-------|--------|--------|
| 2025-11-03 | EURUSD | Enabled Pullback Entry | Critical missing entry logic |
| 2025-11-03 | EURUSD | Fixed Window Offset (0.01→0.001) | Entries too far from ideal price |
| 2025-11-03 | GBPUSD | Enabled ATR Filter | Missing volatility control |
| 2025-11-03 | GBPUSD | Fixed Window Offset (1.0→0.001) | CRITICAL: 1000x too large! |
| 2025-11-03 | USDCHF | Fixed Window Offset (0.01→0.001) | Entries too far from ideal price |

---

## 📚 Related Documentation

- **Strategy Files:** `strategies/sunrise_ogle_{symbol}.py`
- **Bot Main File:** `advanced_mt5_monitor_gui.py`
- **Filter Validation:** Lines 950-1252 (advanced_mt5_monitor_gui.py)
- **Configuration Parser:** Lines 438-637 (advanced_mt5_monitor_gui.py)

---

## ⚙️ Configuration Audit Script

Run the audit script to verify current configuration:

```bash
python audit_all_filters.py
```

This script checks:
- All filter enable/disable flags
- All threshold values
- Configuration consistency across assets
- Critical issues detection

---

**Last Audit:** November 3, 2025 18:45 UTC  
**Status:** ✅ All configurations verified, 0 critical issues  
**Bot Status:** Running with fixed validation logic (all filters checked independently)
