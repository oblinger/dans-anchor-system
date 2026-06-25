# Roadmap — Audit Roadmap Structure (named milestones + future-only)

Check a `{NAME} Roadmap.md` against the named-milestone-era rules introduced by [[F144 — Completed Roadmap + named milestones]] and codified in [[FCT Roadmap]] / [[FCT Completed Roadmap]]. **Reports findings only.** No files are modified (milestone migration + checkbox flips live in `state roadmap`, not here).

## Rules enforced

| Rule | Constraint | Severity |
|------|-----------|----------|
| **R-roadmap-09** | Top-level milestones use named form `M-<Name>` (not pure-numbered `M1`/`M2`). Pure-numbered roadmaps are accepted only when the file carries a `<!-- legacy-numbered-milestones -->` marker comment. | error |
| **R-roadmap-10** | Every roadmap sub-item carrying a `[F<NNN>]` marker resolves to a feature doc on disk; every feature doc whose filename starts with `F<NNN> — M-` matches the full title format `F<NNN> — M-<Name>.<position>: <Title>`. | warning |
| **R-roadmap-11** | Future-only invariant — a roadmap should not accumulate `[x]`-complete top-level milestones (they migrate to the Completed Roadmap). More than 2 lingering complete milestones is flagged as migration drift. | warning |

## Workflow

### 1. Run the checker

```bash
python3 ~/.claude/skills/audit/scripts/audit-roadmap.py --anchor SKA   # one anchor
python3 ~/.claude/skills/audit/scripts/audit-roadmap.py --file PATH     # one file
python3 ~/.claude/skills/audit/scripts/audit-roadmap.py                 # vault-wide
```

The script reuses the audit-q primitives (`build_vault_index`, `links_in_file`, `headings_in`) via importlib, matching the house style of the other audit sub-scripts.

### 2. Report

Print the findings table to the console. Each finding carries `[severity] CODE file:line — message`.

- If `dry` is in the args (or no findings) → stop here; print `roadmap: N findings (no entry written)`.
- Otherwise, surface the residuals the way the other report-only audits do: write a terse backlog row on the owning anchor naming the milestone(s) that need migration (R11) or the malformed identifiers (R09). Fixing is downstream work pulled from the backlog — audit never fixes.

### 3. Hand off the fixes

- **R09 (malformed milestone name)** → rename the milestone to `M-<Name>` form (manual; touches cross-references — grep the old id first).
- **R10 (broken `[F<n>]` marker)** → either author the missing feature doc or correct the marker.
- **R11 (migration drift)** → run `state roadmap migrate M-<Name> --date YYYY-MM-DD` for each lingering complete milestone.

## See also

- [[FCT Roadmap]] — the facet spec + embedded `R-roadmap` RULESET (R09/R10/R11)
- [[FCT Completed Roadmap]] — the migration target + `R-completed-roadmap` RULESET
- [[F145 — Roadmap automation scripts]] — the feature that landed this checker + `state roadmap`
