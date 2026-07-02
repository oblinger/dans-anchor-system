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

**Designed 2026-06-26** (this doc + [[Warden Architecture]] §7a). Not yet implemented — M1 of [[Warden Roadmap]].

## Resolved

1. **When does the compiler run** — once at session start (install all), or incrementally per anchor entered? (Active-set resolution cost trade-off; also [[Warden PRD]] Q1.)
2. **Module format** — emitted Python source vs. a data table the runtime interprets vs. (for Rust) generated/compiled code.
3. **Rule-authored Python in the hot path** — can a compiled module run a rule's Python `if::` / body cheaply, or are code-carrying rules confined to post-hoc moments? (Also [[Warden PRD]] Q2.)

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
