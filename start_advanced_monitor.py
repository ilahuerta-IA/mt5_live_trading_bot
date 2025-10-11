#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Advanced Monitor Launcher
Simple launcher that runs the advanced monitor without complex dependency checking
"""

import os
import sys

def main():
    """Quick launcher"""
    print("🚀 Starting Advanced MT5 Trading Monitor...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('advanced_mt5_monitor_gui.py'):
        print("❌ Error: Please run this script from the mt5_live_trading_bot directory")
        print("   Expected file: advanced_mt5_monitor_gui.py")
        return
    
    print("📊 Features:")
    print("   ✅ Real-time strategy phase tracking")
    print("   ✅ Configuration parameter viewer")
    print("   ✅ Terminal-style phase output") 
    print("   ✅ Window breakout level monitoring")
    print("   ✅ Technical indicators display")
    print("   ⚠️ Charts available if matplotlib is installed")
    
    try:
        # Import and run the advanced GUI
        print("\n🎯 Launching advanced GUI...")
        import advanced_mt5_monitor_gui
        advanced_mt5_monitor_gui.main()
        
    except Exception as e:
        print(f"❌ Error starting advanced GUI: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()