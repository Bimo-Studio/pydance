#!/usr/bin/env python3
"""One-off maintenance: insert stdlib logging + logger into each module (see log_config.py)."""

from __future__ import annotations

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKIP_DIRS = frozenset({"backup_fixes", ".venv", "__pycache__"})
SKIP_FILES = frozenset(
    {
        "log_config.py",
        "inject_module_loggers.py",
    }
)
MARKER = "logger = logging.getLogger(__name__)"


def preamble_end(lines: list[str]) -> int:
    """Return index of first line after shebang, encoding, __future__, module docstring."""
    i = 0
    n = len(lines)
    if i < n and lines[i].startswith("#!"):
        i += 1
    while i < n and lines[i].strip() == "":
        i += 1
    if i < n and "coding" in lines[i] and lines[i].lstrip().startswith("#"):
        i += 1
        while i < n and lines[i].strip() == "":
            i += 1
    while i < n and lines[i].strip().startswith("from __future__"):
        i += 1
        while i < n and lines[i].strip() == "":
            i += 1
    if i >= n:
        return i
    s = lines[i].strip()
    if s.startswith('"""') or s.startswith("'''"):
        delim = '"""' if s.startswith('"""') else "'''"
        if s.count(delim) >= 2:
            i += 1
        else:
            i += 1
            while i < n and delim not in lines[i]:
                i += 1
            if i < n:
                i += 1
    while i < n and lines[i].strip() == "":
        i += 1
    return i


def insert_logging_block(text: str) -> str | None:
    if MARKER in text or "logging.getLogger(__name__)" in text:
        return None
    lines = text.splitlines(keepends=True)
    j = preamble_end(lines)
    block = "import logging\n\n" + MARKER + "\n\n"
    return "".join(lines[:j]) + block + "".join(lines[j:])


def main() -> int:
    changed = 0
    for path in sorted(ROOT.rglob("*.py")):
        rel = path.relative_to(ROOT)
        if any(p in SKIP_DIRS for p in rel.parts):
            continue
        if path.name in SKIP_FILES:
            continue
        if path.name == "constants.py":
            continue
        text = path.read_text(encoding="utf-8")
        new = insert_logging_block(text)
        if new is None:
            continue
        path.write_text(new, encoding="utf-8")
        print("updated", rel)
        changed += 1
    print("done,", changed, "files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
