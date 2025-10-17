#!/usr/bin/env python3
"""Fix syntax error in comprehensive_quantitative_analyst.py by removing malformed section"""

file_path = r"tradingagents\agents\analysts\comprehensive_quantitative_analyst.py"

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines before: {len(lines)}")

# Delete lines 868-1051 (Python uses 0-indexing, so indices 867-1050)
# Line 868 starts with "# These helper functions..."
# Line 1051 ends the malformed section
new_lines = lines[:867] + lines[1051:]

print(f"Total lines after: {len(new_lines)}")
print(f"Deleted {len(lines) - len(new_lines)} lines")

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✓ Fixed syntax error successfully!")
