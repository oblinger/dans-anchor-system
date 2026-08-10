---
description: "product requirements — the kinds of bridging"
---

| -[[DAS Bridge PRD]]- | : product requirements — the kinds of bridging<br>→ [[DAS]] → [design](hook://design) → [DAS Bridge PRD](hook://p/DAS%20Bridge%20PRD)  |
| --- | --- |
| [[DAS Bridge UX Design\|UX Design]]  | the command surface that realizes these requirements |
| [[DAS Bridge Testing\|Testing]]  | how each kind of bridging is verified |
| [[bridge\|SKILL.md]]  | the live runbook |
| ... |  |

# DAS Bridge PRD


## Problem

Working across two Macs — a primary dev machine and a secondary (disk station, test box, twin) — the user needs the second machine to be *reachable* in three increasingly-deep senses: **drivable** (run commands there), **mirrored** (same files there), and **twinned** (run Claude there as if it were here). Plain SSH delivers none of these well: it has no Full Disk Access, no shared filesystem view, and no notion of "the same working environment." `bridge` fills that gap with one umbrella over three kinds of bridging.

## What bridge produces

A configured, verifiable connection from this Mac to a named remote host, in one or more of three kinds. Each kind is independently usable; deeper kinds compose shallower ones.

## The three kinds of bridging

Two are **mechanisms** (how control or bytes move); the third is a **goal** built on top of them.

### 1. Control bridge — *drive the remote as a local box* (mechanism)

**As a** developer working across two Macs, **I want** to run commands on the remote with the user's full TCC/FDA permissions **so that** the agent can read TCC-protected paths (`/Volumes/*`, `~/Desktop`, `~/Documents`) and drive sustained interactive work there.

- Realized by SSH + a remote tmux/screen session launched from a **TCC-blessed Terminal** — the multiplexer inherits FDA from its launcher, and SSH-attached commands inherit it in turn.
- This is the original `mux-bridge` capability; it is the *substrate* the other kinds lean on for command execution.

### 2. Sync bridge — *mirror folders at identical paths* (mechanism)

**As a** developer, **I want** selected folder trees (vault, code repos) to appear at the **same absolute path** on both machines **so that** wiki-links, absolute-path references, and path-baked tooling all resolve identically on either side.

- Realized by Syncthing today (eventual-convergence, both sides keep a local copy). NFS-via-symlink (live mount) and rsync (explicit push/pull) are planned future modes.
- Per-host mode: a host has at most one sync mode at a time.
- **Same-relative-path contract** is load-bearing: `/Users/oblinger/ob/kmr/` on the dev Mac ↔ the same on the remote.
- **Move-aside on seed:** when the remote already holds a prior copy, its content is moved aside (`<path>.old.<date>/`) before sync begins — an empty target can't propagate stale state back, and the moved-aside copy is a recovery point.
- **Direction is a choice:** one-way mirror (Send-Only → Receive-Only) is the safe default; two-way (Send-Receive) is opt-in.

### 3. Claude bridge — *run Claude on the remote as an environment-twin* (goal)

**As a** developer, **I want** the remote to run a Claude instance that behaves like this machine's — same skills, same `CLAUDE.md`, same vault content **so that** I can offload Claude work to the twin without re-provisioning by hand.

- A **composite goal**, not a peer mechanism: it *uses* a sync bridge (for vault + code content) **plus** an rsync of `~/.claude` (skills, `CLAUDE.md`, settings, commands).
- **Environment parity, not session portability.** `~/.claude/projects/*.jsonl` transcripts are a hard exclude — they are high-churn append-logs that generate `.sync-conflict` files under two-way sync and reference machine-local state (PIDs, tmux, background tasks). The twin runs **fresh** sessions; the environment is what travels.

## Cross-cutting requirements

- **Mechanism vs goal.** Control and sync are mechanisms (verbs that move control/bytes). Claude is a goal that composes them. The design must keep this layering visible so "claude" never becomes a confusingly-peer mechanism.
- **Config is the per-user recipe; the skill is the abstract goal.** The skill knows the *shape* of each bridge; `~/.config/bridge/config.yaml` holds *this user's* concrete paths/hosts (`defaults`, and the `claude_environment` manifest of what "my environment" consists of). No host or path is hard-coded in the skill.
- **Idempotent + verifiable.** Every bridge operation is safe to re-run and exposes a verify path (control: a command round-trips with FDA; sync: file appears on the remote within seconds; claude: skills present + `projects/` absent → `twin_ready`).
- **Confirmation gates on destructive steps.** Any move-aside / overwrite of remote content warns and confirms first.

## Non-goals (v1)

- Carrying live Claude **sessions** between machines (excluded by design — see Claude bridge).
- NFS and rsync sync modes (designed in [[F122 — mux-bridge file-sync extension (Syncthing + NFS-via-symlink + rsync future)|F122]], deferred to later phases).
- Non-macOS remotes for the claude/sync bridges (control bridge supports Linux; sync/claude are macOS-first).
- Multi-host fan-out (sharing one folder across 3+ machines).

## Provenance

Commissioned as [[F150 — Rename mux-bridge → bridge — umbrella with mux_sync_claude sub-bridges + environment manifest|F150]]; sync mechanism [[F122 — mux-bridge file-sync extension (Syncthing + NFS-via-symlink + rsync future)|F122]]; defaults/manifest [[F146 — mux-bridge sync defaults + interactive setup|F146]]. First verified live against `haorui.local` 2026-06-11.
