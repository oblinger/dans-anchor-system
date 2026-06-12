---
description: operating-mode framework — defines what a mode is, the metric it optimizes, and how modes are declared
---
| -[[SKL Mode]]- | : <br>→ [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[SKL]] → [SKL Mode](hook://p/SKL%20Mode) |
| --- | --- |
| Trade-off posture | [[SKL Mode Drive\|Drive]],   |
| Git boundaries | [[SKL Mode Git Commit\|Commit]],  [[SKL Mode Git PR\|PR]],   |
| ... |  |

# SKL Mode

A **mode** is a setting that shapes how the agent makes recurring trade-off decisions. Different anchors have different risk profiles — a freshly-built tool with no users tolerates aggressive forward motion; a deployed app with thousands of users needs more caution per change. Mode is the declaration of which posture is appropriate.

Modes are **compositional traits** (per [[F077 — PR mode — mode-as-trait architecture with per-anchor opt-in|F077]]) — an anchor runs with one or more modes active at the same time, composed along independent axes. The two axes today:

- **Trade-off posture** — [[SKL Mode Drive|Drive]] vs. [[Lean]] (the `/fortify` posture). Mutually exclusive.
- **Git boundaries** — [[SKL Mode Git Commit|Commit]] vs. [[SKL Mode Git PR|PR]]. Mutually exclusive.

Bare-noun Trait names — `Drive`, `Lean`, `PR`, `Commit`, `NoGit` — per [[F077 — PR mode — mode-as-trait architecture with per-anchor opt-in|F077]] Q7. Older docs may say "Cautious" as descriptive English for the Lean posture; `Lean` is the canonical Trait name.

The default pair is **Drive + Commit**. Both default modes are inlined in `role-pilot.md` POST-COMPACT RELOAD so they prime the Pilot on every session start.

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

### Trade-off posture

- **[[SKL Mode Drive|Drive]]** — agent-driven, optimistic, minimum-interruption. **System default.** See the page for the full set of assertions.
- **[[Lean]]** — cautious, distrust-the-foundation, fortify-before-adding. Per-turn invocation via `/fortify`; declarative per-anchor activation via `Lean` in `.anchor` `traits:`. User-facing methodology spec at [[SKA fortify]]; CAB Trait spec at [[Lean]].

### Git boundaries

- **[[SKL Mode Git Commit|Commit]]** — agent commits at logical boundaries without asking; new-commit-on-top, never amends; never auto-pushes. **System default.** Use when the cost-of-merge-mistake is low (curation projects, personal anchors, prototypes).
- **[[SKL Mode Git PR|PR]]** — every state-touching commit gated through a pull request on its own branch with user review before further work continues. Use when the cost-of-merge-mistake is high (production code with users, shared libraries, deployed infrastructure). Spec in flight per [[F077 — PR mode — mode-as-trait architecture with per-anchor opt-in|F077]] (Q12 = agreement gate).

## How modes are set

**v1 (current):** the system-wide mode is declared in the Pilot's POST-COMPACT RELOAD section of `role-pilot.md` as a named bullet, with the load-bearing rules inlined so they prime the agent on every session start. The corresponding spec (this folder's `SKL Mode <Name>.md` page) holds the user-facing explanation, the rationale, and the canonical agent-facing version (which is copy-pasted into POST-COMPACT when changes happen).

**v2 (eventual):** per-anchor mode declared via `mode:` field in `.anchor` config; system-wide default in `~/.claude/CLAUDE.md`. Anchor-specific override wins. A future `/mode` skill will support inspection (`/mode` reports current) and switching (`/mode set drive` rewrites the declaration). Agents resolve mode via the same `.anchor` walk-up as other anchor-scoped resolution.

## History

- **2026-05-04** — Mode framework established. **Drive** defined as the first mode and rolled out as the system default. Captured in `SKL Mode.md` (this page) + `SKL Mode Drive.md` (the assertions); inline copy in `role-pilot.md` POST-COMPACT RELOAD. Per-anchor switching deferred until ≥2 modes exist.
- **2026-05-24** — **Git Standard** mode added per [[F085]]. Three load-bearing rules (commit on logical boundary, terse messages, never auto-push). Composed with Drive as the canonical pair.
- **2026-06-01** — **Renamed Git Standard → Commit** per [[F077 — PR mode — mode-as-trait architecture with per-anchor opt-in|F077]] Q7 (bare-noun naming convention `Drive`/`Lean`/`PR`/`Commit`/`NoGit`). Added explicit "never ask permission to commit" rule and "always new commit on top — never amend" rule. **Commit-mode bullets inlined into `role-pilot.md` POST-COMPACT RELOAD** — closes the gap where F085's rules existed in mode/SKILL.md but didn't prime the Pilot at session start (the cause of the observed "agent keeps asking to commit" symptom).
