#!/usr/bin/env python3
"""test-t052-own-anchor-scope.py — T052: the hard-continuation directive is
scoped to the agent's OWN anchor. A vault-wide audit-q run must never tell the
running agent to continue on another anchor's Ready work (the failure that
pushed Lumen (LUM) onto MUX). Asserts:

  1. `_owning_slug_for_cwd` resolves the deepest anchor root containing cwd,
     and None when cwd is outside every anchor.
  2. `_print_hard_continuation_directive` prints ONLY the own anchor, never a
     sibling — and prints nothing when own_slug is None.

Self-contained: imports audit-q in-process, builds fixture anchors on a tmp
tree, captures stdout. No vault I/O."""
import importlib.machinery
import importlib.util
import io
import os
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


aq = _load("audit_q_mod", HERE / "audit-q.py")

PASS = 0
FAIL = 0
def ok(m): globals().__setitem__("PASS", PASS + 1); print(f"  PASS: {m}")
def no(m): globals().__setitem__("FAIL", FAIL + 1); print(f"  FAIL: {m}")


def _mk_anchor(root: Path, slug: str) -> Path:
    """Create {root}/{slug} Track/{slug} Backlog.md and return the backlog path."""
    track = root / f"{slug} Track"
    track.mkdir(parents=True, exist_ok=True)
    bl = track / f"{slug} Backlog.md"
    bl.write_text(f"# {slug} Backlog\n", encoding="utf-8")
    return bl


def _directive_text(banners, own_slug):
    buf = io.StringIO()
    with redirect_stdout(buf):
        aq._print_hard_continuation_directive(banners, own_slug)
    return buf.getvalue()


def run():
    with tempfile.TemporaryDirectory() as td:
        vault = Path(td).resolve()
        lum_root = vault / "Staff" / "Lumen"
        mux_root = vault / "prj" / "MUX"
        all_backlogs = {
            "LUM": _mk_anchor(lum_root, "LUM"),
            "MUX": _mk_anchor(mux_root, "MUX"),
        }
        banners = {
            "LUM": "# [A]  LUM  -  Ready 2    User 1   |   ...",
            "MUX": "# [A]  MUX  -  Ready 9    User 3   |   ...",
        }

        # 1. cwd resolution — deepest containing anchor
        prev = os.getcwd()
        try:
            os.chdir(lum_root)
            own = aq._owning_slug_for_cwd(all_backlogs)
            ok("cwd inside LUM → LUM") if own == "LUM" else no(f"cwd inside LUM → {own!r}")

            # a deeper subdir under Lumen still resolves to LUM
            deep = lum_root / "LUM Design" / "LUM Features"
            deep.mkdir(parents=True, exist_ok=True)
            os.chdir(deep)
            own = aq._owning_slug_for_cwd(all_backlogs)
            ok("cwd deep in LUM → LUM") if own == "LUM" else no(f"cwd deep in LUM → {own!r}")

            # cwd outside every anchor → None
            os.chdir(vault)
            own = aq._owning_slug_for_cwd(all_backlogs)
            ok("cwd outside anchors → None") if own is None else no(f"cwd outside → {own!r}")
        finally:
            os.chdir(prev)

        # 2. directive scoping — own anchor only, sibling never leaks
        txt = _directive_text(banners, "LUM")
        if "Ready 2" in txt and "MUX" not in txt and "Ready 9" not in txt:
            ok("directive from LUM lists LUM only, no MUX")
        else:
            no(f"directive leaked cross-anchor:\n{txt}")

        # own anchor at Ready 0 → silent even though MUX is hot
        cold = {"LUM": "# [A]  LUM  -  Ready 0    User 0   |   ...",
                "MUX": banners["MUX"]}
        txt = _directive_text(cold, "LUM")
        ok("own anchor Ready 0 → silent") if txt.strip() == "" else no(f"expected silence, got:\n{txt}")

        # own_slug None → suppressed entirely
        txt = _directive_text(banners, None)
        ok("own_slug None → suppressed") if txt.strip() == "" else no(f"expected suppression, got:\n{txt}")

        # explicit own anchor = MUX (MUX agent) → MUX shown, LUM not
        txt = _directive_text(banners, "MUX")
        if "Ready 9" in txt and "Ready 2" not in txt:
            ok("MUX agent sees MUX only")
        else:
            no(f"MUX-scoped directive wrong:\n{txt}")


if __name__ == "__main__":
    run()
    print(f"\n{PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)
