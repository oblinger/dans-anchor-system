"""warden_root — locate the rule-corpus repo (dans-anchor-system).

Since the T008 extraction (2026-07-13) the engine code lives at
~/ob/grove/warden while the corpus it compiles (rulesets/, facets/,
disciplines/, skills/audit) stays in dans-anchor-system, so the historic
`HERE.parents[1]` assumption only holds when running from the vendored copy
inside that repo. Resolution order:

1. `$WARDEN_CORPUS_ROOT` (env override — tests, CI, one-offs)
2. `~/.config/anchor-system/warden/config.yaml` `corpus_root:` (F080 per-skill config)
3. `parents[1]` of this file's directory, when it actually holds `rulesets/`
   (the vendored-copy case)

No silent fallback beyond that — fail loudly.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent


def corpus_root() -> Path:
    env = os.environ.get("WARDEN_CORPUS_ROOT")
    if env:
        return Path(env).expanduser()
    cfg = Path.home() / ".config/anchor-system/warden/config.yaml"
    if cfg.is_file():
        for line in cfg.read_text().splitlines():
            line = line.split("#", 1)[0].strip()
            if line.startswith("corpus_root:"):
                return Path(line.split(":", 1)[1].strip()).expanduser()
    if (_HERE.parents[1] / "rulesets").is_dir():  # vendored copy inside the corpus repo
        return _HERE.parents[1]
    sys.exit("warden: cannot locate the rule-corpus root — set corpus_root: in "
             "~/.config/anchor-system/warden/config.yaml or $WARDEN_CORPUS_ROOT")
