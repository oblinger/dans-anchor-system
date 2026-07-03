---
description: "F220 — Live hook install + kill switch — wire the compiled engine into the real Claude Code hook surface, with an instant global disable"
---

# [[Warden]] · F220 — Live hook install + kill switch

## Summary

The productionisation layer that takes the built engine ([[F211 — Rule compiler and installer|F211]] / [[F212 — Python reference implementation|F212]]) **live**: a single dispatcher command registered on the real Claude Code hook surface (`settings.json` hooks — the native interception substrate, [[Warden Integration Strategy]] D2), mapping each hook event to a Warden moment, firing the compiled engine, and emitting steers as hook output. Ships with a **kill switch** — an instant, global, no-edit disable (`warden off`) so a broken rule can be pulled from *every* environment in one move while it is fixed. Going live is safe *because* the kill switch exists: we adopt a small pilot surface, run it for real, and fix breakage live behind a disable that is always one command away.

User directive 2026-07-02: *"go ahead and make some portion of it live and start using it… make sure that it's relatively easy to disable so that I can easily pull it out of all environments if it's broken until we fix it."*

## Success Criteria

**Tier:** 3 (live-environment behavior — user-observable)
**Blocks next:** [[F221 — Live-integration test class|F221]] (live e2e verification rides this)

**What done looks like.** A `warden-hook` dispatcher is registered in `settings.json` for the pilot events; on a real agent action at a live moment, the active-set rules fire and their steers reach the agent. `warden off` disables Warden globally and instantly (the very next hook invocation no-ops); `warden on` re-enables. The disable is checked **first**, before any compile/scan, so a disabled Warden costs ~nothing and cannot itself break a session.

**How it will be verified.** [[F221 — Live-integration test class|F221]]'s live e2e harness drives a real agent through a triggering moment and confirms the rule fired (via the selftest log); toggling `warden off` mid-run makes the same trigger a no-op. Unit tests cover the event→moment mapping and the kill-switch short-circuit.

## Design

- **One dispatcher, thin adapter.** A single entry (`warden/engine/warden_hook.py`, exposed as the `warden-hook` command) is registered for each piloted hook event. It reads the event JSON on stdin, maps event→moment, resolves the anchor from `cwd` (walk up to `.anchor`), fires `WardenEngine`, and writes hook output (steers as `additionalContext`; `deny`/`block` via JSON per [[Warden Integration Strategy]] D5, gated by the `aow-safety` floor — never exit-code-2). The event→moment map is [[Warden Events]]' table: `PreToolUse`→`tool:pre:<Tool>`, `PostToolUse`→`tool:post:<Tool>` (+ the `write:<kind>` content view for Write/Edit), `SessionStart`→`session:start`, `Stop`→`session:stop`, `PreCompact`→`session:compact`, `UserPromptSubmit`→`prompt:submit`, the Skill tool→`skill:pre:<name>`.

- **Kill switch — sentinel file, checked first.** The dispatcher's first act is a disable check: if `~/.warden/DISABLED` exists **or** `WARDEN_DISABLED` is truthy in the env, it prints nothing and exits 0 immediately (no scan, no compile, no fire). File-based so the disable is **global across every environment and every concurrent session** with no `settings.json` edit and no restart — the next hook invocation anywhere sees the sentinel. `WARDEN_DISABLED=1` is the per-session/CI override. A `warden` CLI (`warden/engine/warden` → `~/bin/warden` dev symlink) exposes `warden on` / `warden off` / `warden status` (toggle the sentinel) plus `warden install` / `warden uninstall` (add/remove the `settings.json` hook block) and `warden fire …` (manual one-shot for debugging). The install writes a labelled, idempotent block so `warden uninstall` is a clean removal.

- **Pilot surface, not the whole taxonomy.** Go live on the **smallest safe set first** (Roadmap OQ2 — `audit-q` is the natural pilot, already `when::`) plus the [[F221 — Live-integration test class|F221]] selftest ruleset. Widen the registered events only as each is proven live. A `tool:pre` veto rule is **not** in the pilot (blocking is highest-blast-radius); the pilot is steer-only.

- **Fail-safe, never fail-closed.** Any exception in the dispatcher is caught and swallowed to a no-op (log to `~/.warden/hook.log`, exit 0) — a Warden bug must never break the user's actual tool call. Warm-start compile is lazy + cached (F211), so the steady-state hook cost is a dispatch, not a recompile.

## Status

**Built + LIVE-PROVEN 2026-07-02.** The full dispatcher (`warden/engine/warden_hook.py`), kill switch, and `warden` CLI ship and are proven firing in a **real Claude Code session**: a headless `claude -p` agent driven in a scratch anchor (with the `warden-selftest` trait) fired all four piloted moments — `session:start`, `prompt:submit`, `tool:post:Write`, `write:markdown` — each landing a marker in `~/.warden/selftest.log` ([[F221 — Live-integration test class|F221]]'s harness). The kill switch (`~/.warden/DISABLED` sentinel + `WARDEN_DISABLED` env, checked first) and the merge-safe idempotent `settings.json` install/uninstall are verified. `test_warden_hook.py` covers the event→moment map, kill switch, dispatch→fire→log, and trait gating.

The **live test earned its keep on the first run**: the hook command path contains a space (`Skill Agent`) and was unquoted, so the shell split it and the hook *blocked* the agent instead of failing safe (a broken command never launches the Python fail-safe). Fixed by `shlex.quote`-ing the path — exactly the live-integration failure class F221 exists to catch, caught before any real go-live. A compiler bug was also surfaced and fixed en route: `canonical_moment` was inserting a `pre`/`post` phase for every class, compiling `write:markdown`/`session:start`/`prompt:submit` to moments the dispatcher never fires; now only `tool`/`skill` are phased (F209).

Remaining: the actual go-live into the user's global `~/.claude/settings.json` (the pilot has run only against a project-scoped scratch settings file so far) and widening the registered surface past the steer-only pilot.

## Resolved

1. **Mechanism** — `settings.json` native hooks behind a thin dispatcher adapter (D2), **not** POST-COMPACT self-binding (that is only the `session:compact` case, subsumed by `PreCompact`). Decided 2026-07-02.
2. **Kill switch** — sentinel file `~/.warden/DISABLED` (global) + `WARDEN_DISABLED` env (per-session), checked before any work; `warden on|off|status`. Decided 2026-07-02.
3. **Pilot scope** — `audit-q` + the selftest ruleset, steer-only (no `tool:pre` veto in the pilot). Decided 2026-07-02.

## Open questions

1. **Anchor resolution in a hook** — `cwd`-walk-up is the v1; does a multi-anchor session (worktrees) need the event's `file_path` to pick the anchor instead? Revisit once the pilot runs.
