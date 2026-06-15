---
description: "MUX Testing — strategy + proposed-tests overview"
status:: accepted
---
# MUX Testing

| Type             | Count                | Coverage Target                                                                          | Description                                                                                                      |
| ---------------- | -------------------- | ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Unit             | ~426 in `cargo test` | **Strong** — every public function in `core/src/` has a golden-path test                 | Pure-function Rust tests, no I/O beyond mocks. Default kind; trait-pluggable effectors keep boundaries testable. |
| Integration      | 9 (proposed)         | **Strong** — every subsystem boundary in [[MUX Architecture]]                            | Real internal dependencies (real dispatcher + data, mock shell). Runs in `cargo test` on every push.             |
| Live integration | 22 (proposed)        | **Heavy** — every user-visible interaction has a recipe within one mint of shipping      | Real tmux + real WKWebView on real macOS. `bash + osascript` recipes via `just test-*`. Load-bearing tier.       |
| Subjective       | 12 (proposed)        | **Strong** — every screen the user can land on has a `## Looks like` spec + a check      | Screencap of app state + `## Looks like` spec → LLM scores match/mismatch. Catches the "looks wrong" class.      |
| End-to-end       | 7 (proposed)         | **Bounded** — one per user story (US-MUX-1 … US-MUX-7)                                   | `muxux` binary driven via osascript / IPC; observe DIAG log + state-file + window-frame deltas.                  |

**TLDR**
- **GUI-app posture** — investment leans on what the user sees, not what the compiler verifies.
- **Load-bearing tiers** — live integration recipes (osascript + real WKWebView + real tmux) and subjective LLM-verified visual checks (screencap vs `## Looks like` spec in feature doc).
- **Baseline tiers** — unit + integration cover pure logic underneath; one e2e per user story.
- **Five kinds** — unit / integration / live / subjective / e2e. No property-based, perf, or frontend-unit in v1.
- **Scope column** — every test row tags itself with subsystems / file globs / behavior tags / feature numbers.
- **Relevance gate** — LLM reads the diff + scopes per commit, runs only the plausibly-affected tests.
- **Nightly sweep** — full suite runs once a day to catch long-tail drift the gate skipped.
- **Tier mapping (per [[DSC verification]])** — Tier 1 = relevance-gated agent suites; Tier 2 = nightly sweep; Tier 3 = user dogfooding; Tier 4 = explicit steps in `## Success Criteria`.


## Overview

MuxUX is an 11-subsystem Tauri overlay sitting between macOS UI APIs (AppKit, AX, CGEvents) and tmux — a GUI app where most of what can break breaks at the interface boundary. The testing posture reflects that: **heavy live integration + subjective visual verification, baseline unit + integration coverage for pure logic**. The agent-runnable suites (unit + integration, ~426 `#[test]` and growing) catch regressions in pure logic; the live-integration recipes catch the macOS-bound flows that mocks would lie about (paste, drag-drop, hover, multi-monitor, permission gates); the subjective suite catches the "it works but it looks wrong" class (cardinal zones don't render, watermark doesn't fade, slug color drift) by capturing real bitmaps and asking an LLM to compare them against textual "should-look-like" specs that live in feature docs. **Relevance gating** (per § Relevance Gating below) decides which tests run on each edit vs which defer to a nightly sweep, so the long-tail live + subjective suites stay tractable in the per-commit loop.


## Strategy

### Test Kinds

- **Unit** — pure-function or single-component Rust tests with no I/O beyond mock dispatchers and in-memory state. Most tests are here (current count: ~287 in `core`). Trait-pluggable effectors (`Shell` vs `Mock`) make Effectors unit-testable; pure `Data` types are trivially unit-testable.
- **Integration** — exercise the boundary between two or more subsystems with real internal dependencies (real `MUX-Dispatcher`, real `MUX-Data`, mock `MUX-Effectors` where the boundary is shell-out). Run in CI as part of `cargo test`. Includes the existing `cargo test --features e2e` launch test.
- **Live integration** — exercise the surface against a real tmux server and a real WKWebView on a real macOS host. Implemented as `bash + osascript` recipes invoked via `just test-*`, AND as `cargo test --features live` for tmux-state mutations from Rust. Gated so they don't run unattended in CI. **This is the load-bearing tier for MUX** — most user-visible failures (paste failing, drag-drop misrouted, hover state stuck, multi-monitor placement wrong, permission gates regressing, handoff transitions stuttering) only surface here. The recipe inventory should grow with surface area, not lag it.
- **Subjective (LLM-verified visual)** — capture a real-time bitmap of the app in a specific state (cardinal zones summoned, submenu hovered, watermark visible, F125 popup open, multi-monitor active) and ask an LLM to score it against a textual "should-look-like" spec lifted from feature docs / PRD / UX. The LLM returns pass/fail + reasoning; the test asserts pass. Catches the "compiles, ships, but looks wrong" class (color drift, z-order regressions, layout overflow, font fallback, fade timing) that unit + integration + live can mechanically miss because they don't have eyes. Implementation outline lives in § Subjective implementation notes below.
- **End-to-end** — one per user story in [[MUX PRD]] § User Stories. Invoke the `muxux` binary as a subprocess, drive it with synthesized input (osascript / IPC), observe DIAG log lines + state-file deltas + window-frame deltas. Five to seven at full coverage; v1 ships three to five.

The five kinds above are the full inventory. MUX deliberately does NOT use: property-based tests (no load-bearing universally-quantifiable invariants in v1 — the parts-catalog expander and the layout convergence loop are candidates if schedule allows), performance tests (submenu-latency is the only soft SLO; one targeted live recipe covers it, sufficient for v1), frontend unit tests (the TypeScript surface is thin glue between Tauri IPC and DOM; covered through live + subjective).

**Subjective implementation notes.** Mechanism: a Rust + bash harness that drives the app into the target state (osascript clicks, hotkeys, IPC nudges), waits for the visual to settle (post-render quiesce, watermark-fade timer, layout-realize idempotence), screencaptures the relevant window region via `screencapture -R <rect>` (or full-window via `-l <window-id>`), and hands the resulting PNG + the spec text to an LLM via the Anthropic API. LLM is told the spec, shown the screenshot, and asked: *"Does this match? If no, name the specific mismatch."* The test asserts a pass verdict; failure prints the LLM's reasoning. Specs live in feature docs under a `## Looks like` H2 (or `## Success Criteria § Visual` per [[DSC verification]]) — bullet form, prose, no images of "expected output" (the LLM-vs-LLM comparison would degenerate). When a feature doc lacks a `## Looks like` section, the test is bracketed as roadmap rather than skipped.

### Completeness Targets

- **Unit** — every public function in `core/src/` has at least one unit test exercising its golden path. Module-level convention: a `mod tests` block at the bottom of each `.rs` file. Tauri-side IPC handlers have at least one happy-path test where mockable. Edge cases are added as bugs surface; not pre-targeted.
- **Integration** — every subsystem boundary in [[MUX Architecture]] has at least one integration test:
  - MUX-Dispatcher ↔ MUX-Sensors (event ingress, dedup, pane-level serialization)
  - MUX-Dispatcher ↔ MUX-Engines (layout realization round-trip)
  - MUX-Dispatcher ↔ MUX-Effectors (event-out, command formatting under the `Mock` impl)
  - MUX-Engines ↔ MUX-Data (Layout/Expr/Parts tree mutations)
  - MUX-Effectors ↔ MUX-Native-Bridge (AX trust gates, NSWindow observer wiring)
  - MUX-Frontend ↔ Tauri IPC (Rust ⇄ TypeScript request/response contract)
  - MUX-Launcher ↔ children (spawn dedup, MUXUX_NO_DMUX env gate, handoff promote/collapse)
  - MUX-Logging ↔ structured logsink (channel filtering, ordering)
- **Live integration** — **the load-bearing tier; coverage scales with UI surface area, not lags it.** Bar: *every user-visible interaction has a live recipe within one feature mint of the feature shipping.* Inventory grows as the surface grows; the recipe is part of the mint, not a follow-up. v1 baseline: paste, image-drop, title-rename (synthetic + real-mouse), session-leak detection, session-spawn, startup-restores-claude, suspension, submenu-latency, plus the live-Rust suite (`cargo test --features live`). v1 commission additions: F125 popup show/dismiss, F091 tab strip click-switch, F121 history popup recall, F085 watermark visibility + color match, F092 expanded-mode auto-launch, F079 single-bundle glow propagation, F107 graceful shutdown on signal, F108 broken-state self-heal. Roadmap-tier additions: pin-mode glow tracking (F080/F083), Cmd+J compact↔expanded handoff visual transition, multi-monitor disconnect/reconnect placement, AX-permission re-grant first-launch flow, DMUX dictation→target send round-trip.
- **Subjective** — every screen shape the user can land on has a `## Looks like` spec somewhere reachable (feature doc preferred; PRD or UX fine; bare-bracket roadmap if not yet authored). v1 baseline: cardinal zones at summon, submenu hover state, watermark steady + fading, tmux status-bar slug-block, F125 popup positioning, F121 history-popup right-justification, title-strip rename input, tab strip multi-tab rendering. The bar is "if the user could open a feedback ticket that says *'it looks wrong'*, the surface needs a subjective test."
- **End-to-end** — exactly one e2e per user story in [[MUX PRD]] § User Stories. Seven user stories → seven e2e tests at full coverage; v1 ships with three to five (US-MUX-1, US-MUX-2, US-MUX-4 as priority) and adds the remainder during Drive.

### Responsibilities

- **Unit tests** — agent on `/mint`. Every feature mint that touches `core/src/` or `tauri/src/` writes the unit tests as part of the mint. CLAUDE.md's "No silent fallbacks" + "Single code path" rules make this enforceable: a fallback path with no test fails review.
- **Integration tests** — agent on `/mint` when the feature crosses a subsystem boundary listed above. The boundary inventory is the trigger list.
- **Live integration tests** — agent drafts the bash/osascript recipe under `scripts/integration-*-test.sh` *as part of the mint* (not as a follow-up); user reviews the recipe at the same `/finalize` checkpoint as the feature itself. Required for any feature touching the UI surface.
- **Subjective tests** — agent on `/mint`. The mint that ships a UI feature also (a) adds the `## Looks like` H2 to the feature doc with the textual spec, and (b) wires the screencap→LLM harness row. User reviews the spec text at `/finalize` (the LLM-judged pass/fail is downstream of the spec the user authored). If the user authored no `## Looks like`, the agent drafts one and the user accepts/edits.
- **End-to-end tests** — author-curated initially. Agent drafts the test harness; user signs off on the e2e because each one is a user-story spec turned into executable form.
- **Relevance gate** — agent on every commit (per § Relevance Gating). The agent reads the diff, reads the test inventory's Scope columns, decides which tests are relevant, and runs only those. Nightly sweep runs everything regardless.
- **CI** — runs `cargo test` (unit + integration) on every push — these are deterministic and fast enough to run unconditionally. Live + subjective + e2e are gated through the relevance machinery; nightly host-runner sweep (planned) re-runs them all. Until the nightly runner exists, the user runs `just test-live` before any live-touching merge.

### Tier Mapping

Per [[DSC verification]]:

- **Tier 1 (agent-immediate)** — satisfied by unit + integration tests, all of which run in `cargo test` in under a minute. Also satisfied by relevance-gated live + subjective runs on the changed surface (LLM-judged scope match → run-now; pass → Tier 1 satisfied for that feature). Default tier for MUX features whose surface area is well-scoped.
- **Tier 2 (agent-over-time)** — satisfied by the nightly sweep: every live + subjective + e2e test runs regardless of relevance, on a macOS host runner (planned; not yet provisioned). Drift in the long tail of "features I didn't touch this week" surfaces within a day. Until the nightly runner exists, Tier 2 falls back to the user running `just test-live` + the subjective harness before merging touch to the live surface.
- **Tier 3 (user-passive)** — satisfied by the user dogfooding MuxUX in their daily workflow. The user is the only daily user; surface-area issues surface within hours of merge. CLAUDE.md's "Always commit after shipping; don't ask" + "Rebuild + redeploy without asking" disciplines make this loop tight.
- **Tier 4 (user-explicit)** — fallback only. Used when a feature touches a flow that is not exercised in daily use (e.g., external-monitor disconnect, fresh-permission-grant first launch, two-app handoff under specific failure modes). Each Tier-4 verification spells out the explicit steps in the feature doc's `## Success Criteria` block per [[DSC verification]].


## Relevance Gating

Live + subjective + e2e tests are slow (seconds to minutes each, plus an LLM round-trip for subjective). Running them all on every commit is wasteful; running none of them on every commit is reckless. **Relevance gating** picks the right subset per commit: the tests that exercise the surface the commit touched run now; everything else defers to the nightly sweep.

The mechanism is LLM-decided, not mechanically rule-based. A purely path-glob gate would miss real coverage (e.g. a rename in `core/src/data_types.rs` that quietly changes a serialized field shape — touches no test path, breaks every integration test). The LLM reads the diff + every test's Scope + Exercises columns and decides "is this test plausibly affected?" The bias is **recall over precision**: false-positives (running a test that didn't need to run) cost wall-clock; false-negatives (skipping a test that needed to run) cost a regression slipping to nightly. When in doubt, the LLM runs.

### Scope column

Every row in every `## Proposed Tests` table carries a **Scope** column naming the system surfaces the test exercises. The column is consulted by the relevance gate to decide whether a diff touches anything the test covers. Scope grammar:

- **Subsystem names** from [[MUX Architecture]] (`MUX-Dispatcher`, `MUX-Engines`, `MUX-Effectors`, `MUX-Data`, `MUX-Native-Bridge`, `MUX-Frontend`, `MUX-Launcher`, `MUX-Logging`, `MUX-Sensors`, `MUX-Reference`, `MUX-Permissions`). Coarse-grained but accurate.
- **File globs** (`core/src/parts/**`, `frontend/terminal.ts`, `tauri/src/ipc.rs`) when the subsystem is too coarse and a specific module is what matters.
- **Behavior tags** (`layout-convergence`, `parts-expansion`, `slug-color`, `glow-tracking`, `handoff-promote`, `tcc-permissions`, `tab-strip`, `submenu-render`) when the test exercises an emergent behavior cutting across subsystems.
- **Feature-doc refs** (`F125`, `F091`) when the test is the verification surface for a specific feature.

Multiple entries comma-separated. The LLM matches generously: a diff touching `core/src/layout/convergence.rs` triggers tests scoped `MUX-Engines`, `core/src/layout/**`, AND `layout-convergence`.

### Cadences

| Cadence | Trigger | Suite scope |
|---|---|---|
| **Per-commit (always)** | Every commit, push, or in-flight save during `/mint` | All unit + integration tests (`cargo test`). Fast enough to run unconditionally. |
| **Per-commit (gated)** | Same trigger | The subset of live + subjective + e2e the relevance gate marked relevant. |
| **Pre-merge** | Before merging to `main` | All gated tests run regardless of relevance — guards against the relevance gate's false-negatives. |
| **Nightly sweep** | 2 AM local on the macOS host runner | Every live + subjective + e2e regardless of relevance. Surfaces decay in the long tail. |
| **On-demand** | `just test-live` (existing) + `just test-subjective` (planned) + `just test-all` | User invokes manually when an inquiry crosses surface area larger than the diff suggests. |

### Skip / run signals

The relevance gate considers these signals before deciding:

- **Run** if any of: diff overlaps test Scope; test is new (not seen by gate before); test failed in the last sweep; user added `[relevance-force-run]` to the commit message; the diff is to anything in `core/src/data_types.rs` (cross-cutting, always rerun integration + e2e).
- **Skip** if all of: diff doesn't overlap Scope; test passed in the last sweep; commit message doesn't override.
- **Always-run guards** (override skip): a test that depends on a file touched in *any* of the diff's renames or move operations always runs (renames can silently break wiki-links and serialization compat); subjective tests whose `## Looks like` spec was edited always run (spec changed → re-verify against the new spec).

### Test inventory format

The gate consumes the Proposed Tests tables in this file as authoritative input. The Scope column is mandatory (an empty Scope cell is a gate-config error, not a test that "doesn't have scope"). The agent on `/mint` is responsible for keeping Scope current as code moves.


## Proposed Tests

### Unit

| Test                                          | Exercises                                                              | Scope                                                  | Spec                          |
| --------------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------ | ----------------------------- |
| `test_dispatcher_event_serialization`         | Dispatcher serializes events per pane-id, no cross-pane reorder        | MUX-Dispatcher                                         | [[MUX-Dispatcher]] § Tests    |
| `test_dispatcher_dedup_within_window`         | Identical event arriving within dedup window is dropped                | MUX-Dispatcher                                         | [[MUX-Dispatcher]] § Tests    |
| `test_layout_realize_idempotent`              | Calling `realize()` twice with same State produces no extra commands   | MUX-Engines, layout-convergence                        | [[MUX-Engines]] § Tests       |
| `test_layout_convergence_to_target`           | Engine emits exactly the commands needed to converge from A to B       | MUX-Engines, layout-convergence                        | [[MUX-Engines]] § Tests       |
| `test_parts_catalog_substitute_roles`         | ROW/COL parts file expands roles → concrete agent names                | MUX-Engines, parts-expansion                           | [[MUX-Engines]] § Tests       |
| `test_layout_snapshot_round_trip`             | Serialize and deserialize current layout — no field loss               | MUX-Data, core/src/data_types.rs                       | [[MUX-Data]] § Tests          |
| `test_layout_parser_valid_inputs`             | Parts.md DSL parses an inline corpus of valid expressions (the doc's earlier `core/src/parts/fixtures/` dir never existed — corrected 2026-06-11 per M5) | MUX-Data, core/src/parts/**, parts-expansion           | [[MUX-Data]] § Tests          |
| `test_layout_parser_rejects_malformed`        | Malformed ROW/COL fail with line-localized error, not panic            | MUX-Data, core/src/parts/**, parts-expansion           | [[MUX-Data]] § Tests          |
| `test_settings_yaml_load_defaults`            | Missing fields populate from defaults; partial overrides preserved     | MUX-Data, core/src/data_types.rs                       | [[MUX-Data]] § Tests          |
| `test_settings_yaml_save_round_trip`          | Save then load produces identical struct                               | MUX-Data, core/src/data_types.rs                       | [[MUX-Data]] § Tests          |
| `test_effector_shell_command_formatting`      | tmux command strings escape special chars; no shell injection          | MUX-Effectors                                          | [[MUX-Effectors]] § Tests     |
| `test_effector_mock_records_calls`            | `Mock` effector records call order for assertion in integration tests  | MUX-Effectors                                          | [[MUX-Effectors]] § Tests     |
| `test_preflight_detects_tmux_missing`         | Preflight surfaces missing tmux as named error, not generic failure    | MUX-Effectors                                          | [[MUX-Effectors]] § Tests     |
| `test_sensor_hotkey_event_decoding`           | CGEventTap modifier+keycode mapping per platform spec                  | MUX-Sensors                                            | [[MUX-Sensors]] § Tests       |
| `test_sensor_right_click_to_pane_coord`       | NSEvent screen-coord → tmux pane-id resolution                         | MUX-Sensors, submenu-render                            | [[MUX-Sensors]] § Tests       |
| `test_sensor_socket_cli_parses_command`       | `mux` binary's stdin protocol parses every command shape               | MUX-Sensors, cli/**                                    | [[MUX-Sensors]] § Tests       |
| `test_launcher_dedup_no_double_spawn`         | Two simultaneous spawn requests for same anchor produce one child      | MUX-Launcher, handoff-promote                          | [[MUX-Launcher]] § Tests      |
| `test_launcher_muxux_no_dmux_env_gate`        | Spawning compact sibling sets `MUXUX_NO_DMUX=1` in child env           | MUX-Launcher, handoff-promote                          | [[MUX-Launcher]] § Tests      |
| `test_logsink_channel_filter`                 | Lines emitted on disabled channel are not written                      | MUX-Logging                                            | [[MUX-Logging]] § Tests       |
| `test_logsink_structured_field_format`        | Required `t/level/channel` fields present + correctly ordered          | MUX-Logging                                            | [[MUX-Logging]] § Tests       |
| `test_axtrust_polling_caches_recent_result`   | `AXIsProcessTrusted` cached for poll interval, not hammered per call   | MUX-Native-Bridge, tcc-permissions                     | [[MUX-Native-Bridge]] § Tests |
| `test_permissions_tcc_bundle_id_resolution`   | Helper.app bundle-id maps to parent app's TCC entry                    | MUX-Permissions, tcc-permissions                       | [[MUX-Permissions]] § Tests   |

### Integration

| Test                                            | Exercises                                                              | Scope                                                              | Spec                                    |
| ----------------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------ | --------------------------------------- |
| `test_dispatcher_sensor_event_round_trip`       | Sensor emits event → Dispatcher routes → Effector mock invoked         | MUX-Dispatcher, MUX-Sensors                                        | [MUX Dev Docs/MUX-Dispatcher-Sensors]   |
| `test_dispatcher_engine_realize_round_trip`     | Right-click → Dispatcher → Engine → mocked tmux commands emitted       | MUX-Dispatcher, MUX-Engines, layout-convergence                    | [MUX Dev Docs/MUX-Dispatcher-Engines]   |
| `test_dispatcher_effector_command_formatting`   | Event triggers Effector; recorded shell args match expected            | MUX-Dispatcher, MUX-Effectors                                      | [MUX Dev Docs/MUX-Dispatcher-Effectors] |
| `test_engines_data_layout_mutation`             | Engine writes through to Data layer; State invariants preserved        | MUX-Engines, MUX-Data, core/src/data_types.rs                      | [MUX Dev Docs/MUX-Engines-Data]         |
| `test_effectors_native_bridge_ax_gate`          | Effector defers AX-dependent op until `axtrust` flips true             | MUX-Effectors, MUX-Native-Bridge, tcc-permissions                  | [MUX Dev Docs/MUX-Effectors-Native]     |
| `test_frontend_ipc_request_response_contract`   | Every `mux_*` IPC handler accepts its declared payload + returns shape | MUX-Frontend, tauri/src/ipc.rs                                     | [MUX Dev Docs/MUX-Frontend-IPC]         |
| `test_launcher_spawn_handoff_collapse_cycle`    | Spawn compact, promote to expanded, collapse back — single brain alive | MUX-Launcher, handoff-promote, F092                                | [MUX Dev Docs/MUX-Launcher-Handoff]     |
| `test_logsink_async_ordering_under_load`        | 10k events emitted from N threads land in mtime order, no drops        | MUX-Logging                                                        | [MUX Dev Docs/MUX-Logging-Async]        |
| `e2e_launch_no_errors`                          | Existing `cargo test --features e2e` — binary launches, no stderr      | MUX-Launcher, MUX-Frontend                                         | [[tauri/tests/e2e_launch.rs]]           |

### Live integration

| Test                                  | Recipe                              | Exercises                                                       | Scope                                                          | Spec                                                      |
| ------------------------------------- | ----------------------------------- | --------------------------------------------------------------- | -------------------------------------------------------------- | --------------------------------------------------------- |
| `paste`                               | `just test-paste`                   | Cmd+V from clipboard into focused terminal pane                 | MUX-Frontend, frontend/terminal.ts                             | [scripts/integration-paste-test.sh]                       |
| `image-drop`                          | `just test-image-drop`              | Drag image onto terminal → image arrives as pane content        | MUX-Frontend, MUX-Effectors                                    | [scripts/integration-image-drop-test.sh]                  |
| `title-rename` (synthetic)            | `just test-title-rename`            | Synthetic title-strip click → rename input → commit             | MUX-Frontend, title-strip                                      | [scripts/integration-title-rename-test.sh]                |
| `real-title-click`                    | `just test-real-title-click`        | Real mouse click on title strip, no synthetic shortcuts         | MUX-Frontend, title-strip                                      | [scripts/integration-real-title-click-test.sh]            |
| `unknown-session-leak`                | `just test-unknown-session-leak`    | Unknown tmux sessions don't leak into MuxUX state               | MUX-Engines, MUX-Effectors, session-management                 | [scripts/integration-unknown-session-leak-test.sh]        |
| `session-spawn`                       | `just test-session-spawn`           | Cmd+T creates tmux window, frontend reflects new tab            | MUX-Effectors, MUX-Frontend, tab-strip, session-management     | [scripts/integration-session-spawn-test.sh]               |
| `startup-restores-claude`             | `just test-startup-restores-claude` | Boot restores last-known-claude pane state                      | MUX-Launcher, MUX-Engines, layout-convergence                  | [scripts/integration-startup-restores-claude-test.sh]     |
| `suspension`                          | `just test-suspension`              | App-suspension state-save fires before SIGSTOP                  | MUX-Launcher, F107                                             | [scripts/integration-suspension-test.sh]                  |
| `submenu-latency`                     | `just test-submenu-latency`         | Right-click → submenu visible within latency budget             | MUX-Sensors, MUX-Frontend, submenu-render                      | [scripts/integration-submenu-latency-test.sh]             |
| `test-live-rust`                      | `cargo test --features live`        | Rust-side state mutations against real tmux server              | MUX-Effectors, MUX-Engines                                     | [MUX Dev Docs/MUX-Live-Rust]                              |
| `f125-popup-show-dismiss`             | `just test-f125-popup` *(new)*      | Hover targets/history triggers → popup opens, dismisses on exit | MUX-Frontend, F125, glow-tracking                              | [scripts/integration-f125-popup-test.sh]                  |
| `f091-tab-strip-click-switch`         | `just test-f091-tabs` *(new)*       | Click tab in strip → tmux switches window, frontend updates     | MUX-Frontend, MUX-Effectors, tab-strip                         | [scripts/integration-f091-tabs-test.sh]                   |
| `f121-history-popup-recall`           | `just test-f121-history` *(new)*    | History trigger → popup shows last N entries → click recalls    | MUX-Frontend, F121                                             | [scripts/integration-f121-history-test.sh]                |
| `f085-watermark-visibility-fade`      | `just test-f085-watermark` *(new)*  | Watermark visible on focus → fades after `fade_after_secs`      | MUX-Frontend, frontend/terminal.ts, F085                       | [scripts/integration-f085-watermark-test.sh]              |
| `f092-expanded-auto-launch`           | `just test-f092-autolaunch` *(new)* | DMUX boot with visible windows in state → MuxUX auto-launches   | MUX-Launcher, handoff-promote, F092                            | [scripts/integration-f092-autolaunch-test.sh]             |
| `f079-glow-cross-process`             | `just test-f079-glow` *(new)*       | DMUX-embedded mode: glow renders around correct MuxUX window    | MUX-Native-Bridge, glow-tracking, F079                         | [scripts/integration-f079-glow-test.sh]                   |
| `f107-graceful-shutdown-on-signal`    | `just test-f107-shutdown` *(new)*   | SIGTERM → state.yaml saved, no truncation, no double-save       | MUX-Launcher, F107                                             | [scripts/integration-f107-shutdown-test.sh]               |
| `f108-broken-state-self-heal`         | `just test-f108-selfheal` *(new)*   | Corrupt state.yaml → MuxUX boots with empty default, surfaces warn | MUX-Engines, MUX-Data, F108                                | [scripts/integration-f108-selfheal-test.sh]               |
| `slug-color-watermark-match`          | `just test-slug-color` *(new)*      | tmux status-bar slug-block color == watermark color per anchor  | MUX-Frontend, slug-color                                       | [scripts/integration-slug-color-test.sh]                  |
| `dmux-dictation-target-send`          | `just test-dmux-send` *(new)*       | DMUX dictate → text lands in correct tmux pane via target sys   | MUX-Effectors, MUX-Native-Bridge, glow-tracking                | [scripts/integration-dmux-send-test.sh]                   |
| `multi-monitor-disconnect-reconnect`  | `just test-multi-monitor` *(new)*   | External monitor disconnect → windows reflow → reconnect → restore | MUX-Native-Bridge, MUX-Frontend                             | [scripts/integration-multi-monitor-test.sh]               |
| `ax-permission-regrant-firstlaunch`   | `just test-ax-regrant` *(new)*      | Fresh AX grant on first launch → MuxUX detects, unblocks ops    | MUX-Native-Bridge, MUX-Permissions, tcc-permissions            | [scripts/integration-ax-regrant-test.sh]                  |

### End-to-end

| Test                                   | Exercises (User Story)                                          | Scope                                                            | Spec                          |
| -------------------------------------- | --------------------------------------------------------------- | ---------------------------------------------------------------- | ----------------------------- |
| `e2e_interactive_layout_manipulation`  | US-MUX-1: right-click → cardinal zones → split → new pane lands | MUX-Sensors, MUX-Dispatcher, MUX-Engines, MUX-Effectors, submenu-render | [MUX E2E § US-MUX-1]          |
| `e2e_layout_persistence_round_trip`    | US-MUX-2: snapshot, restart, layout reconstructs identical      | MUX-Engines, MUX-Data, MUX-Launcher, layout-convergence          | [MUX E2E § US-MUX-2]          |
| `e2e_parts_catalog_place`              | US-MUX-3: browse catalog → place composition → pane filled      | MUX-Engines, parts-expansion, submenu-render                     | [MUX E2E § US-MUX-3]          |
| `e2e_pane_targeting_three_paths`       | US-MUX-4: right-click + hotkey + agent-table selection all hit  | MUX-Sensors, MUX-Dispatcher                                      | [MUX E2E § US-MUX-4]          |
| `e2e_session_management_create_rename` | US-MUX-5: create + rename + delete session via Sessions zone    | MUX-Effectors, session-management, submenu-render                | [MUX E2E § US-MUX-5]          |
| `e2e_layout_capture_round_trip`        | US-MUX-6: capture current layout → reappears in catalog → place | MUX-Engines, parts-expansion, layout-convergence                 | [MUX E2E § US-MUX-6]          |
| `e2e_declarative_realize_idempotent`   | US-MUX-7: `realize(State)` twice → no extra commands second pass | MUX-Engines, layout-convergence                                 | [MUX E2E § US-MUX-7]          |

### Subjective

LLM-verified visual checks. Each row drives the app into the named state, screencaptures the relevant region, and hands (PNG + spec text) to an LLM with the prompt *"Does this match the spec? If not, name the specific mismatch."* The Spec column points to the `## Looks like` H2 in the named feature doc (or PRD/UX section). Bare-bracket entries mark a `## Looks like` H2 that hasn't been authored yet — those tests stay in `drafting` state until the spec lands.

| Test                                  | State to capture                                            | Scope                                       | Spec                                         |
| ------------------------------------- | ----------------------------------------------------------- | ------------------------------------------- | -------------------------------------------- |
| `subj_cardinal_zones_summoned`        | Right-click a pane; four zones visible with center input    | MUX-Frontend, submenu-render                | [[MUX UX Design]] § Cardinal Zones           |
| `subj_submenu_hover_state`            | Hover a sub-item; highlight band + slug-color tint visible  | MUX-Frontend, submenu-render, slug-color    | [F107 Submenu Hover § Looks like]            |
| `subj_watermark_visible_at_focus`     | Focus terminal; watermark slug + color visible              | MUX-Frontend, frontend/terminal.ts, F085    | [[MUX UX Design]] § Watermark / [F085 § Looks like] |
| `subj_watermark_fades_after_timeout`  | Focus terminal; wait `fade_after_secs`; watermark gone      | MUX-Frontend, F085                          | [F085 § Looks like]                          |
| `subj_status_bar_slug_color_match`    | tmux status bar: slug block color matches watermark         | MUX-Frontend, slug-color                    | [slug-color § Looks like]                    |
| `subj_f125_targets_popup_position`    | Hover Targets trigger; popup directly below, right-justified | MUX-Frontend, F125                         | [[F125 — Targets popup]] § Looks like        |
| `subj_f125_history_popup_position`    | Hover History trigger; popup directly below, full content   | MUX-Frontend, F121, F125                    | [[F121]] § Looks like                        |
| `subj_title_strip_rename_mode`        | Click title strip; rename input visible, focus, cursor      | MUX-Frontend, title-strip                   | [title-strip § Looks like]                   |
| `subj_tab_strip_multi_tab`            | 2+ tmux windows; tab strip visible with one tile per window | MUX-Frontend, tab-strip, F091               | [[F091]] § Looks like                        |
| `subj_glow_around_target_window`      | DMUX target set; green glow visible around target's bounds  | MUX-Native-Bridge, glow-tracking, F079      | [F079 § Looks like]                          |
| `subj_compact_to_expanded_handoff`    | Cmd+J from compact; expanded window in place of compact     | MUX-Launcher, handoff-promote, F092         | [F092 § Looks like]                          |
| `subj_multi_monitor_window_placement` | External monitor connected; MuxUX window on the chosen one  | MUX-Native-Bridge, MUX-Frontend             | [multi-monitor § Looks like]                 |

Bare-bracket entries (e.g. `[MUX Dev Docs/MUX-Dispatcher-Sensors]`, `[F107 Submenu Hover § Looks like]`) mark proposed-but-unwritten low-level specs or `## Looks like` H2s. Each becomes a `[[wiki-link]]` once the destination doc gains the referenced block.


## See also

- [[CAB Testing]] — facet spec this doc follows
- [[MUX PRD]] — user stories that drive the e2e inventory
- [[MUX Architecture]] — subsystem boundaries that drive the integration inventory
- [[MUX Decisions]] — D-MA01..05 (TCC permissions), single-dispatcher commitment make deterministic testing possible
- [[DSC verification]] — four-tier verification discipline mapped above
- [[design]] — parent orchestrator skill
- [[design-testing]] — authoring sub-skill for `/design testing`
