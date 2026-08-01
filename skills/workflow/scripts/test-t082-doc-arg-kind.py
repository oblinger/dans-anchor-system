#!/usr/bin/env python3
"""T082 — `<doc>` kind follows the RESOLVED FILE, not the caller's spelling.

`state -a Tink Backlog F+` worked; `state -a Tink "Tink Backlog" F+` resolved to
the very same file and then rejected `F+` as an "unknown query kind", falling
through to the generic Q/V branch. The error read self-contradictorily — it
listed the labels valid "on Backlog" while naming `Tink Backlog.md` as the
target — which is what made it expensive: it cost an agent three wrong turns and
produced a false "state is broken" report to Dan.

Not a correctness bug (the working form was documented), so the assertions here
are about the CLASSIFIER, which is where the confusion actually lived:

  1. Every spelling that resolves to the anchor's backlog classifies as
     'backlog' — the bare keyword, the full wiki-name, an absolute path.
  2. A doc that is NOT the backlog still classifies as 'doc'. This is the
     assertion that would catch an over-broad fix.
  3. An anchor with no backlog at all does not crash the classifier.

Run: python3 test-t082-doc-arg-kind.py
"""
import importlib.machinery
import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
loader = importlib.machinery.SourceFileLoader("state_mod", str(HERE / "state"))
spec = importlib.util.spec_from_loader("state_mod", loader)
st = importlib.util.module_from_spec(spec)
sys.modules["state_mod"] = st
loader.exec_module(st)

PASS = 0
FAIL = 0


def check(name, got, want):
    global PASS, FAIL
    if got == want:
        PASS += 1
        print(f"  PASS: {name}")
    else:
        FAIL += 1
        print(f"  FAIL: {name}\n          got  {got!r}\n          want {want!r}")


def build(root: Path):
    """A minimal anchor: .anchor marker, a Track/ backlog, and one feature doc."""
    (root / ".anchor").write_text("slug: ZZ\n")
    track = root / "ZZ Track"
    track.mkdir()
    (track / "ZZ Backlog.md").write_text("# ZZ Backlog\nFixture.\n\n## Now\n")
    feats = root / "ZZ Design" / "ZZ Features"
    feats.mkdir(parents=True)
    (feats / "F001 — Something.md").write_text("# F001 — Something\nFixture.\n")
    return track / "ZZ Backlog.md", feats / "F001 — Something.md"


with tempfile.TemporaryDirectory() as td:
    root = Path(td) / "ZZ"
    root.mkdir()
    backlog, feature = build(root)

    # Point the module's vault + backlog lookup at the fixture.
    st.be.VAULT_ROOT = Path(td)
    st.be.find_backlog = lambda slug: backlog

    print("1. Every spelling of the backlog classifies as 'backlog'")
    for label, arg in [
        ("bare keyword `Backlog`", "Backlog"),
        ("lowercase `backlog`", "backlog"),
        ("full wiki-name `ZZ Backlog`", "ZZ Backlog"),
        ("absolute path", str(backlog)),
    ]:
        kind, path = st.resolve_v2_doc(arg, "ZZ", root)
        check(f"{label} → backlog", (kind, path.resolve()), ("backlog", backlog.resolve()))

    print("2. A non-backlog doc still classifies as 'doc'")
    kind, path = st.resolve_v2_doc("F001 — Something", "ZZ", root)
    check("feature doc by wiki-name → doc", (kind, path.resolve()), ("doc", feature.resolve()))
    kind, path = st.resolve_v2_doc(str(feature), "ZZ", root)
    check("feature doc by path → doc", (kind, path.resolve()), ("doc", feature.resolve()))

    print("3. An anchor with no backlog does not crash the classifier")

    def boom(slug):
        raise RuntimeError("no backlog for this anchor")

    st.be.find_backlog = boom
    kind, path = st.resolve_v2_doc("F001 — Something", "ZZ", root)
    check("still resolves the doc", (kind, path.resolve()), ("doc", feature.resolve()))

print(f"\ntest-t082-doc-arg-kind: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
