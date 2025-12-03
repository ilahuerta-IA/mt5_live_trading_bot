#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script: JPY Pairs Entry Test
=================================
Simple script to test opening LONG positions on EURJPY and USDJPY
with Stop Loss and Take Profit, using coherent lot sizes.

Broker Specifications (from attached images):
---------------------------------------------
USDJPY:
  - Contract Size: 100,000 USD
  - Precision: 3 decimals
  - Spread: Floating
  - Min Volume: 0.01
  - Max Volume: 50
  - Volume Step: 0.01
  - Margin Currency: USD
  - Profit Currency: JPY

EURJPY:
  - Contract Size: 100,000 EUR
  - Precision: 3 decimals
  - Spread: Floating
  - Min Volume: 0.01
  - Max Volume: 50
  - Volume Step: 0.01
  - Margin Currency: EUR
  - Profit Currency: JPY

USAGE:
------
1. Ensure MT5 terminal is running and logged in
2. Run this script: python test_jpy_entries.py
3. Follow the prompts to test entries

DISCLAIMER: This is for DEMO TESTING ONLY!
"""

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
from typing import Dict, Tuple, Optional
import time


# =============================================================
# CONFIGURATION
# =============================================================

# Risk settings
RISK_PERCENT = 0.01  # 1% of balance per trade
DEFAULT_ATR_MULTIPLIER_SL = 2.5  # Stop loss = ATR * 2.5
DEFAULT_ATR_MULTIPLIER_TP = 6.5  # Take profit = ATR * 6.5

# JPY Pair configurations
JPY_PAIRS_CONFIG = {
    'EURJPY': {
        'pip_value': 0.01,           # 1 pip = 0.01 (3 decimal places)
        'contract_size': 100000,     # 100,000 EUR
        'margin_currency': 'EUR',
        'profit_currency': 'JPY',
        'typical_atr_pips': 15,      # Typical ATR in pips for position sizing
        'angle_scale_factor': 100.0, # Scale factor for JPY pairs
    },
    'USDJPY': {
        'pip_value': 0.01,           # 1 pip = 0.01 (3 decimal places)
        'contract_size': 100000,     # 100,000 USD
        'margin_currency': 'USD',
        'profit_currency': 'JPY',
        'typical_atr_pips': 12,      # Typical ATR in pips for position sizing
        'angle_scale_factor': 100.0, # Scale factor for JPY pairs
    }
}


# =============================================================
# MT5 CONNECTION
# =============================================================

def connect_mt5() -> bool:
    """Initialize and connect to MT5 terminal"""
    print("=" * 60)
    print("🔌 Connecting to MetaTrader 5...")
    print("=" * 60)
    
    if not mt5.initialize():
        print(f"❌ Failed to initialize MT5: {mt5.last_error()}")
        return False
    
    # Get account info
    account = mt5.account_info()
    if account is None:
        print(f"❌ Failed to get account info: {mt5.last_error()}")
        mt5.shutdown()
        return False
    
    print(f"✅ Connected to MT5")
    print(f"   Account: {account.login}")
    print(f"   Server: {account.server}")
    print(f"   Balance: {account.balance:.2f} {account.currency}")
    print(f"   Equity: {account.equity:.2f} {account.currency}")
    print(f"   Leverage: 1:{account.leverage}")
    print(f"   Trade Mode: {'DEMO' if account.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO else 'REAL'}")
    
    # Safety check - only allow demo for testing (non-interactive)
    if account.trade_mode != mt5.ACCOUNT_TRADE_MODE_DEMO:
        print("\n⚠️  WARNING: This is a REAL account! Script requires DEMO for safety.")
        mt5.shutdown()
        return False
    
    print("")
    return True


def get_symbol_info(symbol: str) -> Optional[Dict]:
    """Get detailed symbol information from broker"""
    info = mt5.symbol_info(symbol)
    if info is None:
        print(f"❌ Symbol {symbol} not found. Error: {mt5.last_error()}")
        return None
    
    # Enable symbol for trading if not visible
    if not info.visible:
        if not mt5.symbol_select(symbol, True):
            print(f"❌ Failed to select {symbol}")
            return None
    
    return {
        'symbol': symbol,
        'bid': info.bid,
        'ask': info.ask,
        'spread': info.spread,
        'spread_pips': info.spread * info.point / 0.01,  # Convert to pips for JPY
        'digits': info.digits,
        'point': info.point,
        'volume_min': info.volume_min,
        'volume_max': info.volume_max,
        'volume_step': info.volume_step,
        'trade_contract_size': info.trade_contract_size,
        'margin_initial': info.margin_initial,
    }


def calculate_atr(symbol: str, period: int = 14, timeframe=mt5.TIMEFRAME_M5) -> float:
    """Calculate ATR (Average True Range) for position sizing"""
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, period + 1)
    if rates is None or len(rates) < period + 1:
        print(f"⚠️  Could not get rates for {symbol}, using default ATR")
        return JPY_PAIRS_CONFIG.get(symbol, {}).get('typical_atr_pips', 15) * 0.01
    
    df = pd.DataFrame(rates)
    
    # Calculate True Range
    df['high_low'] = df['high'] - df['low']
    df['high_close'] = abs(df['high'] - df['close'].shift(1))
    df['low_close'] = abs(df['low'] - df['close'].shift(1))
    df['true_range'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
    
    # Calculate ATR
    atr = df['true_range'].iloc[-period:].mean()
    
    return atr


def calculate_lot_size(symbol: str, balance: float, risk_percent: float, 
                       sl_distance: float, current_price: float) -> Tuple[float, float]:
    """
    Calculate lot size based on risk management for JPY pairs.
    
    For JPY pairs (3 decimal places):
    - 1 pip = 0.01 (e.g., 155.88 to 155.89 = 1 pip)
    - Pip value per standard lot (100,000 units) = 100,000 × 0.01 / rate
    - Example USDJPY at 155.00: pip value = 1000 JPY = ~$6.45/pip per lot
    
    Formula:
    Risk Amount = Balance × Risk%
    Lot Size = Risk Amount / (SL in pips × Pip Value per lot)
    
    Returns:
        Tuple of (lot_size, pip_value_per_lot)
    """
    symbol_info = mt5.symbol_info(symbol)
    account_info = mt5.account_info()
    
    if symbol_info is None or account_info is None:
        print(f"❌ Could not get info for {symbol}")
        return (symbol_info.volume_min if symbol_info else 0.01, 0.0)
    
    # Calculate risk amount in account currency (USD)
    risk_amount = balance * risk_percent
    
    # Calculate SL distance in pips (for JPY: 1 pip = 0.01)
    sl_pips = sl_distance / 0.01
    
    # Contract size
    contract_size = symbol_info.trade_contract_size  # 100,000
    
    # For JPY pairs, pip value calculation:
    # 1 pip move = 0.01 price change
    # Value per pip per lot = (contract_size × 0.01) / current_price
    # This gives value in USD directly for USDJPY
    
    if symbol == 'USDJPY':
        # Direct calculation: (100,000 × 0.01) / USDJPY = USD per pip per lot
        pip_value_per_lot = (contract_size * 0.01) / current_price
        
    elif symbol == 'EURJPY':
        # For EURJPY: value is in JPY, need to convert to USD
        # (100,000 EUR × 0.01 JPY) = 1000 JPY per pip per lot
        # Convert JPY to USD: 1000 JPY / USDJPY rate
        usdjpy_info = mt5.symbol_info_tick('USDJPY')
        if usdjpy_info:
            jpy_usd_rate = 1 / usdjpy_info.bid  # How much USD per JPY
            pip_value_jpy = contract_size * 0.01  # 1000 JPY per pip per lot
            pip_value_per_lot = pip_value_jpy * jpy_usd_rate
        else:
            # Fallback estimate (assume USDJPY ~155)
            pip_value_per_lot = (contract_size * 0.01) / 155.0
    else:
        # Generic JPY pair calculation (assume quote is JPY)
        pip_value_per_lot = (contract_size * 0.01) / current_price
    
    # Calculate lot size
    if sl_pips > 0 and pip_value_per_lot > 0:
        lot_size = risk_amount / (sl_pips * pip_value_per_lot)
    else:
        lot_size = symbol_info.volume_min
    
    # Store uncapped value for reporting
    raw_lot_size = lot_size
    
    # Apply limits
    lot_size = max(lot_size, symbol_info.volume_min)
    lot_size = min(lot_size, symbol_info.volume_max)
    lot_size = min(lot_size, 0.10)  # Safety cap for testing: 0.10 lots max
    
    # Round to volume step
    volume_step = symbol_info.volume_step
    lot_size = round(lot_size / volume_step) * volume_step
    
    # Ensure minimum
    lot_size = max(lot_size, symbol_info.volume_min)
    
    return (lot_size, pip_value_per_lot)


def print_symbol_details(symbol: str):
    """Print detailed information about a symbol"""
    info = get_symbol_info(symbol)
    if info is None:
        return
    
    atr = calculate_atr(symbol)
    atr_pips = atr / 0.01
    
    config = JPY_PAIRS_CONFIG.get(symbol, {})
    
    print(f"\n{'='*60}")
    print(f"📊 {symbol} - Symbol Details")
    print(f"{'='*60}")
    print(f"   Current Bid: {info['bid']:.3f}")
    print(f"   Current Ask: {info['ask']:.3f}")
    print(f"   Spread: {info['spread']} points ({info['spread_pips']:.1f} pips)")
    print(f"   Digits: {info['digits']}")
    print(f"   Point: {info['point']}")
    print(f"   Contract Size: {info['trade_contract_size']:,.0f}")
    print(f"   Volume Min: {info['volume_min']}")
    print(f"   Volume Max: {info['volume_max']}")
    print(f"   Volume Step: {info['volume_step']}")
    print(f"   ATR(14): {atr:.5f} ({atr_pips:.1f} pips)")
    print(f"   Margin Currency: {config.get('margin_currency', 'N/A')}")
    print(f"   Profit Currency: {config.get('profit_currency', 'N/A')}")


def calculate_sl_tp(symbol: str, entry_price: float, direction: str, 
                    atr: float, sl_mult: float = 2.5, tp_mult: float = 6.5) -> Tuple[float, float]:
    """
    Calculate Stop Loss and Take Profit levels based on ATR.
    
    Args:
        symbol: Trading symbol
        entry_price: Entry price
        direction: 'LONG' or 'SHORT'
        atr: Current ATR value
        sl_mult: ATR multiplier for stop loss
        tp_mult: ATR multiplier for take profit
    
    Returns:
        Tuple of (stop_loss, take_profit)
    """
    symbol_info = mt5.symbol_info(symbol)
    digits = symbol_info.digits if symbol_info else 3
    
    sl_distance = atr * sl_mult
    tp_distance = atr * tp_mult
    
    if direction == 'LONG':
        stop_loss = round(entry_price - sl_distance, digits)
        take_profit = round(entry_price + tp_distance, digits)
    else:  # SHORT
        stop_loss = round(entry_price + sl_distance, digits)
        take_profit = round(entry_price - tp_distance, digits)
    
    return stop_loss, take_profit


def open_long_position(symbol: str, volume: float, sl: float, tp: float, 
                       comment: str = "Test JPY Entry") -> bool:
    """
    Open a LONG position with Stop Loss and Take Profit.
    
    Args:
        symbol: Trading symbol (EURJPY or USDJPY)
        volume: Lot size
        sl: Stop Loss price
        tp: Take Profit price
        comment: Order comment
    
    Returns:
        True if order placed successfully, False otherwise
    """
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"❌ Symbol {symbol} not found")
        return False
    
    # Get current ask price for LONG entry
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        print(f"❌ Could not get tick for {symbol}")
        return False
    
    price = tick.ask
    
    # Prepare the trade request
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,  # Slippage in points
        "magic": 123456,  # Magic number for identification
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    # Print order details before sending
    print(f"\n{'='*60}")
    print(f"📤 Sending LONG Order for {symbol}")
    print(f"{'='*60}")
    print(f"   Entry Price: {price:.3f}")
    print(f"   Volume: {volume:.2f} lots")
    print(f"   Stop Loss: {sl:.3f} ({(price - sl) / 0.01:.1f} pips)")
    print(f"   Take Profit: {tp:.3f} ({(tp - price) / 0.01:.1f} pips)")
    print(f"   Risk/Reward: 1:{(tp - price) / (price - sl):.1f}")
    
    # Send the order
    result = mt5.order_send(request)
    
    if result is None:
        print(f"❌ Order send failed: {mt5.last_error()}")
        return False
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"❌ Order failed: {result.retcode} - {result.comment}")
        return False
    
    print(f"\n✅ Order Executed Successfully!")
    print(f"   Order ID: {result.order}")
    print(f"   Deal ID: {result.deal}")
    print(f"   Volume: {result.volume}")
    print(f"   Price: {result.price:.3f}")
    
    return True


def test_entry_for_symbol(symbol: str, execute: bool = False):
    """
    Test entry calculation for a JPY symbol.
    
    Args:
        symbol: Trading symbol
        execute: If True, actually execute the trade (CAREFUL!)
    """
    print(f"\n{'='*60}")
    print(f"🎯 Testing LONG Entry for {symbol}")
    print(f"{'='*60}")
    
    # Get symbol info
    info = get_symbol_info(symbol)
    if info is None:
        return
    
    # Get account balance
    account = mt5.account_info()
    if account is None:
        print("❌ Could not get account info")
        return
    
    balance = account.balance
    
    # Calculate ATR
    atr = calculate_atr(symbol)
    atr_pips = atr / 0.01
    
    # Entry price (ask for LONG)
    entry_price = info['ask']
    
    # Calculate SL/TP
    sl, tp = calculate_sl_tp(symbol, entry_price, 'LONG', atr, 
                              DEFAULT_ATR_MULTIPLIER_SL, DEFAULT_ATR_MULTIPLIER_TP)
    
    sl_distance = entry_price - sl
    tp_distance = tp - entry_price
    
    # Calculate lot size
    lot_size, pip_value_per_lot = calculate_lot_size(symbol, balance, RISK_PERCENT, sl_distance, entry_price)
    
    # Print calculation details
    print(f"\n📐 Position Sizing Calculation:")
    print(f"   Account Balance: {balance:.2f} {account.currency}")
    print(f"   Risk Percent: {RISK_PERCENT * 100:.1f}%")
    print(f"   Risk Amount: {balance * RISK_PERCENT:.2f} {account.currency}")
    print(f"   ATR(14): {atr:.5f} ({atr_pips:.1f} pips)")
    print(f"   SL Multiplier: {DEFAULT_ATR_MULTIPLIER_SL}x ATR")
    print(f"   TP Multiplier: {DEFAULT_ATR_MULTIPLIER_TP}x ATR")
    print(f"   Pip Value: ${pip_value_per_lot:.4f} per lot per pip")
    
    print(f"\n📍 Entry Levels:")
    print(f"   Entry Price: {entry_price:.3f}")
    print(f"   Stop Loss: {sl:.3f} ({sl_distance / 0.01:.1f} pips away)")
    print(f"   Take Profit: {tp:.3f} ({tp_distance / 0.01:.1f} pips away)")
    print(f"   Risk/Reward: 1:{tp_distance / sl_distance:.1f}")
    
    print(f"\n📦 Position Size:")
    print(f"   Calculated Lots: {lot_size:.2f}")
    print(f"   Min Allowed: {info['volume_min']}")
    print(f"   Max Allowed: {info['volume_max']}")
    print(f"   Volume Step: {info['volume_step']}")
    
    # Estimate profit/loss in account currency using ACTUAL lot size
    sl_pips = sl_distance / 0.01
    tp_pips = tp_distance / 0.01
    
    potential_loss = sl_pips * pip_value_per_lot * lot_size
    potential_profit = tp_pips * pip_value_per_lot * lot_size
    
    print(f"\n💰 Potential Outcome:")
    print(f"   Max Loss: -{potential_loss:.2f} {account.currency}")
    print(f"   Max Profit: +{potential_profit:.2f} {account.currency}")
    
    if execute:
        print(f"\n⚠️  READY TO EXECUTE TRADE")
        print(f"   Run with --execute --symbol {symbol} to place this trade")
        success = open_long_position(symbol, lot_size, sl, tp, f"Test_{symbol}_Long")
        return success
    else:
        print(f"\n📝 DRY RUN - No trade executed")
        print(f"   To execute, run: python test_jpy_entries.py --execute --symbol {symbol}")
    
    return True


def main(dry_run: bool = True, symbol: str = None):
    """
    Main function to run the test.
    
    Args:
        dry_run: If True, only show calculations without executing trades
        symbol: Specific symbol to test ('EURJPY', 'USDJPY', or None for both)
    """
    print("\n" + "=" * 60)
    print("🧪 JPY PAIRS ENTRY TEST SCRIPT")
    print("=" * 60)
    print("This script tests LONG entries on EURJPY and USDJPY")
    print("with proper lot sizing, stop loss, and take profit.")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
    print("=" * 60 + "\n")
    
    # Connect to MT5
    if not connect_mt5():
        return
    
    symbols_to_test = ['EURJPY', 'USDJPY'] if symbol is None else [symbol]
    
    try:
        # Print details for symbols
        for sym in symbols_to_test:
            print_symbol_details(sym)
        
        # Test entry calculations
        print("\n" + "=" * 60)
        print(f"📋 {'DRY RUN' if dry_run else 'LIVE'} - Testing Entry Calculations")
        print("=" * 60)
        
        for sym in symbols_to_test:
            test_entry_for_symbol(sym, execute=not dry_run)
        
        if dry_run:
            print("\n✅ DRY RUN completed (no trades executed)")
            print("\nTo execute real trades, run:")
            print("  main(dry_run=False)  # Both symbols")
            print("  main(dry_run=False, symbol='EURJPY')  # Only EURJPY")
            print("  main(dry_run=False, symbol='USDJPY')  # Only USDJPY")
    
    finally:
        # Disconnect from MT5
        mt5.shutdown()
        print("\n🔌 Disconnected from MT5")


if __name__ == "__main__":
    import sys
    # Default: DRY RUN mode
    # Pass --execute to actually place trades
    # Pass --symbol EURJPY or --symbol USDJPY for specific symbol
    
    dry_run = True
    symbol = None
    
    args = sys.argv[1:]
    if '--execute' in args:
        dry_run = False
        args.remove('--execute')
    
    if '--symbol' in args:
        idx = args.index('--symbol')
        if idx + 1 < len(args):
            symbol = args[idx + 1].upper()
    
    main(dry_run=dry_run, symbol=symbol)
