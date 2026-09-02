#!/usr/bin/env python3
"""loop_checks.py — audit-plan's door into `loop` (TINK F635, R-loop).

`import::` on a ruleset names a Python FILE; `loop` beside this one is
extensionless (like `stone` and `state`), which `spec_from_file_location`
refuses to load. This module loads it the way `loop` loads `stone` and
re-exports its CHECKERS. Nothing is defined here — the checkers, and the
`check_stone` pass they partition, live in `loop`.
"""
import importlib.machinery
import importlib.util
import sys
from pathlib import Path

_path = Path(__file__).resolve().parent / "loop"
if "loop_mod" in sys.modules:
    _mod = sys.modules["loop_mod"]
else:
    _loader = importlib.machinery.SourceFileLoader("loop_mod", str(_path))
    _spec = importlib.util.spec_from_loader("loop_mod", _loader)
    _mod = importlib.util.module_from_spec(_spec)
    sys.modules["loop_mod"] = _mod
    _loader.exec_module(_mod)

CHECKERS = _mod.CHECKERS
