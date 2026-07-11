---
description: "product requirements"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [DAS Groom PRD](hook://p/DAS%20Groom%20PRD)
# Groom PRD

**Shared design:** `/groom` and `/ask` are one **resolution layer** — the frontier, the `F`/`T`/`M`/`R` work-item-identity model, the five groomed states, and the question bar are specified once in **[[Query PRD]]** (read it as the resolution-layer PRD). This doc covers groom-specific requirements; runtime spec is [[skills/groom/SKILL.md\|SKILL.md]]; user guide is [[ASG Groom]].

## Overview

`/groom` is a **convergent maintenance operator** over an anchor's structured-work artifacts (backlog, optionally roadmap). Each invocation moves the artifacts toward a defined **groomed state**. It began as `/ready` (F202 — a batch promote-to-Ready pass) and was reframed and renamed to `/groom` (F201) to anchor the mental model on the invariants kept, not the single promote action taken.

## Goals

- Safe to call anytime — a groom never makes things worse; it always moves the artifact toward the groomed state (the load-bearing property).
- Convergent across calls — repeated calls progressively shrink the gap (not strictly idempotent; may pause for input and leave partial state).
- Drive every frontier item into one of the five groomed states (per [[Query PRD]]); park questions in the queries surface; assign F/T numbers; repair link integrity; enforce section/ordering invariants.

## Non-Goals

- **No user interruption at all** — the entire batch runs autonomously; every question routes to the queries surface, never to chat (per [[Query PRD]] R1; the former "one trivial question deferred" concession was retired 2026-07-05).
- Groom never resolves questions for the user, changes horizon without cause, or touches terminal-state items (Verify/Done).
- Default scope is the frontier (Now/Next + next roadmap milestone) — `## Later` and the icebox are opt-in via `/groom later` / `/groom icebox`.

## User Stories

- As the user, I run `/groom` on a messy backlog and get a tidied, well-numbered, link-clean backlog where every frontier item is executable, questioned, blocked, verifying, or watching — and everything needing my input is consolidated in `{NAME} queries.md`, not scattered in chat.

## Key decisions

- **Operator framing** (F201): `groom: state → state'`, convergent not strictly idempotent; "you can always groom and then groom a little bit more."
- **The five groomed states + body contracts** (F251, 2026-07-06): every frontier row is driven to Executable / Questions / Blocked-Waiting / Verify / Watching, each with a body contract enforced by a checked `R-backlog` rule. See [[Query PRD]] § Grooming the frontier and [[facets/FCT Track/DAS Backlog\|FCT Backlog]] § The groomed states.
- **Definition of Ready** (F202): *an item is Ready when you believe you can do the task without further user involvement*.
- **Minimize-user-back-and-forth** (F202): batch backlog operations complete autonomously before involving the user — one round-trip per pass, not N.
- **Rename in place, no alias** (F201): `skills/ready/` → `skills/groom/`; `/ready` retired. DMUX prefix-trigger `when(groom, prefix(/groom))`.
