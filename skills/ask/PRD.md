---
description: Product requirements for the /ask skill — durable user story + design rationale, colocated with SKILL.md so future revisions of the skill have the context the agent needs to maintain it.
---

# /Ask — PRD

This document is the **durable user story** for `/ask`. It lives next to `SKILL.md` so future revisions of the skill have the rationale on hand. The design journey lives in `SKA Plan/Features/F10 — Ask Skill.md` (initial mint) and `F25 — Q.md as Agent Status Dashboard.md` (the reframe to Agent Status); this file is the steady-state PRD.


## User story

The user is the Pilot — a senior engineer multitasking across many Claude Code agents in many anchors. Each agent has its own backlog, its own questions, its own ready work, its own design context. At any given moment, several agents may have queued questions waiting on the user *or* ready backlog items waiting to be picked up.

Without `/ask`:
- The user has to **remember** which agents have open questions or queued work.
- The user has to **visit each anchor's** `{NAME} Triage.md` to see what's pending.
- The user has to **hope** each agent actually glanced the file when it parked questions (often forgotten — what F10 originally existed to fix).

With `/ask` (and its companion `/triage`, plus `/crank`'s no-action chain):
- **One vault-level page** (`~/ob/kmr/Q.md`, the **Agent Status dashboard**) lists every active anchor with an H2 entry showing pending questions and/or ready item counts.
- **A keyboard shortcut** opens the page in one keypress.
- **Always-move-to-front semantics**: every `/ask` or `/triage` invocation against an anchor floats its H2 to the top of `Q.md`, so the most-recently-touched agent is most visible — even after a long absence.
- **Automatic maintenance**: anchors disappear from `Q.md` when both questions = 0 AND ready = 0. Both `/ask` and `/triage` regenerate `{NAME} Triage.md` AND the anchor's H2 in `Q.md` on every invocation.
- **Universal asking pattern**: any agent that wants to ask the user something invokes `/ask`. The user gets uniform formatting, reliable glancing (in active mode), and a fresh dashboard.

The result: opening `Q.md` (one keystroke) shows the user every active agent — what's queued for input, what's queued for execution, ordered by most-recently-touched. No remembering, no per-agent visits. When everything is drained, the agent disappears.


## Design rationale

### Why a skill, not a discipline

F10 originally framed the problem as "the `ask-questions` discipline says to glance the file after parking questions; agents miss this step; how do we make it reliable?" Four mitigation options were considered:

- **(A) Operating-constants bullet** — bloat the per-turn reload with another rule. Rejected: reload is already saturated; another bullet won't be more enforceable than the existing ones.
- **(B) Wire-into-each-citing-skill** — every skill that cites `[[ask-questions]]` adds an inline "remember to glance" step. Rejected: not structurally enforced; same drift problem.
- **(C) settings.json hook** — fire `open` on certain edit patterns. Rejected: mechanical, ignores active/parking distinction, false-positives common.
- **(D) Self-check rule** — agent self-audits at end of turn. Rejected: can't be enforced from inside the agent's own turn.

User pivot 2026-04-30: **convert the discipline into an invokable skill**. When a parent skill calls `/ask` via the Skill tool, Claude Code loads `ask/SKILL.md` and executes the runbook — including the glance step. Reliability comes from the skill-tool invocation mechanic, structurally. There's no "agent might forget"; the runbook fires when invoked, period.

This is structurally tighter than any of A–D and reframes the problem. Disciplines describe *what to think* (state semantics, structural rules) — referenced when needed. `ask-questions` is fundamentally an *action* — write text, format, glance — and that action is what was unreliable. Promoting it to a skill matches its nature.

### Why the Agent Status dashboard

User reported pain: they multitask across many agents/anchors and per-anchor triage views are insufficient. They open SKA Triage, then HA Triage, then MUX Triage, trying to remember which agents have something for them. They want one page.

The page needs to:
- **Aggregate across the vault** — every active anchor (questions OR ready work) appears.
- **Be agent-owned** — the user shouldn't tend it; `/ask` + `/triage` keep it truthful.
- **Be one keystroke away** — bound to a user-side keyboard shortcut.
- **Drop fully-drained anchors** — when an anchor has zero questions AND zero ready items, it disappears.
- **Show questions and ready** — not just questions. Per F25, the page is a *status* view, not just a *question inbox*.
- **Move-to-front on touch** — when an agent is touched (by `/ask`, `/triage`, or `/crank`'s no-action chain), its H2 floats to the top — so an agent the user hasn't engaged in a week is visible-and-near-top whenever they re-engage.

The page is a **generated view**. The user reads it; they don't edit it. Edits get overwritten by the next `/ask` or `/triage` call.

Per F25, every H2 starts with the dominant state (`QUESTIONS` or `READY` in ALL CAPS), then slug, then wiki-links + count summary. Body for QUESTIONS-prefixed entries: `### F<n>` H3 per feature with condensed-inline Q bullets (12-line soft cap). Body for READY-prefixed entries: empty (the H2 line is the entry).

### Why `~/ob/kmr/Q.md`

| Candidate | Verdict | Reason |
|---|---|---|
| `~/ob/kmr/Q.md` (vault root) | **Chosen** | Page is global across every anchor in the vault. Owning it at the root reflects that scope. Wiki-link `[[Q]]` resolves from anywhere. |
| `~/ob/kmr/SYS/Bespoke/Skill Agent/Q.md` (inside SKA) | rejected | Implicitly scopes to SKA; would awkwardly contain references to peer anchors (HA, MUX, DKT) that SKA shouldn't "own." |
| `skills/ask/Q.md` (inside skill folder) | rejected | The `skills/` tree is synced to the public `ob-skills` repo. The user's actual personal-project open questions would leak into a public sync. Plus skills are portable; `Q.md` is vault-specific and shouldn't ship with the skill code. |
| `~/Q.md` (home dir) | rejected | Outside the Obsidian vault; wouldn't appear in vault search or wiki-link resolution. |

The filename `Q.md` was chosen for keystroke economy: `[[Q]]` is one character. The page is so frequently referenced that brevity matters more than self-documentation in this one case.

### Why two question shapes

Originally `ask-questions` only described doc-attached questions (`## Open Questions` H2 below the H1 of a feature/PRD doc). But many agent-raised questions don't belong to a doc — they're anchor-level ("should we rename this slug?"), cross-cutting ("which horizon for this?"), or planning-time ("what's the next thing you want to work on?"). Forcing all questions onto a doc would mean creating throwaway docs for each.

So `/ask` supports two shapes:

- **`--doc <path>`** — document-attached. Question lives in the doc's `## Open Questions` block.
- **(default — no flag)** — anchor-level. Question is authored directly in the anchor's `{NAME} ask.md § ## Questions`. There is no separate questions file.

Both shapes use **`Q<n>` numbering**, scoped per-container — each feature doc has its own Q-namespace; the anchor's `{NAME} ask.md` has its own Q-namespace. (Per F025 Q5: dropped the earlier `A<n>` naming because the audio "A1" sounds like "ate one" — same prefix is cleaner; the per-container scoping handles disambiguation.)

Reference shorthand:
- Feature-scoped → `F010 Q3`.
- Anchor-level → `{NAME} Q3` (e.g., "SKA Q3").

### Why active vs parking mode

The glance step (open the file at the user) is meaningful **only when the user expects to engage now**. If the user said "put it on the backlog" and then the agent opens a feature doc at them, that's user-hostile — the user explicitly deferred and the agent overrode that.

Active mode signals: "let's design X" / "let's discuss" / `/feature` invoked without deferral language.

Parking mode signals: "put it on the backlog" / "for later" / batch operations like `/groom` / "we'll figure that out."

**Default when ambiguous: parking.** Cost of unwanted glance > cost of missed glance, since the user can re-engage by opening `Q.md`.


## Lifecycle of an `/ask` call

1. Parent skill (e.g., `/feature` mid-design) detects it has decisions for the user.
2. Parent calls `/ask` via the Skill tool, passing the questions in batch + (optionally) `--doc <path>`.
3. `/ask` numbers them (`Q1..Qn`), formats per the spec, writes to the target surface (feature doc's `## Open Questions` or the anchor's `{NAME} ask.md § ## Questions`), regenerates the anchor's H2 in `Q.md` (per F25), and (if active mode) glances the target.
4. User sees the file (or opens `Q.md` later in parking mode), answers via shorthand to the parent skill or via the standard answer pattern (`F005 Q4: yes`).
5. Parent skill (or `/triage`) acts on the answers — moves Qs to `### Resolved`, updates the design, regenerates `Q.md` (next `/ask` or `/triage` invocation will refresh; `/crank` no-action chain handles the case where neither runs explicitly).


## Maintenance constraints

- **Never edit `Q.md` by hand.** The next `/ask` or `/triage` overwrites the relevant H2. Update the underlying triage or feature doc instead.
- **Q-numbers are stable.** Once assigned, never renumber. Skipped numbers are fine.
- **Resolutions don't trigger a glance.** The user already saw the pending question; reopening at them on resolution is noise.
- **Three agent-owned surfaces**: the doc's `## Open Questions` H2 (when `--doc`), `{NAME} Triage.md` (always — both `/ask` and `/triage` regenerate it), and `Q.md` (always — both regenerate the anchor's H2). User edits in any of these get overwritten on next regen.
- **Citations across other skills name `/ask` as the action**, not `[[ask-questions]]` (the old discipline reference). When updating the skill set, sweep citations.
- **Stale-during-mint is acceptable.** `/crank` minting an item to `[Verify]` or `[Done]` does *not* refresh `Q.md` or `{NAME} Triage.md`. The next `/ask` or `/triage` makes them fresh; `/crank`'s no-action chain (which runs `/triage`) is a guaranteed regen point. Mint-time refresh was explicitly considered and rejected (F25 design discussion).


## Out of scope (explicitly)

- **Non-question parking** — `/ask` is for *questions* only. Parking other state (notes, partial designs, todo items) goes through `/groom`, `/triage`, or feature docs directly.
- **Answering questions on the user's behalf** — `/ask` writes; it doesn't answer. The user (or, in autonomous-loop mode, an explicitly delegated agent) answers.
- **Cross-vault federation** — `Q.md` is vault-scoped. Multiple vaults would need their own. Out of scope for v1.


## Cross-references

- `SKILL.md` (this folder) — the runbook the agent executes.
- `~/ob/kmr/Q.md` — the global page maintained by step 4 of the runbook.
- `[[FCT Triage]]` — sibling skill that surfaces (reads) what `/ask` writes.
- `[[CAB Backlog]]` § Numbering policy — same lowest-unused-integer rule.
- `SKA Plan/Features/F10 — Ask Skill.md` — design journey + Resolved Qs.

# BRIEF

- **This file is the durable PRD for `/ask`.** It carries the steady-state user story + design rationale that future revisions of the skill need; SKILL.md is the runbook, this is the *why*. Read before restructuring the skill or arguing about its scope.
- **Not for runbook steps or invocation syntax.** Those live in `SKILL.md`. If a change is to *how the agent executes /ask*, edit SKILL.md; if a change is to *why /ask exists in this shape*, edit here.
- **Not for active design churn.** In-flight Qs / decisions / journey-of-thought live in the feature docs (`F10 — Ask Skill.md`, `F25 — Q.md as Agent Status Dashboard.md`). Only *resolved, durable* rationale graduates into this PRD.
- **Inclusion test for a section here**: would a future maintainer revising `/ask` want this context to make a sensible call? If yes, it belongs. If it's a transient implementation note or unresolved debate, it does not.
- **Update the rationale together with the skill.** When SKILL.md changes the surface (new flag, new file location, new mode), update the matching § Design rationale / § Lifecycle / § Maintenance constraints subsection here so the PRD doesn't drift into folklore.
- **Naming conventions are load-bearing.** `Q.md` at vault root, `Q<n>` numbering (not `A<n>`), `{NAME} ask.md § ## Questions` for anchor-level Qs — these names are cited by SKILL.md, by `/triage`, and by `/crank`'s no-action chain. Do not rename in this file without sweeping all citations.
- **Cross-references at the bottom are the contract.** When a sibling skill or surface is added/removed/renamed, update § Cross-references — readers use it to navigate the constellation.
