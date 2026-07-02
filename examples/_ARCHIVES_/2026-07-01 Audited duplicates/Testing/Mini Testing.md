---
description: "test strategy + proposed tests"
status:: drafting
---
# Mini Testing
How Mini is verified: the kinds of test, how much of each, and the concrete inventory consistent with that strategy.

| -[[Mini Testing]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[Mini]] → [Mini Testing](hook://p/Mini%20Testing)<br>: test strategy + proposed tests |
| --- | --- |
| Anchor | [[Mini Design]] (parent) |
| Related | [[Mini PRD]],  [[DSC verification]],   |

**TLDR**
- **Library-shaped posture** — heavy unit on the one pure function; one e2e on the CLI surface.
- **Two kinds only** — unit and end-to-end. No integration, property, or live tier in v1.
- **Unit bar** — every public function in `src/` has a golden-path test.
- **E2E bar** — exactly one per user story (one story in v1).

## Overview

Mini is a single-function CLI that reverses a string. The whole surface is one pure function plus a thin `main`, so the testing posture is **heavy unit on the pure logic, one e2e on the CLI**. There is nothing to integrate (one module) and no I/O worth a live tier, so those kinds are deliberately absent.

## Strategy

### Test Kinds

- **Unit** — pure-function tests over `reverse()` with no I/O. The default and only numerous kind.
- **End-to-end** — invoke the `mini` binary as a subprocess and observe stdout/exit-code. Exactly one, covering the single user story.

The two kinds above are the full inventory. Mini deliberately does NOT use: integration tests (one module — no boundary to cross), property-based tests (no load-bearing invariant in v1), or live tests (no real external dependency).

### Completeness Targets

- **Unit** — **Strong.** Every public function in `src/` has at least one golden-path unit test. Edge cases added as bugs surface.
- **End-to-end** — **Bounded.** Exactly one e2e per user story (US-MINI-1). No more, no fewer.

### Responsibilities

- **Unit tests** — agent on `/mint`. Every mint touching `src/` writes the unit tests as part of the mint.
- **End-to-end tests** — author-curated. The agent drafts the harness; the user signs off because it is the user story turned executable.
- **CI** — runs the full suite (unit + e2e) on every push. The suite is small enough to run unconditionally.

### Tier Mapping

Per [[DSC verification]]:

- **Tier 1 (agent-immediate)** — unit + e2e, both run in seconds. The default and only tier for Mini features.
- **Tier 3 (user-passive)** — the author running `mini` in daily use surfaces anything the suite missed.

## Proposed Tests

### Unit

| Test | Exercises | Spec |
| --- | --- | --- |
| `test_reverse_basic` | `reverse("abc")` yields `"cba"` | [Mini Core § Tests] |
| `test_reverse_empty` | `reverse("")` yields `""` | [Mini Core § Tests] |

### End-to-end

| Test | Exercises (User Story) | Spec |
| --- | --- | --- |
| `e2e_reverse_cli` | US-MINI-1: `mini reverse <s>` prints the reversed string | [Mini E2E § US-MINI-1] |

Bare-bracket entries (`[Mini Core § Tests]`) mark proposed-but-unwritten low-level specs. Each becomes a `[[wiki-link]]` once the module doc gains a `## Tests` block.

## See also

- [[Mini PRD]] — the user story that drives the e2e inventory.
- [[DSC verification]] — four-tier verification discipline mapped above.
