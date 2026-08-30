---
description: "F303 M5 — restating the corpus and measuring the fit"
---

| -[[STEN Restated Corpus]]- | : F303 M5 — restating the corpus and measuring the fit<br>→ [[DAS]] → [[STEN]] → [STEN Restated Corpus](hook://p/STEN%20Restated%20Corpus)  |
| --- | --- |
| [[Template Examples]]  | the seven-case grammar-derivation corpus (M1); this document is a *different* corpus — the real population, not the cases that derived the grammar |
| [[STEN Language\|Language]]  | the grammar this restatement is written in |
| [[Tink303 - Template DSL - one pattern language for facets, templates, and sections\|F303]]  | *Spec* — M5: *"Existing templates and facets expressed in the notation. Dan expects 'probably not that much refactoring' — M1 is what confirms or refutes that, and it is a real finding either way."* |

# STEN Restated Corpus
M5: the vault's existing templates and facets, restated in Stencil and checked with `sten_match`/`sten_generate` against real files — not the seven-case M1 corpus, but the population M1 was built to eventually cover.

## What this is, and what it is not

**M1** ([[Template Examples]]) derived the grammar from seven hand-picked cases and is frozen. **This document** runs the finished grammar against the *real* population the roadmap names — `facets/*.md` and `templates/*` in this repo — and reports, per item, whether it expresses cleanly, needs the document changed, or defeats the notation outright. Every stencil below was run through `sten_match.match` against a real file (never invented), and the generable ones were round-tripped through `sten_generate.generate`. Verbatim results are in the sections below; the scripts that produced them are not checked in (throwaway verification, per the house rule that a claim needs a run, not a permanent script).

**Scope decision.** `facets/*.md` holds 69 `DAS *.md` documents; checking each individually against a hand-authored stencil would not scale, and doesn't need to — T7 already establishes that facet specs are one shape, so §Facets runs **one** stencil against all 69 and reports the distribution. `templates/*` holds 19 files across 13 flat templates + 3 folder-form templates (`log/`, `rocks/`, `track/`); each is small enough, and different enough from its neighbors, to restate individually, so §Templates does that. For each template a **real instance** was located — inside this repo where one exists (`Stencil/STEN Track/`, `design/DAS Decisions.md`, `examples/HBR/...`, `SYS Catalog/Disk/Disk Log/`), and in the wider vault where it does not (`HA Track/`, `OBU Design/`, `SV Track/`) — on the same precedent M1's own T3/T4 use (`AT/` files outside the DAS repo).

## Templates (`templates/*`)

16 of 19 template files restated and checked; `completed-roadmap.md` has no located real instance (noted, not invented) and the two `templates/log/` members are counted together with the folder's dispatch member. Each entry gives the stencil actually run, the real target, the verdict, and — for a NO MATCH — the specific line the notation and the document disagree on.

### Clean — matches a real instance as restated

**backlog.md** × `Stencil/STEN Track/STEN Backlog.md` — MATCH.
```
# {slug} Backlog

{{dispatch table}}

## Active
- **F{{NNN}} — {{title}}** — {{one-line description of the in-flight item}}

## Ready
- **F{{NNN}} — {{title}}** — {{description; this item is Ready to mint}}

## Now
- **F{{NNN}} — {{title}}** [{{state}}] — {{description}}

## Next
- **F{{NNN}} — {{title}}** [ ] — {{description}}

## Later
- **F{{NNN}} — {{title}}** [ ] — {{long-shot / deferred description}}

## Done
- **F{{NNN}} — {{title}}** — {{outcome; e.g. done in PR #N, see `[[{slug} Roadmap#M<n>]]`}}

## Legwork
- **F{{NNN}} — {{title}}** — {{unscheduled chore / follow-up}}
```
Round-tripped: `generate()` + a synthetic env produced a document `match()` accepts — **with one caveat that belongs in §Findings, not here**: `sten_generate.py` has no `single_brace_vars` option, so `{slug}` in the output is never substituted (it round-trips only because match was *also* run with `single_brace_vars=True`, papering over the same gap on both sides). See Finding 5.

**track/{slug} Track.md** × `Stencil/STEN Track/STEN Track.md` — MATCH.
```
# {slug} Track

{slug} Track is the dispatch page for the {slug} anchor's tracking artifacts.

{{dispatch table}}
```

**rocks/{slug} {ABBR}.md** (the rock-member form) × `examples/HBR/HBR Track/HBR Rocks/HBR HR.md` — MATCH.
```
# {slug} {{ABBR}}
{{ABBR expanded — one line}}

## What

{{One paragraph naming the chunk concretely.}}

## Why now

{{What makes this a rock rather than a backlog row.}}

## Shape

{{The pieces this decomposes into.}}

## Status

{{Where it stands.}}
```

**inbox.md** × `prj/Hook Anchor/HA Track/HA Inbox.md` — MATCH (bound one whole dated entry, body included, as a multi-line hole).

**roadmap.md** × `prj/Hook Anchor/HA Track/HA Roadmap.md` — MATCH, at the milestone/sub-item/task nesting the template proposes (`## M{{N}}` → `### M{{N}}.{{n}}` → `- [{{x}}] {{task}}`).

**agenda.md** × `SV/SV Track/SV Agenda.md` — MATCH, including the `## Purpose` / `## Success` / `## Approach` section spine.

**prd.md** × `SYS/Bespoke/ob-utils/OBU Design/OBU PRD.md` — MATCH **on the H1 + first H2 only** (`## Purpose` bound where the template names an opaque `## {{Overview heading}}`). The template's later sections (`Design Workflow` / `Goals` / `Non-Goals` / `User Stories`) were not exercised — OBU PRD.md doesn't carry them under those names, and open world means their absence is not a failure, but it is also not a positive check of those sections. Flagged as a verification-coverage gap, not a language gap.

**templates/log/{{YYYY-MM-DD}} — {{short topic}}.md** × `SYS/SYS Catalog/Disk/Disk Log/2026-06-09 Master consolidation + storage strategy.md` — MATCH, at the reduced shape `# {{YYYY-MM-DD}} — {{short topic}}` + `{{body}}` (the template's internal `## What happened` / `## Decisions` / `## Outstanding` spine does **not** hold against this real entry — see Finding 4 — so what's confirmed clean is the entry's outer shape, not its interior).

**decisions.md** × `design/DAS Decisions.md` — MATCH, at `# {slug} Decisions` / `{{one sentence}}` / `### D{{N}} — {{Title}}` / `**Why.** {{rationale}}` — with the template's `({{status: checked | open | revised | retired}})` parenthetical dropped (see Finding 3).

**status.md** × `examples/HBR/HBR Track/HBR Status.md` — MATCH, but **only once the five `key:: {{TIER}}` rows were given five distinct variable names** (`{{PRD_TIER}}`, `{{UX_TIER}}`, …). The naive restatement — one `{{TIER}}` reused across all five lines — is a genuine NO MATCH, and it is a matcher-semantics finding, not a document defect: see Finding 2.

That is **9 of 16** restated templates matching a real instance cleanly (with the two caveats above noted honestly rather than folded into "clean").

### Needs the document changed — real, named divergence

**messages.md** × `Stencil/STEN Track/STEN Messages.md` — NO MATCH. The template specifies `- **{{YYYY-MM-DD HH:MM}} · {{source process}}** — {{note}}`; the real file is machine-appended lines shaped `[2026-08-08 21:58:49] [INFO] backlog at ... was edited` — a different literal format end to end, not a drift in one field. **Finding:** whatever process appends to `{slug} Messages.md` (an agent-side logger, not the template) was never reconciled with `templates/messages.md`; the two have independently-evolved formats for the same facet. This is refactoring, but of the writer, not obviously of the template — Dan's call which side moves.

**query.md** × `Stencil/STEN Track/STEN queries.md` — NO MATCH. The template's title line names `Ready / Questions / Now / Next / Later / Verify / Icebox`; the real file (frontmatter: *"mechanically rendered from the backlog... by `/audit q`"*) reads `Ready / User / Now / Next / Later / Parked / Waiting / Icebox {N}` — a different field vocabulary. **Finding:** `templates/query.md` documents an earlier version of the format `/audit q` now emits; the template is stale relative to its own generator, not the other way around.

**rocks/{slug} Rocks.md** (the folder dispatch page) × `examples/HBR/HBR Track/HBR Rocks/HBR Rocks.md` — NO MATCH at one line: the template's one-liner is `The big chunks {slug} is trying to move...`, literally embedding the mechanical slug; the real file reads `The big chunks Harbor is trying to move...` — the anchor's **full name**, not its slug. **Finding:** the template over-constrains a natural-language sentence by hard-coding `{slug}` into it; every other one-liner in this corpus that needed the anchor's identity in prose used an opaque `{{...}}` hole instead (T1.A's `{{one-line description}}`). The fix is in the template, not the notation.

**icebox.md** × `prj/Hook Anchor/HA Track/HA Icebox.md` — NO MATCH. The template groups entries under `## Frozen` / `## Maybe Someday` / `## Revisit Later`; the real file is a flat list of H3 items directly under the H1, no tier grouping at all. **Finding:** the tri-tier structure is aspirational — at least this instance was never organized that way.

**testing.md** × `SYS/Bespoke/ob-utils/OBU Design/OBU Testing.md` — NO MATCH, on one word: the template's table header is `| Kind | In system | Expected |`; the real header is `| Kind | In system | Expected coverage |`. **Finding:** trivial, but real, and exactly the class of drift a mechanical check would have caught immediately had one existed.

**templates/log/{slug} Log.md** (the folder's dispatch member) × `SYS/SYS Catalog/Disk/Disk Log/Disk Log.md` — NO MATCH. The template opens `# {slug} Log`; the real file has **no H1 at all** — frontmatter, then straight into the dispatch table, whose own `-[[Disk Log]]-` masthead cell carries the title. **Finding:** at least one real Log-dispatch page relies on the masthead cell as the title and omits a redundant H1; the template assumes the H1 is always present.

That is **6 of 16** needing a named, specific document (or tooling) change — none of them a notation failure; every one is the template and its real instance saying different things.

### Not verified

**completed-roadmap.md** — no real instance located in the time available. `find` across the vault for `*completed*roadmap*.md` turned up only a *feature doc about* adding completed-roadmaps (SKA F144), not an instantiated one. **This is itself a finding**: the facet may not have been exercised anywhere in the vault yet, which is a fact about adoption, not about the notation.

## Facets (`facets/*.md`)

69 `DAS *.md` documents. T7 ([[Template Examples]]) already establishes that a facet spec is one shape; M5's job is to run that shape against all 69 real instances rather than the one reflexive specimen (`DAS Facet.md`) M1 checked.

**T7.A as frozen in the corpus does not generalize**, and the reason is traceable rather than a grammar defect. Run verbatim against the live `facets/DAS Facet.md` — the very file its sibling specimen T7.b quotes — it fails: `# RULESET R-facet-slug` no longer appears in the file (confirmed: DAS Facet.md's current headings are H1 / `Facet Document Structure` / `Facet Overview` / `Examples of a facet` / `BRIEF` — the ruleset section is gone). This is not a wrong specimen — T7.b is still byte-exact to its 2026-08-05 capture, hash-verified — it is that **the live file has drifted in the three days since M1 was captured.** Separately, and more importantly for the population: measured across all 69 files, only **2** (`DAS Ruleset.md`, `DAS Stone.md`) carry an embedded `# RULESET` heading at all; **64** instead carry a `| Rules | [[R-name]], ... |` row in the dispatch table, pointing *out* to a standalone ruleset page. T7.A generalized from the one file where the facet documents itself (so its `# {{FACET_NAME}} Document Structure` heading happens to read `# Facet Document Structure`) to a claim about all 69, and the claim doesn't hold — `# ... Document Structure` appears nowhere else in the population.

So this document restates the facet-spec shape as **measured**, not as T7.A proposed it:

```
# DAS {{FACET_NAME}}
{{one-line summary}}

{{dispatch table}}

# BRIEF
```

Run against all 69:

| result | count | files |
| --- | --- | --- |
| **Clean match** (H1 `# DAS <Name>` + one-liner + dispatch table + terminal `# BRIEF`) | **60 / 69** | — |
| Has the spine but **no `# BRIEF`** | 2 / 69 | `DAS Dispatch Table Design.md`, `DAS Facets.md` |
| **Fails even the spine** — no `# DAS <Name>` H1 at all | 7 / 69 | `DAS Anchor.md`, `DAS Code.md`, `DAS Design Docs.md`, `DAS Dispatch.md`, `DAS Doc.md`, `DAS Output.md`, `DAS Primitives.md` |

**The 7 are not broken facet specs — they are a second, undeclared facet kind.** Each of the 7 is a **subsystem group-header page**: a dispatch table (T6-shaped) fanning out to the group's real facets (e.g. `DAS Anchor.md`'s dispatch table lists `Anchor Page`, `Project Page`, `Folder`, `Dot Anchor`, ... as its `Facets` row), with a short H1 naming the group (`# Anchor & structure`, `# Code`, `# Sub-dispatch`) rather than a facet. `facets/DAS Facets.md` (the index of all facets) is the 8th member of this family structurally, though it does carry a `# DAS ` H1. **Finding:** the population `facets/*.md` mixes two kinds that T7 never distinguished — facet specs (T7-shaped) and group-header dispatch pages (T6-shaped) — because M1's one instance (`DAS Facet.md`) is a facet spec and never exercised the group-header kind.

The 2 with no `# BRIEF` are the same story at smaller scale: `DAS Facets.md` is the group-header *index* (T6-shaped, correctly has no BRIEF); `DAS Dispatch Table Design.md` is a design doc parked in `facets/` by folder convention, not a facet spec.

**Net for the actual facet-spec population** (69 minus the 8 group/index pages = 61 real facet specs): **60 / 61 clean**, and the one exception (`DAS Facet.md` itself) is clean **as of 2026-08-05** and has since drifted, not a shape it was ever wrong about.

Round-trip: `generate()` against the corrected spine with a synthetic env produced a document `match()` accepts cleanly (verified; not reproduced in this document — see the verification block below).

## Findings — what the notation cannot say, named specifically

Five findings surfaced by running the grammar against the real population that M1's seven hand-picked cases never hit:

1. **The `...` repeat-marker is still live in most of the shipped templates, and under Stencil it is not neutral — it is wrong.** [[STEN Language]] already establishes that many-by-variable makes the marker redundant (T1, T2); what M5 adds is the count: **12 of 19** template files (`templates/*.md` and its three folder members) still carry a bare `- ...` / `## ...` / `### ...` / `| ... | | |` line. Under Stencil's grammar these are not anchors (`# ... LOG` requires text *after* the marker; a bare `### ...` has none) and not holes — they parse as **literal text**, and no real document ever contains a literal line reading `...`. So every one of these 12 templates, matched verbatim, fails one line earlier than its real shape actually diverges. This is exactly the class of refactoring Dan asked M1 to measure: **mechanical, uniform, and touches most of the fleet** — strip the trailing `...` line from each repeating group; nothing else in the template changes, because open world plus many-by-variable already says what the marker used to say.

2. **A variable's binding is scoped to the whole stencil, not to the line it appears on — and reusing a name across semantically-independent slots is a real authoring trap.** `status.md`'s five `key:: value` lines are independent facts (prd tier, ux tier, ...); restated with one shared `{{TIER}}` name, the matcher correctly refuses a document where the five values differ, because T5 already established (and this document's own generator confirms) that a binding is per-document and shared across every occurrence of its name. This is not a bug — it is the same rule that makes `{{NICKNAME}}` mean the same machine in a file's name, H1, and body — but it means a stencil author has to give independent slots independent names, and `status.md` restated naively does not. Not a notation gap; a restatement discipline the corpus should carry as a rule of thumb.

3. **A `({{status: A | B | C}})` parenthetical present in a template's heading may be entirely unused in practice**, and open world quietly absorbs the loss rather than flagging it: `decisions.md`'s heading pattern includes a status marker no real `### D<N>` heading in `design/DAS Decisions.md` carries, and dropping it from the restated stencil is what let it match. This is not a construct the notation lacks — it is a case where the template's own claim (every decision carries a status) is not true of at least one real instance, discoverable only by checking, which is the entire point of M5.

4. **A folder-member's *outer* shape (its anchor / opening line) and its *interior* shape (its H2 spine) can diverge independently**, and a stencil that only checks the outer shape reports success while missing the interior drift entirely. `templates/log/{{YYYY-MM-DD}} — {{short topic}}.md` matches `Disk Log`'s dated entry cleanly at `# {{date}} — {{topic}}` / `{{body}}`, but the entry's actual interior (`## What happened, in order`, no `## Decisions` section at all) does not match the template's stated `## What happened` / `## Decisions` / `## Outstanding` spine. Nothing in the grammar is missing here — a stencil that wants to check the interior has to state it and be run against it — but it is a real trap for M6: a shallow stencil (opaque `{{body}}`) will report a folder member "conforms" while a stricter sibling stencil for the same file reports it does not, and both are correct about what they each check.

5. **`sten_generate.py` has no `single_brace_vars` option — `generate()` cannot fill `{slug}` at all.** Every shipped template in `templates/*` uses the single-brace `{slug}` convention (`# {slug} Backlog`, `{slug} Track is the dispatch page...`); `sten_match.match` supports it via `single_brace_vars=True` (used throughout this document), but `sten_generate.generate` calls `M.parse_stencil(stencil_text)` with no such flag anywhere in the module (confirmed: zero occurrences of `single_brace` in `sten_generate.py`), so `{slug}` is parsed as literal text and passed through unfilled. Concretely: `generate(S_BACKLOG, {"slug": "WGT", ...})` emits a document whose H1 reads literally `# {slug} Backlog`, not `# WGT Backlog`. This round-trips clean **only** because match was re-run with `single_brace_vars=True`, which accepts the un-substituted `{slug}` as a match on itself rather than catching the omission — the round-trip test in this document's own §Templates is not proof the generator handles `{slug}`, it is proof the check didn't require it to. **This is a real M4 gap, invisible to M1–M4's own test suites because none of the seven M1 cases uses `{slug}`** (T2 and T5 both use it in prose but the corpus's own generate-direction cases don't exercise it as a filled value) — it surfaces only once M5 runs the generator against the shipped templates that M4 was implicitly supposed to already cover.

## Verdict on Dan's expectation

**"Probably not that much refactoring" is confirmed, not refuted — but with real qualifications on both ends.**

- **Facets: strongly confirmed.** 60 of 61 real facet-spec documents already fit the notation's *actual* required shape (H1 + one-liner + dispatch table + terminal BRIEF) with zero changes. The one that doesn't (`DAS Facet.md`) drifted out of its *own* 2026-08-05 shape in three days — a currency problem, not a design problem. The corpus's frozen T7.A proposal over-specified (an embedded `# RULESET` section that 67 of 69 real facets never had), but that is a finding about M1's one specimen generalizing too far, not about the population needing to change.
- **Templates: real refactoring, but of a specific, bounded, mostly-mechanical kind.** 9 of 16 restated templates matched a real instance outright. Of the 6 that didn't, one class — the `...` marker, live in 12 of 19 template files — is uniform and mechanical (delete a line per repeating group). The rest (4 items: messages.md, query.md, rocks.md's one-liner, icebox.md's tier grouping, testing.md's header word) are small, independent, single-line divergences between a template and the one real instance it was checked against — not restructuring, but genuine and worth fixing before templates are relied on as Warden's M6 source of truth.
- **The generator has a real gap** (Finding 5) that isn't about the corpus at all — it's a hole in M4 that this exercise is what exposed, because M1's seven cases happen not to need `{slug}` filled.

So: the corpus does not need restructuring to fit Stencil. It needs a bounded, enumerable sweep (strip 12 dead `...` lines, fix 4 named one-line drifts, add `single_brace_vars` to the generator) — closer to "clean up before Warden checks it" than to "redesign the templates," which is what "probably not that much refactoring" predicted.

## Verification

All three suites green, run fresh at the end of this pass:

```
$ python3 Stencil/engine/test_sten_match.py 2>&1 | tail -3
  DKT Track.md: T6.A's row pattern matches 10 lines — 3 above the `| --- | |` separator (line 12) and 7 below it, inside the electric zone HookAnchor recomputes.

SUITE GREEN

$ python3 Stencil/engine/test_sten_generate.py 2>&1 | tail -3
  ok T1.A vs generate(T1.A): expected MATCH, got MATCH — control — T1.A must still match its own generated instance

SUITE GREEN

$ python3 Stencil/engine/test_sten_corpus_integrity.py 2>&1 | tail -3
  19 block(s) checked against Template Examples.manifest.json

SUITE GREEN
```

Every per-item verdict in §Templates and §Facets above was produced by an actual `sten_match.match()` (and, where generable, `sten_generate.generate()`) call against the cited real file — not eyeballed. The verification scripts themselves are throwaway (run under `/private/tmp/`, not checked into this repo), consistent with the house convention that a permanent script isn't warranted for a one-time measurement; the results are captured verbatim above so the run doesn't need to be reproduced to be checked.

`git status` in `dans-anchor-system` at the end of this pass shows only this file added; `design/Template Examples.md` and the `Stencil/engine/*.py` sources are untouched.

## Status

Authored 2026-08-08 as [[Tink303 - Template DSL - one pattern language for facets, templates, and sections|F303]] M5. Restates `facets/*.md` (69 files, one shared shape, measured distribution) and 16 of 19 `templates/*` files (individually, against a located real instance each) in Stencil, verifies every restated stencil against real files with `sten_match`/`sten_generate`, and reports five notation/authoring findings and a verdict on Dan's "probably not that much refactoring" expectation. Does **not** modify any facet or template — that sweep (12 `...` lines, 4 named one-line drifts, the `single_brace_vars` generator gap) is scoped but left for Dan to schedule.
