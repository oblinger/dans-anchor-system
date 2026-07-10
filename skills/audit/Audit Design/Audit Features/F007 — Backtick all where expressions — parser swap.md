---
description: "Backtick-wrap every where:: expression; coordinated parser swap gated by a green test suite."
---

# [[SKA]] · F172 — Backtick all where:: expressions in rulesets — coordinated parser swap

## Summary

A rule's `where::` value is a selector expression — `file:{ANCHOR}/**/* PRD.md`, `sentinel:^## \d{4}-`, `{a,b}` brace-alternation, etc. — full of characters (`*`, `:`, `{}`, `!`) that are **markdown syntax** and corrupt rendering when written bare. The fix: **wrap the whole expression in backticks**, including the `file:` prefix — `` where:: `file:{ANCHOR}/**/* PRD.md` `` — so it renders as inline code and the glob stops screwing up the doc.

This is a **coordinated move**, not a find-replace: the scripts that *parse* `where::` (the F161 engine's selector parser in `audit-plan.py`, plus any other consumer) must strip the surrounding backticks before parsing. Do the code first, prove it with a test suite that captures current behavior, then swap every rule-set file, then verify the engine resolves **identically** to before.

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

**Done** (2026-07-05) — the coordinated sequence ran exactly as § Design ordered it, same day the hold released:

1. **Baseline first** — snapshotted `audit-plan --batch examples --json` + two representative anchor plans + the live `rules-ir.json` before touching anything.
2. **Parser** — `strip_ticks` in `warden_compile.py` (ruleset-header + rule-level `where::`) and `_strip_ticks` in `audit-plan.py` (both parse sites): a **single surrounding pair** is stripped only when the interior carries no further backtick, so prose values with inline code spans (`R-doc-structure`) pass through untouched and the bare legacy form stays accepted. `warden_docfire` + the Rust engine consume the parsed IR, so two parsers cover every consumer.
3. **Tests** — `test_warden_compile.test_backticked_where` pins strip semantics + a mixed fixture (backticked / bare / prose rule-level values).
4. **Sweep** — 60 `where::` lines across 57 ruleset files wrapped (machine selectors only: `always` / `anchor` / `file:` / `sentinel:` / bare globs; prose selectors skipped). **`FCT Query.md` (R-query) deliberately excluded** — another agent owns the query/groom surfaces right now; its 2 bare lines sweep later (parser tolerates both).
5. **Verified identical** — IR diff vs baseline: the 60 swept lines produced **zero** field diffs (byte-identical parse), moment dispatch + doc_rules identical; all three audit-plan snapshots byte-identical (modulo a cache-warm counter); 10 unit suites + 10 cargo tests + both Rust differentials + golden corpus 7/7 (both engines, unchanged signatures) + perf gate green; live corpus recompiled (465 rules) and smoke through the installed Rust dispatcher clean.

**Bug fixed en route:** 8 rules (`R-cli-01..08`) had been authored backticked *before* any parser stripped ticks — the leading backtick made `parse_selector` read them as junk bare globs, so the whole R-cli family was **silently dead**. Post-swap they parse to real `file:` selectors and match their CLI docs again (proven against `HBR CLI.md`). `R-ruleset-12` + [[DAS Ruleset]] § Where clause now document the backtick-wrapped authored form as canonical.

**Earlier: Blocked** — spec complete, but the sweep was HELD until the Warden M0 language freeze lands ([[F210 — Conjunction binding + indexing|F210]] pins the `where::`/`if::` grammar this sweep would rewrite — running first risks a second vault-wide pass). Execute the coordinated sequence when M0 freezes.
