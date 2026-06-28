---
traits: [Code]
description: Lint an anchor — static analysis against CAB type rules.
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[CAB]] → [LINT](hook://p/LINT)

**[[LINT Docs\|Docs]]:** ~~, [[LINT Plan\|Plan]]

# LINT — CAB Lint

Specification page for the LINT tool — static analysis that audits an anchor against the CAB type rules (structure, naming, dispatch tables, module-doc coverage).

# BRIEF

- **This page is the spec home for the LINT tool**, not a general lint-discussion page; everything here describes what `lint` does, how it's invoked, and what it checks against CAB.
- **NOT a rule catalog** — individual lint checks belong in [[FCT Ruleset]] / the relevant `R-` rule files; this page references them, it does not redefine them.
- **NOT the skill runbook** — agent-facing how-to-run-the-skill lives under `~/.claude/skills/lint/SKILL.md`; this page is the CAB-side specification the skill conforms to.
- **Inclusion test** — content belongs here only if it describes LINT-the-tool's contract (CLI surface, exit codes, scope of analysis, integration with `/audit`, output shape). Per-anchor findings, per-rule semantics, and per-skill workflow live elsewhere.
- **Linking conventions** — the dispatch table is the canonical entry; subordinate docs go under `LINT Docs/` and the planning thread under `LINT Plan/`. Wiki-link as `[[LINT]]` (the RID) for the anchor, `[[LINT Tool]]` only when referring to this spec specifically.
- **Load-bearing constraints** — the H1 must keep its `LINT — CAB Lint` form (the dispatch table breadcrumb and the [[Atlas]] entry both reference this exact title); don't rename without sweeping the vault.
- **Pair with siblings** — keep this spec aligned with the other CAB tool specs (`stat`, `cab-config`, `cab-scan`) so the tool family stays coherent; cross-link rather than restate shared mechanics.
