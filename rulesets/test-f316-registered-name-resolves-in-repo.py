#!/usr/bin/env python3
"""test-f316-registered-name-resolves-in-repo.py — a DAS document may not claim
a name the vault already owns.

A registered name is vault-wide, so two documents cannot hold one. When a
DAS-repo document's masthead claims a name that HookAnchor resolves to a
DIFFERENT file, the loser's identity cell is computed from the winner's
ancestry — so the page displays somebody else's breadcrumb and nothing can
regenerate it. `skills/survey/Survey.md` showed exactly that
(`→ [[kmr]] → [[Topic]] → [[SRCH]] → [Survey]`, the vault catalog's chain, on
the skill's own page) until F316 retired it 2026-08-13 along with the atlas,
find and profile stubs.

**This must be keyed on the CLAIMED NAME, never on the filename.** F316's first
sweep keyed on basename and produced three phantoms: `skills/architect/SKILL.md`
and `skills/rewire/SKILL.md` carry an identity-SHAPED row as a *specimen* in
their bodies, and `examples/Snap/SKILL.md` is registered as `Snap` while its
masthead displays the fictional label `Snapper Dapper`. A detector keyed on the
filename cannot see which name a file actually claims — the
[[project_probe_that_can_never_pass]] shape one step earlier: not a probe that
never fires, but one that fires on the wrong key. Hence the masthead scan below,
and hence the head-only window: an identity-shaped row deeper in a body is a
specimen, not a claim.

Unresolvable claims are counted and printed but do NOT fail. Two legitimate
kinds exist and both are load-bearing: template placeholders (`{slug} Backlog`,
`{date} {name}`) whose whole job is to be uninstantiated, and example labels
like `Snapper Dapper`. Failing on them would make the suite red forever and it
would be turned off, which is worse than the defect it guards.

Costs ~40s: one `ha -p` per masthead, ~300 of them. That is the price of asking
the live command store rather than a reimplementation of its resolution rules —
a second resolver would be the two-engines hazard this repo refuses elsewhere.

    python3 test-f316-registered-name-resolves-in-repo.py
"""
import pathlib
import re
import subprocess

REPO = pathlib.Path(__file__).resolve().parent.parent

# `| -[[Name]]- |` or `| -[[Name\|Display]]- |` — Obsidian escapes the pipe
# inside a table cell, so the alias separator is `\|` here and `|` elsewhere.
MASTHEAD = re.compile(r"^\|\s*-\[\[(.+?)\]\]-\s*\|")
HEAD_LINES = 12          # a masthead is in the head; deeper rows are specimens


def claimed_name(line):
    """The name a masthead row claims, alias stripped."""
    m = MASTHEAD.match(line)
    if not m:
        return None
    name = m.group(1)
    for sep in ("\\|", "|"):
        if sep in name:
            name = name.split(sep, 1)[0]
            break
    return name.strip()


def mastheads(root):
    """(path, claimed name) for every file in `root` whose head carries one."""
    out = []
    for p in sorted(root.rglob("*.md")):
        if ".git" in p.parts:
            continue
        try:
            lines = p.read_text(encoding="utf-8").split("\n")
        except (OSError, UnicodeDecodeError):
            continue
        for line in lines[:HEAD_LINES]:
            name = claimed_name(line)
            if name:
                out.append((p, name))
                break
    return out


def resolve(name):
    """`ha -p <name>` — the live command store, not a reimplementation."""
    r = subprocess.run(["ha", "-p", name], capture_output=True, text=True)
    return r.stdout.strip() or None


results = []


def check(label, cond, detail=""):
    results.append(cond)
    print(f"  {'PASS' if cond else 'FAIL'}: {label}{(' — ' + detail) if detail else ''}")


# --- the sweep -------------------------------------------------------------
claims = mastheads(REPO)
print(f"{len(claims)} DAS documents carry a masthead identity cell\n")

foreign, unresolved = [], []
for path, name in claims:
    got = resolve(name)
    if got is None:
        unresolved.append((path, name))
    elif not pathlib.Path(got).resolve().is_relative_to(REPO):
        foreign.append((path, name, got))

for path, name, got in foreign:
    print(f"  !! {path.relative_to(REPO)}\n     claims [[{name}]] -> {got}")
check("no DAS document claims a name that resolves outside the repo",
      not foreign, f"{len(foreign)} collision(s)")

print(f"\n  ({len(unresolved)} claim(s) resolve to nothing — placeholders and "
      f"example labels, listed for eyes, not failures)")
for path, name in unresolved:
    print(f"     {path.relative_to(REPO)}  [[{name}]]")

# --- red-check: the sweep must actually be able to go red ------------------
# Asserting only "zero found" cannot distinguish a clean repo from a broken
# detector. Point a synthetic masthead at a name the VAULT owns and confirm it
# is caught — `Atlas` is the vault-wide router at SYS/Atlas/Atlas.md, and the
# retired `skills/atlas/Atlas.md` claiming it is the exact defect F316 closed.
print()
vault_owned = resolve("Atlas")
check("red-check fixture resolves (vault owns the name `Atlas`)",
      vault_owned is not None and not pathlib.Path(vault_owned).resolve()
      .is_relative_to(REPO), f"got {vault_owned}")
check("a masthead claiming `Atlas` parses as that claim",
      claimed_name("| -[[Atlas]]- | : whatever<br>-> [[x]] |") == "Atlas")
check("the alias form parses to the NAME, not the display text",
      claimed_name("| -[[DAS Audit Design\\|Audit Design]]- | : x |")
      == "DAS Audit Design")
check("a non-masthead row is not read as a claim",
      claimed_name("| Related | [[DAS Skills\\|Skills]],   |") is None)

print(f"\nF316 registered-name uniqueness: {sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
