# Testing Catalog

Check that source modules have corresponding tests, test files exist for critical paths, and test coverage is not obviously missing.

## Semgrep Checks

None — test coverage is structural, not pattern-based.

## Agent Checks

### Test file existence

For each source module, check if a corresponding test file exists:

| Language | Source | Expected test |
|----------|--------|--------------|
| Rust | `src/foo.rs` | `tests/foo.rs` or `#[cfg(test)] mod tests` inline |
| Swift | `Foo.swift` | `FooTests.swift` or `FooSpec.swift` |
| Python | `foo.py` | `test_foo.py` or `tests/test_foo.py` |
| TypeScript | `foo.ts` | `foo.test.ts` or `foo.spec.ts` |

Flag modules with public API that have no test file.

### Critical path coverage

For each module the agent reads, check if these are tested:
- Error handling paths — are error cases exercised?
- Edge cases — empty inputs, nil values, boundary conditions
- State transitions — if the module manages state, are transitions tested?

### Test quality signals

Flag these patterns in test files:
- Tests that assert nothing (`assert true`, empty test bodies)
- Tests that only test the happy path (no error cases)
- Tests commented out or marked `#[ignore]` / `@disabled` without explanation
- Test files that import the module but have fewer tests than the module has public methods

### How to Report

| # | Module | Issue | Severity |
|---|--------|-------|----------|
| 1 | src/sync.rs | No test file, no inline tests | High — has 5 public methods |
| 2 | src/config.rs | Tests exist but only happy path | Medium |
| 3 | tests/old_test.rs | 3 tests marked #[ignore] with no explanation | Low |
