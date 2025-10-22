# MT5 EMA SETUP - QUICK START GUIDE

## 🚀 **5-MINUTE SETUP**

### **For EURUSD (and all pairs)**

1. **Right-click on chart** → Insert → Indicators → Trend → **Moving Average**

2. **Add 5 EMAs** with these settings:

---

### **EMA #1: Confirm**
```
Period: 1
Method: Exponential
Apply to: Close
Shift: 0
Color: Cyan
```

### **EMA #2: Fast**
```
Period: 18
Method: Exponential
Apply to: Close
Shift: 0
Color: Orange
```

### **EMA #3: Medium**
```
Period: 18
Method: Exponential
Apply to: Close
Shift: 0
Color: Green
```

### **EMA #4: Slow**
```
Period: 24
Method: Exponential
Apply to: Close
Shift: 0
Color: Dark Green
```

### **EMA #5: Filter**
```
Period: 70
Method: Exponential
Apply to: Close
Shift: 0
Color: Purple
```

---

## ⚡ **KEY POINT**

**CRITICAL**: Select **"Exponential"** from the "Method" dropdown!

```
[Method dropdown]
  ├── Simple          ❌ NO
  ├── Exponential     ✅ YES - SELECT THIS!
  ├── Smoothed        ❌ NO
  └── Linear Weighted ❌ NO
```

---

## 💾 **SAVE AS TEMPLATE**

After setup:
1. Right-click chart → **Template** → **Save Template**
2. Name: `Sunrise_Strategy`
3. Apply to other charts: **Template** → **Load Template** → `Sunrise_Strategy`

---

## ✅ **VERIFICATION**

Your EMAs should match bot values within ±0.00005

**Example check**:
- Bot shows: Fast EMA = 1.15586
- MT5 shows: Fast EMA = 1.15586
- ✅ **Perfect match!**

---

## 🎯 **WHY THIS WORKS**

Backtrader's `bt.ind.EMA(period=X)` uses:
```
α = 2 / (period + 1)
EMA = (Close × α) + (Previous_EMA × (1 - α))
```

MT5's "Exponential" method uses **THE SAME FORMULA**!

**Result**: Perfect alignment between bot and MT5 ✅

---

**Quick Setup Time**: 2-3 minutes per chart  
**Templates**: Save once, apply everywhere  
**Compatibility**: 100% with backtrader strategies
