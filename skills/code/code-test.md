# Test — Test Advisor & Developer

Build the right tests for the project. Autonomous test developer — identifies gaps, designs scaffolds, writes tests, verifies them.

## Reference Files (load when needed)

| File | When to load |
|------|-------------|
| [[code-test-scaffolds]] | When planning or building scaffolds (step 3) |
| [[code-test-quality]] | When reviewing tests or self-checking while writing (step 5, `/code test review`) |
| [[code-test-external]] | When testing code that interfaces with OS, network, or external services |

Full design rationale: `~/ob/kmr/SYS/Bespoke/Skill Agent/DEV/DEV Docs/DEV Plan/DEV Test PRD.md`


## What This Is

- An autonomous test developer that writes code
- Agent-first: use judgment, don't ask about priority or ordering
- Only pause for decisions that change production code or genuine architectural questions

## What This Is NOT

- Not a TDD enforcer — works on existing code with zero tests
- Not a coverage tool — no line coverage percentages
- Not a gate — doesn't block anything


## Invocation

```
/code test                    # Default: level 5 test development
/code test 3                  # Build tests through level 3
/code test 8                  # Deep adversarial testing
/code test recommend          # Just show what's missing, don't write code
/code test review             # Review quality of existing tests
/code test verify             # Run tests and produce completion proof
```


## Workflow

### Step 0: Test Design Document (always first)

Create or open `{NAME} Docs/{NAME} Dev/{NAME} Test Design.md`:

```markdown
# {NAME} Test Design

## Open Questions

## Test Design

| SCAFFOLDS            | Description                                    |
| -------------------- | ---------------------------------------------- |
| [[#KitchenSink]]     | Full system with realistic data                |

| TEST AREAS                    | Category | Level | Description                    |
| ----------------------------- | -------- | ----- | ------------------------------ |
```

**Open Questions at the top** — user sees them immediately. Add questions as they arise during any step. Don't batch them.

### Steps 1-7

1. **Assess** — Read source code, existing tests, git history. Understand the architecture.
2. **Identify gaps** — Biggest gaps first, using priorities below. Add findings to Test Design doc.
3. **Plan scaffolds** — Kitchen sink first. Focused scaffolds only for isolation. Document in Test Design.
4. **Implement** — Write tests matching the design doc. Self-check against anti-patterns. Tag each test with category.
5. **Verify** — Run tests. Produce completion proof.
6. **Report** — Show test report, gaps remaining, next steps.

### Operating Principles

- **Do not ask about priority or ordering.** Use judgment.
- **Only pause for** decisions that change production code or genuine architectural questions.
- **Work around open questions** — if a question blocks one test area, keep building other areas. Make maximum progress before the user needs to intervene.
- **Add open questions as you go** — don't batch. User answers asynchronously while you keep working.
- **Parallelize** — build multiple scaffolds and test areas concurrently when independent.
- **Do as much upfront as possible** — even with open questions pending, build everything that isn't blocked.


## Priorities (what to build, in order)

1. **Critical path integration** — The core loop end-to-end
2. **Regression tests** — Commits with "fix" — write a test for each bug
3. **Boundary/contract** — Malformed input, missing files, permissions. Test the sad paths.
4. **Public API smoke** — Every public function called at least once
5. **Change-based** — Source changed since tests last updated


## Test Levels (how deep)

| Level | What |
|-------|------|
| 1 | Build kitchen sink scaffold |
| 2 | Happy path: core loop, startup, data round-trip |
| 3 | Boundaries: malformed input, missing files |
| 4 | Public API smoke tests |
| 5 | **Default**: regression tests, stale test detection |
| 6 | Adversarial: race conditions, concurrency |
| 7 | Data edge cases: off-by-one, overflow, Unicode, max-size |
| 8 | Failure cascades: A fails, does B handle it? |
| 9 | Chaos: corrupt state, kill processes, disk full |

Kitchen sink grows at every level. Levels 1-5 standard. 6-9 adversarial.


## Test Categories (when tests run)

| Category | When | Constraint |
|----------|------|------------|
| **snap** | Every commit | Under 2 seconds. No I/O. |
| **pr** | Every PR / milestone | Under 60 seconds. No visible side effects. |
| **demand** | On demand | Slow, exhaustive. Worth running sometimes. |
| **witness** | User present | Affects visible environment. User hands off. |

Each includes previous: `pr` runs snap too. `witness` runs everything.

**Probe tag**: test may fail for environmental reasons. Retry once before reporting.

```bash
just test              # snap
just test pr           # snap + pr
just test demand       # snap + pr + demand
just test witness      # everything
```

Levels and categories are **orthogonal**. Level = how deep. Category = when to run.


## Scaffolds

**Kitchen Sink first.** One big realistic scaffold, all tests run against it. Extend as the app grows — every new edge case goes in, creating cross-product coverage.

**Focused scaffolds** only for: clean/empty state, debugging isolation, performance testing.

**Tricky Cases** go into the kitchen sink, not separate scaffolds.

See PRD for detailed scaffold descriptions and examples.


## File Organization

**Rust:** Inline `#[cfg(test)]` for snap. `tests/` for pr/demand/witness. Scaffold in `tests/scaffold/`.

**Python:** `tests/` folder, **pytest**. Files: `test_{module}.py`. Scaffold: fixture in `conftest.py`. Markers: `@pytest.mark.snap`, `@pytest.mark.pr`, `@pytest.mark.demand`, `@pytest.mark.witness`.

**Swift:** `{Project}Tests/`, files: `{Module}Tests.swift`.


## Anti-Pattern Self-Check

While writing tests, verify:
1. Testing real behavior, not mock behavior?
2. Assertions check specific values, not just truthiness?
3. No test-only methods added to production code?
4. Mocks realistic, not hiding assumptions?


## External Dependencies

OS APIs, network, hardware — where the painful bugs live. **Isolate and pound.** Test the interface in isolation, many variations. Tag flaky ones `probe`.


## Refactoring for Testability

When complex logic is buried deep and hard to test through scaffolds, consider extracting to a pure function for unit testing.

**⚠️ NEVER refactor production code without user approval.** Propose: what to extract, what tests it enables. Wait for approval.


## Escalation Rule

3 failed attempts → stop. "Is this code testable? Should we refactor?" Suggest specific changes. Don't keep trying workarounds.


## Completion Proof

MUST produce this report by RUNNING the test suite — not by belief:

```
## Test Report
Tests written this session: 12
Tests passing: 11
Tests failing: 1 (TestConfigMalformed — line 45)
Kitchen sink scaffold: extended (added 3 edge cases)
Gaps remaining: 4 (listed below)
```

No "done" without this report.


## Red-Green Verification

- **Levels 1-5**: Run tests, confirm green, show report.
- **Levels 6+**: Additionally mutate production code to confirm tests catch breakage. Undo after.
