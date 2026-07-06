"""Exit 0 if running Python is 3.10+, else 1. Used by start/*.bat to avoid () in CMD."""
import sys

v = sys.version_info
ok = v.major > 3 or (v.major == 3 and v.minor >= 10)
raise SystemExit(0 if ok else 1)
