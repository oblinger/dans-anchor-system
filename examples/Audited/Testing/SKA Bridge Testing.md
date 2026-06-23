---
description: "SKA Bridge Testing — strategy + proposed-tests overview"
status:: drafting
---
# SKA Bridge Testing
How the Bridge skill is verified: the kinds of test, how much of each, and the concrete inventory consistent with that strategy.

| -[[SKA Bridge Testing]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[SKA Bridge]] → [[SKA Bridge Design]] → [SKA Bridge Testing](hook://p/SKA%20Bridge%20Testing)<br>: test strategy + proposed tests |
| --- | --- |
| Anchor | [[SKA Bridge Design]] (parent) |
| Related | [[SKA Bridge PRD]],  [[SKA Bridge UX Design]],  [[DSC verification]],   |

**TLDR**
- **Two-machine posture** — center of gravity is integration testing against a real remote; most logic is I/O orchestration.
- **Four kinds** — unit / integration / e2e / property. Unit covers the small pure-logic islands; integration is the load-bearing tier.
- **Integration bar** — every `bridge` verb (Control / Sync / Claude) has a recipe against a reachable host.
- **E2E bar** — exactly one "twin" scenario proves the composite goal.
- **Property bar** — one hard invariant: `~/.claude/projects/` never lands on the remote.

## Overview

Bridge is inherently a **two-machine** system, so its center of gravity is **integration testing against a real remote** — most of the logic is I/O orchestration (SSH, REST, rsync) that unit tests can't meaningfully cover. Unit tests cover the small islands of pure logic in the helper scripts; the e2e tier ties the kinds together into the "twin" scenario; one property test guards the hard transcript-exclusion invariant. The harness is `bridge-test.sh` under the skill folder — it runs the runnable tiers and prints mechanical PASS/FAIL per the [[CLAUDE.md]] no-manual-reproduction discipline.

## Strategy

### Test Kinds

- **Unit** — pure-logic islands in the helper scripts, no remote required. Scope: config load/migration, manifest include/exclude resolution, `.stignore` intent.
- **Integration** — every verb exercised end-to-end against the live test remote, grouped by bridge kind (Control / Sync / Claude). The load-bearing layer.
- **End-to-end** — one full "twin" scenario: fresh host → sync + claude → run Claude on the twin and confirm it is the same agent.
- **Property / invariant** — one hard invariant guarded after every claude-bridge op.

The four kinds above are the full inventory. Bridge deliberately does NOT use: performance tests (no SLO worth a tier in v1) or fuzz tests (the input surface is a hostname + a verb).

### Completeness Targets

- **Unit** — **Bounded.** Each pure-logic island in the helper scripts (config migration, defaults, manifest exclude, `.stignore` intent) has at least one test. The rest is I/O and out of scope for unit.
- **Integration** — **Strong.** Every `bridge` verb across all three bridge kinds (Control, Sync, Claude) has at least one integration recipe against a reachable host. Tests skip-with-warning (not fail) when no remote is reachable.
- **End-to-end** — **Bounded.** Exactly one e2e — the "twin identity" scenario that proves the composite goal.
- **Property / invariant** — **Bounded.** One invariant: transcripts never travel. Checked after every claude-bridge op.

### Responsibilities

- **Unit tests** — agent on `/mint`. Every mint touching a helper script's pure-logic island writes the unit test as part of the mint.
- **Integration tests** — agent drafts the recipe in `bridge-test.sh`; the user reviews at `/finalize` because each asserts behavior against a real remote.
- **End-to-end tests** — author-curated. The agent drafts the harness; the user signs off because the twin scenario is the composite goal turned executable.
- **Property tests** — agent on `/mint`. The invariant guard runs as part of the integration harness.
- **CI** — the harness runs the runnable tiers on demand (`bridge-test.sh <host>`); destructive / manual recipes are gated. A reachable test remote is required for integration + e2e.

### Tier Mapping

Per [[DSC verification]]:

- **Tier 1 (agent-immediate)** — all unit + integration tests with a reachable remote, deterministic PASS/FAIL via `bridge-test.sh`.
- **Tier 2 (agent-over-time)** — the e2e twin scenario when it needs a convergence soak.
- **Tier 3 (user-passive)** — "does the twin actually feel like this machine in normal use?" surfaces in daily dogfooding.

## Proposed Tests

### Unit

| Test | Exercises | Spec |
| --- | --- | --- |
| `T-cfg-migrate` | Legacy flat `defaults.yaml` migrates to nested `config.yaml` shape | [SKA Bridge Dev Docs/Config § Tests] |
| `T-cfg-defaults` | `defaults --set` writes nested shape; legacy flat names map through | [SKA Bridge Dev Docs/Config § Tests] |
| `T-manifest-exclude` | `projects` is always in the resolved exclude set, regardless of includes | [SKA Bridge Dev Docs/Provision § Tests] |
| `T-stignore-intent` | `.claude/` path resolves `ignored: true`; normal `.md` path `ignored: false` | [SKA Bridge Dev Docs/Sync § Tests] |

### Integration

| Test | Bridge kind | Exercises | Spec |
| --- | --- | --- | --- |
| `T-ctl-ssh` | Control | Key-auth SSH returns remote hostname, no password prompt | [SKA Bridge Integration § Control] |
| `T-ctl-fda` | Control | tmux-pane TCC-protected command succeeds (FDA inherited); plain SSH denied | [SKA Bridge Integration § Control] |
| `T-syn-pair` | Sync | Each daemon's device ID appears in the other's device list | [SKA Bridge Integration § Sync] |
| `T-syn-forward` | Sync | File written on dev Mac appears on remote within 15 s, identical content | [SKA Bridge Integration § Sync] |
| `T-syn-reverse` | Sync | File created on remote appears on dev Mac within 15 s (two-way) | [SKA Bridge Integration § Sync] |
| `T-syn-moveaside` | Sync | Pre-existing remote content moved to `<folder>.old.<date>/`; nothing leaks back | [SKA Bridge Integration § Sync] |
| `T-syn-teardown` | Sync | Folder share removed from both daemons; files remain on both sides | [SKA Bridge Integration § Sync] |
| `T-syn-fastlink` | Sync | Active connection address is the `169.254.x.x` bridge, not wifi IP (informational) | [SKA Bridge Integration § Sync] |
| `T-cla-apply` | Claude | `skills/` and `CLAUDE.md` land on remote per manifest include set | [SKA Bridge Integration § Claude] |
| `T-cla-verify` | Claude | `twin_ready: true` — skills + CLAUDE.md present, `~/.claude/projects` empty | [SKA Bridge Integration § Claude] |
| `T-cla-idempotent` | Claude | Second `apply` completes with no errors; end state unchanged | [SKA Bridge Integration § Claude] |
| `T-cla-runtime` | Claude | `claude` + `node` + auth present → twin can actually run Claude | [SKA Bridge Integration § Claude] |

### End-to-end

| Test | Exercises | Spec |
| --- | --- | --- |
| `T-e2e-twin-identity` | Run a real Claude session on the remote; it identifies as the SKA Pilot with the synced CLAUDE.md — proves "it's really me" | [SKA Bridge E2E § Twin Identity] |

### Property

| Test | Invariant | Spec |
| --- | --- | --- |
| `T-inv-no-transcripts` | After any claude-bridge op, `~/.claude/projects/` on the remote is absent or empty | [SKA Bridge Integration § Claude] |

Bare-bracket entries (`[SKA Bridge Integration § Control]`) mark proposed-but-unwritten low-level spec destinations — each test's Precondition / Steps / Pass detail moves to the linked block once authored. Status as of 2026-06-11 (manual run against `haorui.local`): 8 PASS, 1 expected FAIL (`T-cla-runtime` — runtime gap), 4 SKIP (manual/destructive). The remaining gaps blocking `T-e2e-twin-identity` are tracked in [[F151 — Bridge integration tests — verify Control _ Sync _ Claude bridges all work|F151]].

## See also

- [[SKA Bridge PRD]] — the requirements each test verifies.
- [[SKA Bridge UX Design]] — the verbs under test.
- [[DSC verification]] — four-tier verification discipline mapped above.
