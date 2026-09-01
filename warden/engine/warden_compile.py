#!/usr/bin/env python3
"""Warden rule compiler (F211 — Rule compiler / installer).

Compiles authored rulesets into the two coordinated artifacts the F211 §
IR schema specifies (per anchor, into `.warden/`):

  1. `rules-ir.json` — the shared IR table both engines interpret
     (F212 Python reference + F213 Rust): a moment dispatch index, the
     per-trait active-sets, and one row per rule carrying its declarative
     residual (`where` glob, fixed-vocab `guards`, declarative `action`)
     plus the `guard_py` / `body_py` escapes to the warm Python daemon.
  2. `rules_<anchor>.py` — the emitted module holding one function per
     inherently-Python clause (arbitrary `if::` guards, computed bodies).

This slice compiles the **executable when-rule** form (F180): a rule whose
heading paren / `when::` field names a moment and whose body is a fenced
```python``` `trigger`/`guard`/`body` function. That grammar is a superset of
the tier-audit grammar `audit-plan.py` parses (which requires a
`(checked|sampled|stated|tracked)` tier suffix and drops `when::`/`if::`/the
python body), so the block parser here is Warden-specific, not a duplicate of
the audit resolver.

Scope of THIS slice (the `R-query-14` pilot, per F211 Success Criteria):
compile a ruleset's when-rules → their exact IR rows + a working emitted
module, worked end-to-end through `R-query-14`. Tier doc-rules in the same
ruleset (R-query-01..13) are parsed and recorded in the IR `deferred` list
rather than emitted — their declarative `check::`/agent-judge actions ride the
next slice. The multi-file `include::` DAG flatten (for a real trait umbrella)
reuses `audit-plan.flatten_umbrella` and is wired when a trait with a
non-empty `include::` is first compiled; the pilot ruleset is self-contained.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

IR_SCHEMA = 1

# ── ruleset / rule grammar ──────────────────────────────────────────────────

_RULESET_RE = re.compile(r"^(#+)\s+RULESET\s+(R-[\w-]+)\s*$")
# A RULE heading's trailing paren is EITHER a tier OR an executable `when::` —
# and is OPTIONAL: the documented field-style form (F211/F232) carries neither
# in the heading, taking its `when::`/`if::` from the body field lines instead
# (`rm.group(4)` is None for a paren-less heading; see `paren` below).
_RULE_RE = re.compile(r"^(#+)\s+RULE\s+(R-[\w-]+-\d+)\s+[—-]\s+(.*?)(?:\s*\((.*?)\))?\s*$")
# A loose superset of `_RULE_RE` used only to detect a malformed RULE heading
# that fails the strict grammar (Warden Audit 2026-07-12 W1) — so it warns
# instead of silently vanishing from `rule_idxs`.
_RULE_LOOSE_RE = re.compile(r"^#+\s+RULE\s+R-")
_FIELD_RE = re.compile(r"^([a-z][a-z_-]*)::\s*(.*)$")
_TIERS = {"checked", "sampled", "stated", "tracked"}
_PHASES = {"pre", "post"}
# Only these moment classes carry a pre/post phase segment (F209 / [[Warden
# Events]]): tool (pre/post) and skill (pre/post — v1 pre only). session, write,
# read, git, prompt, timer refine by their own parameter, NOT a phase — their
# second segment is the refinement (start/compact/stop, markdown, commit, …), so
# no phase is inserted or they'd compile to a moment the dispatcher never fires.
_PHASED_CLASSES = {"tool", "skill"}

# Declarative `if::` vocabulary (F210 Q1) — anything outside compiles to guard_py.
_GUARD_KEYS = {"git-aspect", "mode", "trait", "facet"}
_GUARD_OPS = [(" has ", "has"), (" in ", "in"), ("==", "eq")]

# Recognised entry-function names in a rule's python body (F180).
_ENTRY_DEFS = ("trigger", "guard", "body")

# The moment-class vocabulary ([[Warden Events]] / F209) — a `when::` whose
# class is outside this set compiles to a key no dispatcher ever fires (F232
# A3), so the compiler warns instead of silently burying the rule.
_MOMENT_CLASSES = {"session", "tool", "skill", "write", "read", "git",
                   "prompt", "timer"}


def _san(rule_id: str) -> str:
    """`R-query-14` → `R_query_14` for use in a Python identifier."""
    return rule_id.replace("-", "_")


def strip_ticks(val: str) -> str:
    """Strip a single surrounding backtick pair from a field value (F172 —
    `` where:: `file:{ANCHOR}/**/*.md` `` is the canonical authored form; the
    selector grammar inside is unchanged). Only a whole-expression wrap is
    stripped: values whose interior contains further backticks (prose with
    inline code spans) pass through untouched, as does the bare legacy form."""
    if len(val) >= 2 and val[0] == "`" and val[-1] == "`" and "`" not in val[1:-1]:
        return val[1:-1].strip()
    return val


def fence_mask(lines: list[str]) -> list[bool]:
    """Per-line ``` fence membership (marker lines count as inside). Structural
    matches — RULESET/RULE headings, `field::` lines, block-terminating headings
    — must skip fenced lines (F232 A1): a fenced sentinel is a shown example,
    not a live declaration. `_extract_py` still reads its ```python fences from
    the raw body; the mask suppresses only structural interpretation."""
    mask = []
    in_fence = False
    for ln in lines:
        if ln.lstrip().startswith("```"):
            mask.append(True)
            in_fence = not in_fence
        else:
            mask.append(in_fence)
    return mask


def extract_ruleset_block(lines: list[str], name: str) -> tuple[int, int, int] | None:
    """Return (start, end, level) line-span of `# RULESET <name>`; the block runs
    until the next heading of level <= its own. Fenced headings are ignored on
    both the open and the close scan."""
    mask = fence_mask(lines)
    start = -1
    level = 0
    for i, ln in enumerate(lines):
        if mask[i]:
            continue
        m = _RULESET_RE.match(ln)
        if m and m.group(2) == name:
            start, level = i, len(m.group(1))
            break
    if start < 0:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if mask[j]:
            continue
        hm = re.match(r"^(#+)\s+\S", lines[j])
        if hm and len(hm.group(1)) <= level:
            end = j
            break
    return start, end, level


_MEND_RE = re.compile(r"^(#+)\s+MEND\s+([\w-]+)\s*$")


def parse_mend_blocks(text: str, source: str) -> dict[str, dict]:
    """Every `### MEND <slug>` block in one file → {slug: {text, source}} (F280).

    The block runs to the next heading of the same or shallower level — the
    same sentinel grammar rulesets use. A blank-line terminator was considered
    and rejected: it breaks the moment a message wants a list followed by a
    sentence, which targeted fix instructions do constantly.
    """
    lines = text.splitlines()
    mask = fence_mask(lines)
    heads = [(i, len(m.group(1)), m.group(2))
             for i, ln in enumerate(lines)
             if not mask[i] and (m := _MEND_RE.match(ln))]
    out: dict[str, dict] = {}
    for start, level, slug in heads:
        end = len(lines)
        for j in range(start + 1, len(lines)):
            if mask[j]:
                continue
            hm = re.match(r"^(#+)\s+\S", lines[j])
            if hm and len(hm.group(1)) <= level:
                end = j
                break
        out[slug] = {"text": "\n".join(lines[start + 1:end]).strip(),
                     "source": source}
    return out


def _extract_py(body_lines: list[str], rid: str = "") -> str | None:
    """Return the source of the rule's fenced ```python block.

    F232 A5 hardening: an unclosed fence warns (the partial block is still
    used — better a syntax error at emit than a silently dead rule); multiple
    fences warn and the first ENTRY-DEF-BEARING block wins (an illustrative
    fence before the real implementation used to silently displace it)."""
    blocks: list[str] = []
    cur: list[str] = []
    inside = False
    for ln in body_lines:
        fence = ln.strip()
        if not inside and fence.startswith("```") and "python" in fence:
            inside, cur = True, []
            continue
        if inside and fence.startswith("```"):
            inside = False
            blocks.append("\n".join(cur))
            continue
        if inside:
            cur.append(ln)
    if inside:
        print(f"warden: WARNING — {rid or 'rule'}: unclosed ```python fence",
              file=sys.stderr)
        blocks.append("\n".join(cur))
    if not blocks:
        return None
    if len(blocks) > 1:
        entry_re = re.compile(rf"\bdef\s+(?:{'|'.join(_ENTRY_DEFS)})\s*\(")
        bearing = [b for b in blocks if entry_re.search(b)]
        pick = bearing[0] if bearing else blocks[0]
        print(f"warden: WARNING — {rid or 'rule'}: {len(blocks)} ```python "
              f"fences in one rule body; using the first "
              f"{'entry-def-bearing ' if bearing else ''}block",
              file=sys.stderr)
        return pick
    return blocks[0]


def _checker_names(root: Path, rel: str) -> dict:
    """What a corpus-declared module registers (F289): {"check": …, "fix": …}.

    Loaded by corpus-root-relative path with no assumption about where it sits —
    that assumption is precisely what this feature removed from the engine. A
    module that cannot be loaded warns ONCE, by path, rather than turning into
    one warning per ref that names it.

    The two registries are kept apart because conflating them produces false
    ghosts: the first cut of this check reported `R-doc-structure-01 — fix::
    breadcrumb_position` as registered nowhere, when it is a perfectly good
    FIXER. `FIXERS` is optional — plenty of rulesets check without repairing."""
    key = (str(root), rel)
    if key in _CHECKER_NAMES:
        return _CHECKER_NAMES[key]
    import importlib.util
    p = (root / rel).resolve()
    names: dict = {"check": set(), "fix": set()}
    if not p.is_file():
        print(f"warden: WARNING — import:: {rel} — no such file under {root}; "
              f"every check:: ref it was meant to supply now resolves nowhere",
              file=sys.stderr)
    else:
        try:
            spec = importlib.util.spec_from_file_location(f"_warden_ck_{abs(hash(rel))}", p)
            mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
            spec.loader.exec_module(mod)  # type: ignore[union-attr]
            reg = getattr(mod, "CHECKERS", None)
            if isinstance(reg, dict):
                names["check"] = set(reg)
            else:
                print(f"warden: WARNING — import:: {rel} defines no CHECKERS dict",
                      file=sys.stderr)
            fx = getattr(mod, "FIXERS", None)
            if isinstance(fx, dict):
                names["fix"] = set(fx)
        except Exception as e:
            print(f"warden: WARNING — import:: {rel} failed to load — "
                  f"{type(e).__name__}: {e}", file=sys.stderr)
    _CHECKER_NAMES[key] = names
    return names


_CHECKER_NAMES: dict = {}


def _warn_checker_registration(root: Path, rs_imports: dict, rs_refs: dict) -> None:
    """Verify each ruleset's `check::`/`fix::` refs against its OWN imports (F289).

    Execution uses one merged environment — refs are global names against a flat
    registry — but a purely global model lets a ruleset's refs resolve BY
    ACCIDENT, satisfied by an import a neighbouring ruleset declared. That is
    harmless inside one corpus and precisely the failure when the ruleset is
    extracted into a new one: it breaks, because its dependency was covered by a
    file it never named. Runtime is unchanged here; the declaration merely loses
    the ability to lie.

    A ref registered NOWHERE is the worse case and fails quietly by design: the
    doc-fire path decides mechanical-vs-agent with a membership test, so an
    unregistered name misses, the rule is promoted to agent judgment, and the
    `unknown checker` error never runs because the rule never reaches it. One
    typo turns a free deterministic check into a billed non-deterministic one
    that reports nothing."""
    if not any(rs_imports.values()):
        return  # a corpus that declares no checker modules has nothing to verify
    own: dict = {}
    everywhere: dict = {"check": set(), "fix": set()}
    for name, rels in rs_imports.items():
        s: dict = {"check": set(), "fix": set()}
        for rel in rels:
            got = _checker_names(root, rel)
            for k in ("check", "fix"):
                s[k] |= got[k]
                everywhere[k] |= got[k]
        own[name] = s
    for name, refs in sorted(rs_refs.items()):
        for rid, field, ref in refs:
            if ref in own.get(name, {}).get(field, ()):
                continue
            if ref in everywhere[field]:
                print(f"warden: WARNING — {rid}: {field}:: {ref} resolves only "
                      f"through another ruleset's import:: — {name} declares no "
                      f"module that defines it, so it breaks if extracted",
                      file=sys.stderr)
            else:
                print(f"warden: WARNING — {rid}: {field}:: {ref} is registered by "
                      f"no imported module — the rule silently becomes agent "
                      f"judgment rather than reporting an unknown checker",
                      file=sys.stderr)


def parse_ruleset(text: str, name: str, source: str) -> dict | None:
    """Parse `# RULESET <name>` into {name, where, description, includes, rules[]}.

    Each rule: {id, title, paren, when, where, ifs[], py_src, py_kind, tier}."""
    lines = text.splitlines()
    span = extract_ruleset_block(lines, name)
    if span is None:
        return None
    start, end, _ = span
    block = lines[start:end]
    # Fence membership within the block (starts at the unfenced RULESET
    # heading, so fence state opens False). Fenced lines never declare rules,
    # never terminate a rule body, and never carry live `field::` lines.
    bmask = fence_mask(block)

    rs = {"name": name, "where": None, "confirm": None, "description": None,
          "includes": [], "imports": [], "rules": [], "source": source}
    # Header fields: contiguous `field::` lines before the first rule/blank body.
    i = 1
    while i < len(block):
        s = block[i].strip()
        if not s:
            i += 1
            continue
        fm = _FIELD_RE.match(s)
        if not fm:
            break
        key, val = fm.group(1), fm.group(2).strip()
        if key == "include":
            targets = re.findall(r"\[\[([^\]|]+)", val)
            if not targets and val:
                # bare-name form (`include:: R-sugiyama, R-c4`) — documented
                # in DAS Ruleset but previously dropped silently (F232 A6).
                targets = [t.strip() for t in val.split(",") if t.strip()]
            rs["includes"] = targets
        elif key == "import":
            # F289 — corpus-root-relative Python providing this ruleset's
            # `check::` implementations. A distinct key from `include::`: one
            # flattens rules into a trait, the other executes code, and a reader
            # should not have to inspect a file extension to know which.
            rs["imports"].extend(t for t in re.split(r"[,\s]+", val) if t.strip())
        elif key == "where":
            rs["where"] = strip_ticks(val) or None
        elif key == "confirm":
            # F314/F601 — grading authority for the whole set (`user`); a rule
            # may override. Carried so a corpus test can read it with the same
            # parser that compiles, and audit-plan's `effective_confirm` applies.
            rs["confirm"] = strip_ticks(val) or None
        elif key == "description":
            rs["description"] = val or None
        i += 1

    # Rules: each `### RULE …` heading + its body up to the next RULE / higher heading.
    rule_idxs = []
    for j, ln in enumerate(block):
        if bmask[j]:
            continue
        if _RULE_RE.match(ln):
            rule_idxs.append(j)
        elif _RULE_LOOSE_RE.match(ln):
            # Audit W1: a heading that starts a RULE but fails the strict
            # grammar used to vanish from `rule_idxs` with no trace.
            print(f"warden: WARNING — {source}: malformed RULE heading "
                  f"(fails to parse, dropped): {ln.strip()!r}", file=sys.stderr)
    for j in rule_idxs:
        rm = _RULE_RE.match(block[j])
        assert rm is not None  # j came from a matching line
        rlevel = len(rm.group(1))
        # body spans to the next RULE heading, or a heading of level <= this rule's.
        stop = len(block)
        for jj in range(j + 1, len(block)):
            if bmask[jj]:
                continue
            if _RULE_RE.match(block[jj]):
                stop = jj
                break
            hm = re.match(r"^(#+)\s+\S", block[jj])
            if hm and len(hm.group(1)) <= rlevel:
                stop = jj
                break
        body = block[j + 1:stop]
        body_mask = bmask[j + 1:stop]
        # A paren-less heading (field-style rule, F211/F232) leaves group(4)
        # None — its when/tier come from the body `when::`/`if::` field lines
        # parsed below, not the heading.
        paren = (rm.group(4) or "").strip()
        rule = {
            "id": rm.group(2), "title": rm.group(3).strip(), "paren": paren,
            "when": None, "where": None, "ifs": [], "tier": None, "check": None,
            "fix": None, "py_src": _extract_py(body, rm.group(2)),
            "py_kind": None, "py_kinds": [], "mend": None, "confirm": None,
        }
        # Paren is a tier or an executable `when::`.
        if paren in _TIERS:
            rule["tier"] = paren
        elif paren.startswith("when::"):
            rule["when"] = paren[len("when::"):].strip()
        # Body field lines refine when/where/if. Fenced lines are examples —
        # a `when::` shown inside a fence must not re-key the rule.
        for ln, fenced in zip(body, body_mask):
            if fenced:
                continue
            fm = _FIELD_RE.match(ln.strip())
            if not fm:
                continue
            key, val = fm.group(1), fm.group(2).strip()
            if key == "when":
                rule["when"] = val
            elif key == "where":
                rule["where"] = strip_ticks(val)
            elif key == "if":
                # strip_ticks like where:: (T007) — a backtick-wrapped guard
                # used to compile the ticks into the emitted function, a
                # SyntaxError that broke the whole rules_all.py module.
                rule["ifs"].append(strip_ticks(val))
            elif key == "check":
                rule["check"] = val
            elif key == "confirm":
                rule["confirm"] = strip_ticks(val) or None
            elif key == "fix":
                rule["fix"] = val
            elif key == "mend":
                # F280: the slug of the MEND block that teaches this rule's
                # remediation. The reference lives INSIDE the rule so it
                # travels with a renumber — nothing ever points at a rule id.
                rule["mend"] = strip_ticks(val)
        if rule["py_src"]:
            # ALL entry defs present, not just the first (F232 A4 — a rule
            # authoring both `def guard` and `def body` used to wire only the
            # guard, silently dropping the body).
            rule["py_kinds"] = [n for n in _ENTRY_DEFS
                                if re.search(rf"\bdef\s+{n}\s*\(", rule["py_src"])]
            rule["py_kind"] = rule["py_kinds"][0] if rule["py_kinds"] else None
        rs["rules"].append(rule)
    return rs


# ── clause-split (per rule → IR row) ────────────────────────────────────────

def canonical_moment(when_val: str) -> tuple[str, str]:
    """Normalise a `when::` value to its canonical moment path + phase.

    Only the **phased classes** (`tool`, `skill`) take a pre/post segment: an
    explicit phase is honoured; a bare `tool:<name>` defaults to `post` and a
    bare `skill:<name>` to `pre` (F209). The unphased classes (`session`,
    `write`/`read`, `git`, `prompt`, `timer`) refine by their own parameter and
    are returned **unchanged** — inserting a phase would compile them to a moment
    the live dispatcher never fires. Their phase field is `post` (observational).
    """
    # Strip a trailing `# comment` (F232 A3 — `when:: tool:pre  # note` used
    # to compile the comment into the moment key, silently killing the rule).
    when_val = when_val.split("#", 1)[0].strip()
    parts = when_val.split(":")
    cls = parts[0]
    if cls not in _PHASED_CLASSES:
        return when_val, "post"
    if len(parts) >= 2 and parts[1] in _PHASES:
        # v1 ships `skill:pre` only — an authored `skill:post` is accepted and
        # treated as `skill:pre` (F209 Q3; the post ladder is V2/V3). Keying it
        # verbatim would orphan the rule: the live dispatcher never fires a
        # skill:post moment, so it could never run.
        if cls == "skill" and parts[1] == "post":
            return ":".join([cls, "pre"] + parts[2:]), "pre"
        return when_val, parts[1]
    phase = "post" if cls == "tool" else "pre"   # tool→post, skill→pre (F209)
    return ":".join([cls, phase] + parts[1:]), phase


def parse_if(expr: str) -> dict | None:
    """A declarative `if::` guard {key, op, value} over the frozen vocabulary,
    or None (→ compiles to a guard_py function)."""
    for token, op in _GUARD_OPS:
        if token in expr:
            lhs, rhs = expr.split(token, 1)
            key = lhs.strip()
            if key in _GUARD_KEYS:
                val = rhs.strip()
                if val.startswith("[") and val.endswith("]"):
                    value = [v.strip().strip("'\"") for v in val[1:-1].split(",") if v.strip()]
                else:
                    value = val.strip("'\"")
                return {"key": key, "op": op, "value": value}
            return None
    return None


def _kinds(rule: dict) -> list[str]:
    """The rule's entry-def kinds, tolerating synthetic rule dicts that carry
    only the legacy single `py_kind`."""
    kinds = rule.get("py_kinds")
    if kinds is None:
        kinds = [rule["py_kind"]] if rule.get("py_kind") else []
    return kinds


def compile_rule(rule: dict, ruleset: dict) -> dict:
    """One parsed rule → its IR row (F211 § A rule row)."""
    rid = rule["id"]
    row: dict = {
        "id": rid,
        "source": f"{ruleset['source']}#RULESET {ruleset['name']}",
        "tier": rule["tier"],
        "phase": None, "moment": None, "where": None,
        "guards": [], "guard_py": None, "action": None, "body_py": None,
        "mend": rule.get("mend"),
    }
    if rule["when"] is not None and not rule["when"].strip():
        # F232 A8: an empty `when::` used to silently reclassify the rule as
        # a doc-rule — almost certainly not what the author meant.
        print(f"warden: WARNING — {rid}: empty when:: — rule compiles as a "
              "doc-rule, not a moment rule", file=sys.stderr)
    if rule["when"]:
        moment, phase = canonical_moment(rule["when"])
        row["moment"], row["phase"] = moment, phase
        cls = moment.split(":", 1)[0]
        if cls not in _MOMENT_CLASSES:
            # F232 A3: a typo'd class compiles to a key no dispatcher fires.
            print(f"warden: WARNING — {rid}: unknown moment class '{cls}' in "
                  f"when:: '{rule['when']}' — rule can never fire",
                  file=sys.stderr)
        # A when-rule's place-residual is its OWN `where::` (rare); the ruleset's
        # doc-selector governs the tier doc-rules, not the moment rules.
        # T633 (B): fire enforces this per-rule glob as a place filter; the
        # header glob deliberately does NOT flow here. A moment rule left with
        # no scoping at all under a scoped header reads as covered while
        # firing everywhere — the R-ha shape — so that exact case warns.
        row["where"] = rule["where"]
        if (ruleset.get("where") and not rule["where"] and not rule["ifs"]
                and "guard" not in _kinds(rule)):
            print(f"warden: WARNING — {rid}: the ruleset-header where:: is a "
                  "doc-selector and does not scope this moment rule — add a "
                  "per-rule where:: (enforced at fire time) or an if:: guard",
                  file=sys.stderr)
    else:
        # doc-audit tier rule: where-major (no runtime moment), post-phase. Its
        # action delegates to a checker primitive (`check::`), is agent-judged
        # (`stated` / a `checked` rule with no ref), or is merely recorded
        # (`tracked`). The checker registry is audit-plan's — the Warden engine
        # references it by name, staying adapter-isolated from the checker impl.
        row["phase"] = "post"
        row["where"] = rule["where"] or ruleset["where"]
        if rule["check"]:
            parts = rule["check"].split()
            row["action"] = {"kind": "check", "ref": parts[0], "args": parts[1:]}
            # F004/M4a: the mechanical fixer reference (on-write auto-fix);
            # execution stays audit-plan's (`run_fixer`), referenced by name.
            if rule.get("fix"):
                row["fix"] = rule["fix"]
        elif rule["tier"] == "tracked":
            row["action"] = {"kind": "track"}
        else:
            row["action"] = {"kind": "judge"}

    # if:: → declarative guards + a residual guard_py. An authored python
    # guard also earns the guard_py slot even with no residual `if::` (F215 —
    # previously such a guard was parsed but never wired to fire).
    residual_if = []
    for expr in rule["ifs"]:
        g = parse_if(expr)
        if g is not None:
            row["guards"].append(g)
        else:
            residual_if.append(expr)
    kinds = _kinds(rule)
    if residual_if or "guard" in kinds:
        row["guard_py"] = f"guard_{_san(rid)}"

    # body: a python trigger/body computes its output → body_py. Checked
    # against ALL entry defs (F232 A4) — a rule with both `def guard` and
    # `def body` wires both slots.
    if "trigger" in kinds or "body" in kinds:
        row["body_py"] = f"body_{_san(rid)}"

    # F217: a statically-visible `agent.turn` / `agent.response` reference
    # marks the rule turn-bearing — it is skipped wholesale for an unbound
    # (R4) agent and deduped once-per-(rule, turn) by the daemon.
    content = " ".join(rule["ifs"]) + " " + (rule.get("py_src") or "")
    if "agent.turn" in content or "agent.response" in content:
        row["turn_bearing"] = True
    # F215: a `file.` reference marks the rule file-bearing — at fire time the
    # engine binds `ctx.file` to a per-(rule, event-file) FileView whose
    # `.diff` is the change since this rule last evaluated the file.
    if "file." in content:
        row["file_bearing"] = True
    return row


# The names a residual `if::` may read — the documented interpretation
# environment ([[Warden Semantics]]), all bound into the synthesised guard.
_GUARD_ENV_NAMES = {"ctx", "file", "agent", "event", "anchor", "git",
                    "re", "json", "datetime", "today", "now"}


def _warn_unknown_guard_names(rule: dict, residual: list[str]) -> None:
    """Audit 2026-07-12 W5 (compile-time half): an `if::` referencing a name
    outside the guard environment raises NameError at fire time, which the
    fail-safe `except` converts to a silent never-fire — an authoring error
    worth surfacing when it is cheap to see."""
    import ast
    import builtins
    known = _GUARD_ENV_NAMES | set(dir(builtins))
    for expr in residual:
        try:
            tree = ast.parse(expr, mode="eval")
        except SyntaxError:
            print(f"warden: WARNING — {rule['id']}: if:: {expr!r} is not a "
                  "valid expression — guard will break the emitted module",
                  file=sys.stderr)
            continue
        loads = {n.id for n in ast.walk(tree)
                 if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
        # names the expression binds itself (comprehension targets, lambda
        # args) are in scope at runtime — never flag them
        bound = {n.id for n in ast.walk(tree)
                 if isinstance(n, ast.Name) and not isinstance(n.ctx, ast.Load)}
        bound |= {a.arg for a in ast.walk(tree) if isinstance(a, ast.arg)}
        unknown = sorted(loads - bound - known)
        if unknown:
            print(f"warden: WARNING — {rule['id']}: if:: references name(s) "
                  f"outside the guard environment: {', '.join(unknown)} — "
                  "guard will evaluate False", file=sys.stderr)


def synth_guard_src(rule: dict) -> str:
    """Synthesise a guard function from a rule's residual `if::` expressions
    (F215). Historically a non-vocabulary `if::` earned a `guard_py` NAME in
    the IR but no emitted function unless the rule also authored a python
    guard — the rule could then never fire. The synthesised guard evaluates
    the residual conjunction against the fire ctx; any error is False
    (fail-safe: a broken gate suppresses the rule, never breaks the moment).

    Audit 2026-07-12 W5: the guard scope binds the FULL documented `if::`
    environment — `event`/`anchor`/`git`/`re`/`json`/`today`/`now`, not just
    `file` and `agent`; a spec-legal `if:: event.target …` used to NameError
    into a silent False.

    When the rule ALSO authors its own `def guard(…)`, that function is
    emitted under `guard_<id>__authored` and the synthesised guard requires
    both it and the residual conjunction."""
    residual = [e for e in rule["ifs"] if parse_if(e) is None]
    _warn_unknown_guard_names(rule, residual)
    conj = " and ".join(f"({e})" for e in residual) or "True"
    call = f" and guard_{_san(rule['id'])}__authored(ctx)" \
        if "guard" in _kinds(rule) else ""
    return (
        "def guard(ctx):\n"
        "    import datetime\n"
        "    import json\n"
        "    import re\n"
        "    file = getattr(ctx, 'file', None)\n"
        "    agent = getattr(ctx, 'agent', None)\n"
        "    event = getattr(ctx, 'event', None)\n"
        "    anchor = getattr(ctx, 'anchor', None)\n"
        "    git = getattr(ctx, 'git', None)\n"
        "    today = datetime.date.today()\n"
        "    now = datetime.datetime.now()\n"
        "    try:\n"
        f"        return bool({conj}){call}\n"
        "    except Exception:\n"
        "        return False\n"
    )


# ── emit ────────────────────────────────────────────────────────────────────

_ENTRY_DEF_RE = re.compile(rf"^(\s*)def\s+({'|'.join(_ENTRY_DEFS)})\s*\(")


def _split_src(src: str) -> tuple[list[str], list[str], dict, list[str]]:
    """Split a rule's python block into (imports, preamble, entry-def blocks,
    entry order). An entry-def block runs from its `def trigger/guard/body(`
    line to the next entry-def line (or EOF); imports and preamble are the
    lines before the first entry def."""
    imports: list[str] = []
    pre: list[str] = []
    entries: dict = {}
    order: list[str] = []
    cur = None
    for ln in src.splitlines():
        m = _ENTRY_DEF_RE.match(ln)
        if m:
            cur = m.group(2)
            entries[cur] = [ln]
            order.append(cur)
            continue
        if cur is None:
            if re.match(r"^\s*(import |from )\S", ln):
                imports.append(ln)
            else:
                pre.append(ln)
        else:
            entries[cur].append(ln)
    return imports, pre, entries, order


def _encapsulate(src: str, fn: str, imports: list[str], entry: str | None = None) -> str:
    """Turn one rule's python block into a single self-contained function `fn`.

    Imports are hoisted (de-duplicated into `imports`); any module-level
    preamble (helper constants/regexes the entry function references) is moved
    *inside* the function as locals — so two rulesets that both define a
    `PUSHCOMMIT` at corpus scale never collide. `entry` names WHICH entry def
    (`trigger`/`guard`/`body`) becomes `fn` — sibling entry defs in the same
    block are dropped from this emission (each gets its own pass; F232 A4 —
    previously only the first def was renamed and the second leaked verbatim
    to module scope, shadowing across rules)."""
    imps, pre, entries, order = _split_src(src)
    for ln in imps:
        if ln not in imports:
            imports.append(ln)
    name = entry if entry is not None else (order[0] if order else None)
    if name is None or name not in entries:
        # no entry def — emit the raw block (legacy tolerance; nothing to rename)
        return src.strip("\n")
    block = entries[name]
    head = _ENTRY_DEF_RE.sub(rf"\1def {fn}(", block[0], count=1)
    out = [head]                          # the `def fn(ctx):` line
    for p in pre:                         # module-level preamble → function locals
        out.append("    " + p if p.strip() else "")
    out.extend(block[1:])                 # original (already-indented) body
    return "\n".join(out).strip("\n")


def rule_emissions(rule: dict, row: dict) -> list[tuple[str, str, str | None]]:
    """The (source, function-name, entry-def) triples one rule contributes to
    the emitted module: its authored body/trigger, its authored guard, and/or
    the guard synthesised from residual `if::` expressions (F215)."""
    kinds = _kinds(rule)
    out: list[tuple[str, str, str | None]] = []
    if row["body_py"]:
        entry = "trigger" if "trigger" in kinds else "body"
        out.append((rule["py_src"], row["body_py"], entry))
    if row["guard_py"]:
        has_residual = any(parse_if(e) is None for e in rule["ifs"])
        if "guard" in kinds:
            if has_residual:
                out.append((rule["py_src"], row["guard_py"] + "__authored", "guard"))
                out.append((synth_guard_src(rule), row["guard_py"], None))
            else:
                out.append((rule["py_src"], row["guard_py"], "guard"))
        else:
            out.append((synth_guard_src(rule), row["guard_py"], None))
    return out


def emit_module(anchor: str, py_rules: list[tuple[dict, dict]]) -> str:
    """Emit `rules_<anchor>.py`: one self-contained function per python-bearing
    rule (`body_<id>` / `guard_<id>`), imports hoisted + de-duplicated."""
    imports: list[str] = []
    bodies: list[str] = []
    for rule, row in py_rules:
        for src, fn, entry in rule_emissions(rule, row):
            bodies.append(_encapsulate(src, fn, imports, entry))
    parts = [
        "# GENERATED by warden_compile.py — do not edit.",
        "# Source rulesets are authoritative; regenerate on rule change.",
        f'# anchor: {anchor}',
        "",
    ]
    parts += imports + ["", ""]
    parts.append("\n\n\n".join(bodies))
    return "\n".join(parts).rstrip() + "\n"


def compile_ruleset(rs: dict, anchor: str) -> tuple[dict, str, dict]:
    """Compile a parsed ruleset → (ir, module_src, stats).

    Every rule is emitted: when-rules index into `moments` (fired at a runtime
    moment); tier doc-rules index into `doc_rules` (where-major, fired on the
    `/audit doc` pass by matching their `where` glob)."""
    trait = rs["name"][2:] if rs["name"].startswith("R-") else rs["name"]
    rules_ir: dict = {}
    moments: dict = {}
    doc_rules: list[str] = []
    py_rules: list[tuple[dict, dict]] = []
    for rule in rs["rules"]:
        # Duplicate-id policy: first definition wins, loudly — same policy as
        # compile_corpus (F232 A2; single-ruleset mode used to silently
        # last-win while corpus mode silently first-won).
        if rule["id"] in rules_ir:
            print(f"warden: WARNING — duplicate rule id {rule['id']} in "
                  f"RULESET {rs['name']} ({rs['source']}); first definition wins",
                  file=sys.stderr)
            continue
        row = compile_rule(rule, rs)
        rules_ir[rule["id"]] = row
        if row["moment"]:
            moments.setdefault(row["moment"], []).append(rule["id"])
        else:
            doc_rules.append(rule["id"])
        if rule["py_kind"] or row["guard_py"]:
            py_rules.append((rule, row))
    trait_set = {trait: list(rules_ir.keys())}
    active_hash = hashlib.sha256(
        "|".join(sorted(rules_ir)).encode()).hexdigest()[:16]
    ir = {
        "schema": IR_SCHEMA,
        "root": None,
        "active_set_hash": active_hash,
        "moments": moments,
        "doc_rules": doc_rules,
        "traits": trait_set,
        "rules": rules_ir,
    }
    module_src = emit_module(anchor, py_rules)
    when_rules = sum(1 for r in rules_ir.values() if r["moment"])
    stats = {"when_rules": when_rules, "doc_rules": len(doc_rules),
             "py_rules": len(py_rules)}
    return ir, module_src, stats


# ── whole-corpus compile (consumes the warden_scan index) ────────────────────

def vault_root(scan_root: Path) -> Path:
    """The tree whose `.anchor` files count as trait declarations (F219).
    `WARDEN_VAULT` env wins; else the nearest ancestor named `kmr` (the
    knowledge-repo convention — the rule corpus lives inside the vault);
    else the scan root itself (self-contained repo)."""
    import os
    env = os.environ.get("WARDEN_VAULT", "").strip()
    if env:
        return Path(env).expanduser()
    for p in [scan_root, *scan_root.parents]:
        if p.name == "kmr":
            return p
    return scan_root


def _include_target(target: str) -> str:
    """An `include::` wiki-link target → the included ruleset's name.
    `DAS Brief#RULESET R-brief` → `R-brief`; `R-arch` → `R-arch` (file basename
    equals the ruleset name per the R-<slug> naming convention)."""
    if "#" in target:
        m = re.search(r"RULESET\s+(R-[\w-]+)", target.rsplit("#", 1)[1])
        if m:
            return m.group(1)
    return target.strip()


# The anchor-base trait's members (F229 A′) — traits every anchor carries by
# construction, over and above `anchor-base` itself. Documented for the user in
# `traits/Anchor Base.md` (keep the two in sync); stamped into the IR as
# `base_traits` so both dispatchers expand an anchor's effective traits from
# one compiled source.
ANCHOR_BASE_TRAITS = ("audit-on-write", "ob-remote-ops", "state-region", "ios",
                      "code-mirror", "pathguard", "backupguard",
                      "ob-browser-lease", "dispatch-guard", "ob-commons",
                      # Raw-automation hygiene (2026-08-28). Always-on for the
                      # same reason as ob-remote-ops and ob-browser-lease: the
                      # Mac's GUI is one surface per MACHINE, so an anchor-scoped
                      # version would leave every other anchor free to drive it.
                      "ob-osascript")


def anchor_trait_map(vault: Path) -> dict[Path, list[str]]:
    """Every anchor root under the vault → the traits its `.anchor` declares.
    One walk (~0.5 s vault-wide), shared by `declared_anchor_traits` (F219) and
    `governed_paths` (F297) so a compile never walks the vault twice."""
    import warden_fire as wf
    out: dict[Path, list[str]] = {}
    try:
        for dot in vault.rglob(".anchor"):
            try:
                out[dot.parent] = wf.read_anchor_traits(dot.parent)
            except OSError:
                continue
    except OSError:
        pass
    return out


def declared_anchor_traits(vault: Path, amap: dict | None = None) -> list[str]:
    """Every trait some `.anchor` under the vault declares, plus the implicit
    `anchor-base` — the ground truth the F219 reachability self-audit checks the
    compiled trait index against. Pass `amap` to reuse an already-walked
    `anchor_trait_map`. Warns on stderr when a `.anchor` explicitly declares
    `anchor-base` — it is applied by construction and must never be written
    into a traits list."""
    declared = {"anchor-base", *ANCHOR_BASE_TRAITS}
    for root, traits in (anchor_trait_map(vault) if amap is None else amap).items():
        # read_anchor_traits appends the implicit trait itself; a DOUBLE
        # occurrence means the file declares it explicitly.
        if traits.count("anchor-base") > 1:
            print(f"warden: WARNING — {root / '.anchor'} declares `anchor-base`; "
                  "it is implicit (applied by construction) — remove it",
                  file=sys.stderr)
        declared.update(traits)
    return sorted(declared)


# F297 leg 2 — the governed-path list, so a SCRIPT's writes are seen.
#
# Claude Code hooks fire on tool calls. A `PostToolUse` for Bash carries the
# command string and nothing about which files ran through it, so
# `python3 make_diagram.py` is invisible: there is no hook that reports "the
# agent wrote this file, by whatever means". Covering a generator's output means
# diffing the filesystem after Bash, and only one of the three ways to do that
# is affordable — measured on this vault, `git status --porcelain` costs
# 160-180 ms per Bash call and a live `rglob("*.svg")` costs 228 ms, while an
# mtime sweep over a KNOWN list of 124 paths costs 0.5 ms.
#
# What makes the cheap one possible is that discovery does not have to happen at
# fire time: the compile already walks the vault for `.anchor` files, so it
# resolves the governed set once and stamps it into the IR. The hook then only
# stats. The trade is that a file created after the last compile is not governed
# until the next one — an mtime sweep over a list cannot see a path that is not
# in the list.

_GLOB_EXT = re.compile(r"\*\.([A-Za-z0-9]+)")


def governed_extensions(traits: dict, rules: dict, doc_rules: list) -> dict[str, set[str]]:
    """trait → the non-markdown file extensions its doc-rules govern. A rule's
    `where` glob is the only declaration of what file types it reaches; markdown
    needs no entry, since the write hook has always seen markdown."""
    docset = set(doc_rules)
    out: dict[str, set[str]] = {}
    for trait, ids in traits.items():
        exts = {"." + e.lower()
                for rid in ids if rid in docset
                for e in _GLOB_EXT.findall((rules.get(rid) or {}).get("where") or "")
                if e.lower() not in ("md", "markdown")}
        if exts:
            out[trait] = exts
    return out


def governed_paths(vault: Path, amap: dict, traits: dict, rules: dict,
                   doc_rules: list) -> list[str]:
    """Every existing file a *declared* non-markdown doc-rule governs. A file is
    governed when the nearest anchor above it declares a trait whose doc-rules
    name its extension — the same ownership the fire path resolves, decided here
    once instead of per Bash call."""
    by_trait = governed_extensions(traits, rules, doc_rules)
    if not by_trait:
        return []
    per_anchor: dict[Path, set[str]] = {}
    for root, declared in amap.items():
        exts: set[str] = set()
        for t in {*declared, *ANCHOR_BASE_TRAITS, "anchor-base"}:
            exts |= by_trait.get(t, set())
        if exts:
            per_anchor[root] = exts
    if not per_anchor:
        return []
    roots = set(amap)
    found: set[str] = set()
    for ext in sorted(set().union(*per_anchor.values())):
        try:
            for p in vault.rglob("*" + ext):
                # `parents` is nearest-first, so the first anchor above the file
                # is the one that owns it — a sub-anchor's declaration wins over
                # its parent's, exactly as `find_anchor` resolves at fire time.
                owner = next((c for c in p.parents if c in roots), None)
                if owner is not None and ext in per_anchor.get(owner, ()):
                    found.add(str(p))
        except OSError:
            continue
    return sorted(found)


def compile_corpus(root: Path, index: dict, anchor: str = "all",
                   source_hash: str = "") -> tuple[dict, str, dict]:
    """Compile every ruleset the scan index lists under `root` into one combined
    IR + module. Rule ids are globally unique (`R-<slug>-NN`), so `rules`,
    `moments`, `doc_rules`, and per-trait `traits` merge by simple union. The
    per-anchor *active-set* (which of these a given `.anchor` actually adopts) is
    resolved at fire time by intersecting the anchor's declared traits — the
    corpus IR carries them all, keyed by trait."""
    merged_rules: dict = {}
    moments: dict = {}
    doc_rules: list[str] = []
    traits: dict = {}
    py_rules: list[tuple[dict, dict]] = []
    rs_includes: dict = {}   # ruleset name → include:: target ruleset names
    rs_rule_ids: dict = {}   # ruleset name → its own rule ids
    rs_has_rules: dict = {}  # ruleset name → carries rules (vs a catalog stub)
    rs_imports: dict = {}    # F289: ruleset name → import:: module paths
    rs_refs: dict = {}       # F289: ruleset name → [(rule id, field, checker name)]
    mend: dict = {}          # F280: mend slug → {text, source}
    files = errors = 0
    for entry in index.get("files", []):
        path = root / entry["path"]
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            errors += 1
            continue
        files += 1
        if entry.get("mend_names"):
            for slug, block in parse_mend_blocks(text, entry["path"]).items():
                if slug in mend:
                    # A slug is the join key rules point at, so two blocks
                    # answering to one name means some rule silently gets the
                    # wrong lesson. First wins, loudly (F280).
                    print(f"warden: WARNING — duplicate mend block '{slug}' in "
                          f"{entry['path']}; first definition "
                          f"({mend[slug]['source']}) wins", file=sys.stderr)
                    continue
                mend[slug] = block
        for name in entry.get("ruleset_names", []):
            rs = parse_ruleset(text, name, entry["path"])
            if rs is None:
                continue
            if name in rs_has_rules:
                # Whole-ruleset redefinition across files (F232 A2). The F133
                # catalog convention legitimately re-declares a ruleset as a
                # RULE-LESS stub (`# RULESET` heading + `include::` pointer at
                # the facet-embedded canonical body) — a stub is a pointer,
                # skipped silently; and a rule-bearing definition beats a stub
                # regardless of scan order. Two RULE-BEARING definitions are a
                # real authoring collision: first wins, loudly.
                if not rs["rules"]:
                    continue
                if rs_has_rules[name]:
                    print(f"warden: WARNING — duplicate ruleset {name} in "
                          f"{entry['path']}; first definition wins",
                          file=sys.stderr)
                    continue
                # prior definition was a stub — this one carries the body.
            rs_has_rules[name] = bool(rs["rules"])
            trait = name[2:] if name.startswith("R-") else name
            rs_includes[name] = [_include_target(t) for t in rs["includes"]]
            rs_rule_ids[name] = [r["id"] for r in rs["rules"]]
            rs_imports[name] = list(rs["imports"])
            # F289 registration is only meaningful for a `fix::` `compile_rule`
            # actually wires into the IR — and it wires `row["fix"]` ONLY when
            # the SAME rule also carries `check::` (see `compile_rule` below:
            # the `fix` assignment sits inside the `if rule["check"]:` branch).
            # A `fix::`-only rule (no `check::` on that rule — a resolution
            # move documented for an iterative repair loop, not a doc-fire
            # mechanical fixer) never reaches that branch; its `fix::` is
            # dead at compile time regardless of registration, so verifying
            # it here manufactured a warning against a value that could never
            # do anything either way (T172 — 5 ghost warnings on R-svg-jiggle).
            rs_refs[name] = [(r["id"], f, r[f].split()[0])
                             for r in rs["rules"] for f in ("check", "fix")
                             if r.get(f) and (f == "check" or r.get("check"))]
            # T175: the T172 exclusion above (a `fix::` with no `check::` on the
            # SAME rule never reaches `compile_rule`'s `row["fix"]` assignment)
            # is correct about the IR, but it left the authoring mistake itself
            # unflagged — a `fix::` declared alone reads as a wired auto-repair
            # and silently does nothing. Warn distinctly from the registration
            # warning above: this is never-wired, not merely unregistered.
            for rule in rs["rules"]:
                if rule.get("fix") and not rule.get("check"):
                    print(f"warden: WARNING — {rule['id']} declares fix:: "
                          f"{rule['fix'].split()[0]} with no check:: on the "
                          f"same rule; the ref is never wired", file=sys.stderr)
            for rule in rs["rules"]:
                if rule["id"] in merged_rules:
                    # First occurrence wins (stable) — but never silently
                    # (F232 A2): a redefinition means two authored rules share
                    # an id, and which one governs depended on scan order.
                    prev = merged_rules[rule["id"]]["source"]
                    cur = f"{entry['path']}#RULESET {name}"
                    if cur != prev:
                        print(f"warden: WARNING — duplicate rule id {rule['id']} "
                              f"in {cur}; first definition ({prev}) wins",
                              file=sys.stderr)
                    else:
                        print(f"warden: WARNING — duplicate rule id {rule['id']} "
                              f"within {cur}; first definition wins",
                              file=sys.stderr)
                    continue
                row = compile_rule(rule, rs)
                merged_rules[rule["id"]] = row
                if row["moment"]:
                    moments.setdefault(row["moment"], []).append(rule["id"])
                else:
                    doc_rules.append(rule["id"])
                traits.setdefault(trait, []).append(rule["id"])
                if rule["py_kind"] or row["guard_py"]:
                    py_rules.append((rule, row))
    # include:: composition (DAS Ruleset — acyclic depth-first flatten): an
    # umbrella's trait keys its own rules PLUS every included ruleset's rules,
    # transitively. Without this, "adopt the umbrella to pull all its rulesets"
    # was a documented no-op — every umbrella trait keyed zero rules (found by
    # the F218 SC check, 2026-07-05).
    def _closure(name: str, seen: set) -> list[str]:
        if name in seen:
            return []  # cycle / repeat guard
        seen.add(name)
        out = list(rs_rule_ids.get(name, []))
        for child in rs_includes.get(name, []):
            out.extend(_closure(child, seen))
        return out
    for name in rs_includes:
        if not rs_includes[name]:
            continue
        for child in rs_includes[name]:
            if child != name and child not in rs_rule_ids:
                # F232 A7: an include target that resolves to no scanned
                # ruleset (typo, heading-fragment miss) contributes zero rules
                # — say so instead of silently thinning the umbrella.
                print(f"warden: WARNING — ruleset {name} includes unknown "
                      f"ruleset '{child}' — contributes nothing",
                      file=sys.stderr)
        trait = name[2:] if name.startswith("R-") else name
        flat, have = [], set()
        for rid in _closure(name, set()):
            if rid not in have and rid in merged_rules:
                have.add(rid)
                flat.append(rid)
        if flat:
            traits[trait] = flat
    _warn_checker_registration(root, rs_imports, rs_refs)
    vault = vault_root(root)
    amap = anchor_trait_map(vault)
    declared = declared_anchor_traits(vault, amap)
    # T002: trait matching is exact-string, case-sensitive, and the identifier
    # convention is lowercase kebab. Two near-miss shapes are silent foot-guns:
    # (1) a declared trait matching a corpus key only case-insensitively
    #     (`Code` declared, corpus keys `code` → activates NO rules);
    # (2) case-variant declarations across .anchor files (`Track` here, `track`
    #     there → the two anchors activate different rule sets).
    corpus_by_lower = {k.lower(): k for k in traits}
    declared_by_lower: dict[str, list[str]] = {}
    for d in declared:
        declared_by_lower.setdefault(d.lower(), []).append(d)
        near = corpus_by_lower.get(d.lower())
        if near is not None and near != d:
            print(f"warden: WARNING — some .anchor declares trait `{d}` but the "
                  f"corpus keys `{near}`; matching is case-sensitive, so `{d}` "
                  f"activates NO rules — rename the declaration to `{near}`",
                  file=sys.stderr)
    for low, variants in declared_by_lower.items():
        if len(variants) > 1:
            print(f"warden: WARNING — trait `{low}` is declared with mixed "
                  f"casings across .anchor files ({', '.join(sorted(variants))}); "
                  f"matching is case-sensitive — normalize all to `{low}`",
                  file=sys.stderr)
    # F280 mend integrity. The whole point of pointing rule → slug (rather than
    # a mend block naming rule ids) is that a renumber cannot orphan a message;
    # what CAN still rot is a typo or a renamed/retired slug, so both directions
    # are checked here and nowhere else.
    # A mend slug is named for WHAT IT TELLS YOU, never numbered. A numbered
    # slug invites mirroring the rule's own number, and then two number spaces
    # drift against each other — harmless to the machine, wrong to read, and a
    # standing invitation to assume `mend-07` teaches `R-x-07`. Semantic names
    # also make the duplicate check useful: colliding on a phrase means two
    # authors described the same fix, which is worth knowing.
    for slug in sorted(mend):
        if re.match(r"^R-[\w-]+-\d+$", slug) or re.search(r"-\d+$", slug):
            print(f"warden: WARNING — mend block '{slug}' "
                  f"({mend[slug]['source']}) is numbered; name it for what it "
                  f"tells the reader to do (`log-location`, not `log-01`) so it "
                  f"never drifts against rule numbering", file=sys.stderr)

    referenced: set[str] = set()
    for rid, row in sorted(merged_rules.items()):
        slug = row.get("mend")
        if not slug:
            continue
        if slug in mend:
            referenced.add(slug)
        else:
            # A rule promising a lesson the corpus cannot produce would emit a
            # `mend` marker the agent then cannot cash in — the one failure the
            # marker must never have.
            print(f"warden: WARNING — {rid} declares `mend:: {slug}` but no "
                  f"MEND block defines it — the marker would be unresolvable",
                  file=sys.stderr)
            row["mend"] = None
    for slug in sorted(set(mend) - referenced):
        print(f"warden: WARNING — mend block '{slug}' ({mend[slug]['source']}) "
              f"is referenced by no rule — dead teaching material",
              file=sys.stderr)

    active_hash = hashlib.sha256("|".join(sorted(merged_rules)).encode()).hexdigest()[:16]
    ir = {
        "schema": IR_SCHEMA,
        "root": str(root),
        "source_hash": source_hash,        # the scan-index content hash — the recompile cache key
        "active_set_hash": active_hash,
        "moments": moments,
        "doc_rules": doc_rules,
        "traits": traits,
        "rules": merged_rules,
        # F219: the wiring snapshot the trait-reachability self-audit reads —
        # traits actually declared by `.anchor` files under the vault.
        "declared_traits": declared,
        # F229 A′: the anchor-base trait's members — both dispatchers extend an
        # anchor's effective traits with these, so base membership is compiled
        # policy, not per-hook hardcoding.
        "base_traits": list(ANCHOR_BASE_TRAITS),
        # F297 leg 2: the non-markdown files a declared doc-rule governs. The
        # post-Bash sweep stats this list to catch a file a SCRIPT wrote, which
        # no tool-call hook can see. Discovery is the expensive half and it is
        # paid here, once.
        "governed_paths": governed_paths(vault, amap, traits, merged_rules, doc_rules),
        # F280: remediation messages, keyed by hand-chosen slug. Rules carry
        # `mend:: <slug>`; `warden mend <rule-id>` resolves rule → slug → text.
        "mend": mend,
    }
    module_src = emit_module(anchor, py_rules)
    stats = {"files": files, "read_errors": errors, "rulesets": sum(
        len(e.get("ruleset_names", [])) for e in index.get("files", [])),
        "rules": len(merged_rules), "moments": len(moments),
        "doc_rules": len(doc_rules), "py_rules": len(py_rules)}
    return ir, module_src, stats


# ── CLI ──────────────────────────────────────────────────────────────────────

def cached_source_hash(out: Path) -> str | None:
    """The `source_hash` recorded in a prior compile's IR, or None. The recompile
    cache key: equal to the current scan-index hash ⇒ the artifacts are current."""
    fp = out / "rules-ir.json"
    try:
        return json.loads(fp.read_text(encoding="utf-8")).get("source_hash")
    except (OSError, ValueError):
        return None


def _write_artifacts(out: Path, anchor: str, ir: dict, module_src: str) -> tuple[Path, Path]:
    import os
    out.mkdir(parents=True, exist_ok=True)
    ir_path = out / "rules-ir.json"
    mod_path = out / f"rules_{anchor}.py"
    # Atomic per-file (tmp + os.replace), MODULE first, IR last (F232 B5): a
    # reader that keys freshness on the IR then never loads a new IR against
    # an old module, and a crash mid-write never leaves a truncated artifact.
    for path, data in ((mod_path, module_src),
                       (ir_path, json.dumps(ir, indent=2, sort_keys=True) + "\n")):
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(data, encoding="utf-8")
        os.replace(tmp, path)
    return ir_path, mod_path


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="warden-compile",
        description="Compile authored rulesets into rules-ir.json + rules_<anchor>.py.")
    ap.add_argument("--root", default=None,
                    help="corpus mode: compile every ruleset the scan index lists under this root")
    ap.add_argument("--index", default=None,
                    help="scan index path (corpus mode; default: <root>/.warden/rules-index.json)")
    ap.add_argument("--file", default=None, help="single-ruleset mode: file holding the # RULESET block")
    ap.add_argument("--name", default=None, help="single-ruleset mode: ruleset id, e.g. R-query")
    ap.add_argument("--anchor", default=None, help="module/anchor name (default: ruleset trait, or 'all')")
    ap.add_argument("--out", default=None, help="output dir (default: <root|file-dir>/.warden)")
    ap.add_argument("--force", action="store_true", help="corpus mode: recompile even on a cache hit")
    ap.add_argument("--stats", action="store_true", help="print compile stats to stderr")
    args = ap.parse_args(argv)

    if args.root:
        import warden_scan
        root = Path(args.root).expanduser().resolve()
        if not root.is_dir():
            ap.error(f"root is not a directory: {root}")
        index_path = Path(args.index).expanduser() if args.index else (root / ".warden" / "rules-index.json")
        prior_bearing, prior_seen = warden_scan.load_index(str(index_path))
        files, seen, _ = warden_scan.build_index(str(root), prior_bearing, prior_seen, rescan=False)
        index = {"root": str(root), "files": files, "seen": seen}
        # Cache key = ruleset content ⊕ compiler source ⊕ declared anchor
        # traits (F232 A9 — the md-only key went stale on compiler-code edits
        # and `.anchor` trait changes, both of which move the IR).
        salt = hashlib.sha256()
        salt.update(Path(__file__).read_bytes())
        salt.update("|".join(declared_anchor_traits(vault_root(root))).encode())
        source_hash = f"{warden_scan.index_hash(files)}:{salt.hexdigest()[:12]}"
        anchor = args.anchor or "all"
        out = Path(args.out).expanduser() if args.out else (root / ".warden")

        # Recompile cache: the compiled artifacts are a pure function of the
        # ruleset content, so an unchanged scan-index hash ⇒ they are current.
        if not args.force and cached_source_hash(out) == source_hash:
            if args.stats:
                print(f"warden-compile [corpus] cache hit ({source_hash}) — skipped recompile",
                      file=sys.stderr)
            print(out / "rules-ir.json")
            print(out / f"rules_{anchor}.py")
            return 0

        ir, module_src, stats = compile_corpus(root, index, anchor, source_hash)
        ir_path, mod_path = _write_artifacts(out, anchor, ir, module_src)
        if args.stats:
            print(f"warden-compile [corpus] {stats['rules']} rules from {stats['rulesets']} "
                  f"rulesets / {stats['files']} files — {stats['moments']} moment(s), "
                  f"{stats['doc_rules']} doc-rule(s), {stats['py_rules']} python",
                  file=sys.stderr)
        print(ir_path)
        print(mod_path)
        return 0

    if not (args.file and args.name):
        ap.error("provide --root (corpus mode) or both --file and --name (single-ruleset mode)")
    path = Path(args.file).expanduser().resolve()
    if not path.is_file():
        ap.error(f"not a file: {path}")
    rs = parse_ruleset(path.read_text(encoding="utf-8"), args.name, path.name)
    if rs is None:
        ap.error(f"no # RULESET {args.name} block in {path.name}")
    trait = args.name[2:] if args.name.startswith("R-") else args.name
    anchor = args.anchor or trait
    ir, module_src, stats = compile_ruleset(rs, anchor)
    out = Path(args.out).expanduser() if args.out else (path.parent / ".warden")
    ir_path, mod_path = _write_artifacts(out, anchor, ir, module_src)
    if args.stats:
        print(f"warden-compile {args.name}: {stats['when_rules']} when-rule(s), "
              f"{stats['doc_rules']} doc-rule(s), {stats['py_rules']} python", file=sys.stderr)
    print(ir_path)
    print(mod_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
