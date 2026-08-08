#!/usr/bin/env python3
"""test-f269-qmd-orphan.py — TINK F269: fixture renders must not reach the real
Q.md, and a section whose anchor is gone must be prunable.

Two halves, and the ORDER of them is the point. `queries-render.py` resolved
the vault root with no override, so `test-f244-stop-gate.sh` and
`test-f241-q-stamp.sh` spliced their fixture sections into the live Q.md;
teardown `rm -rf`d the fixture directory but could not reach into Q.md, and
four orphan sections (`F244FIX`, `F244FIXP`, `F241FIX`, `CTEST`) were still
sitting there on 2026-07-18.

  (1) `ANCHOR_VAULT_ROOT` is the actual fix — the leak stops at its source.
  (2) C56 is the net under it. Shipping only (2) would leave a checker
      permanently cleaning up after a bug nobody closed.

Cases:
  A. the override beats the F080 config and the ~/ob/kmr fallback
  B. a full fixture render writes the fixture Q.md and never opens the real one
  C. C56 flags a section whose anchor has no backlog
  D. C56 is silent on every live section — and the census is not vacuous
  E. the fixer prunes exactly the orphan span, leaving its neighbours intact
  F. THE DANGEROUS ONE — judged against the backlog universe, not the scoped
     set, so a per-anchor run cannot conclude every other section is dead

Self-contained: temp dirs only. Case B asserts the real Q.md's bytes are
unchanged rather than trusting that it was not opened."""
import hashlib
import importlib.machinery
import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
AQ = HERE / "audit-q.py"
RENDER = HERE / "queries-render.py"


def load_aq(vault_root=None):
    """Load audit-q.py fresh, optionally under an ANCHOR_VAULT_ROOT override."""
    old = os.environ.get("ANCHOR_VAULT_ROOT")
    if vault_root is None:
        os.environ.pop("ANCHOR_VAULT_ROOT", None)
    else:
        os.environ["ANCHOR_VAULT_ROOT"] = str(vault_root)
    try:
        name = f"aq_f269_{id(vault_root)}"
        loader = importlib.machinery.SourceFileLoader(name, str(AQ))
        spec = importlib.util.spec_from_loader(name, loader)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        loader.exec_module(mod)
        return mod
    finally:
        if old is None:
            os.environ.pop("ANCHOR_VAULT_ROOT", None)
        else:
            os.environ["ANCHOR_VAULT_ROOT"] = old


PASS = 0
FAIL = 0


def ok(m):
    global PASS
    PASS += 1
    print(f"  ok    {m}")


def no(m, got=None, want=None):
    global FAIL
    FAIL += 1
    print(f"  FAIL  {m}")
    if got is not None or want is not None:
        print(f"          got  {got!r}")
        print(f"          want {want!r}")


SECTION = """# [A]  [[{n} queries|{n}]]  -  Ready 1    User 0   |   Now 1    Next 0    Later 0   |   Parked 0    Waiting 0    Icebox 0

## Ready
- [[{n} Backlog#^F001|F001]] — **Next:** do the {n} thing
"""


def make_vault(root: Path, anchors, qmd_order):
    """Anchors get a backlog; qmd_order names the sections Q.md carries (which
    may include names with no anchor — that is the orphan case)."""
    for name in anchors:
        track = root / name / f"{name} Track"
        track.mkdir(parents=True)
        (root / name / ".anchor").write_text(f"slug: {name}\n", encoding="utf-8")
        (track / f"{name} Backlog.md").write_text(
            f"# {name} Backlog\n\n## Now\n\n"
            f"- **F001 — A row** [Ready] — body ^F001\n"
            f"  - **Next:** do the {name} thing\n\n## Done\n",
            encoding="utf-8")
    (root / "Q.md").write_text(
        "\n".join(SECTION.format(n=n) for n in qmd_order), encoding="utf-8")


# ---------------------------------------------------------------- A
print("A: ANCHOR_VAULT_ROOT beats the config and the ~/ob/kmr fallback")
with tempfile.TemporaryDirectory() as td:
    aq = load_aq(td)
    base = load_aq(None)
    if str(aq.VAULT_ROOT) == td and aq.Q_MD == Path(td) / "Q.md":
        ok("the override is honoured, and Q_MD follows it")
    else:
        no("the override is honoured, and Q_MD follows it",
           (str(aq.VAULT_ROOT), str(aq.Q_MD)), (td, f"{td}/Q.md"))
    if str(base.VAULT_ROOT) != td:
        ok("and without it the live vault root is unchanged")
    else:
        no("and without it the live vault root is unchanged",
           str(base.VAULT_ROOT), "not the fixture root")

# ---------------------------------------------------------------- B
print("\nB: a fixture render writes the fixture Q.md and not the real one")
real_qmd = load_aq(None).Q_MD


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None


with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    make_vault(root, ["ZFIXTURE"], [])
    (root / "Q.md").write_text("# Q\n", encoding="utf-8")
    before = digest(real_qmd)
    env = dict(os.environ, ANCHOR_VAULT_ROOT=str(root))
    r = subprocess.run([sys.executable, str(RENDER), "ZFIXTURE"],
                       capture_output=True, text=True, env=env)
    after = digest(real_qmd)
    if r.returncode == 0 and "ZFIXTURE" in (root / "Q.md").read_text():
        ok("the fixture Q.md received the section")
    else:
        no("the fixture Q.md received the section", r.stdout + r.stderr, "rc=0")
    if before == after:
        ok("the real Q.md is byte-identical afterwards")
    else:
        no("the real Q.md is byte-identical afterwards", after, before)

# ---------------------------------------------------------------- C
print("\nC: a section whose anchor has no backlog is a finding")
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    make_vault(root, ["ALPHA", "BETA"], ["ALPHA", "F244FIX", "BETA"])
    aq = load_aq(root)
    f = aq.check_c56_qmd_orphan_section(
        (root / "Q.md").read_text(), aq.find_anchor_backlogs(root))
    if len(f) == 1 and "F244FIX" in f[0].message and f[0].mechanically_fixable:
        ok("fires once, names the orphan, and offers the fix")
    else:
        no("fires once, names the orphan, and offers the fix",
           [x.message for x in f], ["…'F244FIX'…"])

# ---------------------------------------------------------------- D
print("\nD: every live section is silent, and the census is not vacuous")
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    make_vault(root, ["ALPHA", "BETA"], ["ALPHA", "BETA"])
    aq = load_aq(root)
    text = (root / "Q.md").read_text()
    f = aq.check_c56_qmd_orphan_section(text, aq.find_anchor_backlogs(root))
    ok("silent") if not f else no("silent", [x.message for x in f], [])
    n = len(aq._qmd_sections(text))
    if n == 2:
        ok("…and the parser actually saw both sections (a zero that means "
           "something)")
    else:
        no("…and the parser actually saw both sections", n, 2)

# ---------------------------------------------------------------- E
print("\nE: the fixer prunes exactly the orphan span")
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    make_vault(root, ["ALPHA", "BETA"], ["ALPHA", "F244FIX", "BETA"])
    aq = load_aq(root)
    log = aq.apply_c56_fix(root / "Q.md", aq.find_anchor_backlogs(root))
    text = (root / "Q.md").read_text()
    labels = [s[0] for s in aq._qmd_sections(text)]
    if labels == ["ALPHA", "BETA"]:
        ok("the orphan is gone and both neighbours survive, in order")
    else:
        no("the orphan is gone and both neighbours survive, in order",
           labels, ["ALPHA", "BETA"])
    if len(log) == 1 and "F244FIX" in log[0]:
        ok("…and the prune is reported, not silent")
    else:
        no("…and the prune is reported, not silent", log, ["…F244FIX…"])
    if "F244FIX" not in text and "do the ALPHA thing" in text:
        ok("…and the surviving section kept its body")
    else:
        no("…and the surviving section kept its body", text[:200], "ALPHA body")
    if not aq.apply_c56_fix(root / "Q.md", aq.find_anchor_backlogs(root)):
        ok("…and a second run is a no-op (no rewrite when nothing is orphaned)")
    else:
        no("…and a second run is a no-op", "rewrote again", "no-op")

# ---------------------------------------------------------------- F
print("\nF: judged against the UNIVERSE, never a scoped subset")
# The trap: `--scope backlog --anchor ALPHA` narrows `anchor_backlogs` to one
# entry. If C56 read that instead of `all_backlogs`, every other section in the
# file would look like an orphan and the first per-anchor `--fix` would empty
# Q.md. This asserts the difference explicitly rather than trusting the wiring.
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    make_vault(root, ["ALPHA", "BETA"], ["ALPHA", "BETA"])
    aq = load_aq(root)
    universe = aq.find_anchor_backlogs(root)
    scoped = {"ALPHA": universe["ALPHA"]}
    text = (root / "Q.md").read_text()
    if not aq.check_c56_qmd_orphan_section(text, universe):
        ok("the universe verdict is clean")
    else:
        no("the universe verdict is clean", "findings", [])
    if len(aq.check_c56_qmd_orphan_section(text, scoped)) == 1:
        ok("…and a scoped dict WOULD have condemned BETA — which is why the "
           "call site passes all_backlogs")
    else:
        no("…and a scoped dict WOULD have condemned BETA",
           aq.check_c56_qmd_orphan_section(text, scoped), "1 finding")
    src = AQ.read_text(encoding="utf-8")
    if "check_c56_qmd_orphan_section(qmd_text, all_backlogs)" in src:
        ok("…and the live call site does pass the universe")
    else:
        no("…and the live call site does pass the universe",
           "call site not found", "check_c56_qmd_orphan_section(qmd_text, all_backlogs)")

print("\n" + "-" * 40)
print(f"test-f269-qmd-orphan: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
