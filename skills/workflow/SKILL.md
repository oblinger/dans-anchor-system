---
name: workflow
description: Discipline that owns the canonical state graph for a unit of work — state names, transitions, Definition of Ready, and per-surface mappings (Backlog, Roadmap, Feature lifecycle, PRD). Cited from CAB Backlog, feature/SKILL.md, /groom, /mint, /finalize, and other skills that advance work through states.
user_invocable: false
---

# Workflow Discipline
requires:: vault, skill:audit, facet:backlog, facet:roadmap
The canonical state graph for a unit of work — every state, the Definition of Ready, the per-surface mappings, and the `state` CLI that all advancing skills call.

| Table of Contents |  |
|---|---|
| **[[#Why this exists — the problem it solves]]** |  |
| **[[#Never strand the user — the stop invariant (F244)]]** |  |
| **[[#The canonical state graph]]** |  |
|    [[#State graph]] |  |
|    [[#Definition of Ready]] |  |
| **[[#State transitions]]** |  |
|    [[#Anti-transitions (state changes that should NOT happen silently)]] |  |
| **[[#Interface-validation gate]]** |  |
| **[[#Blocked, Waiting, and Watching semantics]]** |  |
|    [[#The self-unblock test — before ANY item rests as `[Blocked]` (load-bearing)]] |  |
|    [[#Description requirements for state-loaded brackets]] |  |
|    [[#The lazy-Blocked / lazy-Waiting / lazy-Watching failure mode]] |  |
| **[[#Skill cross-references]]** |  |
| **[[#Mutation API — `state`]]** |  |
|    [[#Backlog rows — `state Backlog <F<n>\|T<n>> <verb>`]] |  |
|    [[#Doc queries — `state <doc> <Q<n>\|V<n>> <verb>`]] |  |
|    [[#Side effects]] |  |
|    [[#Legacy `backlog-edit.py`]] |  |
| **[[#Per-surface mappings]]** |  |
|    [[#Backlog (`{slug} Backlog.md`)]] |  |
|    [[#Roadmap (`{slug} Roadmap.md`)]] |  |
|    [[#Feature lifecycle (`feature/SKILL.md`)]] |  |
|    [[#PRD]] |  |
| **[[#Active-work invariant]]** |  |
|    [[#Three surfaces, parallel namespaces]] |  |
|    [[#When does a milestone need a feature doc?]] |  |
|    [[#Content philosophy — feature doc vs spec docs]] |  |
|    [[#Icebox interaction]] |  |
|    [[#Enforcement]] |  |
| **[[#Horizons vs workflow states]]** |  |
| **[[#Anti-patterns]]** |  |

The canonical state graph for a unit of work — names every state, defines Definition of Ready, maps states onto each surface (Backlog / Roadmap / Feature / PRD), and owns the `state` mutation CLI that all advancing skills must call.

The single source of truth for **what state a unit of work is in**, **what it means**, and **what advances it to the next state**. Every skill that touches the state of work — `/groom`, `/feature`, `/mint`, `/finalize`, `/code release`, audits — cites this discipline.

> **F129 (2026-06-07):** state mutations go through `~/.claude/skills/workflow/scripts/state` (verb-first CLI). Old positional `backlog-edit.py` invocations still work during the migration window. Full CLI spec: [[DAS State]] (`~/.claude/skills/workflow/DAS State.md`).

## Why this exists — the problem it solves

The same vocabulary appears across many surfaces: backlog items have a status, feature docs have a Status field, roadmap milestones have progress, PRDs have a draft/approved cycle. **The labels diverge subtly** — "Agreed" in feature lifecycle is roughly "Ready" in backlog; "Done" in features is "Completed" in backlog; "Active" appears in both but with slightly different gates. Skills that touch state pick whichever label was nearest at hand.

The drift compounds: a new skill writes its own state names; the user can't tell at a glance whether `Designing` and `Proposed` are the same thing or different; the Definition of Ready lives in CAB Backlog but is implicitly assumed by skills that don't cite it.

This discipline collapses that to **one state graph** with **one Definition of Ready** that every surface and every skill references. Surfaces (backlog, roadmap, feature, PRD) get a short mapping section saying "here's how the canonical states appear here" — they don't redefine the graph.

## Never strand the user — the stop invariant (F244)

This is the **Agent Drive** idea (the Drive group's core promise, [[DAS Drive Design]] § Overview): **both the agent and the user keep making as much progress as they can, without needless back-and-forth.** Concretely, every handoff back to the user hands them **the biggest chunk of progress it can** — the deck cleared of everything the agent could do itself — and **the most decisions it can** — every pending question recorded in state, none left in chat to scroll away. That gives one hard rule at every stop:

> **On a work-armed stop, the anchor's grooming worklist must be empty.**

When the agent stops, the user can do exactly two things next: **answer** a pending question, or tell the agent to **crank**. A legal stop must leave at least one of those live — otherwise the user is stranded (they can't crank, because they can't see what's Ready; and they can't answer, because no question is recorded). So:

- **To let them crank** — the frontier must be *groomed*: every `## Now`/`## Next` row in an honest state (Ready+Next / Questions / Blocked / Waiting / Verify). "Ungroomed" rows are the **grooming worklist** — mechanically, `_triage_gate_findings` (a `[Ready]` row with no executable `- **Next:**`, an F242 non-answer Next, a bracket/H2 mismatch). See it any time with **`state groom-list`** (prints the worklist, or the empty-worklist status line `{SLUG}: {recommendation} . Groomed . Runnable N . User M . Verify K` — `all clear` in the recommendation slot only when nothing is open).
- **To let them answer** — a real question must be **recorded in state** (`state … Q+ define` → the row becomes `[Questions]`), *not merely typed in chat.* A chat-only question rolls off the screen; the user says "crank," never realizing a question was pending, and it is lost. Recording the question grooms that item off the worklist — so posting it *is* how you clear the gate for a decision you can't make yourself.

**"Work-armed"** means the ending turn used a tool (an edit / write / bash / state mutation). A pure Q&A or design turn is never gated — this is not a nag on conversation, it is a backstop on *work* stops. There is **no context-<40% escape**: emptying the list from a low budget costs only a little (grooming is planning / rebracketing / posting a question — never execution), so the agent spends it and leaves things clean rather than bailing. Enforced involuntarily by the Stop-hook (`crank-stop-hook.py`, F244) with a fail-open block cap; the agent should not need the backstop — ending a work session with an empty worklist is the norm.

**The closing line — echo the status banner (the handoff made visible).** The point of the handoff is to show the user where things stand, so a work-armed turn **ends by echoing the anchor's status banner as its last line**, in this one exact format (T034):

`{SLUG}: {recommendation} . Groomed . Runnable N . User M . Verify K`

Straight from **`state <anchor> summary-line --recommend <directive>`** (F248) — the canonical emitter for this line. The agent supplies **only** the recommendation directive; `state` owns and derives everything else (counts, ` . ` separators, `Groomed`, TTY-blue) so the line can never drift from what the user sees in `Q.md`. `--recommend` is **required** — the never-strand guard (F244): the agent cannot emit the closing line without explicitly making the compact/clear/crank/answer call. Directive → slot: `compact`→`please /compact`, `clear`→`please /clear`, `crank` (or `nothing`)→`crank with '`, `answer`→`answer the N on your plate` (N derived), `clear-all` (or `done`)→`all clear`. Rules: **(1)** lead with the anchor **slug + colon** (`SKA:`) — deliberate identity redundancy, so a user jumping between agent tabs sees who they're talking to; **(2)** the `{recommendation}` slot carries the agent's recommended next move; **(3)** `Groomed` is the fixed single word meaning the worklist is empty; **(4)** counts as `Runnable N . User M . Verify K`, separator ` . ` (space-period-space), never ` · `; **(5)** the **entire line is blue** (see § the blue-rendering mechanism below). Canonical: `SKA: please /clear . Groomed . Runnable 1 . User 0 . Verify 0`. **Call `summary-line` once and echo its stdout verbatim** — do not hand-compose the line, and do not make each `state` mutation emit a banner (a turn calls `state` many times; per-call banners are noise, not signal). The one closing line lets the user pick their own next move at a glance: questions piling up → answer a batch; lots Ready → press `'` and crank. (`state groom-list` still prints the same-format line on its empty-worklist branch, but with only the *derivable* slot — reach for `summary-line` when you want to state the recommendation, `groom-list` when you want the ungroomed frontier.)

`Groomed` names the **grooming** state, never open work — it means the frontier is fully planned, *not* "nothing to do" (Runnable>0 is still open work). The distinct all-zero phrasing is `all clear` in the recommendation slot, which appears only when Runnable+User+Verify are all zero. (Saying "all caught up · Ready 1" was the confusing wording this fixed.)

**The recommendation slot is where the agent's judgment shows.** The counts tell the user *where things stand*; the recommendation tells them *what to do*, and the agent often knows better than the counts alone. `state groom-list` fills what it can derive (`crank with '` when Ready>0, `answer the N questions` when Questions>0); the agent **overrides** the slot when it knows more. Chief case: when the only Ready item is **fresh-session-scale** — large, self-contained in its feature doc, and better executed by an unfatigued context than by cranking on this turn's accumulated one — the honest recommendation is **`please /compact`** (or **`please /clear`** when the feature doc + its survey fully specify the work and nothing in the current context is worth keeping), naming the item. The user acts on that immediately.

**The blue-rendering mechanism (T034c, resolved).** The `state groom-list` emitter wraps the whole line in ANSI blue (`\033[34m…\033[0m`), tty-guarded and `NO_COLOR`-respecting — so anyone who runs the command **in a terminal** sees blue. The one limit worth knowing: Claude Code renders assistant messages as **markdown** and provides no blue-text primitive (it does not honor ANSI in assistant prose), so when the agent *echoes* the line as chat text it renders in the default color, not blue. The blue "scan across tabs" affordance is therefore delivered by the emitter as a terminal surface, not by the agent's markdown echo; the agent's job is to echo the exact-format line as its last output. If a future Claude Code build exposes a color primitive for assistant text, wire the echo to it there.

## The canonical state graph

A unit of work moves through these states. Each state has a **square-bracket label** that appears in bullet form (extending the markdown checkbox idiom) and a **canonical name**.

| Label | Canonical name | Meaning |
|---|---|---|
| `[ ]` | **Unset** | Idea captured, no progress yet. Default for new items. |
| `[Designing]` | **Designing** | Being thought through. Design work in flight; spec not yet locked. No questions raised yet. |
| `[Questions]` | **Questions** | Blocked on user input on open questions. **Must** be paired with a `→ [[Feature Doc]]` link to where the `## Open Questions` block lives. |
| `[User]` | **User-action** | Gated on a genuinely user-only ACTION the agent cannot perform itself — a login, a permission-dialog click, a credential, a 2FA tap. Body **MUST** carry a `- **User:**` sub-bullet naming the exact action (with live `[[wiki-links]]` / URLs); **MAY** also carry a `- **Next:**`, the queued agent step once the user acts. Distinct from `[Questions]` (a user *answer*) and `[Verify]` (a user *judgment*): `[User]` is a user *action*. Surfaces to the user — its count folds into the Questions (user-gated) banner bucket (count-only) — but keeps its distinct bracket. Minted via `state … set --status User --user "<action>" --why-user-action "<why only you>"`; the [[F259 — User-action state (User bracket for user-gated actions)\|F259]] ownership gate (the F240 sibling) refuses a `[User]` the agent could do itself — if you *can* do it, it's `[Ready]` with a `- **Next:**`, not `[User]`. |
| `[Blocked]` | **Blocked** | Blocked on something other than user questions — a dependency, an external review, a CI / build issue, missing diagnostic evidence, or any other non-question blocker. Body of the row should describe what's blocking. |
| `[Blocked F<NNN>]` | **Blocked on a feature** | Parameterized form of `[Blocked]`. The blocker is another feature's progression — click `F<NNN>` to see its current state (typically `[Verify]`, `[Active]`, or `[Designing]`). The chained reference IS the blocker description; body need not repeat it. |
| `[Waiting]` / `[Waiting Nd]` / `[Waiting Nh]` | **Waiting** | **Body MUST say what we're waiting on.** Not actively blocked — no actor's action would unblock it; just letting time pass or observing for an external event (bug to reoccur, log file to fill, user to exercise the feature, GPU run to finish). Distinct from `[Blocked]`: Blocked has a fixable obstacle; Waiting does not. For timed forms (`Nd`, `Nh`), the body must **additionally** give the absolute calendar date/time the wait expires — relative durations age and "1d" is meaningless without knowing when it was written. Soft, not hard: `[Waiting 1d]` means "give it at least a day, re-check at next `/groom` pass," not "exactly 1 day then act." |
| `[Watching]` / `[Watching Nd]` / `[Watching Nh]` | **Watching** | **Soak — we may have fixed it; observing for recurrence.** Body MUST say (1) what was changed that's under observation and (2) what *non*-recurrence would prove. Distinct from `[Waiting]` by **resolution polarity**: Watching resolves when the watched event *doesn't* occur (no recurrence by expiry → fix held → `[Verify]`); Waiting resolves when the watched event *does* occur (e.g. bug recurs → diagnostic captured → `[Verify]`). Opposite reconsideration prompts: "any recurrence since YYYY-MM-DD?" (Watching) vs "has the event happened yet?" (Waiting). Timed forms preferred (`[Watching 7d]`, `[Watching 24h]`); bare `[Watching]` is rare. For timed forms, body MUST give the absolute calendar date/time the soak expires. Soft, not hard: at expiry, `/groom` suggests `[Verify]`; the user confirms. **No `[Watching F<NNN>]` form** — Watching is about a fix you shipped, not a chained dependency. |
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
      │ user ACTION needed (login / auth / permission click)
      │        ↓
      │  ┌─────────────┐
      │  │   [User]    │ ◄─── surfaces like a question
      │  │             │      (mandatory - **User:** action)
      │  └─────┬───────┘
      │        │ user acts
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
- **`[User]`** — there's an ACTION only the user can take (a login, a permission-dialog click, a credential, a 2FA tap). Body must carry a `- **User:**` sub-bullet naming it. Only honest when the agent genuinely cannot do it — even via `box` / `osascript` / `bridge`; else it's `[Ready]` with a `- **Next:**` (the lazy-delegation antipattern).

#### Disqualifying language

If a candidate `[Ready]` row's description contains any of these hedging phrases, it is **by definition not Ready** — the language IS the evidence of the dependency:

| Phrase pattern | Honest bracket | Why |
|---|---|---|
| "likely superseded by `F<NNN>`" / "supersedes" | `[Blocked F<NNN>]` | Contingent on whether `F<NNN>` actually fixed it. |
| "held as fallback" / "kept as backup" | `[Blocked F<NNN>]` or `[Waiting]` | The row exists *because* the primary path might fail — that's the blocker. |
| "in case X surprises us" / "in case X fails" | `[Blocked F<NNN>]` | Same — contingent on X's outcome. |
| "revisit only if X" | `[Blocked F<NNN>]` or `[Waiting]` | The row sleeps until X resolves. |
| "awaits natural recurrence" / "awaits next event" | `[Waiting]` | Passive observation for an event we *want* to occur; no agent action would advance it. |
| "soaking" / "burn-in" / "watching for recurrence" / "fix shipped, observing" | `[Watching Nd]` | Soaking on a fix; observing for *non*-recurrence with an expiry date. Opposite polarity from Waiting. |
| "may need" / "might want to" / "probably" / "possibly" | `[Questions]` or `[Designing]` | The uncertainty is a question the agent can't answer alone. |
| "you need to log in / authenticate" / "click allow" / "enter your password / credential" / "grant permission" / "approve on your device" | `[User]` | An ACTION only the user can perform (F259) — not the agent's to do. Name it in a `- **User:**` sub-bullet; the row surfaces to the user like a question. |
| "contingent on" / "depends on whether" | `[Blocked]` | Same — explicit dependency. |

The list isn't exhaustive — it names the failure mode (hedging stands in for honest state). When you find yourself wanting to write hedging language in a `[Ready]` description, that's the signal to rebracket.

#### Rebracket discipline

`[Ready]` is re-evaluated on every `/groom` pass, the same way `[Blocked]` and `[Waiting]` are. A row that fails the RIGHT NOW test gets rebracketed in the backlog, and the render reflects its honest state. `/groom` is the enforcement moment.

This is the canonical definition. CAB Backlog cites it; `/groom` checks it for each candidate and enforces it on every pass; `/feature` gates the Designing → Ready transition on it.

## State transitions

Every transition is driven by an explicit skill or trigger. There are no silent state changes.

| From | To | Triggered by | Notes |
|---|---|---|---|
| `[ ]` | `[Designing]` | `/feature`, manual edit, `/code plan` | A feature doc is created OR planning begins. |
| `[Designing]` | `[Questions]` | `/ask` skill | Pending Qs added to `## Open Questions`; bullet description rewritten as `→ [[Feature Doc]]` (link is mandatory). |
| `[Questions]` | `[Designing]` | User answers Qs | When pending Qs are resolved (`### Resolved`), description gets rewritten to reflect the resolved design. |
| any non-terminal | `[User]` | Agent hits a user-only action | `state … set --status User --user "<action>" --why-user-action "<why only you>"`. The agent has done all it can; further progress needs a login / permission-click / credential / 2FA the agent cannot perform (F259). Refused if the agent could do it itself. |
| `[User]` | prior state | User performs the action | Returns to whatever state it was in — `[Ready]` if design-clean (the queued `- **Next:**` becomes executable), else `[Designing]`. Exactly like `[Blocked]` / `[Questions]` resolution. |
| any non-terminal | `[Blocked]` (or `[Blocked F<NNN>]`) | External blocker arises | Dependency, external review, CI failure, missing diagnostics, another feature's progression, etc. The work was at any state — `[Designing]`, `[Ready]`, `[Active]` — and hit a blocker that prevents further progress until something external resolves. |
| `[Blocked]` (or `[Blocked F<NNN>]`) | prior state | Blocker resolves | When a chained `F<NNN>` reaches `[Done]` (or otherwise the blocking condition clears), the item returns to whatever state it was in pre-block. Often `[Ready]` if it was design-clean, otherwise `[Designing]`. |
| any non-terminal | `[Waiting]` (or timed form) | Agent or user decides to wait | No actor's action would unblock; just letting time pass or observing for an event we *want*. Body must say what we're waiting on; timed forms must give the absolute expiration date in the body. |
| `[Waiting]` | various — `[Verify]`, `[Ready]`, `[Active]`, or stays `[Waiting]` | `/groom` reconsideration | **No automated transition.** Re-evaluated at every `/groom` pass: has the wait expired? did the watched event occur? — agent or user picks the next state case-by-case. Often `[Verify]` (check whether the wait condition occurred) or `[Ready]` (resume work). |
| typically `[Active]` post-fix, sometimes `[Verify]` if shipped via mechanical path | `[Watching]` / `[Watching Nd]` | Agent ships a fix and enters soak | Body must name what was changed, what non-recurrence proves, and (for timed forms) the absolute soak-expiry date. |
| `[Watching]` | `[Verify]`, `[Active]`, `[Designing]`, or stays `[Watching]` | `/groom` reconsideration | **No automated transition.** Re-evaluated at every `/groom` pass: has the soak expired? has there been a recurrence? At expiry with no recurrence → typically `[Verify]` (user confirms fix held, then `[Done]`). On recurrence → regress to `[Active]` or `[Designing]` (fix didn't hold; resume work). |
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

Interface docs carry a user-validation gate: creating a new `{slug} Interface.md` or significantly modifying one is design-bearing work that must pass through `[Designing]` → `[Ready]` (user approves the contract) → `[Done]` (user verifies it describes the layer). The gate's full contract — when it fires, when it doesn't, and why — lives in **[[DAS Interface]] § Interface-validation gate**. This discipline enforces it as the state transitions for any Interface doc.

## Blocked, Waiting, and Watching semantics

Honest categorization. `[Ready]` means *I (the agent) know how to do this without further user involvement* — pure agent-actionable. Everything that fails the bar but isn't waiting on user input lands in one of three "not-actionable-right-now" buckets, distinguished by *what* would advance the row:

- **`[Blocked]`** — someone (or something) needs to act to unblock it.
- **`[Waiting]`** — no one needs to act; we're observing for an event we *want* to occur. Resolution = event happens.
- **`[Watching]`** — no one needs to act; we're observing for an event we *don't* want to occur (a shipped fix's recurrence). Resolution = event *doesn't* happen by the soak expiry.

The point of being honest is that a `[Ready]` count the user trusts is more valuable than a `[Ready]` count that has drifted into "items the agent has read."

### The self-unblock test — before ANY item rests as `[Blocked]` (load-bearing)

A blocker is real **only if it is outside the agent's control.** The four real blockers:
1. a pending **user** decision/answer (often better expressed as `[Questions]`),
2. an **external system** the agent can't make happen now — a remote host being reachable, a third-party API shipping, a CI run completing,
3. **another unfinished feature's** outcome (`[Blocked F<NNN>]` — and only while that `F<NNN>` is genuinely unfinished),
4. an explicit user **"do not build ahead of X"** directive.

Before leaving anything `[Blocked]`, ask: **"Can I unblock this myself?"** If the "blocker" is **work the agent could just do** — *a script not yet written, a spec/doc not yet authored, a sweep / migration / rename not yet run, a refactor not yet done* — then it is **NOT blocked. It is unstarted `[Ready]`/`[Active]` work. Build it.** "I'd have to make X first" is never a blocker; X *is* the work.

This is the failure mode the test kills: items parked `[Blocked]` for months whose only "blocker" is that nobody wrote the obvious prerequisite — the agent chasing its tail instead of building the thing. (Canonical example: F156 sat `[Blocked]` because `audit-dispatch.py` "didn't exist" — but writing it was exactly the agent's job.) **When in doubt, it's Ready, not Blocked.** `/groom` applies this test on every pass: a `[Blocked]` row whose blocker is agent-doable gets rebracketed to `[Ready]` (or `[Active]`) and surfaced for the agent to land.

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
| `[Blocked F<NNN>]` | Nothing required — the `F<NNN>` link IS the description |
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

**Watching vs Waiting — polarity, not timing.** The two states look similar (both passive, both timed, both reconsidered at `/groom`) but they resolve on *opposite* outcomes. Picking the right one matters for the reconsideration prompt: "any recurrence since YYYY-MM-DD?" (Watching) versus "has the event happened yet?" (Waiting). Saying "Waiting" when you mean "Watching" sets up the wrong question for the user.

**Groom reconsideration.** All three states — `[Blocked]`, `[Waiting]`, `[Watching]` — are reconsidered at every `/groom` pass. Has the blocker resolved? Has the wait condition occurred? Has the soak expired without recurrence? Is the labeling still honest? There is no automated transition; the `/groom` bracket-reassessment pass IS the re-evaluation moment.

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
- **The render** (`queries-render.py`) renders the bracket as-is in the body — `**[Blocked]**`, `**[Blocked F015]**`, `**[Waiting]**`, `**[Waiting 1d]**`, `**[Watching]**`, `**[Watching 7d]**` — and counts the row under its **horizon H2 only** (Now/Next/Later). Blocked, Waiting, and Watching items contribute *zero* to the H1 banner's `Runnable` / `User` buckets (nor the `Verify` horizon count), and *zero* to the TAG cascade's U or A. **All three states are reconsidered every `/groom` pass** — that's the reconsideration's primary purpose. An anchor whose only items are Blocked / Waiting / Watching falls through to TAG `[G]` (groomable — user/time/soak needs to clear something) or `[]` (nothing actionable).
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
| Q.md status banner (render) | Reads state across all items and prints per-bucket counts; refreshed by every `state` mutation. |
| `/audit` | Generates new `[ ]` items from findings (no state advancement). |

## Mutation API — `state`

The canonical state editor for everything below the anchor level — backlog rows AND feature-doc Open Questions. All skills that advance, park, rebracket items, or manage Qs go through this script instead of editing the backlog or feature doc directly. **Full CLI spec:** [[DAS State]] (`~/.claude/skills/workflow/DAS State.md`).

**Path:** `~/.claude/skills/workflow/scripts/state` (skill-owned; no `~/bin/` dependency).

**Synopsis:**

```
state [-a/--anchor ANCHOR] <doc> <label> <verb> [flags] [< body]
```

- **`<doc>`** — `Backlog` (the anchor's backlog file), a wiki-name (case-insensitive basename match, anchor tree first then vault; ambiguity errors listing candidates), or a path to any `.md` doc.
- **`<label>`** — LETTERS+DIGITS (`F157`, `T8` on Backlog; `Q7`, `V3` on any doc) or LETTERS+`+` to auto-mint the next number (`F+`, `T+`, `Q+`, `V+` — mint is `define`-only).
- **`<verb>`** — `define` (create-or-replace whole body) | `set` (partial row update, Backlog-only) | `resolve` (move to the item's resolved home) | `remove` (soft-delete with audit trail).

`--anchor` accepts a path (folder containing `.anchor`) or a slug (`SKA`, `MUX`, …). If absent, the script walks `cwd` UP looking for `.anchor`. In skill templates we usually pass `--anchor {slug}` explicitly.

### Backlog rows — `state Backlog <F<n>|T<n>> <verb>`

| Verb | Form |
|---|---|
| `define` | `echo '- **F+ — TITLE** [STATUS] — BODY' \| state --anchor {slug} Backlog F+ define [--horizon HORIZON]` — create-or-replace the whole row; the body IS the complete row markdown (optionally followed by indented sub-bullets). `F+`/`T+` mints the next number (separate namespaces, zero-padded); an explicit `F<NNN>` replaces that row. Default horizon for a new row is `Now`. |
| `set` | `state --anchor {slug} Backlog F<NNN> set [--status STATUS] [--horizon HORIZON] [--title "TITLE"] [--body BODY] [--next "STEP"] [--verify "QUESTION"] [--why-user "SENTENCE"]` — partial update; omitted flags preserve current values. Entering Verify/Verify-by/Watching requires `--why-user` naming the human faculty (taste / preference / ratification / passive-use), and a mechanically-phrased Verify question is refused outright (F240 ownership gate; see [[DAS State]]). |
| `resolve` | `state --anchor {slug} Backlog F<NNN> resolve [--body "NOTE"]` — moves the row to `## Done` `[Done]`, appending `— resolved <date>: <note>` to the body. |
| `remove` | `state --anchor {slug} Backlog F<NNN> remove` — removes the row entirely (rare). |

Row shape produced:

```
- **<row-id> — <title>** [<status>] — <body> ^<row-id>
```

**Preserve-on-omit semantics.** On `set`, omitted flags preserve the current value. The common bracket-only transition:

```
state --anchor SKA Backlog F095 set --status Ready --next "the declared step"    # bracket + Next
state --anchor SKA Backlog F095 set --status Done --horizon Done                 # move to ## Done
state --anchor SKA Backlog F095 set --title "New Title"                          # rename
state --anchor SKA Backlog F095 set --body "Shipped 2026-06-15"                  # body only
```

### Doc queries — `state <doc> <Q<n>|V<n>> <verb>`

Any markdown doc can carry labeled queries — feature docs, PRDs, standalone design docs; a doc does not need to be a numbered feature.

| Verb | Form |
|---|---|
| `Q define` | `state --anchor {slug} "<doc>" Q+ define < q-body.md` — `Q+` mints the lowest unused Q-number; an explicit `Q<n>` create-or-replaces that Q (subsumes add + rewrite). Lands in `## Open Questions` (the first H2, below the H1). **The q-body must carry a `- **Damage:**` line** (first word ∈ `waste`/`priority`/`irreversible`/`locking`/`taste`/`other`; `waste`/`priority` auto-resolve on define and never surface — [[DAS ask-format]] § The Damage field). |
| `Q resolve` | `state --anchor {slug} "<doc>" Q<n> resolve --choice "(A)" [body source]` — migrates the Q to the bottom `## Resolved` H3. |
| `Q remove` | `state --anchor {slug} "<doc>" Q<n> remove --reason "..."` — migrates to `### Removed` H3 with audit trail. |
| `V define/resolve/remove` | same grammar with `V<n>`/`V+` — addressable verifications under the doc's `## Verifications` H2 (per F235, the doc is the verify home). |

The script enforces ask-format spec (block-IDs, Q-numbering, Phase 1/2/3 lifecycle, ≥2 labeled options + a `Recommendation:` line) at write time. Q-numbers are canonical (referenced by block-IDs and audit-q messages).

### Side effects

1. Mutates the target row in `{slug} Backlog.md` (`Backlog` target) or the doc's `## Open Questions` / `## Verifications` block (doc target).
2. Invokes `~/.claude/skills/audit/scripts/audit-q.py --scope backlog --anchor <slug> --fix` to refresh `~/ob/kmr/Q.md` (banner counts, status drift).
3. Appends one `[INFO]` entry to the per-anchor `{slug} Messages.md` and one to the global sentinel `~/.claude/state/agent-messages` (surfaced to the next agent on Stop hook).
4. For doc targets: also runs a lenient `audit-q --scope q --dry` as a post-condition. (The per-anchor `{slug} queries.md` page is a mechanical render — `queries-render.py` produces it from the backlog + feature-doc questions, refreshed through the `/ask` pipeline, per F231; it is not hand-authored.)

**Output:** stdout = one summary line naming the row-id/label and its new state. For mint operations (`F+`/`T+`/`Q+`/`V+`), the assigned label is in the output — parse it when the caller needs to reference the new item (e.g., `/feature` naming a new feature doc file).

**Discipline — skills MUST NOT edit backlog files or doc Open Questions directly.** All row creation, status changes, horizon moves, Q additions, and Q resolutions go through `state`. Direct edits bypass the Q.md refresh and the Messages notification, which silently breaks the cross-agent state-of-the-anchor surface. (Warden enforces this from the other side: `R-pathguard` denies backlog/queries hand-edits, and `R-state-region` reminds on hand-edits to any item-bearing doc's state-managed regions.)

The script is invoked via `Bash`:

```
echo '- **F+ — Title** [Designing] — → [[F095 — Title]]' | ~/.claude/skills/workflow/scripts/state --anchor SKA Backlog F+ define
```

**Minting flow** (when the caller needs the new F/T number — e.g., `/feature` naming a new feature doc file):

1. Invoke `Backlog F+ define` with the placeholder row (`- **F+ — Title** [Status]`).
2. Parse the assigned row-id from stdout — output line is `<slug>: added <row-id> in <horizon> [<status>]`. Extract the second word after `added`.
3. Use the parsed row-id downstream (feature doc filename, wiki-links, etc.).
4. If the caller needs to update the row body once downstream artifacts exist (e.g., after creating the feature doc, the row should include `→ [[F<NNN> — Title]]`), invoke `Backlog F<NNN> set --body "..."`.

### Legacy `backlog-edit.py`

`~/.claude/skills/workflow/scripts/backlog-edit.py` ships the F128-era positional CLI (`<slug> <horizon> <row-id> <status> [title] [body]` for rows, `-Q add|resolve|remove|rewrite` flag-mode for Qs). It remains functional during the migration window — both scripts coexist. New code should prefer `state` per the verb-first design (F129).

## Per-surface mappings

Each surface that uses workflow state cites this discipline and maps the canonical states onto its own structure.

### Backlog (`{slug} Backlog.md`)

Per `[[DAS Backlog]]`:

- Workflow state is shown via the `[Status]` square-bracket prefix in each bullet, OR implied by the bullet's H2 placement.
- H2 sections combine **horizon** (`## Now`, `## Next`, `## Later`) and **workflow state** (`## Active`, `## Ready`, `## Done`).
- Items in horizon H2s use `[Status]` brackets — typically `[ ]`, `[Designing]`, `[Questions]`, `[Blocked]`, `[Waiting]`, `[Watching]`, or `[Verify]`.
- Items in workflow-state H2s have their state implied by the H2 — the bracket is optional/redundant.
- **`[Verify]` is bracket-only — there is no `## Verify` H2.** Verify items stay in their horizon (typically `## Now`) with the `[Verify]` bracket. Rationale: verify is short-lived (waiting on user yes/no) and conceptually keeps the item in its horizon. The bracket alone carries the state, and the backlog-row description text becomes the verify-plan instructions for the user (consumed by the render, `queries-render.py`).
- The `## Legwork` H2 is a **category tag**, not a workflow state. Items in Legwork still have a state (Ready / Active / etc.), shown in their bracket.

### Roadmap (`{slug} Roadmap.md`)

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

These are PRD-doc-internal; they don't appear in the backlog or the status banner.

## Active-work invariant

> **Every feature doc representing active work is reachable in ≤2 clicks from EITHER `{slug} Backlog.md` OR `{slug} Roadmap.md`. Iced feature docs are reachable from `{slug} Icebox.md`. Anything in `{slug} Features/` not reachable from one of those three is an *orphan* and a violation.**

This is the structural sharpening of the per-surface mappings above: those say *what state items are in*; this says *where the items must live to be tracked*.

### Three surfaces, parallel namespaces

| Surface | File | Namespace | Role |
|---|---|---|---|
| **Backlog** | `{slug} Backlog.md` | F-numbers (`F1`, `F2`, ...) — monotonic-forever, never recycled per `[[DAS Backlog]]` § Numbering policy | Active to-do list |
| **Roadmap** | `{slug} Roadmap.md` | M-numbers (`M1`, `M1.2`, `M1.2.3` — hierarchical) | Milestone-level active work |
| **Icebox** | `{slug} Icebox.md` | Shares F-number namespace with backlog | Parked / frozen — explicitly inactive but tracked |

**F and M are distinct namespaces.** A backlog row never collides with a roadmap milestone — `F5` and `M5` can coexist. F-numbers are unique across backlog AND icebox: an item moving between them keeps its F-number; thawing an iced item brings the same F-number back. M-numbers belong only to the roadmap.

**Letter prefix choice — M not R:** M (for Milestone) parses cleanly in DMUX dictation; R does not without a leading "letter" qualifier. M is also the de-facto convention across existing roadmaps (HA, MUX, DMUX, DKT).

### When does a milestone need a feature doc?

- **Top-level milestones (M1, M2, ...) ALWAYS have a feature doc** at `Features/M{n} — {Name}.md`. Even if the user-facing/system-facing spec lives elsewhere (PRD, system design, user docs), the feature doc still exists as the home for **meta-discussion and "what's the work to do" notes** that don't belong in shipping documentation.
- **Sub-milestones (M1.2, M1.2.3) get feature docs only when needed** — when there's real meta or work-breakdown to capture. Otherwise the milestone bullet in the roadmap is enough. Per-sub-milestone judgment call.

### Content philosophy — feature doc vs spec docs

The feature doc is **work-TBD + meta-discussion**:
- *Why* decisions were made (trade-offs, alternatives, rationale).
- *What work needs to be done* (implementation plan, acceptance criteria, sub-tasks).
- Open questions during design (per `[[SKA queries]]`).

The user-facing and system-facing **spec content** (API surfaces, command syntax, screens, architecture, data models) lives in:
- **User docs** (`{slug} User/`) — what the user sees / types / configures.
- **System Design** / **PRD** (`{slug} Plan/`) — what the system does / how it's built.
- **Module docs** (`{slug} Dev/`) — per-component developer documentation.

Why split? **No duplication** — if the API spec lives in both the feature doc and `{slug} User/CLI.md`, the two will drift; one source of truth. **The feature doc is ephemeral, the spec is durable** — once a milestone ships, the feature doc's "why" still has historical value, but its "what" should be the system docs (which keep getting updated). Keeping the "what" out of the feature doc forces the agent to write the spec into the durable doc the first time, instead of writing it twice (or worse, leaving the durable doc stale).

### Icebox interaction

The icebox is a **sanctioned exception** to the "active" part of the invariant. Items in `{slug} Icebox.md` are not active by definition.

1. **F-number namespace is shared across backlog AND icebox** — no F-number collisions; an item moving between the two keeps its F-number.
2. **`/groom` ignores the icebox by default.** Default scope = backlog only. Iced items don't appear in the body of `/groom`'s output.
3. **Counts surface the icebox total.** The render (status banner) shows `(Icebox: N)` in the count line — visibility without competing for attention.
4. **Explicit invocation can target the icebox.** `/groom icebox`, `/groom F<n>` (where `F<n>` is iced) all work.
5. **Iced feature docs are NOT orphans.** A doc linked from `{slug} Icebox.md` satisfies the invariant.

### Enforcement

- **At creation time** — `feature/SKILL.md` step 1.5 mandates minting a backlog (or roadmap) row when a feature doc is created. The mint happens via `state Backlog F+ define` (see § Mutation API above); no `--orphan` flag, no convention-only escape hatch, no direct backlog edit.
- **Continuous** — `/audit structure` includes an orphan-check sub-audit: walks `{slug} Features/` and flags any feature doc not linked from backlog/roadmap/icebox.
- **One-time sweep at landing** — when this invariant first lands per anchor, run `/audit structure --orphan-sweep` to backfill rows for any pre-existing orphans.

## Horizons vs workflow states

These are **two independent axes**:

- **Horizon** — *when* the user wants the work to happen. Owned by `[[DAS Backlog]]`. Values: Now, Next, Later (plus Icebox outside the backlog).
- **Workflow state** — *whether* the work has progressed and how far. Owned by this discipline. Values: Unset, Designing, Blocked, Ready, Active, Verify, Done.

**Common conflation: "Now" vs "Active."** They look similar but mean different things.

- `Now` is a **scheduling intent**: "we want to pull this into action soon."
- `[Active]` is a **state**: "we have actually started and are working on it."

An item can sit in `## Now` for a while as `[Ready]` (we want to do it soon, haven't started yet). When work begins, it transitions to `[Active]` and typically **moves out of the horizon section into `## Active`** — because once active, the horizon question is moot.

Same for `[Verify]` and `[Done]`: those states have their own H2s. Horizon H2s are for **upcoming** work (pre-In-Progress); workflow-state H2s are for **active and finished** work.

## Anti-patterns

- **Inventing a new state name** instead of citing the canonical one. If your skill needs a state that isn't in the canonical graph, propose adding it here — don't fork.
- **Implicit state transitions.** Every state change should be driven by a named skill or trigger; "the agent decided" is not a transition.
- **Treating "Ready" loosely.** Ready means *the agent could complete this in this turn with zero further user interaction*. If the description says "likely superseded," "held as fallback," "in case X," "awaits natural recurrence," "revisit only if," "soaking," "burn-in," "watching for recurrence," "may need," "might want to," "probably," "possibly," "contingent on," "depends on whether" — it is **not Ready**. The honest bracket is `[Waiting]`, `[Watching]`, `[Blocked]` / `[Blocked F<NNN>]`, or `[Questions]`. See § Definition of Ready → The RIGHT NOW test for the full rule and rebracket discipline.
- **Lazy-Blocked / lazy-Waiting / lazy-Watching.** Labeling a row `[Blocked]`, `[Waiting]`, or `[Watching]` without a body that names the specific blocker / watched event / shipped change. The most common drift in this vocabulary — these brackets get used as thought-terminating labels ("not progressing, mark it Blocked, move on"). The required-description rule is the antidote: if you can't write an actor-and-action sentence (Blocked), an event/time sentence (Waiting), or a "this was changed; non-recurrence proves it held" sentence (Watching), the row isn't actually in that state. Also: **don't conflate Waiting and Watching** — they resolve on opposite outcomes (event-occurs vs event-doesn't-occur) and set up opposite reconsideration prompts.
- **Skipping `[Verify]`.** Implementations that go straight to Completed bypass the verification gate. `/finalize` enforces this; manual edits should respect it.
- **State drift between surfaces.** If a backlog item is `[Active]` but the feature doc Status says "Designing," one of them is wrong — the user shouldn't have to guess which.
- **Lazy-Blocked / lazy-Waiting.** Labeling a row `[Blocked]` or `[Waiting]` without a body that names the specific blocker or watched condition. The most common drift in this vocabulary — when "Blocked" gets used as a thought-terminating label ("not progressing, mark it Blocked, move on"). The required-description rule above is the antidote: if you can't write an actor-and-action sentence (Blocked) or an event/time sentence (Waiting), the row isn't actually in that state.
