#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced MT5 Trading Monitor - Launcher
Enhanced launcher for the advanced strategy phase tracking GUI
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox
import importlib.util

def check_core_requirements():
    """Check if core required packages are installed"""
    try:
        import MetaTrader5
        import pandas
        import numpy
        return True, None
    except ImportError as e:
        return False, str(e)

def check_chart_requirements():
    """Check if charting packages are installed"""
    try:
        import matplotlib
        # Dynamic import to avoid VS Code warnings
        import importlib.util
        mplfinance_spec = importlib.util.find_spec('mplfinance')
        if mplfinance_spec is None:
            raise ImportError("mplfinance not found")
        # Test actual import
        mplfinance = importlib.util.module_from_spec(mplfinance_spec)
        mplfinance_spec.loader.exec_module(mplfinance)  # type: ignore
        return True, None
    except ImportError as e:
        return False, str(e)

def install_core_requirements():
    """Install core required packages"""
    packages = ['MetaTrader5>=5.0.45', 'pandas>=1.5.0', 'numpy>=1.24.0']
    
    print("📦 Installing core dependencies...")
    
    for package in packages:
        try:
            print(f"  Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"  ✅ {package} installed")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to install {package}: {e}")
            return False
    
    return True

def install_chart_requirements():
    """Install charting packages"""
    packages = ['matplotlib>=3.5.0', 'mplfinance>=0.12.0']
    
    print("🎨 Installing charting libraries...")
    
    for package in packages:
        try:
            print(f"  Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"  ✅ {package} installed")
        except subprocess.CalledProcessError as e:
            print(f"  ⚠️ Warning: Could not install {package}")
            print("     Charts will be disabled")
    
    return True

def setup_environment():
    """Setup the environment and dependencies"""
    print("🚀 Advanced MT5 Trading Monitor Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('advanced_mt5_monitor_gui.py'):
        print("❌ Error: Please run this script from the mt5_live_trading_bot directory")
        print("   Expected file: advanced_mt5_monitor_gui.py")
        return False
    
    # Check core requirements
    core_ok, core_error = check_core_requirements()
    if not core_ok:
        print(f"⚠️ Missing core dependencies: {core_error}")
        
        root = tk.Tk()
        root.withdraw()
        result = messagebox.askyesno(
            "Install Dependencies",
            "Core dependencies are missing (MetaTrader5, pandas, numpy).\n\n"
            "Install them now?"
        )
        root.destroy()
        
        if result:
            if not install_core_requirements():
                print("❌ Failed to install core dependencies")
                return False
        else:
            print("❌ Core dependencies are required to run the monitor")
            return False
    
    print("✅ Core dependencies OK")
    
    # Check chart requirements
    chart_ok, chart_error = check_chart_requirements()
    if not chart_ok:
        print(f"⚠️ Missing chart libraries: {chart_error}")
        
        root = tk.Tk()
        root.withdraw()
        result = messagebox.askyesno(
            "Install Chart Libraries",
            "Chart libraries are missing (matplotlib, mplfinance).\n\n"
            "These enable live candlestick charts with indicators.\n"
            "The monitor will work without them but charts will be disabled.\n\n"
            "Install chart libraries?"
        )
        root.destroy()
        
        if result:
            install_chart_requirements()
        else:
            print("⚠️ Charts will be disabled")
    else:
        print("✅ Chart libraries OK")
    
    # Check strategy files
    strategies_dir = 'strategies'
    if not os.path.exists(strategies_dir):
        print(f"⚠️ Strategies directory not found: {strategies_dir}")
        print("   Strategy configuration viewing will be limited")
    else:
        strategy_files = [f for f in os.listdir(strategies_dir) if f.endswith('.py')]
        print(f"✅ Found {len(strategy_files)} strategy files")
        
        for file in strategy_files:
            symbol = file.replace('sunrise_ogle_', '').replace('.py', '').upper()
            print(f"   📈 {symbol}")
    
    return True

def main():
    """Main launcher"""
    print()
    
    # Setup environment
    if not setup_environment():
        input("\nPress Enter to exit...")
        return
    
    print("\n" + "=" * 50)
    print("🎯 Launching Advanced MT5 Trading Monitor...")
    print("=" * 50)
    
    try:
        # Import and run the advanced GUI
        sys.path.insert(0, os.getcwd())
        import advanced_mt5_monitor_gui
        
        print("✅ Advanced GUI module loaded")
        print("📊 Starting strategy phase monitoring...")
        print("\nFeatures enabled:")
        
        # Check what features are available
        try:
            import matplotlib
            print("   ✅ Live candlestick charts")
            print("   ✅ Technical indicator overlay") 
            print("   ✅ Strategy phase visualization")
        except ImportError:
            print("   ⚠️ Charts disabled (matplotlib not available)")
            
        print("   ✅ Real-time strategy phase tracking")
        print("   ✅ Configuration parameter viewer")
        print("   ✅ Terminal-style phase output")
        print("   ✅ Window breakout level monitoring")
        
        print("\nStarting GUI...")
        advanced_mt5_monitor_gui.main()
        
    except KeyboardInterrupt:
        print("\n⚠️ Startup cancelled by user")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Please ensure all required files are present")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"❌ Error starting advanced GUI: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()