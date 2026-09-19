"""
paths.py

Resolves where user-writable files (config.json, verification.db) live.

In development, that's next to the source files — same as before. In a
PyInstaller-frozen .exe, the source directory is a temp extraction folder
(onefile) or may be installed somewhere non-writable (Program Files), so
writable data moves to a per-user AppData folder instead. Every module
that used to hardcode os.path.dirname(__file__) for a writable file
should go through app_data_dir() instead.
"""

import os
import sys


def app_data_dir() -> str:
    if getattr(sys, "frozen", False):
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        path = os.path.join(base, "LedgerLens")
    else:
        path = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(path, exist_ok=True)
    return path
