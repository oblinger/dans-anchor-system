#!/usr/bin/env python3
"""Stencil generator — the GENERATE direction only (F303 M4).

Implements the same language as `sten_match.py` (`Stencil/STEN Language.md`):

    {{NAME}}      a variable
    # ... LOG     an anchor: heading matching LOG at this depth OR DEEPER
    # == LOG      an anchor: heading matching LOG at EXACTLY this depth

and its four defaults: open world, exactly one, many-by-variable, whole
document.  Generation takes a stencil plus a binding **environment** and
produces the text of a conforming document — the dual of `match()`, which
takes a stencil plus a document and produces bindings.

**The parser is not duplicated.**  `parse_stencil` and its AST
(`Blank`/`Hole`/`Pat`/`Anchor`) live in `sten_match.py` and are imported
here unchanged — a second parser is exactly the drift Stencil exists to
eliminate.  `generate` builds no regex and does no matching; everything
below walks the same tree `match()` walks, in the direction it does not.

**The environment.** `env` maps a variable name to either a single string
(bound once) or a **list** of strings (bound once per repetition).  Whether
a list is required is not declared anywhere in the stencil — it falls out
of which stencil lines are *free* at the point they are reached, exactly
as multiplicity is a consequence of freedom on the match side.  A run of
consecutive stencil lines that share at least one variable not yet bound
is one repeatable unit ("a group"); the run is generated once per entry
in the binding list, and every free variable in it must supply a list of
the SAME length.  A line with no unbound variable — a literal line, or a
line whose only variables are already bound from an earlier line — always
ends the current group and is emitted exactly once.  This grouping rule is
an implementation property of the generator, not new grammar: T3's own
`## {{YYYY-MM-DD}} {{DAY}}  {{DIRECTION}} — {{KIND}}` / `{{entry body}}`
pair is one group (both needed, together, per LOG entry); its preceding
`{{one-line description}}` is a group of one (the section's own
description, bound once); T6's `| {{LEFT}}  | {{RIGHT}} |` is a group of
one line that repeats once per row, broken from its neighbours by the
literal `| --- | --- |` separator on one side and end-of-table on the
other.

**Multiplicity inside a document is one-or-more** (STEN Language, measured
by M3): a binding list of length zero is refused rather than silently
producing zero occurrences of a required item.  Zero-or-more exists only
for a folder member, where the filesystem supplies the boundary — that is
`match_folder`'s territory, not this module's; a folder-tree stencil
(T2.A, T5.A) is out of scope here for the same reason `match_folder` is a
separate function from `match`.

**Failure is loud.** A missing binding, a binding-list length that
disagrees with a sibling in the same group, an empty list, or a malformed
stencil (the adjacent-unbound-variable defect `parse_stencil` already
flags as a note) all raise `StencilError` naming the stencil and the
variable — never a partial document.

Run `python3 sten_generate.py <stencil-file> <bindings.json>` to generate
one document from the command line.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import sten_match as M            # noqa: E402  — the parser, reused, not copied


class StencilError(Exception):
    """Generation refused: a malformed stencil, a missing binding, or a
    binding-list whose length disagrees with a sibling in the same group."""


# ------------------------------------------------------------- table escaping

# T6 finding (F303 M4 escaping defect): an unescaped `|` inside a substituted
# value opens a new markdown table column, silently turning a two-cell row
# into four.  A malformed stencil written this way is invisible to
# `M.match`, because match and generate both parse the SAME `parse_stencil`
# and a table row is just literal text to it — only comparing generated
# output against a REAL specimen exposes it.  So the escaping has to live
# here, in the generator, rather than be pushed onto every env as a rule
# callers must remember: a binding that must be pre-escaped is a trap the
# corpus (T6.A / ENV_T6A) already proves people fall into.
_UNESCAPED_PIPE_RE = re.compile(r"(?<!\\)\|")


def _escape_pipes(value: str) -> str:
    """Escape every `|` in `value` that is not already escaped — never
    double-escapes a `\\|` the binding already carries."""
    return _UNESCAPED_PIPE_RE.sub(r"\\|", value)


def _is_table_row(pat: "M.Pat") -> bool:
    """A stencil line is a table row by its OWN shape — a leading `|` — not
    by anything the binding says.  Only substituted values get escaped;
    the stencil's own structural pipes (`| --- | --- |`) are literal text
    and pass through untouched."""
    return pat.raw.lstrip().startswith("|")


# --------------------------------------------------------------- primitives

def _item_segs(item):
    """The (kind, value) segments that decide an item's free variables and
    that render it — `segs` for a Pat (the whole line, prefix included),
    `text_segs` for an Anchor (its heading text only)."""
    if isinstance(item, M.Pat):
        return item.segs
    if isinstance(item, M.Anchor):
        return item.text_segs
    return None


def _free_vars_of_item(item, bound: dict) -> list[str]:
    """Variable names this item mentions that `bound` does not yet supply,
    in first-seen order.  A Hole is its own single (possibly multi-line)
    variable; a Pat/Anchor may name several inline."""
    if isinstance(item, M.Hole):
        return [] if item.name in bound else [item.name]
    segs = _item_segs(item)
    if segs is None:
        return []
    out: list[str] = []
    for kind, val in segs:
        if kind == "var" and val not in bound and val not in out:
            out.append(val)
    return out


def _render_segs(segs, bound: dict, name: str, escape_pipes: bool = False) -> str:
    parts = []
    for kind, val in segs:
        if kind == "lit":
            parts.append(val)
        elif val in bound:
            v = bound[val]
            parts.append(_escape_pipes(v) if escape_pipes else v)
        else:
            raise StencilError(
                f"{name}: missing binding for variable {{{{{val}}}}}")
    return "".join(parts)


def _render_item(item, bound: dict, name: str) -> str:
    if isinstance(item, M.Hole):
        if item.name not in bound:
            raise StencilError(
                f"{name}: missing binding for variable {{{{{item.name}}}}}")
        return bound[item.name]
    if isinstance(item, M.Pat):
        return _render_segs(item.segs, bound, name, escape_pipes=_is_table_row(item))
    raise AssertionError(f"unexpected item in a repeatable group: {item!r}")


# --------------------------------------------------------------- generation

def _render_run(run: list, ctx: dict, env: dict, out: list, name: str) -> None:
    """Emit one group of consecutive Pat/Hole items, once per binding.

    `ctx` is the running, GLOBAL bindings dict — the generation-side twin of
    `_Ctx.b` in `sten_match.py`.  A variable this run introduces is written
    back into `ctx` from its LAST repetition once the run is done, so a
    later line that names the same variable sees it as already bound (T5's
    finding: a binding is per-member and shared across the member's
    artifacts) rather than asking for its own list.
    """
    if not run:
        return

    free: list[str] = []
    for item in run:
        for v in _free_vars_of_item(item, ctx):
            if v not in free:
                free.append(v)

    if not free:
        for item in run:
            out.append(_render_item(item, ctx, name))
        return

    lists: dict[str, list[str]] = {}
    length = None
    for v in free:
        if v not in env:
            raise StencilError(
                f"{name}: missing binding for variable {{{{{v}}}}}")
        val = env[v]
        vlist = val if isinstance(val, list) else [val]
        if length is None:
            length = len(vlist)
        elif len(vlist) != length:
            raise StencilError(
                f"{name}: binding-list length mismatch — {{{{{v}}}}} has "
                f"{len(vlist)} value(s), {{{{{free[0]}}}}} has {length}")
        lists[v] = vlist

    if length == 0:
        names = " / ".join("{{%s}}" % v for v in free)
        raise StencilError(
            f"{name}: empty binding list for {names} — a document item "
            f"needs at least one occurrence (STEN Language: many-by-variable "
            f"is one-or-more inside a document, zero-or-more only for a "
            f"folder member)")

    multi_line = len(run) > 1     # a paragraph-shaped group gets a blank
    for r in range(length):       # line between repetitions; a one-line
        rep = dict(ctx)           # group (a table row) does not.
        for v in free:
            rep[v] = lists[v][r]
        for item in run:
            out.append(_render_item(item, rep, name))
        if multi_line and r != length - 1:
            out.append("")

    for v in free:                # settle: last repetition's value is what
        ctx[v] = lists[v][length - 1]   # later, already-bound lines will see


def _emit_level(items: list, ctx: dict, env: dict, out: list, name: str) -> None:
    """Walk one items list (the root, or one Anchor's body) left to right,
    accumulating a repeatable group until a Blank, an Anchor, or a line with
    no unbound variable closes it."""
    run: list = []
    for item in items:
        if isinstance(item, M.Blank):
            _render_run(run, ctx, env, out, name)
            run = []
            out.append("")
            continue
        if isinstance(item, M.Anchor):
            _render_run(run, ctx, env, out, name)
            run = []
            _emit_anchor(item, ctx, env, out, name)
            continue
        if _free_vars_of_item(item, ctx):
            run.append(item)
            continue
        _render_run(run, ctx, env, out, name)
        run = []
        out.append(_render_item(item, ctx, name))
    _render_run(run, ctx, env, out, name)


def _emit_anchor(anchor: M.Anchor, ctx: dict, env: dict, out: list, name: str) -> None:
    """Emit an anchor's heading at its OWN stencil depth — there is no
    existing document to float against when generating from scratch — then
    recurse into its body.  No corpus anchor's heading text carries a free
    variable, so repeating an anchor itself is out of scope; a heading
    variable given as a list of anything but length 1 is refused rather
    than guessed at."""
    free = _free_vars_of_item(anchor, ctx)
    if free:
        for v in free:
            if v not in env:
                raise StencilError(
                    f"{name}: missing binding for variable {{{{{v}}}}}")
            val = env[v]
            if isinstance(val, list):
                if len(val) != 1:
                    raise StencilError(
                        f"{name}: anchor heading variable {{{{{v}}}}} cannot "
                        f"repeat — generate emits exactly one heading per "
                        f"anchor")
                val = val[0]
            ctx[v] = val
    heading_text = _render_segs(anchor.text_segs, ctx, name)
    out.append("#" * anchor.depth + " " + heading_text)
    _emit_level(anchor.body, ctx, env, out, name)


def generate(stencil_text: str, env: dict, *, name: str = "<stencil>",
             single_brace_vars: bool = False) -> str:
    """Generate a document conforming to `stencil_text` from `env`.

    `env` maps a `{{NAME}}` to a string (bound once) or a list of strings
    (bound once per repetition of the group it lives in — see module
    docstring).  Raises `StencilError`, naming `name` and the offending
    variable, rather than emitting a partial document.

    `single_brace_vars` mirrors `sten_match.match`'s flag of the same name and
    must be forwarded, not defaulted away: every shipped template in
    `templates/*` uses the single-brace `{slug}` convention, and without this
    the parser reads `{slug}` as literal text, so `generate(S, {"slug": "WGT"})`
    emits an H1 reading literally `# {slug} Backlog`.

    The two directions disagreeing about what the grammar IS is the defect —
    F303 M5's Finding 5, a gap in M4 that M4's own suite could not see. The
    round-trip test passed anyway, because match was re-run with
    `single_brace_vars=True` and accepted the un-substituted `{slug}` as a
    literal matching itself. It was not proof the generator handled `{slug}`;
    it was proof the check never asked it to.
    """
    # `fold_quoting=False` — see `unquote_description`: unquoting is a MATCH
    # normalization, and a generator that applied it would emit frontmatter no
    # YAML parser reads. `drops` is discarded rather than fatal: a dropped
    # breadcrumb is a line the daemon writes moments after the file lands.
    items, notes, _drops = M.parse_stencil(stencil_text,
                                           single_brace_vars=single_brace_vars,
                                           fold_quoting=False)
    if notes:
        raise StencilError(
            f"{name}: refusing to generate from a malformed stencil — "
            + "; ".join(notes))
    ctx: dict = {}
    out: list = []
    _emit_level(items, ctx, env, out, name)
    return "\n".join(out) + "\n"


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    stencil = Path(argv[1]).read_text(encoding="utf-8")
    env = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
    try:
        sys.stdout.write(generate(stencil, env, name=argv[1]))
    except StencilError as e:
        print(f"! {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
