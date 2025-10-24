"""
Quick MT5 Order Test Script
Tests order execution with correct filling mode detection
"""
import MetaTrader5 as mt5
from datetime import datetime

def test_order_execution(symbol="XAGUSD", volume=0.01):
    """Test order execution with minimal risk"""
    
    print("=" * 70)
    print("🧪 MT5 ORDER EXECUTION TEST")
    print("=" * 70)
    
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
    
    print(f"📊 Account: {account_info.login} | Balance: ${account_info.balance:.2f}")
    
    # Get symbol info
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"❌ {symbol} not found")
        mt5.shutdown()
        return False
    
    if not symbol_info.visible:
        print(f"⚠️ {symbol} not visible, trying to enable...")
        if not mt5.symbol_select(symbol, True):
            print(f"❌ Failed to enable {symbol}")
            mt5.shutdown()
            return False
    
    print(f"✅ Symbol: {symbol} | Spread: {symbol_info.spread}")
    
    # Check minimum volume
    min_volume = symbol_info.volume_min
    max_volume = symbol_info.volume_max
    volume_step = symbol_info.volume_step
    print(f"📊 Volume requirements: MIN={min_volume} | MAX={max_volume} | STEP={volume_step}")
    
    # Adjust volume to meet minimum requirement
    if volume < min_volume:
        print(f"⚠️ Requested volume {volume} is below minimum {min_volume}, using {min_volume}")
        volume = min_volume
    
    # Detect filling mode
    filling_mode_flags = symbol_info.filling_mode
    print(f"🔧 Filling mode flags: {filling_mode_flags}")
    
    if filling_mode_flags & 2:  # IOC
        filling_type = mt5.ORDER_FILLING_IOC
        filling_name = "IOC (Immediate or Cancel)"
    elif filling_mode_flags & 1:  # FOK
        filling_type = mt5.ORDER_FILLING_FOK
        filling_name = "FOK (Fill or Kill)"
    elif filling_mode_flags & 4:  # RETURN
        filling_type = mt5.ORDER_FILLING_RETURN
        filling_name = "RETURN"
    else:
        filling_type = mt5.ORDER_FILLING_FOK
        filling_name = "FOK (Default)"
    
    print(f"✅ Using filling mode: {filling_name}")
    
    # Get current price
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        print(f"❌ Cannot get {symbol} tick")
        mt5.shutdown()
        return False
    
    price = tick.ask  # For BUY order
    print(f"💹 Current ASK price: {price:.5f}")
    
    # Calculate SL/TP with proper distance (using stops level)
    point = symbol_info.point
    digits = symbol_info.digits
    stops_level = symbol_info.trade_stops_level
    print(f"⚠️ Minimum stops level: {stops_level} points")
    
    # Use 2x stops level to be safe
    safe_distance = max(stops_level * 2, 100)  # At least 100 points
    sl_price = round(price - safe_distance * point, digits)
    tp_price = round(price + safe_distance * 2 * point, digits)
    
    print(f"📊 Order parameters:")
    print(f"   Entry: {price:.5f}")
    print(f"   SL: {sl_price:.5f} (50 points)")
    print(f"   TP: {tp_price:.5f} (100 points)")
    print(f"   Volume: {volume} lots")
    
    # Prepare order
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": sl_price,
        "tp": tp_price,
        "deviation": 20,
        "magic": 999999,
        "comment": "TEST_ORDER",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling_type,
    }
    
    print("\n" + "=" * 70)
    print("🚀 SENDING TEST ORDER...")
    print("=" * 70)
    
    # Send order
    result = mt5.order_send(request)
    
    if result is None:
        print(f"❌ Order send failed - No response")
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
        
        # Show common error codes
        error_codes = {
            10004: "REQUOTE - Requote",
            10006: "REJECT - Request rejected",
            10007: "CANCEL - Request canceled",
            10008: "PLACED - Order placed",
            10009: "DONE - Request completed",
            10010: "DONE_PARTIAL - Request partially completed",
            10011: "ERROR - Request error",
            10012: "TIMEOUT - Request timeout",
            10013: "INVALID - Invalid request",
            10014: "INVALID_VOLUME - Invalid volume",
            10015: "INVALID_PRICE - Invalid price",
            10016: "INVALID_STOPS - Invalid stops",
            10017: "TRADE_DISABLED - Trade disabled",
            10018: "MARKET_CLOSED - Market closed",
            10019: "NO_MONEY - Not enough money",
            10020: "PRICE_CHANGED - Price changed",
            10021: "PRICE_OFF - No prices",
            10022: "INVALID_EXPIRATION - Invalid expiration",
            10023: "ORDER_CHANGED - Order changed",
            10024: "TOO_MANY_REQUESTS - Too many requests",
            10025: "NO_CHANGES - No changes",
            10026: "SERVER_DISABLES_AT - Auto trading disabled by server",
            10027: "CLIENT_DISABLES_AT - Auto trading disabled by client",
            10028: "LOCKED - Request locked",
            10029: "FROZEN - Order/position frozen",
            10030: "INVALID_FILL - Invalid fill",
            10031: "CONNECTION - No connection",
            10032: "ONLY_REAL - Only real accounts",
            10033: "LIMIT_ORDERS - Limit orders only",
            10034: "LIMIT_VOLUME - Limit volume",
            10035: "INVALID_ORDER - Invalid order",
            10036: "POSITION_CLOSED - Position already closed",
        }
        
        if result.retcode in error_codes:
            print(f"   Meaning: {error_codes[result.retcode]}")
        
        mt5.shutdown()
        return False
    
    # Success!
    print(f"\n✅ ORDER EXECUTED SUCCESSFULLY!")
    print(f"   Order ticket: #{result.order}")
    print(f"   Deal ticket: #{result.deal}")
    print(f"   Volume: {result.volume} lots")
    print(f"   Price: {result.price:.5f}")
    print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
    
    print("\n" + "=" * 70)
    print("⚠️ REMEMBER TO CLOSE THE TEST POSITION MANUALLY IN MT5!")
    print("=" * 70)
    
    mt5.shutdown()
    return True


if __name__ == "__main__":
    print("\n🧪 MT5 ORDER TEST SCRIPT")
    print("This will place a REAL order with minimal volume (0.01 lots)")
    print("Make sure you have enough balance and are connected to MT5\n")
    
    # Test with different symbols
    symbols_to_test = [
        ("XAGUSD", 0.01),  # Silver - the one that failed
        # ("EURUSD", 0.01),  # Uncomment to test forex
        # ("XAUUSD", 0.01),  # Uncomment to test gold
    ]
    
    for symbol, volume in symbols_to_test:
        print(f"\n{'=' * 70}")
        print(f"Testing {symbol}...")
        print(f"{'=' * 70}")
        
        success = test_order_execution(symbol, volume)
        
        if success:
            print(f"\n✅ {symbol} test PASSED")
            
            # Ask if user wants to continue with next symbol
            if len(symbols_to_test) > 1:
                response = input("\nTest next symbol? (y/n): ")
                if response.lower() != 'y':
                    break
        else:
            print(f"\n❌ {symbol} test FAILED")
            break
    
    print("\n" + "=" * 70)
    print("Test completed!")
    print("=" * 70)
