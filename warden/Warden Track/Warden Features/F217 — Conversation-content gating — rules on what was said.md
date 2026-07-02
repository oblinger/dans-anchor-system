---
description: "F217 — Conversation-content gating — rules on what the agent said and didn't say"
---

# [[Warden]] · F217 — Conversation-content gating — rules on what the agent said and didn't say

## Summary

Beyond the agent's generic *state* ([[F216 — Agent-state model]]), some rules want to gate on **what the agent actually said — or didn't say — in the conversation**. For example: "whenever the agent asks the user *this kind* of question, surface guidance about how it's reasoning," or "if the agent claimed a task was done but never ran the test, flag it." F217 extends the observable surface from *state* to the **conversation transcript**, so an `if::` (or an `ask_oracle` over a turn) can condition on the content of a turn.

## Success Criteria

**Tier:** 2 (after F216) — depends on the agent-state plumbing and the `prompt:*` moments.
**Blocks next:** none.

**What done looks like.** A rule on `when:: prompt:stop` can read the **last turn's content** (what the agent said, the user's prior message, what was *absent*) and gate on it — directly in Python for simple cases, or via `ask_oracle` for judgment ("did the agent answer the user's actual question?"). The transcript slice is bounded (the current turn, not the whole history) and lazy.

**How it will be verified.** Fixture turns ([[F214 — Rule-system testing regime|F214]]): an agent message that asks a flagged kind of question → the rule fires; a turn whose ledger lacks a required command → the "didn't do" rule fires; a normal turn → silence. Loop fixture: a Stop-steer continuation does not re-fire the same rule.

## Design

### The `turn` view

**`turn`** joins the interpretation environment ([[Warden Semantics]] § The interpretation environment) beside `agent` — the bounded, lazy view of the conversation turn containing the triggering moment.

**Identity — which turn.** `turn` binds to the same session as `agent` (live: the session that produced the moment; audit: the session running the audit) and to **the turn the triggering moment belongs to**. At `prompt:stop` that is the just-ended turn, complete; at a mid-turn moment (`tool:post`, `write:*`) it is the in-flight turn so far — every member is *as of the triggering event*. The turn's id is the session's latest `prompt:submit` in the moment ledger; a Stop-steer continuation resumes **the same turn** (the agent continues without a new submit), which is exactly what loop-prevention keys on (§ Loop prevention).

**Members** — text members are transcript-sourced; activity members are ledger-sourced:

| Member | What it is |
|---|---|
| `turn.user_said` | the user message that opened the turn — text, capped |
| `turn.agent_said` | the agent's visible words as of the triggering moment — the assistant text blocks joined; thinking and tool payloads excluded; capped |
| `turn.text` | the whole turn flattened — user + agent text + one-line tool summaries; capped |
| `turn.messages` | the turn's transcript records, structured — for the rare rule that needs more than the flattened text |
| `turn.tools` | the tool invocations this turn — `(name, key input)` pairs from the moment ledger |
| `turn.commands` | the Bash command lines this turn — sugar over `.tools` |
| `turn.asks_question` | does the turn end addressing a question to the user — the F216 Q3 heuristic as a property (§ Mechanical gating) |

**Sources and rungs.** Text members parse the **transcript JSONL tail**, delimited by the ledger's `prompt:submit`/`prompt:stop` boundaries — the same tail read the F216 classifier makes, one read per pass, shared. Activity members read the **moment ledger** directly (rung R1), with a transcript fallback (the tool-use records) at R2/R3. At **R4** (no per-session mapping) the view is unresolvable: every member reads as its error value (`''` / `[]` / `False`), and reads never raise — the same error-channel contract as `agent.*`.

**Laziness.** A `turn` reference is statically visible in an `if::`/body, so the compiler marks **turn-bearing rules** at compile time. The view is built on the first `turn.*` read of a pass and cached for the pass; a pass whose session sits at R4 skips turn-bearing rules wholesale. Rules that never read `turn` pay nothing.

**Cost bounds.** One transcript-tail read per pass (shared with the classifier); each text member is capped at **`TURN_CAP`** (an engine-config constant, default **16 KB**; truncation keeps head + tail around an elision mark, so both the opening claim and the closing question survive). The bound is the *current turn* — a deliberate privacy + cost line; reaching further back is the § Open Questions Q2 fork.

### Mechanical gating — plain Python over the turn

The cheap tier is ordinary Python over the members — the condition language *is* Python, so there is no pattern DSL to learn:

- **Said-checks** — `re.search(r'(?i)\ball tests pass\b', turn.agent_said)`, `'?' in turn.agent_said`.
- **Did-checks** — absence of an *action* is read from the **ledger, not the prose**: `not any(c.startswith(('pytest', 'just test', 'cargo test')) for c in turn.commands)`. The ledger is the truth about what the agent *did*; the text is only the truth about what it *said*. Structured absence ("finished without running the test") is therefore fully mechanical — the interesting judgment cases are the *semantic* absences (§ Judgment gating).
- **`turn.asks_question`** — the one shipped predicate: last non-code paragraph of `agent_said` ends in `?`, or carries an options pattern (`(A)`/`(B)`, `Q<n>:`). This is **the same implementation** the F216 classifier's Q3 test calls — one heuristic, two consumers, so the state model and the content rules can never disagree about "is this a question."

The v1 pattern catalog — question-to-user, options menu, done-claim (`\b(done|complete|all tests pass)\b`), promise (`\b(I will|next I'll)\b`), missing-command — ships as **documented idioms in [[Warden Examples]]**, each a worked rule; the environment surface itself stays at the seven members above (fork on growing it: § Open Questions Q3).

### Judgment gating — `ask_oracle` over the turn

The judgment tier reuses the existing verb unchanged — **`ask_oracle(prompt) → str`** ([[Warden Semantics]] § Verbs) — with the turn slice merged into the prompt by the rule author. F217 adds the *idiom*, the *paths*, and the *budget*, not a new API:

- **Binary-verdict idiom.** Instruct the oracle to reply exactly `yes` or `no` ("reply `yes` only if confident"), gate on the sentinel in code, and let the **rule author write the `tell`** the agent sees. A malformed or empty reply is treated as `no` — the rule stays silent. Confidence lives in the prompt's instruction, keeping the verb's contract (`→ str`) frozen.
- **Audit path — the oracle's home.** The pass blocks on the `claude -p` Sonnet call (seconds, ~1¢, [[Warden Runtime]] § LLM judgments), and the verdict is **cached by `(rule, hash of the oracle prompt)`** — a re-audit of an unchanged turn reuses it.
- **Live path — delegated.** The hot hook cannot block on a seconds-grade call, so a live judgment at `prompt:stop` is **delegated to the running agent as a steer**: the rule prefilters mechanically, then `tell`s an author-written self-check directive — the agent already holds the full turn context and is the cheapest competent judge. (Whether an *async* oracle with next-moment delivery also ships is the § Open Questions Q1 fork.)
- **Prefilter discipline.** Every oracle-bearing content rule carries a **mechanical `if:: `prefilter** over the turn (a regex, `turn.asks_question`, a `commands` check) that passes on the order of ~10% of turns — that is the budget line that makes "oracle checks ~10% of responses" a property of the ruleset, and it is lintable (a future warden-audit rule can flag an unprefiltered oracle rule).
- **Failure semantics.** Oracle unavailable, timed out, or malformed → **the rule does not fire** (conservative silence, matching the daemon's fail-open posture) — and under audit the report marks the verdict **unevaluated**, never *pass*, with any prior cached verdict persisting (the [[F215 — Re-evaluation economy — the significant-edit gate|F215]] rule that silence must not clear a standing finding).

### Loop prevention

Two walls, both daemon-side, keep content rules from feeding themselves:

1. **Oracle sessions are moment-silent.** The daemon spawns every oracle with **`WARDEN_ORACLE=1`** in its environment; the notifier exits immediately when the marker is set, so an oracle's own tool uses and turn boundaries never reach the ledger. The session registry additionally drops any session carrying the marker — oracle sessions never bind `agent`/`turn` and never make rules candidates. Belt and braces on one invariant: *the judge is not an observed agent.*
2. **Once per `(rule, turn)`.** A `tell` at `prompt:stop` re-invokes the agent, and the continuation ends in another `prompt:stop` on the **same turn id** (no new `prompt:submit`). The daemon records each content rule's firing against the turn id and suppresses a re-fire — so a steer can extend the turn, and the extended turn cannot re-trigger the rule that steered it. Distinct rules still fire independently; a genuinely new turn resets the key.

The delegated self-check steer is additionally **terminal by construction** — its text is author-written (the oracle idiom: the oracle judges, the author speaks), directing the agent to check-and-correct, never to re-invoke Warden.

### Example rules

Three rules this feature enables, in the [[Warden Rule]] shape (the `R-ex` fixture namespace, joining F216's `R-ex-10`).

#### RULE R-ex-11 — question-kind steer

description:: when the agent ends a turn asking a low-stakes ordering question, steer it to decide itself
when:: `prompt:stop`
if:: `agent.is_asking and re.search(r'(?i)\b(should i|which order|do you want me to)\b', turn.agent_said)`

Low-stakes ordering / batching choices are yours to make — pick a sensible order, announce it, and proceed; don't end the turn on this question.

#### RULE R-ex-12 — done-claim without a test run

description:: flag a completion claim in a turn whose ledger shows no test command
when:: `prompt:stop`
if:: `re.search(r'(?i)\b(all tests pass|task (is )?done|complete[d]?)\b', turn.agent_said) and not any(c.startswith(('pytest', 'just test', 'cargo test')) for c in turn.commands)`

You claimed completion but this turn ran no test command — run the test suite and report the actual result before landing.

#### RULE R-ex-13 — did the agent answer the actual question (delegated judgment)

description:: when the user asked something and the agent's reply may have sidestepped it, prompt a self-check
when:: `prompt:stop`
if:: `'?' in turn.user_said and not agent.is_asking`

Re-read the user's question in this turn. If your reply addressed something adjacent rather than what was actually asked, answer the actual question now.

*(R-ex-13 is the delegated live form; its audit twin replaces the bare-prose body with an `ask_oracle` over `turn.user_said` + `turn.agent_said`, sentinel-gated per § Judgment gating.)*

### Dependency ledger

| Piece | Waits on |
|---|---|
| The `turn` view spec — members, identity, error-value contract, `TURN_CAP` | nothing — frozen here |
| `turn` joining the frozen interpretation-environment table | M0 ratification — a one-row surface addition; no open F209/F210 question bears on it (`prompt:stop` is already canonical, `if::` is already Python) |
| `Turn` class, transcript-tail parser, turn-bearing compiler mark | M2 ([[F212 — Python reference implementation|F212]]) — builds on F216's session registry + moment ledger |
| `turn.asks_question` | F216 classifier implementation — one shared predicate with its Q3 test |
| Oracle spawn marker (`WARDEN_ORACLE`), `(rule, turn)` dedup | M2 daemon features |
| Fixture turns + loop fixture | [[F214 — Rule-system testing regime|F214]] (M3) |
| Async live oracle (if chosen at Q1) | M8-class daemon machinery — pending-verdict queue + next-moment delivery |

## Resolved

- **Transcript access (prior Q1)** — the **transcript JSONL tail, delimited by the moment ledger's turn boundaries**, is the content source; the tmux pane contributes rendered state only (F216's ladder) and is never a content source. History in scope: the current turn. § The `turn` view.
- **Privacy/cost bound (prior Q2)** — current turn only, each text member capped at `TURN_CAP` (default 16 KB, head+tail-preserving truncation); one shared transcript read per pass. Opt-in prior turns is the Q2 fork below.
- **Overlap with `ask_oracle` on responses (prior Q3)** — codified as the judgment tier: the "oracle checks ~10% of responses" pattern becomes declarative via the **prefilter discipline** (mechanical `if::` gate in front of every oracle rule), with the audit path blocking-and-cached and the live path delegated to the agent. § Judgment gating.

## Open Questions

### Q1 — Live-path judgment: delegated self-check or async oracle? ^F217-Q1

The hot hook can't block on a seconds-grade oracle, so a live content judgment needs one of two shapes.

- **(A)** Delegate-to-agent — the rule prefilters mechanically, then `tell`s an author-written self-check directive; the agent, already holding the full context, is the judge. Zero added latency and zero new machinery; costs main-model tokens and trusts the agent to self-grade.
- **(B)** Async oracle — the daemon fires `claude -p` in the background, holds the verdict, and delivers the steer at the session's next moment. Independent judge; adds a pending-verdict queue and the steer lands one turn late.
- **(C)** Both — (A) as the idiom default, (B) opt-in per rule for judgments that need an independent grader.
- **Recommendation:** Lean (A) for v1 — it matches the live-path doctrine already fixed in [[Warden Runtime]] (no blocking model call on the hot path; delegate to the agent), and (B) can arrive later as pure daemon machinery (M8-class) without touching the rule language.

### Q2 — Prior-turn window: ship `turn.prior(n)` in v1? ^F217-Q2

The Summary promises an opt-in reach to a few prior turns; the shared transcript tail makes it cheap to build, but it widens the privacy/cost bound.

- **(A)** v1 is current-turn only — `turn.prior` arrives when a real rule needs it.
- **(B)** v1 ships `turn.prior(n)`, capped at an engine constant (n ≤ 5), each prior turn a `Turn` under the same `TURN_CAP`.
- **Recommendation:** Lean (A) — the v1 pattern catalog and all three example rules read only the current turn, and adding a capped `prior` later is purely additive; shipping it unused widens the bound for nothing.

### Q3 — Shipped predicate surface: one core property or a pattern library? ^F217-Q3

How much of the pattern catalog hardens into the frozen environment surface?

- **(A)** Core stays minimal — `turn.asks_question` only (forced into core by sharing with the F216 classifier); every other pattern is plain `re` in the rule, with the catalog as worked idioms in [[Warden Examples]].
- **(B)** A shipped `convo` helpers module (`helpers:: convo`) carrying the library (`convo.claims_done(turn)`, `convo.options_menu(turn)`), versioned with the engine.
- **Recommendation:** Lean (A) — the environment table is the frozen thing, and a pattern library can ship later as an ordinary ruleset helper module without reopening the freeze; (B) becomes attractive only if the same regexes start getting copy-pasted across many rulesets.

## Status

**Designed 2026-07-01** — the `turn` view (members, turn identity, rung/error-value contract, `TURN_CAP` bound), the two gating tiers (mechanical Python with the shared `asks_question` predicate; `ask_oracle` with the binary-verdict idiom, prefilter discipline, and fail-silent semantics), loop prevention (moment-silent oracles + once-per-`(rule, turn)`), three example rules, and the dependency ledger are concrete. Three forks filed (§ Open Questions). Not built — the `Turn` class and daemon features implement inside M2 ([[F212 — Python reference implementation|F212]]) on F216's plumbing; fixtures land with [[F214 — Rule-system testing regime|F214]]. Pending propagation on acceptance: the `turn` row joins the interpretation-environment table in [[Warden Semantics]].
