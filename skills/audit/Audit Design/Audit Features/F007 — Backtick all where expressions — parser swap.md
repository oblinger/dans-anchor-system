---
description: "Backtick-wrap every where:: expression; coordinated parser swap gated by a green test suite."
---

# [[SKA]] · F172 — Backtick all where:: expressions in rulesets — coordinated parser swap

## Summary

A rule's `where::` value is a selector expression — `file:{ANCHOR}/**/* PRD.md`, `sentinel:^## \d{4}-`, `{a,b}` brace-alternation, etc. — full of characters (`*`, `:`, `{}`, `!`) that are **markdown syntax** and corrupt rendering when written bare. The fix: **wrap the whole expression in backticks**, including the `file:` prefix — `` where:: `file:{ANCHOR}/**/* PRD.md` `` — so it renders as inline code and the glob stops screwing up the doc.

This is a **coordinated move**, not a find-replace: the scripts that *parse* `where::` (the F161 engine's selector parser in `audit-plan.py`, plus any other consumer) must strip the surrounding backticks before parsing. Do the code first, prove it with a test suite that captures current behavior, then swap every rule-set file, then verify the engine resolves **identically** to before.

Parked on **Next** — not being taken on now.

## Success Criteria

**Tier:** 1 (agent-immediate)
**Blocks next:** none

**What done looks like.** Every `where::` line across all rule sets is `` where:: `<expr>` `` (backtick-wrapped, whole expression). The selector parser accepts both backticked and bare forms (backticked canonical), and a vault-wide `audit-plan` run produces the **same (rule × target) match sets** as before the swap. A rule-set test suite exists and is green both before and after the change.

**How it will be verified.** (1) Snapshot the current resolution: `audit-plan --batch examples --json` (and a representative anchor set) → baseline match sets. (2) After the parser change + file swap, re-run → diff must be empty (identical matches). (3) The new/extended test suite passes. (4) Spot-check that a backticked `where::` renders as inline code in Obsidian (no broken markdown).

## Design

### The change

- **Form:** `where:: <expr>` → `` where:: `<expr>` `` — backticks wrap the **entire** expression (the `file:` / `sentinel:` prefix is *inside* the backticks). Applies to rule-level and ruleset-header `where::` alike.
- **Why whole-expression:** the prefix + glob is one syntactic unit; half-wrapping is ugly and still leaks `:` outside. Inside one code span, none of `*:{}!` is interpreted by markdown.

### Coordinated sequence (the order matters)

1. **Build / extend the rule-set test suite** — capture the *current* behavior of the `where::` parser + the engine's match-set resolution (the selector parser in `audit-plan.py`: the `where::` field extraction, `parse_selector`, `match_targets`; plus any other script that reads `where::`). Baseline = a snapshot of match sets over `examples/` + a representative anchor set. **Run it; confirm green** before touching anything.
2. **Design + write the new parser code** — the `where::` reader strips a single surrounding pair of backticks (and tolerates bare, for migration). Keep everything downstream identical.
3. **Verify the new code** — the test suite passes with *both* backticked and bare inputs; unit-test the backtick-strip.
4. **Swap all the files** — wrap every `where::` value across all rule-set files (facets' embedded `# RULESET` blocks + standalone rule-set files) in backticks. Mechanical sweep, but verify each.
5. **Verify nothing changed** — re-run the baseline snapshot; the (rule × target) match sets must be **identical** to step 1. Any diff is a regression to fix before done.

### Scope of consumers to update (find them all first)

- `audit-plan.py` — the primary `where::` parser (F161). Confirmed consumer.
- Any `where::`-reading sweep/lint scripts (e.g. a future `lint-ruleset.py`), and the `R-ruleset` facet's documented `where::` syntax (R-ruleset-12) — update the examples to the backticked form.
- A grep for `where::` across scripts is step 0 of step 1, so no consumer is missed.

### Why a test suite first (the load-bearing discipline)

The selector engine is now load-bearing across `/audit`. A blind find-replace could silently change which files a rule matches (a stray backtick inside a glob, a parser that strips too much). The test = a frozen snapshot of match sets; the swap is only "done" when the snapshot is byte-identical after. This also seeds the **rule-set testing strategy** (extend it, don't one-off it).

## Status

**Ready** — parked on Next. Spec complete; no open questions. Execute the coordinated sequence when picked up.
