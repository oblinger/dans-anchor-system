---
description: "F216 — Agent-state model — sensing what the agent is doing"
---

# [[Warden]] · F216 — Agent-state model — sensing what the agent is doing

## Summary

Rules can sense the **agent itself** via the `agent` object in the interpretation environment ([[Warden Semantics]] § The interpretation environment) — `agent.state` (`working` / `landed` / `asking` / `idle`), `agent.skill`, `agent.is_asking`. This lets a rule fire at a turn boundary (`when:: prompt:stop`) and react to *how the turn ended*. F216 designs **how that state is actually determined**, which is non-trivial: it requires reasoning about the agent's recent activity, not reading a single flag.

**The governing frame (user, 2026-07-01): the state model answers "what is the agent doing *right now*."** Is it thinking? Waiting for the user to type? And if waiting — did it just ask a question, either through the harness's multi-choice dialog (AskUserQuestion) or in plain text (detectable by cheap heuristics — a question mark, an options pattern — no LLM call)? Did it land clean, or stop with work still open (the harness task list tells)? It is explicitly **not** about the queue of questions an agent has raised over time — `{NAME} queries.md` is *anchor* state, reachable via `anchor.doc(…)`, never an `agent.state` signal.

## Success Criteria

**Tier:** 1 (design) — powers `agent.*` in the environment; rules that read it can't ship until this does.
**Blocks next:** [[F217 — Conversation-content gating — rules on what was said|F217]] (which extends observation from *state* to *transcript content*).

**What done looks like.** Given a live agent session, the daemon can answer `agent.state` accurately for the common cases: actively working (a task/skill in flight), landed (a clean turn end), asking (the turn ended addressing a question — dialog up or closing text asks), idle. `agent.skill` reports the running skill. The classifier is lazy + cached per pass (one read, shared across rules).

**How it will be verified.** Scripted scenarios that drive an agent into each state (mid-task, post-`/land`, post-`/query`, idle), asserting `agent.state` matches; a fixture rule (`R-ex-10`) fires its `tell` only in the `asking` state.

## Design

### The states — a closed set of five

`agent.state` is one of **five strings** — the four live states plus the honest error value — with a sixth, `paused`, *(accepted 2026-07-02)* splitting "stopped with open work" out of `landed`. The set is **closed**: a rule can exhaustively match on it, and a read **never raises** — when no signal rung can answer confidently, the value is `unknown`.

| State | Meaning | Entered on | Left on |
|---|---|---|---|
| `working` | the agent holds control — a turn is in flight (model thinking, tool calls, a skill mid-run) | `prompt:submit`, or any tool/skill moment after the last turn end | a turn boundary, or liveness failure |
| `asking` | control is with the user **and the turn just ended addressing a question to them** — a harness dialog is up, or the closing text asks | `prompt:stop` with the pending-question predicate **true** | the user replies (`prompt:submit` → `working`) |
| `landed` | control is with the user, nothing pending — the turn ended clean | `prompt:stop` with the predicate **false** *(and no open tasks — see `paused`)* | next `prompt:submit`, or quiet ≥ `T_idle` → `idle` |
| `paused` | control is with the user, no question pending, **but open work remains** — the harness task list still holds open items (the "stopped but not finished" the user named) | `prompt:stop`, predicate false, open tasks > 0 | next `prompt:submit`; tasks all closing re-reads as `landed` |
| `idle` | no live activity — a long-quiet clean end, or the session is over | `landed` + quiet ≥ `T_idle`; `session:stop`; process gone | next `prompt:submit` / `session:start` |
| `unknown` | the bound session can't be classified at the available signal rung | fallback rung R4, or a liveness ambiguity (§ Debounce) | a better signal arriving |

**Transition semantics** (the asymmetries are the design):

- **Entering `working` is instant** — one `prompt:submit` or one tool moment flips it; there is no debounce on the way in.
- **Leaving `working` requires a boundary, never silence.** A long `Bash` call or a long model think emits no moments for minutes; mid-turn quiet is still `working`. Only `prompt:stop`, `session:stop`, or a liveness failure ends it.
- **`asking` is sticky.** A pending question does not decay on a timer — an unanswered question at hour three is exactly as pending as at minute one. It clears when the user answers (`prompt:submit`); how *long* it has been pending is readable as `agent.state_seconds`, so a rule conditions on elapsed time instead of the state decaying.
- **`landed` decays to `idle`** after a quiet window `T_idle` (default **10 min**, an engine-config constant — not per-rule surface). `landed` is the *instantaneous* "just ended clean"; `idle` is the *durable* "nothing happening."
- **Session end is `idle`.** `agent.*` describes a *running* agent (Q2 resolution, 2026-07-01); a rule that cares about a dead session's leftover queue reads `anchor.doc("{NAME} queries.md")` directly.
- `agent.is_asking` is sugar for `agent.state == 'asking'`, unchanged from [[Warden Semantics]].

### The signal inventory

What the daemon can actually observe, per environment. Ordered by trust.

| Signal | What it carries | Trust | Latency | Available when |
|---|---|---|---|---|
| **Moment ledger** — the daemon's own event stream | every hook moment ([[Warden Events]]): `prompt:submit/stop`, `tool:pre/post`, `skill:pre/post`, `session:*`, each timestamped per session | exact — structured events from the source | none — current up to the triggering event | hooks wired for the session (always true at live rule-fire time) |
| **Transcript JSONL** — `transcript_path` from the hook payload | the structured message stream: the last agent message, Skill/Task invocations, turn boundaries | high — Claude Code's own record | flush lag (sub-second to seconds) | any Claude Code session the daemon can map |
| **tmux pane** — `capture-pane` + pane title | the *rendered* state: input prompt idle vs busy, the running command, the last output, a **permission dialog pending** (which reaches neither hooks nor transcript) | medium — text of a render, parsed heuristically | ~instant | the session runs in tmux and the pane id is registered |
| **`{NAME} queries.md`** | the durable pending-question queue for the cwd anchor — **anchor state, not an `agent.state` signal** (user 2026-07-01); rules read it via `anchor.doc(…)` | high for *queue* state; says nothing about right-now | file-fresh | the anchor exists (vault-wide convention) |
| **Harness task list** | open/closed tasks per session — `TaskCreate`/`TaskUpdate` tool moments in the ledger (transcript records as fallback) | high — structured tool calls | none | hooks wired (transcript for out-of-band reads) |
| **Process table** | is the session's `claude` process alive | exact, but liveness only | ~instant | always |
| **mtimes** — transcript file recency | coarse "something is happening" | low — activity, not meaning | write-flush | always |

**The session registry** is the plumbing under all of this: every hook payload carries `session_id`, `transcript_path`, and `cwd`, and the notifier forwards `$TMUX_PANE` from its inherited environment when present — so the daemon accumulates a per-session record `(session_id → transcript_path, cwd, pane_id, pid)` for free, from the first moment it sees. The **moment ledger** is a bounded in-memory ring per session (moments + timestamps); on daemon restart it is rebuilt from the transcript tail, so a restart costs recency of the ring, not correctness of the answer.

### The classifier — signals → state

Fully **mechanical — no LLM at any rung** (resolving prior open question 3): the four states are decidable from events and cheap text checks. Judgment-grade reading of *what was said* is [[F217 — Conversation-content gating — rules on what was said|F217]]'s `ask_oracle`, deliberately out of scope here. Evaluation order, on first `agent.*` read of a pass:

```
1. liveness   — session process gone, or session:stop seen        → idle
2. in flight  — ledger shows prompt:submit (or any tool/skill
                moment) after the last prompt:stop                → working
3. turn end   — last boundary is prompt:stop
                → pending-question predicate Q true               → asking
                → Q false, open-work test W true                  → paused
                → Q false, W false                                → landed
4. decay      — landed and no moment for ≥ T_idle                 → idle
```

**The pending-question predicate Q** — reworked 2026-07-01 to the user's right-now frame: the question is *"did this turn end addressing a question to the user?"* — answered from the turn itself, never from the queue. True if either test holds, checked cheapest-first:

- **T1 — dialog signal.** The turn ended in the harness's **multi-choice question dialog** — an `AskUserQuestion` tool moment in the ledger with no answering moment after it (the dialog is a tool call, so the ledger sees it exactly). This is the strongest signal: the widget is literally up, waiting.
- **T2 — chat-question heuristic.** The turn's final agent message addresses a question to the user: last non-code paragraph ends in `?`, or carries an options pattern (`(A)`/`(B)`, `Q<n>:`). Read from the transcript's last assistant record. Explicitly a **mechanical heuristic** — no LLM call, per the user: *"I think we can just have some heuristics that look for a question mark."* Occasional misses on rhetorical questions are accepted; a rule needing judgment-grade detection layers F217 on top.

*(Retired: the former queue signal — open `queries.md` items making the agent `asking`. Per the user 2026-07-01, the queries pile is the anchor's long-horizon state, not what the agent is doing right now; a rule about queue pressure reads `anchor.doc("{NAME} queries.md")`. A `skill:post:query` moment remains a useful corroborating hint but is not part of Q.)*

**The open-work test W** — feeds the `paused` state — — at a turn end with Q false, are there open items on the harness **task list**? The ledger sees `TaskCreate`/`TaskUpdate` tool moments, so the daemon can track open-task count per session mechanically (transcript records as the R3 fallback). Open tasks > 0 → `paused` ("stopped, but still has work"); zero → `landed`.

**Debounce / hysteresis** — restated as the invariants an implementation must hold:

- No debounce into `working`; no silence-based exit from `working` (long tool calls and long thinks are quiet and normal).
- One timer, `T_idle`, on the `landed → idle` edge only. `asking` carries no timer.
- **Crash ambiguity is `unknown`, not a guess.** Process alive, no `Stop`, ledger and transcript both quiet past `T_dead` (default **30 min**): a very long tool call and a hung agent are indistinguishable, so the classifier says `unknown` rather than fabricating `working` or `idle`. Process *dead* without a `Stop` is unambiguous → `idle`.
- Subagent moments (a `Task` fan-out) attribute to the **top-level session**; `agent` always describes the session the user is talking to, never a subagent.

**`agent.skill`** — the running skill, derived by rank:

1. **Skill moments** — a `skill:pre`/`skill:post` pair in the ledger maintains a stack; `agent.skill` is the innermost active skill's kebab name, `None` when the stack is empty. *Named dependency:* this rung waits on [[F209 — Unified trigger taxonomy + when language|F209]]'s open question — the `skill:pre/post` emission point (skills are runbooks, not processes). Until the skill-dispatch layer emits those moments, rank 1 is empty and rank 2 carries the answer — the design degrades, it does not block on M0.
2. **Transcript sniff** — the Skill-tool invocation (or `<command-name>` tag) in the current turn's records.
3. **Pane sniff** — the `/skill` command line visible at the last user prompt in scrollback.

Value contract: a kebab skill-name string, or `None` (no skill running, *or* not derivable at the current rung — a rule that must distinguish those reads `agent.state == 'unknown'` first).

**Laziness + cost.** One classification per pass, computed on the first `agent.*` read and shared by every rule in the pass ([[Warden Runtime]] § Indexed evaluation). The work is dict lookups over the ledger, at most one transcript-tail read, and one `queries.md` parse — well inside the audit budget and cheap enough for a `prompt:stop` steer.

### The fallback ladder

Each rung names what it can answer exactly and what degrades. The classifier binds a session, takes the **highest rung available** for it, and answers from there.

| Rung | Signals | Exact | Degraded |
|---|---|---|---|
| **R1 — in-band** (live rule fire: hook event + ledger + transcript) | all of § Signal inventory | everything — full-fidelity states, Q1–Q3, ranked `agent.skill` | nothing. Every *live* `agent.*` read is R1 by construction — a live rule runs inside a hook, so the ledger is current up to that very event |
| **R2 — tmux-registered** (out-of-band read — an audit pass, or observing a registered sibling session) | pane + transcript + queries.md + process table | `working`/`idle` from the rendered prompt state; permission-dialog stalls **visible** (uniquely at this rung) | boundary timing is render-grade, not event-grade; `agent.skill` from sniff (ranks 2–3); Q1 unavailable |
| **R3 — transcript-mapped** (no tmux; session's JSONL known) | transcript + queries.md + process table + mtime | `asking`/`landed` from the last assistant record + Q2/Q3; `idle` from stale mtime | `working` inferred from mtime freshness (latency = flush lag); a permission-dialog stall reads as `working`; skill from sniff |
| **R4 — residual** (no per-session mapping at all) | queries.md + process table | queue-state `asking` (coarse, anchor-scoped only); alive/dead | every turn-boundary state → `unknown`; `agent.skill` → `None`. This rung is the honest floor: turn-grade states need a per-session signal, and R4 says so rather than guessing |

This resolves prior open question 1 (how much to lean on tmux): the pane is **one rung, not the foundation** — the moment ledger and transcript outrank it for structure, and the pane's unique contribution is the rendered view (permission dialogs, control-with-user) plus coverage of sessions observed from outside.

### The environment contract

What a rule actually gets at fire time:

- **Binding.** Live path: `agent` binds to the session that produced the triggering moment. Audit path: to the session running the audit. Headless batch audit with no session: every read returns the error values (`state == 'unknown'`, `skill is None`, `is_asking is False`).
- **Values.** `agent.state` ∈ `{'working','landed','asking','idle','unknown'}` (closed); `agent.skill` is `str | None`; `agent.is_asking` is `bool`. Reads never raise — `unknown` / `None` **are** the error channel.
- **Freshness.** R1: exact as of the triggering event. R2/R3: staleness bounded by transcript flush lag (seconds) plus the pass's own runtime. R4 carries no freshness bound — which is precisely why its turn-grade answer is `unknown`.
- **Per-pass cache.** One classification per pass; all rules in the pass see the same answer. A later moment in the same turn opens a new pass and re-classifies.
- **Cost.** Mechanical at every rung; `agent.state` never spends LLM tokens (resolving prior open question 3 in the contract itself).

### The environment contract (addendum) — attach-guard at launch (from F148 retirement, 2026-07-02)

SKA F148 (agent instance tracking) was retired as superseded: worktree-per-agent + this feature's session registry + `/cleanup` cover it. The one residual it hands to F216/MUX policy: **a launcher must not `--continue`/`--resume` into a cwd that already has a live session** (the JSONL-interleave footgun's last surviving form — a second tab opened into an *occupied* worktree). The session registry answers "is there a live session here?" in one lookup; the guard is a launch-time check against it, not new machinery.

## Resolved

- **tmux dependency (prior Q1)** — the pane is rung R2 of a four-rung ladder, not the primary source; the daemon's own moment ledger + the transcript outrank it, and R4 names the honest floor. § The fallback ladder.
- **`agent.skill` emission (prior Q2)** — ranked derivation: skill moments when the skill-runner emits them (named F209 dependency), transcript sniff until then, pane sniff last. § The classifier.
- **Classifier cost (prior Q3)** — fully mechanical, no LLM at any rung; one lazy classification per pass. Judgment-grade content reading is F217's job.
- **Q1 — which `queries.md` items make the agent `asking`?** — **Resolution (user, 2026-07-01): neither option — the premise was wrong.** `agent.state` answers *what the agent is doing right now*; the queries pile is the anchor's long-horizon state, not a state signal at all. The queue signal is retired from the pending-question predicate — `asking` is sensed from the turn itself (T1 dialog moment, T2 text heuristic); queue pressure is read via `anchor.doc("{NAME} queries.md")`. ^F216-Q1
- **Q2 — does `asking` survive session end?** — **Resolution (2026-07-01): (A)**, following directly from the right-now doctrine — a dead session is `idle`; the leftover queue stays visible through `anchor.*`. ^F216-Q2

## Status

**Designed 2026-07-01; reframed to the right-now model same day (user) — zero open questions.** Taxonomy (closed state set + transition semantics, with the `paused` split, accepted 2026-07-02), signal inventory, mechanical classifier (dialog-signal + text-heuristic pending-question predicate, debounce invariants, ranked `agent.skill`), four-rung fallback ladder, and the environment contract are concrete.

**Built 2026-07-05 — `engine/warden_agent.py`, live in both engines.** The classifier implements the full ladder (liveness → in-flight → turn-end with Q/W → decay) with `T_idle`/`T_dead` as engine constants; Q is T1 (an `AskUserQuestion` tool_use ending the transcript, unanswered) then T2 (final non-code paragraph ends `?` or carries an `(A)`/`Q<n>:` options pattern); W counts open harness tasks from `TaskCreate`/`TaskUpdate` records. `ctx.agent` is a lazy `AgentView` (one classification per pass, cached; reads never raise — `unknown`/`None`/`False` are the error channel) exposing `state`, `skill`, `is_asking`, `state_seconds`, `open_tasks`. Wiring: `build_ctx` defaults to the unbound view (headless/audit contract); the Python hook binds the triggering session; the daemon holds the session registry + bounded per-session moment ledger and the `fire_rules` op grew an optional `session` field, which the Rust hook forwards — so R1 exactness comes from the triggering moment, history from the transcript tail (the ledger's sanctioned rebuild source), and a sparse ledger degrades recency, not correctness. Rank-1 `agent.skill` reads `skill:pre` ledger moments (live today); rank 2 is the transcript sniff (Skill tool_use / `<command-name>` tag, current turn only). The R2 tmux rung is not yet built — the ladder degrades past it by design. Verified by `test_warden_agent.py` (scripted transcripts driving every state, incl. the Success-Criteria fixture rule firing its tell only in `asking`), the extended daemon test, the Rust↔Python hook differential, and the perf gate (3.05/3.46 ms — the lazy view costs the hot path nothing).

**Standing requirement (user, 2026-07-01 consumer review):** many rules condition on agent state, so `agent.*` should grow toward a **pretty complete set of lazily-computed state properties** — lazy because each costs computation/resources; the classifier's `state`/`skill` are just the first two. The starter surface (identity, activity, `response` alias, `context_used`, `state_seconds`, `open_tasks`) is ratified (accepted 2026-07-02) in [[Warden Semantics]] § `agent`; members join by proposal, each justified by a real rule that reads it.
