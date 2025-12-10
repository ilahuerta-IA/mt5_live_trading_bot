import re

with open('advanced_mt5_monitor_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replacements for chart display bars (100 bars)
content = content.replace("df.tail(100),  # Show last 100 bars in chart", "df.tail(CHART_DISPLAY_BARS),  # Show last bars in chart")
content = content.replace("df.tail(100),  # Show last 100 bars (much better zoom level)", "df.tail(CHART_DISPLAY_BARS),  # Show last bars (much better zoom level)")

# Replacements for MIN_BARS checks
content = content.replace('if len(rates) < 100:', 'if len(rates) < MIN_BARS_REQUIRED:')
content = content.replace('if len(df) < 100:  # Verify we still have enough data after removal', 'if len(df) < MIN_BARS_REQUIRED:  # Verify we still have enough data after removal')

# Fix the error message - use f-string properly
content = content.replace(
    'bars, need 100+"',
    'bars, need {MIN_BARS_REQUIRED}+"'
)

with open('advanced_mt5_monitor_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Replaced 100 bar references with constants')
