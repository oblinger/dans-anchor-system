#!/usr/bin/env python3
"""aow-safety.py — F179 no-collateral-damage check.

For each `.md` path given, COPY it (never touches the original), run the on-write doc
audit on the copy, and assert the two safety properties that make vault-wide rollout
acceptable:
  • content-preservation — the copy's alphanumeric character sequence is preserved as a
    subsequence after the fix (insertions/escapes/whitespace OK; no letter/digit deleted);
  • idempotence — a second on-write pass makes no further change.

Prints a JSON summary and exits non-zero if any doc shows a defect. Thin wrapper around
the F177/F179 engine in audit-plan.py, so the fix logic stays single-sourced."""
import importlib.util
import json
import pathlib
import shutil
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("ap", HERE / "audit-plan.py")
assert _spec and _spec.loader
ap = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ap)


def _alnum(s):
    return [c for c in s if c.isalnum()]


def _subseq(small, big):
    it = iter(big)
    return all(c in it for c in small)


def check_one(path: str) -> dict:
    p = pathlib.Path(path).expanduser()
    if not p.is_file():
        return {"doc": path, "skip": "missing"}
    work = pathlib.Path(tempfile.mkdtemp(prefix="aow-"))
    copy = work / p.name
    try:
        shutil.copy2(p, copy)
        orig = copy.read_text(encoding="utf-8", errors="replace")
        ap.execute_on_write(ap.plan_one(copy, "doc", None, []), None)
        after1 = copy.read_text(encoding="utf-8", errors="replace")
        ap.execute_on_write(ap.plan_one(copy, "doc", None, []), None)
        after2 = copy.read_text(encoding="utf-8", errors="replace")
        return {
            "doc": path,
            "changed": orig != after1,
            "content_preserved": _subseq(_alnum(orig), _alnum(after1)),
            "idempotent": after1 == after2,
        }
    except Exception as e:
        return {"doc": path, "error": f"{type(e).__name__}: {e}"}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    # Paths come from argv, or (robust for paths with spaces) newline-delimited on stdin.
    paths = sys.argv[1:]
    if not paths and not sys.stdin.isatty():
        paths = [ln for ln in (l.rstrip("\n") for l in sys.stdin) if ln.strip()]
    results = [check_one(d) for d in paths]
    defects = [r for r in results
               if not r.get("skip") and not r.get("error")
               and (not r.get("content_preserved") or not r.get("idempotent"))]
    errors = [r for r in results if r.get("error")]
    print(json.dumps({"n": len(results), "defects": defects,
                      "errors": errors, "results": results}, indent=1))
    sys.exit(1 if (defects or errors) else 0)


if __name__ == "__main__":
    main()
