#!/usr/bin/env python3
import logging

logger = logging.getLogger(__name__)

import glob
import re


def fix_file(filename):
    """Fix common Python 2 to 3 issues in a file."""
    with open(filename) as f:
        content = f.read()

    original = content
    changes = []

    # 1. Fix 'is 0' comparisons (should be '== 0')
    if re.search(r"\bis\s+\d+", content):
        content = re.sub(r"\bis\s+(\d+)", r"== \1", content)
        changes.append("Fixed 'is N' comparisons")

    # 2. Remove dircache imports
    if "import dircache" in content or "from dircache" in content:
        content = re.sub(r"import dircache\n?", "", content)
        content = re.sub(r"from dircache import .*\n?", "", content)
        content = content.replace("dircache.", "os.")
        changes.append("Removed dircache (use os.listdir)")

    # 3. Fix except syntax (except Exception, e: -> except Exception as e:)
    if re.search(r"except\s+\w+\s*,\s*\w+\s*:", content):
        content = re.sub(r"except\s+(\w+)\s*,\s*(\w+)\s*:", r"except \1 as \2:", content)
        changes.append("Fixed except syntax")

    # 4. Fix print statements (add parentheses if missing)
    # Be careful with this one - only fix simple print statements
    lines = content.split("\n")
    fixed_lines = []
    for line in lines:
        if re.match(r"^print\s+[^(]", line) and "print(" not in line:
            # Convert 'print something' to 'print(something)'
            line = re.sub(r"^print\s+(.*)$", r"print(\1)", line)
            changes.append("Added parentheses to print")
        fixed_lines.append(line)
    content = "\n".join(fixed_lines)

    # 5. Fix 'rU' mode in open()
    if "rU" in content:
        content = content.replace('"rU"', "'r'")
        content = content.replace("'rU'", "'r'")
        changes.append("Fixed 'rU' file mode")

    # 6. Fix has_key() method
    if ".has_key(" in content:
        content = re.sub(r"(\w+)\.has_key\(([^)]+)\)", r"\2 in \1", content)
        changes.append("Fixed has_key()")

    # Write back if changes were made
    if content != original:
        with open(filename, "w") as f:
            f.write(content)
        if changes:
            print(f"Fixed {filename}: {', '.join(changes)}")
        return True
    return False


# Fix all Python files
py_files = glob.glob("*.py")
fixed_count = 0

for filename in py_files:
    if filename in ["fix_python3.py", "fix_imports_correct.py"]:
        continue
    if fix_file(filename):
        fixed_count += 1

print(f"\nFixed {fixed_count} files")
