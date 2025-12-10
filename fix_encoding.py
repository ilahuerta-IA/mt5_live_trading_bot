#!/usr/bin/env python3
"""Fix encoding issues - ONLY in comments, preserve code strings"""
import re

def fix_comments_only():
    with open('advanced_mt5_monitor_gui.py', 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    
    fixed = 0
    for i, line in enumerate(lines):
        # Only fix lines that are comments (start with #, possibly indented)
        stripped = line.lstrip()
        if stripped.startswith('#'):
            original = line
            
            # Fix separator lines (box drawing chars)
            if re.search(r'#\s*[^\x00-\x7F]{20,}', line):
                # Replace with clean separator
                indent = len(line) - len(stripped)
                lines[i] = ' ' * indent + '# ' + '=' * 67 + '\n'
                fixed += 1
            # Fix emoji prefixes in comments
            elif re.search(r'#\s*[^\x00-\x7F]{1,10}\s+[A-Z]', line):
                # Remove non-ASCII between # and first uppercase letter
                lines[i] = re.sub(r'(#\s*)[^\x00-\x7F]{1,10}\s+', r'\g<1>', line)
                fixed += 1
            # Fix multiplication sign
            elif '\xc3\x97' in line or '\xc3\x83' in line:
                lines[i] = line.replace('\xc3\x97', 'x').replace('\xc3\x83\xe2\x80\x94', 'x')
                fixed += 1
    
    with open('advanced_mt5_monitor_gui.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f'Fixed {fixed} comment lines')

if __name__ == '__main__':
    fix_comments_only()
