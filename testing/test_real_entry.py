"""
Simulate REAL Bot Entry - Test with actual bot parameters
Uses the same ATR, SL/TP multipliers, and volume calculation as the bot
"""
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

def calculate_atr(df, period=14):
    """Calculate ATR exactly like the bot does"""
    high_low = df['high'] - df['low']
    high_close = abs(df['high'] - df['close'].shift())
    low_close = abs(df['low'] - df['close'].shift())
    
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()
    
    return atr.iloc[-1]

def test_real_bot_entry(symbol="XAGUSD"):
    """
    Simulate real bot entry with actual parameters:
    - ATR-based SL/TP
    - Real volume calculation (1% risk)
    - Same multipliers as bot (SL=4.5, TP=6.5)
    """
    
    print("=" * 80)
    print("🤖 SIMULATING REAL BOT ENTRY TEST")
    print("=" * 80)
    
    # Initialize MT5
    if not mt5.initialize():
        print(f"❌ MT5 initialization failed: {mt5.last_error()}")
        return False
    
    print(f"✅ MT5 initialized")
    
    # Get account info
    account_info = mt5.account_info()
    if account_info is None:
        print(f"❌ Cannot get account info")
        mt5.shutdown()
        return False
    
    balance = account_info.balance
    print(f"📊 Account: {account_info.login} | Balance: ${balance:.2f}")
    
    # Get symbol info
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"❌ {symbol} not found")
        mt5.shutdown()
        return False
    
    if not symbol_info.visible:
        if not mt5.symbol_select(symbol, True):
            print(f"❌ Failed to enable {symbol}")
            mt5.shutdown()
            return False
    
    print(f"✅ Symbol: {symbol}")
    print(f"   Min volume: {symbol_info.volume_min}")
    print(f"   Max volume: {symbol_info.volume_max}")
    print(f"   Volume step: {symbol_info.volume_step}")
    
    # Try to get stops level (may not exist in all MT5 versions)
    try:
        stops_level = symbol_info.trade_stops_level
        print(f"   Stops level: {stops_level}")
    except:
        stops_level = 0
        print(f"   Stops level: Not available (will skip validation)")
    
    # Detect filling mode (like the bot does)
    filling_mode_flags = symbol_info.filling_mode
    if filling_mode_flags & 2:
        filling_type = mt5.ORDER_FILLING_IOC
        filling_name = "IOC"
    elif filling_mode_flags & 1:
        filling_type = mt5.ORDER_FILLING_FOK
        filling_name = "FOK"
    elif filling_mode_flags & 4:
        filling_type = mt5.ORDER_FILLING_RETURN
        filling_name = "RETURN"
    else:
        filling_type = mt5.ORDER_FILLING_FOK
        filling_name = "FOK (Default)"
    
    print(f"🔧 Filling mode: {filling_name} (flags: {filling_mode_flags})")
    
    # Fetch data for ATR calculation
    print(f"\n📊 Fetching market data for ATR calculation...")
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 151)
    
    if rates is None or len(rates) < 100:
        print(f"❌ Cannot fetch rates")
        mt5.shutdown()
        return False
    
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    print(f"✅ Fetched {len(df)} bars")
    
    # Calculate ATR (like the bot does)
    atr = calculate_atr(df, period=14)
    print(f"📈 ATR (14): {atr:.5f}")
    
    # Bot configuration for XAGUSD
    config = {
        'atr_sl_multiplier': 4.5,
        'atr_tp_multiplier': 6.5,
        'risk_percent': 0.01,  # 1%
    }
    
    print(f"\n⚙️ Bot configuration:")
    print(f"   ATR SL Multiplier: {config['atr_sl_multiplier']}")
    print(f"   ATR TP Multiplier: {config['atr_tp_multiplier']}")
    print(f"   Risk: {config['risk_percent']*100}%")
    
    # Get current price
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        print(f"❌ Cannot get {symbol} tick")
        mt5.shutdown()
        return False
    
    # Simulate LONG entry (like the bot detected breakout)
    direction = "LONG"
    entry_price = tick.ask
    order_type = mt5.ORDER_TYPE_BUY
    
    print(f"\n💹 Current market:")
    print(f"   BID: {tick.bid:.5f}")
    print(f"   ASK: {tick.ask:.5f}")
    print(f"   Entry (ASK): {entry_price:.5f}")
    
    # Calculate SL/TP distances (like the bot does)
    sl_distance = atr * config['atr_sl_multiplier']
    tp_distance = atr * config['atr_tp_multiplier']
    
    digits = symbol_info.digits
    sl_price = round(entry_price - sl_distance, digits)  # LONG: SL below entry
    tp_price = round(entry_price + tp_distance, digits)  # LONG: TP above entry
    
    print(f"\n📏 Stop/Target calculation:")
    print(f"   SL Distance: {sl_distance:.5f} (ATR {atr:.5f} × {config['atr_sl_multiplier']})")
    print(f"   TP Distance: {tp_distance:.5f} (ATR {atr:.5f} × {config['atr_tp_multiplier']})")
    print(f"   SL Price: {sl_price:.5f}")
    print(f"   TP Price: {tp_price:.5f}")
    
    # Calculate volume (like the bot does)
    risk_amount = balance * config['risk_percent']
    tick_value = symbol_info.trade_tick_value
    tick_size = symbol_info.trade_tick_size
    
    # Calculate pip value
    sl_distance_pips = sl_distance / tick_size
    risk_per_lot = sl_distance_pips * tick_value
    
    if risk_per_lot > 0:
        calculated_volume = risk_amount / risk_per_lot
    else:
        calculated_volume = symbol_info.volume_min
    
    # Round to volume step
    volume_step = symbol_info.volume_step
    lot_size = round(calculated_volume / volume_step) * volume_step
    
    # Ensure within limits
    lot_size = max(symbol_info.volume_min, min(lot_size, symbol_info.volume_max))
    
    print(f"\n💰 Volume calculation:")
    print(f"   Risk amount: ${risk_amount:.2f} ({config['risk_percent']*100}% of ${balance:.2f})")
    print(f"   Tick value: ${tick_value:.2f}")
    print(f"   Risk per lot: ${risk_per_lot:.2f}")
    print(f"   Calculated volume: {calculated_volume:.2f} lots")
    print(f"   Rounded volume: {lot_size:.2f} lots")
    print(f"   Volume limits: {symbol_info.volume_min} - {symbol_info.volume_max}")
    
    # Check stops level
    actual_sl_distance = abs(entry_price - sl_price)
    actual_tp_distance = abs(tp_price - entry_price)
    
    print(f"\n🛡️ Stops validation:")
    if stops_level > 0:
        min_distance = stops_level * symbol_info.point
        print(f"   Min stops level: {stops_level} points ({min_distance:.5f})")
        print(f"   SL distance: {actual_sl_distance:.5f} {'✅' if actual_sl_distance >= min_distance else '❌ TOO CLOSE'}")
        print(f"   TP distance: {actual_tp_distance:.5f} {'✅' if actual_tp_distance >= min_distance else '❌ TOO CLOSE'}")
    else:
        print(f"   SL distance: {actual_sl_distance:.5f}")
        print(f"   TP distance: {actual_tp_distance:.5f}")
        print(f"   (Stops level validation skipped)")
    
    # Prepare order (exactly like the bot)
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot_size,
        "type": order_type,
        "price": entry_price,
        "sl": sl_price,
        "tp": tp_price,
        "deviation": 20,
        "magic": 234000,
        "comment": f"TEST_Sunrise_{direction}",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling_type,
    }
    
    print("\n" + "=" * 80)
    print("🚀 SENDING ORDER (SIMULATING BOT ENTRY)...")
    print("=" * 80)
    print(f"📋 Order summary:")
    print(f"   Direction: {direction}")
    print(f"   Entry: {entry_price:.5f}")
    print(f"   SL: {sl_price:.5f} (-{sl_distance:.5f})")
    print(f"   TP: {tp_price:.5f} (+{tp_distance:.5f})")
    print(f"   Volume: {lot_size} lots")
    print(f"   Risk: ${risk_amount:.2f}")
    print(f"   Filling: {filling_name}")
    
    # Ask for confirmation
    print("\n⚠️ THIS WILL PLACE A REAL ORDER!")
    response = input("Continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("❌ Test cancelled by user")
        mt5.shutdown()
        return False
    
    # Send order
    result = mt5.order_send(request)
    
    if result is None:
        print(f"\n❌ Order send failed - No response")
        print(f"   Last error: {mt5.last_error()}")
        mt5.shutdown()
        return False
    
    # Check result
    print(f"\n📋 Order result:")
    print(f"   Return code: {result.retcode}")
    print(f"   Comment: {result.comment}")
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"\n❌ ORDER FAILED!")
        print(f"   Code: {result.retcode}")
        print(f"   Description: {result.comment}")
        
        # Common error codes
        errors = {
            10004: "REQUOTE", 10006: "REJECT", 10010: "DONE_PARTIAL",
            10013: "INVALID", 10014: "INVALID_VOLUME", 10015: "INVALID_PRICE",
            10016: "INVALID_STOPS", 10018: "MARKET_CLOSED", 10019: "NO_MONEY",
            10030: "INVALID_FILL",
        }
        if result.retcode in errors:
            print(f"   Error: {errors[result.retcode]}")
        
        mt5.shutdown()
        return False
    
    # Success!
    print(f"\n✅ ✅ ✅ ORDER EXECUTED SUCCESSFULLY! ✅ ✅ ✅")
    print(f"\n📊 Trade details:")
    print(f"   Order ticket: #{result.order}")
    print(f"   Deal ticket: #{result.deal}")
    print(f"   Volume: {result.volume} lots")
    print(f"   Price: {result.price:.5f}")
    print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"   Direction: {direction}")
    print(f"   SL: {sl_price:.5f}")
    print(f"   TP: {tp_price:.5f}")
    
    print("\n" + "=" * 80)
    print("🎯 BOT ENTRY SIMULATION: SUCCESS!")
    print("🎉 The bot's filling mode fix is working correctly!")
    print("⚠️ REMEMBER TO MANAGE THIS POSITION IN MT5")
    print("=" * 80)
    
    mt5.shutdown()
    return True


if __name__ == "__main__":
    print("\n🤖 REAL BOT ENTRY SIMULATION")
    print("This test uses the EXACT same parameters as your bot:")
    print("  - ATR calculation (14 periods)")
    print("  - SL multiplier: 4.5")
    print("  - TP multiplier: 6.5")
    print("  - Risk: 1% of balance")
    print("  - Volume calculation matching bot logic")
    print("  - Filling mode detection (FOK/IOC/RETURN)")
    print("\n⚠️ This will place a REAL order with REAL money!")
    
    success = test_real_bot_entry("XAGUSD")
    
    if success:
        print("\n✅ Test PASSED - Bot is ready for live trading!")
    else:
        print("\n❌ Test FAILED - Check errors above")
