---
description: "Warden runtime — how it observes tool uses, file changes, and the agent, and runs rule checks without per-moment cost"
---
# Warden Runtime

How Warden **observes** the system — tool uses, file changes, the agent — and **runs rule checks** at scale without paying a per-moment cost. This page is the consolidated record of the efficiency commitments; [[Warden Semantics]] is the rule model these mechanisms serve, and [[Warden Architecture]] §7 the engine overview.

The whole design rests on one move: **do the work in a warm process, and keep the per-moment signal tiny.** Everything below follows from that.

## The resident daemon

A long-running **Python daemon** is the engine. It holds, in memory:

- the **compiled, indexed** active rule set (per anchor), and
- **lazy / per-pass-cached `ctx`** state (`file`, `anchor`, `git`, `event`, `agent`).

Because it stays warm, evaluating a moment is **one pre-compiled function call** over already-loaded rules — **sub-millisecond, and constant in the total rule count** (dispatch is an index lookup, not a scan). It never pays interpreter startup.

**Socket interface.** The daemon listens on a Unix socket / FIFO and accepts notifications — uniformly:

- `moment <event>` — a tool use, a write, a turn boundary fired; reply with a verdict for a blocking (`tool:pre`) moment, else fire-and-forget.
- `file-changed <path>` — a file changed (from a watcher; § File changes). Change is just another input on the same socket.

**Lifecycle — the real complexity this buys.** It **warm-starts lazily** on the first hook (that first call pays the load+compile), **fails open** if it is down or still warming (never blocking the agent), and **recompiles** the affected index when a rule or `Decisions.md` changes — itself just a `write:*` notification it receives.

## The notifier — pluggable, OS-selected

What Claude Code's hook actually spawns is a tiny **non-Python notifier** whose only job is to signal the daemon. It must avoid Python's ~30–80 ms startup. Warden **bundles several implementations and picks one at load** by inspecting the OS:

| Notifier | Spawn cost | Role |
|---|---|---|
| **Native binary** (pre-compiled per OS, in the Warden bundle) | ~1–2 ms | fastest; used where a build exists for this OS |
| **`sh` hook** (`printf '%s' "$EVENT" >> warden.fifo`) | ~1–3 ms | the **universal floor** — works everywhere, no build |
| `nc -U` / native socket round-trip | ~2–4 ms | the **blocking** `tool:pre` veto only |
| ~~Python~~ | ~30–80 ms | **never** — the cost we exist to avoid |

So **hook efficiency is a solved, non-issue**: native where we can, `sh` everywhere as the backup. The binaries live *inside the Warden package* (never `~/bin` — packaged-app rule). Non-blocking moments fire-and-forget into the FIFO and the daemon drains it off the agent's critical path; only the rare veto pays a round-trip.

## Tracking tool uses

Claude Code's hook subsystem (`PreToolUse` / `PostToolUse` / `SessionStart` / …, [[Warden Events]]) → the notifier → the daemon. Each moment is one notifier spawn (~1–3 ms); the daemon does the indexed eval warm. Dozens of tool calls per turn × ~2 ms is imperceptible, so **we can instrument as much as we want.**

## Tracking file changes — dual mode

- **Agent writes** are free — the `write:*` hook already fires; the daemon gets `event.diff`.
- **External changes** (Obsidian, `git pull`) need a watcher. Warden is **dual-mode**, to honor its zero-dependency North Star *and* the one-watcher principle:
  - **A shared watcher exists** (HookAnchor's, or a system one) → Warden **subscribes** to it; that watcher sends `file-changed` to the daemon socket.
  - **None exists** → Warden runs **its own** watcher — naturally an **in-Python** watch inside the daemon (FSEvents/inotify), feeding the same socket. Warden stays freestanding.
- **One watcher per machine.** Redundant trackers waste CPU during event storms (a `git checkout` touching thousands of paths is processed *per* watcher), so Warden never adds a 3rd alongside HookAnchor / DMUX — it prefers the shared one and only self-hosts as a fallback.
- Even with no live watcher at all, external changes are still caught at the next `/audit` via the **content-hash** (the audit re-evaluates changed/new files). The watcher only buys *liveness*, not correctness.

## Tracking the agent

`agent.state` (`working` / `landed` / `asking` / `idle`), `agent.skill`, `agent.is_asking` — sensed at a turn boundary (`when:: prompt:stop`) to react to *how a turn ended*. The signal→state classifier is non-trivial (it reasons over recent activity, not a flag) and is its own design item: **[[F216 — Agent-state model — sensing what the agent is doing|F216]]** (the agent's tmux pane as the clean source, with a fallback ladder where tmux isn't available). Sensed **lazily** — computed only when a rule reads `agent.*`. Conditioning on *what the agent said / didn't say* extends this: **[[F217 — Conversation-content gating — rules on what was said|F217]]**.

## LLM judgments — the oracle

An `if::` that needs judgment, or any `ask_oracle`, runs on a **cheaper model (Sonnet)** through Claude Code's *own* access — **no API key, no tmux**:

- **`claude -p` headless** — Anthropic's purpose-built non-interactive interface; the sanctioned automation path, on the subscription. This is the default oracle implementation, including the gating `if::` judgments.
- On the **audit path** the call blocks the *audit* (not the agent) and the verdict is cached. On the **live path** there is no blocking model call — a live judgment is **delegated to the running agent** as a steer, because `claude -p` is *seconds* (CLI + model) and can't sit on the hot path.
- ≈**5× cheaper** than the main Opus agent, **~1¢/check**, so oracling even ~10% of responses is ~1–2% of total spend. The **external Sonnet API is opt-in** — only to dodge subscription usage caps; not required.

## Indexed evaluation

The compiler turns the active rules into an **index** (moment → pre-built function; sometimes `where::` → function for a rare-file rule). Fire time is a **lookup → one call**; a linear scan of the rule list is the **last-resort fallback only**. Combined with **lazy per-pass `ctx`** (each object computed on first access, cached for the pass), the cost is constant in *both* the rule count and the object count — one `git` call, one content-hash, one `agent.state` read per pass, shared across every rule.

## The cost picture

| Concern | Cost | Why it's bounded |
|---|---|---|
| Per moment | ~1–3 ms (notifier) + µs IPC + [blocking: sub-ms eval] | warm daemon; non-Python notifier |
| More rules | ~0 | indexed dispatch, not a scan |
| More `ctx` reads | ~0 | lazy, cached per pass |
| File tracking | ~0 extra | no own watcher unless alone; one watcher max |
| Oracle | ~1¢/check, seconds, **off** the hot path | Sonnet via `claude -p`; audit/async or delegated |

**The genuinely new costs** Warden takes on are the **daemon lifecycle** (warm-start / fail-open / recompile) and the **agent-state classifier** ([[F216 — Agent-state model — sensing what the agent is doing|F216]]) — both bounded, neither fatal.

## See also

- [[Warden Semantics]] — the rule model (condition, actions, the interpretation environment) these mechanisms run.
- [[Warden Architecture]] §6–7 — the hook subsystem + the compiler/audit engine overview.
- [[Warden Events]] — the moment catalog the hooks fire on.
- [[F216 — Agent-state model — sensing what the agent is doing|F216]], [[F217 — Conversation-content gating — rules on what was said|F217]] — the two tracking design items.
