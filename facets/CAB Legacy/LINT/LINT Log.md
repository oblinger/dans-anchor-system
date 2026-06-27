​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[CAB]] → [[LINT]] → [[LINT Docs]] → [[LINT Track]] → [LINT Discussion](hook://p/LINT%20Design%20Discussions)

# LINT Discussion


## 2026-03-14  Testing Checking

### Context

Solo developer, large applications (up to 60K lines), heavily AI-assisted, some commercially released. No team to catch regressions. AI generates code fast but can introduce subtle bugs.

### What Matters Most
1. **Integration tests over unit tests** — With AI writing code, individual functions usually work. It's the *interactions* between components that break. A test exercising the full pipeline (config loads → command dispatches → action executes → UI updates) catches more real bugs than 50 unit tests on individual methods.
2. **Regression tests on fixed bugs** — Every bug fix should have a test that reproduces the original bug. Highest-ROI testing — prevents the same bug from returning during AI refactoring (AI doesn't remember the bug).
3. **Boundary/contract tests** — Test interfaces between modules: malformed config, network down, file missing. AI tends to write happy-path code. Edges are where it fails.
4. **Smoke tests for deployment** — Can the app start? Can it handle the most common user action? Catches catastrophic regressions before release.
5. **Don't chase coverage percentages** — 80% line coverage with meaningless tests is worse than 30% coverage of critical paths. Focus on "does this critical module have ANY tests?" not "what percentage of lines are covered?"

### What the Lint Tool Should Check

| Check | Why |
|-------|-----|
| Does each module have a corresponding test file? | Basic coverage existence |
| Do public API functions have at least one test? | Critical path coverage |
| Are there regression test files? | Bug-fix discipline |
| When was the test last updated vs the source? | Stale test detection |

### What NOT to Build

- Line-level coverage analysis (requires running tests, expensive, noisy)
- Auto-generated tests (AI can do this on demand when asked)
- Coverage thresholds that block commits

### Approach: Test Advisor, Not Coverage Enforcer

The tool should be a **test advisor** — "this module changed 500 lines since its tests were last updated" or "this public API has no tests at all" — rather than a coverage enforcer.

### Superpowers / Iron Laws Approach

From the antigravity-superpowers skill set — three discipline principles worth incorporating:

1. **"NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST"** — strict TDD. Write test, watch it fail, then write minimal code. If code is written first, delete it.
2. **"NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST"** — don't guess-and-fix. Reproduce, trace, gather evidence. If 3rd fix attempt fails, question the architecture.
3. **"NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE"** — before saying "done", actually run tests and read full output. No "it should work."

These are **development-time disciplines** (enforced during coding), complementary to our **after-the-fact lint checking** (enforced during review). Both are needed:
- Lint catches what slipped through during development
- Iron Laws prevent the slippage in the first place

### Testing Anti-Patterns to Check For
From the Superpowers testing-anti-patterns skill:
1. Testing mock behavior instead of real behavior
2. Test-only methods in production classes
3. Mocking without understanding dependencies
4. Incomplete mocks that hide structural assumptions
5. Integration tests as afterthought

### Two Tools, Two Purposes

| Tool | When | What |
|------|------|------|
| **Dev skill (TDD discipline)** | During coding | Iron Laws — force test-first, root cause investigation, verification |
| **Lint tool (test advisor)** | After coding | Report untested modules, stale tests, missing regression tests |

The dev skill could be a new action `/dev test` or integrated into `/dev execute`. The lint tool adds test-checking rules to `cab-lint.py`.

### Open Questions

- **Q1**: How to match source files to test files? Naming convention (`foo.rs` → `test_foo.rs`)? Import analysis? Both?
- **Q2**: How to detect regression tests vs regular tests? Naming convention? Comments?
- **Q3**: Should the lint tool suggest WHAT to test, or just report what's untested?
- **Q4**: Integration test detection — how to distinguish integration tests from unit tests statically?
- **Q5**: Should we create a `/dev test` skill with Iron Law discipline, or fold it into `/dev execute`?
- **Q6**: Mutation testing (cargo-mutants, mutmut) — worth integrating as a lint rule at higher levels?


## 2026-03-14  Design decisions and trade-offs for the CAB Lint tool.

---

| Level  | Meaning    | Description                                      |
| ------ | ---------- | ------------------------------------------------ |
| Lint 1 | Bare Bones | Only the most basic stuff that defines an anchor |
| Lint 2 | Core       | Fast and Core elements for each anchor type      |
| Lint 3 |            |                                                  |
| Lint 4 |            |                                                  |
| Lint 5 | Default    | Default level for linting                        |
| Lint 6 |            |                                                  |
| Lint 7 |            |                                                  |
| Lint 8 |            |                                                  |
| Lint 9 |            |                                                  |

## 2026-03-14  CAB Lint Skill

A `/cab lint` skill that analyzes an anchor's structure and contents against its CAB type rules — structural conformance, documentation coverage, and test coverage. See [[2026-03-14 CAB Lint Tools Survey]] for the tools survey.

### Open Questions

- **Q1: Anchor type detection** — How does the validator know which anchor type it's checking? Options: read a `type:` frontmatter field in the anchor page, infer from structure (has Code symlink → Code Anchor, has SKILL.md → Skill Anchor), or require the user to specify.
- **Q2: Language choice** — What language for the validator? Python is readable and easy to work in. Performance matters for source parsing (up to 100K lines), but caching mitigates this. Rust would be faster but harder to iterate on.
- **Q3: Source code parsing** — Need to parse source code to extract module structure (functions, classes, exports). Options: tree-sitter (multi-language, fast, incremental), Python `ast` module (Python only), language-specific LSPs, or regex-based heuristics.
- **Q4: Caching strategy** — Parse results should be cached to avoid recomputing on every run. Cache key = file content hash? Invalidate per-file on change?
- **Q5: Existing tools** — Are there existing skills, MCP servers, or open-source tools that already do code structure analysis, doc coverage, or test coverage checking? Where to survey: GitHub (Claude Code community skills, MCP server repos), tree-sitter ecosystem, language-specific tools (interrogate for Python doc coverage, cargo-tarpaulin for Rust, jest --coverage for JS).
- **Q6: Output format** — Should validation produce a YAML summary of the codebase structure? A markdown report? Both?

### Architecture Discussion

Two-layer architecture:

**Layer 1 — Anchor structure validation** (build first, high value, simple):
- Does the anchor have the required files for its type?
- Does the anchor page have a dispatch table, breadcrumb, `desc::`?
- Do subfolder dispatch pages exist and have dispatch tables?
- Are all markdown files reachable from the dispatch tree?
- Is the Code symlink valid? Is CLAUDE.md in the right place?

Pure file/content checking. Python, no heavy dependencies. Inspired by PSX's YAML-rules approach — define expected structure per anchor type, validate against it.

**Layer 2 — Code quality validation** (build later, per-language):
- tree-sitter-analyzer for structure extraction → JSON/YAML
- interrogate for Python doc coverage
- coverage.py for test coverage
- Cached per-file by content hash

Key insight from the survey: no one has built anything quite like Layer 1. Structure validators exist for generic projects (PSX, directory-schema-validator) but nothing for a system like CAB with typed anchors, dispatch tables, and wiki-link navigation trees. This is genuinely novel.

### Decisions Made

- **D1: Language** — Python. Readable, easy to iterate, `uv run` for deps. Performance-critical parts (tree-sitter) are C-backed anyway.
- **D2: Anchor type detection** — Infer from structure. `Code` symlink or `.git/` → Code Anchor, `SKILL.md` → Skill Anchor, version table → Paper Anchor, child anchors → Topic Anchor, none → Simple Anchor.
- **D3: Two layers** — Layer 1 (structure) first, Layer 2 (code quality) later.
- **D4: Output** — Quality gate: PASS / CONCERNS / REWORK / FAIL. Per-rule results with severity.


## 2026-03-14  Program Design

### Architecture

```
cab-lint.py                          single Python script, invoked by /cab lint
├── detect_type(path) -> AnchorType  infer anchor type from structure
├── load_rules(type, level) -> list  rules for this type at this lint level
├── run_rules(path, rules) -> list   execute each rule, collect results
├── report(results) -> str           format as markdown report
└── gate(results) -> str             PASS / CONCERNS / REWORK / FAIL
```

### Invocation

```bash
uv run cab-lint.py <anchor-path> [--level 5] [--type code] [--json]
```

- `anchor-path` — path to the anchor folder (default: current directory)
- `--level` — lint level 1-9 (default: 5)
- `--type` — override auto-detected type
- `--json` — output as JSON instead of markdown

The `/cab lint` skill reads and runs this script via `uv run`.

### Rule Structure

Each rule is a Python function with metadata:

```python
@rule(level=1, types=[AnchorType.ALL], id="marker-file")
def check_marker_file(anchor: Anchor) -> RuleResult:
    """Marker file exists with same name as folder."""
    marker = anchor.path / f"{anchor.folder_name}.md"
    if marker.exists():
        return RuleResult.PASS
    return RuleResult.FAIL(f"Missing marker file: {marker.name}")
```

- **`level`** — minimum lint level to trigger this rule (1=bare bones, 5=default, 9=pedantic)
- **`types`** — which anchor types this rule applies to
- **`id`** — stable identifier for the rule (used in JSON output, suppression)

### Lint Levels (detail)

| Level | Meaning    | What it checks |
|-------|------------|----------------|
| 1     | Bare Bones | Marker file exists, anchor page exists |
| 2     | Core       | Type-specific required files (CLAUDE.md for Code, SKILL.md for Skill) |
| 3     | Structure  | Docs folder structure, Code symlink validity |
| 4     | Content    | `desc::` present, breadcrumb present |
| 5     | Default    | Dispatch tables exist and have entries, Dev/Plan/User dispatch pages |
| 6     | Links      | All markdown files reachable from dispatch tree |
| 7     | Cross-ref  | Wiki-links resolve, no broken internal links |
| 8     | Naming     | `{NAME}` prefix on all files/folders, casing conventions |
| 9     | Pedantic   | Spacing rules, TOC format, dispatch table column alignment |

### Example Rules by Level

**Level 1 — Bare Bones:**
- `marker-file` — folder has `{FolderName}.md`
- `anchor-page` — has an anchor page (marker or separate `{NAME}.md`)

**Level 2 — Core:**
- `code-has-claude` — Code Anchor has CLAUDE.md at anchor root
- `code-has-readme` — Code Anchor repo has README.md
- `skill-has-skillmd` — Skill Anchor has SKILL.md
- `code-symlink-valid` — Code symlink resolves to existing directory

**Level 3 — Structure:**
- `docs-folder` — has `{NAME} Docs/` with dispatch page
- `plan-folder` — has `{NAME} Plan/` under Docs
- `dev-folder` — Code Anchor has `{NAME} Dev/` under Docs

**Level 5 — Default:**
- `dispatch-table` — anchor page has a dispatch table (detects `-[[NAME]]-` pattern)
- `dispatch-entries` — dispatch table has at least one entry
- `plan-dispatch` — Plan folder has dispatch page with dispatch table
- `dev-dispatch` — Dev folder has dispatch page with dispatch table

**Level 7 — Cross-ref:**
- `wiki-links-resolve` — all `[[Target]]` links in anchor markdown files resolve to existing files
- `module-docs-linked` — every module doc in Dev is referenced from Dev dispatch page

### Output Format

**Markdown (default)** — the tool emits a `## CAB Lint: <Anchor>` heading, a Type/Level preamble, then a `### PASS` / `### CONCERNS` / `### FAIL` section per status, closing with a `**Result:**` line. The rendered shape:

- **`## CAB Lint: Hook Anchor`** — then `Type: Code Anchor (detected)` and `Level: 5`.
- **`### PASS (12 rules)`** — `✓ marker-file — Marker file exists`, `✓ anchor-page — Anchor page found: HA.md`, …
- **`### CONCERNS (2 rules)`** — `⚠ dispatch-entries — Plan dispatch table has no entries`, `⚠ dev-dispatch — Dev dispatch page missing dispatch table`
- **`### FAIL (1 rule)`** — `✗ code-has-readme — README.md not found in repo`
- **`**Result: CONCERNS**`** — the overall gate.

**JSON (`--json`):**
```json
{
  "anchor": "Hook Anchor",
  "type": "code",
  "level": 5,
  "gate": "CONCERNS",
  "results": [
    {"id": "marker-file", "level": 1, "status": "pass", "message": "Marker file exists"},
    {"id": "dispatch-entries", "level": 5, "status": "concern", "message": "Plan dispatch table has no entries"}
  ]
}
```

### File Location

The script lives in the LINT project's code area. Since LINT is under Skill Agent (vault), and this is a Python script that should be directly runnable:

```
Skill Agent/LINT/cab-lint.py              the script
Skill Agent/LINT/pyproject.toml           dependencies (if any beyond stdlib)
```

The `/cab lint` skill file (`~/.claude/skills/cab/cab-lint.md`) documents the invocation and delegates to `uv run cab-lint.py`.


## 2026-03-14  Tempo and Scheduling

### Problem

Some lint checks are cheap (marker file exists) and should run every time. Others are expensive (parse 100K lines of source, resolve all wiki-links) and should only run periodically. The system needs a way to control *when* checks run, not just *whether* they run.

### Tempo Concept

Each lint operation can have a **tempo** — a condition that must be met before the operation runs again. If no tempo is specified, the operation runs every time. Tempo types:

| Tempo | Meaning | Example |
|-------|---------|---------|
| (none) | Every time | `lint marker-file` |
| `--after 7d` | After 7 days since last run | `lint wiki-links --after 7d` |
| `--after 5c` | After 5 commits since last run | `lint module-docs --after 5c` |
| `--after 3k` | After 3KB of changes since last run | `lint naming --after 3k` |

The system tracks last-run timestamps/commit-counts per operation and skips if the tempo condition isn't met.

### Lint Spec File

The lint operations for an anchor are defined in a **markdown file** — human-editable, version-controlled. This is NOT the lint script itself — it's the configuration for what to lint and when.

The spec file lives in the anchor and lists operations grouped by level. Its shape: a `# Lint Spec` H1, then one `## Level N` H2 per level, each containing a fenced block of `lint <op> [--after <tempo>]` lines. The standard levels and their operations:

- **`## Level 1`** — `lint marker-file`, `lint anchor-page`
- **`## Level 3`** — `lint docs-folder`, `lint plan-folder`, `lint code-symlink --after 7d`
- **`## Level 5`** — `lint dispatch-table`, `lint dispatch-entries`, `lint plan-dispatch`, `lint dev-dispatch --after 7d`
- **`## Level 7`** — `lint wiki-links --after 7d`, `lint module-docs-linked --after 5c`
- **`## Level 9`** — `lint naming-prefix --after 3k`, `lint spacing-rules --after 14d`

When you run `cab-lint <path> --level 5`, it executes all operations at level 5 and below, respecting each operation's tempo.

### Two Files, Two Purposes

1. **Lint spec** (per-anchor, markdown) — WHAT to lint and WHEN (human-editable configuration)
2. **Lint script** (`cab-lint.py`) — HOW to lint (the rule implementations, shared across all anchors)

The spec file is the thing the user edits to tune linting for their project. The script is the engine that reads the spec and runs the rules.

### State Tracking

The system needs to remember when each operation last ran. Options:
- **JSON sidecar** — `.cab-lint-state.json` in the anchor folder, storing `{rule_id: {last_run: timestamp, last_commit: hash}}`
- **Hidden folder** — `.cab-lint/` with per-rule state files
- **Inline in spec** — append last-run info to the spec file itself (messy, probably not)

Leaning toward JSON sidecar — simple, single file, easy to read/write, can be gitignored.


## 2026-03-14  Module Doc Comparison System

### Overview

Three-phase pipeline that ensures module docs match source code. Each phase is independent and can run separately.

### Phase 1: Scanner (source → cache)

```
scan(repo_root) → .skl/lint/source-cache/*.json
```

- Walks the source tree recursively
- For each source file (.rs, .py, .swift):
  - Compare source file mtime vs cached JSON mtime
  - If source is newer (or no cache): parse with tree-sitter, write JSON cache
  - If cache is current: skip
- Cache location: `.skl/lint/source-cache/{relative-path}.json`
  - e.g., `src/ui/popup.rs` → `.skl/lint/source-cache/src/ui/popup.rs.json`
- Cache format: raw tree-sitter output (classes, methods, fields, imports, line ranges)
- **No transformation** — cache is faithful to what the parser found

### Phase 2: Loader (cache + markdown → ModuleInfo)

```
load_source(cache_dir) → List[ModuleInfo]
load_docs(dev_dir)     → List[ModuleInfo]
```

Both sides produce the same `ModuleInfo` structure:

```python
@dataclass
class MethodInfo:
    name: str
    visibility: str        # pub, private, etc.
    signature: str         # full signature if available
    has_detail: bool       # has METHOD DETAILS section (docs only)

@dataclass
class ClassInfo:
    name: str              # PascalCase from source
    visibility: str
    fields: list[str]
    methods: list[MethodInfo]

@dataclass
class ModuleInfo:
    file_path: str         # relative path in repo
    doc_path: str          # relative path in Dev docs (if exists)
    classes: list[ClassInfo]
    free_functions: list[MethodInfo]
    mtime: float           # modification time of source file
```

**Source loader:** Reads cached JSON files. Per-language logic associates methods with their parent class (Rust: match `impl` blocks by line range; Python: methods inside `class` by indentation; Swift: methods inside `class`/`struct` by nesting).

**Markdown loader:** Reads module doc `.md` files. Parses:
- CLASSES table → class names
- Per-class tables → field names, method names
- CLASS DETAILS H2 sections → which classes have detail
- METHOD DETAILS H3 sections → which methods have detail

### Phase 3: Comparator (source ModuleInfo vs doc ModuleInfo)

```
compare(source: List[ModuleInfo], docs: List[ModuleInfo]) → List[LintResult]
```

Always compares — no mtime shortcuts, because edits don't guarantee correctness.

Comparison produces:
- **Source file with no module doc** — CONCERN or FAIL depending on lint level
- **Module doc with no source file** — CONCERN (stale doc?)
- **Class in source but missing from doc** — FAIL
- **Class in doc but not in source** — CONCERN (removed?)
- **Method in source but missing from doc table** — CONCERN
- **Method in doc but not in source** — CONCERN (removed?)
- **Field count mismatch** — CONCERN
- **Module doc not linked from Dev dispatch** — FAIL

### File Layout

```
.skl/
└── lint/
    └── source-cache/
        ├── src/ui/popup.rs.json
        ├── src/core/commands.rs.json
        └── ...
```

### Decision: tree-sitter-analyzer for Rust/Python, defer Swift

Testing showed:
- **Rust**: tree-sitter-analyzer works well — finds structs, methods, fields, imports
- **Python**: bundled grammar, should work
- **Swift**: NOT supported by tree-sitter-analyzer. Defer until needed, then use py-tree-sitter + tree-sitter-swift directly

Key gap: tree-sitter-analyzer lists methods flat (not associated with parent struct/class). The source loader must post-process to associate methods with their `impl`/`class` block using line ranges.


## 2026-03-14  Exceptions System

### Workflow

Lint reports warnings → agent reviews → agent either fixes the doc or declares an exception. Lint never auto-corrects. The agent has judgment about what's worth documenting.

### Exceptions File

Located at `.skl/lint/exceptions.md` in the anchor. The file opens with a `# Lint Exceptions` H1, then a markdown table sorted by module path then target, with four columns (Module / Target / Rule / Reason) — for example:

| Module | Target | Rule | Reason |
|--------|--------|------|--------|
| build.rs | | file-no-module-doc | Build script, not API |
| src/core/sys_data.rs | SysData.get_sys_data | method-undocumented | Trivial accessor |
| src/core/sys_data.rs | SysData.set_state | method-undocumented | Trivial accessor |
| src/ui/popup.rs | ExternalDialogState | class-undocumented | Private internal state |
| src/ui/popup.rs | WindowSizeMode | class-undocumented | Private enum, internal only |
| *.toml | | file-no-module-doc | Config files |
| *.js | | file-no-module-doc | JavaScript config, not Rust API |

- **Module** — relative source path, sorted alphabetically. Glob patterns (`*.toml`) for whole categories.
- **Target** — specific class, method, or field. Empty = applies to the whole module.
- **Rule** — the lint rule ID being suppressed.
- **Reason** — agent must justify the exception (forces deliberation).

### Behavior

- Lint tool reads `exceptions.md` before reporting
- Matching warnings are suppressed from output
- Suppressed count shown in summary: `(12 suppressed by exceptions)`
- `--show-exceptions` flag to see what's being suppressed
- Agent adds rows when it decides something isn't worth documenting
- Human can delete rows to re-enable warnings


## 2026-03-14  Test Coverage Goals

### Context

Solo developer building large applications (up to 60K lines), heavily AI-assisted, some commercially released. Testing is critical because:
- No team to catch regressions
- AI generates code fast but can introduce subtle bugs
- Commercial release means reliability matters
- Refactoring happens frequently — tests are the safety net

### Discussion


## Backlog

- **UX element field suppression** — Views, controllers, and other UI elements almost never have fields worth documenting (they're all private wiring like `cancellables`, `scrollView`, `escapeMonitor`). Domain logic objects (buffers, routers, state managers) DO have important fields. Consider a way to designate UI-layer classes so lint auto-suppresses their fields. No clean solution yet — could be a naming convention, a tag in the module doc, or a folder-based heuristic (`*/Window/*`, `*/UI/*`, `*View.swift`).
