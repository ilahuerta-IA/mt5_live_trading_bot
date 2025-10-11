"""MT5 Quick Test Script
====================
Simple script to test MetaTrader 5 installation and basic connection.
Run this first to verify your setup before using the full trading connector.
"""

import sys
from pathlib import Path

def test_mt5_installation():
    """Test if MT5 package is properly installed"""
    print("🔧 Testing MT5 package installation...")
    
    try:
        import MetaTrader5 as mt5
        print("✅ MetaTrader5 package found")
        
        # Get version info
        try:
            version = mt5.__version__
            print(f"📦 MT5 package version: {version}")
        except:
            print("📦 MT5 package version: Unknown")
        
        return True
    except ImportError as e:
        print(f"❌ MetaTrader5 package not found: {e}")
        print("💡 Install with: pip install MetaTrader5")
        return False

def test_mt5_terminal():
    """Test if MT5 terminal is running and accessible"""
    print("\n🔧 Testing MT5 terminal connection...")
    
    try:
        import MetaTrader5 as mt5
        
        # Try to initialize
        if not mt5.initialize():
            error = mt5.last_error()
            print(f"❌ MT5 terminal initialization failed: {error}")
            print("💡 Make sure MetaTrader 5 terminal is running")
            return False
        
        print("✅ MT5 terminal is accessible")
        
        # Get terminal info
        terminal_info = mt5.terminal_info()
        if terminal_info:
            print(f"📊 MT5 Terminal: {terminal_info.name}")
            print(f"📊 Build: {terminal_info.build}")
            print(f"📊 Path: {terminal_info.path}")
        
        # Cleanup
        mt5.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Error testing MT5 terminal: {e}")
        return False

def test_demo_connection():
    """Test connection with demo credentials (if available)"""
    print("\n🔧 Testing demo account connection...")
    
    # Check if credentials file exists
    config_file = Path(__file__).parent / 'config' / 'mt5_credentials.json'
    
    if not config_file.exists():
        print("ℹ️  No credentials file found - skipping connection test")
        print(f"💡 Create credentials file at: {config_file}")
        return True
    
    try:
        import json
        import MetaTrader5 as mt5
        
        # Load credentials
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        login = config.get('login')
        password = config.get('password')
        server = config.get('server')
        
        # Check if still template values
        if login == "YOUR_MT5_ACCOUNT_NUMBER":
            print("ℹ️  Template credentials detected - skipping connection test")
            print("💡 Update credentials file with your MT5 account details")
            return True
        
        # Initialize MT5
        if not mt5.initialize():
            print(f"❌ MT5 initialization failed: {mt5.last_error()}")
            return False
        
        # Attempt login
        if not mt5.login(login, password=password, server=server):
            error = mt5.last_error()
            print(f"❌ Login failed: {error}")
            print("💡 Check your credentials and ensure MT5 account is active")
            mt5.shutdown()
            return False
        
        # Get account info
        account_info = mt5.account_info()
        if account_info:
            print("✅ Successfully connected to MT5 account!")
            print(f"📊 Account: {account_info.login}")
            print(f"💰 Balance: {account_info.balance}")
            print(f"💱 Currency: {account_info.currency}")
            print(f"🏦 Server: {account_info.server}")
            
            # Safety check
            if account_info.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO:
                print("✅ Demo account confirmed - Safe for testing")
            else:
                print("⚠️  REAL ACCOUNT detected - Use with caution!")
        
        mt5.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

def test_symbol_access():
    """Test access to common trading symbols"""
    print("\n🔧 Testing symbol access...")
    
    try:
        import MetaTrader5 as mt5
        
        if not mt5.initialize():
            print("❌ Cannot initialize MT5 for symbol test")
            return False
        
        # Test common symbols
        test_symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'AUDUSD']
        available_symbols = []
        
        for symbol in test_symbols:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info:
                # Try to enable symbol
                if not symbol_info.visible:
                    mt5.symbol_select(symbol, True)
                
                # Get current tick
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    available_symbols.append(symbol)
                    print(f"✅ {symbol}: Bid={tick.bid:.5f}, Ask={tick.ask:.5f}")
                else:
                    print(f"⚠️  {symbol}: Symbol info available but no tick data")
            else:
                print(f"❌ {symbol}: Not available")
        
        print(f"\n📊 Available symbols: {len(available_symbols)}/{len(test_symbols)}")
        
        mt5.shutdown()
        return len(available_symbols) > 0
        
    except Exception as e:
        print(f"❌ Error testing symbols: {e}")
        return False

def test_strategy_imports():
    """Test importing Sunrise strategies"""
    print("\n🔧 Testing strategy imports...")
    
    try:
        # Use local strategies directory (independent from quant_bot_project)
        current_dir = Path(__file__).parent
        local_strategies_dir = current_dir / "strategies"
        
        if not local_strategies_dir.exists():
            print(f"❌ Local strategies directory not found: {local_strategies_dir}")
            return False
        
        sys.path.insert(0, str(local_strategies_dir))
        
        strategies_to_test = [
            'sunrise_ogle_eurusd',
            'sunrise_ogle_gbpusd', 
            'sunrise_ogle_xauusd',
            'sunrise_ogle_audusd',
            'sunrise_ogle_xagusd',
            'sunrise_ogle_usdchf'
        ]
        
        imported_strategies = []
        
        for strategy_name in strategies_to_test:
            try:
                module = __import__(strategy_name)
                imported_strategies.append(strategy_name)
                print(f"✅ {strategy_name}: Successfully imported")
            except ImportError as e:
                print(f"❌ {strategy_name}: Import failed - {e}")
        
        print(f"\n📊 Imported strategies: {len(imported_strategies)}/{len(strategies_to_test)}")
        
        if len(imported_strategies) > 0:
            print("✅ Strategy integration ready")
            return True
        else:
            print("❌ No strategies imported - check local strategies folder")
            return False
            
    except Exception as e:
        print(f"❌ Error testing strategy imports: {e}")
        return False

def run_all_tests():
    """Run comprehensive MT5 setup tests"""
    print("🌅 MT5 Live Trading Bot - Setup Verification")
    print("=" * 55)
    
    tests = [
        ("Package Installation", test_mt5_installation),
        ("Terminal Connection", test_mt5_terminal),
        ("Demo Account Connection", test_demo_connection),
        ("Symbol Access", test_symbol_access),
        ("Strategy Imports", test_strategy_imports)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 55)
    print("📊 TEST SUMMARY")
    print("=" * 55)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\n📈 Tests passed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("🎉 All tests passed! Ready for MT5 live trading.")
    else:
        print("⚠️  Some tests failed. Please address issues before proceeding.")
        print("\n💡 Common solutions:")
        print("   - Install MetaTrader5 package: pip install MetaTrader5")
        print("   - Ensure MT5 terminal is running")
        print("   - Create and configure credentials file")
        print("   - Verify MT5 account is active and accessible")
        print("   - Check local strategies are available")
    
    return passed == len(results)

if __name__ == "__main__":
    # Run tests
    success = run_all_tests()
    
    if success:
        print("\n🚀 Next steps:")
        print("1. Configure your MT5 credentials in config/mt5_credentials.json")
        print("2. Test signal generation: python src/sunrise_signal_adapter.py")
        print("3. Start live trading: python src/mt5_live_trading_connector.py")
        print("4. Always test on demo account first!")
    
    input("\nPress Enter to exit...")