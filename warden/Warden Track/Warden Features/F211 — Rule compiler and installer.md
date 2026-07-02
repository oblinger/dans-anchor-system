---
description: "F211 — Rule compiler / installer"
---

# [[Warden]] · F211 — Rule compiler / installer

## Summary

The engine that makes active rules fire **implicitly** at runtime moments — a *compiler*, not an interpreter. It resolves the rules active for an anchor — a pure function of its `.anchor` **traits**, each trait pulling in its omnibus rulesets — indexes each onto its dispatch key (by `when::` moment, or by `where::` place), and **pre-compiles** all rules sharing a moment into one fast module (generalizing today's `/distill`). At fire time the hook subsystem ([[Audit Architecture]]) runs the compiled module for that moment, which checks the residual conjunction and emits steers/fixes. This is the hot path the millisecond budget rides on.

## Success Criteria

**Tier:** 1 (agent-immediate, after F209/F210)
**Blocks next:** [[F212 — Python reference implementation|F212]], [[F213 — Rust performance implementation + ms budget|F213]]

**What done looks like.** Given an anchor's active rule set, the compiler emits per-moment modules; installing them makes a real rule (`R-query-14`, ported) fire at `skill:post:audit-q` with no per-rule wiring, evaluating its residual `where::`/`if::` and emitting the mode-appropriate steer.

**How it will be verified.** A test anchor with two adopted rules on different moments: firing each moment runs only that moment's compiled module; the other rule does not execute (proves indexing). Re-compile is skipped when the active set + rules are unchanged (cache hit).

## Design

1. **Resolve active set** — per anchor, the active-set is the union of its `.anchor` **traits'** rule sets (each trait → its omnibus rulesets, flattened; `{NAME} Rules.md` is active for its own anchor). Compile each trait to a hash-set of rule-ids; at fire time resolve the anchor by a cached path **reverse-index** to `.anchor`. ([[Warden Runtime]] § Activation.)
2. **Index** — choose key per rule (when-major default; where-major when a `when:: always` rule touches a rare path).
3. **Pre-compile** — group by moment; emit one module per moment (the residual `where::`/`if::` checks + each rule's body).
4. **Install** — register each moment's module with the runtime hook surface; cache keyed by (active-set hash, rules hash); invalidate on change.
5. **Fire** — the hook calls the module; module checks **active-set membership** + the residual `where::`/`if::` conjunction; emits steers (agent-directed) + mechanical fixes (safety-floored). Output uses **JSON `deny`/`block`/`reason`**, never exit-code-2 (per [[Warden Survey]] / [[Warden Integration Strategy]] D5).

The interception substrate is Claude Code hooks, used natively behind a thin portability adapter ([[Warden Integration Strategy]] D2); external checker engines (Vale/Semgrep) are opt-in, adapter-isolated, and confined to the explicit audit path (D3) — the compiler's hot-path modules are self-contained native code.

## Status

**Designed 2026-06-26** (this doc + [[Warden Architecture]] §7a).

**Scan command built + tested 2026-07-02** — `warden/engine/warden_scan.py` implements the committed always-scan contract (§ Discovery resolved: scan command + always-freshen): stat-sweep + selective re-read, index schema `{path, mtime_ns, size, hash, ruleset_names[]}` plus a `seen` all-files stat map (so unchanged *non*-bearing files are skipped too), `--rescan` from-scratch build, `--root` as the engine config parameter. Verified against the live root — 112 ruleset files / 116 rulesets; from-scratch 232 ms, an unchanged freshen **reads 0 files in 15 ms**, a touched bearing file re-reads exactly one, and a ruleset added to a previously non-bearing file is caught on the next freshen (the self-freshening property). A standalone regression test (`warden/engine/test_warden_scan.py`, 5 behaviors) pins the read-0 property. The M0 language freeze is complete ([[F209 — Unified trigger taxonomy + when language|F209]]/[[F210 — Conjunction binding + indexing|F210]], 2026-07-02), and the **three M2 engine-design questions are now resolved** (2026-07-02, user): lazy/incremental compile, dual output (shared IR + emitted Python modules; Rust delegates the Python bits), and Python-allowed-everywhere under an operation-cost budget. **F211 is fully designed** — the compile→install→fire contract + the `R-query-14` pilot are buildable.

## Resolved

The M2 engine-design gate — all three resolved by the user 2026-07-02 (Q1 accepted the lean; Q2 accepted the lean and **refined it with a dual output**; Q3 **opened up** rather than confined).

### Q1 — When does the compiler run? — RESOLVED: (B) lazy / incremental ^F211-Q1

Compile an anchor's modules on first entry, matching the daemon's lazy warm-start ([[Warden Runtime]]); never compile anchors a session never visits. (Ties [[Warden PRD]] Q1.)

### Q2 — Compiled module format? — RESOLVED: (B) shared IR + emitted Python modules (dual output) ^F211-Q2

The compiler emits **two coordinated artifacts**:

1. A **shared IR / data-table** for the declarative parts — moment dispatch, `where::` selectors, fixed-vocabulary `if::` guards. Both engines interpret the *same* table (the Python reference and the Rust hot-path engine), so they stay behavior-identical under the differential harness.
2. **Emitted Python modules** holding the functions for the **inherently-Python** parts — arbitrary `if::` expressions and rule bodies outside the fixed vocabulary. These run in the warm Python daemon.

**Rust never embeds a CPython interpreter.** It interprets the IR natively (the fast majority) and, for a rule's Python bits, **delegates to the Python daemon**. IR for what Rust can do in-process; Python modules for what only Python can do; one shared table keeps the two engines identical on the declarative surface. (User's refinement of lean B — per-engine native codegen (C) stays an M8 perf option if table-interpret is too slow.)

### Q3 — Rule-authored Python on the hot path? — RESOLVED: Python allowed everywhere; the limit is an operation-cost budget, not a language/moment ban ^F211-Q3

Rule Python is allowed at **every** moment, including `tool:pre`. The Warden daemon is a **warm, always-running Python process** ([[Warden Runtime]]), so a rule's Python `if::` is not an interpreter launch but an **in-process function call** — microseconds of dispatch plus whatever the body does. A quick predicate (comparison, regex, dict lookup over already-cached `ctx`) is **well under the ~2 ms `tool:pre` budget**.

- **The real constraint is operation cost, not language.** What blows the veto-path budget is slow *work* — a file read, a subprocess, a `git` call, an oracle — in any language. The guard is a **per-moment time/operation budget** plus an authoring lint that flags known-slow operations on `tool:pre`; heavy judgments (the oracle) are already delegated off the hot path ([[Warden Runtime]] § LLM judgments). Quick Python stays quick.
- **Rust-path caveat (M8).** In the Rust deployment, Rust runs declarative (IR) veto rules **in-process** (fast); a **Python-carrying** veto rule makes Rust hop to the Python daemon (a bounded IPC round-trip). This affects only the rare Python-carrying veto rule — most `tool:pre` rules are path/pattern checks = pure IR — so Rust's speedup fully applies to the declarative majority. (Ties [[Warden PRD]] Q2.)

Supersedes the original lean (B) "confine code-carrying rules to `post`": confinement isn't needed once the constraint is framed as cost, not language.

# Discussion

## 2026-07-01 — Rule discovery: how the engine finds where rules live

**Question (user):** structurally, where do rules live and how are they found? Options weighed: convention-named files per ruleset (still a scan); a rules root (fights colocation; still scans every md under it); a frontmatter marker (YAML parse per file — expensive); a manual scan step that captures an index of ruleset-bearing files + mtimes and watches them (self-contained, but new rulesets need a rescan).

**Prior art:** ESLint/Prettier — convention-named configs + declared plugins, discovery follows declarations, never scans; systemd/udev/polkit — fixed `rules.d` roots where *presence = enrollment*; Semgrep — explicit `--config` paths/registry; Cursor — a `.cursor/rules/` root; cargo/LSP — a build-time index kept fresh by events. Two families: follow-the-declarations vs. index-plus-events. Nobody serious scans at fire time.

**Recommendation (agent):** separate the three concerns, then combine both families:

1. **Authoring stays colocated** — rules keep living as `# RULESET` tails of the spec docs they enforce. Discovery must not dictate location; colocation is a design principle worth protecting.
2. **Declarations are the primary path** — the `include::` DAG (umbrellas → stubs → embedded blocks) plus the trait→ruleset activation map. Resolving declarations touches only the files they name — no filesystem scan on the common path. A ruleset not reachable from any umbrella or trait is *by definition* inert, and that's [[F219 — Activation self-audit rules — base-trait + ruleset-reachability|F219]]'s reachability finding — the "scan missed my new ruleset" failure converts into an audit finding instead of silent non-firing.
3. **The index is compile-time output, maintained by events** — the installer (this feature) materializes the resolved DAG into the rules cache keyed by content hash (audit-plan's cache today; keep). Freshness is event-driven, not fs-watched: Warden's own moment ledger sees every `write:markdown`, so the installer invalidates any written file that contains — or previously contained — the `# RULESET` sentinel. Nearly all edits arrive through agents, so the ledger covers them; a full sentinel rescan (ripgrep `^#+ RULESET`, sub-second on the whole vault) heals out-of-band edits at session start / daily — the same posture as `ha --rescan`.
4. **Rejected:** frontmatter markers (duplicate declaration + YAML parse per file; the `# RULESET` heading already *is* the declaration, and it's line-greppable); a mandatory rules root (fights colocation — though `library/Rulesets/` stays valid as one home for standalone stubs); convention filenames (rulesets deliberately live inside docs whose names serve the doc, not the rule).

**Net:** the user's "manual scan + captured index + watch" instinct is right, with two upgrades — the watcher is the moment ledger (already built, no fs-watcher), and reachability-from-declarations makes the index self-auditing rather than trust-me. Feeds § Design's active-set resolution; ratify alongside M0.

## 2026-07-01 — Discovery resolved: scan command + always-freshen compiler (user direction, benchmarked)

**User direction:** the index is compiler output; discovery is a **scan command** given a configured **root** (the vault root — an engine configuration parameter, resolving the compiler's catch-22 of not knowing where rulesets live). No filesystem watcher. The scan reads every markdown file under the root, finds `# RULESET` blocks, and writes an index of ruleset-bearing files **with mtimes**; the compiler **freshens** against that index, so a ruleset added to an already-indexed file is picked up automatically. Open empiric: could the compiler just scan the vault every time?

**Benchmark (live vault, warm cache, 6,743 md files / 58 MB, 112 ruleset-bearing):**

| Pass | Wall time |
| --- | --- |
| enumerate + stat every md (freshen sweep) | ~220 ms |
| full content read + sentinel regex (single-thread Python) | 0.7–1.3 s |
| `rg '^#+ RULESET R-'` (parallel) | ~116 ms |
| baseline: audit-plan single-doc compile, `--no-cache` | ~250 ms |

**Resolution (COMMITTED, user 2026-07-01) — always-scan, implemented as stat-sweep + selective re-read.** Benchmarks confirmed viability; this is now the contract, not a lean: Every compile: enumerate + stat all md under the root (~220 ms), content-read **only** files that are new or whose mtime/size changed since the index, then re-flatten. This makes the mtime index self-freshening at enumeration time — new ruleset FILES and new rulesets in old files are both caught on every compile, eliminating the stale-index failure class entirely; the standalone scan command remains as the from-scratch builder (first run / `--rescan`, 0.7–1.3 s single-threaded, ~116 ms if shelled to rg). Cost at installer cadence: ~220 ms per compile against a ~250 ms compile baseline — acceptable absolute cost, and the naive always-full-read (1.3 s) would also be tolerable but is unnecessary. *(Supersedes the moment-ledger-invalidation idea from the prior entry — the stat-sweep is simpler, self-contained, and covers out-of-band edits that the ledger cannot see.)*

**Carry-outs for § Design:** (1) `root` becomes an engine config parameter — today's engine hardcodes the ob-skills repo root; generalize to the vault root (all 112 current ruleset files happen to live in ob-skills, but the anchor-embedded future won't). (2) Index schema: `{path, mtime_ns, size, ruleset_names[]}` + the flattened-rules content hash F214's corpus already pins.
