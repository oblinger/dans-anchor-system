---
name: workflow
description: Discipline that owns the canonical state graph for a unit of work — state names, transitions, Definition of Ready, and per-surface mappings (Backlog, Roadmap, Feature lifecycle, PRD). Cited from CAB Backlog, feature/SKILL.md, /groom, /mint, /finalize, and other skills that advance work through states.
user_invocable: false
---

# Workflow Discipline

The single source of truth for **what state a unit of work is in**, **what it means**, and **what advances it to the next state**. Every skill that touches the state of work — `/groom`, `/feature`, `/mint`, `/finalize`, `/code release`, `/roster`, audits — cites this discipline.

> **F129 (2026-06-07):** state mutations now go through `~/.claude/skills/workflow/scripts/state` (verb-first CLI). Old positional `backlog-edit.py` invocations still work during the migration window; new code should prefer `state task <verb>` / `state q <verb>`. Full CLI spec: [[SKL State]] (`~/.claude/skills/workflow/SKL State.md`). Examples below this banner still reference `backlog-edit.py` and will be migrated incrementally.

## Why this exists — the problem it solves

The same vocabulary appears across many surfaces: backlog items have a status, feature docs have a Status field, roadmap milestones have progress, PRDs have a draft/approved cycle. **The labels diverge subtly** — "Agreed" in feature lifecycle is roughly "Ready" in backlog; "Done" in features is "Completed" in backlog; "Active" appears in both but with slightly different gates. Skills that touch state pick whichever label was nearest at hand.

The drift compounds: a new skill writes its own state names; the user can't tell at a glance whether `Designing` and `Proposed` are the same thing or different; the Definition of Ready lives in CAB Backlog but is implicitly assumed by skills that don't cite it.

This discipline collapses that to **one state graph** with **one Definition of Ready** that every surface and every skill references. Surfaces (backlog, roadmap, feature, PRD) get a short mapping section saying "here's how the canonical states appear here" — they don't redefine the graph.

## The canonical state graph

A unit of work moves through these states. Each state has a **square-bracket label** that appears in bullet form (extending the markdown checkbox idiom) and a **canonical name**.

| Label | Canonical name | Meaning |
|---|---|---|
| `[ ]` | **Unset** | Idea captured, no progress yet. Default for new items. |
| `[Designing]` | **Designing** | Being thought through. Design work in flight; spec not yet locked. No questions raised yet. |
| `[Questions]` | **Questions** | Blocked on user input on open questions. **Must** be paired with a `→ [[Feature Doc]]` link to where the `## Open Questions` block lives. |
| `[Blocked]` | **Blocked** | Blocked on something other than user questions — a dependency, an external review, a CI / build issue, missing diagnostic evidence, or any other non-question blocker. Body of the row should describe what's blocking. |
| `[Blocked F<NNN>]` | **Blocked on a feature** | Parameterized form of `[Blocked]`. The blocker is another feature's progression — click `F<NNN>` to see its current state (typically `[Verify]`, `[Active]`, or `[Designing]`). The chained reference IS the blocker description; body need not repeat it. |
| `[Waiting]` / `[Waiting Nd]` / `[Waiting Nh]` | **Waiting** | **Body MUST say what we're waiting on.** Not actively blocked — no actor's action would unblock it; just letting time pass or observing for an external event (bug to reoccur, log file to fill, user to exercise the feature, GPU run to finish). Distinct from `[Blocked]`: Blocked has a fixable obstacle; Waiting does not. For timed forms (`Nd`, `Nh`), the body must **additionally** give the absolute calendar date/time the wait expires — relative durations age and "1d" is meaningless without knowing when it was written. Soft, not hard: `[Waiting 1d]` means "give it at least a day, re-check at next triage," not "exactly 1 day then act." |
| `[Watching]` / `[Watching Nd]` / `[Watching Nh]` | **Watching** | **Soak — we may have fixed it; observing for recurrence.** Body MUST say (1) what was changed that's under observation and (2) what *non*-recurrence would prove. Distinct from `[Waiting]` by **resolution polarity**: Watching resolves when the watched event *doesn't* occur (no recurrence by expiry → fix held → `[Verify]`); Waiting resolves when the watched event *does* occur (e.g. bug recurs → diagnostic captured → `[Verify]`). Opposite triage prompts: "any recurrence since YYYY-MM-DD?" (Watching) vs "has the event happened yet?" (Waiting). Timed forms preferred (`[Watching 7d]`, `[Watching 24h]`); bare `[Watching]` is rare. For timed forms, body MUST give the absolute calendar date/time the soak expires. Soft, not hard: at expiry, triage suggests `[Verify]`; the user confirms. **No `[Watching F<NNN>]` form** — Watching is about a fix you shipped, not a chained dependency. |
| `[Ready]` | **Ready** | Design clean. Agent knows how to do the task without further user involvement. (See § Definition of Ready.) |
| `[Active]` | **Active** | Actively being worked on. |
| `[Verify]` | **Verify** | Implementation done, awaiting **user judgment** on whether the result matches intent. Apply only when user judgment is genuinely needed (semantic correctness, UX, design fit, whether prose captures the right idea). Mechanical work — terminology sweeps, refactors, mechanical renames, sed/grep replacements where the diff is its own proof — skip `[Verify]` and go `[Active]` → `[Done]` directly. The agent self-verifies the mechanical class. |
| `[Done]` | **Done** | Verified done. Terminal state for most work. |

Two **optional extension states** that not every surface uses:

| Label | Canonical name | Meaning |
|---|---|---|
| `[Released]` | **Released** | Shipped to users (post-`/code release`). Used when the surface tracks shipped state distinctly from completed. |
| `[Cancelled]` | **Cancelled** | Work was abandoned without completion. Terminal but not a success. |

### State graph

```
        ┌─────┐
        │ [ ] │  Unset
        └──┬──┘
           │  someone starts thinking
           ↓
   ┌──────────────┐
   │ [Designing]  │
   └──┬────┬────┬─┘
      │    │    │
      │    │    │ external blocker
      │    │    ↓
      │    │  ┌───────────┐
      │    │  │ [Blocked] │
      │    │  └─────┬─────┘
      │    │        │ blocker resolves
      │    │        ↓
      │    │ user input needed
      │    ↓
      │  ┌─────────────┐
      │  │ [Questions] │ ◄─── /ask skill
      │  │             │      (mandatory → [[Doc]] link)
      │  └─────┬───────┘
      │        │ user resolves
      │        ↓
      │ design clean
      ↓
   ┌────────────┐
   │  [Ready]   │  ◄─── /groom promotes here
   └─────┬──────┘
         │  /mint, /code mint, /code bugfix
         ↓
   ┌────────────────┐
   │ [Active]  │
   └─────┬──────────┘
         │  implementation complete
         ↓
   ┌─────────────┐
   │  [Verify]  │
   └─────┬───────┘
         │  /finalize discipline
         ↓
   ┌──────────────┐
   │ [Done]  │  (optional: → [Released] via /code release)
   └──────────────┘
```

### Definition of Ready

> **An item is Ready when you believe you know how to do this task without further involvement of the user.**

Sharper than "design questions resolved." If the task still hides any "wait, what about X?" that the user would have to answer, it's **not** Ready — it's `[Questions]`, and the work belongs in a feature doc until those questions resolve.

#### The RIGHT NOW test

> **`[Ready]` is a promise: the agent could pick this row up in this turn and execute it to `[Done]` (or `[Verify]`) with zero further interaction with the user.**

Not "soon." Not "next." Not "after we see if X happens." Not "in case the other fix fails." *Right now, this turn, no questions, no observations, no contingencies.* If anything stands between "agent reads the row" and "agent commits the work," the row is **not Ready** — it's one of the honest non-Ready states:

- **`[Waiting]`** / **`[Waiting Nd]`** — passively observing for an event we *want* to occur (a bug to recur with new logging, an external system to finish). Body must name what we're waiting on (and for timed forms, the absolute expiry date).
- **`[Watching]`** / **`[Watching Nd]`** — soaking on a fix; observing for *non*-recurrence of an event we *don't* want. Body must name what was changed, what non-recurrence proves, and (for timed forms) the absolute soak-expiry date.
- **`[Blocked]`** / **`[Blocked F<NNN>]`** — actively contingent on something external (another feature's outcome, a diagnostic capture, a review). Body must name the blocker; the chained-feature form lets the link carry the description.
- **`[Questions]`** — there's a decision the user has to make. Must point at a feature doc via `→ [[Doc]]`.

#### Disqualifying language

If a candidate `[Ready]` row's description contains any of these hedging phrases, it is **by definition not Ready** — the language IS the evidence of the dependency:

| Phrase pattern | Honest bracket | Why |
|---|---|---|
| "likely superseded by F<NNN>" / "supersedes" | `[Blocked F<NNN>]` | Contingent on whether F<NNN> actually fixed it. |
| "held as fallback" / "kept as backup" | `[Blocked F<NNN>]` or `[Waiting]` | The row exists *because* the primary path might fail — that's the blocker. |
| "in case X surprises us" / "in case X fails" | `[Blocked F<NNN>]` | Same — contingent on X's outcome. |
| "revisit only if X" | `[Blocked F<NNN>]` or `[Waiting]` | The row sleeps until X resolves. |
| "awaits natural recurrence" / "awaits next event" | `[Waiting]` | Passive observation for an event we *want* to occur; no agent action would advance it. |
| "soaking" / "burn-in" / "watching for recurrence" / "fix shipped, observing" | `[Watching Nd]` | Soaking on a fix; observing for *non*-recurrence with an expiry date. Opposite polarity from Waiting. |
| "may need" / "might want to" / "probably" / "possibly" | `[Questions]` or `[Designing]` | The uncertainty is a question the agent can't answer alone. |
| "contingent on" / "depends on whether" | `[Blocked]` | Same — explicit dependency. |

The list isn't exhaustive — it names the failure mode (hedging stands in for honest state). When you find yourself wanting to write hedging language in a `[Ready]` description, that's the signal to rebracket.

#### Rebracket discipline

`[Ready]` is re-evaluated on every `/triage` pass, the same way `[Blocked]` and `[Waiting]` are. A row that fails the RIGHT NOW test gets rebracketed in the backlog and in the triage output under its honest state. Triage is the enforcement moment.

This is the canonical definition. CAB Backlog cites it; `/groom` checks it for each candidate; `/feature` gates the Designing → Ready transition on it; `/triage` enforces it on every pass.

## State transitions

Every transition is driven by an explicit skill or trigger. There are no silent state changes.

| From | To | Triggered by | Notes |
|---|---|---|---|
| `[ ]` | `[Designing]` | `/feature`, manual edit, `/code plan` | A feature doc is created OR planning begins. |
| `[Designing]` | `[Questions]` | `/ask` skill | Pending Qs added to `## Open Questions`; bullet description rewritten as `→ [[Feature Doc]]` (link is mandatory). |
| `[Questions]` | `[Designing]` | User answers Qs | When pending Qs are resolved (`### Resolved`), description gets rewritten to reflect the resolved design. |
| any non-terminal | `[Blocked]` (or `[Blocked F<NNN>]`) | External blocker arises | Dependency, external review, CI failure, missing diagnostics, another feature's progression, etc. The work was at any state — `[Designing]`, `[Ready]`, `[Active]` — and hit a blocker that prevents further progress until something external resolves. |
| `[Blocked]` (or `[Blocked F<NNN>]`) | prior state | Blocker resolves | When a chained `F<NNN>` reaches `[Done]` (or otherwise the blocking condition clears), the item returns to whatever state it was in pre-block. Often `[Ready]` if it was design-clean, otherwise `[Designing]`. |
| any non-terminal | `[Waiting]` (or timed form) | Agent or user decides to wait | No actor's action would unblock; just letting time pass or observing for an event we *want*. Body must say what we're waiting on; timed forms must give the absolute expiration date in the body. |
| `[Waiting]` | various — `[Verify]`, `[Ready]`, `[Active]`, or stays `[Waiting]` | `/triage` reconsideration | **No automated transition.** Re-evaluated at every `/triage` pass: has the wait expired? did the watched event occur? — agent or user picks the next state case-by-case. Often `[Verify]` (check whether the wait condition occurred) or `[Ready]` (resume work). |
| typically `[Active]` post-fix, sometimes `[Verify]` if shipped via mechanical path | `[Watching]` / `[Watching Nd]` | Agent ships a fix and enters soak | Body must name what was changed, what non-recurrence proves, and (for timed forms) the absolute soak-expiry date. |
| `[Watching]` | `[Verify]`, `[Active]`, `[Designing]`, or stays `[Watching]` | `/triage` reconsideration | **No automated transition.** Re-evaluated at every `/triage` pass: has the soak expired? has there been a recurrence? At expiry with no recurrence → typically `[Verify]` (user confirms fix held, then `[Done]`). On recurrence → regress to `[Active]` or `[Designing]` (fix didn't hold; resume work). |
| `[Designing]` | `[Ready]` | `/groom`, `/feature` (Agreed gate) | Design is locked; Definition of Ready met. |
| `[ ]` | `[Ready]` | `/groom` (autonomous) | Item was clear enough that `/groom` could promote without going through Designing. |
| `[Ready]` | `[Active]` | `/mint`, `/code mint`, `/code bugfix`, `/code spike`, manual claim | Work begins. |
| `[Active]` | `[Verify]` | `/code mint`, `/code verify`, `/finalize` (verify step) | Implementation done; awaiting verification. |
| `[Verify]` | `[Done]` | `/finalize` discipline (verify → commit → push → merge → docs → cleanup), user confirmation | Verification passed. |
| `[Done]` | `[Released]` | `/code release` (optional) | Surfaces that distinguish shipped state. |
| any | `[Cancelled]` | manual decision | Work abandoned. Bullet typically moves to a "Cancelled" or "Icebox" location. |

### Anti-transitions (state changes that should NOT happen silently)

- **`[Active]` directly to `[Done]` for design-bearing work.** Always pass through `[Verify]` when user judgment is needed (`/finalize` owns this). **Exception:** mechanical work — terminology sweeps, refactors, mechanical renames, sed/grep replacements — skip `[Verify]` since the diff is self-evident; agent self-verifies and goes straight to `[Done]`. Don't ask the user to "skim a diff" — that's an abuse of the verify gate.
- **`[Designing]` to `[Active]` skipping `[Ready]`.** Definition of Ready is the gate; without it, you risk implementing on unresolved design.
- **`[Done]` back to any earlier state.** Once Completed, the work is closed. Reopening means a new B-number for the follow-up.

## Interface-validation gate

Interfaces (per [[CAB Interface]]) are the human-authored layer contracts that callers above the layer rely on. Creating a new Interface doc OR significantly modifying an existing one is **design-bearing work** — the agent's role is to draft and propose; the user's role is to validate.

**The gate fires when:**

- **Creating a new `{NAME} Interface.md`** — the file goes to `[Designing]` immediately. The agent drafts the layer contract (or works from a `rewire`-generated scaffold); promotion to `[Ready]` requires user approval of the contract; promotion to `[Done]` requires user verification that the final Interface accurately describes the layer.
- **Significantly modifying an existing Interface** — same gate. "Significant" means: adding, removing, or renaming public API entries; changing the conceptual model the doc presents; reshaping `## Public Modules` / `## How They Group`; changing the `## What's Hidden` boundary.
- **Migrating from legacy `{NAME} Rollup.md` to `{NAME} Interface.md`** — counts as significant (the semantics tightened — see F062). Same gate.

**The gate does NOT fire for:**

- Typo / grammar fixes that don't change meaning.
- Dead-link repair, wiki-link target updates, basename normalizations.
- Terminology sweeps that don't change what's documented (e.g., "rollup" → "interface" rename within doc body).
- Reformatting that doesn't shift the contract (column widths, table polish, header levels).
- Agent-driven structural rewrites the user already approved.

**Why the gate matters.** Without it, Interface docs drift into agent-generated noise that doesn't match the user's mental model of the layer. The layer-completeness and hiding invariants ([[CAB Interface]] § Defining Properties) require a human reviewer — they can't be auto-checked. The gate is a checkpoint, not a brake: the agent does the writing work; the user reads and approves.

**Sub-Interfaces.** Same gate applies — creating a new `{NAME} {LayerName} Interface.md` (sub-Interface) or significantly modifying one goes through user validation. Nested layers don't bypass the rule.

**Rewire's role.** When `rewire` finds a missing Interface, it scaffolds the file (empty TODO sections) AND files a `## Now [Designing]` backlog row pointing the user to author the contract collaboratively. The scaffold itself is not a contract; it's a placeholder until the gate completes.

## Blocked, Waiting, and Watching semantics

Honest categorization. `[Ready]` means *I (the agent) know how to do this without further user involvement* — pure agent-actionable. Everything that fails the bar but isn't waiting on user input lands in one of three "not-actionable-right-now" buckets, distinguished by *what* would advance the row:

- **`[Blocked]`** — someone (or something) needs to act to unblock it.
- **`[Waiting]`** — no one needs to act; we're observing for an event we *want* to occur. Resolution = event happens.
- **`[Watching]`** — no one needs to act; we're observing for an event we *don't* want to occur (a shipped fix's recurrence). Resolution = event *doesn't* happen by the soak expiry.

The point of being honest is that a `[Ready]` count the user trusts is more valuable than a `[Ready]` count that has drifted into "items the agent has read."

**Forms:**

- `[Blocked]` — generic. Body describes what's blocking (diagnostic capture, external review, missing dependency, cross-agent decision, future API, …).
- `[Blocked F<NNN>]` — chained. The blocker is another feature's progression. The chained F-number IS the description; click it to see real-time state. No body prose needed.
- `[Waiting]` — body MUST say what we're waiting on. Indefinite, observation-only for an event we *want* (e.g., "for the freeze bug to reoccur with the new logging in place").
- `[Waiting Nd]` / `[Waiting Nh]` — body MUST say what we're waiting on **plus** the absolute calendar date/time the wait expires. Summary stays terse (`1d`, `4h`) so the bracket doesn't bloat; the date lives in the body. **No `[Waiting F<NNN>]` form** — if you're waiting on another feature, you're action-shaped Blocked, not soft-observation Waiting.
- `[Watching]` — body MUST say what was changed and what non-recurrence would prove. Indefinite soak (rare; usually prefer the timed form).
- `[Watching Nd]` / `[Watching Nh]` — body MUST say what was changed, what non-recurrence proves, **and** the absolute calendar date/time the soak expires. **No `[Watching F<NNN>]` form** — Watching is about a fix you shipped, not a chained dependency.

### Description requirements for state-loaded brackets

`[Blocked]`, `[Waiting]`, `[Watching]`, and `[Verify]` are not just labels — they're claims that must be auditable in one read of the row. The body must answer:

| Bracket | Body must say |
|---|---|
| `[Blocked]` | What/who is blocking it |
| `[Blocked F<NNN>]` | Nothing required — the F<NNN> link IS the description |
| `[Waiting]` | What we're waiting on (event or time) |
| `[Waiting Nd]` / `[Waiting Nh]` | What we're waiting on **plus** the absolute calendar date/time the wait expires (relative durations age — "1d" is meaningless without knowing when it was written) |
| `[Watching]` | What was changed and what non-recurrence would prove |
| `[Watching Nd]` / `[Watching Nh]` | What was changed, what non-recurrence proves, **and** the absolute calendar date/time the soak expires |
| `[Verify]` | What to verify (the test or check that signals done) |

A bracket without a matching body answer is malformed.

### The lazy-Blocked / lazy-Waiting / lazy-Watching failure mode

**The most common drift in this vocabulary**: labeling something `[Blocked]` when it actually isn't blocked at all. Either no actor needs to do anything (so it's `[Waiting]` or `[Watching]`, or there's nothing to wait for and it's just `[Ready]`), or the only actor is *you, the agent* (so it's `[Questions]` or actually `[Active]`).

This happens when "Blocked" gets used as a thought-terminating label — "I'm not making progress on this, mark it Blocked, move on." The required-description rule above is the antidote: forcing the body to name the blocker reveals whether there's a real one. If you can't write a specific actor-and-action sentence, the row isn't actually Blocked.

**Parallel failure modes for Waiting and Watching:**

- **Lazy-Waiting** — body doesn't actually name an event we're observing for. Usually `[Ready]` or `[Blocked]` in disguise; rebracket honestly.
- **Lazy-Watching** — body doesn't name a fix that was shipped *and* what non-recurrence would prove. The defining test: did you ship a change whose holding is now under observation? If no — it's `[Waiting]` (we want the event) or `[Blocked]` (someone needs to act). If yes — it's `[Watching]` (we want *no* event).

**Watching vs Waiting — polarity, not timing.** The two states look similar (both passive, both timed, both reconsidered at triage) but they resolve on *opposite* outcomes. Picking the right one matters for the triage prompt: "any recurrence since YYYY-MM-DD?" (Watching) versus "has the event happened yet?" (Waiting). Saying "Waiting" when you mean "Watching" sets up the wrong question for the user.

**Triage reconsideration.** All three states — `[Blocked]`, `[Waiting]`, `[Watching]` — are reconsidered at every `/triage` pass. Has the blocker resolved? Has the wait condition occurred? Has the soak expired without recurrence? Is the labeling still honest? There is no automated transition; the triage discipline IS the re-evaluation moment.

**Examples (illustrative — the form, not the work itself):**

```
- **F019 — Image-clip drag-drop landing zone** [Blocked] — pending one human drag with a screenshot in the clipboard against the latest build to confirm the surface accepts it. (Diagnostic capture blocker; effectively pre-Verify.)
- **F034 — Sessions submenu centering** [Blocked] — defer until `submenuRect.w` is known synchronously at draw time; no upstream API yet.
- **F041 — Tier 3 Claude-Code-aware send verification** [Blocked F015] — extends F015's Tier 2 verifier with session-type detection. Cannot start until F015 ships.
- **F012 — Voice-bridge follow-up sweep** [Blocked F011] — depends on F011's MuxUX target bridge reaching `[Done]` (currently `[Verify]` — user judgment pending).
- **F-cross — DMUX schema change for dynamic File menu** [Blocked] — touches DMUX's config schema; cross-agent decision needed before MUX can implement. (Tracked elsewhere.)
- **F026 — Post-freeze flag-diff** [Waiting] — for the freeze bug to recur naturally so the 30s window-flag dumper can capture the culprit flag. Healthy baseline already taken 2026-05-08. (We *want* the event.)
- **F011 — MuxUX target bridge** [Watching 14d] — fix shipped `muxux@67ea41f` 2026-05-12; soaking until 2026-05-26. If no negative-X-screen freeze recurrence by then, fix held → mark `[Verify]` for confirmation and close. (We *don't* want the event.)
```

**How surfaces treat Blocked, Waiting, and Watching:**

- **`/groom`** skips all three — none is promotable to `[Ready]` without external resolution (Blocked), wait-condition observation (Waiting), or soak-expiry-without-recurrence (Watching). When a chained `F<NNN>` reaches `[Done]`, a wait-condition is observed to occur, or a Watching soak expires cleanly, /groom may auto-suggest a rebracket on a future sweep (or the agent re-brackets manually when noticed).
- **`/triage`** renders the bracket as-is in the body — `**[Blocked]**`, `**[Blocked F015]**`, `**[Waiting]**`, `**[Waiting 1d]**`, `**[Watching]**`, `**[Watching 7d]**` — and counts the row under its **horizon H2 only** (Now/Next/Later). Blocked, Waiting, and Watching items contribute *zero* to the H1 banner's `Active`/`Ready`/`Questions`/`Verify` columns, and *zero* to the TAG cascade's U or A. **All three states are reconsidered every triage pass** — that's their primary purpose. An anchor whose only items are Blocked / Waiting / Watching falls through to TAG `[G]` (groomable — user/time/soak needs to clear something) or `[]` (nothing actionable).
- **Banner**: no separate Blocked / Waiting / Watching count column. The horizon counts (Now/Next/Later) show where those items live; the per-row bracket carries the workflow truth. Keeping the banner at 4+4 columns prevents it from becoming a tally.

**The rebracket discipline.** When you find yourself about to mark something `[Ready]` to "represent that the agent has read it," stop — that's a `[Blocked]`, `[Waiting]`, or `[Watching]` candidate. Be specific about *why* it isn't Ready:
- missing diagnostic, awaiting another feature, pre-spec, cross-agent → **`[Blocked]`**
- time-passing, external observation we *want* to see (bug recurs, run finishes) → **`[Waiting]`**
- soaking on a fix, observing for *non*-recurrence → **`[Watching]`**

The bracket should be checkable against the row's body in one read.

## Skill cross-references

| Skill | What it advances |
|---|---|
| `/feature` | `[ ]` → `[Designing]` (creates feature doc); `[Designing]` → `[Ready]` at the Agreed gate. |
| `/groom` | `[ ]` or `[Designing]` → `[Ready]` autonomously, or `[Designing]` → `[Questions]` if questions remain (parks them in a feature doc with a `→ [[Doc]]` link). |
| `/ask` (skill) | Manages `[Questions]` ↔ `[Designing]` via question batching and resolution. The `→ [[Doc]]` link is the source of truth for where the questions live. Maintains the global `~/ob/kmr/Q.md` index. |
| `/mint`, `/code mint` | `[Ready]` → `[Active]` → `[Verify]`. |
| `/code bugfix` | Same as `/mint` but with a red-test gate at the start. |
| `/code spike` | Stays in `[Active]` while diagnosing root cause. |
| `/code verify` | `[Active]` → `[Verify]` (proof of completion). |
| `/finalize` (discipline) | `[Verify]` → `[Done]` (verify, commit, push, merge, update docs, cleanup). |
| `/code release` | `[Done]` → `[Released]` (changelog, version, package, publish, ship). |
| `/roster` | Reads state across all items and prints per-bucket counts. |
| `/audit` | Generates new `[ ]` items from findings (no state advancement). |

## Mutation API — `backlog-edit.py`

The canonical way to mutate a backlog row. All skills that advance, park, or rebracket items go through this script instead of editing the backlog file directly.

**Path:** `~/.claude/skills/workflow/scripts/backlog-edit.py` (skill-owned; no `~/bin/` dependency).

**Args (positional):**

```
backlog-edit.py <slug> <horizon> <row-id> <status> [title] [body]
```

| Arg | Values |
|---|---|
| `slug` | Anchor slug (`SKA`, `MUX`, `HA`, …). The tool finds the backlog file from this — callers do not pass paths. |
| `horizon` | `Now` / `Next` / `Later` / `Active` / `Ready` / `Done` / `Verify`, or **`same`** to leave the row in its current H2 (errors if the row doesn't exist). |
| `row-id` | `F<NNN>` / `B<n>` / `B-<slug>` to address an existing row, or **`Fnew`** / **`Bnew`** to mint the next available number (max + 1, F-numbers zero-padded to three digits). |
| `status` | Bracket text (`Ready`, `Questions`, `Verify`, `Watching 7d`, `Done`, `Verify-by 2026-06-15`, …), or **`delete`** to remove the row. |
| `title` | Row title — goes inside the bold prefix. Optional. |
| `body` | Trailing text after the status bracket — wiki-link, description, dates, etc. Optional. |

Row shape produced:

```
- **<row-id> — <title>** [<status>] — <body> ^<row-id>
```

**Preserve-on-omit semantics for existing rows.** When updating a row that already exists, omitting `title` / `body` **or passing them as empty strings** preserves the row's current title/body — only the status/horizon change. This is the common case for status transitions:

```
backlog-edit.py SKA same F095 Ready                          # bracket-only; preserves title+body
backlog-edit.py SKA Done F095 Done                           # move to ## Done + status; preserves title+body
backlog-edit.py SKA same F095 Designing "New Title"          # update title; preserve body
backlog-edit.py SKA same F095 Done "" "Shipped 2026-06-15"   # update body; preserve title
```

For new rows, omitting title/body produces `- **<row-id>** [<status>] ^<row-id>` (bare row) — empty strings on new rows also produce a bare row.

**Side effects:**

1. Mutates the row in `{slug} Backlog.md`.
2. Invokes `~/.claude/skills/audit/scripts/audit-q.py --scope backlog --anchor <slug> --fix` to refresh `~/ob/kmr/Q.md` (banner counts, status drift).
3. Appends one `[INFO]` entry to the per-anchor `{slug} Messages.md` and one to the global sentinel `~/.claude/state/agent-messages` (surfaced to the next agent on Stop hook).

**Output:** stdout = `<slug>: <verb> <row-id> in <horizon> [<status>]` (one line). For mint operations, the assigned row-id is in the output — parse it when the caller needs to reference the new row (e.g., `/feature` naming a new feature doc file).

**Discipline — skills MUST NOT edit backlog files directly.** All row creation, status changes, horizon moves, and deletions go through this script. Direct edits bypass the Q.md refresh and the Messages notification, which silently breaks the cross-agent state-of-the-anchor surface.

The script is invoked via `Bash`:

```
~/.claude/skills/workflow/scripts/backlog-edit.py SKA Now Fnew Designing "Title" "→ [[F095 — Title]]"
```

**Minting flow** (when the caller needs the new F/B number — e.g., `/feature` naming a new feature doc file):

1. Invoke with `Fnew` (or `Bnew`) and stub content.
2. Parse the assigned row-id from stdout — output line is `<slug>: added <row-id> in <horizon> [<status>]`. Extract the second word after `added`.
3. Use the parsed row-id downstream (feature doc filename, wiki-links, etc.).
4. If the caller needs to update the row body once downstream artifacts exist (e.g., after creating the feature doc, the row should include `→ [[F<NNN> — Title]]`), invoke again with the explicit row-id and `same` horizon.

## Per-surface mappings

Each surface that uses workflow state cites this discipline and maps the canonical states onto its own structure.

### Backlog (`{NAME} Backlog.md`)

Per `[[CAB Backlog]]` and `[[SKA backlog]]`:

- Workflow state is shown via the `[Status]` square-bracket prefix in each bullet, OR implied by the bullet's H2 placement.
- H2 sections combine **horizon** (`## Now`, `## Next`, `## Later`) and **workflow state** (`## Active`, `## Ready`, `## Done`).
- Items in horizon H2s use `[Status]` brackets — typically `[ ]`, `[Designing]`, `[Questions]`, `[Blocked]`, `[Waiting]`, `[Watching]`, or `[Verify]`.
- Items in workflow-state H2s have their state implied by the H2 — the bracket is optional/redundant.
- **`[Verify]` is bracket-only — there is no `## Verify` H2.** Verify items stay in their horizon (typically `## Now`) with the `[Verify]` bracket. Rationale: verify is short-lived (waiting on user yes/no) and conceptually keeps the item in its horizon. The bracket alone carries the state, and the backlog-row description text becomes the verify-plan instructions for the user (consumed by `/triage`).
- The `## Legwork` H2 is a **category tag**, not a workflow state. Items in Legwork still have a state (Ready / Active / etc.), shown in their bracket.

### Roadmap (`{NAME} Roadmap.md`)

Milestones use the same canonical states at coarser granularity. A milestone is in the **most-advanced state shared by all its acceptance criteria**:

- All criteria `[Done]` → milestone `[Done]`.
- Any criterion `[Active]` → milestone `[Active]`.
- All criteria `[Ready]` or beyond → milestone `[Ready]`.
- Else → milestone `[Designing]` or `[Blocked]` per most-blocking criterion.

### Feature lifecycle (`feature/SKILL.md`)

The feature doc Status field uses the canonical states with two feature-specific accommodations:

- **`Proposed` collapses to `[Designing]`.** Don't use "Proposed" as a separate state; it's just early Designing. The bracket on a freshly-created feature doc is `[Designing]`.
- **`Agreed` is a feature-doc-specific synonym for `[Ready]`.** Kept distinct because the Agreed gate is genuinely meaningful — it marks user approval to start implementation, not just "design clean." A feature doc moves to `Agreed` when the user explicitly approves; the bracket may be either `[Agreed]` or `[Ready]` (interchangeable in feature-doc context).

| Feature lifecycle label | Canonical state | Notes |
|---|---|---|
| Designing | `[Designing]` | Same. (Replaces former "Proposed" — it's just early Designing.) |
| Agreed | `[Ready]` (synonym `[Agreed]`) | User has approved the design. Synonym preserved for the Agreed gate semantics. |
| Implementing | `[Active]` | Canonical-name alias. |
| Testing | `[Verify]` | Same. |
| Done | `[Done]` | Canonical-name alias. |

### PRD

Light usage. PRDs are documents, not units of work — they're *artifacts* produced during the Designing phase of a feature or planning cycle. Common PRD-internal states:

- `[Draft]` — being written.
- `[Approved]` — user has signed off; work can proceed against this PRD.

These are PRD-doc-internal; they don't appear in backlog or roster.

## Active-work invariant

> **Every feature doc representing active work is reachable in ≤2 clicks from EITHER `{NAME} Backlog.md` OR `{NAME} Roadmap.md`. Iced feature docs are reachable from `{NAME} Icebox.md`. Anything in `{NAME} Features/` not reachable from one of those three is an *orphan* and a violation.**

This is the structural sharpening of the per-surface mappings above: those say *what state items are in*; this says *where the items must live to be tracked*.

### Three surfaces, parallel namespaces

| Surface | File | Namespace | Role |
|---|---|---|---|
| **Backlog** | `{NAME} Backlog.md` | F-numbers (`F1`, `F2`, ...) — monotonic-forever, never recycled per `[[CAB Backlog]]` § Numbering policy | Active to-do list |
| **Roadmap** | `{NAME} Roadmap.md` | M-numbers (`M1`, `M1.2`, `M1.2.3` — hierarchical) | Milestone-level active work |
| **Icebox** | `{NAME} Icebox.md` | Shares F-number namespace with backlog | Parked / frozen — explicitly inactive but tracked |

**F and M are distinct namespaces.** A backlog row never collides with a roadmap milestone — `F5` and `M5` can coexist. F-numbers are unique across backlog AND icebox: an item moving between them keeps its F-number; thawing an iced item brings the same F-number back. M-numbers belong only to the roadmap.

**Letter prefix choice — M not R:** M (for Milestone) parses cleanly in DMUX dictation; R does not without a leading "letter" qualifier. M is also the de-facto convention across existing roadmaps (HA, MUX, DMUX, DKT).

### When does a milestone need a feature doc?

- **Top-level milestones (M1, M2, ...) ALWAYS have a feature doc** at `Features/M{n} — {Name}.md`. Even if the user-facing/system-facing spec lives elsewhere (PRD, system design, user docs), the feature doc still exists as the home for **meta-discussion and "what's the work to do" notes** that don't belong in shipping documentation.
- **Sub-milestones (M1.2, M1.2.3) get feature docs only when needed** — when there's real meta or work-breakdown to capture. Otherwise the milestone bullet in the roadmap is enough. Per-sub-milestone judgment call.

### Content philosophy — feature doc vs spec docs

The feature doc is **work-TBD + meta-discussion**:
- *Why* decisions were made (trade-offs, alternatives, rationale).
- *What work needs to be done* (implementation plan, acceptance criteria, sub-tasks).
- Open questions during design (per `[[SKA ask]]`).

The user-facing and system-facing **spec content** (API surfaces, command syntax, screens, architecture, data models) lives in:
- **User docs** (`{NAME} User/`) — what the user sees / types / configures.
- **System Design** / **PRD** (`{NAME} Plan/`) — what the system does / how it's built.
- **Module docs** (`{NAME} Dev/`) — per-component developer documentation.

Why split? **No duplication** — if the API spec lives in both the feature doc and `{NAME} User/CLI.md`, the two will drift; one source of truth. **The feature doc is ephemeral, the spec is durable** — once a milestone ships, the feature doc's "why" still has historical value, but its "what" should be the system docs (which keep getting updated). Keeping the "what" out of the feature doc forces the agent to write the spec into the durable doc the first time, instead of writing it twice (or worse, leaving the durable doc stale).

### Icebox interaction

The icebox is a **sanctioned exception** to the "active" part of the invariant. Items in `{NAME} Icebox.md` are not active by definition.

1. **F-number namespace is shared across backlog AND icebox** — no F-number collisions; an item moving between the two keeps its F-number.
2. **`/groom` and `/triage` ignore the icebox by default.** Default scope = backlog only. Iced items don't appear in the body of either skill's output.
3. **Counts surface the icebox total.** Both `/roster` and `/triage` show `(Icebox: N)` in the count line — visibility without competing for attention.
4. **Explicit invocation can target the icebox.** `/groom icebox`, `/triage icebox`, `/groom F<n>` (where F<n> is iced) all work.
5. **Iced feature docs are NOT orphans.** A doc linked from `{NAME} Icebox.md` satisfies the invariant.

### Enforcement

- **At creation time** — `feature/SKILL.md` step 1.5 mandates minting a backlog (or roadmap) row when a feature doc is created. The mint happens via `backlog-edit.py Fnew` (see § Mutation API above); no `--orphan` flag, no convention-only escape hatch, no direct backlog edit.
- **Continuous** — `/audit structure` includes an orphan-check sub-audit: walks `{NAME} Features/` and flags any feature doc not linked from backlog/roadmap/icebox.
- **One-time sweep at landing** — when this invariant first lands per anchor, run `/audit structure --orphan-sweep` to backfill rows for any pre-existing orphans.

## Horizons vs workflow states

These are **two independent axes**:

- **Horizon** — *when* the user wants the work to happen. Owned by `[[SKA backlog]]`. Values: Now, Next, Later (plus Icebox outside the backlog).
- **Workflow state** — *whether* the work has progressed and how far. Owned by this discipline. Values: Unset, Designing, Blocked, Ready, Active, Testing, Completed.

**Common conflation: "Now" vs "Active."** They look similar but mean different things.

- `Now` is a **scheduling intent**: "we want to pull this into action soon."
- `[Active]` is a **state**: "we have actually started and are working on it."

An item can sit in `## Now` for a while as `[Ready]` (we want to do it soon, haven't started yet). When work begins, it transitions to `[Active]` and typically **moves out of the horizon section into `## Active`** — because once active, the horizon question is moot.

Same for `[Verify]` and `[Done]`: those states have their own H2s. Horizon H2s are for **upcoming** work (pre-In-Progress); workflow-state H2s are for **active and finished** work.

## Anti-patterns

- **Inventing a new state name** instead of citing the canonical one. If your skill needs a state that isn't in the canonical graph, propose adding it here — don't fork.
- **Implicit state transitions.** Every state change should be driven by a named skill or trigger; "the agent decided" is not a transition.
- **Treating "Ready" loosely.** Ready means *the agent could complete this in this turn with zero further user interaction*. If the description says "likely superseded," "held as fallback," "in case X," "awaits natural recurrence," "revisit only if," "soaking," "burn-in," "watching for recurrence," "may need," "might want to," "probably," "possibly," "contingent on," "depends on whether" — it is **not Ready**. The honest bracket is `[Waiting]`, `[Watching]`, `[Blocked]` / `[Blocked F<NNN>]`, or `[Questions]`. See § Definition of Ready → The RIGHT NOW test for the full rule and rebracket discipline.
- **Lazy-Blocked / lazy-Waiting / lazy-Watching.** Labeling a row `[Blocked]`, `[Waiting]`, or `[Watching]` without a body that names the specific blocker / watched event / shipped change. The most common drift in this vocabulary — these brackets get used as thought-terminating labels ("not progressing, mark it Blocked, move on"). The required-description rule is the antidote: if you can't write an actor-and-action sentence (Blocked), an event/time sentence (Waiting), or a "this was changed; non-recurrence proves it held" sentence (Watching), the row isn't actually in that state. Also: **don't conflate Waiting and Watching** — they resolve on opposite outcomes (event-occurs vs event-doesn't-occur) and set up opposite triage prompts.
- **Skipping `[Verify]`.** Implementations that go straight to Completed bypass the verification gate. `/finalize` enforces this; manual edits should respect it.
- **State drift between surfaces.** If a backlog item is `[Active]` but the feature doc Status says "Designing," one of them is wrong — the user shouldn't have to guess which.
- **Lazy-Blocked / lazy-Waiting.** Labeling a row `[Blocked]` or `[Waiting]` without a body that names the specific blocker or watched condition. The most common drift in this vocabulary — when "Blocked" gets used as a thought-terminating label ("not progressing, mark it Blocked, move on"). The required-description rule above is the antidote: if you can't write an actor-and-action sentence (Blocked) or an event/time sentence (Waiting), the row isn't actually in that state.

