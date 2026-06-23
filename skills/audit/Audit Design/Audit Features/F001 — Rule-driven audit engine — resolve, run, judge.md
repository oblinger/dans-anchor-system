---
description: "The engine: resolve applicable rules per target, run mechanical by script, judge the rest by agent; content-hash cached."
---

# [[Audit]] · F001 — Rule-driven audit engine — resolve, run, judge

## Summary

A single engine that audits an anchor (or a document) against **the rules of the facets it has** — and scales from one anchor to a vault-wide batch. The system already has the right primitives: rulesets (`R-<facet>`) with per-rule **tiers** (`checked` / `sampled` / `stated` / `tracked`) and `Check pattern` blocks ([[FCT Ruleset]]). This feature is the matcher + scheduler that binds rules to targets and runs them — **mechanical rules by script, judgment rules by agent** — with caching so re-audits are cheap.

It unifies today's piecemeal audits (`/audit anchor`, `/audit rules`, `/audit dispatch`) under one pipeline and adds the missing **batch** mode.

## Success Criteria

**Tier:** 1 (agent-immediate)
**Blocks next:** none

**What done looks like.** `/audit anchor <X>` resolves X's facets → the union of their rulesets → binds each rule to a concrete target in X → runs `checked` rules by script and `stated`/`sampled` rules by agent → emits a per-rule pass/fail/N-A report. A `--batch` run over a directory of anchors produces the same per-anchor reports, re-running only rules whose target file (or rule) changed since the last run.

**How it will be verified.** Run the engine on the FEX examples ([[HBR]], [[ESR]]) — every `R-anchor-page` rule reports pass on the (perfect) examples; deliberately break one rule in a scratch copy and confirm it reports fail; confirm a second run with no changes reuses cached verdicts (timing / cache-hit log).

## Design

### The surface — two commands, two umbrellas

Two entry points, each resolving its own umbrella ruleset:

- **`/audit anchor <path-or-slug>`** — audits a whole anchor (folder path or slug). Pulls the umbrella **`R-anchor`** (the union of every anchor-level facet's ruleset). Auditing the anchor's documents is *part of* this — each doc target also gets its doc-level rules.
- **`/audit doc <path>`** — audits a single document at the document level. Pulls the umbrella **`R-doc`** (the union of the doc-facet rulesets, [[FCT Document]]).

Both implicitly walk to the relevant rule data set; the command names which umbrella. `R-anchor` and `R-doc` are `include::`-umbrellas over the per-facet `# RULESET` blocks — so adding a facet's rules to an audit is just adding it to the umbrella's `include::`.

### The frame — a lint engine over the rulesets

Think ESLint, not a bespoke checker: **rules** (each with a selector + a checker), **targets** (files/regions), a **scheduler** that matches rules to targets, runs the mechanical ones, and batches the judgment ones, with a **content-hash cache**. The tier annotation already in every rule *is* the mechanical-vs-judgment split:

| Tier | Who runs it |
|---|---|
| `checked` | **script** — deterministic, cached by content-hash |
| `sampled` | script where possible, else agent (risk-prioritized) |
| `stated` | **agent** — judgment, batched + cached |
| `tracked` | neither — recorded for awareness only |

### Three-stage pipeline: Resolve → Run → Judge

**Stage 1 — RESOLVE (pure compute, cached): "what rules apply where?"**
For an anchor:
1. **Detect facets** — from `.anchor` traits **and** structural presence (`{NAME} Design/` → design facet; `{NAME} Backlog.md` → backlog facet; the entry page → anchor-page facet; …). Facet presence is mostly *folder/file presence*.
2. **Flatten** the union of those facets' rulesets (resolve the `include::` DAG) → one flat rule list.
3. **Bind** each rule to its concrete target(s) in *this* anchor via its selector (Q1). If the target is absent → the rule is **N/A** (skipped, never failed). This is exactly the "not looking at a backlog → don't check backlog rules" case, handled structurally by selector-misses.

Output: a **worklist** of `(rule-id, tier, target-path, checker)` rows. Pure data — cacheable.

**Stage 2 — RUN mechanical rules (script, content-hash cache).**
The rule-runner executes each `checked` rule's checker against its target. Cache each verdict by `(rule-id, target-content-hash)` — unchanged file + unchanged rule ⇒ reuse. This is the batch win: a vault re-audit only re-runs rules on files that changed.

**Stage 3 — JUDGE non-mechanical rules (agent, batched).**
The residue (`stated` / unscriptable `sampled`) goes to the agent. Batch smartly — group by rule (one rule × many targets) or by target (many rules × one file) — dispatch to subagents, cache verdicts by the Q3 key. The agent reads rule + target, returns pass/fail + reason.

### Where-clauses + iteration order (file-major vs rule-major)

Each rule carries a **`where::` clause** — the selector, as a **glob** — saying which files it tests. **Precedence:** a rule's own `where::` wins; if it has none, its ruleset's `where::` applies (a typing-saver — write it once for all backlog rules); if neither, the scope default (`always`). Anchor-root is the explicit token **`{ANCHOR}`** (`{ANCHOR}/* Backlog.md`); bare globs are anchor-relative. Three scope kinds:

- **`always`** — universal; every file (naming, markdown hygiene).
- **`file: <glob>`** — per file matching the glob (most rules: `* Backlog.md`, the `{slug}.md` anchor page, …).
- **`anchor`** — once per anchor, checking the *tree/structure* not one file's content (`.anchor` has a slug; `Design` row iff `{NAME} Design/` exists). Doc audits add a **region** scope (a heading-block within the file).

The script glob-matches to build the bipartite **(rule × file) match set**, then the **scheduler picks the iteration order by job:**

- **Single anchor → file-major.** Few files; emit a per-file report. Walk files; for each, run its matched rules ("universal rules + these file-specific rules").
- **Batch / vault → rule-major.** Invert: load the backlog ruleset once → glob every `* Backlog.md` across the vault → sweep them; then triage rules → all triage files; then anchor-page rules → all `{slug}.md`; etc. One ruleset in context at a time over many homogeneous files — better agent focus, better cache locality, minimal context-switching. (The classic join-order choice: drive from the smaller side.)

Same match set both ways; only the grouping differs. The tier-split rides underneath: `checked` rules run *in the glob sweep* (no agent); only the `stated`/`sampled` residue reaches the batched agent. The caches make re-audits cheap; rule-major batch parallelizes across subagents.

### The artifacts — planner script + query-plan recipe

`audit-plan <path-or-slug>` (Python) is the resolver/planner. It:
1. **Flattens + merges** the applicable rulesets and materializes each grouping as a **cached flat rule file** (hashed → reused across anchors and runs).
2. **Glob-matches** the `where::` clauses into the (ruleset × files) groupings.
3. **Runs the mechanical (`checked`) rules itself** during the sweep and bakes their pass/fail into the plan.
4. **Emits a query-plan recipe** — rule-major for batch (`ruleset R-backlog [cached at …] → check files X, Y, Z; R-triage → …`), file-major for a single anchor — listing, per grouping, the cached rule file + only the **judgment residue** (`stated`/`sampled` rules × files-needing-judgment, minus cache hits).

The agent then **just follows the recipe**: read a grouping's flat rule file, judge its listed files, emit verdicts — no rule-selection thinking. The plan itself is cached (keyed by `anchor-tree-hash` + `rules-hash`), so an unchanged re-audit reuses plan + verdicts and does near-zero agent work.

### Caches (the precompute layer)

1. **Flattened-rules cache** — `R-<facet>` → flat rule list (invalidate on rule-file change). Shared across all anchors.
2. **Verdict cache** — `(rule-id, rule-body-hash, target-content-hash[, model-id])` → pass/fail + reason. The big batch win.
3. **Anchor-manifest cache** — anchor → facets + target map (invalidate on tree change). Skips re-resolve.

### Documents vs. anchors — same engine, smaller facet set

A document's doc-facets ([[FCT Document]]: Ruleset / Brief / Discussion / Glossary / Log / Messages) are just another facet set whose targets are *regions within the file* rather than files in a tree. Same Resolve→Run→Judge; the selector resolves to a heading-region instead of a path.

### Division of labor (the scripting / cache / precompute / agentic split the user asked for)

- **Scripting:** Stage 1 (resolve) + Stage 2 (mechanical run) + cache management.
- **Precompute / cache:** the three caches + the batch index.
- **Agentic action:** Stage 3 (judgment), final synthesis/report, and offering fixes.

Net effect: mechanical rules never burn agent tokens; the agent only sees the genuine-judgment residue; a re-audit of a large vault touches only changed files.

### Relationship to existing skills

`/audit anchor` becomes "run the pipeline on one anchor." `/audit dispatch` stays the table-fixer Stage-2 checker delegates to. `/audit rules` folds into the flatten + Stage-1 resolve. Batch mode is the new capability. The planned `flatten-ruleset.py` is Stage 1's flattener.

## Status

**Parked on `Next` (2026-06-13).** The engine, both command surfaces (`/audit anchor`, `/audit doc`), all three caches, and the full `where::` matcher (per F168) are complete and **deployable today**. The only open work is the incremental Slice-10 grind, captured in **§ Remaining — deferred to Next** below. Deferred deliberately: the engine already works without it — un-annotated `checked` rules route to the agent-judgment path, so completeness of the mechanical split is an optimization, not a blocker.

**Slice 1 — document rulesets + umbrellas (done).** All doc-facet rulesets exist (R-ruleset / R-brief / R-discussion / R-log / R-messages), `R-doc` umbrella wired; `R-anchor` umbrella created (R-doc + anchor-page / naming / design / roadmap / prd / status / stories).

**Slice 2 — `audit-plan` resolver (done, 2026-06-13).** `skills/audit/scripts/audit-plan.py` implements Stage 1 (RESOLVE) end-to-end: flattens an umbrella through its `include::` DAG to leaf `# RULESET` blocks (standalone stubs + embedded-in-facet, with a repo-wide fallback for stub-less sets like R-ruleset / R-file-association); resolves each rule's `where::` selector (scope kinds `always` / `file:<glob>` / `anchor` / `sentinel:<regex>`, `{ANCHOR}` token, `rule > ruleset > always` precedence); builds the (rule × target) match set with selector-miss = N/A; caches flattened rule files (reused, not rewritten); emits a query-plan recipe (file-major for a single anchor/doc, rule-major for `--batch`). Verified on [[HBR]]: 9 rulesets, 25 files, **0 unresolved includes**; doc-mode + batch (10 nested anchors) work; flat-cache reuse confirmed. The run also surfaced + fixed a real latent bug — `R-anchor-page` had no `where::` (defaulted to `always`, matching every file); set `where:: anchor` so it binds once per anchor.

**Slice 3 — Stage 2 mechanical execution (core done, 2026-06-13).** `audit-plan --run` executes the mechanical rules: a `check::` machine-ref field on each checked rule (prose `Check pattern` stays the human spec) names a primitive from a small checker library (7 so far: `anchor_has` / `entry_page_matches_slug` / `frontmatter_has` / `h1_present` / `no_blank_after_h1` / `regex_present` / `regex_absent`); verdicts are cached by `(rule-id, rule-body-hash, target-content-hash)`. Verified the SC's break-detection: HBR passes 4/4; a broken copy correctly fails R-anchor-page-03 (`frontmatter missing description:`); cache reuse confirmed (2nd run = 4 cache hits). Initial `check::` annotations on R-anchor-page-01/02/03/07 (in `facets/FCT Anchor Page.md`).

**Slice 4 — batch dedup + shared flatten cache (done, 2026-06-13).** Nearest-anchor ownership: every file is audited by its *deepest* enclosing anchor, so a parent anchor's scope drops nested sub-anchor subtrees (`sub_anchor_roots` + `enumerate_scope(exclude_roots=…)`), applied uniformly to single audits and `--batch` (a single audit is a batch-of-one). HBR's scope dropped from 25 files (it was swallowing its 5 nested sub-anchors) to its own 4; the nested anchors get their own plans. Added `flatten_umbrella_cached` — an in-process memo + disk cache keyed by a repo-wide md corpus signature (relpath+mtime+size) — so a batch flattens the include:: DAG **once** instead of per-anchor. Verified: cold batch over `examples/` (10 anchors) = `1 miss / 0 disk-hit / 9 mem-hit`; warm batch = `0 miss / 1 disk-hit / 9 mem-hit`; HBR `--run` still 4/4 pass; break-detection still fails R-anchor-page-03 on a description-stripped scratch copy.

**Slice 5 — Stage 3 agent-judge scaffolding (done, 2026-06-13).** `audit-plan <target> --judge --model M` emits the judgment residue as a manifest — every rule needing the agent (`stated`, plus `sampled`/`checked` with no usable `check::`; `tracked` skipped as awareness-only) × its matched targets — pre-filtered by the verdict cache, each task carrying the **full Q3 key** `(rule-id, judge-body-hash, target-content-hash, model-id)`. The driving agent judges each task, then `audit-plan --record-verdict --key K --status pass|fail --detail D` persists the verdict under that key; a re-judge with unchanged rule + target + model serves it from cache (zero agent work). Verified on HBR: 294 judgment tasks; record one → re-run = 293 to-judge / 1 cached with the recorded verdict returned; **model-id partitions the cache** (`--model other` = 0 cached). Factored a shared `_content_hash` helper. The script side of Stage 3 is complete; the agent-runtime driver (the `/audit` skill loop that reads the manifest, dispatches subagents, calls `--record-verdict`) is the remaining piece.

**Slice 6 — unified `--report` (done, 2026-06-13).** `audit-plan <target> --report` runs the mechanical checks and the judgment manifest together and prints one audit view: pass/fail/error counts (+ cache hits), the mechanical-failure list, and the judgment residue summarized by ruleset. Additive (no skill-contract change). This is the script-side **synthesis** half of the remaining bundle; the agent-runtime orchestration (the `/audit` skill driving the loop + writing backlog rows) is what's left. Verified on HBR: `4 pass · 0 fail · 0 error`, 293 to-judge across 9 rulesets, 1 judged-cached.

**Slice 7 — `/audit anchor` wired to the engine (done, 2026-06-13).** `audit-anchor.md` now drives `audit-plan` (resolve → `--run` mechanical → `--judge`/`--record-verdict` agent loop) instead of hand-walking the A/B/C checks — those become the human-readable summary of `R-anchor`; the engine is the executable form, so the two never drift. Fail-verdicts map onto the established state-clustered backlog contract (mechanical → one `[Ready]` row, judgment-fails-needing-input → `[Questions]` rows, sub-bullets = findings, minted via `state task create`). `SKILL.md`'s `/audit anchor` action row updated; doc-level audit documented as the `audit-plan <file> --mode doc` sibling. Verified the runbook's script path resolves through the `~/.claude/skills` symlink and runs.

**Slice 8 — `/audit doc` first-class action (done, 2026-06-13).** `audit-doc.md` created + `SKILL.md` action row added — `/audit doc <file>` drives `audit-plan --mode doc` over the `R-doc` umbrella (markdown / file-association / brief / discussion / log / messages), same run → judge → record → backlog-row flow as `/audit anchor`. Completes the F161 two-command surface. Verified doc-mode on a standalone doc: `R-doc` → 2 applicable rulesets, 17 judgment tasks.

**Slice 9 — whole-plan (anchor-manifest) cache (done, 2026-06-13).** `plan_one` now caches the resolved `(rule × target)` plan keyed by abs-anchor + mode + tree-hash (relpath + bytes of every scope file + `.anchor`) + rules-hash (selector/tier/checker fields); an unchanged re-audit returns the cached plan and skips selector resolution entirely, and any file edit or rule-field change invalidates it. Completes the design's **three-cache set** (flattened-rules + verdict + plan). Verified: warm batch over `examples/` = 10/10 plan hits, cached plan byte-identical to fresh resolution, edit-then-rerun re-resolves cleanly.

**The F161 engine, both command surfaces, and all three caches are complete.**

**`where::` matcher completed to the full [[FCT Ruleset]] § Where clause spec (2026-06-13, per F168).** The Stage-1 selector resolver previously honored only `{ANCHOR}/` + standard globs (`*`/`**`/`?`/`[...]`) for the `file:` kind; the F168 spec additions (`{NAME}` substitution, `{a,b}` brace-alternation, comma-separated union, gitignore-style `!`-negation) now resolve too (`_anchor_name` / `_expand_braces` / `_split_terms` / `_match_file_glob` in `audit-plan.py`). Verified on a scratch anchor: `{ANCHOR}/**/{NAME} Backlog.md` → the backlog; `*.{svg,png}` → both; `{NAME} {PRD,Roadmap}.md` → the PRD; `*, !*.png` → everything except the png. HBR `--report` regression-clean (the lone `R-design-04` fail is a real finding — HBR example lacks `HBR Track/HBR Status.md` — and is `anchor`-scoped, untouched by the matcher change). This closes the deployability gap for the where-clause system: every example in the spec now binds to real files.

**Slice 10 — resume `check::` annotation (in progress, 2026-06-13).** The facet restructuring landed (commit `5644d4a`, clean tree) — engine still resolves `R-anchor` to 9 leaves with 0 warnings against the new layout. Resumed annotating `checked` rules: added 3 primitives (`h1_matches_slug`, `breadcrumb_row`, `design_row_iff_folder`) and annotated `R-anchor-page` 05/11/13. HBR mechanical 4/4 → 7/7 pass; break-detection verified for each. The 6 complex `R-anchor-page` rules (09 page-order, 12 Related-laterality, 16 cell-pipe-escape, 20 member-zone-marker, 21 name-prefix, 15 no-track-row) are intentionally left to the judgment path — naive primitives would false-positive against the spec's exceptions.

**`R-naming` annotated (2026-06-13).** `R-naming-01` → new `name_slug_prefixed` primitive (per-file: basename starts with `{slug} `, equals the anchor marker, or matches a sanctioned allowlist shape). Verifying against every example anchor caught two sanctioned patterns **missing from the R-naming-03 allowlist** — `SKILL.md` and `R-<x>.md` — which would have false-failed vault-wide; added both to the spec + checker. HBR 11/11 mechanical pass. R-naming-03 is folded into 01 (no separate checker); R-naming-05 deferred (overlaps R-anchor-page-02 and needs a `where:: anchor` spec touch). **Real finding surfaced (not an F161 bug):** the `FEX Repo` example anchor is malformed — its `.anchor` declares no `slug:`/`traits:`, and its files mix `FEX`/`FEX Repo` prefixes; the audit correctly flags it. Needs a decision: is that anchor's slug `FEX` or `FEX Repo`? (Resolving it touches the `.anchor` + the entry-page filename + the member files.)

### Remaining — deferred to Next (captured 2026-06-13)

The engine is done and usable; these are the open items for whoever resumes F161:

1. **Annotate the remaining `checked` rules with `check::` primitives** — the per-ruleset grind: `R-facet-spec` (~15), `R-rules` (~11), `R-prd` (~8), `R-testing` (~7), `R-status` (~7), `R-stories` (~6), `R-roadmap` (~6), `R-diagram-geometry` (~5), … Each rule needs a *safe* primitive **verified against a real example before commit** — the R-naming / R-anchor-page passes showed this routinely surfaces spec gaps and real example bugs, so it's investigative work, not a mechanical sweep. The engine runs against whatever `check::` refs exist, so each annotation just widens the mechanical (free, cached) share; un-annotated rules keep working via the judgment path.
2. **Leave the genuinely-ambiguous rules on the judgment path** — e.g. the 6 complex `R-anchor-page` rules (09 page-order, 12 Related-laterality, 16 cell-pipe-escape, 20 member-zone-marker, 21 name-prefix, 15 no-track-row); naive primitives false-positive against the spec's exceptions. Annotate only where a primitive is provably safe.
3. **Fix the anchor-scoped verdict-cache invalidation bug (found 2026-06-13).** An `anchor`-kind rule's verdict is cached by `(rule-id, rule-body-hash, target-content-hash)` with the anchor root as target — but the anchor-target content-hash is `.anchor`-only, not tree-aware, so **adding / removing a file does not invalidate the cached verdict**. Observed: after adding `HBR Track/HBR Status.md`, `R-design-04` still served its stale `fail` until the cache was cleared. Fix: fold the anchor tree-hash (already computed for the plan cache, `_plan_tree_hash`) into the content-hash used for `anchor`-target verdicts.
4. **`R-naming-05`** — deferred; overlaps `R-anchor-page-02` and needs a `where:: anchor` spec touch before it can be annotated.
5. **`FEX Repo` example anchor is malformed** (surfaced by the audit, see R-naming note above) — its `.anchor` declares no `slug:`/`traits:` and its files mix `FEX`/`FEX Repo` prefixes. Needs a slug decision (`FEX` vs `FEX Repo`), then fix the `.anchor` + entry-page filename + member files. (Example-fix, not engine work.)

## Resolved

### Surface — two commands (`/audit anchor`, `/audit doc`) over two umbrellas (`R-anchor`, `R-doc`)
**Choice:** `/audit anchor <path-or-slug>` resolves the `R-anchor` umbrella; `/audit doc <path>` resolves the `R-doc` umbrella. Auditing an anchor includes auditing its documents. The umbrellas `include::` the per-facet `# RULESET` blocks, so each command implicitly knows the rule data set to pull. (User direction, this session.)

### Q1 — Rule selectors (the `where::` clause)
**Choice:** Each rule carries a `where::` selector — a **glob** (anchor-root = the explicit `{ANCHOR}` token; bare globs anchor-relative). **Rule-level `where::` overrides ruleset-level**; the ruleset `where::` is the typing-saver default; absent both, scope default `always`. Three scope kinds: `always` / `file: <glob>` / `anchor` (+ region for docs). The script glob-matches to build the (rule × file) set; the scheduler iterates **file-major** (single anchor) or **rule-major** (batch). (Refined per user direction this session — see Design § Where-clauses + iteration order.)

### Artifacts — planner script + cached query-plan recipe
**Choice:** A Python planner (`audit-plan <path>`) flattens the applicable rulesets into cached flat rule files, glob-matches `where::` clauses into (ruleset × files) groupings, runs the `checked` rules itself, and emits a query-plan recipe (rule-major for batch, file-major for single) naming per grouping the cached rule file + the judgment residue. The agent follows the recipe — no rule-selection thinking. Plan + verdicts are cached (`anchor-tree-hash` + `rules-hash`) so unchanged re-audits do near-zero agent work. (User-confirmed implementation shape, this session.)

### Q2 — Making `checked` rules mechanical
**Choice:** A small reusable checker library (~10 primitives) named by each rule; the prose `Check pattern` stays the human spec. Confirmed.

### Q3 — Judgment-verdict cache key
**Choice:** `(rule-id, rule-body-hash, target-content-hash, model-id)`. Confirmed.

### Q4 — Source of the facet→rule binding
**Choice:** The embedded `# RULESET R-<facet>` block is the source of truth; `R-anchor` / `R-doc` umbrellas aggregate via `include::`; the `Rulesets` catalog is an index. Confirmed.
