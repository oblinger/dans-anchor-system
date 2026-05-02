---
description: Product requirements for the /ask skill — durable user story + design rationale, colocated with SKILL.md so future revisions of the skill have the context the agent needs to maintain it.
---

# /Ask — PRD

This document is the **durable user story** for `/ask`. It lives next to `SKILL.md` so future revisions of the skill — by the user, by Claude, or by an audit — have the rationale on hand. The original design journey (open questions, options considered, what was rejected) lives in `SKA Plan/Features/F10 — Ask Skill.md`; this file is the steady-state PRD.

(Per F10 Q on documentation: F-numbered design doc captures the *journey*; this PRD captures the *durable user-story + design*. Optional pattern, not mandatory; warranted for skills with genuine user-facing complexity. `/ask` qualifies.)


## User story

The user is the Pilot — a senior engineer multitasking across many Claude Code agents in many anchors. Each agent has its own backlog, its own questions, its own design context. At any given moment, several agents may have queued questions waiting on the user.

Without `/ask`:
- The user has to **remember** which agents have open questions.
- The user has to **visit each anchor's** `{NAME} Triage.md` to see what's pending.
- The user has to **hope** each agent actually glanced the file when it parked questions (often forgotten — this is what F10 originally existed to fix).

With `/ask`:
- **One global page** (`~/ob/kmr/Q.md`, vault root) lists every anchor with active questions, click-throughs to per-project triage, and any vault-scoped à la carte questions.
- **A keyboard shortcut** (user-side) opens the global page in one keypress.
- **Automatic maintenance**: when an anchor has zero active questions, it disappears from the global page; when it gains questions, it reappears. The user doesn't tend the page.
- **Universal asking pattern**: any agent in any anchor that wants to ask the user something invokes `/ask`. The user gets uniform formatting, reliable glancing (in active mode), and the global page stays truthful.

The result: at any moment, opening `Q.md` (one keystroke) shows the user every active question across every agent. No remembering, no per-agent visits. When a project's questions are answered, it falls off the page.


## Design rationale

### Why a skill, not a discipline

F10 originally framed the problem as "the `ask-questions` discipline says to glance the file after parking questions; agents miss this step; how do we make it reliable?" Four mitigation options were considered:

- **(A) Operating-constants bullet** — bloat the per-turn reload with another rule. Rejected: reload is already saturated; another bullet won't be more enforceable than the existing ones.
- **(B) Wire-into-each-citing-skill** — every skill that cites `[[ask-questions]]` adds an inline "remember to glance" step. Rejected: not structurally enforced; same drift problem.
- **(C) settings.json hook** — fire `open` on certain edit patterns. Rejected: mechanical, ignores active/parking distinction, false-positives common.
- **(D) Self-check rule** — agent self-audits at end of turn. Rejected: can't be enforced from inside the agent's own turn.

User pivot 2026-04-30: **convert the discipline into an invokable skill**. When a parent skill calls `/ask` via the Skill tool, Claude Code loads `ask/SKILL.md` and executes the runbook — including the glance step. Reliability comes from the skill-tool invocation mechanic, structurally. There's no "agent might forget"; the runbook fires when invoked, period.

This is structurally tighter than any of A–D and reframes the problem. Disciplines describe *what to think* (state semantics, structural rules) — referenced when needed. `ask-questions` is fundamentally an *action* — write text, format, glance — and that action is what was unreliable. Promoting it to a skill matches its nature.

### Why the global page

User reported pain: they multitask across many agents/anchors and per-anchor triage views are insufficient. They open SKA Triage, then HA Triage, then MUX Triage, trying to remember which has new questions. They want one page.

The page needs to:
- **Aggregate across the vault** — every anchor with pending questions appears.
- **Be agent-owned** — the user shouldn't tend it; agents keep it truthful.
- **Be one keystroke away** — bound to a user-side keyboard shortcut.
- **Drop empty anchors** — when an anchor has zero pending Qs, it disappears.
- **Hold à la carte items** — cross-cutting questions that don't belong to any anchor.

The page is a **generated view**, like `{NAME} Triage.md` is for an anchor. The user reads it; they don't edit it. Edits would be overwritten by the next `/ask` call.

### Why `~/ob/kmr/Q.md`

| Candidate | Verdict | Reason |
|---|---|---|
| `~/ob/kmr/Q.md` (vault root) | **Chosen** | Page is global across every anchor in the vault. Owning it at the root reflects that scope. Wiki-link `[[Q]]` resolves from anywhere. |
| `~/ob/kmr/SYS/Bespoke/Skill Agent/Q.md` (inside SKA) | rejected | Implicitly scopes to SKA; would awkwardly contain references to peer anchors (HA, MUX, DKT) that SKA shouldn't "own." |
| `skills/ask/Q.md` (inside skill folder) | rejected | The `skills/` tree is synced to the public `obs-tradecraft` repo. The user's actual personal-project open questions would leak into a public sync. Plus skills are portable; `Q.md` is vault-specific and shouldn't ship with the skill code. |
| `~/Q.md` (home dir) | rejected | Outside the Obsidian vault; wouldn't appear in vault search or wiki-link resolution. |

The filename `Q.md` was chosen for keystroke economy: `[[Q]]` is one character. The page is so frequently referenced that brevity matters more than self-documentation in this one case.

### Why two question shapes

Originally `ask-questions` only described doc-attached questions (`## Open Questions` H2 below the H1 of a feature/PRD doc). But many agent-raised questions don't belong to a doc — they're cross-cutting ("should we adopt M-numbers across anchors?"), planning-time ("what's the next thing you want to work on?"), or backlog-routing ("which horizon for this?"). Forcing all questions onto a doc would mean creating throwaway docs for each cross-cutting question.

So `/ask` supports two shapes:

- **`--doc <path>`** — document-attached. Question lives in the doc's `## Open Questions` block.
- **(default — no flag)** — à la carte. Question lives in the project's `{NAME} Triage.md` § `## À la carte`.

À la carte questions use `A<n>` numbering (vs `Q<n>` for doc-scoped) to disambiguate when the user references them.

### Why active vs parking mode

The glance step (open the file at the user) is meaningful **only when the user expects to engage now**. If the user said "put it on the backlog" and then the agent opens a feature doc at them, that's user-hostile — the user explicitly deferred and the agent overrode that.

Active mode signals: "let's design X" / "let's discuss" / `/feature` invoked without deferral language.

Parking mode signals: "put it on the backlog" / "for later" / batch operations like `/groom` / "we'll figure that out."

**Default when ambiguous: parking.** Cost of unwanted glance > cost of missed glance, since the user can re-engage by opening `Q.md`.


## Lifecycle of an `/ask` call

1. Parent skill (e.g., `/feature` mid-design) detects it has decisions for the user.
2. Parent calls `/ask` via the Skill tool, passing the questions in batch + (optionally) `--doc <path>`.
3. `/ask` numbers them (`Q1..Qn` or `A1..An`), formats per the spec, writes to the target surface, updates `Q.md`, and (if active mode) glances.
4. User sees the file (or opens `Q.md` later in parking mode), answers via shorthand to the parent skill or via the standard answer pattern (`F5 Q4: yes`).
5. Parent skill (or `/triage`) acts on the answers — moves Qs to `### Resolved`, updates the design, recomputes counts, refreshes `Q.md` if a count crossed 0.


## Maintenance constraints

- **Never edit `Q.md` by hand.** The next `/ask` overwrites the body. Update the underlying triage or feature doc instead.
- **Q-numbers are stable.** Once assigned, never renumber. Skipped numbers are fine.
- **Resolutions don't trigger a glance.** The user already saw the pending question; reopening at them on resolution is noise.
- **Two surfaces are agent-owned: the doc's `## Open Questions` H2 + `Q.md`.** User edits would conflict with regeneration.
- **Citations across other skills name `/ask` as the action**, not `[[ask-questions]]` (the old discipline reference). When updating the skill set, sweep citations.


## Out of scope (explicitly)

- **Non-question parking** — `/ask` is for *questions* only. Parking other state (notes, partial designs, todo items) goes through `/groom`, `/triage`, or feature docs directly.
- **Answering questions on the user's behalf** — `/ask` writes; it doesn't answer. The user (or, in autonomous-loop mode, an explicitly delegated agent) answers.
- **Cross-vault federation** — `Q.md` is vault-scoped. Multiple vaults would need their own. Out of scope for v1.


## Cross-references

- `SKILL.md` (this folder) — the runbook the agent executes.
- `~/ob/kmr/Q.md` — the global page maintained by step 4 of the runbook.
- `[[CAB Triage]]` — sibling skill that surfaces (reads) what `/ask` writes.
- `[[CAB Backlog]]` § Numbering policy — same lowest-unused-integer rule.
- `SKA Plan/Features/F10 — Ask Skill.md` — design journey + Resolved Qs.
