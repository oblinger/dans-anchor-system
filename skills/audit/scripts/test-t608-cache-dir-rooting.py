#!/usr/bin/env python3
"""T608 — the audit cache root is never derived from the process cwd.

`~/ob/kmr/umbrella/R-anchor-450377da353065e3.json` was found at the VAULT ROOT
and git-tracked, so the hourly sweep had committed a regenerable cache into the
commons. The default was always absolute; the escape is a RELATIVE
`--cache-dir`, which stayed relative and so resolved against wherever the run
started.

Both halves are pinned, because either alone leaves the hole open: a relative
option must resolve to one stable place regardless of cwd, and a cache dir
inside a git working tree must be refused outright — that is the actual damage,
and it is the half that still bites a caller passing an absolute repo path.
"""
import importlib.util, os, pathlib, subprocess, sys, tempfile

_HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("ap", _HERE / "audit-plan.py")
ap = importlib.util.module_from_spec(_spec)
sys.modules["ap"] = ap
_spec.loader.exec_module(ap)

PASSED = FAILED = 0


def check(name, cond):
    global PASSED, FAILED
    print(f"  {'ok  ' if cond else 'FAIL'}    {name}")
    PASSED += bool(cond)
    FAILED += not cond


# --- the cwd must not reach the result ------------------------------------
orig = os.getcwd()
try:
    a = tempfile.mkdtemp()
    b = tempfile.mkdtemp()
    os.chdir(a)
    from_a = ap.cache_dir("t608-probe")
    os.chdir(b)
    from_b = ap.cache_dir("t608-probe")
finally:
    os.chdir(orig)

check("a relative --cache-dir resolves identically from two directories", from_a == from_b)
check("and it is absolute", from_a.is_absolute())
check("and it is not under either cwd",
      not str(from_a).startswith(a) and not str(from_a).startswith(b))
check("the default is absolute and outside any repo", ap.cache_dir(None).is_absolute())

# --- a git working tree is refused ----------------------------------------
repo = pathlib.Path(tempfile.mkdtemp()) / "r"
repo.mkdir()
subprocess.run(["git", "init", "-q", str(repo)], check=True,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

refused = False
try:
    ap.cache_dir(str(repo / "cache"))
except SystemExit as e:
    refused = "git working tree" in str(e)
check("a cache dir inside a git working tree is refused", refused)

# Nested deeper — the walk must reach the repo root, which is the shape the
# vault-root find actually had (the cache sat several levels down from .git).
deep = repo / "x" / "y" / "cache"
refused_deep = False
try:
    ap.cache_dir(str(deep))
except SystemExit:
    refused_deep = True
check("refusal walks up to the repo root, not just the immediate parent", refused_deep)

msg = ""
try:
    ap.cache_dir(str(repo / "c"))
except SystemExit as e:
    msg = str(e)
check("the refusal names the tracked root and a remedy",
      str(repo) in msg and "--cache-dir" in msg)

# --- a non-repo absolute path still works ---------------------------------
ok_dir = pathlib.Path(tempfile.mkdtemp()) / "plain"
got = ap.cache_dir(str(ok_dir))
check("an absolute path outside any repo is accepted", got == ok_dir and (got / "flat").is_dir())

print(f"\n{PASSED}/{PASSED + FAILED} passed")
sys.exit(1 if FAILED else 0)
