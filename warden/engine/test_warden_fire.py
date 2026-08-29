#!/usr/bin/env python3
"""Regression test for warden_fire.py (F211 fire path — Success Criteria).

Pins the two properties the F211 Success Criteria name:
  1. The real `R-query-14` fires end-to-end at `skill:pre:audit-q` against a
     fixture anchor whose queries file carries a commit/push question — the
     compile → install → fire loop, module-emitted body and all.
  2. Indexed dispatch + active-set gating, via a synthesized two-rule fixture on
     different moments: firing one moment runs ONLY its rule; a rule whose trait
     the anchor has not adopted does not fire.

Runnable standalone (`python3 test_warden_fire.py`) — no test framework.
"""
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
from warden_root import corpus_root
REPO = corpus_root()
sys.path.insert(0, str(HERE))

import warden_compile as wc   # noqa: E402
import warden_fire as wf      # noqa: E402

RS_QUERY = REPO / "rulesets" / "R-query.md"   # F234 extraction (was facets/DAS Query.md)

# A synthesized ruleset with two when-rules on DIFFERENT moments; each body
# records a distinct marker so we can prove only one executes per moment.
FIXTURE_RULESET = '''# RULESET R-fix
include::

### RULE R-fix-01 — audit-q marker (when:: skill:post:audit-q)
when:: skill:post:audit-q

```python
def trigger(ctx):
    return ["A-fired"]
```

### RULE R-fix-02 — write marker (when:: tool:post:Write)
when:: tool:post:Write

```python
def body(ctx):
    return ["B-fired"]
```
'''


def _compile_into(warden_dir: Path, text: str, name: str, anchor: str):
    rs = wc.parse_ruleset(text, name, "fixture.md")
    assert rs is not None, f"ruleset {name} not parsed"
    ir, module_src, _ = wc.compile_ruleset(rs, anchor)
    warden_dir.mkdir(parents=True, exist_ok=True)
    import json
    (warden_dir / "rules-ir.json").write_text(json.dumps(ir), encoding="utf-8")
    (warden_dir / f"rules_{anchor}.py").write_text(module_src, encoding="utf-8")
    return ir


def test_real_r_query_14_fires(tmp: Path):
    """Build a fixture anchor that adopted the `query` trait + Commit aspect, with
    a commit/push question in its queries file; fire audit-q → the steer."""
    anchor = tmp / "FX"
    (anchor / "FX Track").mkdir(parents=True)
    (anchor / ".anchor").write_text("slug: FX\ntraits: [query, Commit]\n", encoding="utf-8")
    (anchor / "FX Track" / "FX queries.md").write_text(
        "## Immediate Questions\n\n- **Q1** Should I commit and push this branch now?\n",
        encoding="utf-8")

    wdir = anchor / ".warden"
    _compile_into(wdir, RS_QUERY.read_text(encoding="utf-8"), "R-query", "query")
    ir, module = wf.load_compiled(wdir, "query")
    traits = wf.read_anchor_traits(anchor)
    ctx = wf.build_ctx(anchor, "skill:pre:audit-q")

    assert ctx.git_aspect == "commit", ctx.git_aspect
    assert "commit and push" in ctx.queries_text
    steers = wf.fire(ir, module, "skill:pre:audit-q", ctx, traits)
    assert steers and "Do NOT ask" in steers[0], steers
    assert "commit now" in steers[0], steers[0]
    print("PASS  real_r_query_14_fires")


def test_indexed_dispatch_and_gating(tmp: Path):
    wdir = tmp / "fixwarden"
    _compile_into(wdir, FIXTURE_RULESET, "R-fix", "fix")
    ir, module = wf.load_compiled(wdir, "fix")

    # sanity: two rules, on two different moments
    assert set(ir["moments"]) == {"skill:pre:audit-q", "tool:post:Write"}, ir["moments"]

    adopted = ["fix", "anchor-base"]
    ctx = wf.build_ctx(tmp, "skill:pre:audit-q")  # tmp has no .anchor → bare ctx

    # firing audit-q runs ONLY R-fix-01
    a = wf.fire(ir, module, "skill:pre:audit-q", ctx, adopted)
    assert a == ["A-fired"], a
    # firing Write runs ONLY R-fix-02
    b = wf.fire(ir, module, "tool:post:Write", ctx, adopted)
    assert b == ["B-fired"], b

    # active-set gating: an anchor that has NOT adopted the `fix` trait fires nothing
    none = wf.fire(ir, module, "skill:pre:audit-q", ctx, ["other", "anchor-base"])
    assert none == [], none
    print("PASS  indexed_dispatch_and_gating")


def main():
    with tempfile.TemporaryDirectory() as td:
        test_real_r_query_14_fires(Path(td) / "a")
        test_indexed_dispatch_and_gating(Path(td) / "b")
    print("\nall warden_fire tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())


def test_command_text_helpers():
    """T605 / T609 — the `tool:pre:Bash` rules judge a command's SHAPE, and the
    helpers that give them that shape are pinned here.

    Both defects were the same mistake at different grains: reading text that is
    DATA (a heredoc body, a quoted argument) as if it were shell. The fixtures
    below pin both directions, because the cheap fix in each case would have
    blinded the rule rather than sharpening it.
    """
    import warden_fire as wf
    nl = chr(10)

    # --- T609: heredoc bodies -------------------------------------------
    doc = nl.join(["cat > n.md <<'EOF'", "bad: ssh h 'make test'", "EOF"])
    assert "ssh h" not in wf.strip_heredoc_bodies(doc), \
        "a documentation heredoc body must not be tokenized as command position"
    shell = nl.join(["bash <<EOF", "ssh h 'make test'", "EOF"])
    assert "ssh h" in wf.strip_heredoc_bodies(shell), \
        "a heredoc fed to a SHELL is code -- its body must be retained"
    assert wf.strip_heredoc_bodies('cat <<<"ssh h uptime"') == 'cat <<<"ssh h uptime"', \
        "a herestring is not a heredoc"
    assert wf.strip_heredoc_bodies("ssh h uptime") == "ssh h uptime", \
        "a command with no heredoc is unchanged"

    # --- T611: an unquoted newline is a command separator ----------------
    assert wf.newlines_to_separators("cd /x" + nl + "ssh h c") == "cd /x ; ssh h c", \
        "a bare newline separates commands exactly as `;` does"
    assert wf.newlines_to_separators('echo "a' + nl + 'b"') == 'echo "a' + nl + 'b"', \
        "a newline INSIDE quotes is data and must survive"
    assert wf.newlines_to_separators("echo a \\" + nl + "  b") == "echo a    b", \
        "a trailing backslash is a line continuation, not a separator"
    assert wf.newlines_to_separators("ssh h c") == "ssh h c", \
        "a single-line command is unchanged"

    # --- T605: quoted spans are data ------------------------------------
    assert wf.mask_quoted("""a 'bcd' e""") == "a '   ' e", "quote contents blanked, delimiters kept"
    assert len(wf.mask_quoted('x "yz" w')) == len('x "yz" w'), "mask is length-preserving"

    # --- T605: `>` only counts when it writes a FILE ---------------------
    def writes(cmd):
        ops = wf.mask_quoted(cmd)
        return bool(wf.REDIRECT_RE.search(ops) or wf.MOVE_COPY_RE.search(ops))

    # Reads. `2>&1` is the commonest suffix in the corpus and duplicates a file
    # descriptor -- it creates nothing. Treating it as a write is what made a
    # pure `grep -c` on a spine-dirty page refuse.
    assert not writes("grep -c foo a.md 2>&1"), "2>&1 is fd duplication, not a file write"
    assert not writes("ls >&2"), ">&2 is fd duplication, not a file write"
    assert not writes("grep foo a.md | head -1"), "a pipe is not a redirect"
    assert not writes("cat a.md"), "a plain read is not a write"
    assert not writes('state drop X "a path -> another"'), \
        "an arrow inside a quoted argument is prose, not a redirect"
    assert not writes('echo "cp is mentioned here" a.md'), \
        "mv/cp inside a quoted argument is prose, not command position"

    # Writes -- the fix must not open a hole.
    assert writes("echo x > a.md"), "truncating redirect"
    assert writes("cat a.md >> b.md"), "appending redirect"
    assert writes("cp /tmp/x.md a.md"), "cp in command position"
    assert writes("mv /tmp/x.md a.md"), "mv in command position"
    assert writes("foo; cp /tmp/x.md a.md"), "cp after a separator is command position"
    assert writes("echo x 2>/tmp/err.log"), "2>file really does write a file"
    print("PASS  command_text_helpers (T605 / T609)")
