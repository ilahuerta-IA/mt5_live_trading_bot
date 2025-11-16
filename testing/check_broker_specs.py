"""
Check actual broker specifications for all symbols
"""
import MetaTrader5 as mt5

if not mt5.initialize():
    print("MT5 initialization failed")
    exit()

symbols = ['EURUSD', 'GBPUSD', 'XAUUSD', 'AUDUSD', 'XAGUSD', 'USDCHF']

print("=" * 100)
print("BROKER SYMBOL SPECIFICATIONS")
print("=" * 100)

for symbol in symbols:
    info = mt5.symbol_info(symbol)
    if info is None:
        print(f"\n❌ {symbol}: Not found")
        continue
    
    print(f"\n📊 {symbol}:")
    print(f"   Digits: {info.digits}")
    print(f"   Point: {info.point:.10f}")
    print(f"   Tick Size: {info.trade_tick_size:.10f}")
    print(f"   Tick Value: ${info.trade_tick_value:.10f}")
    print(f"   Contract Size: {info.trade_contract_size:,.0f}")
    print(f"   Volume: min={info.volume_min}, max={info.volume_max}, step={info.volume_step}")
    
    # Calculate value per point
    if info.trade_tick_size > 0 and info.point > 0:
        value_per_point = info.trade_tick_value * (info.point / info.trade_tick_size)
    else:
        value_per_point = info.trade_tick_value
    
    print(f"   Calculated Value/Point: ${value_per_point:.10f}")

mt5.shutdown()
print("\n" + "=" * 100)
