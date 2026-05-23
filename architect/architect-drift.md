---
name: architect-drift
description: >
  Architecture-vs-code drift report. Read-only diagnostic that compares the canonical
  `Architecture.md` against the actual code, categorizes findings, and writes a dated
  report to `Versions/`. Architecture is canon; code is reality; the report tells you
  where they diverge. Never modifies the architecture or code — remediation is a
  separate user-driven step (run `/architect update` or `/feature`).
  Use when the user says: "drift", "architect drift", "what's diverged?",
  "is the architecture stale?", "compare arch to code".
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Architect Drift — Architecture-vs-Code Diagnostic

One of the four `/architect` sub-skills (per [[F084 — Architect redesign]]). Pure diagnostic — produces a categorized drift report, never modifies anything.

Adapted from [agent-sh/drift-detect](https://github.com/agent-sh/drift-detect) — the structural pattern (pure-data collectors + single-LLM analysis call) transfers cleanly. The drift categories are different (this skill is arch-vs-code; agent-sh is plan/doc/issue/scope drift). See § Sources.

## Architecture

Two-phase, mirroring agent-sh's separation:

```
/architect drift
  │
  ├─→ collectors (pure parsing — no LLM)
  │   ├─ parseArchitectureDoc()    extract subsystems, modules, actions, data, principles
  │   ├─ scanCode()                 walk source per `.anchor` `code:` config
  │   └─ extractModuleDocs()        read module docs first; fall back to source
  │
  └─→ analyzer (single LLM call with full context)
      └─ Semantic comparison + categorization + report rendering
```

**Data collection**: pure parsing — fast, deterministic, idempotent.
**Semantic analysis**: one LLM call holding the full collected context.

## Drift categories

Adapted from agent-sh's plan/doc/issue/scope-drift taxonomy to the arch-vs-code domain:

| Category | Meaning |
|---|---|
| **Aligned** | Module exists in both arch and code, declarations match. Summarized count at top of report; not listed per-item. |
| **Orphan in code** | Module exists in code but architecture doesn't mention it. May be a recent addition, an implementation detail, or genuine drift. |
| **Ghost in arch** | Architecture mentions a module that doesn't exist in code. May be planned-but-not-implemented, or stale arch. |
| **Diverged** | Module exists in both, but specifications differ. Sub-categorize: **Renamed**, **Role drift**, **Structural move**, or **Action/data drift**. |

## Severity

| Severity | Criteria |
|---|---|
| **High** | User-facing interface affected (CLI, public API, data format) or cross-subsystem boundary affected |
| **Medium** | Internal restructuring; affects multiple modules within one subsystem |
| **Low** | Local renaming or organizational drift within a single module |
| **Info** | Documentation-only divergence; no behavioral implication |

## Workflow

1. **Detect anchor + architecture file.** Walk up from `cwd` to find `.anchor`. Locate `{anchor}/Docs/User/Architecture/Architecture.md` (or the equivalent per the anchor's actual layout). If missing → report `drift: no architecture file — invoke /architect new first` and stop.

2. **Detect code path.** Read `.anchor` `code:` key. Resolve to an existing directory. Missing → report `drift: no code path — anchor not configured as code-trait` and stop.

3. **Parse `Architecture.md`** (pure parsing, no LLM):
   - Subsystems (per the anchor's subsystem-folder decomposition)
   - Modules (per-subsystem lists or sub-page references)
   - Actions / operations (declared API per module)
   - Data structures (declared schemas / models)
   - Principles (the architectural commitments)

4. **Scan code** (pure parsing, no LLM):
   - Module files / packages per language conventions
   - Public exports / declared API per module
   - Data structures (classes / structs / records / schemas)
   - Cross-module references (call graph hints)

5. **Read module docs first.** Per F074 spec — module docs are ground truth for the declared API; source code is the fallback when module docs are missing or stale. Faster + more reliable than re-reading every source file.

6. **Build comparison map** (still pure):
   - For each architecture element → find code counterpart (or note absence)
   - For each code element → find architecture counterpart (or note absence)
   - Use fuzzy matching for names (see § Cross-reference matching)

7. **Categorize**: each non-aligned mapping is Orphan / Ghost / Diverged. For Diverged, identify the sub-category (Renamed / Role drift / Structural move / Action-or-data drift).

8. **Single LLM analysis call.** Pass the parsed architecture + scanned code + comparison map to the LLM (Sonnet by default; can use Opus for harder cases). LLM produces:
   - Executive summary
   - Per-finding analysis with severity + recommendation
   - Cross-cutting patterns (multiple findings sharing a root cause)

9. **Write the drift report** to `{anchor}/Docs/User/Architecture/Versions/{YYYY-MM-DD} Drift Report.md`. See § Report template.

10. **No automatic remediation.** Report is diagnostic. User runs `/architect update` (to update arch) or `/feature` / `/mint` (to update code).

11. **Glance** the drift report (per F084 spec — all `/architect` sub-skills glance their output).

## Cross-reference matching

Names rarely match exactly between architecture prose and code identifiers. Normalize before comparing (adapted from agent-sh's `featureMatch` pattern):

```python
def normalize(name):
    """Lowercase, strip separators, strip trailing 's' for plural tolerance."""
    return re.sub(r'[-_\s]+', '', name.lower()).rstrip('s')

def matches(arch_name, code_name):
    """True if names probably refer to the same thing."""
    a, c = normalize(arch_name), normalize(code_name)
    return a in c or c in a or levenshtein(a, c) < 3
```

Common arch-prose → code-identifier mismatches:

| Arch says | Code uses |
|---|---|
| "user authentication" | `auth/`, `login/`, `session/` |
| "window manager" | `wm`, `WindowManager`, `windowing` |
| "event dispatcher" | `bus::Dispatcher`, `events/`, `eventbus` |
| "logging system" | `logger/`, `logs/`, `telemetry/` |

When fuzzy matching is ambiguous, the LLM analysis call resolves; don't make hard decisions in the pure-parsing phase.

## Report template

```markdown
---
description: Architecture-vs-code drift report — {YYYY-MM-DD}
---

# Drift Report — {YYYY-MM-DD}

## Executive Summary

**Aligned**: {N} modules / {M} subsystems / {K} actions match between architecture and code.
**Drift**: {N_orphan} Orphan-in-code, {N_ghost} Ghost-in-arch, {N_diverged} Diverged.

Headline findings:
- {1-3 most significant issues, written for the user reading the report cold}

## Aligned

({N} modules / {M} subsystems / {K} actions match. Not listed per-item — see code + `Architecture.md` for per-element alignment.)

## Orphan in code

### High
- **{Module}** at `{code/path}` — exists in code but not mentioned in architecture. {Recommendation: add to arch / remove from code / clarify intent.}

### Medium
- ...

### Low / Info
- ...

## Ghost in arch

### High
- **{Module}** mentioned in `Architecture.md` § {subsystem} — does not exist in code. {Recommendation.}

### Medium
- ...

## Diverged

### High
- **{Module}** — Renamed: arch says `{X}`, code has `{Y}`. {Sub-category details + recommendation.}
- **{Module}** — Role drift: arch role *"{declared}"* doesn't match code behavior *"{observed}"*.

### Medium
- ...

## Cross-cutting patterns

- {Pattern 1 — e.g., "5 modules in subsystem X don't have arch counterparts, suggesting subsystem X was added to code after the most recent /architect update."}
- {Pattern 2 — e.g., "All Ghost-in-arch findings are in subsystem Y — possibly an aspirational subsystem awaiting implementation."}

## Sources

- Architecture: `{anchor}/Docs/User/Architecture/Architecture.md` (last modified: {date})
- Code root: `{code path}` (per `.anchor` `code:` key)
- Module docs read: {count} files
- Source files scanned: {count} files
- Analysis model: {model name}
```

## Best practices

Adapted from agent-sh's best-practices to the arch-vs-code domain:

1. **Look for patterns, not individual items.** One missing module isn't drift; five missing modules in the same subsystem is a pattern.
2. **Distinguish recency from staleness.** An Orphan-in-code may be a legitimate recent addition; a Ghost-in-arch may be a planned-but-not-implemented item. Use file mtimes and git log dates to disambiguate.
3. **Weight by interface impact.** User-facing changes (CLI, public APIs, data formats) get High severity. Internal restructuring is Medium. Local renaming is Low.
4. **Consider intent.** Architecture may legitimately spec a module that's "planned but not implemented" — that's Ghost-in-arch but not necessarily a finding (it's a roadmap item). When evidence is ambiguous, the LLM analysis call should err toward Info severity and let the user decide.

## Relationship to other `/architect` sub-skills

- **`/architect new`** (greenfield) — drift on fresh code typically means "code drifted from the original design"; common when implementation outpaced arch updates.
- **`/architect update`** — drift findings are typical inputs to update. After running `/architect drift`, the user often invokes `/architect update` to bring arch in line with code.
- **`/architect changes`** — unrelated. That's intra-architecture-doc diff (between snapshots), not arch-vs-code.

## Sources

- [agent-sh/drift-detect SKILL.md](https://github.com/agent-sh/drift-detect/blob/main/skills/drift-analysis/SKILL.md) — pattern source. What we adapted: two-phase architecture (pure-data collectors + single-LLM analysis), severity framework, fuzzy-matching normalization, report-section structure, best practices.
- What we did NOT adopt from agent-sh: their JavaScript collectors (Node-specific; ours can be Python or shell), their GitHub-issue / PR / milestone integration (not relevant to arch-vs-code), their priority-calculation framework (we use severity directly without scaled scoring), their reconstruction-plan generation (we're diagnostic-only).
- [[F084 — Architect redesign]] — parent spec defining the four-sub-skill split and the category taxonomy.
- [[2026-05-22 Architect Skill Survey]] — the survey identifying agent-sh/drift-detect as the strongest adoption candidate.
