#!/usr/bin/env python3
"""F600 — a mirrored doc carries no spine.

A `:>>` breadcrumb and a dispatch masthead are wiki-links and `hook://` URIs, so
they render as literal noise once a file is copied into an external repo. Dan
ruled 2026-08-28 that the rule is a PROHIBITION, not an exemption: *"the rule
should be mirrored docs cannot have a spine, because it just doesn't mean
anything in the receiver's environment."*

The two fail in opposite directions, and that is what these fixtures pin. An
exemption says *do not look*, so a mirrored doc that later acquires a breadcrumb
is invisible forever and the noise arrives on GitHub. A prohibition says *look,
and expect nothing*, so the same doc is a finding on the next pass. Both
directions are asserted below, because a change that only silenced R-spine on
mirrored docs would pass half of this file and ship the failure mode the ruling
was about.
"""
import importlib.util, json, pathlib, sys, tempfile

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
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


# ── the grammar ────────────────────────────────────────────────────────────
# Mirror-ness is a MODIFIER on the line, not a word in the glob vocabulary:
# `!`-negation is implemented in exactly one of the five kinds, so a rule saying
# `always` could not exclude anything at all.
check("`always` is unmodified", ap.parse_selector("always") == ("always", "", None))
check("a trailing `, !mirror` excludes",
      ap.parse_selector("always, !mirror") == ("always", "", "exclude"))
check("the bare kind `mirror` selects",
      ap.parse_selector("mirror") == ("mirror", "", "only"))
check("the modifier composes with `file:` and does not leak into the glob",
      ap.parse_selector("file:{anchor}/**, !mirror") == ("file", "{anchor}/**", "exclude"))
check("and with `group:`",
      ap.parse_selector("group:facet, !mirror") == ("group", "facet", "exclude"))
check("whitespace around the modifier is tolerated",
      ap.parse_selector("always ,  !mirror ") == ("always", "", "exclude"))
check("a glob whose own text contains 'mirror' is untouched",
      ap.parse_selector("file:mirror/**") == ("file", "mirror/**", None))

# ── the filter, against a route index we control ───────────────────────────
td = pathlib.Path(tempfile.mkdtemp())
route = td / "anchor" / "Mirrored"
route.mkdir(parents=True)
outside = td / "anchor" / "Vault Side.md"
inside = route / "Doc.md"
outside.write_text(":>> [[a]] -> [[b]]\n\n# Vault Side\nOrientation.\n", encoding="utf-8")
inside.write_text("# Doc\nOrientation.\n", encoding="utf-8")

index = td / "mirror-routes.json"
index.write_text(json.dumps({"routes": [{"here": str(route), "there": "/tmp/repo"}]}),
                 encoding="utf-8")
spine = ap._spine_sibling("spine")
_orig_index = spine.MIRROR_INDEX
spine.MIRROR_INDEX = index

scope = [inside, outside]
root = td / "anchor"


def names(where):
    k, a, m = ap.parse_selector(where)
    return sorted(p.name for p in ap.match_targets(k, a, scope, root, m))


check("`always` still matches everything", names("always") == ["Doc.md", "Vault Side.md"])
check("`always, !mirror` drops the mirrored doc", names("always, !mirror") == ["Vault Side.md"])
check("`mirror` selects exactly the mirrored doc", names("mirror") == ["Doc.md"])
check("the two selectors partition the scope — no doc is in both, none in neither",
      set(names("always, !mirror")) | set(names("mirror")) == set(names("always"))
      and not (set(names("always, !mirror")) & set(names("mirror"))))

# ── the rule itself ────────────────────────────────────────────────────────
v, _ = ap.chk_mirrored_doc_has_no_spine(inside, root, None)
check("a mirrored doc with no spine passes R-spine-11", v == "pass")

inside.write_text(":>> [[a]] -> [[b]]\n\n# Doc\nOrientation.\n", encoding="utf-8")
v, msg = ap.chk_mirrored_doc_has_no_spine(inside, root, None)
check("a mirrored doc that ACQUIRES a breadcrumb is a finding", v == "fail")
check("and the message says why it is wrong there, not merely that it is wrong",
      "external repo" in msg and "render" in msg)

masthead = "| -[[Doc]]- | x |\n| --- | --- |\n| ... | |\n\n# Doc\nOrientation.\n"
inside.write_text(masthead, encoding="utf-8")
v, _ = ap.chk_mirrored_doc_has_no_spine(inside, root, None)
check("a dispatch masthead is caught too, not just a breadcrumb", v == "fail")

# ── an unreadable index fails toward MORE checking, never less ─────────────
spine.MIRROR_INDEX = td / "does-not-exist.json"
check("with no route index, `, !mirror` excludes nothing",
      names("always, !mirror") == ["Doc.md", "Vault Side.md"])
check("and `mirror` selects nothing rather than everything", names("mirror") == [])
spine.MIRROR_INDEX = _orig_index

print(f"\n{PASSED}/{PASSED + FAILED} passed")
sys.exit(1 if FAILED else 0)
