---
description: "The on-write path: distilled per-hook script, where::-relevance-gated assert + judgment reminder, one test workflow."
---

# [[Audit]] · F003 — On-write rule hook + test workflow

## Summary

The just-in-time half of the rule system ([[F002 — Audit fix-by-default + Python rule functions|F002]] is the on-demand half). **Every time the agent writes a file**, a hook runs a **distilled, hardcoded Python script** that, given the file path + content, surfaces the rules relevant to *that* file:

- **Mechanical rules** (computable Python) — run immediately; a violation is **asserted** (flagged as an error to fix).
- **Judgment rules** (LLM must look) — their short titles are **surfaced as a reminder** so the agent self-checks against them in the moment, pulling full text only when needed.

Relevance comes from each rule's **`where::` clause** (already introduced by F161); the write-hook only ever surfaces rules whose `where::` matches the written file. For speed, the whole applicable rule corpus is **distilled into one baked Python script per hook** — rule bodies, `where::` globs, and judgment-rule titles bound as module-level lists — so a write triggers a single fast script with everything pre-computed.

Because this spans hooks, distillation, relevance, and many file kinds, the feature ships with an **extensive test strategy executed as a single workflow** — a checklist that exercises the capability across uses and reports pass/fail mechanically.

## Success Criteria

**Tier:** 1 (agent-immediate)
**Blocks next:** none

**What done looks like.** A `PostToolUse` hook on `Write`/`Edit` runs the distilled script on the written file in **milliseconds**. Writing a file that violates a mechanical rule surfaces the violation immediately; writing a recognized file kind surfaces the abbreviated judgment-rule reminders for that kind (relevance-gated, throttled); writing an unrelated file surfaces nothing. The whole behavior is verified by **one runnable test workflow** whose checklist passes.

**How it will be verified.** Run the F167 **test workflow** (the deliverable in § Testing strategy): it sets up scratch files of several kinds, performs writes, and asserts the hook output per case (mechanical violation caught; correct judgment reminders surfaced; no false reminders on non-matching files; sub-second latency; throttling honored). Green checklist = pass. Plus the M1 smoke test: a trivial hook proves `PostToolUse` fires and can inject feedback.

## Design

### Relationship to F166 / F161

- **F161** built the rule engine (resolve → run → judge), the `where::` selector, and `check::` primitives — the **on-demand `/audit`** path.
- **F166** set the direction: fix-by-default, Python rule bodies, and the rule-set design docs as the home.
- **F167 (this)** builds the **on-write** path: the distilled hook that surfaces rules at write-time. Same rule sets, same `where::`; different trigger (every write) and different posture (fast assert + reminder, not a thorough fixing pass). The two paths are complementary: the hook is the cheap in-the-moment guardrail; `/audit` is the thorough backstop.

### `where::` relevance (reuse, don't reinvent)

Rules already carry a **`where::`** clause from F161 (scope kinds `always` / `file:<glob>` / `anchor` / `sentinel:<regex>`, `{ANCHOR}` token). The write-hook reuses it verbatim to decide which rules apply to the written file — no new "scope" vocabulary. (The user may extend the rule-set facet's documentation of `where::` independently; this feature **verifies** the facet documents it and adds it if missing — see Roadmap M2.)

### Distill → one hardcoded Python script per hook

The `/distill` skill compiles the applicable rule corpus into a **single self-contained Python script per hook kind**, written to the config folder (`~/.config/ob-skills/hooks/on-write-rules.py`). Everything is **baked in** — no runtime discovery/parse:

- Module-level **lists/dicts** bound at distill time: `(where-glob → mechanical rule body)` and `(where-glob → [judgment rule titles])`.
- The script takes the written file's **path + content** (two strings), matches the path against the baked `where::` globs, runs the matching mechanical bodies, and **prints**: violation lines (mechanical) + a compact reminder block (judgment titles).
- Designed for **milliseconds**: one process, no imports beyond stdlib, no filesystem walk unless a rule asks for it.

Re-distill whenever rule sets change (the script is a derived artifact, like the F161 caches).

### The hook + what it surfaces

A **`PostToolUse` hook on `Write` | `Edit` | `NotebookEdit`** runs the distilled script against the just-written file and injects its output back to the agent:

- **Mechanical violations** — asserted as errors ("R-x violated: <detail> — fix it"). Always surfaced.
- **Judgment-rule reminders** — the **rule titles** (the free abbreviation; no new authoring) for rules whose `where::` matches, e.g. *"backlog file — review against: R-backlog-03 source-order, R-backlog-07 one-form-per-parent."* The trip-wire; the agent fetches full text only on doubt.

**Posture: advisory feedback, not a hard pre-write block.** `PostToolUse` fires *after* the write, so the agent gets immediate feedback and self-corrects — it does not gate the write. (A `PreToolUse` hard-block mode is a future option, parked with the leveled-fixing aspiration in F166.)

### Relevance + throttling (anti-fatigue)

- **Relevance-gated** — only `where::`-matching rules, always (the whole point of the clause).
- **Throttle judgment reminders** — surface a file kind's judgment reminders **once per file per session** (not on every successive edit), so the agent isn't spammed. Mechanical violations are always surfaced (they're specific and actionable).
- **Abbreviation = titles**, full body on demand.

### Rule-set facet `where::` (verify/extend)

Part of this feature: ensure the **rule-set facet** (FCT Ruleset) documents the `where::` clause (the relevance vocabulary the hook depends on). The user may do this independently; the feature **verifies it was done and adds it if not**.

## Roadmap

- **M1 — Verify the hook fires.** A trivial `PostToolUse` hook on `Write`/`Edit` proves the trigger fires reliably and can inject feedback the agent sees. De-risk the mechanism before building on it.
- **M2 — `where::` relevance.** Confirm `where::` on rules (from F161); ensure FCT Ruleset documents it; build the `path → matching-rules` resolver the distiller will bake in.
- **M3 — Distill → hardcoded per-hook script.** `/distill` compiles the doc/anchor rule corpus (mechanical bodies + `where::` globs + judgment titles) into `~/.config/ob-skills/hooks/on-write-rules.py` with the lists bound at module level.
- **M4 — On-write surfacing.** Wire the hook to run the distilled script; mechanical violations asserted, judgment reminders surfaced (relevance-gated + throttled). End-to-end on a real write.
- **M5 — Test workflow.** The extensive checklist (below) runnable as a single workflow; green = the capability works across uses.

## Testing strategy

This capability is complex enough to need its own strategy, and the test surface itself is the primary `## Success Criteria` evidence. The strategy lives (long-form) in the **rule-set / testing design docs**; the executable form is **one workflow** that runs the whole checklist and reports pass/fail.

**Test kinds + coverage:**

| Kind | What it covers | Coverage target |
| --- | --- | --- |
| Unit | the `where::` path-matcher; the distiller (corpus → baked script); each mechanical checker | Strong — every `where::` scope kind + every shipped checker |
| Integration | distilled script: path+content in → correct violations + reminders out | Strong — one case per file kind (backlog / anchor page / PRD / status / log / messages) |
| Live | a real `Write`/`Edit` in a session fires the real hook and the agent sees the output | Heavy — the load-bearing path; ≥1 per surfaced channel (violation, reminder) |
| Speed | the distilled script returns in milliseconds | Bounded — assert < ~50 ms on a representative file |
| Negative | a write to a non-matching file surfaces **nothing**; throttle suppresses repeat reminders | Strong — false-positive guard is as important as detection |

**The single workflow (the deliverable checklist).** A named workflow stands up scratch files, performs writes, and asserts per case — at minimum:

1. **Mechanical catch** — write a backlog file with a known mechanical violation → violation asserted.
2. **Mechanical clean** — write a conforming file → no violation.
3. **Judgment reminder** — write a recognized file kind → its judgment-rule titles surfaced.
4. **Relevance gate** — write an unrelated file (e.g. a scratch `.txt`) → nothing surfaced.
5. **Multi-kind sweep** — repeat 1-4 across backlog / anchor-page / PRD / status / log / messages.
6. **Throttle** — two successive edits to the same file → reminder once, not twice.
7. **Speed** — time the distilled script on each kind → all under budget.
8. **Distill freshness** — change a rule, re-distill, confirm the baked script reflects it.

The workflow tallies pass/fail across the checklist; **green = the system is verified across its uses**, runnable on demand as a single command.

## Status

**Designing** — design complete; all questions auto-resolved (see ## Resolved). Awaiting agreement to implement.

## Resolved

### `where::` reused, not a new "scope" keyword
**Choice:** Reuse F161's existing `where::` clause for relevance; do not introduce a parallel `scope::`. One selector vocabulary across `/audit` and the write-hook. Alternative ("scope") rejected — it would fork the vocabulary for no gain.

### Distill output = one hardcoded Python script per hook, in the config folder
**Choice:** `/distill` bakes the corpus into a single self-contained `~/.config/ob-skills/hooks/on-write-rules.py` with rule bodies + `where::` globs + judgment titles bound as module-level lists. Matches the user's "everything baked in, the hook loads the script, local variables bound with lists" model. Alternative (load + parse rule sets at hook time) rejected — too slow for an every-write trigger.

### Hook = PostToolUse on Write/Edit/NotebookEdit; advisory, not blocking
**Choice:** Surface as immediate feedback *after* the write (agent self-corrects), not a `PreToolUse` hard block. `PostToolUse` is the natural fit for "you just wrote X; it violates Y." A blocking `PreToolUse` mode is parked as a future option alongside F166's leveled-fixing. Alternative (block the write) rejected for v1 — too disruptive; the file-already-written + feedback loop is cheaper and matches "flag an error."

### Two channels: assert mechanical, remind judgment (titles, throttled)
**Choice:** Mechanical violations asserted every write; judgment rules surfaced as their **titles** (free abbreviation), relevance-gated by `where::` and throttled once-per-file-per-session. Full rule text fetched on demand. Alternative (dump full rule bodies every write) rejected — token cost + alert fatigue.

### Test surface = one runnable workflow
**Choice:** The extensive cross-use checklist is implemented as a single workflow that asserts each case and tallies pass/fail, so the whole system verifies in one command. This *is* the Tier-1 success evidence.
