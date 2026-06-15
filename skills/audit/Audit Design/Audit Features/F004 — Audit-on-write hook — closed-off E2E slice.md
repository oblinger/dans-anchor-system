---
description: "First buildable slice: PostToolUse hook auto-fixes mechanical findings, messages subjective ones. Shipped."
---

# [[Audit]] · F004 — Audit-on-write hook — closed-off E2E slice

## Summary

A small, **closed-off, independently-testable** slice of [[F002 — Audit fix-by-default + Python rule functions|F002]]: stand up the **write-hook** end of document auditing and prove it works both ways. On every `.md` write the hook runs the document audit and does two things — **auto-fixes the mechanical findings in place** (the deterministic ones) and **messages the agent** about the subjective ones (the judgment ones it must not silently rewrite). Correctness of the *rules themselves* is out of scope (tested elsewhere); this feature verifies the **plumbing** — that an introduced fault is either silently repaired or surfaced to the agent, every write.

F166 remains the design home for the broader system (fix-by-default `/audit`, leveled fixing, Python rule-functions, `/distill` fast-path, the PRD/Architecture/API doc set). F177 builds only the minimum needed to exercise the two write-hook paths end-to-end.

## Success Criteria

**Tier:** 1 (agent-immediate)
**Blocks next:** none

**What done looks like.** A PostToolUse hook on `Write`/`Edit` is installed. Writing a `.md` file with a **mechanical** fault (e.g. a malformed breadcrumb / missing blank line around a table) causes the file on disk to be **auto-corrected** without agent involvement. Writing a `.md` file with a **subjective** fault (e.g. a first sentence that doesn't state the doc's essence) leaves the file unchanged but surfaces an **agent-visible message** naming the finding. A single integration test drives both and reports PASS/FAIL mechanically.

**How it will be verified.** `bash <repo>/skills/audit/scripts/test-audit-on-write.sh` (or a `just` recipe) — the harness writes the two broken fixtures through the hook path, then asserts: (1) the mechanical fixture's on-disk content now matches the repaired form; (2) the subjective fixture is byte-unchanged AND the hook emitted the expected agent-message marker. Exit 0 on both-pass. Fixtures + scratch run under `~/ob/kmr/Topic/Misc/Test/F177/`.

## Design

### Relationship to F166 — design-by-reference, no re-litigation

F166 already resolved the mechanism: the write-hook is **PostToolUse on Write/Edit** (F166 Q3); rule checks are `(path, content)` → stdout violations (F166 Q1); embedded or separated rule bodies (F166 Q2). F177 inherits all of that. The **one extension** F177 adds — and it's exactly what the user asked for — is that the hook does not merely *flag*: for the deterministic findings it **applies the `fix::` repair in place** (F166 Thrust-1's fix mechanism, run from the hook instead of only from on-demand `/audit`). Mechanical → fix silently; subjective → message, never auto-rewrite.

### The two paths

| Path | Finding kind | Hook action | Why |
|---|---|---|---|
| **Auto-fix** | mechanical (`checked` rule with a `fix::`) | repair the file on disk, silently | deterministic; no judgment; matches the existing maintain-hook breadcrumb-fix precedent |
| **Message** | subjective (`stated`/judgment rule) | leave file untouched; emit an agent-visible finding | the fix needs judgment — the agent (or user) must decide; silent rewrite of prose is the thing we must *not* do (per the no-delete / preserve-content audit discipline) |

A single audit run over the just-written file produces both buckets; the hook applies bucket 1 and reports bucket 2.

### Engine the hook calls

For this slice the hook invokes the **F161 engine directly** on the written file — `audit-plan.py --mode doc` extended with a fix step (run the `checked` rules, apply each failed rule's `fix::`, re-run to confirm; collect the `stated` residue as messages). This is the simplest path that proves both buckets with the fewest moving parts. F166's `/distill`-merged precompiled module (the millisecond fast-path) is the **production** answer for always-on use and stays in F166 — F177 deliberately does **not** build distill; it accepts a heavier synchronous run because the goal is "the plumbing works," not "it's fast." (The hook's innards can later be swapped from engine-direct to distilled without changing its contract.)

### How the agent sees a message

PostToolUse runs after the write lands. The hook returns the subjective findings through the PostToolUse hook's **agent-visible output channel** (JSON `hookSpecificOutput.additionalContext`, falling back to exit-2 + stderr if needed) so the finding appears in the agent's next turn — the same "pending message surfaces to the agent" shape the existing `maintain-hook` uses, but synchronous to the write rather than deferred to the next Read.

### Minimum fixers

The slice needs at least **one** `fix::` repair wired into `audit-plan` — whichever the mechanical fixture exercises (a safe, obviously-deterministic one: blank-line-around-table, or breadcrumb normalization). Building the general `fix::` framework across all rules is F166; F177 needs only enough to make the mechanical fixture converge.

### Test fixtures + harness (per the "write an automated test" rule)

- **`fix-me.md`** — a doc with a purely mechanical fault (e.g. a table with no surrounding blank line, or a denormalized breadcrumb). Expected: hook rewrites it to the correct form.
- **`flag-me.md`** — a well-formed doc whose **first sentence fails to state the essence** (R-anchor-page-06 / a `stated` rule). Expected: file unchanged; hook emits the finding.
- **`test-audit-on-write.sh`** — drives each fixture through the hook code path (invoking the hook with a synthesized PostToolUse payload, or calling the hook's core function directly), then asserts on-disk content + captured message. Mechanical PASS/FAIL, exit code. Lives in `skills/audit/scripts/`; fixtures + scratch copies under `~/ob/kmr/Topic/Misc/Test/F177/`.

### Scope

**In:** the PostToolUse Write/Edit hook; engine-direct doc audit with one+ `fix::`; the auto-fix-vs-message split; two fixtures; one integration test; `settings.json` wiring.

**Out (→ F166):** `/distill` + precompiled module + millisecond fast-path; the general `fix::` library across all rules; leveled/per-anchor fix aggressiveness; the rule-set PRD/Architecture/API docs; making `/audit` fix-by-default on-demand; exhaustive rule-correctness testing.

## Status

**Done** (2026-06-14) — implemented and verified end-to-end. Shipped: `audit-plan` gained a `fix::` rule field + `FIXERS` registry + `--on-write` driver (auto-fix mechanical fails with a fixer; message the fails without one); `audit-on-write.sh` PostToolUse hook (fast bash prefilter → opt-in roots → engine → PostToolUse `additionalContext` messages); R-markdown-02 annotated `check::`+`fix:: md_table_blank_lines` (auto-fix path), R-markdown-11 annotated `check:: md_fence_no_markdown`, no fixer (message path); two fixtures + `test-audit-on-write.sh` (**3/3 PASS** — auto-fix repairs the table, judgment fault stays byte-unchanged + emits the agent message); `settings.json` wired `Write|Edit|MultiEdit` → the hook, kept **inert for normal work** via the opt-in roots file (`~/.config/ob-skills/audit-on-write-roots`, currently the F177 test dir only). No regression: `facet-check` 10/10, existing `--run` clean. Broader F166 pieces (`/distill` fast-path, general `fix::` library, leveled fixing, the rule-set design docs) remain in F166.

## Resolved

### Engine-direct, not distilled, for this slice
**Choice:** the hook calls `audit-plan --mode doc` (run + fix) directly on the written file. The `/distill` precompiled fast-path is F166 production work, deferred. Reversible — the hook contract is unchanged if the innards are swapped later. Accepts a heavier synchronous run because F177's goal is plumbing-correctness, not latency.

### Hook auto-fixes mechanical in place; never auto-rewrites subjective
**Choice:** the write-hook mutates the file for deterministic findings (extending F166's flag-only write-hook per the user's explicit "fix the document" ask) but only *messages* for judgment findings — silent prose rewrite is forbidden (consistent with the audit fix discipline: move/simplify, never delete/rewrite whole chunks without review). Precedent: the existing `maintain-hook` already silently fixes breadcrumbs on Read.

### Test artifacts under the vault, not /tmp
**Choice:** fixtures + scratch runs live at `~/ob/kmr/Topic/Misc/Test/F177/` so they're browsable in Obsidian (per the smoke-tests-in-vault discipline). The harness script lives with the audit scripts in the repo.

### Closed-off slice, not folded into F166
**Choice:** F177 is a separate, independently-testable feature (the user explicitly asked for a "closed off feature … to really test both of these ways"), cross-referencing F166 as the design parent so the mechanism design stays single-sourced. F166 keeps the broad design + remaining thrusts.
