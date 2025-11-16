"""
FINAL VERIFICATION - Test position sizing for all symbols
===========================================================
Portfolio: $50,121.28 (from your screenshot)
Risk: 0.5% per trade (configurable)
"""

import MetaTrader5 as mt5
import numpy as np

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

DEFAULT_RISK_PERCENT = 0.005  # 0.5% risk per trade

# ATR multipliers (from strategy configs)
ATR_MULTIPLIERS = {
    'EURUSD': {'sl': 1.5, 'tp': 10.0},
    'GBPUSD': {'sl': 2.5, 'tp': 10.0},
    'XAUUSD': {'sl': 1.5, 'tp': 12.0},
    'AUDUSD': {'sl': 2.0, 'tp': 10.0},
    'XAGUSD': {'sl': 1.5, 'tp': 12.0},
    'USDCHF': {'sl': 2.5, 'tp': 10.0},
}

# Portfolio balance from screenshot
portfolio_balance = 50121.28

print("=" * 100)
print("FINAL VERIFICATION - ALL SYMBOLS POSITION SIZING")
print("=" * 100)
print(f"\n💰 Portfolio Balance: ${portfolio_balance:,.2f}")
print(f"⚠️  Risk per Trade: {DEFAULT_RISK_PERCENT*100:.2f}% of allocated capital\n")

for symbol in ASSET_ALLOCATIONS.keys():
    print("\n" + "=" * 100)
    print(f"📊 {symbol}")
    print("=" * 100)
    
    # Get symbol info
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"   ❌ Symbol not available")
        continue
    
    # Get current price
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        print(f"   ❌ Cannot get price")
        continue
    
    current_price = tick.ask
    
    # Get rates for ATR
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 20)
    if rates is None or len(rates) < 11:
        print(f"   ❌ Cannot get rates")
        continue
    
    # Calculate ATR
    high = np.array([r['high'] for r in rates[-11:]])
    low = np.array([r['low'] for r in rates[-11:]])
    close = np.array([r['close'] for r in rates[-11:]])
    tr = np.maximum(high - low, np.abs(high - np.roll(close, 1)))
    atr = np.mean(tr[1:])
    
    # Get multipliers
    atr_sl_mult = ATR_MULTIPLIERS[symbol]['sl']
    atr_tp_mult = ATR_MULTIPLIERS[symbol]['tp']
    
    # Calculate Dalio allocation
    allocation_percent = ASSET_ALLOCATIONS[symbol]
    allocated_capital = portfolio_balance * allocation_percent
    risk_amount = allocated_capital * DEFAULT_RISK_PERCENT
    
    # Calculate SL/TP
    sl_distance = atr * atr_sl_mult
    tp_distance = atr * atr_tp_mult
    
    # Get broker specs
    point = symbol_info.point
    tick_value = symbol_info.trade_tick_value
    tick_size = symbol_info.trade_tick_size
    
    # Calculate value per point
    if tick_size > 0 and point > 0:
        value_per_point = tick_value * (point / tick_size)
    else:
        value_per_point = tick_value
    
    # Calculate lot size
    sl_distance_in_points = sl_distance / point
    if value_per_point > 0 and sl_distance_in_points > 0:
        lot_size_raw = risk_amount / (sl_distance_in_points * value_per_point)
    else:
        print(f"   ❌ Invalid calculation values")
        continue
    
    # Apply limits
    lot_min = symbol_info.volume_min
    lot_max = symbol_info.volume_max
    lot_step = symbol_info.volume_step
    
    lot_size = round(lot_size_raw / lot_step) * lot_step
    lot_size = max(lot_min, min(lot_size, lot_max))
    
    # Verify risk
    actual_risk = lot_size * sl_distance_in_points * value_per_point
    
    # Calculate potential profit
    tp_distance_in_points = tp_distance / point
    potential_profit = lot_size * tp_distance_in_points * value_per_point
    
    # Print results
    print(f"\n📈 DALIO ALLOCATION:")
    print(f"   Allocation: {allocation_percent*100:.0f}% = ${allocated_capital:,.2f}")
    print(f"   Risk: {DEFAULT_RISK_PERCENT*100:.2f}% = ${risk_amount:.2f}")
    
    print(f"\n🎯 ATR CALCULATION:")
    print(f"   ATR (10 bars): {atr:.5f}")
    print(f"   SL Multiplier: {atr_sl_mult} → Distance: {sl_distance:.5f}")
    print(f"   TP Multiplier: {atr_tp_mult} → Distance: {tp_distance:.5f}")
    
    print(f"\n📐 POSITION SIZING:")
    print(f"   Value/Point: ${value_per_point:.5f}")
    print(f"   SL Points: {sl_distance_in_points:.1f}")
    print(f"   Raw Lot Size: {lot_size_raw:.6f} lots")
    print(f"   Final Lot Size: {lot_size:.2f} lots")
    
    print(f"\n✅ VERIFICATION:")
    print(f"   Expected Risk: ${risk_amount:.2f}")
    print(f"   Actual Risk: ${actual_risk:.2f}")
    print(f"   Difference: ${abs(actual_risk - risk_amount):.2f}")
    
    if abs(actual_risk - risk_amount) < 1.0:
        print(f"   ✅ VERIFIED!")
    else:
        print(f"   ⚠️ Risk mismatch")
    
    print(f"\n💰 EXPECTED RESULTS:")
    print(f"   Entry: {current_price:.5f}")
    print(f"   SL: {current_price - sl_distance:.5f} → Loss: ${actual_risk:.2f}")
    print(f"   TP: {current_price + tp_distance:.5f} → Profit: ${potential_profit:.2f}")
    print(f"   R:R Ratio: 1:{potential_profit/actual_risk:.2f}")

mt5.shutdown()

print("\n" + "=" * 100)
print("✅ VERIFICATION COMPLETE - Ready for rebuild")
print("=" * 100)
