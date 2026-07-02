---
description: "F217 — Conversation-content gating — rules on what the agent said and didn't say"
---

# [[Warden]] · F217 — Conversation-content gating — rules on what the agent said and didn't say

## Summary

Beyond the agent's generic *state* ([[F216 — Agent-state model — sensing what the agent is doing|F216 — Agent-state model]]), some rules want to gate on **what the agent actually said — or didn't say — in the conversation**. For example: "whenever the agent asks the user *this kind* of question, surface guidance about how it's reasoning," or "if the agent claimed a task was done but never ran the test, flag it." F217 extends the observable surface from *state* to the **conversation transcript**, so an `if::` (or an `ask_oracle` over a turn) can condition on the content of a turn.

## Success Criteria

**Tier:** 2 (after F216) — depends on the agent-state plumbing and the `prompt:*` moments.
**Blocks next:** none.

**What done looks like.** A rule on `when:: prompt:stop` can read the **last turn's content** (what the agent said, the user's prior message, what was *absent*) and gate on it — directly in Python for simple cases, or via `ask_oracle` for judgment ("did the agent answer the user's actual question?"). The transcript slice is bounded (the current turn, not the whole history) and lazy.

**How it will be verified.** Fixture turns ([[F214 — Rule-system testing regime|F214]]): an agent message that asks a flagged kind of question → the rule fires; a turn whose ledger lacks a required command → the "didn't do" rule fires; a normal turn → silence. Loop fixture: a Stop-steer continuation does not re-fire the same rule.

## Design

### The `agent.turn` view

**`agent.turn`** joins the interpretation environment ([[Warden Semantics]] § The interpretation environment) as a **member of `agent`**, not a sibling top-level object *(revised 2026-07-02, user direction: the turn is an aspect of the agent)*. The top-level object surface stays at five, and the agent-rooted sugar that already existed (`agent.response`, `agent.tools_this_turn`) becomes plain intra-object aliasing rather than cross-object reach. The turn remains a **distinct lazy sub-object** rather than flattening into `agent`'s property set — `agent`'s own members are *interpreted state*; `agent.turn`'s are *raw content*, and that line is the design.

**Identity — which turn.** `agent.turn` binds to the agent's session (live: the session that produced the moment; audit: the session running the audit) and to **the turn the triggering moment belongs to**. At `prompt:stop` that is the just-ended turn, complete; at a mid-turn moment (`tool:post`, `write:*`) it is the in-flight turn so far — every member is *as of the triggering event*. The turn's id is the session's latest `prompt:submit` in the moment ledger; a Stop-steer continuation resumes **the same turn** (the agent continues without a new submit), which is exactly what loop-prevention keys on (§ Loop prevention).

**Members** — six, all content; text members are transcript-sourced, activity members are ledger-sourced:

| Member | What it is |
|---|---|
| `agent.turn.user_said` | the user message that opened the turn — text, capped |
| `agent.turn.agent_said` | the agent's visible words as of the triggering moment — the assistant text blocks joined; thinking and tool payloads excluded; capped. `agent.response` is its everyday alias |
| `agent.turn.text` | the whole turn flattened — user + agent text + one-line tool summaries; capped |
| `agent.turn.messages` | the turn's transcript records, structured — for the rare rule that needs more than the flattened text |
| `agent.turn.tools` | the tool invocations this turn — `(name, key input)` pairs from the moment ledger |
| `agent.turn.commands` | the Bash command lines this turn — sugar over `.tools` |

**No predicates on the turn** *(revised 2026-07-02)*: "did the turn end addressing a question" is `agent.is_asking`, on `agent` — interpretation lives with the state model, content lives here (§ Mechanical gating).

**Sources and rungs.** Text members parse the **transcript JSONL tail**, delimited by the ledger's `prompt:submit`/`prompt:stop` boundaries — the same tail read the F216 classifier makes, one read per pass, shared. Activity members read the **moment ledger** directly (rung R1), with a transcript fallback (the tool-use records) at R2/R3. At **R4** (no per-session mapping) the view is unresolvable: every member reads as its error value (`''` / `[]`), and reads never raise — the same error-channel contract as `agent.*`.

**Laziness.** An `agent.turn` (or `agent.response`) reference is statically visible in an `if::`/body, so the compiler marks **turn-bearing rules** at compile time. The view is built on the first `agent.turn.*` read of a pass and cached for the pass; a pass whose session sits at R4 skips turn-bearing rules wholesale. Rules that never read `turn` pay nothing.

**Cost bounds.** One transcript-tail read per pass (shared with the classifier); each text member is capped at **`TURN_CAP`** (an engine-config constant, default **16 KB**; truncation keeps head + tail around an elision mark, so both the opening claim and the closing question survive). The bound is the *current turn* — a deliberate privacy + cost line (Q2, resolved: v1 is current-turn only; a capped `agent.turn.prior(n)` arrives later when a real rule needs it).

### Mechanical gating — plain Python over the turn

The cheap tier is ordinary Python over the members — the condition language *is* Python, so there is no pattern DSL to learn:

- **Said-checks** — `re.search(r'(?i)\ball tests pass\b', agent.response)`, `'?' in agent.response` (`agent.response` is the everyday alias of `agent.turn.agent_said`).
- **Did-checks** — absence of an *action* is read from the **ledger, not the prose**: `not any(c.startswith(('pytest', 'just test', 'cargo test')) for c in agent.turn.commands)`. The ledger is the truth about what the agent *did*; the text is only the truth about what it *said*. Structured absence ("finished without running the test") is therefore fully mechanical — the interesting judgment cases are the *semantic* absences (§ Judgment gating).
- **`agent.is_asking`** — the one shipped predicate, and it lives on `agent`, not the turn *(revised 2026-07-02)*: sugar for `agent.state == 'asking'`, whose classifier question-test is the last-non-code-paragraph heuristic (ends in `?`, or carries an options pattern — `(A)`/`(B)`, `Q<n>:`). One heuristic, one spelling — the state model and the content rules can never disagree about "is this a question." (Mid-turn, `state` reflects the last classification; content rules that care fire at `prompt:stop`, where the two coincide.)

The v1 pattern catalog — question-to-user, options menu, done-claim (`\b(done|complete|all tests pass)\b`), promise (`\b(I will|next I'll)\b`), missing-command — ships as **documented idioms in [[Warden Examples]]**, each a worked rule; the environment surface itself stays at the six members above (Q3, resolved: core stays minimal — a `convo` helpers module can ship later as an ordinary ruleset helper).

### Judgment gating — `ask_oracle` over the turn

The judgment tier reuses the existing verb unchanged — **`ask_oracle(prompt) → str`** ([[Warden Semantics]] § Verbs) — with the turn slice merged into the prompt by the rule author. F217 adds the *idiom*, the *paths*, and the *budget*, not a new API:

- **Binary-verdict idiom.** Instruct the oracle to reply exactly `yes` or `no` ("reply `yes` only if confident"), gate on the sentinel in code, and let the **rule author write the `tell`** the agent sees. A malformed or empty reply is treated as `no` — the rule stays silent. Confidence lives in the prompt's instruction, keeping the verb's contract (`→ str`) frozen.
- **Audit path — the oracle's home.** The pass blocks on the `claude -p` Sonnet call (seconds, ~1¢, [[Warden Runtime]] § LLM judgments), and the verdict is **cached by `(rule, hash of the oracle prompt)`** — a re-audit of an unchanged turn reuses it.
- **Live path — delegated.** The hot hook cannot block on a seconds-grade call, so a live judgment at `prompt:stop` is **delegated to the running agent as a steer**: the rule prefilters mechanically, then `tell`s an author-written self-check directive — the agent already holds the full turn context and is the cheapest competent judge. (Q1, resolved: this delegated form *is* v1; an async oracle with next-moment delivery may arrive later as M8-class daemon machinery.)
- **Prefilter discipline.** Every oracle-bearing content rule carries a **mechanical `if:: `prefilter** over the turn (a regex, `agent.is_asking`, a `commands` check) that passes on the order of ~10% of turns — that is the budget line that makes "oracle checks ~10% of responses" a property of the ruleset, and it is lintable (a future warden-audit rule can flag an unprefiltered oracle rule).
- **Failure semantics.** Oracle unavailable, timed out, or malformed → **the rule does not fire** (conservative silence, matching the daemon's fail-open posture) — and under audit the report marks the verdict **unevaluated**, never *pass*, with any prior cached verdict persisting (the [[F215 — Re-evaluation economy — the significant-edit gate|F215]] rule that silence must not clear a standing finding).

### Loop prevention

Two walls, both daemon-side, keep content rules from feeding themselves:

1. **Oracle sessions are moment-silent.** The daemon spawns every oracle with **`WARDEN_ORACLE=1`** in its environment; the notifier exits immediately when the marker is set, so an oracle's own tool uses and turn boundaries never reach the ledger. The session registry additionally drops any session carrying the marker — oracle sessions never bind `agent` (nor its `.turn`) and never make rules candidates. Belt and braces on one invariant: *the judge is not an observed agent.*
2. **Once per `(rule, turn)`.** A `tell` at `prompt:stop` re-invokes the agent, and the continuation ends in another `prompt:stop` on the **same turn id** (no new `prompt:submit`). The daemon records each content rule's firing against the turn id and suppresses a re-fire — so a steer can extend the turn, and the extended turn cannot re-trigger the rule that steered it. Distinct rules still fire independently; a genuinely new turn resets the key.

The delegated self-check steer is additionally **terminal by construction** — its text is author-written (the oracle idiom: the oracle judges, the author speaks), directing the agent to check-and-correct, never to re-invoke Warden.

### Example rules

Three rules this feature enables, in the [[Warden Rule]] shape (the `R-ex` fixture namespace, joining F216's `R-ex-10`).

#### RULE R-ex-11 — question-kind steer

description:: when the agent ends a turn asking a low-stakes ordering question, steer it to decide itself
when:: `prompt:stop`
if:: `agent.is_asking and re.search(r'(?i)\b(should i|which order|do you want me to)\b', agent.response)`

Low-stakes ordering / batching choices are yours to make — pick a sensible order, announce it, and proceed; don't end the turn on this question.

#### RULE R-ex-12 — done-claim without a test run

description:: flag a completion claim in a turn whose ledger shows no test command
when:: `prompt:stop`
if:: `re.search(r'(?i)\b(all tests pass|task (is )?done|complete[d]?)\b', agent.response) and not any(c.startswith(('pytest', 'just test', 'cargo test')) for c in agent.turn.commands)`

You claimed completion but this turn ran no test command — run the test suite and report the actual result before landing.

#### RULE R-ex-13 — did the agent answer the actual question (delegated judgment)

description:: when the user asked something and the agent's reply may have sidestepped it, prompt a self-check
when:: `prompt:stop`
if:: `'?' in agent.turn.user_said and not agent.is_asking`

Re-read the user's question in this turn. If your reply addressed something adjacent rather than what was actually asked, answer the actual question now.

*(R-ex-13 is the delegated live form; its audit twin replaces the bare-prose body with an `ask_oracle` over `agent.turn.user_said` + `agent.turn.agent_said`, sentinel-gated per § Judgment gating.)*

### Dependency ledger

| Piece | Waits on |
|---|---|
| The `agent.turn` view spec — members, identity, error-value contract, `TURN_CAP` | nothing — frozen here |
| `agent.turn` joining the frozen `agent` property set | M0 ratification — a nested-member addition, no new top-level object; no open F209/F210 question bears on it (`prompt:stop` is already canonical, `if::` is already Python) |
| `Turn` class, transcript-tail parser, turn-bearing compiler mark | M2 ([[F212 — Python reference implementation|F212]]) — builds on F216's session registry + moment ledger |
| `agent.is_asking`'s question heuristic | F216 classifier implementation — one shared predicate with its Q3 test |
| Oracle spawn marker (`WARDEN_ORACLE`), `(rule, turn)` dedup | M2 daemon features |
| Fixture turns + loop fixture | [[F214 — Rule-system testing regime|F214]] (M3) |
| Async live oracle (post-v1 option per Q1) | M8-class daemon machinery — pending-verdict queue + next-moment delivery |

## Resolved

- **Q1 — Live-path judgment (user, 2026-07-02): (A) delegate-to-agent for v1.** A live content judgment is a mechanical prefilter + an author-written self-check steer — the agent, already holding the full turn context, is the judge (matches the [[Warden Runtime]] live-path doctrine: no blocking model call on the hot path). The async oracle (B) can arrive later as pure M8-class daemon machinery without touching the rule language. ^F217-Q1
- **Q2 — Prior-turn window (user, 2026-07-02): (A) current-turn only in v1.** `agent.turn.prior(n)` arrives when a real rule needs it — purely additive; shipping it unused widens the privacy/cost bound for nothing. ^F217-Q2
- **Q3 — Shipped predicate surface (user, 2026-07-02): (A) core stays minimal.** `agent.is_asking` is the only shipped predicate; every other pattern is plain `re` in the rule, with the catalog as worked idioms in [[Warden Examples]]. A `convo` helpers module remains possible later as an ordinary ruleset helper without reopening the freeze. ^F217-Q3
- **Top-level `turn` (user, 2026-07-02)** — nested: the view is **`agent.turn`**, a member of `agent` — the turn is an aspect of the agent, not a sibling top-level object. Kept as a distinct lazy sub-object rather than flattened into `agent` (also user's call): `agent`'s members are interpreted state, `agent.turn`'s are raw content. `agent.response` stays as the everyday alias of `agent.turn.agent_said`. § The `agent.turn` view.
- **Where the asking predicate lives (2026-07-02)** — on `agent` only: `agent.is_asking` is the single spelling of "did the turn end addressing a question"; the former `turn.asks_question` member is dropped (six content members remain). The last-paragraph heuristic stays one shared implementation behind the F216 classifier and this predicate — resolving the R-ex-11 confusion where `agent.is_asking` and `turn.agent_said` mixed two objects in one condition. § Mechanical gating.
- **Transcript access (prior Q1)** — the **transcript JSONL tail, delimited by the moment ledger's turn boundaries**, is the content source; the tmux pane contributes rendered state only (F216's ladder) and is never a content source. History in scope: the current turn. § The `agent.turn` view.
- **Privacy/cost bound (prior Q2)** — current turn only, each text member capped at `TURN_CAP` (default 16 KB, head+tail-preserving truncation); one shared transcript read per pass. Opt-in prior turns is the Q2 fork below.
- **Overlap with `ask_oracle` on responses (prior Q3)** — codified as the judgment tier: the "oracle checks ~10% of responses" pattern becomes declarative via the **prefilter discipline** (mechanical `if::` gate in front of every oracle rule), with the audit path blocking-and-cached and the live path delegated to the agent. § Judgment gating.

## Status

**Designed 2026-07-01; user-endorsed same day** — in the [[Warden Consumers]] review the user promoted conversation gating to the confident set (*"quite important"*), independently sketching exactly this design: a lazily-computed last-response string (`agent.response` in their words — realized as `agent.turn.agent_said`, with `agent.response` as its everyday alias, accepted 2026-07-02, in [[Warden Semantics]] § `agent`), regex over it inside `if::`, and the gate-before-tell economy ("we don't tell the agent this unless there's evidence from the conversation" — the § Judgment gating prefilter discipline). Rules over **user** content were raised as plausible ("I'm not sure, but those things should be made visible") — `turn.user_said` provides it. The design itself: the `agent.turn` view (members, turn identity, rung/error-value contract, `TURN_CAP` bound), the two gating tiers (mechanical Python with the shared question heuristic behind `agent.is_asking`; `ask_oracle` with the binary-verdict idiom, prefilter discipline, and fail-silent semantics), loop prevention (moment-silent oracles + once-per-`(rule, turn)`), three example rules, and the dependency ledger are concrete. All three forks resolved 2026-07-02 (user accepted the filed Leans: delegated self-check live path; current-turn-only v1; minimal predicate surface — § Resolved Q1–Q3). Not built — the `Turn` class and daemon features implement inside M2 ([[F212 — Python reference implementation|F212]]) on F216's plumbing; fixtures land with [[F214 — Rule-system testing regime|F214]]. **Revised 2026-07-02 (user design review):** `turn` nested under `agent` as `agent.turn` (an aspect of the agent, not a top-level object; still a distinct sub-object, not flattened), and `asks_question` dropped from the turn — `agent.is_asking` is the one asking predicate. Propagated: [[Warden Semantics]]' environment table + § `agent` updated.
