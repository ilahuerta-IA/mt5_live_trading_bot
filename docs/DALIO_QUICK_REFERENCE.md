# Dalio Allocation - Quick Reference

## Current Balance: $50,078.20

### Asset Allocations & Risk Per Trade (1%)

| Symbol | Allocation | Allocated Capital | Risk (1%) | Expected Behavior |
|--------|-----------|------------------|-----------|-------------------|
| **USDCHF** | 20% | $10,015.64 | $100.16 | Largest positions (deflation hedge) |
| **XAUUSD** | 18% | $9,014.08 | $90.14 | Large gold positions (inflation hedge) |
| **GBPUSD** | 16% | $8,012.51 | $80.13 | Standard forex exposure |
| **EURUSD** | 16% | $8,012.51 | $80.13 | Standard forex exposure |
| **XAGUSD** | 15% | $7,511.73 | $75.12 | Silver commodity exposure |
| **AUDUSD** | 15% | $7,511.73 | $75.12 | Commodity currency exposure |

---

## Lot Size Examples (Typical SL Distance)

### Forex Pairs (100,000 contract size, ~$10/pip)

**USDCHF** (20% allocation → $100.16 risk)
- 30 pips SL: 0.03 lots
- 45 pips SL: 0.02 lots
- 60 pips SL: 0.017 lots

**GBPUSD/EURUSD** (16% allocation → $80.13 risk)
- 30 pips SL: 0.027 lots
- 45 pips SL: 0.018 lots
- 60 pips SL: 0.013 lots

**AUDUSD** (15% allocation → $75.12 risk)
- 30 pips SL: 0.025 lots
- 45 pips SL: 0.017 lots
- 60 pips SL: 0.013 lots

### Commodities (100 oz contract size)

**XAUUSD - Gold** (18% allocation → $90.14 risk)
- $15 SL (150 pips): 0.06 lots
- $28 SL (280 pips): 0.03 lots
- $40 SL (400 pips): 0.023 lots

**XAGUSD - Silver** (15% allocation → $75.12 risk)
- $0.30 SL (300 pips): 0.25 lots
- $0.50 SL (500 pips): 0.15 lots
- $0.70 SL (700 pips): 0.11 lots

---

## ⚠️ What Changed From Old System

### Old System (Equal Risk)
```
All assets: $500.78 risk per trade
Result: Same lot sizes regardless of economic role
Problem: XAGUSD showed tiny 1.0 lot (insufficient exposure)
```

### New System (Dalio Allocation)
```
USDCHF: $100.16 risk (20% allocation)
XAUUSD: $90.14 risk (18% allocation)
GBPUSD/EURUSD: $80.13 risk (16% allocation)
XAGUSD/AUDUSD: $75.12 risk (15% allocation)

Result: Lot sizes scale with economic scenario importance
Fix: XAGUSD now gets proper 15% commodity allocation
```

---

## 📊 Expected Log Output

When a trade executes, you'll see:

```
💰 USDCHF: Dalio Allocation System
   Portfolio Balance: $50,078.20
   Asset Allocation: 20% = $10,015.64
   Risk Per Trade: 1.0% of allocated = $100.16

💰 USDCHF: Position Sizing Calculation:
   Allocated: $10,015.64 (20% of $50,078.20) | Risk: 1.0% = $100.16
   SL Distance: 0.00450 price units (450.0 points)
   Contract Size: 100000 | Tick Value: $1.00 | Value/Point: $10.00
   Calculated Volume: 0.022258 lots (BEFORE limits)
   Final Volume: 0.020000 lots (min=0.01, max=500.0, step=0.01)
```

**Verify:** 
- ✅ "Allocated" shows asset-specific capital
- ✅ "Risk Per Trade" is 1% of allocated (not total balance)
- ✅ Final volume scales with allocation percentage

---

## 🧮 Manual Verification Formula

To verify any trade:

```python
# 1. Get current balance from MT5
balance = [CHECK MT5 BALANCE]

# 2. Look up allocation
allocation = {
    'USDCHF': 0.20,
    'XAUUSD': 0.18,
    'GBPUSD': 0.16,
    'EURUSD': 0.16,
    'XAGUSD': 0.15,
    'AUDUSD': 0.15
}[symbol]

# 3. Calculate allocated capital
allocated_capital = balance × allocation

# 4. Calculate risk amount (default 1%)
risk_amount = allocated_capital × 0.01

# 5. Verify lot size
# lot_size = risk_amount / (sl_distance_pips × pip_value)
```

**Example (XAGUSD with $50,078.20 balance):**
```
allocated_capital = 50_078.20 × 0.15 = 7_511.73
risk_amount = 7_511.73 × 0.01 = 75.12
lot_size (50 pips SL, $5/pip) = 75.12 / (50 × 5) = 0.30 lots ✅
```

---

## 🔍 Troubleshooting

### Problem: "Risk amount doesn't match expected"
**Check:**
1. Is balance fetched correctly? (account_info.balance)
2. Is symbol in ASSET_ALLOCATIONS dictionary?
3. Is RISK_PER_TRADE overridden in strategy config?

### Problem: "Lot size too small/large"
**Check:**
1. Verify allocated_capital calculation
2. Check SL distance (ATR × multiplier)
3. Verify pip value for symbol
4. Check volume_min/max/step constraints

### Problem: "Allocation percentage not showing in logs"
**Check:**
1. Search logs for "💰 [SYMBOL]: Dalio Allocation System"
2. Verify ASSET_ALLOCATIONS dictionary loaded
3. Check for typos in symbol names (XAUUSD vs XAUUSD_)

---

## 📝 Quick Test Checklist

When testing the system:

- [ ] **Balance Check**: Verify MT5 balance in logs matches reality
- [ ] **Allocation Check**: Each symbol shows correct % (20%, 18%, 16%, 15%)
- [ ] **Risk Check**: Risk amount = allocated_capital × 1%
- [ ] **Lot Size Check**: Compare calculated vs final volume
- [ ] **Constraints Check**: Volume respects min/max/step limits
- [ ] **Multiple Assets**: If 2+ assets enter simultaneously, total risk ≈ 2-3% of portfolio (not 6%)

---

## 💡 Economic Scenario Examples

### Inflationary Environment (High CPI, Money Printing)
**Expected Leaders:** XAUUSD (18%), XAGUSD (15%), AUDUSD (15%)
**Expected Laggards:** USDCHF (20% allocated but may underperform)

### Deflationary Environment (Economic Contraction)
**Expected Leaders:** USDCHF (20%), XAUUSD (18% as safe haven)
**Expected Laggards:** AUDUSD (15% commodity currency)

### Balanced Growth (Goldilocks Economy)
**Expected Balance:** All assets perform, diversification works optimally

**Strategy Benefit:** Portfolio has exposure to ALL scenarios, no single event destroys account.

---

## 📈 Portfolio Risk Summary

### Maximum Theoretical Risk (All 6 Assets Enter Simultaneously)
```
USDCHF: $100.16 (0.20% of portfolio)
XAUUSD: $90.14 (0.18% of portfolio)
GBPUSD: $80.13 (0.16% of portfolio)
EURUSD: $80.13 (0.16% of portfolio)
XAGUSD: $75.12 (0.15% of portfolio)
AUDUSD: $75.12 (0.15% of portfolio)
─────────────────────────────────────
TOTAL: $500.80 (1.00% of portfolio) ✅
```

**Old System (Equal Risk):** $3,004.68 (6% of portfolio) ❌

**Improvement:** 5x reduction in simultaneous risk exposure while maintaining economic diversification.

---

**Last Updated:** November 5, 2025  
**Balance Reference:** $50,078.20  
**Update Frequency:** Update this table when balance changes significantly (±10%)
