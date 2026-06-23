---
description: "load-bearing decisions citing rules"
---

# CAE Decisions
include:: [[R-diagram]], [[R-c4]], [[R-wcag-contrast]]

> **Migrated per F113 Phase 1b.** Lean canonical list — rationale lives in [[CAE Decisions Details]]. Initial H2 grouping is pass-through (by source file); refine into topic groups post-migration.

## Adoption implementation map

| Rule | CAE implementation |
| ---- | ------------------ |
| `R-c4-01` (every arrow labeled) | `CAE Architecture/CAE Architecture.svg`; verified by `/audit decisions` against the SVG; cited by D11 |
| `R-c4-02` (title or legend present) | `CAE Architecture.svg` `<title>` element "CAE Architecture"; cited by D11 |
| `R-wcag-contrast-01` (text contrast ≥4.5:1) | `CAE Architecture.svg` palette; cited by D11 |
| `R-wcag-contrast-02` (color not sole communicator) | every box in `CAE Architecture.svg` carries a text role label; cited by D11 |

## Principles (migrated from CAE Principles.md)

### D01 — One Queue, One Clock (checked)
All scheduling decisions flow through a single priority queue and a single injected `Clock`. No module constructs its own queue, BTreeMap-over-deadline, or ad-hoc ordering of pending work. No module reads wall-clock time directly.

**Why.** A single queue + single clock is the foundation of deterministic scheduling and testability; scattered ordering or direct wall-clock reads make the system's timing impossible to reason about or test.

### D02 — Fail Loudly (checked)
Errors propagate. Defaults are declared at the callsite or not at all. Retries are explicit and logged. Task failures reach the caller as errors, not swallowed with a substituted default.

**Why.** Silent fallbacks hide bugs until they surface far from their cause; loud failure keeps the failure local to where it can be understood and fixed.

### D03 — Deterministic Tests (checked)
Time is injectable. I/O is mockable at the trait boundary. Nothing in a test should require wall-clock delay or environmental state.

**Why.** Wall-clock or environment-dependent tests are flaky and slow; injecting time and mocking I/O at the trait boundary makes the suite fast and reproducible.

## Rules (migrated from CAE Rules.md, default tier: checked)

### D04 — Every Markdown File Prefixed with `{NAME}` (checked)
Every `.md` file and subfolder inside the anchor uses the `CAE` prefix. No unprefixed names like `PRD.md`, `Backlog.md`, `Plan/`.

**Why.** Consistent prefixing keeps the anchor's files unambiguous in search and wiki-links, and prevents collisions when files from multiple anchors share a workspace.

**Check pattern:**
- Walk the anchor tree. Any `.md` file or directory whose name doesn't start with `CAE ` or `CAE.` (other than `SKILL.md`, `CLAUDE.md`, `README.md`, `.anchor`) is a violation.

**Exceptions:**

_None._

### D05 — Blank Line Before Every Table (checked)
Every markdown table in the anchor is preceded by a blank line. Tables that come directly after a heading or paragraph without a blank line fail to render in Obsidian.

**Why.** Obsidian's renderer requires the blank line; without it the table silently degrades to literal pipe text.

**Check pattern:**
- Grep `^\|` lines. The preceding line must be blank.

**Exceptions:**

_None._

### D06 — Escape Pipes in Wiki-Link Aliases Inside Tables (checked)
Inside a table cell, wiki-links with an alias use `\|` to escape the pipe: `[[target\|alias]]`. An unescaped `|` breaks the column.

**Why.** An unescaped pipe is read as a column separator, shifting every following cell and corrupting the row.

**Check pattern:**
- Grep tables for wiki-links containing an unescaped `|` in the alias.

**Exceptions:**

_None._

### D07 — One Queue, One Clock (checked)
All task scheduling flows through `TaskScheduler.queue`. No module outside `src/execution/scheduler.rs` constructs its own priority queue, `BTreeMap<Instant, ...>`, `BinaryHeap<Task ...>`, or ad-hoc ordering of pending work.

**Why.** Concrete enforcement of the D01 principle in code; a second ordering structure anywhere would silently fork scheduling behavior.

**Check pattern:**
- Grep for `PriorityQueue`, `BinaryHeap<Task`, `BTreeMap<Instant` outside `scheduler.rs`
- Semantic: any sort-by-deadline over pending tasks

**Exceptions:**

_None yet._

### D08 — No `sleep()` in Production Paths (checked)
Production code does not call `thread::sleep`, `tokio::time::sleep`, `std::thread::sleep`, or equivalent. All time coordination goes through the injected `Clock` trait.

**Why.** A raw `sleep` reintroduces wall-clock dependence, breaking the deterministic-test guarantee (D03); routing through `Clock` keeps time injectable.

**Check pattern:**
- Grep `thread::sleep|tokio::time::sleep|std::thread::sleep` outside `tests/` and `src/clock.rs`

**Exceptions:**

| ID    | File                    | Line | Grade | Summary                                   |
| ----- | ----------------------- | ---- | ----- | ----------------------------------------- |
| EX001 | `src/cli/progress.rs`   | 42   | B     | UI refresh tick, 16ms — not time-critical |

**EX001 — `src/cli/progress.rs:42`**

- **Summary:** Progress bar refresh uses `thread::sleep(Duration::from_millis(16))` in the render loop.
- **Purpose:** Human-readable animation; not coordinating with task scheduling.
- **Keep:** Yes. Test coverage for progress rendering does not depend on wall-clock time.
- **Alternative:** Could route through `Clock`, but `Clock` is scheduler-scoped and this is a cosmetic concern.
- **Gain/Loss:** Keeping saves an architectural layer; loss is a tiny, localized `sleep` call isolated to UI.

### D09 — Fail Loudly, No Silent Fallbacks (checked)
When a task submission, worker init, or config load fails, code either returns an error that propagates to the caller or panics. It does not silently substitute a default, retry without logging, or swallow the error.

**Why.** Concrete enforcement of the D02 principle; a swallowed error converts a diagnosable failure into mysterious downstream misbehavior.

**Check pattern:**
- Grep `.unwrap_or(|_|` patterns with silent defaults
- Grep `.ok()` that discards an error without logging

**Exceptions:**

_None yet._

### D10 — Retries Are Declared, Not Implicit (checked)
Retry logic lives only in `src/retry.rs`. No other module wraps a call in a `loop { match ... }` to retry failures. Tasks declare their retry policy at submission time.

**Why.** Centralizing retry keeps the policy explicit and auditable; scattered ad-hoc retry loops hide latency and mask persistent failures.

**Check pattern:**
- Grep `loop { match` or `for _ in 0..` surrounding a `Result`-returning call, outside `retry.rs`

**Exceptions:**

_None yet._

## Anchor-specific applied choices (post-2026-06-08 rules/decisions split)

The H2 sections above (Principles, Rules) carry D01–D10 from the F113 unification. Going forward, this H2 holds true anchor-specific *decisions* — applied choices with rationale that cite rules from the adopted sets above. (Future migration may re-split D04–D10 into anchor-local rules under [[CAE Rules]]; deferred.)

### D11 — Architecture diagram authored in SVG, with arrows and labels on every edge (checked)

We chose hand-written SVG over D2 or Excalidraw for the `CAE Architecture/CAE Architecture.svg` figure to keep full control of palette, font, and arrow style consistent with the project's existing diagram aesthetic. Every arrow carries an italic-blue verb label (`submit`, `dispatch`, `persist`, `on failure`), and the figure includes a title element identifying it as "CAE Architecture" at the top.

**Cites:** [[R-c4-01]] (every arrow labeled), [[R-c4-02]] (title or legend present), [[R-wcag-contrast-01]] (text contrast ≥4.5:1), [[R-wcag-contrast-02]] (color is not the sole communicator — every box carries a text label naming its role). _(Renumbered 2026-06-09 from legacy R-diagram-07/13/16/17; see [[R-diagram]] § Migration map.)_

**Why.** Worked example of the new rules-vs-decisions split. The rationale captures CAE-specific application; the cited rules in [[R-diagram]] capture the portable, audit-checkable constraints. `/audit decisions` walks here, collects the citations, and verifies each on the SVG.

## Migration

Generated by `migrate-f113.py` Phase B. Source: `CAE Principles.md` `CAE Rules.md`. Why / rationale → [[CAE Decisions Details]]. D-numbers persist (never recycled).
