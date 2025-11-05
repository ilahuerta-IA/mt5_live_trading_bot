"""
COMPREHENSIVE FILTER AUDIT - ALL 6 ASSETS
==========================================
This script audits ALL filter configurations for each asset to ensure compliance.
"""

import os
import re

ASSETS = ['EURUSD', 'GBPUSD', 'XAUUSD', 'AUDUSD', 'XAGUSD', 'USDCHF']

FILTERS_TO_CHECK = {
    # ATR Filters
    'LONG_USE_ATR_FILTER': ('ATR Filter Enabled', 'bool'),
    'LONG_ATR_MIN_THRESHOLD': ('ATR Min', 'float'),
    'LONG_ATR_MAX_THRESHOLD': ('ATR Max', 'float'),
    'LONG_USE_ATR_INCREMENT_FILTER': ('ATR Increment Filter', 'bool'),
    'LONG_ATR_INCREMENT_MIN_THRESHOLD': ('ATR Incr Min', 'float'),
    'LONG_ATR_INCREMENT_MAX_THRESHOLD': ('ATR Incr Max', 'float'),
    'LONG_USE_ATR_DECREMENT_FILTER': ('ATR Decrement Filter', 'bool'),
    'LONG_ATR_DECREMENT_MIN_THRESHOLD': ('ATR Decr Min', 'float'),
    'LONG_ATR_DECREMENT_MAX_THRESHOLD': ('ATR Decr Max', 'float'),
    
    # Angle Filter
    'LONG_USE_ANGLE_FILTER': ('Angle Filter Enabled', 'bool'),
    'LONG_MIN_ANGLE': ('Min Angle (°)', 'float'),
    'LONG_MAX_ANGLE': ('Max Angle (°)', 'float'),
    'LONG_ANGLE_SCALE_FACTOR': ('Angle Scale Factor', 'float'),
    
    # Price Filter
    'LONG_USE_PRICE_FILTER_EMA': ('Price Filter EMA Enabled', 'bool'),
    
    # Candle Direction
    'LONG_USE_CANDLE_DIRECTION_FILTER': ('Candle Direction Filter', 'bool'),
    
    # EMA Ordering
    'LONG_USE_EMA_ORDER_CONDITION': ('EMA Ordering Filter', 'bool'),
    
    # Time Filter
    'USE_TIME_RANGE_FILTER': ('Time Range Filter', 'bool'),
    'ENTRY_START_HOUR': ('Start Hour (UTC)', 'int'),
    'ENTRY_END_HOUR': ('End Hour (UTC)', 'int'),
    
    # Pullback Entry
    'LONG_USE_PULLBACK_ENTRY': ('Pullback Entry System', 'bool'),
    'LONG_PULLBACK_MAX_CANDLES': ('Pullback Candles', 'int'),
    'LONG_ENTRY_WINDOW_PERIODS': ('Window Periods', 'int'),
    'USE_WINDOW_TIME_OFFSET': ('Window Time Offset', 'bool'),
    'WINDOW_OFFSET_MULTIPLIER': ('Window Offset Multiplier', 'float'),
    'WINDOW_PRICE_OFFSET_MULTIPLIER': ('Window Price Offset', 'float'),
}

def extract_value(content, param_name):
    """Extract parameter value from strategy file"""
    pattern = rf'^{param_name}\s*=\s*(.+?)(?:#|$)'
    match = re.search(pattern, content, re.MULTILINE)
    if match:
        value = match.group(1).strip().rstrip(',').strip()
        # Remove quotes
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        return value
    return 'NOT FOUND'

def main():
    print("=" * 120)
    print("COMPREHENSIVE FILTER CONFIGURATION AUDIT - ALL 6 ASSETS")
    print("=" * 120)
    print("\nThis audit checks ALL filter configurations to ensure proper setup.")
    print("\n")
    
    all_configs = {}
    
    # Read all strategy files
    for asset in ASSETS:
        filepath = f"strategies/sunrise_ogle_{asset.lower()}.py"
        if not os.path.exists(filepath):
            print(f"❌ {asset}: Strategy file not found!")
            continue
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        config = {}
        for param, (desc, dtype) in FILTERS_TO_CHECK.items():
            value = extract_value(content, param)
            config[param] = value
        
        all_configs[asset] = config
        print(f"✅ {asset}: Configuration loaded ({len(config)} parameters)")
    
    # Generate detailed report
    print("\n" + "=" * 120)
    print("FILTER CONFIGURATION TABLE")
    print("=" * 120)
    
    for param, (desc, dtype) in FILTERS_TO_CHECK.items():
        print(f"\n📋 {desc} ({param}):")
        print("-" * 100)
        for asset in ASSETS:
            value = all_configs.get(asset, {}).get(param, 'N/A')
            status = "✅" if value != 'NOT FOUND' else "❌"
            print(f"  {status} {asset:8s}: {value}")
    
    # Critical issues check
    print("\n" + "=" * 120)
    print("CRITICAL ISSUES CHECK")
    print("=" * 120)
    
    issues = []
    
    for asset in ASSETS:
        config = all_configs.get(asset, {})
        
        # Check 1: ATR Filter must be enabled
        if config.get('LONG_USE_ATR_FILTER') != 'True':
            issues.append(f"⚠️  {asset}: ATR Filter is DISABLED (should be enabled)")
        
        # Check 2: If ATR filter enabled, check thresholds
        elif config.get('LONG_USE_ATR_FILTER') == 'True':
            min_val = config.get('LONG_ATR_MIN_THRESHOLD')
            max_val = config.get('LONG_ATR_MAX_THRESHOLD')
            if min_val == 'NOT FOUND' or max_val == 'NOT FOUND':
                issues.append(f"❌ {asset}: ATR thresholds are missing!")
        
        # Check 3: Angle filter check
        if config.get('LONG_USE_ANGLE_FILTER') == 'True':
            min_angle = config.get('LONG_MIN_ANGLE')
            max_angle = config.get('LONG_MAX_ANGLE')
            if min_angle == 'NOT FOUND' or max_angle == 'NOT FOUND':
                issues.append(f"❌ {asset}: Angle filter enabled but thresholds missing!")
        
        # Check 4: Pullback entry check
        if config.get('LONG_USE_PULLBACK_ENTRY') != 'True':
            issues.append(f"⚠️  {asset}: Pullback entry system is DISABLED")
        
        # Check 5: Window offset check (should be 0.001, not 0.5)
        offset = config.get('WINDOW_PRICE_OFFSET_MULTIPLIER')
        if offset and offset != '0.001':
            issues.append(f"⚠️  {asset}: Window price offset is {offset} (should be 0.001)")
    
    if issues:
        print(f"\n🚨 Found {len(issues)} potential issues:\n")
        for issue in issues:
            print(issue)
    else:
        print("\n✅ No critical issues found!")
    
    print("\n" + "=" * 120)
    print("AUDIT COMPLETE")
    print("=" * 120)

if __name__ == '__main__':
    main()
