#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced MT5 Trading Monitor V2 - Enhanced Launcher
Now with:
- Minimal terminal output (only critical events)
- Asset-specific EMA display on charts
- Real-time ATR SL/TP visualization
- EMA crossover detection and alerts
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
        import importlib.util
        mplfinance_spec = importlib.util.find_spec('mplfinance')
        if mplfinance_spec is None:
            raise ImportError("mplfinance not found")
        mplfinance = importlib.util.module_from_spec(mplfinance_spec)
        mplfinance_spec.loader.exec_module(mplfinance)
        return True, None
    except ImportError as e:
        return False, str(e)

def main():
    """Main launcher - minimal output"""
    print("\n🚀 Advanced MT5 Trading Monitor V2")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('advanced_mt5_monitor_gui.py'):
        print("❌ Error: Please run this script from the mt5_live_trading_bot directory")
        input("Press Enter to exit...")
        return
    
    # Silent dependency check
    core_ok, core_error = check_core_requirements()
    if not core_ok:
        print(f"❌ Missing core dependencies. Please install: pip install -r requirements.txt")
        input("Press Enter to exit...")
        return
    
    chart_ok, chart_error = check_chart_requirements()
    
    # Quick status
    print("✅ Bot ready - Starting monitor...")
    print("\n📊 Features enabled:")
    if chart_ok:
        print("   ✅ Live candlestick charts with asset-specific EMAs")
        print("   ✅ ATR-based SL/TP visualization")
        print("   ✅ EMA crossover detection")
    print("   ✅ Phase tracking (NORMAL → PULLBACK → BREAKOUT)")
    print("   ✅ Critical event alerts only")
    
    print("\n" + "=" * 50)
    print("🎯 Launching monitor...")
    print("=" * 50 + "\n")
    
    try:
        # Import and run the advanced GUI
        sys.path.insert(0, os.getcwd())
        import advanced_mt5_monitor_gui
        advanced_mt5_monitor_gui.main()
        
    except KeyboardInterrupt:
        print("\n⚠️ Startup cancelled by user")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
