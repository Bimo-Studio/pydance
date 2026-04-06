#!/usr/bin/env python3
import logging

logger = logging.getLogger(__name__)

import glob

# List of files to fix (or we can fix all .py files)
files_to_fix = glob.glob("*.py")

for filename in files_to_fix:
    if filename == "fix_imports_correct.py":
        continue

    print(f"Processing: {filename}")

    # Read the file
    with open(filename) as f:
        lines = f.readlines()

    # Check if import already exists
    if any("from i18n import _" in line for line in lines):
        print("  Already has import, skipping")
        continue

    # Find where to insert the import
    insert_line = 0
    last_future_line = -1

    # Find the last __future__ import line
    for i, line in enumerate(lines):
        if line.startswith("from __future__"):
            last_future_line = i

    # If we found __future__ imports, insert right after the last one
    if last_future_line >= 0:
        insert_line = last_future_line + 1
        # Skip any blank lines after __future__ imports
        while insert_line < len(lines) and lines[insert_line].strip() == "":
            insert_line += 1
    else:
        # No __future__ imports, check for shebang
        if lines and lines[0].startswith("#!"):
            insert_line = 1  # After shebang
        else:
            insert_line = 0  # At the very beginning

    # Insert the import
    lines.insert(insert_line, "from i18n import _\n")

    # Write back
    with open(filename, "w") as f:
        f.writelines(lines)

    print(f"  Fixed! Added import at line {insert_line}")

print("\nDone! Check a few files to verify:")
print("head -10 dance.py")
