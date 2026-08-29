#!/usr/bin/env python3
"""Warden moment dispatcher — the fire half of F211 (Rule compiler / installer).

Given a compiled anchor (`rules-ir.json` + `rules_<anchor>.py`, produced by
`warden_compile.py`) and a runtime moment, `fire()` runs **only** that moment's
rules and returns their steers. This is the hot path the ms budget rides on:

  fire(moment) = a dict lookup on `ir["moments"][moment]`  → candidate rule ids
               → filter by active-set membership (rule's trait ∈ anchor traits)
               → evaluate the declarative residual (`guards`; `where` is a place
                 filter applied by the caller when it has a target path)
               → run the rule's body (declarative `action`, or the emitted
                 `body_<id>` / `guard_<id>` from the module) → collect steers.

A rule keyed under a *different* moment is never in the bucket, so it never
executes — that indexed dispatch is the property the F211 Success Criteria
pins (two adopted rules on different moments; firing one runs only its module).

`build_ctx` assembles the interpretation environment a rule body reads. It is
moment-shaped: for the `audit-q` cooperative post-moment it carries
`queries_text` + `git_aspect` + `anchor` (what `R-query-14` reads). Callers may
inject/override any field (tests, or a moment that carries different context).

Install (registering these modules with the live Claude Code hook surface) is
the productionisation layer above this dispatcher; this module is the
engine-level fire that the differential harness (F214) and F212 test directly.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shlex
import sys
import types
from pathlib import Path

# Trait name (in `.anchor` `traits:`) → the git_aspect string a rule body reads.
_GIT_ASPECT = {"commit": "commit", "pr": "pr", "push": "push", "nogit": "nogit"}


# ── loading the compiled artifacts ──────────────────────────────────────────

def load_compiled(warden_dir: Path, anchor: str) -> tuple[dict, types.ModuleType | None]:
    """Load `rules-ir.json` + import `rules_<anchor>.py` from a compiled dir."""
    ir = json.loads((warden_dir / "rules-ir.json").read_text(encoding="utf-8"))
    mod_path = warden_dir / f"rules_{anchor}.py"
    module = None
    if mod_path.is_file():
        spec = importlib.util.spec_from_file_location(f"rules_{anchor}", mod_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
    return ir, module


# ── anchor sensing (active-set + ctx inputs) ────────────────────────────────

def _read_trait_list(text: str, key: str) -> list[str]:
    """One `.anchor` trait-valued key in either YAML shape (flow or block).
    `key` is matched literally at line start, so `traits:` and `traits-:` never
    catch each other."""
    k = re.escape(key)
    m = re.search(rf"^{k}:\s*\[(.*?)\]", text, re.MULTILINE)
    if m:
        return [t.strip().strip("'\"") for t in m.group(1).split(",") if t.strip()]
    block = re.search(rf"^{k}:\s*\n((?:\s*-\s*.+\n?)+)", text, re.MULTILINE)
    if block:
        return [ln.split("-", 1)[1].strip()
                for ln in block.group(1).splitlines() if ln.strip().startswith("-")]
    return []


def _read_anchor_text(anchor_root: Path) -> str:
    dot = anchor_root / ".anchor"
    if not dot.is_file():
        return ""
    try:
        # errors="replace": a non-UTF-8 `.anchor` degrades to whatever parses,
        # never aborts the dispatch (F232 C3).
        return dot.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def read_anchor_traits(anchor_root: Path) -> list[str]:
    """The `.anchor` `traits:` list (YAML flow or block), plus the implicit base
    trait every anchor carries without declaring it ([[Warden Semantics]]).
    The raw declaration read — opt-outs are applied by `effective_traits`."""
    return _read_trait_list(_read_anchor_text(anchor_root), "traits") + ["anchor-base"]


def read_anchor_optouts(anchor_root: Path) -> list[str]:
    """The `.anchor` `traits-:` list — traits this anchor opts OUT of (F285).

    Declared, never inherited: `traits-` governs only the anchor whose
    `.anchor` carries it. That keeps an anchor's meaning a property of the
    anchor, so moving one never silently changes which rules govern it — and it
    avoids reintroducing the unbounded upward walk that caused F285."""
    return _read_trait_list(_read_anchor_text(anchor_root), "traits-")


def effective_traits(ir: dict, anchor_root: Path) -> list[str]:
    """The anchor's declared traits + `anchor-base` + the base trait's members
    (`ir["base_traits"]`, stamped by the compiler per F229 A′ — e.g.
    `audit-on-write` rides every anchor), less anything the anchor opts out of
    via `traits-` (F285). This is the trait set live dispatch gates on;
    `read_anchor_traits` alone is the raw declaration read.

    Two subtraction semantics, both load-bearing:

    - **Subtracting an umbrella subtracts its members** — `traits-:
      [anchor-base]` drops the base traits too. Otherwise the opt-out would
      itself be an enumerated list that decays as base members are added, which
      is the failure mode the design exists to avoid.
    - **An explicit `traits:` entry always wins** — `traits-` subtracts only
      what the anchor gets implicitly, so `traits: [pathguard]` with `traits-:
      [anchor-base]` yields exactly `pathguard`. This is what makes "an exact
      rule set" expressible as a composition instead of needing its own key.
    """
    declared = _read_trait_list(_read_anchor_text(anchor_root), "traits")
    traits = read_anchor_traits(anchor_root)
    for t in ir.get("base_traits", []):
        if t not in traits:
            traits.append(t)

    optouts = read_anchor_optouts(anchor_root)
    if not optouts:
        return traits
    drop = set(optouts)
    if "anchor-base" in drop:
        drop.update(ir.get("base_traits", []))
    drop -= set(declared)
    return [t for t in traits if t not in drop]


def anchor_name(anchor_root: Path) -> str:
    dot = anchor_root / ".anchor"
    if dot.is_file():
        m = re.search(r"^\s*(?:slug|name)\s*:\s*(.+?)\s*$", dot.read_text(encoding="utf-8"),
                      re.MULTILINE)
        if m:
            return m.group(1).strip().strip("'\"")
    return anchor_root.name


def git_aspect_of(traits: list[str]) -> str:
    for t in traits:
        if t.lower() in _GIT_ASPECT:
            return _GIT_ASPECT[t.lower()]
    return ""


def build_ctx(anchor_root: Path, moment: str, **overrides) -> types.SimpleNamespace:
    """Assemble the interpretation environment for a moment. Moment-shaped;
    overrides win (tests inject, or a caller supplies moment-specific context)."""
    traits = read_anchor_traits(anchor_root)
    name = anchor_name(anchor_root)
    import warden_agent as wa
    fields: dict = {
        "anchor": name,
        "anchor_root": anchor_root,      # F601: the exception loader's owner walk starts here
        "moment": moment,
        "traits": traits,
        "git_aspect": git_aspect_of(traits),
        "queries_text": "",
        "mode": None,
        "facets": [],
        # F216: the agent-state view. Unbound by default (headless/audit path —
        # every read returns the error values); live callers override with a
        # session-bound AgentView (warden_agent.make_agent).
        "agent": wa.unbound(),
        # F217: the judgment verb — blocking, cached, fail-silent.
        "ask_oracle": wa.ask_oracle,
        # F215: the event's file (write:/read: moments) — fire() binds
        # `ctx.file` per file-bearing rule from this path.
        "file_path": None,
        "file": None,
        # F131: the tool event under way (tool:pre/post moments) — a view of
        # {tool, target, input} so veto-path rules can test the pending call.
        "event": None,
    }
    # audit-q cooperative post-moment: the freshly-built queries file is the input.
    if moment.endswith(":audit-q"):
        q = anchor_root / f"{name} Track" / f"{name} queries.md"
        if q.is_file():
            fields["queries_text"] = q.read_text(encoding="utf-8")
    fields.update(overrides)
    return types.SimpleNamespace(**fields)


# ── declarative guard evaluation ────────────────────────────────────────────

def _ctx_value(ctx, key):
    return {"git-aspect": getattr(ctx, "git_aspect", None),
            "mode": getattr(ctx, "mode", None),
            "trait": getattr(ctx, "traits", []),
            "facet": getattr(ctx, "facets", [])}.get(key)


def eval_guard(guard: dict, ctx) -> bool:
    """A declarative {key, op, value} guard against ctx (F210 fixed vocabulary)."""
    actual = _ctx_value(ctx, guard["key"])
    op, value = guard["op"], guard["value"]
    if op == "eq":
        return actual == value
    if op == "in":
        return actual in (value if isinstance(value, (list, tuple, set)) else [value])
    if op == "has":
        return value in (actual or [])
    return False


def _rule_traits(ir: dict, rule_id: str) -> list[str]:
    return [t for t, ids in ir.get("traits", {}).items() if rule_id in ids]


def is_active(ir: dict, rule_id: str, anchor_traits) -> bool:
    """Active iff some trait that keys the rule is in the anchor's trait set."""
    keying = _rule_traits(ir, rule_id)
    return any(t in anchor_traits for t in keying)


# ── fire ────────────────────────────────────────────────────────────────────

def excepted_by(ctx, rule_id: str) -> dict | None:
    """The admitted exception row that quiets `rule_id` for this event, else None.

    F601 — one loader for both executors. Every moment rule in the corpus is
    Python-bodied (measured 2026-08-28: zero declarative `tell`/`deny` rows),
    so the Rust hook routes each one through the daemon and lands here; there
    is nothing on the Rust side left to load for. The parser is audit-plan's
    (`load_exceptions` — the same rows, the same grading authority, the same
    `_exception_for` glob) reached through `warden_docfire`, which already
    keeps that module warm and fresh in the daemon.

    Target: the event's file when there is one (`write:`/`read:`/file-bearing
    tool moments), matched relative to the OWNING anchor; a moment with no
    file (Bash, session, prompt) is covered only by an anchor-wide `**` row.
    Fail-open: any error means the rule fires as it always did."""
    try:
        import warden_docfire as wd
        wd.refresh_audit_plan()
        ap = wd.ap
        anchor_root = getattr(ctx, "anchor_root", None)
        if anchor_root is None:
            return None
        anchor_root = Path(anchor_root)
        excs, _declined, _problems = ap.load_exceptions(anchor_root)
        if not excs:
            return None
        fp = getattr(ctx, "file_path", None)
        if fp:
            return ap._exception_for(excs, rule_id, Path(fp), anchor_root)
        for e in excs:
            if e["rule"] == rule_id and e["target"].strip() == "**":
                return e
        return None
    except Exception as exc:  # noqa: BLE001 — fail-open, never mute a rule by accident
        try:
            import warden_hook as _wh
            _wh._log(f"exceptions: loader error for {rule_id}: {exc!r} — rule fires unexcepted")
        except Exception:
            pass
        return None


def fire(ir: dict, module, moment: str, ctx, anchor_traits) -> list[str]:
    """Run the rules keyed at `moment` and active for the anchor; return steers.
    Rules on any other moment are not in the bucket and never execute."""
    return [s for _, produced in fire_records(ir, module, moment, ctx, anchor_traits)
            for s in produced]


def fire_records(ir: dict, module, moment: str, ctx, anchor_traits) -> list[tuple[str, list[str]]]:
    """`fire()` with per-rule attribution (F231): one `(rule_id, steers)` pair
    per rule CONSIDERED at the moment — in the bucket and active for the anchor.
    A considered rule whose guard gated it out (or whose body returned nothing)
    appears with `[]`, so the fire log can distinguish "no rule was live here"
    from "the rule was live and stayed silent". Steer text is verbatim what the
    agent receives (denies keep their sentinel)."""
    records: list[tuple[str, list[str]]] = []
    for rule_id in ir.get("moments", {}).get(moment, []):
        # A bucket entry with no rule row (hand-edited/corrupt IR) is skipped —
        # never aborts the moment's other rules (F232 C3).
        row = ir.get("rules", {}).get(rule_id)
        if row is None:
            continue
        if not is_active(ir, rule_id, anchor_traits):
            continue
        # F217: a turn-bearing rule needs a bound session (rungs R1–R3);
        # at R4 the turn view is unresolvable and the rule is skipped wholesale.
        if row.get("turn_bearing") and not getattr(
                getattr(ctx, "agent", None), "is_bound", False):
            records.append((rule_id, []))
            continue
        # F215: bind `ctx.file` per (rule, event-file) — its `.diff` is the
        # change since THIS rule last evaluated the file, so the binding
        # cannot be shared across rules the way the rest of ctx is.
        fv = None
        if row.get("file_bearing"):
            fp = getattr(ctx, "file_path", None)
            if fp:
                import warden_reval as wr
                fv = wr.FileView(rule_id, fp)
            ctx.file = fv
        if not all(eval_guard(g, ctx) for g in row.get("guards", [])):
            records.append((rule_id, []))
            continue
        gp = row.get("guard_py")
        if gp and module is not None and not getattr(module, gp)(ctx):
            records.append((rule_id, []))
            continue
        produced: list[str] = []
        if row.get("body_py") and module is not None:
            out = getattr(module, row["body_py"])(ctx)
            if out:
                produced = out if isinstance(out, list) else [out]
        # F601 — the anchor's exception table quiets a moment rule exactly as
        # it quiets a doc-rule: a graded A–C row naming this rule and covering
        # the event's file (or `**`) drops the steer, deny included. Grading
        # authority is the loader's business (a `confirm:: user` rule is
        # honoured only when the user graded it), so nothing here re-decides
        # it. Suppressions are kept on ctx for the fire record.
        if produced:
            exc = excepted_by(ctx, rule_id)
            if exc is not None:
                ctx.excepted = getattr(ctx, "excepted", None) or []
                ctx.excepted.append({"rule": rule_id, "handle": exc["handle"],
                                     "grade": exc["grade"],
                                     "steers": list(produced)})
                produced = []
        elif row.get("action"):
            act = row["action"]
            if act.get("kind") in ("tell", "deny"):
                text = act.get("text") or act.get("reason") or ""
                # F131: a deny travels as a sentinel-prefixed steer — same
                # string channel end-to-end; the hook layer converts it to a
                # real PreToolUse permissionDecision (fail-open elsewhere).
                produced = [f"DENY: {text}" if act["kind"] == "deny" else text]
        records.append((rule_id, produced))
        # F215: the rule fully evaluated this revision — advance its
        # last-evaluated record (a gate-suppressed pass never reaches here,
        # so sub-threshold edits accumulate in the diff until they cross).
        if fv is not None:
            fv.mark_evaluated(verdict=produced)
    return records


# ── CLI ──────────────────────────────────────────────────────────────────────

def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="warden-fire",
        description="Fire a moment against a compiled anchor; print the steers.")
    ap.add_argument("--anchor-root", required=True, help="the anchor directory (holds .anchor)")
    ap.add_argument("--warden-dir", default=None, help="compiled dir (default: <anchor-root>/.warden)")
    ap.add_argument("--anchor", default=None, help="anchor/module name (default: sensed from .anchor)")
    ap.add_argument("--moment", required=True, help="the moment to fire, e.g. skill:post:audit-q")
    args = ap.parse_args(argv)

    root = Path(args.anchor_root).expanduser().resolve()
    name = args.anchor or anchor_name(root)
    wdir = Path(args.warden_dir).expanduser() if args.warden_dir else (root / ".warden")
    ir, module = load_compiled(wdir, name)
    ctx = build_ctx(root, args.moment)
    traits = read_anchor_traits(root)
    steers = fire(ir, module, args.moment, ctx, traits)
    for s in steers:
        print(s)
    return 0


# ---------------------------------------------------------------------------
# Command-text helpers for `tool:pre:Bash` rules
# ---------------------------------------------------------------------------

# `<<EOF` / `<<'EOF'` / `<<"EOF"` / `<<-EOF`. `<<<word` (herestring) is NOT a
# heredoc and deliberately does not match — after `<<` comes `<`, which is
# neither a quote nor an identifier start.
_HEREDOC_OPEN_RE = re.compile(
    r"""<<-?\s*(?:'([^']*)'|"([^"]*)"|([A-Za-z_][A-Za-z0-9_]*))""")

# A heredoc fed to one of these IS command position — `bash <<EOF … ssh h c … EOF`
# really runs the ssh. Those bodies are kept.
_SHELL_WORDS = {"bash", "sh", "zsh", "ksh", "dash", "eval", "source", "."}


def newlines_to_separators(cmd: str, sep: str = ";") -> str:
    """`cmd` with every UNQUOTED newline turned into a command separator.

    T611. `shlex.split` throws newlines away with the rest of the whitespace, so
    a token scan that recognises command position by "index 0, or after a token
    ending in `;`, `&`, `|`, `(`" cannot see a line boundary at all — and a
    newline separates commands exactly as `;` does. The consequence measured
    2026-08-28: a two-line Bash command whose second line began with a one-shot
    ssh was not denied by R-ob-remote-ops-01, and multi-line commands are the
    ordinary shape a coding agent submits. Surfaced by a T609 fixture that
    failed for a reason unrelated to the change under test.

    Two newlines are deliberately NOT separators:

    - one inside quotes, which is data — the same distinction `mask_quoted`
      draws, tracked here directly because a quoted newline must be *preserved*
      rather than blanked;
    - one after a trailing backslash, which is a line continuation and joins
      the two lines into a single command.

    Run this AFTER `strip_heredoc_bodies`, so a heredoc body's lines are already
    gone rather than being promoted to command positions.
    """
    out = []
    i, n = 0, len(cmd)
    quote = None
    while i < n:
        ch = cmd[i]
        if quote:
            if ch == "\\" and quote == '"' and i + 1 < n:
                out.append(ch)
                out.append(cmd[i + 1])
                i += 2
                continue
            if ch == quote:
                quote = None
            out.append(ch)
            i += 1
            continue
        if ch in ("'", '"'):
            quote = ch
            out.append(ch)
            i += 1
            continue
        if ch == "\\" and i + 1 < n and cmd[i + 1] == "\n":
            out.append(" ")               # line continuation: one command
            i += 2
            continue
        if ch == "\n":
            out.append(f" {sep} ")
            i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def mask_quoted(cmd: str, fill: str = " ") -> str:
    """`cmd` with the CONTENTS of every quoted span blanked, quotes kept.

    Length-preserving, so an offset found in the mask is the offset in `cmd`.
    The delimiters survive so a redirect target still reads as one token; only
    what a human wrote *inside* them goes away.

    Same principle as `strip_heredoc_bodies` at a smaller grain: a quoted span
    is data, and scanning it for operators reads prose as shell. This is what
    made `state drop <anchor> "... a path -> another ..."` look like a
    redirection to R-dispatch-guard-04. T605.
    """
    out = list(cmd)
    i, n = 0, len(cmd)
    while i < n:
        ch = cmd[i]
        if ch in ("'", '"'):
            j = i + 1
            while j < n and cmd[j] != ch:
                if ch == '"' and cmd[j] == "\\" and j + 1 < n:
                    j += 1                 # a backslash escape inside "..."
                j += 1
            for k in range(i + 1, min(j, n)):
                if out[k] != "\n":
                    out[k] = fill
            i = j + 1
            continue
        i += 1
    return "".join(out)


# A `>` that actually creates or appends to a FILE. `2>&1` and `>&2` duplicate a
# file descriptor and write nothing, and they are the commonest suffix in the
# corpus — which is why a bare `">" in cmd` test made every `grep … 2>&1` read
# look like a write (T605).
# `>/dev/null` (and `2>/dev/null`) discards output; it creates nothing, and it
# is the second-commonest suffix after `2>&1`. Two read-only compound commands
# were refused on a spine-dirty page for carrying it (2026-08-28, TINK).
REDIRECT_RE = re.compile(r"(?:^|[\s;|&(])(?:\d|&)?>>?\s*(?!&|/dev/null(?:\s|$|[;|&)]))\S")

# `mv` / `cp` in command position — not the letters appearing inside prose.
MOVE_COPY_RE = re.compile(r"(?:^|[;|&(])\s*(?:sudo\s+)?(?:mv|cp)\s")


def strip_heredoc_bodies(cmd: str) -> str:
    """`cmd` with every heredoc BODY removed and its opener line kept.

    A heredoc body is data the shell hands to a program on stdin, not command
    position — and it is also the one place an agent routinely writes *about*
    commands, so a rule that tokenizes the raw text reads documentation as
    execution. `R-ob-remote-ops-01` has now been patched three times for
    prose-vs-code misreads: a quoted `--body` argument (2026-07-06), a trailing
    pipe defeating the tmux exemption (2026-08-13), and a markdown code span
    whose opening backtick made prose tokenize as command substitution
    (2026-08-28). The third denied the write that was *filing the report about
    it*, which is the corrosive part — the way to get a note past the rule is to
    describe the command less precisely, so the record degrades toward vagueness
    exactly where it should be sharpest.

    **A body fed to a shell is kept**, because there it genuinely is code. That
    is the whole reason this is not a blanket strip: the cheap version of this
    fix would open a real evasion (`bash <<EOF` … `EOF`) while closing a
    documentation false-positive, trading a loud wrong answer for a silent one.

    Lives in the dispatcher rather than in a ruleset because two rules in two
    different ruleset files need it and each ruleset block compiles to its own
    module. `warden_fire` is already imported whenever any rule body runs, so a
    rule reaching for it costs no import. T609.
    """
    lines = cmd.split("\n")
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        i += 1
        delims = [m.group(1) or m.group(2) or m.group(3)
                  for m in _HEREDOC_OPEN_RE.finditer(line)]
        if not delims:
            continue
        try:
            opener_words = set(shlex.split(line))
        except ValueError:
            opener_words = set(line.split())
        if opener_words & _SHELL_WORDS:
            continue                      # really is code — leave it alone
        # Consume each heredoc in the order the shell reads them. `<<-` allows an
        # indented terminator, so compare on the stripped line either way.
        for delim in delims:
            while i < len(lines) and lines[i].strip() != delim:
                i += 1
            if i < len(lines):
                out.append(lines[i])      # keep the terminator; it ends nothing else
                i += 1
    return "\n".join(out)


if __name__ == "__main__":
    sys.exit(main())
