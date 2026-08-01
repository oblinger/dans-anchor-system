#!/usr/bin/env python3
"""F281 — C53 flags colliding ANCHOR names, and nothing else.

The property under test is the severity split that is the whole of F281's
design: an anchor page is an address written from anywhere in the vault, so a
colliding anchor name resolves by proximity to the *linking* file and is wrong
from most of the vault — an error. An ordinary file's collision is latent, not
active, and stays a warning on `ha --dump --format=collisions`.

The tests weight false positives heavily, because the population is what makes
error severity affordable: 3 anchor collisions today against 296 file-level
ones. One wrong firing on a folder-index or an externally-mandated filename and
the check is noise on day one.

Run: python3 test-f281-anchor-collisions.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "aq", Path(__file__).resolve().parent / "audit-q.py")
aq = importlib.util.module_from_spec(_spec)
sys.modules["aq"] = aq
_spec.loader.exec_module(aq)

FAILURES = []


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")
        FAILURES.append(name)


def anchor(root, rel, name=None):
    """Create `<rel>/<name>.md` beside a `.anchor` marker; default name = folder."""
    d = root / rel
    d.mkdir(parents=True, exist_ok=True)
    (d / ".anchor").write_text("")
    stem = name or d.name
    (d / f"{stem}.md").write_text(f"# {stem}\nAn anchor page.\n")
    return d / f"{stem}.md"


def plain(root, rel):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("# note\nOrdinary file.\n")
    return p


def run(root):
    index = aq.build_vault_index(root)
    return aq.check_c53_anchor_name_collisions(index, root)


def codes(findings):
    return sorted({f.code for f in findings})


with tempfile.TemporaryDirectory() as td:
    root = Path(td)

    print("1. Two anchor pages sharing a name → one error EACH")
    a = anchor(root, "RR/Ask")
    b = anchor(root, "prj/Ask")
    f = run(root)
    check("two findings, not one per group", len(f), 2)
    check("both are errors", sorted({x.severity for x in f}), ["error"])
    check("code is C53", codes(f), ["C53"])
    check("surfaces are the two anchor pages",
          sorted(x.surface_file for x in f), sorted([a, b]))
    # Routing lands each half on its own anchor only if the surfaces differ —
    # that is the whole reason this emits per-page rather than per-group.
    check("each finding names the OTHER path",
          all(str(other.relative_to(root)) in x.message
              for x, other in ((f[0], b), (f[1], a))
              if x.surface_file == a or x.surface_file == b),
          True)

with tempfile.TemporaryDirectory() as td:
    root = Path(td)

    print("2. What must NOT fire")
    # Ordinary files colliding — the 296-instance population. Warning territory,
    # owned by `ha`, never C53.
    plain(root, "prj/one/results.md")
    plain(root, "prj/two/results.md")
    check("ordinary-file collision is silent", run(root), [])

    # A folder index whose name differs from the folder: `Foo/SKILL.md` is not
    # Foo's anchor page, so many of them colliding is not an anchor collision.
    anchor(root, "skills/crank", name="SKILL")
    anchor(root, "skills/land", name="SKILL")
    check("non-eponymous page in an anchor folder is silent", run(root), [])

    # A page named for its folder but with no `.anchor` beside it is not an
    # anchor page at all.
    for rel in ("a/Shared", "b/Shared"):
        d = root / rel
        d.mkdir(parents=True, exist_ok=True)
        (d / "Shared.md").write_text("# Shared\nNot an anchor.\n")
    check("eponymous page without .anchor is silent", run(root), [])

    # One anchor, no twin.
    anchor(root, "prj/Solo")
    check("a unique anchor name is silent", run(root), [])

with tempfile.TemporaryDirectory() as td:
    root = Path(td)

    print("3. Exemptions and de-duplication")
    # Externally-mandated filenames are exempt by allowlist, even when they DO
    # sit as the eponymous page of their own folder.
    for rel in ("x/README", "y/README"):
        anchor(root, rel)
    check("README anchors are exempt", run(root), [])

    for rel in ("p/index", "q/index"):
        anchor(root, rel)
    check("index anchors are exempt", run(root), [])

    # Same file reachable by two walk paths (symlinked tree) is not a collision.
    real = anchor(root, "real/Twin")
    link = root / "mirror"
    try:
        link.symlink_to(root / "real")
        f = run(root)
        check("symlinked duplicate of one anchor is silent", f, [])
    except OSError:
        print("  skip symlink case (not permitted here)")

print()
if FAILURES:
    print(f"test-f281-anchor-collisions: {len(FAILURES)} FAILED — {FAILURES}")
    sys.exit(1)
print("test-f281-anchor-collisions: all checks pass")
