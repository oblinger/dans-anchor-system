#!/usr/bin/env python3
"""Stencil matcher — the MATCH direction only (F303 M3).

Implements the language defined in `Stencil/STEN Language.md`:

    {{NAME}}      a variable
    # ... LOG     an anchor: heading matching LOG at this depth OR DEEPER
    # == LOG      an anchor: heading matching LOG at EXACTLY this depth

and its four defaults: open world, exactly one, many-by-variable, whole
document.  Anchors nest; depths inside an anchor are relative to it.

Nothing here generates.  `generate` is F303 M4 and is deliberately absent.

Three switches exist so that grammar questions the spec left open can be
*measured* rather than argued:

  extent=       "line"     a stencil line carrying any literal text is matched
                           line-wise; a line that is nothing but a variable is
                           a multi-line hole.   (STEN Language option (A),
                           repaired: end-of-line counts as a literal.)
                "strict-a" the recommendation read literally — a variable
                           reaches until the next literal ANYWHERE later in the
                           stencil, so a trailing variable spans lines.
  multiplicity= "min1"     every stencil item must match at least once.
                "min0free" an item holding a free variable may match zero
                           times — the literal `[0+]` reading of
                           many-by-variable.
  single_brace_vars=       treat `{name}` as a variable too.  The grammar says
                           only `{{NAME}}` is a variable; the shipped
                           `templates/log/` folder relies on `{slug}` being one.

Run `python3 sten_match.py <stencil-file> <target-file>` to match one pair.
"""
from __future__ import annotations

import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------- normalization

# T4 finding: the two live LOG spellings differ only in invisible bytes —
# U+00A0 after `**From:**` (pasted out of Apple Mail) and a trailing space on
# `# LOG `.  A matcher written against what these look like on screen matches
# neither.  Normalizing is an implementation property of M3, not a grammar one.
_SPACES = "               　"
_SPACE_MAP = {ord(c): " " for c in _SPACES}


def normalize_line(s: str) -> str:
    """NFC, every Unicode space to U+0020, trailing whitespace stripped.

    Internal runs are preserved — T3.A's entry heading distinguishes fields by
    a DOUBLE space, so collapsing runs would destroy the pattern.
    """
    return unicodedata.normalize("NFC", s).translate(_SPACE_MAP).rstrip()


# The identity cell's breadcrumb SEGMENT is machine-owned, exactly as the `:>>`
# LINE is (see BREADCRUMB_RE below) — one column over, same daemon, same proof:
# holing it in `templates/{slug} Rocks.md` and `templates/{slug} Track.md` was
# reverted by HookAnchor within seconds on both, back to the trail to the
# template itself. But unlike `:>>` it does not own the whole line: the cell
# holds two `<br>`-delimited segments, a `: description` the author owns (it is
# mirrored from frontmatter, and holing THAT survived the same experiment) and
# a `→ …` trail the author does not. Dropping the line would throw away the
# half the stencil legitimately asserts.
#
# So the drop is symmetric — the segment leaves the stencil AND the target,
# which is why it lives in normalization rather than in `parse_stencil`. Both
# live orders are covered, and measuring them is what made the symmetric form
# obvious: 656 pages vault-wide write the trail first (`→ …<br>: desc`) and 76
# write it last (`: desc<br>→ …`). Neither order is machine-owned — HookAnchor
# rewrote the trail in place and left the order alone — so a stencil in one
# order and an instance in the other are the same page, and after this both
# normalize to `| -[[X]]- | : desc |` and match. Ordering was never content.
IDENTITY_CELL_RE = re.compile(r"^\|\s*-\[\[")
_UNESCAPED_PIPE_RE = re.compile(r"(?<!\\)\|")


def drop_masthead_breadcrumb(line: str) -> str:
    """Strip the `→ …` segment from an identity cell, in either order."""
    if not IDENTITY_CELL_RE.match(line):
        return line
    cells = _UNESCAPED_PIPE_RE.split(line)
    if len(cells) < 4:
        return line
    segs = [s.strip() for s in cells[2].split("<br>")]
    kept = [s for s in segs if s and not s.startswith("→")]
    if len(kept) == len([s for s in segs if s]):
        return line
    cells[2] = f" {'<br>'.join(kept)} "
    return "|".join(cells).rstrip()


# Frontmatter `description:` QUOTING is machine-owned too, and this one is
# settled by reading the writer rather than by watching it: HookAnchor's
# `write_frontmatter_description` (HookAnchorApp `src/capabilities/description.rs`)
# routes every inline value through `yaml_encode_inline`, which unconditionally
# wraps it in double quotes. So a page is quoted if and only if the daemon has
# rewritten its description since it was authored — which is an accident of
# history, not a property of the page. Measured across the vault: 1083 pages are
# quoted with no YAML need and 1426 are bare with no YAML need, so neither form
# is even the majority convention, and any page can flip to quoted tomorrow.
#
# A stencil cannot pick a side, and it cannot abstain either: a hole opening
# with `{` (`description: {{one line …}}`) is a YAML flow mapping, so a template
# that holes its own description MUST quote to stay parseable. Unquoting both
# sides is what lets the quoted template match the 1426 bare pages.
#
# Block scalars (`description: |-`) are deliberately out of scope — that form
# spans lines, and this normalization is line-wise.
#
# Unlike the two breadcrumb drops this one is MATCH-ONLY (`fold_quoting`), and
# the asymmetry is the point: a breadcrumb is text the generator legitimately
# omits, because the daemon writes it moments later — but quoting is not text,
# it is how a value the generator DOES emit gets spelled, and emitting
# `description: some value: with a colon` unquoted is not a page HookAnchor
# will fix, it is frontmatter no YAML parser will read. `generate` therefore
# parses with `fold_quoting=False` and keeps the stencil's quotes.
_FM_DESC_QUOTED_RE = re.compile(r'^(description): "(.*)"$')


def unquote_description(line: str) -> str:
    """Strip HookAnchor's YAML quoting from a `description:` line."""
    m = _FM_DESC_QUOTED_RE.match(line)
    if not m:
        return line
    return f"{m.group(1)}: " + m.group(2).replace('\\"', '"').replace("\\\\", "\\")


def normalize_lines(text: str, *, fold_quoting: bool = True) -> list[str]:
    out = []
    for l in text.split("\n"):
        l = drop_masthead_breadcrumb(normalize_line(l))
        out.append(unquote_description(l) if fold_quoting else l)
    return out


# ---------------------------------------------------------------------- parsing

VAR_RE = re.compile(r"\{\{(.*?)\}\}")
SINGLE_VAR_RE = re.compile(r"(?<!\{)\{([^{}]+)\}(?!\})")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
ANCHOR_RE = re.compile(r"^(#{1,6})\s+(\.\.\.|==)\s+(.*)$")

# A `:>>` breadcrumb line is never part of a stencil, in either direction.
#
# Measured 2026-08-12 (F303): holing the breadcrumb in `templates/icebox.md`,
# `inbox.md` and `testing.md` was reverted by HookAnchor within seconds on all
# three — the daemon owns that line in every registered file, and a template
# file is a registered file. So a stencil literally CANNOT state its own
# breadcrumb: whatever an author writes there, the machine replaces with the
# trail to the template itself, which is the one trail no instance will ever
# have. Requiring it made every one of those templates unmatchable against
# every real instance, forever, for a line no author controls.
#
# Dropping it is not a fourth construct. Open-world already permits a target to
# carry lines the stencil does not name, so the instance's own breadcrumb passes
# either way; this only stops the stencil from ASSERTING a line it cannot own.
# Verified against the pinned corpus: all three suites stay green and no
# specimen verdict moves, which is what distinguishes a repair from a language
# change.
BREADCRUMB_RE = re.compile(r"^\s*:>>\s")


@dataclass
class Blank:
    lineno: int


@dataclass
class Hole:
    """A stencil line that is nothing but one variable — a multi-line hole."""
    name: str
    lineno: int


@dataclass
class Pat:
    """A stencil line carrying literal text (and possibly inline variables)."""
    raw: str
    segs: list                      # [("lit", s) | ("var", name)]
    depth: int | None               # heading depth, if heading-shaped
    text_segs: list                 # segs of the heading text only
    lineno: int


@dataclass
class Anchor:
    depth: int                      # stencil depth of the marker heading
    mode: str                       # "..." (this deep or deeper) | "==" (exact)
    text_segs: list
    lineno: int
    body: list = field(default_factory=list)


def _segment(line: str, single_brace: bool) -> list:
    """Split a line into literal / variable segments."""
    out, pos = [], 0
    pattern = VAR_RE
    matches = list(VAR_RE.finditer(line))
    if single_brace:
        matches = sorted(matches + [m for m in SINGLE_VAR_RE.finditer(line)
                                    if not any(v.start() <= m.start() < v.end()
                                               for v in matches)],
                         key=lambda m: m.start())
    for m in matches:
        if m.start() > pos:
            out.append(("lit", line[pos:m.start()]))
        out.append(("var", m.group(1)))
        pos = m.end()
    if pos < len(line):
        out.append(("lit", line[pos:]))
    return out


def _is_pure_var(segs) -> bool:
    return len(segs) == 1 and segs[0][0] == "var"


def parse_stencil(text: str, *, extent: str = "line",
                  single_brace_vars: bool = False,
                  fold_quoting: bool = True):
    """Return (items, notes, drops).

    `items` is a nested list of Blank/Hole/Pat/Anchor. The two report channels
    are SEPARATE because they mean opposite things to a caller: `notes` are
    malformations — the stencil says something no reading can honour, and
    `generate` refuses to run — while `drops` are lines a well-formed stencil is
    simply not allowed to own. Folding them into one list is what made `generate`
    refuse `templates/icebox.md`, `inbox.md` and `testing.md` outright: all three
    open with a `:>>` breadcrumb, so all three produced a note, and a note was
    fatal. The drop is still reported rather than silent — a stencil author who
    writes a breadcrumb expecting it to be asserted must be told it wasn't."""
    notes: list[str] = []
    drops: list[str] = []
    lines = normalize_lines(text, fold_quoting=fold_quoting)
    while lines and lines[-1] == "":
        lines.pop()
    while lines and lines[0] == "":
        lines.pop(0)

    flat: list = []
    for i, line in enumerate(lines, 1):
        if line.strip() == "":
            flat.append(Blank(i))
            continue
        if BREADCRUMB_RE.match(line):
            drops.append(f"line {i}: `:>>` breadcrumb dropped from the stencil "
                         f"— machine-owned, no stencil can assert one")
            continue
        am = ANCHOR_RE.match(line)
        if am:
            flat.append(Anchor(len(am.group(1)), am.group(2),
                               _segment(am.group(3), single_brace_vars), i))
            continue
        segs = _segment(line, single_brace_vars)
        for a, b in zip(segs, segs[1:]):
            if a[0] == "var" and b[0] == "var":
                notes.append(
                    f"line {i}: adjacent variables {{{{{a[1]}}}}}{{{{{b[1]}}}}} "
                    f"with no literal between them — extent is ambiguous under "
                    f"any reading (STEN Language § Variable extent)")
        stripped = line.strip()
        stripped_segs = _segment(stripped, single_brace_vars)
        if _is_pure_var(stripped_segs):
            flat.append(Hole(stripped_segs[0][1], i))
            continue
        hm = HEADING_RE.match(line)
        depth = len(hm.group(1)) if hm else None
        text_segs = _segment(hm.group(2), single_brace_vars) if hm else []
        pat = Pat(line, segs, depth, text_segs, i)
        if extent == "strict-a" and segs and segs[-1][0] == "var":
            # The recommendation read literally: a trailing variable is bounded
            # by the next literal the stencil names, which lives on a LATER
            # line — so it spans lines.  Split the item in two.
            head = segs[:-1]
            if head:
                raw_head = "".join(s if k == "lit" else "{{%s}}" % s
                                   for k, s in head)
                htext = _segment(HEADING_RE.match(raw_head).group(2),
                                 single_brace_vars) if HEADING_RE.match(raw_head) else []
                flat.append(Pat(raw_head, head, depth, htext, i))
            flat.append(Hole(segs[-1][1], i))
            continue
        flat.append(pat)

    return _nest(flat), notes, drops


def _nest(flat: list) -> list:
    """Anchors own everything after them until a heading at depth <= their own."""
    root: list = []
    stack: list[Anchor] = []

    def cur() -> list:
        return stack[-1].body if stack else root

    for item in flat:
        d = item.depth if isinstance(item, (Anchor, Pat)) else None
        if d is not None:
            while stack and d <= stack[-1].depth:
                stack.pop()
        cur().append(item)
        if isinstance(item, Anchor):
            stack.append(item)
    return root


# --------------------------------------------------------------------- matching

@dataclass
class Result:
    ok: bool
    bindings: dict = field(default_factory=dict)
    unbound: list = field(default_factory=list)
    failures: list = field(default_factory=list)
    notes: list = field(default_factory=list)

    def __str__(self) -> str:
        head = "MATCH" if self.ok else "NO MATCH"
        bits = [head]
        if self.bindings:
            bits.append("  bindings: " + ", ".join(
                f"{k}={v!r}" for k, v in sorted(self.bindings.items())))
        if self.unbound:
            bits.append("  unbound: " + ", ".join(sorted(set(self.unbound))))
        for f in self.failures:
            bits.append("  ! " + f)
        for n in self.notes:
            bits.append("  . " + n)
        return "\n".join(bits)


class _Ctx:
    def __init__(self, env, multiplicity):
        self.b = dict(env or {})
        self.env_keys = set(self.b)
        self.unbound: list[str] = []
        self.failures: list[str] = []
        self.notes: list[str] = []
        self.multiplicity = multiplicity


def _segs_regex(segs, bindings):
    """Build an anchored regex for one line/heading-text pattern.

    A variable already bound (from a filename, or from an earlier line) is
    emitted as a LITERAL — this is what makes a binding per-member and shared
    across a member's artifacts, which is T5's central claim, and what lets the
    corpus falsify it.
    """
    parts, names = [], []
    for i, (kind, val) in enumerate(segs):
        if kind == "lit":
            parts.append(re.escape(val))
        elif val in bindings:
            parts.append(re.escape(bindings[val]))
        else:
            last = i == len(segs) - 1
            parts.append("(.*)" if last else "(.*?)")
            names.append(val)
    return re.compile("^" + "".join(parts) + "$"), names


def _try(segs, target, bindings):
    rx, names = _segs_regex(segs, bindings)
    m = rx.match(target)
    if not m:
        return None
    return dict(zip(names, m.groups()))


def _free_names(segs, bindings) -> list[str]:
    return [v for k, v in segs if k == "var" and v not in bindings]


def _section_end(lines, i, depth, hi) -> int:
    """Where the section opened by a heading of `depth` at index i ends."""
    for j in range(i + 1, hi):
        hm = HEADING_RE.match(lines[j])
        if hm and len(hm.group(1)) <= depth:
            return j
    return hi


def _find_pat(pat, lines, cursor, hi, ctx, adepth_doc, adepth_sten):
    """First index at/after cursor satisfying `pat`.  Returns (idx, binds)."""
    heading_mode = pat.depth is not None and adepth_sten is not None
    want = None
    if heading_mode:
        want = adepth_doc + (pat.depth - adepth_sten)
    for i in range(cursor, hi):
        if heading_mode:
            hm = HEADING_RE.match(lines[i])
            if not hm or len(hm.group(1)) != want:
                continue
            binds = _try(pat.text_segs, hm.group(2), ctx.b)
        else:
            binds = _try(pat.segs, lines[i], ctx.b)
        if binds is not None:
            return i, binds
    return None, None


def _find_anchor(anc, lines, cursor, hi, ctx, adepth_doc, adepth_sten):
    if adepth_sten is None:
        want_min = anc.depth
    else:
        want_min = adepth_doc + (anc.depth - adepth_sten)
    for i in range(cursor, hi):
        hm = HEADING_RE.match(lines[i])
        if not hm:
            continue
        d = len(hm.group(1))
        if anc.mode == "==" and d != want_min:
            continue
        if anc.mode == "..." and d < want_min:
            continue
        binds = _try(anc.text_segs, hm.group(2), ctx.b)
        if binds is not None:
            return i, d, binds
    return None, None, None


def _match_body(items, lines, lo, hi, ctx, adepth_doc, adepth_sten) -> tuple[bool, int]:
    cursor = lo
    pending: list[Hole] = []

    def settle(hole_stop: int):
        if not pending:
            return
        if len(pending) > 1:
            ctx.notes.append(
                "adjacent holes " +
                " ".join("{{%s}}" % h.name for h in pending) +
                " — extent ambiguous; all but the last bound to nothing")
        for h in pending[:-1]:
            ctx.b.setdefault(h.name, "")
        last = pending[-1]
        ctx.b.setdefault(last.name, "\n".join(lines[cursor:hole_stop]))
        pending.clear()

    for item in items:
        if isinstance(item, Hole):
            pending.append(item)
            continue

        if isinstance(item, Blank):
            idx = next((i for i in range(cursor, hi) if lines[i] == ""), None)
            if idx is None:
                if pending:
                    settle(hi)
                    cursor = hi
                    continue
                ctx.failures.append(f"stencil line {item.lineno}: blank line not found")
                return False, cursor
            settle(idx)
            cursor = idx + 1
            continue

        if isinstance(item, Pat):
            idx, binds = _find_pat(item, lines, cursor, hi, ctx,
                                   adepth_doc, adepth_sten)
            if idx is None:
                free = _free_names(item.segs if item.depth is None or adepth_sten is None
                                   else item.text_segs, ctx.b)
                if ctx.multiplicity == "min0free" and free:
                    ctx.unbound.extend(free)
                    settle(cursor)
                    continue
                ctx.unbound.extend(free)
                ctx.failures.append(
                    f"stencil line {item.lineno}: no line matches {item.raw!r}")
                return False, cursor
            settle(idx)
            ctx.b.update(binds)
            cursor = idx + 1
            continue

        if isinstance(item, Anchor):
            idx, d, binds = _find_anchor(item, lines, cursor, hi, ctx,
                                         adepth_doc, adepth_sten)
            if idx is None:
                ctx.failures.append(
                    f"stencil line {item.lineno}: no heading anchors "
                    f"{item.mode} {''.join(s if k=='lit' else '{{%s}}' % s for k, s in item.text_segs)!r}")
                return False, cursor
            settle(idx)
            ctx.b.update(binds)
            end = _section_end(lines, idx, d, hi)
            ok, _ = _match_body(item.body, lines, idx + 1, end, ctx, d, item.depth)
            if not ok:
                return False, cursor
            cursor = end
            continue

    settle(hi)
    return True, cursor


def match(stencil_text: str, target_text: str, *, env: dict | None = None,
          extent: str = "line", multiplicity: str = "min1",
          single_brace_vars: bool = False) -> Result:
    """Match one stencil against one document."""
    items, notes, drops = parse_stencil(stencil_text, extent=extent,
                                        single_brace_vars=single_brace_vars)
    lines = normalize_lines(target_text)
    ctx = _Ctx(env, multiplicity)
    ctx.notes.extend(notes)
    ctx.notes.extend(drops)
    ok, _ = _match_body(items, lines, 0, len(lines), ctx, None, None)
    for k in list(ctx.b):
        if ctx.b[k] == "" and k not in ctx.env_keys:
            ctx.unbound.append(k)
    return Result(ok, ctx.b, ctx.unbound, ctx.failures, ctx.notes)


# ------------------------------------------------------------ folder direction

def match_folder(member_patterns: list[str], names: list[str], *,
                 env: dict | None = None,
                 single_brace_vars: bool = False) -> Result:
    """Match a folder stencil (a list of member names) against real filenames.

    A member with no free variable is bound and must appear EXACTLY ONCE.
    A member holding a free variable matches once per binding — any number,
    including none (many-by-variable).  Files nobody claims are fine: open world.
    """
    env = dict(env or {})
    ctx = _Ctx(env, "min1")
    bindings: dict = {}
    claimed: set[str] = set()
    for raw in member_patterns:
        segs = _segment(normalize_line(raw), single_brace_vars)
        free = _free_names(segs, env)
        hits = []
        for n in names:
            b = _try(segs, normalize_line(n), env)
            if b is not None:
                hits.append((n, b))
        if not free:
            if len(hits) != 1:
                ctx.failures.append(
                    f"member {raw!r}: expected exactly one, found {len(hits)}")
        for n, b in hits:
            claimed.add(n)
            for k, v in b.items():
                bindings.setdefault(k, []).append(v)
        if free and not hits:
            ctx.notes.append(
                f"member {raw!r}: zero bindings — permitted by many-by-variable, "
                f"and therefore unfalsifiable")
    extra = sorted(set(names) - claimed)
    if extra:
        ctx.notes.append("unclaimed files (open world permits): " + ", ".join(extra))
    return Result(not ctx.failures, bindings, ctx.unbound, ctx.failures, ctx.notes)


# ----------------------------------------------------------------- measurement

def count_occurrences(pattern_line: str, target_text: str, *,
                      env: dict | None = None) -> list[tuple[int, dict]]:
    """Every line of the target that the given one-line pattern matches.

    Used to measure how far a free-variable row pattern reaches — T6's
    "what it cannot do is stop".
    """
    segs = _segment(normalize_line(pattern_line), False)
    out = []
    for i, line in enumerate(normalize_lines(target_text)):
        b = _try(segs, line, dict(env or {}))
        if b is not None:
            out.append((i, b))
    return out


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    s = Path(argv[1]).read_text(encoding="utf-8")
    t = Path(argv[2]).read_text(encoding="utf-8")
    print(match(s, t))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
