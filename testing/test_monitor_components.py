#!/usr/bin/env python3
"""
Test MT5 Trading Monitor Components
Quick test to verify all components are working
"""

import sys
import os
import importlib.util

def test_imports():
    """Test all imports"""
    print("🧪 Testing imports...")
    
    try:
        import MetaTrader5 as mt5
        print("✅ MetaTrader5 imported successfully")
    except ImportError as e:
        print(f"❌ MetaTrader5 import failed: {e}")
        return False
        
    try:
        import pandas as pd
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
        
    try:
        import tkinter as tk
        print("✅ Tkinter imported successfully")
    except ImportError as e:
        print(f"❌ Tkinter import failed: {e}")
        return False
        
    try:
        # Dynamic import of signal adapter components
        signal_adapter_path = os.path.join(os.path.dirname(__file__), "src", "sunrise_signal_adapter.py")
        spec = importlib.util.spec_from_file_location("sunrise_signal_adapter", signal_adapter_path)
        if spec and spec.loader:
            sunrise_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(sunrise_module)
            
            # Check if classes exist
            MultiSymbolSignalManager = getattr(sunrise_module, 'MultiSymbolSignalManager', None)
            MT5DataProvider = getattr(sunrise_module, 'MT5DataProvider', None)
            
            if MultiSymbolSignalManager and MT5DataProvider:
                print("✅ Signal components imported successfully")
            else:
                raise ImportError("Required classes not found in module")
        else:
            raise ImportError("Could not create module spec")
    except Exception as e:
        print(f"❌ Signal components import failed: {e}")
        return False
        
    return True

def test_mt5_connection():
    """Test MT5 connection"""
    print("\n🔌 Testing MT5 connection...")
    
    try:
        import MetaTrader5 as mt5
        
        if not mt5.initialize():
            print(f"❌ MT5 initialization failed: {mt5.last_error()}")
            return False
            
        terminal_info = mt5.terminal_info()
        if terminal_info:
            print(f"✅ MT5 connected - Terminal: {terminal_info.company}")
            print(f"   Connected: {terminal_info.connected}")
            print(f"   Trade allowed: {terminal_info.trade_allowed}")
        else:
            print("⚠️  MT5 initialized but no terminal info available")
            
        mt5.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ MT5 connection test failed: {e}")
        return False

def test_signal_manager():
    """Test signal manager"""
    print("\n📊 Testing signal manager...")
    
    try:
        # Dynamic import of signal manager
        signal_adapter_path = os.path.join(os.path.dirname(__file__), "src", "sunrise_signal_adapter.py")
        spec = importlib.util.spec_from_file_location("sunrise_signal_adapter", signal_adapter_path)
        if spec and spec.loader:
            sunrise_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(sunrise_module)
            
            MultiSymbolSignalManager = getattr(sunrise_module, 'MultiSymbolSignalManager', None)
            if not MultiSymbolSignalManager:
                raise ImportError("MultiSymbolSignalManager class not found")
        
        manager = MultiSymbolSignalManager()
        
        # Try to add a symbol
        if manager.add_symbol('EURUSD'):
            print("✅ Signal manager created and symbol added")
        else:
            print("⚠️  Signal manager created but symbol addition failed")
            
        return True
        
    except Exception as e:
        print(f"❌ Signal manager test failed: {e}")
        return False

def test_gui_components():
    """Test GUI components"""
    print("\n🖥️ Testing GUI components...")
    
    try:
        import tkinter as tk
        from tkinter import ttk
        
        # Create test window
        root = tk.Tk()
        root.title("Test Window")
        root.geometry("300x200")
        root.withdraw()  # Hide window
        
        # Test basic widgets
        label = tk.Label(root, text="Test")
        button = ttk.Button(root, text="Test Button")
        
        print("✅ GUI components working")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ GUI components test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 MT5 Trading Monitor Component Tests")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("MT5 Connection", test_mt5_connection), 
        ("Signal Manager", test_signal_manager),
        ("GUI Components", test_gui_components)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    print("-" * 30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 All tests passed! Monitor should work correctly.")
    else:
        print(f"\n⚠️  {len(tests) - passed} tests failed. Please check the issues above.")
    
    return passed == len(tests)

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")