---
description: "Bracket-to-H2 placement consistency rules (C13-C18). Shipped."
bucket: drive
---

# [[Audit]] · F010 — audit-q bracket-H2 consistency rules

## Summary

audit-q.py currently checks link existence, Q-marker presence, stale `[Done]` rows, and duplicate detection (C1/C2/C4/D1). It does **not** check that bracket state matches H2 placement. The result is rot like MUX's current Q.md output, where `## Ready` H2 contains `[Watching]` and `[Blocked DMUX]` rows — items that are by definition not actionable-right-now, but appear ready to the user because the H2 says so.

The fix is to extend audit-q.py with mechanical placement-consistency rules (C13–C18). The script is already auto-wired as a post-condition into every state-touching skill (per F076 Q6), so the new rules fire automatically — no per-skill changes. Same architecture as B16 (which extends the same script with ask-format compliance rules C6–C12); F089 adds a different rule family (bracket↔H2 placement) to the same file.

The motivating example: user reads Q.md, sees MUX claims `Ready 0` but `## Ready` H2 has two rows, and asks "why are those listed under Ready when they're `[Watching]` and `[Blocked]`?" The answer is: triage faithfully renders source order from the backlog, the backlog has those rows under `## Ready` H2 because /groom hasn't been run, /groom's bracket reassessment rule exists but only fires on invocation. The script makes the check unconditional.

## Design

### Ruleset

| Rule | Check | Default action |
|---|---|---|
| **C13** | `## Ready` H2 must contain only `[Ready]` rows. Violations: any row whose bracket isn't `[Ready]`. | Per Q1 — auto-move `[Watching]/[Waiting]/[Blocked]/[Blocked F<n>]` rows to `## Later`; report-only QFix for `[Questions]` / `[Designing]` / other. |
| **C14** | `## Active` H2 must contain only `[Active]` rows. | Auto-move violating rows to the bracket-implied H2 (per C13 hybrid logic). |
| **C15** | `[Watching]` / `[Waiting]` / `[Watching Nd]` / `[Waiting Nd]` rows belong in `## Later`. | Auto-move when found in `## Now` / `## Next` / `## Active` / `## Ready`. (Subsumes the C13/C14 cases for these brackets; listed separately for the case where a non-Ready/non-Active H2 has them — e.g., `## Now` carries `[Watching]`.) |
| **C16** | `[Blocked]` / `[Blocked F<n>]` rows belong in `## Later`. | Auto-move when found anywhere else. |
| **C17** | `[Done]` / `[Done YYYY-MM-DD]` rows in any horizon H2 (`## Now` / `## Next` / `## Later`) → move to `## Done`. | Partial overlap with C4 (which catches stale Done refs); C17 catches misplaced Done rows. Auto-move. |
| **C18** | `[Verify-by YYYY-MM-DD]` rows past their date → flag for auto-Done per [[F087 — Extract ask-format as a discipline]] § Deferred-by-use Verify. | Default: auto-move to `## Done` with body note `Auto-Done <today> — [Verify-by <date>] window expired`. Mechanizes what /groom § 2a already does for the bracket-reassessment pass. |

### Implementation notes

- **Same script** — `skills/audit/scripts/audit-q.py`. Adds 6 new check functions following the existing pattern (`check_c13_ready_h2_purity`, `check_c14_active_h2_purity`, `check_c15_watching_waiting_in_later`, `check_c16_blocked_in_later`, `check_c17_done_in_horizon`, `check_c18_verify_by_expired`). Each returns a list of `Finding` records.
- **Same wiring** — already fires as a post-condition on `/triage`, `/groom`, `/mint`, `/finalize`, `/feature` per F076 Q6. No per-skill changes needed.
- **Sequential after B16** — B16 lands C6–C12 (ask-format rules); F089 lands C13–C18 (placement rules). Rule numbers stay monotonic; same script, distinct rule families.
- **Fix mode** — per Q1 hybrid: auto-fix when bracket implies an unambiguous canonical H2 (pure-state brackets); QFix entry when the bracket is ambiguous (`[Questions]` could mean either rebracket or move).
- **QFix format** — when fix-by-default can't resolve, emit a `[Ready]` row under `## Now` in the anchor's backlog with text `QFix — <rule>: <count> findings (<date>)` and one sub-bullet per finding. Same pattern as F076 Q6's existing QFix mechanism.

### How C13/C14 differ from /groom § 2a

/groom § 2a "Bracket-H2 mismatch" already says:

> a row under `## Ready` H2 with a `[Questions]` / `[Blocked]` / `[Waiting]` / `[Watching]` bracket is misplaced

The rule exists; what's missing is **unconditional mechanical enforcement**. /groom is an agent skill — runs only when invoked, costs tokens, requires body reading for the disambiguation half. C13/C14 mechanize the unambiguous half of that rule so it fires on every state-touching action, regardless of whether /groom is invoked. /groom's body-reading rebracket logic stays — it handles the cases C13/C14 can't (e.g., `[Designing]` row that should be rebracketed to `[Ready]` based on linked feature doc state).

### Anti-cases

- **Don't auto-rebracket** — F089 only moves rows between H2s based on their existing brackets. Changing a bracket itself (e.g., `[Watching]` → `[Verify]` on soak expiry) requires body-reading and stays in /groom.
- **Don't reorder within an H2** — moves are H2-to-H2 only; within-H2 source order is preserved (per F075 Q2 backlog-source-order-preserved invariant).
- **Don't touch Icebox** — `{NAME} Icebox.md` is out of scope; users explicitly park items there and the placement rules don't apply.

## Status

**Agreed 2026-05-24** — all 2 Qs resolved (Q1 hybrid C13/C14 auto-fix per option C, Q2 vault-wide scope per option A). Ready for implementation.

## Resolved

### Q1 — Auto-fix vs report-only for placement violations
**Choice:** (C) Hybrid — auto-move pure-state brackets (`[Watching]` / `[Waiting]` / `[Blocked]` / `[Blocked F<n>]`) to `## Later` mechanically; report-only QFix for ambiguous brackets (`[Questions]` could mean either rebracket-to-Ready or move-to-Later — body content disambiguates, agent territory).

Pure-state brackets have unambiguous canonical homes (`## Later`). Ambiguous brackets need body-reading judgment that /groom already does. Hybrid puts the mechanical part in the script and leaves judgment in /groom. (A) auto-fix-all would surprise the user on ambiguous cases; (B) report-only would leave easy wins unfixed. Incorporated into Design § Ruleset (C13/C14 default-action column) and § How C13/C14 differ from /groom § 2a.

### Q2 — Vault scope — all-anchors default
**Choice:** (A) Vault-wide scan by default — no `--project` flag needed.

User principle: "Obsidian is vault-scope, so we want to be all vault scope." Applies to **every** audit-q rule, not just F089's additions. The script's job is to catch drift wherever it surfaces — the smoking-gun evidence (MUX's `## Ready` H2 with `[Watching]`+`[Blocked DMUX]` rows) only got caught because of vault-wide visibility; a current-anchor scan would have stayed blind. Auto-wired post-condition (F076 Q6) runs on the local anchor's state-touching action, but the script itself walks the whole vault — same as existing C1/C2/C4 behavior. No new `--project` flag.

### Rule numbering — C13–C18 after B16's C6–C12
**Choice:** F089 takes rule numbers C13–C18, sequential after B16's C6–C12.

audit-q.py uses a monotonic rule-number namespace (C1, C2, C4, D1 existing; C6–C12 reserved for B16). F089 picks up at C13. Skipping C3 / C5 is intentional — those numbers are reserved or were dropped during prior design; the namespace is monotonic-forever like F-numbers. Same script-level convention as existing rules.

### Same file as B16, not a new script
**Choice:** F089 extends `skills/audit/scripts/audit-q.py` rather than creating a new script.

audit-q.py is already the right tool (vault-index + link primitives + auto-wired post-condition + fix-by-default mode). Different rule family doesn't justify a new script — same architecture, same call sites, same wiring. The split between B16's ask-format rules and F089's placement rules is a logical grouping inside the script, not a separate executable.

### Title — "audit-q bracket-H2 consistency rules"
**Choice:** Filename uses ASCII dash, not the `↔` arrow.

The arrow is filesystem-friendly on macOS but renders poorly in some terminals + makes grep harder. Body text uses `↔` freely; filename uses `-`.
