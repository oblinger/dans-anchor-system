#!/usr/bin/env python3
"""T297 leg 3 — audit-surfaced.py resolves the two checkable `surfaced::`
forms and reports (never fixes) when they rot.

Unit-tests the pure functions against synthetic input (no vault I/O), then
runs a live sanity pass against the real Agent Recipes tree to prove the
checker is not vacuous on the corpus it actually audits.

Run: python3 test-t297-audit-surfaced.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent


def _load(name, fn):
    # A hyphenated filename is not importable, so load it by path. Both the spec
    # and its loader are Optional in the stubs; fail loudly here rather than let
    # a missing checker surface later as an opaque AttributeError.
    spec = importlib.util.spec_from_file_location(name, _HERE / fn)
    if spec is None or spec.loader is None:
        raise ImportError("cannot load %s from %s" % (name, _HERE / fn))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


asf = _load("asf", "audit-surfaced.py")

FAILURES = []


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")
        FAILURES.append(name)


print("1. parse_surfaced_line is anchored — doctrine mentions don't count")
check("a real declaration parses",
      asf.parse_surfaced_line("# H1\nsurfaced:: in-area\n"), "in-area")
check("embedded prose mentioning the field does not",
      asf.parse_surfaced_line("| **[[#`surfaced::`]]** |  |\n"), None)

print("2. classify splits each form correctly")
check("in-area", asf.classify("in-area")[0], "in-area")
check("memory", asf.classify("memory — `gotcha_foo`"), ("memory", "gotcha_foo"))
check("claude", asf.classify("CLAUDE.md — the `x` row")[0], "claude")
check("skill", asf.classify("skill — foo")[0], "skill")
check("facet", asf.classify("facet — foo")[0], "facet")
check("template placeholder is unparseable",
      asf.classify("{{in-area, or the mechanism}}")[0], "unparseable")
check("garbage is unparseable", asf.classify("something else")[0], "unparseable")

print("3. resolve_memory accepts hyphen/underscore either way")
with tempfile.TemporaryDirectory() as td:
    mem = Path(td)
    (mem / "gotcha_foo_bar.md").write_text("x")
    check("underscore slug, underscore file", asf.resolve_memory("gotcha_foo_bar", mem), True)
    check("hyphen slug, underscore file", asf.resolve_memory("gotcha-foo-bar", mem), True)
    check("missing slug is broken", asf.resolve_memory("gotcha_nope", mem), False)

print("4. extract_quotes finds backtick and double-quote literals")
check("backtick literal", asf.extract_quotes("the `yore` row"), ["yore"])
check("double-quote literal", asf.extract_quotes('the "Never ask" line'), ["Never ask"])
check("no literal at all", asf.extract_quotes("a plain description"), [])

print("5. resolve_claude — ok / broken / unverifiable")
claude_text = "Some preamble.\n**Never ask the user to run a shell command** — you run it.\n"
check("a matching literal resolves",
      asf.resolve_claude("the `Never ask the user to run a shell command` rule", claude_text)[0],
      "ok")
check("a literal that no longer appears is broken",
      asf.resolve_claude("the `this text was deleted long ago` rule", claude_text)[0],
      "broken")
check("no literal to check is unverifiable",
      asf.resolve_claude("a vague description with no excerpt", claude_text)[0],
      "unverifiable")

print("6. find_recipe_files skips underscore-prefixed templates")
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    (root / "AREC Real.md").write_text("surfaced:: in-area\n")
    (root / "_AREC Template.md").write_text("surfaced:: {{in-area}}\n")
    found = [p.name for p in asf.find_recipe_files(root)]
    check("real recipe included", "AREC Real.md" in found, True)
    check("template excluded", "_AREC Template.md" in found, False)

print("7. scan() end-to-end never fixes and reports both a break and a pass")
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    mem = root / "memory"
    mem.mkdir()
    (mem / "gotcha_present.md").write_text("x")
    claude = root / "CLAUDE.md"
    claude.write_text("The `alpha` marker is present.\n")
    (root / "AREC Good.md").write_text("# H1\nsurfaced:: memory — `gotcha_present`\n")
    (root / "AREC Bad.md").write_text("# H1\nsurfaced:: memory — `gotcha_missing`\n")
    (root / "AREC Claude Good.md").write_text("# H1\nsurfaced:: CLAUDE.md — the `alpha` marker\n")
    (root / "AREC Claude Bad.md").write_text("# H1\nsurfaced:: CLAUDE.md — the `omega` marker\n")
    before = {p: (root / p).read_text() for p in
              ["AREC Good.md", "AREC Bad.md", "AREC Claude Good.md", "AREC Claude Bad.md"]}
    results = asf.scan(root=root, memory_dir=mem, claude_path=claude)
    by_file = {r["file"]: r for r in results}
    check("a present memory is ok", by_file["AREC Good.md"]["status"], "ok")
    check("a missing memory is broken", by_file["AREC Bad.md"]["status"], "broken")
    check("a present CLAUDE.md excerpt is ok", by_file["AREC Claude Good.md"]["status"], "ok")
    check("a missing CLAUDE.md excerpt is broken", by_file["AREC Claude Bad.md"]["status"], "broken")
    after = {p: (root / p).read_text() for p in before}
    check("scan() never writes to any recipe file", after, before)

print("8. Live sanity — the real vault is not vacuous")
live = asf.scan()
check("the real recipe corpus has more than a handful of declarations",
      len(live) > 10, True)
kinds = {r["kind"] for r in live}
check("at least one real memory-form recipe exists", "memory" in kinds, True)
check("at least one real CLAUDE.md-form recipe exists", "claude" in kinds, True)

print()
if FAILURES:
    print(f"test-t297-audit-surfaced: {len(FAILURES)} FAILED — {FAILURES}")
    sys.exit(1)
print("test-t297-audit-surfaced: all checks pass")
