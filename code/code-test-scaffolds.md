# Test Scaffolds — Reference

Loaded by `/code test` when planning or building scaffolds.


## Kitchen Sink Scaffold

One large scaffold with maximal complexity — every edge case, every combination, every subsystem populated. Built once, tested against by many test functions.

### Why Kitchen Sink First

- Build the scaffold once, get broad coverage from every test
- Every new test reuses it — no duplicating setup code
- Catches interaction bugs that focused scaffolds miss
- **Cross-product effect** — complexity added for one test potentially exposes bugs in every other test area

### What Goes In

- Large, realistic dataset (not toy data)
- Deep hierarchy (nested structures, multiple levels)
- Multiple config overrides and flag combinations
- History with duplicates, gaps, edge cases
- Mixed types (every action type, every command variation)
- Comments in the scaffold code explaining what each edge case tests

### Growth Pattern

The kitchen sink grows at every test level:
- Level 1: realistic data representing a real user's setup
- Level 2: common user flows added as state
- Level 3: malformed and missing data alongside the good data
- Level 5: exact data that triggered recent bugs
- Level 6: scenarios for concurrent access
- Level 7: extreme-size and edge-case data (10,000 entries, 10MB strings)
- Level 9: corrupted state (half-written files, broken references)

**Always extend, never replace.** New edge cases go INTO the kitchen sink. Every existing test benefits from the added complexity.


## Focused Scaffold

Tests one specific area with realistic state. Use ONLY when:
- You need **empty/clean state** the kitchen sink can't provide (fresh install, first-run)
- You're **debugging a test failure** and kitchen sink is too complex to isolate the cause
- A subsystem needs **performance testing** with controlled, minimal state

Examples:
- "Config scaffold" — loads a real config, parses, builds command tree, verifies dispatch
- "History scaffold" — known history entries, tests queries/merges/deletions
- "Clean install scaffold" — empty database, no config, tests first-run experience


## Tricky Cases

Don't build a separate scaffold. Add tricky cases TO the kitchen sink:
- Commands with special characters in names
- Patches with overlapping paths
- Config files with duplicate entries
- Concurrent scanner updates
- Empty strings, nil values, maximum-length inputs

The value is in **identifying the tricky cases** as much as testing them — the scaffold serves as documentation of what's hard about this system.


## Scaffold Recommendations

When assessing a project, think about scaffolds:
- "This project has 200 unit tests but no integration scaffold → build kitchen sink"
- "Kitchen sink hasn't been updated since new feature X → extend it"
- "Recent bug fix in Y → add tricky case to kitchen sink"
- "Need to test clean install → build focused scaffold"
