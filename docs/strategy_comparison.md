# Strategy Configuration Comparison

This document serves as the "Source of Truth" for the configuration parameters of the Sunrise Ogle strategy across all traded assets.

## 📊 Core Asset Parameter Comparison

| Parameter | AUDUSD | EURUSD | GBPUSD | USDCHF | XAGUSD | XAUUSD | EURJPY | USDJPY |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Direction** | LONG ONLY | LONG ONLY | LONG ONLY | LONG ONLY | LONG ONLY | LONG ONLY | LONG ONLY | LONG+SHORT |
| **Long Pullback Candles** | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 2 |
| **Long Window Periods** | 1 | 1 | 1 | 2 | 3 | 1 | 3 | 7 |
| **Short Pullback Candles** | 2 | N/A | N/A | 2 | 2 | 2 | N/A | 2 |
| **Short Window Periods** | 7 | N/A | N/A | 7 | 7 | 7 | N/A | 7 |
| **Window Offset Mult** | 0.5 | 1.0 | 1.0 | 1.0 | 0.5 | 1.0 | 2.0 | 2.0 |
| **Window Price Offset** | 0.001 | 0.01 | 1.0 | 0.01 | 0.001 | 0.001 | 0.01 | 0.01 |
| **Long ATR SL Mult** | 4.4 | 1.5 | 3.5 | 2.5 | 4.5 | 4.5 | 3.0 | 3.5 |
| **Long ATR TP Mult** | 6.8 | 10.0 | 6.5 | 10.0 | 6.5 | 6.5 | 6.5 | 6.5 |
| **Short ATR SL Mult** | 2.5 | N/A | N/A | 2.5 | 2.5 | 2.5 | N/A | 2.5 |
| **Short ATR TP Mult** | 6.5 | N/A | N/A | 6.5 | 6.5 | 6.5 | N/A | 6.5 |

## 📈 EMA Configuration

| Parameter | AUDUSD | EURUSD | GBPUSD | USDCHF | XAGUSD | XAUUSD | EURJPY | USDJPY |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **EMA Fast Length** | 18 | 18 | 18 | 18 | 14 | 14 | 18 | 14 |
| **EMA Medium Length** | 18 | 18 | 18 | 18 | 18 | 14 | 18 | 14 |
| **EMA Slow Length** | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 |
| **EMA Confirm Length** | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| **EMA Filter Price Length** | 40 | 70 | 70 | 50 | 50 | 100 | 70 | 70 |

## 📐 Angle Filter Configuration

| Parameter | AUDUSD | EURUSD | GBPUSD | USDCHF | XAGUSD | XAUUSD | EURJPY | USDJPY |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Long Angle Filter** | ✅ On | ❌ Off | ✅ On | ❌ Off | ✅ On | ❌ Off | ✅ On | ✅ On |
| **Long Min Angle** | 0° | 35° | 45° | 40° | 0° | 35° | 60° | 30° |
| **Long Max Angle** | 30° | 85° | 95° | 80° | 50° | 95° | 88° | 95° |
| **Long Scale Factor** | 10 | 10000 | 10000 | 10000 | 10 | 10 | 100 | 100 |
| **Short Angle Filter** | ✅ On | N/A | N/A | ✅ On | ✅ On | ✅ On | N/A | ✅ On |
| **Short Min Angle** | -90° | N/A | N/A | -90° | -90° | -80° | N/A | -90° |
| **Short Max Angle** | -20° | N/A | N/A | -20° | -50° | -30° | N/A | -20° |
| **Short Scale Factor** | 10 | N/A | N/A | 10000 | 10 | 10 | N/A | 100 |

> **Scale Factor Notes:**
> - **10** = Metals (XAGUSD, XAUUSD) and AUDUSD
> - **100** = JPY pairs (EURJPY, USDJPY)
> - **10000** = Standard forex (EURUSD, GBPUSD, USDCHF)

## 📊 ATR Volatility Filter Configuration

| Parameter | AUDUSD | EURUSD | GBPUSD | USDCHF | XAGUSD | XAUUSD | EURJPY | USDJPY |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **ATR Length** | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 |
| **Long ATR Filter** | ❌ Off | ❌ Off | ❌ Off | ❌ Off | ✅ On | ✅ On | ❌ Off | ❌ Off |
| **Long ATR Increment Filter** | ❌ Off | ❌ Off | ❌ Off | ❌ Off | ✅ On | ✅ On | ✅ On | ❌ Off |
| **Long ATR Decrement Filter** | ❌ Off | ❌ Off | ❌ Off | ❌ Off | ✅ On | ❌ Off | ✅ On | ❌ Off |

## 🔧 Entry Filter Configuration

| Parameter | AUDUSD | EURUSD | GBPUSD | USDCHF | XAGUSD | XAUUSD | EURJPY | USDJPY |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Price Filter EMA** | ✅ On | ✅ On | ✅ On | ✅ On | ✅ On | ✅ On | ✅ On | ✅ On |
| **Candle Direction Filter** | ❌ Off | ❌ Off | ❌ Off | ❌ Off | ❌ Off | ❌ Off | ❌ Off | ❌ Off |
| **EMA Order Condition** | ❌ Off | ❌ Off | ❌ Off | ❌ Off | ❌ Off | ❌ Off | ❌ Off | ❌ Off |
| **EMA Below Price Filter** | ❌ Off | ❌ Off | ❌ Off | ❌ Off | ❌ Off | ❌ Off | ❌ Off | ❌ Off |

## ⏰ Time Range Filter Configuration

| Parameter | AUDUSD | EURUSD | GBPUSD | USDCHF | XAGUSD | XAUUSD | EURJPY | USDJPY |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Time Filter Enabled** | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Start Hour (UTC)** | 23:00 | 21:00 | (7:00) | 07:00 | 00:00 | (0:00) | (7:00) | (0:00) |
| **End Hour (UTC)** | 16:00 | 03:00 | (18:00) | 13:00 | 15:00 | (8:00) | (16:00) | (23:59) |

## 🔄 Window Time Offset Configuration

| Asset | USE_WINDOW_TIME_OFFSET |
| :--- | :---: |
| AUDUSD | `False` |
| EURUSD | `False` |
| GBPUSD | `False` |
| USDCHF | `False` |
| XAGUSD | **`True`** |
| XAUUSD | `False` |
| EURJPY | `False` |
| USDJPY | **`True`** ⬅️ Both XAGUSD + USDJPY use time offset! |

## 🧠 Critical Strategy Concepts

### 1. Pullback Candle vs. Window Candle
It is crucial to distinguish between the candle that *creates* the setup and the candle that *triggers* the entry.

*   **Pullback Candle (The Setup)**:
    *   This is the last candle of the pullback sequence (e.g., the 2nd red candle if `LONG_PULLBACK_MAX_CANDLES = 2`).
    *   **Role**: It defines the **Reference High/Low** for the breakout window.
    *   **Limits**: The Success/Failure limits are calculated based on *this* candle's High/Low (plus/minus the offset).
    *   **Behavior**: This candle *cannot* trigger an entry or a failure because the window doesn't exist yet; it is being created *at the close* of this candle.

*   **Window Candle (The Trigger)**:
    *   This is any candle that opens *after* the Pullback Candle (within the `WINDOW_PERIODS` duration).
    *   **Role**: It tests the limits set by the Pullback Candle.
    *   **Success**: If it breaks the **Top Limit** (for Longs), it triggers an **ENTRY**.
    *   **Failure**: If it breaks the **Bottom Limit** (for Longs), it triggers a **RESET**.

### 2. Phase 4: Window Monitor Logic (Success Priority)
In all strategy files, the `_phase4_monitor_window` method implements a specific priority when checking for breakouts:

1.  **Success Check First**: The code checks if the price has hit the **Entry Target** (Top Limit for Longs).
2.  **Failure Check Second**: Only if the Success condition is NOT met, it checks if the price has hit the **Failure Limit** (Bottom Limit for Longs).

**Implication**: If a single candle ("Outside Bar") breaks **BOTH** the Top and Bottom limits:
- The strategy will trigger a **SUCCESS** (Entry).
- The Failure condition is ignored for that bar.
- This is intended behavior to capture high-volatility breakout moves.

### 3. Window Failure & Reset Logic
When a candle breaks the Failure Limit (without breaking the Entry Target):
1.  **Immediate Reset**: The `entry_state` is reset to `ARMED`.
2.  **Counter Reset**: `pullback_candle_count` is reset to 0.
3.  **Candle Consumption**: The candle that caused the failure is "consumed" by the failure event. It is **NOT** counted as the first candle of a new pullback sequence.
4.  **Next Step**: The strategy waits for the **NEXT** candle to begin searching for a new pullback pattern.

## 📂 Source Files
- `mt5_live_trading_bot/strategies/sunrise_ogle_audusd.py`
- `mt5_live_trading_bot/strategies/sunrise_ogle_eurusd.py`
- `mt5_live_trading_bot/strategies/sunrise_ogle_gbpusd.py`
- `mt5_live_trading_bot/strategies/sunrise_ogle_usdchf.py`
- `mt5_live_trading_bot/strategies/sunrise_ogle_xagusd.py`
- `mt5_live_trading_bot/strategies/sunrise_ogle_xauusd.py`
- `mt5_live_trading_bot/strategies/sunrise_ogle_eurjpy.py`
- `mt5_live_trading_bot/strategies/sunrise_ogle_usdjpy.py`
