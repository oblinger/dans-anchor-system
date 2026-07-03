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
# A RULE heading's trailing paren is EITHER a tier OR an executable `when::`.
_RULE_RE = re.compile(r"^(#+)\s+RULE\s+(R-[\w-]+-\d+)\s+[—-]\s+(.*?)\s*\((.*?)\)\s*$")
_FIELD_RE = re.compile(r"^([a-z][a-z_-]*)::\s*(.*)$")
_TIERS = {"checked", "sampled", "stated", "tracked"}
_PHASES = {"pre", "post"}

# Declarative `if::` vocabulary (F210 Q1) — anything outside compiles to guard_py.
_GUARD_KEYS = {"git-aspect", "mode", "trait", "facet"}
_GUARD_OPS = [(" has ", "has"), (" in ", "in"), ("==", "eq")]

# Recognised entry-function names in a rule's python body (F180).
_ENTRY_DEFS = ("trigger", "guard", "body")


def _san(rule_id: str) -> str:
    """`R-query-14` → `R_query_14` for use in a Python identifier."""
    return rule_id.replace("-", "_")


def extract_ruleset_block(lines: list[str], name: str) -> tuple[int, int, int] | None:
    """Return (start, end, level) line-span of `# RULESET <name>`; the block runs
    until the next heading of level <= its own."""
    start = -1
    level = 0
    for i, ln in enumerate(lines):
        m = _RULESET_RE.match(ln)
        if m and m.group(2) == name:
            start, level = i, len(m.group(1))
            break
    if start < 0:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        hm = re.match(r"^(#+)\s+\S", lines[j])
        if hm and len(hm.group(1)) <= level:
            end = j
            break
    return start, end, level


def _extract_py(body_lines: list[str]) -> str | None:
    """Return the source of the first fenced ```python block in `body_lines`."""
    out, inside = [], False
    for ln in body_lines:
        fence = ln.strip()
        if not inside and fence.startswith("```") and "python" in fence:
            inside = True
            continue
        if inside and fence.startswith("```"):
            return "\n".join(out)
        if inside:
            out.append(ln)
    return None


def parse_ruleset(text: str, name: str, source: str) -> dict | None:
    """Parse `# RULESET <name>` into {name, where, description, includes, rules[]}.

    Each rule: {id, title, paren, when, where, ifs[], py_src, py_kind, tier}."""
    lines = text.splitlines()
    span = extract_ruleset_block(lines, name)
    if span is None:
        return None
    start, end, _ = span
    block = lines[start:end]

    rs = {"name": name, "where": None, "description": None,
          "includes": [], "rules": [], "source": source}
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
            rs["includes"] = re.findall(r"\[\[([^\]|]+)", val)
        elif key == "where":
            rs["where"] = val or None
        elif key == "description":
            rs["description"] = val or None
        i += 1

    # Rules: each `### RULE …` heading + its body up to the next RULE / higher heading.
    rule_idxs = [j for j, ln in enumerate(block) if _RULE_RE.match(ln)]
    for j in rule_idxs:
        rm = _RULE_RE.match(block[j])
        assert rm is not None  # j came from a matching line
        rlevel = len(rm.group(1))
        # body spans to the next RULE heading, or a heading of level <= this rule's.
        stop = len(block)
        for jj in range(j + 1, len(block)):
            if _RULE_RE.match(block[jj]):
                stop = jj
                break
            hm = re.match(r"^(#+)\s+\S", block[jj])
            if hm and len(hm.group(1)) <= rlevel:
                stop = jj
                break
        body = block[j + 1:stop]
        paren = rm.group(4).strip()
        rule = {
            "id": rm.group(2), "title": rm.group(3).strip(), "paren": paren,
            "when": None, "where": None, "ifs": [], "tier": None, "check": None,
            "py_src": _extract_py(body), "py_kind": None,
        }
        # Paren is a tier or an executable `when::`.
        if paren in _TIERS:
            rule["tier"] = paren
        elif paren.startswith("when::"):
            rule["when"] = paren[len("when::"):].strip()
        # Body field lines refine when/where/if.
        for ln in body:
            fm = _FIELD_RE.match(ln.strip())
            if not fm:
                continue
            key, val = fm.group(1), fm.group(2).strip()
            if key == "when":
                rule["when"] = val
            elif key == "where":
                rule["where"] = val
            elif key == "if":
                rule["ifs"].append(val)
            elif key == "check":
                rule["check"] = val
        if rule["py_src"]:
            for name_ in _ENTRY_DEFS:
                if re.search(rf"\bdef\s+{name_}\s*\(", rule["py_src"]):
                    rule["py_kind"] = name_
                    break
        rs["rules"].append(rule)
    return rs


# ── clause-split (per rule → IR row) ────────────────────────────────────────

def canonical_moment(when_val: str) -> tuple[str, str]:
    """Normalise a `when::` value to a phase-explicit moment path + its phase.
    Honours an explicit phase segment; else applies the F209 default
    (`tool`→post, everything else→pre)."""
    parts = when_val.split(":")
    if len(parts) >= 2 and parts[1] in _PHASES:
        return when_val, parts[1]
    phase = "post" if parts[0] == "tool" else "pre"
    return ":".join([parts[0], phase] + parts[1:]), phase


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


def compile_rule(rule: dict, ruleset: dict) -> dict:
    """One parsed rule → its IR row (F211 § A rule row)."""
    rid = rule["id"]
    row: dict = {
        "id": rid,
        "source": f"{ruleset['source']}#RULESET {ruleset['name']}",
        "tier": rule["tier"],
        "phase": None, "moment": None, "where": None,
        "guards": [], "guard_py": None, "action": None, "body_py": None,
    }
    if rule["when"]:
        moment, phase = canonical_moment(rule["when"])
        row["moment"], row["phase"] = moment, phase
        # A when-rule's place-residual is its OWN `where::` (rare); the ruleset's
        # doc-selector governs the tier doc-rules, not the moment rules.
        row["where"] = rule["where"]
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
        elif rule["tier"] == "tracked":
            row["action"] = {"kind": "track"}
        else:
            row["action"] = {"kind": "judge"}

    # if:: → declarative guards + a residual guard_py.
    residual_if = []
    for expr in rule["ifs"]:
        g = parse_if(expr)
        if g is not None:
            row["guards"].append(g)
        else:
            residual_if.append(expr)
    if residual_if:
        row["guard_py"] = f"guard_{_san(rid)}"

    # body: a python trigger/body computes its output → body_py.
    if rule["py_kind"] in ("trigger", "body"):
        row["body_py"] = f"body_{_san(rid)}"
    return row


# ── emit ────────────────────────────────────────────────────────────────────

def emit_module(anchor: str, py_rules: list[tuple[dict, dict]]) -> str:
    """Emit `rules_<anchor>.py`: the entry function per python-bearing rule,
    renamed to `body_<id>` / `guard_<id>`, imports hoisted + de-duplicated."""
    imports: list[str] = []
    bodies: list[str] = []
    for rule, row in py_rules:
        src = rule["py_src"]
        kept = []
        fn = row["body_py"] or row["guard_py"]
        for ln in src.splitlines():
            if re.match(r"^\s*(import |from )\S", ln):
                if ln not in imports:
                    imports.append(ln)
                continue
            kept.append(ln)
        block = "\n".join(kept).strip("\n")
        # rename the recognised entry def to the row's stable function name.
        block = re.sub(rf"\bdef\s+(?:{'|'.join(_ENTRY_DEFS)})\s*\(",
                       f"def {fn}(", block, count=1)
        bodies.append(block)
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
        row = compile_rule(rule, rs)
        rules_ir[rule["id"]] = row
        if row["moment"]:
            moments.setdefault(row["moment"], []).append(rule["id"])
        else:
            doc_rules.append(rule["id"])
        if rule["py_kind"]:
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


# ── CLI ──────────────────────────────────────────────────────────────────────

def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="warden-compile",
        description="Compile a ruleset's when-rules into rules-ir.json + rules_<anchor>.py.")
    ap.add_argument("--file", required=True, help="markdown file holding the # RULESET block")
    ap.add_argument("--name", required=True, help="ruleset id, e.g. R-query")
    ap.add_argument("--anchor", default=None, help="anchor name for the emitted module (default: ruleset trait)")
    ap.add_argument("--out", default=None, help="output dir (default: <file-dir>/.warden)")
    ap.add_argument("--stats", action="store_true", help="print compile stats to stderr")
    args = ap.parse_args(argv)

    path = Path(args.file).expanduser().resolve()
    if not path.is_file():
        ap.error(f"not a file: {path}")
    text = path.read_text(encoding="utf-8")
    rs = parse_ruleset(text, args.name, path.name)
    if rs is None:
        ap.error(f"no # RULESET {args.name} block in {path.name}")

    trait = args.name[2:] if args.name.startswith("R-") else args.name
    anchor = args.anchor or trait
    ir, module_src, stats = compile_ruleset(rs, anchor)

    out = Path(args.out).expanduser() if args.out else (path.parent / ".warden")
    out.mkdir(parents=True, exist_ok=True)
    ir_path = out / "rules-ir.json"
    mod_path = out / f"rules_{anchor}.py"
    ir_path.write_text(json.dumps(ir, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    mod_path.write_text(module_src, encoding="utf-8")

    if args.stats:
        print(f"warden-compile {args.name}: {stats['when_rules']} when-rule(s), "
              f"{stats['py_rules']} python body/guard, {stats['deferred']} deferred tier-rule(s)",
              file=sys.stderr)
    print(ir_path)
    print(mod_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
