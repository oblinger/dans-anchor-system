---
description: "F232 — spec-vs-code latent-bug audit of the Warden engine (2026-07-06): verified findings register + fix clusters"
---
:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[Warden]] → [[Warden Backlog]] → [F232](hook://p/F232%20—%20Latent-bug%20audit%202026-07-06%20—%20findings%20register)
# F232 — Latent-bug audit 2026-07-06 — findings register

Adversarial spec-vs-code audit of the Warden engine (user-commissioned, Fable recipe: read spec + code, hypothesize divergence, construct concrete breaking inputs, delegate sub-exploration to lighter models, **verify everything they report**). Three scoped sub-explorations (dispatcher parity, scan/compile, daemon/runtime) ran on lighter models; every finding below was verified by direct code read or an executed repro before inclusion. Specs audited against: [[Warden Architecture]], [[Warden Interface]], [[Warden Semantics]], [[FCT Ruleset]], [[Warden PRD]].

Each finding: **status** (CONFIRMED = repro executed or code-read proven; LATENT = proven possible, no live trigger yet), the failure scenario, and its fix cluster (backlog row).

## A · Corpus integrity — scanner and compiler (→ T010, T011)

- **A1 · Fence-blind scanning — CONFIRMED, live contamination.** `warden_scan`/`warden_compile` track no code-fence state, while [[FCT Ruleset]] explicitly promises "fence-aware: fenced *example* RULESETs are skipped." A fixture proved a fenced example compiles into a firing rule; the live corpus has **19 fenced sentinels scanned**, and the production IR carries phantom rulesets `R-sample` and `R-wp` (documentation examples), `R-wp-01` keyed by the widely-adopted `facet` trait. `R-diagram`'s fenced twin currently loses only by alphabetical scan order; the real `R-testing-01` survived its fenced twin by parse-shape luck. This is the F251 19-MB-incident mechanism, still armed.
- **A2 · Silent, inconsistent rule-id collisions — CONFIRMED.** Corpus mode is first-wins (`continue`), single-ruleset mode is last-wins (plain dict assignment); neither emits a diagnostic, though [[FCT Ruleset]] § diagnostics lists `rule-id-collision`. With A1, a fenced example of a real rule id can silently displace the real rule depending on scan order.
- **A3 · `canonical_moment` validates nothing — CONFIRMED.** A typo'd class (`toool:pre`) or a trailing comment (`tool:pre  # note`) compiles into a garbage moment key that never fires — the rule is silently dead. No moment-vocabulary check exists.
- **A4 · Dual `def guard` + `def body` in one rule — CONFIRMED.** Kind detection stops at the first entry-def, so the body is never wired (`body_py` unset), and `_encapsulate` renames only the first def — the second leaks verbatim into the emitted module where same-named defs from different rules shadow each other. Silent.
- **A5 · First-`python`-fence-wins — CONFIRMED.** A rule showing an illustrative fence before its real implementation has the real logic silently discarded; an unclosed fence drops the body entirely.
- **A6 · Bare-name `include::` silently dropped — CONFIRMED.** [[FCT Ruleset]] documents `include:: R-sugiyama, R-c4` as legal; the compiler only extracts `[[…]]` forms. Not live-triggered (all current includes use brackets) — a landmine.
- **A7 · Include-fragment refs silently contribute zero rules — CONFIRMED** (heading-fragment targets that don't match `RULESET R-*` resolve to nothing, no warning); cycles/self-includes are safe but equally silent.
- **A8 · Empty `when::` silently reclassifies the rule as a doc-rule — CONFIRMED.**
- **A9 · Stale compile cache — CONFIRMED, narrow.** The cache key is the md scan hash only: `.anchor` trait edits and compiler-code changes don't invalidate. The `warden compile` CLI bypasses the cache (always recompiles), so exposure is the `warden-compile` entrypoint only.

## B · Daemon and runtime (→ T012, T013 Q1, T014)

- **B1 · Serial daemon = cross-session blocking — CONFIRMED.** One accept-handle loop, no concurrency primitive. A slow request (an `audit` op, or a rule body calling `ask_oracle` — 60 s subprocess timeout) blocks **every session's hooks**; the Rust client waits up to 20 s per call. [[Warden Interface]]'s "never blocking" holds for a dead daemon, not a slow one.
- **B2 · Python-bodied deny is best-effort — CONFIRMED.** All four R-pathguard vetoes are `body_py`; when the daemon is busy/down the Rust dispatcher skips owed steers and the guarded Edit/Write **proceeds un-vetoed**. Now documented in [[Warden Interface]] § Non-guarantees; a guarantee-grade path is a design question (T013 Q1).
- **B3 · Doc-fire re-flattens the corpus per write — CONFIRMED, measured.** `fire_on_write` re-parses the whole R-doc umbrella from ~50 markdown files on **every** markdown write: **~90 ms warm** (measured), 9× the 10 ms write budget — and the AOW branch sits outside the budget-timed region in both dispatchers, so the advisory never sees it. `flatten_umbrella_cached` exists and is unused on this path. Multiplied by B1 across sessions.
- **B4 · `except Exception` misses `SystemExit` — CONFIRMED.** A rule body calling `sys.exit()` kills the whole shared daemon (the docstring promises per-request fail-safe).
- **B5 · Non-atomic compile artifacts — CONFIRMED.** `rules-ir.json` and `rules_all.py` are written sequentially in place; the daemon's per-request mtime check can load a truncated IR (that request's rules skipped) or a new-IR/old-module mismatch; an interrupted compile leaves every request failing until a successful recompile.
- **B6 · Socket-steal TOCTOU — PLAUSIBLE-CONFIRMED (code-read).** A busy daemon with a full 8-slot backlog refuses the stale-socket probe exactly like a dead one; the prober unlinks the **live** daemon's socket and binds its own — orphan daemon plus a fresh process whose in-memory `TURN_FIRED`/session registry silently reset. Cold-start double-spawn also leaves the bind loser exiting on an uncaught `OSError`.
- **B7 · Mid-response crash retried without idempotency — CONFIRMED (logic).** The Rust client re-submits after a partial response; `TURN_FIRED` dies with the crashed daemon, so a turn-bearing rule can double-fire. Low frequency.
- **B8 · Reval / oracle-cache growth + write races — LATENT.** `reval.json` stores **full file text** per (rule, file) with no GC and whole-blob rewrite per mark (cost grows with history); `warden fire` CLI runs an independent in-process store that can clobber the daemon's writes last-wins. `oracle-cache.json` is uncapped and non-atomic. No store files exist yet on this machine — latent, will materialize with file-bearing/oracle rule adoption.

## C · Dispatcher parity — Rust vs Python reference (→ T015)

- **C1 · `find_anchor` doesn't canonicalize in Rust — CONFIRMED.** Python `resolve()`s (absolutizes + follows symlinks) before walking; Rust walks the literal path. A relative `file_path` or a symlinked tree (`~/.claude/skills` → ob-skills is exactly such a path) resolves to **different governing anchors** on the two engines — different rules fire for the same event. Python's semantics are the intended ones (F229: the file's anchor owns the file).
- **C2 · `.anchor` `traits:` parsing diverges on edge shapes — CONFIRMED.** Rust locks onto the first `traits:` line and breaks (even if unparsable) and stops a block list at the first blank line; Python regex-searches the whole file and tolerates blank lines. Duplicate keys or a blank line inside the block list yield different trait sets → different active rules.
- **C3 · Malformed-payload granularity — CONFIRMED.** A non-string `skill`/`file_path` field, a non-UTF-8 `.anchor`, or a bucket referencing a missing rule id aborts Python's **entire** dispatch (blanket catch → zero steers) while Rust degrades gracefully per-field and still emits legitimate steers. Reference-hygiene: align Python to graceful degradation.
- **C4 · `turn_bearing`/`file_bearing` absent from the Rust IR schema — LATENT, currently masked.** Turn-bearing rules always compile with Python guards/bodies today (the `agent.*` reference lands in `guard_py`), so the daemon re-applies the gate; a future declaratively-expressed turn-bearing rule would fire ungated in Rust.
- **C5 · F231 considered-set asymmetry — FIXED in this audit's pass** (same-day bug in the new fire-record code: Rust omitted guard-gated rules from `considered` and derived the owed-budget from the surviving plan; both now mirror the Python reference).

## D · Cross-cutting

- **D1 · Deny sentinel is unvalidated in-band signaling — CONFIRMED (executed).** Any steer string beginning `DENY: ` at PreToolUse becomes a real `permissionDecision: deny` — a `tell` that quotes the sentinel (docs example, echoed input) escalates advisory → veto. Authoring-side validation or an out-of-band action channel would close it.
- **D2 · Installed-surface drift check absent — no live gap today.** Every IR moment is currently deliverable by the installed hooks (verified), but nothing warns when a `when::` moment has no installed hook — the class that hid the F131 veto surface for a day. A compile-time warning is cheap (folded into T011).

## Status

**Ready** — findings verified and clustered; fixes tracked as T010 (fence + collisions), T011 (compile robustness + moment vocabulary), T012 (daemon hardening + doc-fire cache), T013 (concurrency/veto posture — Q1 pending), T014 (store growth, Later), T015 (parity alignment). C5 fixed and B2 documented in-pass.
