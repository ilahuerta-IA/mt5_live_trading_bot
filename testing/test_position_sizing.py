"""
TEST POSITION SIZING - Verify Dalio Allocation System
======================================================
Portfolio: $50,000
Risk: 0.5% per trade
Testing EURUSD entry with ATR-based SL/TP
"""

import MetaTrader5 as mt5

# Initialize MT5
if not mt5.initialize():
    print("MT5 initialization failed")
    exit()

# ═══════════════════════════════════════════════════════════════════
# DALIO ALLOCATION SYSTEM
# ═══════════════════════════════════════════════════════════════════
ASSET_ALLOCATIONS = {
    'USDCHF': 0.20,   # 20% - Deflation hedge
    'XAUUSD': 0.18,   # 18% - Inflation hedge
    'GBPUSD': 0.16,   # 16% - Standard forex
    'EURUSD': 0.16,   # 16% - Standard forex
    'XAGUSD': 0.15,   # 15% - Commodity metal
    'AUDUSD': 0.15,   # 15% - Commodity currency
}

DEFAULT_RISK_PERCENT = 0.005  # 0.5% risk per trade (of allocated capital)

# ═══════════════════════════════════════════════════════════════════
# TEST PARAMETERS
# ═══════════════════════════════════════════════════════════════════
symbol = "EURUSD"
portfolio_balance = 50000.0  # $50K portfolio

# Get current price and symbol info
tick = mt5.symbol_info_tick(symbol)
symbol_info = mt5.symbol_info(symbol)

if tick is None or symbol_info is None:
    print(f"Failed to get {symbol} data")
    mt5.shutdown()
    exit()

current_price = tick.ask  # For buy order

# Get recent rates for ATR calculation
rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 20)
if rates is None:
    print(f"Failed to get {symbol} rates")
    mt5.shutdown()
    exit()

# Calculate ATR (simple approximation - last 10 bars)
import numpy as np
high = np.array([r['high'] for r in rates[-10:]])
low = np.array([r['low'] for r in rates[-10:]])
close = np.array([r['close'] for r in rates[-10:]])
tr = np.maximum(high - low, np.abs(high - np.roll(close, 1)))
atr = np.mean(tr[1:])  # Skip first element due to roll

print("=" * 80)
print("POSITION SIZING TEST - DALIO ALLOCATION SYSTEM")
print("=" * 80)
print()

# ═══════════════════════════════════════════════════════════════════
# STEP 1: DALIO ALLOCATION
# ═══════════════════════════════════════════════════════════════════
allocation_percent = ASSET_ALLOCATIONS[symbol]
allocated_capital = portfolio_balance * allocation_percent
risk_percent = DEFAULT_RISK_PERCENT
risk_amount = allocated_capital * risk_percent

print("📊 STEP 1: DALIO ALLOCATION")
print(f"   Portfolio Balance: ${portfolio_balance:,.2f}")
print(f"   Asset Allocation ({symbol}): {allocation_percent*100:.0f}% = ${allocated_capital:,.2f}")
print(f"   Risk per Trade: {risk_percent*100:.2f}% of allocated = ${risk_amount:.2f}")
print()

# ═══════════════════════════════════════════════════════════════════
# STEP 2: STOP LOSS CALCULATION (ATR-based)
# ═══════════════════════════════════════════════════════════════════
# EURUSD: 1.5 ATR for SL, 10 ATR for TP (from strategy config)
ATR_SL_MULTIPLIER = 1.5
ATR_TP_MULTIPLIER = 10.0

sl_distance = atr * ATR_SL_MULTIPLIER
tp_distance = atr * ATR_TP_MULTIPLIER

sl_price = current_price - sl_distance
tp_price = current_price + tp_distance

print("🎯 STEP 2: STOP LOSS/TAKE PROFIT (ATR-based)")
print(f"   Current Price: {current_price:.5f}")
print(f"   ATR (10 bars): {atr:.5f}")
print(f"   SL Distance: {ATR_SL_MULTIPLIER} × {atr:.5f} = {sl_distance:.5f}")
print(f"   TP Distance: {ATR_TP_MULTIPLIER} × {atr:.5f} = {tp_distance:.5f}")
print(f"   SL Price: {sl_price:.5f}")
print(f"   TP Price: {tp_price:.5f}")
print()

# ═══════════════════════════════════════════════════════════════════
# STEP 3: LOT SIZE CALCULATION
# ═══════════════════════════════════════════════════════════════════
# Formula: lot_size = risk_amount / (sl_distance_in_points × value_per_point)

point = symbol_info.point
tick_value = symbol_info.trade_tick_value
tick_size = symbol_info.trade_tick_size
contract_size = symbol_info.trade_contract_size
digits = symbol_info.digits

# Calculate value per point from MT5 symbol info
if tick_size > 0 and point > 0:
    value_per_point = tick_value * (point / tick_size)
else:
    value_per_point = tick_value if tick_value > 0 else 0.01

# Calculate SL distance in points
sl_distance_in_points = sl_distance / point

# Calculate lot size
if value_per_point > 0 and sl_distance_in_points > 0:
    lot_size = risk_amount / (sl_distance_in_points * value_per_point)
else:
    print("ERROR: Invalid calculation values!")
    mt5.shutdown()
    exit()

print("📐 STEP 3: LOT SIZE CALCULATION")
print(f"   Contract Size: {contract_size:,.0f}")
print(f"   Point: {point:.5f}")
print(f"   Tick Size: {tick_size:.5f}")
print(f"   Tick Value: ${tick_value:.5f}")
print(f"   Value per Point: ${value_per_point:.5f}")
print()
print(f"   SL Distance in Points: {sl_distance_in_points:.1f}")
print(f"   Formula: lot_size = ${risk_amount:.2f} / ({sl_distance_in_points:.1f} × ${value_per_point:.5f})")
print(f"   Calculated: lot_size = ${risk_amount:.2f} / ${sl_distance_in_points * value_per_point:.5f}")
print(f"   RAW LOT SIZE: {lot_size:.6f} lots")
print()

# Apply lot size limits
lot_min = symbol_info.volume_min
lot_max = symbol_info.volume_max
lot_step = symbol_info.volume_step

# Round to step
lot_size = round(lot_size / lot_step) * lot_step

# Clamp to limits
lot_size = max(lot_min, min(lot_max, lot_size))

print(f"   Volume Limits: min={lot_min}, max={lot_max}, step={lot_step}")
print(f"   FINAL LOT SIZE: {lot_size:.2f} lots")
print()

# ═══════════════════════════════════════════════════════════════════
# STEP 4: RISK VERIFICATION
# ═══════════════════════════════════════════════════════════════════
actual_risk = lot_size * sl_distance_in_points * value_per_point
risk_diff = abs(actual_risk - risk_amount)

print("✅ STEP 4: RISK VERIFICATION")
print(f"   Formula: {lot_size:.2f} lots × {sl_distance_in_points:.1f} points × ${value_per_point:.5f}")
print(f"   Actual Risk: ${actual_risk:.2f}")
print(f"   Expected Risk: ${risk_amount:.2f}")
print(f"   Difference: ${risk_diff:.2f}")

if risk_diff < 1.0:
    print(f"   ✅ VERIFIED! Risk matches expected (within $1)")
else:
    print(f"   ⚠️ WARNING: Risk mismatch of ${risk_diff:.2f}")
print()

# ═══════════════════════════════════════════════════════════════════
# STEP 5: WHAT USER SHOULD SEE IN MT5
# ═══════════════════════════════════════════════════════════════════
print("=" * 80)
print("📋 EXPECTED MT5 ORDER RESULTS:")
print("=" * 80)
print(f"Symbol: {symbol}")
print(f"Type: BUY")
print(f"Volume: {lot_size:.2f} lots")
print(f"Entry Price: {current_price:.5f}")
print(f"Stop Loss: {sl_price:.5f}")
print(f"Take Profit: {tp_price:.5f}")
print()
print(f"If SL is hit, loss should be: ${actual_risk:.2f}")
print(f"If TP is hit, profit should be: ${lot_size * (tp_distance/point) * value_per_point:.2f}")
print()
print("=" * 80)

# Calculate what the user is currently seeing (wrong calculation)
print("🔴 CURRENT BOT CALCULATION (WRONG - 0.1 lots):")
print("=" * 80)
wrong_lot_size = 0.1
wrong_risk = wrong_lot_size * sl_distance_in_points * value_per_point
print(f"Volume: {wrong_lot_size} lots")
print(f"Risk at SL: ${wrong_risk:.2f}")
print(f"Expected Risk: ${risk_amount:.2f}")
print(f"ERROR: Risk is {risk_amount/wrong_risk:.1f}x TOO SMALL!")
print()

mt5.shutdown()

print("=" * 80)
print("CONCLUSION:")
print("=" * 80)
print(f"✅ Correct lot size should be: {lot_size:.2f} lots (not 0.1!)")
print(f"✅ This will risk ${actual_risk:.2f} (target: ${risk_amount:.2f})")
print(f"✅ SL distance: {sl_distance:.5f} ({ATR_SL_MULTIPLIER} × ATR)")
print(f"✅ TP distance: {tp_distance:.5f} ({ATR_TP_MULTIPLIER} × ATR)")
print("=" * 80)
