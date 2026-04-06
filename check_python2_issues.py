import logging

logger = logging.getLogger(__name__)

import glob
import re
from typing import TypedDict


class IssueEntry(TypedDict):
    pattern: str
    message: str
    files: list[str]


issues: dict[str, IssueEntry] = {
    "print_statement": {
        "pattern": r"^print\s+[^(]",
        "message": "Python 2 print statement (should be print())",
        "files": [],
    },
    "except_comma": {
        "pattern": r"except\s+\w+\s*,\s*\w+\s*:",
        "message": 'Python 2 except syntax (use "as" instead of ",")',
        "files": [],
    },
    "has_key": {
        "pattern": r"\.has_key\(",
        "message": 'dict.has_key() (use "in" operator)',
        "files": [],
    },
    "cmp_usage": {
        "pattern": r"\bcmp\(",
        "message": "cmp() function (use key functions instead)",
        "files": [],
    },
    "unicode_literal": {
        "pattern": r"u'",
        "message": "Unicode literal (Python 3 strings are Unicode by default)",
        "files": [],
    },
    "cStringIO": {
        "pattern": r"cStringIO",
        "message": "cStringIO module (use io.BytesIO/StringIO)",
        "files": [],
    },
    "cPickle": {"pattern": r"cPickle", "message": "cPickle module (use pickle)", "files": []},
    "dircache": {
        "pattern": r"dircache",
        "message": "dircache module (use os.listdir)",
        "files": [],
    },
    "__dict__assign": {
        "pattern": r"__dict__\[",
        "message": "__dict__ assignment (use setattr for class __dict__)",
        "files": [],
    },
    "rU_mode": {
        "pattern": r'["\']rU["\']',
        "message": "'rU' file mode (use 'r' in Python 3)",
        "files": [],
    },
    "xrange": {
        "pattern": r"\bxrange\(",
        "message": "xrange() (use range() in Python 3)",
        "files": [],
    },
    "iteritems": {
        "pattern": r"\.iteritems\(\)",
        "message": "dict.iteritems() (use .items() in Python 3)",
        "files": [],
    },
}

for py_file in glob.glob("*.py"):
    if py_file in ["fix_python3.py", "check_python2_issues.py"]:
        continue

    with open(py_file) as f:
        try:
            content = f.read()
            for issue_name, issue_info in issues.items():
                if re.search(issue_info["pattern"], content, re.MULTILINE):
                    issue_info["files"].append(py_file)
        except Exception:
            print(f"Could not read {py_file}")

print("\n=== PYTHON 2 ISSUES FOUND ===")
for issue_name, issue_info in issues.items():
    if issue_info["files"]:
        print(f"\n{issue_info['message']}:")
        for fname in sorted(set(issue_info["files"])):
            print(f"  - {fname}")

# Also check for syntax errors
print("\n=== SYNTAX ERRORS ===")
for py_file in glob.glob("*.py"):
    if py_file in ["fix_python3.py", "check_python2_issues.py"]:
        continue
    try:
        with open(py_file) as f:
            compile(f.read(), py_file, "exec")
    except SyntaxError as e:
        print(f"{py_file}: Line {e.lineno}: {e.msg}")
