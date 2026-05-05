---
description: operating-mode framework — defines what a mode is, the metric it optimizes, and how modes are declared
---

# SKL Mode

A **mode** is a setting that shapes how the agent makes recurring trade-off decisions. Different anchors have different risk profiles — a freshly-built tool with no users tolerates aggressive forward motion; a deployed app with thousands of users needs more caution per change. Mode is the declaration of which posture is appropriate.

For now (v1), there is **one system-wide mode**, declared inline in the Pilot's POST-COMPACT RELOAD. Eventually, modes will be declared per-anchor (in `.anchor` config) with the system default as fallback.

## The metric — outcome per interaction

The agent optimizes:

> **outcome per interaction**

with this cost structure for the denominator:

- **Heavy weight** — each content-full batch (any session where the user must read, think, and respond).
- **Lighter weight** — each round-trip within a batch (back-and-forth Q&A inside one active session).
- **Lightest weight** — each `/crank` press (no content but still attention).

The numerator is **capability produced** — features shipped, decisions resolved, working code committed, design questions answered, technical debt paid. Lines of code is a proxy, not the goal.

The whole posture follows from this metric: **minimize content-full batches first, round-trips within them second, crank presses third.** Tokens are not in the denominator at all.

## Defined modes

- **[[SKL Mode Drive|Drive]]** — agent-driven, optimistic, minimum-interruption. The current system default. See the page for the full set of assertions.
- (future modes added here as they're defined — e.g., a `Caution` or `Step` mode for high-risk anchors)

## How modes are set

**v1 (current):** the system-wide mode is declared in the Pilot's POST-COMPACT RELOAD section of `role-pilot.md` as a named bullet, with the load-bearing rules inlined so they prime the agent on every session start. The corresponding spec (this folder's `SKL Mode <Name>.md` page) holds the user-facing explanation, the rationale, and the canonical agent-facing version (which is copy-pasted into POST-COMPACT when changes happen).

**v2 (eventual):** per-anchor mode declared via `mode:` field in `.anchor` config; system-wide default in `~/.claude/CLAUDE.md`. Anchor-specific override wins. A future `/mode` skill will support inspection (`/mode` reports current) and switching (`/mode set drive` rewrites the declaration). Agents resolve mode via the same `.anchor` walk-up as other anchor-scoped resolution.

## History

- **2026-05-04** — Mode framework established. **Drive** defined as the first mode and rolled out as the system default. Captured in `SKL Mode.md` (this page) + `SKL Mode Drive.md` (the assertions); inline copy in `role-pilot.md` POST-COMPACT RELOAD. Per-anchor switching deferred until ≥2 modes exist.
