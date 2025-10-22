# TIME FILTER AND CHART NAVIGATION IMPROVEMENTS

## Date
October 15, 2025

## Overview
This document details critical fixes to time filter logic alignment with Backtrader design principles and major enhancements to chart navigation capabilities.

---

## PART 1: TIME FILTER FIX - BACKTRADER DESIGN COMPLIANCE

### Problem Identified
Time filter was being checked at the **beginning** of pullback entry logic (line 1631), which blocked state progression during signal detection and pullback phases. This violated Backtrader's design philosophy.

### Backtrader Design Principle
**"Setup detection can occur 24/7, but entry execution respects time windows"**

The strategy should:
1. ✅ Detect signals anytime (PHASE 1: SCANNING → ARMED)
2. ✅ Count pullbacks anytime (PHASE 2: ARMED → PULLBACK → WINDOW)
3. ✅ Monitor breakout windows anytime (PHASE 3: WINDOW monitoring)
4. ⏰ **ONLY check time filter at entry execution** (PHASE 4: ENTRY)

### Changes Made

#### Before (WRONG):
```python
def _handle_long_pullback_entry(self, dt):
    """LONG pullback entry state machine logic"""
    # ❌ WRONG: Time filter at start blocks all state progression
    if not self._is_in_trading_time_range(dt):
        print(f"Time Filter: LONG entry rejected...")
        return False
    # ... rest of logic
```

#### After (CORRECT):
```python
def _handle_long_pullback_entry(self, dt):
    """LONG pullback entry state machine logic
    
    NOTE: Time filter is checked ONLY at entry execution (Phase 3), not during 
    signal detection or pullback phases. This matches Backtrader design where
    setup detection can occur 24/7 but entry execution respects time windows.
    """
    # ... signal detection, pullback counting (NO time filter)
    
    # PHASE 3: Entry execution
    if current_high >= self.breakout_target:
        # ✅ CORRECT: Time filter ONLY at entry execution
        if not self._is_in_trading_time_range(dt):
            if self.p.verbose_debug:
                print(f"ENTRY BLOCKED: LONG breakout outside trading hours")
            # Don't reset state - keep waiting for valid time window
            return False
        # ... execute entry
```

### Impact
| Aspect | Before | After |
|--------|--------|-------|
| Signal Detection | ❌ Blocked outside hours | ✅ Works 24/7 |
| Pullback Counting | ❌ Stopped outside hours | ✅ Continuous |
| Window Monitoring | ❌ Blocked outside hours | ✅ Active 24/7 |
| Entry Execution | ✅ Time-filtered | ✅ Time-filtered |

### Configuration
```python
USE_TIME_RANGE_FILTER = False  # Set True to enable
ENTRY_START_HOUR = 7           # UTC start hour
ENTRY_END_HOUR = 18            # UTC end hour
```

When `USE_TIME_RANGE_FILTER = False`:
- All phases work without time restriction
- Entries can execute anytime

When `USE_TIME_RANGE_FILTER = True`:
- Phases 1-3 work 24/7 (setup detection)
- Phase 4 only executes during specified hours

---

## PART 2: CHART NAVIGATION - PLOTLY-STYLE INTERACTIVITY

### Overview
Upgraded chart navigation from basic zoom/pan to professional-grade Plotly-style controls with multiple interaction modes.

### New Features

#### 1. **Mouse Wheel Zoom** (Default)
- **Action**: Scroll wheel
- **Behavior**: Zoom in/out centered on cursor position
- **Use Case**: Quick zoom to specific price/time region

#### 2. **Horizontal Scroll** (Shift + Wheel)
- **Action**: Hold SHIFT + Scroll wheel
- **Behavior**: Pan left/right along time axis
- **Use Case**: Navigate through historical data quickly

#### 3. **Vertical Zoom Only** (Ctrl + Wheel)
- **Action**: Hold CTRL + Scroll wheel
- **Behavior**: Zoom price axis only (time axis stays fixed)
- **Use Case**: Examine price movements in detail

#### 4. **Pan in Any Direction** (Right-Click Drag)
- **Action**: Right-click and drag
- **Behavior**: Move chart in any direction
- **Cursor**: Changes to "fleur" (4-way arrow)
- **Use Case**: Reposition view after zooming

#### 5. **Box Zoom** (Middle-Click Drag)
- **Action**: Middle-click and drag
- **Behavior**: Draw selection box, zoom to that region
- **Visual**: Blue transparent overlay
- **Use Case**: Precise zoom to specific time/price rectangle

#### 6. **Reset View** (Double-Click)
- **Action**: Double-click anywhere on chart
- **Behavior**: Auto-scale to show all data
- **Use Case**: Return to full view after zooming

### Technical Implementation

```python
def setup_chart_navigation(self):
    """Setup interactive zoom and pan - Plotly-style behavior"""
    
    # State tracking
    self.original_xlim = None      # Store original view for reset
    self.original_ylim = None
    self.zoom_box_start = None     # Box zoom start point
    self.zoom_box_rect = None      # Box zoom visual rectangle
    self.pan_start = None          # Pan operation start point
    self.pan_active = False        # Pan state flag
    
    # Event handlers:
    # - on_scroll: Handle wheel events with modifiers
    # - on_press: Detect click type and start interaction
    # - on_release: Complete zoom/pan operations
    # - on_motion: Update during drag operations
```

### Modifier Key Summary

| Keys | Mouse Action | Result |
|------|--------------|--------|
| None | Wheel | Zoom both axes |
| SHIFT | Wheel | Horizontal scroll |
| CTRL | Wheel | Vertical zoom only |
| None | Right drag | Pan any direction |
| None | Middle drag | Box zoom |
| None | Double-click | Reset to auto-scale |

### Performance Optimizations

1. **draw_idle() instead of draw()**
   - Defers redraw until event loop is idle
   - Prevents excessive redraws during drag operations
   - Smoother interaction

2. **Zoom Factor: 1.15**
   - Gentler zoom than default 1.2
   - More control for precision work
   - Matches Plotly behavior

3. **Cursor Feedback**
   - Pan: Shows "fleur" cursor (4-way arrows)
   - Box zoom: Visual blue overlay
   - Normal: Default cursor

### Code Comparison

#### Before (Basic):
```python
# Only right-click pan and wheel zoom
# No modifiers, no box zoom, no reset
```

#### After (Advanced):
```python
# Full Plotly-style controls:
# - Modifier key support (Shift, Ctrl)
# - Box zoom with visual feedback
# - Double-click reset
# - Cursor state indicators
# - Optimized redraw with draw_idle()
```

---

## Files Modified

### 1. strategies/sunrise_ogle_gbpusd.py
**Lines changed**: 1628-1633, 1745-1753

**Changes**:
- Removed time filter check from start of `_handle_long_pullback_entry()`
- Added time filter check at entry execution point (PHASE 3)
- Added docstring explaining Backtrader design compliance
- Preserved state when entry blocked by time (allows retry)

### 2. advanced_mt5_monitor_gui.py
**Lines changed**: 405-580

**Changes**:
- Complete rewrite of `setup_chart_navigation()`
- Added modifier key detection (Shift, Ctrl)
- Implemented box zoom with visual feedback
- Added double-click reset functionality
- Improved pan with cursor feedback
- Optimized with `draw_idle()`

---

## Testing Checklist

### Time Filter Testing
- [ ] Verify ARMED signal can be set outside trading hours
- [ ] Confirm pullback counting works outside trading hours
- [ ] Check window monitoring continues outside hours
- [ ] Validate entry execution blocked outside hours (when filter enabled)
- [ ] Test entry execution proceeds inside hours

### Chart Navigation Testing
- [ ] Mouse wheel: Zoom in/out at cursor
- [ ] Shift+Wheel: Horizontal scroll
- [ ] Ctrl+Wheel: Vertical zoom only
- [ ] Right-click drag: Pan
- [ ] Middle-click drag: Box zoom
- [ ] Double-click: Reset view
- [ ] Cursor changes during pan
- [ ] Blue box shows during box zoom

---

## User Benefits

### Time Filter
1. ✅ **Natural Workflow**: See setups form even outside trading hours
2. ✅ **No Lost Opportunities**: State preserved until valid entry time
3. ✅ **Backtrader Compliant**: Matches original strategy design philosophy
4. ✅ **Flexible**: Can disable time filter entirely if needed

### Chart Navigation
1. ✅ **Professional Tools**: Same controls as Plotly/TradingView
2. ✅ **Multiple Modes**: Different tools for different analysis needs
3. ✅ **Intuitive**: Modifier keys follow industry standards
4. ✅ **Smooth**: Optimized performance with draw_idle()
5. ✅ **Visual Feedback**: Clear indication of active operations

---

## Configuration Examples

### Example 1: 24/7 Trading (Crypto)
```python
USE_TIME_RANGE_FILTER = False  # No time restrictions
```

### Example 2: Forex London Session
```python
USE_TIME_RANGE_FILTER = True
ENTRY_START_HOUR = 7    # 7:00 UTC (London open)
ENTRY_END_HOUR = 16     # 16:00 UTC (London close)
```

### Example 3: US Stock Market
```python
USE_TIME_RANGE_FILTER = True
ENTRY_START_HOUR = 14   # 14:00 UTC (9:30 AM ET)
ENTRY_END_HOUR = 21     # 21:00 UTC (4:00 PM ET)
```

---

## Notes

1. **Type Errors**: Pylance shows type warnings for set_xlim/set_ylim - these are false positives. Matplotlib accepts both lists and tuples.

2. **State Preservation**: When entry is blocked by time filter, the state machine preserves WAITING_BREAKOUT state, allowing automatic entry when trading hours begin.

3. **Chart Refresh**: Navigation works independently of chart data refresh. Zoom/pan state is maintained across data updates.

4. **Performance**: All draw operations use `draw_idle()` for optimal performance during interactive operations.
