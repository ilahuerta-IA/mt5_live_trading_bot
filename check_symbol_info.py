"""
Check MT5 Symbol Volume Requirements
"""
import MetaTrader5 as mt5

if not mt5.initialize():
    print(f"❌ MT5 initialization failed")
    exit()

symbol = "XAGUSD"
symbol_info = mt5.symbol_info(symbol)

if symbol_info is None:
    print(f"❌ {symbol} not found")
    mt5.shutdown()
    exit()

print("=" * 70)
print(f"📊 {symbol} SYMBOL INFORMATION")
print("=" * 70)
print(f"Spread: {symbol_info.spread}")
print(f"Digits: {symbol_info.digits}")
print(f"Point: {symbol_info.point}")
print(f"Trade contract size: {symbol_info.trade_contract_size}")
print("\n🔧 VOLUME REQUIREMENTS:")
print(f"   Volume MIN: {symbol_info.volume_min}")
print(f"   Volume MAX: {symbol_info.volume_max}")
print(f"   Volume STEP: {symbol_info.volume_step}")
print("\n🔧 FILLING MODE:")
print(f"   Filling mode flags: {symbol_info.filling_mode}")
if symbol_info.filling_mode & 1:
    print("   ✅ FOK (Fill or Kill)")
if symbol_info.filling_mode & 2:
    print("   ✅ IOC (Immediate or Cancel)")
if symbol_info.filling_mode & 4:
    print("   ✅ RETURN")
print("=" * 70)

# Test other symbols for comparison
print("\n📊 COMPARISON WITH OTHER SYMBOLS:")
print("=" * 70)
for test_symbol in ["EURUSD", "XAUUSD", "GBPUSD"]:
    info = mt5.symbol_info(test_symbol)
    if info:
        print(f"{test_symbol}:")
        print(f"   Volume MIN: {info.volume_min} | MAX: {info.volume_max} | STEP: {info.volume_step}")
        print(f"   Filling mode: {info.filling_mode}")

mt5.shutdown()
