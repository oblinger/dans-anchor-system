---
description: "test strategy + proposed tests"
status:: drafting
---
# HBR Testing
How Harbor is verified: the kinds of test, how much of each, and the concrete inventory consistent with that strategy.

| -[[HBR Testing]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[HBR]] → [[HBR Design]] → [HBR Testing](hook://p/HBR%20Testing)<br>: test strategy + proposed tests |
| --- | --- |
| Anchor | [[HBR Design]] (parent) |
| Related | [[HBR Architecture]],  [[HBR PRD]],  [[DSC verification]],   |

**TLDR**
- **Library-shaped posture** — heavy unit + integration on catalog logic; live + e2e kept lean because the surface is one CLI plus one LAN page.
- **Catalog is the seam** — the three pipelines (Ingest / Serve / Operate) meet only at SQLite, so integration tests target catalog boundaries.
- **Live tier is real I/O** — real ffmpeg transcode, real byte-range stream, real crash recovery; mocks would lie about exactly these.
- **One e2e per story** — US-HBR-1..5 each get exactly one end-to-end pass, no more.
- **Bar vocabulary** — Strong / Heavy / Bounded / Sampled per kind, no percentages.

## Overview

Harbor is a single Rust binary over one SQLite catalog, fronted by a CLI and a small LAN web page. Most of what can break is **pure catalog logic** — hashing, dedup folding, metadata extraction, checkpoint / restore — which is cheap to test exhaustively in `cargo test`. The posture leans there: **Strong unit + integration coverage of the catalog and the three pipeline boundaries, a small live tier for the genuinely I/O-bound flows (real transcode, real byte-range serve, real crash recovery), and exactly one e2e per user story.** The thin LAN viewer is verified through e2e and a Sampled live check, not a frontend unit suite. Where a mock would lie — ffmpeg behavior on a real codec, SQLite recovery after an unclean shutdown — the live tier uses the real dependency.

## Strategy

### Test Kinds

- **Unit** — pure-function Rust tests over a single component with no I/O beyond a temp dir or in-memory SQLite. Scope: content hashing, dedup decision, metadata parsing, codec-compatibility decision, byte-range math, checkpoint serialization. The default and most numerous kind.
- **Integration** — exercise a pipeline boundary against a **real catalog** (temp SQLite file) with mocked external dependencies (mock ffmpeg, fixture media). Scope: the Ingest write path (Scanner→Importer→Deduper), the Serve read path, and the Operate checkpoint path — the seams in [[HBR Architecture]] where pipelines meet only at the catalog.
- **Live integration** — exercise a flow against the **real external dependency**: real ffmpeg transcode, real HTTP byte-range stream over a socket, real SIGKILL-then-restart recovery. Scope: the handful of flows where mocking the dependency would hide the actual failure mode. The load-bearing tier for Serve and Operate.
- **End-to-end** — drive the `harbor` binary as a subprocess through one full user story, observing catalog rows + emitted stream + exit state. Scope: exactly one per US-HBR-N in [[HBR PRD]] § User Stories.

The four kinds above are the full inventory. Harbor deliberately does NOT use: property-based tests (no load-bearing universally-quantified invariant in v1), performance tests (no SLO beyond "playback starts in a few seconds", covered by one live check), or frontend unit tests (the LAN page is thin glue over the Serve API, covered through live + e2e).

### Completeness Targets

- **Unit** — **Strong.** Every public function in the catalog and pipeline crates has at least one golden-path unit test; the dedup decision, codec-compatibility decision, and checkpoint round-trip additionally get failure-path tests. Edge cases added as bugs surface, not pre-targeted.
- **Integration** — **Strong.** Every pipeline↔catalog boundary in [[HBR Architecture]] has at least one integration test: Ingest write path, Serve read path, Operate checkpoint path.
- **Live integration** — **Heavy** for Serve + Operate (every flow depending on real ffmpeg, real socket I/O, or real crash semantics has a live recipe); **Sampled** for the LAN viewer (one smoke check that the page lists and plays). Bar: every flow whose failure mode a mock would hide gets a live test.
- **End-to-end** — **Bounded.** Exactly one e2e per user story (US-HBR-1..5). No more, no fewer.

### Responsibilities

- **Unit tests** — agent on `/mint`. Every mint touching catalog or pipeline code writes the unit tests as part of the mint.
- **Integration tests** — agent on `/mint` when the feature crosses a pipeline↔catalog boundary. The boundary list above is the trigger.
- **Live integration tests** — agent drafts the recipe (`cargo test --features live` or a `just test-*` script) as part of the mint; the user reviews it at `/finalize` because it asserts behavior against a real dependency.
- **End-to-end tests** — author-curated. Agent drafts the harness; the user signs off because each one is a user story turned executable.
- **CI** — runs `cargo test` (unit + integration) on every push; deterministic and fast. Live + e2e are gated behind `--features live` / `--features e2e`, run pre-merge for any touch to Serve / Operate, plus a nightly sweep (planned).

### Tier Mapping

Per [[DSC verification]]:

- **Tier 1 (agent-immediate)** — unit + integration tests, all in `cargo test` in seconds. Default tier for Ingest and any pure-catalog feature.
- **Tier 2 (agent-over-time)** — the nightly live sweep: real transcode, real serve, real restore-from-backup run regardless of relevance, catching long-tail drift. The Operate backup / restore check lives here.
- **Tier 3 (user-passive)** — the owner streaming from the library in daily use surfaces Serve / viewer issues within hours of merge.
- **Tier 4 (user-explicit)** — flows not exercised daily (full power-loss recovery, a never-seen codec) get explicit steps in the feature doc's `## Success Criteria`.

## Proposed Tests

### Unit

| Test | Exercises | Spec |
| --- | --- | --- |
| `test_content_hash_stable` | Same bytes hash identically across runs; different bytes differ | [[HBR Ingest]] § Tests |
| `test_dedup_folds_identical` | Two files with equal content-hash fold to one catalog entry | [[HBR Ingest]] § Tests |
| `test_importer_reads_metadata` | Title, duration, codec parsed from fixture media into a `media` row | [[HBR Ingest]] § Tests |
| `test_codec_compat_decision` | Device profile + source codec → direct-play vs transcode verdict | [[HBR Serve]] § Tests |
| `test_byte_range_math` | Requested range maps to correct file offsets, clamped at EOF | [[HBR Serve]] § Tests |
| `test_checkpoint_round_trip` | Catalog serialize → checkpoint → restore yields identical rows | [[HBR Operate]] § Tests |

### Integration

| Test | Exercises | Spec |
| --- | --- | --- |
| `test_ingest_write_path_to_catalog` | Scan fixture folder → Importer → Deduper → row count correct, duplicates folded | [HBR Ingest § Boundary] |
| `test_rescan_only_new_files` | Re-scan a watched folder; only new/changed files processed, removed marked absent (US-HBR-2) | [HBR Ingest § Rescan] |
| `test_serve_read_path_direct_play` | Catalog row → Streamer emits byte range for a supported-codec fixture (mock client) | [HBR Serve § Boundary] |
| `test_operate_checkpoint_path` | Backup snapshots catalog on schedule; snapshot reopens with all rows | [HBR Operate § Boundary] |

### Live integration

| Test | Recipe | Exercises | Spec |
| --- | --- | --- | --- |
| `live-transcode` | `cargo test --features live transcode` | Real ffmpeg transcodes an unsupported-codec fixture to a playable profile (US-HBR-4) | [tests/live/transcode.rs] |
| `live-byte-range-serve` | `just test-serve` | Real HTTP byte-range request over a socket returns correct bytes, supports seek | [scripts/live-serve-test.sh] |
| `live-crash-recovery` | `just test-recovery` | SIGKILL mid-ingest → restart resumes from last checkpoint, catalog intact, ingest re-queued (US-HBR-5) | [scripts/live-recovery-test.sh] |
| `live-lan-viewer-smoke` | `just test-viewer` | LAN page lists titles with poster + duration and starts playback (Sampled) | [scripts/live-viewer-test.sh] |

### End-to-end

| Test | Exercises (User Story) | Spec |
| --- | --- | --- |
| `e2e_add_library` | US-HBR-1: `harbor ingest <path>` catalogs media, re-run adds nothing | [HBR E2E § US-HBR-1] |
| `e2e_rescan_on_change` | US-HBR-2: drop a file in a watched folder → it appears without a full re-ingest | [HBR E2E § US-HBR-2] |
| `e2e_browse_and_play` | US-HBR-3: LAN client lists titles and direct-plays a supported codec | [HBR E2E § US-HBR-3] |
| `e2e_transcode_on_demand` | US-HBR-4: unsupported codec still plays, transcoded, no format choice | [HBR E2E § US-HBR-4] |
| `e2e_recover_after_crash` | US-HBR-5: power-loss restart resumes from last checkpoint, catalog intact | [HBR E2E § US-HBR-5] |

## See also

- [[HBR Architecture]] — the three pipelines + catalog seam that drive the integration inventory.
- [[HBR PRD]] — user stories that drive the e2e inventory.
- [[DSC verification]] — four-tier verification discipline mapped above.
