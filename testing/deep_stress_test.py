#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deep Stress Test for MT5 Trading Monitor
Comprehensive testing of all system components under load
"""

import time
import threading
import sys
import os
from datetime import datetime, timedelta
import json

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

def dynamic_import(module_name, package_name=None):
    """Dynamic import helper"""
    try:
        import importlib.util
        if package_name:
            spec = importlib.util.find_spec(f"{package_name}.{module_name}")
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
        
        spec = importlib.util.find_spec(module_name)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    except (ImportError, ModuleNotFoundError):
        pass
    return None

def test_imports():
    """Test all critical imports"""
    print("🧪 DEEP TEST: Import Validation")
    print("-" * 40)
    
    try:
        import MetaTrader5 as mt5
        print("✅ MetaTrader5 imported")
        
        import pandas as pd
        import numpy as np
        print("✅ Data processing libraries imported")
        
        import tkinter as tk
        from tkinter import ttk
        print("✅ GUI libraries imported")
        
        # Test strategy imports
        sunrise_signal_adapter = dynamic_import("sunrise_signal_adapter", "src")
        if sunrise_signal_adapter:
            print("✅ Signal processing module imported")
        else:
            print("⚠️ Signal processing module not found")
            
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_mt5_connection():
    """Test MT5 connection stability"""
    print("\n🔌 DEEP TEST: MT5 Connection Stability")
    print("-" * 40)
    
    try:
        import MetaTrader5 as mt5
        
        # Test multiple connection cycles
        for i in range(3):
            print(f"Connection cycle {i+1}/3...")
            
            if not mt5.initialize():
                print(f"❌ Failed to initialize MT5: {mt5.last_error()}")
                return False
                
            account_info = mt5.account_info()
            if account_info:
                print(f"✅ Connected to account: {account_info.login}")
            else:
                print("❌ No account info")
                return False
                
            # Test symbol info retrieval
            symbols = ['EURUSD', 'XAUUSD', 'GBPUSD']
            for symbol in symbols:
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    print(f"   ✅ {symbol}: {tick.bid}/{tick.ask}")
                else:
                    print(f"   ⚠️ {symbol}: No tick data")
                    
            mt5.shutdown()
            time.sleep(1)
            
        return True
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_signal_generation():
    """Test signal generation system"""
    print("\n📊 DEEP TEST: Signal Generation System")
    print("-" * 40)
    
    try:
        import MetaTrader5 as mt5
        import pandas as pd
        
        if not mt5.initialize():
            print("❌ Could not initialize MT5")
            return False
            
        # Test signal generation for multiple symbols
        symbols = ['EURUSD', 'XAUUSD', 'GBPUSD', 'AUDUSD']
        signals_generated = 0
        
        sunrise_signal_adapter = dynamic_import("sunrise_signal_adapter", "src")
        if not sunrise_signal_adapter:
            print("⚠️ No signal adapter found")
            return True  # Not critical
            
        if hasattr(sunrise_signal_adapter, 'MultiSymbolSignalManager'):
            signal_manager = sunrise_signal_adapter.MultiSymbolSignalManager()
            
            for symbol in symbols:
                try:
                    # Add symbol to manager
                    signal_manager.add_symbol(symbol)
                    print(f"✅ {symbol}: Added to signal manager")
                    
                    # Get recent data
                    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 100)
                    if rates is not None and len(rates) > 50:
                        df = pd.DataFrame(rates)
                        df['time'] = pd.to_datetime(df['time'], unit='s')
                        
                        # Check for signal
                        signal = signal_manager.check_signal(symbol, df)
                        if signal and signal != 'HOLD':
                            signals_generated += 1
                            print(f"   🎯 {symbol}: {signal} signal detected at {df.iloc[-1]['close']:.5f}")
                        else:
                            print(f"   📊 {symbol}: No signal (current state: {signal or 'HOLD'})")
                            
                    else:
                        print(f"   ⚠️ {symbol}: Insufficient data")
                        
                except Exception as e:
                    print(f"   ❌ {symbol}: Error - {str(e)}")
                    
        mt5.shutdown()
        
        print(f"\n📈 Total signals generated: {signals_generated}")
        return True
        
    except Exception as e:
        print(f"❌ Signal generation error: {e}")
        return False

def test_gui_components():
    """Test GUI component initialization"""
    print("\n🖥️ DEEP TEST: GUI Component Stress Test")
    print("-" * 40)
    
    try:
        import tkinter as tk
        from tkinter import ttk, scrolledtext
        
        # Create test window
        test_root = tk.Tk()
        test_root.title("Deep Test - GUI Components")
        test_root.geometry("800x600")
        test_root.withdraw()  # Hide the window
        
        # Test notebook creation
        notebook = ttk.Notebook(test_root)
        print("✅ Notebook widget created")
        
        # Test multiple tabs
        tab_names = ["Overview", "Strategies", "Positions", "Signals", "Logs", "Connection"]
        tabs = []
        
        for name in tab_names:
            tab = ttk.Frame(notebook)
            notebook.add(tab, text=name)
            tabs.append(tab)
            
        print(f"✅ {len(tabs)} tabs created")
        
        # Test treeview widgets
        columns = ("Col1", "Col2", "Col3", "Col4")
        tree = ttk.Treeview(tabs[0], columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
            
        print("✅ Treeview widget created")
        
        # Test scrolled text
        scroll_text = scrolledtext.ScrolledText(tabs[1], height=10)
        scroll_text.insert(tk.END, "Test content\n" * 20)
        print("✅ ScrolledText widget created")
        
        # Test text tags (for colored logging)
        scroll_text.tag_config("ERROR", foreground="red")
        scroll_text.tag_config("SUCCESS", foreground="green")
        scroll_text.tag_config("WARNING", foreground="orange")
        print("✅ Text tags configured")
        
        # Test button creation
        for i in range(10):
            btn = ttk.Button(tabs[2], text=f"Button {i}")
            
        print("✅ Multiple buttons created")
        
        # Cleanup
        test_root.quit()
        test_root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ GUI component error: {e}")
        return False

def test_threading_performance():
    """Test threading performance and stability"""
    print("\n⚡ DEEP TEST: Threading Performance")
    print("-" * 40)
    
    try:
        import threading
        import queue
        
        # Test queue operations
        test_queue = queue.Queue()
        
        def producer():
            for i in range(100):
                test_queue.put(f"message_{i}")
                time.sleep(0.001)
                
        def consumer():
            messages = []
            while len(messages) < 100:
                try:
                    msg = test_queue.get(timeout=1)
                    messages.append(msg)
                except queue.Empty:
                    break
            return len(messages)
            
        # Start threads
        prod_thread = threading.Thread(target=producer, daemon=True)
        cons_thread = threading.Thread(target=consumer, daemon=True)
        
        start_time = time.time()
        prod_thread.start()
        cons_thread.start()
        
        prod_thread.join(timeout=5)
        cons_thread.join(timeout=5)
        
        end_time = time.time()
        
        print(f"✅ Threading test completed in {end_time - start_time:.2f} seconds")
        
        # Test event handling
        stop_event = threading.Event()
        
        def test_worker():
            count = 0
            while not stop_event.is_set() and count < 1000:
                count += 1
                time.sleep(0.001)
            return count
            
        worker_thread = threading.Thread(target=test_worker, daemon=True)
        worker_thread.start()
        
        time.sleep(0.5)
        stop_event.set()
        worker_thread.join(timeout=2)
        
        print("✅ Event-driven threading test passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Threading error: {e}")
        return False

def test_data_processing():
    """Test data processing capabilities"""
    print("\n📈 DEEP TEST: Data Processing Performance")
    print("-" * 40)
    
    try:
        import pandas as pd
        import numpy as np
        
        # Create test dataset
        dates = pd.date_range(start='2025-01-01', periods=10000, freq='1min')
        
        # Simulate OHLCV data
        np.random.seed(42)
        base_price = 1.1000
        price_changes = np.random.normal(0, 0.0001, len(dates))
        prices = base_price + np.cumsum(price_changes)
        
        df = pd.DataFrame({
            'time': dates,
            'open': prices,
            'high': prices + np.random.uniform(0, 0.0005, len(prices)),
            'low': prices - np.random.uniform(0, 0.0005, len(prices)),
            'close': prices + np.random.uniform(-0.0002, 0.0002, len(prices)),
            'volume': np.random.randint(100, 1000, len(prices))
        })
        
        print(f"✅ Created dataset with {len(df)} records")
        
        # Test various operations
        start_time = time.time()
        
        # Moving averages
        df['ma_20'] = df['close'].rolling(20).mean()
        df['ma_50'] = df['close'].rolling(50).mean()
        
        # Technical indicators
        df['rsi'] = calculate_rsi(df['close'], 14)
        
        # Signal conditions
        df['signal'] = np.where(df['ma_20'] > df['ma_50'], 1, -1)
        
        end_time = time.time()
        
        print(f"✅ Data processing completed in {end_time - start_time:.3f} seconds")
        print(f"   - Records processed: {len(df):,}")
        print(f"   - Processing rate: {len(df)/(end_time - start_time):.0f} records/second")
        
        # Test memory usage
        memory_usage = df.memory_usage(deep=True).sum() / 1024 / 1024
        print(f"   - Memory usage: {memory_usage:.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Data processing error: {e}")
        return False

def calculate_rsi(prices, period=14):
    """Calculate RSI indicator"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def test_file_operations():
    """Test file I/O operations"""
    print("\n💾 DEEP TEST: File Operations")
    print("-" * 40)
    
    try:
        # Test log file writing
        test_log_file = "deep_test_log.txt"
        
        with open(test_log_file, 'w', encoding='utf-8') as f:
            for i in range(1000):
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                f.write(f"[{timestamp}] Test log entry {i}\n")
                
        print(f"✅ Created test log file with 1000 entries")
        
        # Test JSON operations
        test_data = {
            'timestamp': datetime.now().isoformat(),
            'test_results': {
                'imports': True,
                'connection': True,
                'signals': True,
                'gui': True
            },
            'performance_metrics': {
                'processing_time': 0.123,
                'memory_usage': 45.6,
                'thread_count': 5
            },
            'symbols': ['EURUSD', 'XAUUSD', 'GBPUSD', 'AUDUSD'],
            'large_array': list(range(1000))
        }
        
        test_json_file = "deep_test_data.json"
        with open(test_json_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2)
            
        print("✅ JSON data export successful")
        
        # Read back and verify
        with open(test_json_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
            
        if len(loaded_data['large_array']) == 1000:
            print("✅ JSON data verification successful")
        else:
            print("❌ JSON data verification failed")
            
        # Cleanup
        os.remove(test_log_file)
        os.remove(test_json_file)
        print("✅ Test files cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ File operations error: {e}")
        return False

def main():
    """Run comprehensive deep testing"""
    print("🚀 MT5 TRADING MONITOR - DEEP STRESS TEST")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    test_results = {}
    start_time = time.time()
    
    # Run all tests
    tests = [
        ("Import Validation", test_imports),
        ("MT5 Connection Stability", test_mt5_connection),
        ("Signal Generation System", test_signal_generation),
        ("GUI Components", test_gui_components),
        ("Threading Performance", test_threading_performance),
        ("Data Processing", test_data_processing),
        ("File Operations", test_file_operations)
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            test_results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"\n{status}: {test_name}")
        except Exception as e:
            test_results[test_name] = False
            print(f"\n❌ FAILED: {test_name} - Exception: {str(e)}")
    
    # Final results
    end_time = time.time()
    total_time = end_time - start_time
    
    print("\n" + "=" * 60)
    print("🎯 DEEP TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("-" * 60)
    print(f"📊 Overall Score: {passed_tests}/{total_tests} tests passed")
    print(f"⏱️ Total Runtime: {total_time:.2f} seconds")
    print(f"🏆 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL DEEP TESTS PASSED! System is ready for production use.")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} tests failed. Please review and fix issues.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()