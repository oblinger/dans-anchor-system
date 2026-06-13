---
name: audit
description: >
  Anchor auditing — verify structure, rules, documentation, code quality, publish readiness, and
  Q.md / triage consistency. Most sub-audits report findings and write a backlog entry
  (**audit never fixes** — fixing is downstream work, pulled from the backlog later). The `/audit q`
  subaction is the **exception per F076**: it fixes by default (script-vs-skill split — the underlying
  script is read-only + `--fix` flag; the skill always passes `--fix`). Use when the user says: "audit this",
  "check the structure", "are the docs current", "lint this", "check before publish", "any broken links",
  "audit Q", "run an audit". Subcommands: /audit structure, /audit dispatch (fix-by-default — build/repair
  one anchor's dispatch table), /audit rules, /audit docs, /audit publish,
  /audit code, /audit q (fix-by-default per F076), /audit q-fix (pick up a QFix backlog entry per F076).
  Add "dry" anywhere in the args to print findings without writing a backlog entry.
tools: Read, Write, Edit, Bash, Glob, Grep, Agent
user_invocable: true
---

# Audit

Skill spec for `/audit` — the anchor-auditing orchestrator and its sub-audit actions (structure, rules, docs, publish, code, q, q-fix, features, markdown, architecture, integrity, api-doc).

Audits diagnose. Most never fix. Each sub-audit produces **≥1 backlog entry** under `## Next` (default horizon — deprioritized by default; per F061 Q4) in `{NAME} Backlog.md`, **pre-split by state-cluster** of the remaining findings (one `[Ready]` row for mechanical findings, one or more `[Questions]` rows for findings needing user input). The fix work happens later, when someone pulls that backlog item — sub-bullets within a row are the natural splits if the work needs to be broken up further.

## Governing principle — `/audit q`: the agent fixes 100%

(Per user direction 2026-06-04, establishing the discipline for `/audit q` and the loop-until-clean post-condition in `/triage` + `/groom`. Replaces the prior "mechanical-only, never agent-guessed" rule and tightens the F076 three-tier flow.)

**The agent's job is to drive the audit residual to zero on every run.** Not "fix what's mechanical and catalog the rest" — *fix all of it*. Every check that audit-q surfaces has been deliberately chosen because it has an agent-side fix path; the agent's job is to take it. The cultural failure mode this rule defeats is *agent laziness disguised as discipline*: leaving warnings behind under the cover of "user input needed" when honest effort would have produced an answer. **If you find yourself reaching for QFix because "the user might prefer something different" — stop. Try harder. The user can correct a written `None — <reason>`; they can't correct silence.**

The principle has three explicit implications:

1. **`None` is a real Recommendation.** When the agent has no basis for Strong or Lean *after honest effort*, the answer is `**Recommendation:** None — <one-line reason naming what specifically the agent doesn't know>`. The user reviews None recommendations specifically — that's their actionable inbox. **Empty Recommendation is the agent declaring it didn't try.** Same shape applies to other agent-fillable fields: write the plausible-exercise sentence for `Naturally exercised by:` (or rebracket honestly); write the next-action for `[Designing]` rows (or rebracket).
2. **Every warning is somebody's work, and the auditing agent is the somebody.** Cross-anchor findings catalog to the owning anchor's backlog, but only because that's the right *routing* — the principle still applies: that owning anchor's next agent invocation drives that residual to zero too.
3. **If a check has no agent-side fix path, delete the check.** A warning the agent is "reasonable to not correct" is not a warning the audit should be surfacing — it would only train the agent to skip warnings as habit, defeating the entire discipline. Add audits only when they're agent-actionable; if a discipline boundary changes and a check stops being actionable, retire the check rather than let it accumulate as unaddressed residual.

This principle governs **`/audit q`** specifically (and any sub-audit that adopts the fix-by-default model). For sub-audits that follow the older "diagnose, write backlog entry, fix work happens later" pattern, see the next paragraph — the principle there is different.

**Exception — `/audit q`** (per F076): fixes by default because Q.md drift is mechanical and unambiguous to repair. The three-tier flow (mechanical via Python script → agent-inline-judgment → singleton `QFix` backlog entry only for the rare cases where the answer genuinely requires user-private information the agent can't reach) keeps the audit-fixes-it model contained to the Q.md surface where the cost/benefit decisively favors auto-repair. The broader principle "audit never fixes" still applies to every OTHER subaction.

## Runbook

### Single sub-audit (`/audit structure`, `/audit docs`, `/audit rules`, `/audit publish`, `/audit code`, `/audit q`, `/audit q-fix`)

1. Read the sub-skill file from this folder (it contains the full checklist inline).
2. Execute the runbook in that file. It scans, reports findings, and writes the backlog entry.
3. Print a one-line summary: `<kind>: N findings → B<n>` (or `<kind>: clean — no entry written`).

### Bare `/audit` (orchestrator — runs all applicable sub-audits)

1. Determine the anchor's traits from `.anchor` config or frontmatter; pick the sub-audits that apply (see § Which apply).
2. **Dispatch each sub-audit as a worker** (Agent tool, `subagent_type=general-purpose`). The orchestrator does *not* execute sub-audit runbooks itself — it only collects results.
   - Pass each worker: the anchor path, the sub-skill file path, and any flags (`dry`, `recheck`).
   - Each worker scans, reports, writes its own backlog entry, and reports back the B-number(s) it wrote (or "clean").
3. After all workers return, print a per-sub-audit summary line, then post one stat update:

```bash
skl-stat add "Review" "[[{NAME}]]" "Audit: <total> findings across <K> sub-audits"
```

Use `Done` + `Audit: clean` if every sub-audit returned zero findings.

## Why workers for the orchestrator

A full audit can surface hundreds of findings across sub-audits. If the orchestrator runs each sub-audit inline, its context fills up before the last sub-audit has even started. Dispatching to workers keeps each sub-audit's scratch state in its own context, and the orchestrator only sees the final summary line per worker.

## Flags

Flags can be passed as `--<flag>` or as a bare word/substring anywhere in the arguments.

- **dry / dry-run / dry run** — Match is a **substring**: anywhere the four letters `dry` appear in the args, the audit reports findings to the console but **does not write a backlog entry**. Useful for quick exploratory passes. Default behavior is to write the entry.
- **recheck / rechecked** — Ignore freshness timestamps, check everything (`docs` only).

There is no `--fix` flag. Audits never fix.

## Backlog entry format

Each sub-audit produces **≥1 backlog row**, pre-split by **state-cluster** of the remaining findings (per F061 Q4). The split is mechanical:

- **One `[Ready]` row** containing all sub-bullets that have **no open questions** — mechanical / spec-clear / no user policy needed. The agent (or `/crank`) can pick this up immediately.
- **One or more `[Questions]` rows** for sub-bullets that need user input. Each cluster of related questions gets its own row; orthogonal question-sets get separate rows so the user can resolve them independently. Each `[Questions]` row links to a feature doc (`→ [[F<n> — <Title>]]`) holding the Qs parked per `[[SKA ask]]`.
- **Done sub-bullets are excluded entirely** — they shouldn't appear in an audit-result row at all. If a finding is resolved during audit-write, drop it.

**Default horizon: `## Next`, NOT `## Now`.** Audit findings are surfaced but **deprioritized by default** — they don't compete with whatever's currently flowing through `## Now`. The user can promote to `## Now` explicitly when the audit work moves up in priority. Use `## Now` only when the audit was explicitly invoked because the user wants the findings to land in the active horizon.

**Mutation discipline — every audit row goes through `state task create`.** Direct `Edit`/`Write` against `{NAME} Backlog.md` is forbidden (per [[SKA workflow]] § Mutation API). The workflow skill's `state` mints the F-number atomically (no agent-side scan), inserts the row in the right H2, preserves source order, and auto-refreshes `~/ob/kmr/Q.md` — so § Q.md update post-condition below is satisfied as a side effect.

For each row (one per state-cluster), invoke:

```bash
~/.claude/skills/workflow/scripts/state --anchor {NAME} task create --horizon Next --status Ready \
    --title "<Kind> audit (<state-cluster>): <N> findings (<YYYY-MM-DD>)" \
    --body "work surfaced by /audit <kind>. Sub-bullets are candidate splits if this needs to be broken up."
```

Parse the assigned `F<NNN>` from stdout (`<slug>: added F<NNN> in Next [Ready]` — second word after `added`).

For `[Questions]` rows, swap `--status Ready` → `--status Questions` and put the feature-doc wiki-link in the body:

```bash
~/.claude/skills/workflow/scripts/state --anchor {NAME} task create --horizon Next --status Questions \
    --title "<Kind> audit (Questions: <cluster name>): <N> findings (<YYYY-MM-DD>)" \
    --body "→ [[F<NNN> — <Title>]]"
```

The script produces row shape:

```
- **F<NNN> — <Kind> audit (<state-cluster>): <N> findings (<YYYY-MM-DD>)** [Ready] — work surfaced by /audit <kind>. ... ^F<NNN>
```

**Sub-bullets are findings, one per line** — append them below the row via direct `Edit` against the file. (Sub-bullets are within-row content, not row-level mutations; `state` v1 handles row lines only.) Order sub-bullets by category, then by file path.

**Default horizon: `Next`, NOT `Now`** (per the deprioritization rule above). Override to `Now` only when the audit was explicitly invoked because the user wants the findings to land in the active horizon.

**No aggregate `[Partial — …]` row.** That bracket form is banned by `[[CAB Backlog]]` § Status brackets. Pre-splitting by state-cluster on creation IS the spec; never collapse mixed-state findings into a single row.

**One row-set per sub-audit run.** Each invocation of `/audit <kind>` writes its state-clustered row(s) — no merging with prior audit entries (those are stable references). If a prior entry from the same sub-audit is still un-cleared, the user can decide whether to consolidate manually.


## Q.md update post-condition — automatic via `state`

Each `state` invocation auto-regenerates the anchor's per-anchor section in `~/ob/kmr/Q.md` (by shelling out to `audit-q.py --scope backlog --anchor {NAME} --fix`). **The backlog file is NOT reordered** — source order is preserved (per F075 Q2). Bubble-to-top is a Q.md-only behavior; the user reading Q.md sees the just-audited anchor at the top with its new finding rows.

For sub-audit runs that write multiple rows in sequence, the Q.md regen fires once per row — fine for low row counts (~1-3) but redundant for large finding sweeps. When the orchestrator (bare `/audit`) collects results from many worker sub-audits writing dozens of rows, the per-call regen is unhelpful write amplification; in that case workers should be invoked with their findings collected in memory and a single final `state` call per row writes the lot, with the final Q.md state being correct on the last write.


## Actions

| Action | File | Compiled | Description |
|--------|------|----------|-------------|
| `/audit structure` | [[audit-structure]] | [[code-rewire.compiled]] | Files, dispatch tables, links, orphans |
| `/audit anchor` | [[audit-anchor]] | — | Audit one anchor against the `R-anchor` ruleset via the **F161 engine** (`audit-plan`): resolve rules → run mechanical (`--run`) → agent-judge the residue (`--judge`/`--record-verdict`). Covers `.anchor` set + anchor-page conformance ([[FCT Anchor Page]]) + dispatch table (table *repair* delegates to `/audit dispatch`). Doc-level sibling: `audit-plan <file> --mode doc`. Per [[F161 — Rule-driven audit engine — resolve, run, judge\|F161]]. |
| `/audit doc` | [[audit-doc]] | — | Audit one standalone document against the `R-doc` umbrella ([[FCT Document]]) via the **F161 engine** (`audit-plan --mode doc`): markdown hygiene + file-association / ruleset / brief / discussion / log / messages facets. Doc-mode sibling of `/audit anchor`. Per [[F161 — Rule-driven audit engine — resolve, run, judge\|F161]]. |
| `/audit dispatch` | [[audit-dispatch]] | — | **Fix-by-default** — build/repair one anchor's dispatch table (Masthead + Member zone) |
| `/audit rules` | [[audit-rules]] | — | Rule violations from `/rule check --all` |
| `/audit docs` | [[audit-docs]] | [[audit-docs.compiled]] | Module docs vs source code |
| `/audit publish` | [[audit-publish]] | — | PII, credentials, sensitive paths |
| `/audit code` | [[audit-code]] | — | Code quality: silent fallbacks, dead code, magic values (Semgrep + agent) |
| `/audit q` | [[audit-q]] | — | `~/ob/kmr/Q.md` constraints: link existence, Q-marker existence at target, banner derivation. **Fixes by default** (script-vs-skill split per F076 Q4); three-tier flow (mechanical → agent-inline-judgment → QFix backlog). Auto-wired post-condition into the 5 F075 participating skills. Per [[F076 — audit q — Q.md constraint validator with mechanical-fix mode]]. |
| `/audit q-fix` | [[audit-q-fix]] | — | Pick up a singleton `QFix [Ready]` backlog entry filed by an earlier `/audit q` run; work through its findings with agent judgment; re-run `/audit q` until QFix entry disappears (converged) or findings stall (user-input needed; ≤3-iteration cap). Per F076 Q5. |
| `/audit features` | [[audit-features]] | — | F-doc cross-linking — every F-doc in `SKA Features/` reachable from at least one bucket PRD's Feature Docs table. Per [[F083 — Cross-Linking]]. Orthogonal to `/audit q` (different invariant, different output). |
| `/audit markdown` | [[audit-markdown]] | — | Markdown hygiene — runs a rules library (bundled `skills/audit/rules-markdown/*.md` + user-space `~/.config/ob-skills/audit-markdown/rules/*.md`) against given files or `--all <dir>`. Rules-as-markdown (each rule = one `.md` file with YAML frontmatter + an embedded `python` block compiled at load). Starter rules: `trailing-whitespace`, `final-newline`, `heading-spacing`. Per [[F081 — audit markdown — markdown hygiene via MCP server]] v1 minimal (no MCP, no Stop-hook auto-register yet — invoke manually). |
| `/audit architecture` | [[audit-architecture]] | — | Architecture-doc shape + wiki-link integrity. Walks each anchor's main `<NAME> Architecture.md` + transitively reachable subsystem Arch docs; checks (R1) diagram-then-table at top, (R2) every cell of the component table that names a vault file is a wiki-link. Auto-fixes A3 wrap-in-brackets when the basename match is unambiguous. Auto-wired post-condition into `/architect` and its sub-skills (`new` / `update` / `changes` / `drift`). Per [[F092 — Audit architecture]]. |
| `/audit integrity` | [[audit-integrity]] | — | **Detect direct edits that bypassed `state`/`backlog-edit.py`.** Walks every `<NAME> Backlog.md` in the vault; compares its `mtime` against the last-script-run timestamp in `~/.config/ob-skills/backlog-edit/state.json` (per anchor). Flags any backlog whose mtime is newer than the recorded script-run as a `bypass` (agent direct-edit OR legitimate user edit — the audit can't distinguish; user filters). Anchors never touched by the script appear as `unknown`. Report-only; never writes a backlog entry of its own. |
| `/audit api-doc` | `audit-api-doc.py` | — | **CAB API Doc facet conformance check.** Validates a target API doc against [[FCT Module Doc]] rules. 26 checks: top-of-doc (frontmatter, H1, compact rule, breadcrumb), figure (embed present, SVG file exists, .excalidraw source exists), SECTIONS table (header, type-qualified rows, block-ID resolution), per-class blocks (H2 type form, description-with-block-ID, ALL-CAPS table headers, bold-identifier rows, method-link form, methods divider, block-ID matching), Class Method Details zone (H1 present, per-class H2s, block-ID-tagged method H3s), spacing (compact rule, 2-blank H2 separator, 7-blank Class Method Details separator, merged-bullet method body), dispatch linking (Dev.md + Files.md). `--fix` auto-repairs the 5 spacing checks (C3, C21, C22, C23, C24). Invoked by `/api-doc` skill during its iterate loop; can also run standalone on existing API docs. Per [[F119 — api-doc skill + audit-api-doc.py — author audit iterate for CAB API Doc facet\|F119]]. |

## Which apply

| Trait | structure | rules | docs | code | publish |
|-------|-----------|-------|------|------|---------|
| Simple | ✓ | | | | |
| Topic | ✓ | | | | ✓ |
| Code | ✓ | ✓ | ✓ | ✓ | ✓ |
| Paper | ✓ | | | | ✓ |
| Skill | ✓ | | | | ✓ |

For multi-trait anchors, run the union of all applicable checks across all traits.

`/audit` with no args → read `traits` from config, run all applicable sub-audits as workers.
