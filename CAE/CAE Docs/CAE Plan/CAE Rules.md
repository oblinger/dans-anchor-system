---
description: project rules and exceptions
---

:>> [[CAE]] → [[CAE Docs]] → [[CAE Plan]]

# CAE Rules

Single destination for everything the audit system checks. Three sections, in this order:

1. **Design Principles** — the project's stated philosophy (P01, P02, ...). Canonical source; referenced by System Design and by the R-rules below.
2. **Structural Rules** — naming, markdown, dispatch-table, docs-sync checks. Apply to every anchor regardless of trait.
3. **Code Rules** — code-specific checks. Only present for anchors with the `code` trait.

Rule IDs (`R01`, `R02`, ...) and principle IDs (`P01`, `P02`, ...) never change once assigned. Exceptions are numbered `EX001`, `EX002`, ... and tagged in source with `// EX001` comments.

See `~/.claude/skills/rule/` for the tooling that scans code against these rules.



## Design Principles

The project's declared philosophy. Stated once here. Referenced by ID from System Design, Architecture, and the R-rules below. If the philosophy changes, edit here — nowhere else restates the principle.


### P01 — One Queue, One Clock

All scheduling decisions flow through a single priority queue and a single injected `Clock`. No module constructs its own queue, BTreeMap-over-deadline, or ad-hoc ordering of pending work. No module reads wall-clock time directly.

**Why:** parallel scheduling paths diverge under load and make starvation invisible. A single queue and a single time source give one place to reason about priority, fairness, and test determinism.

**Encoded by:** R01, R02


### P02 — Fail Loudly, No Silent Fallbacks

Errors propagate. Defaults are declared at the callsite or not at all. Retries are explicit and logged. Task failures reach the caller as errors, not swallowed with a substituted default.

**Why:** silent fallbacks mask broken production. We want failure to surface in dev, not after deployment.

**Encoded by:** R03, R04


### P03 — Deterministic Tests

Time is injectable. I/O is mockable at the trait boundary. Nothing in a test should require wall-clock delay or environmental state.

**Why:** flaky tests destroy trust. A test that depends on `sleep()` will eventually fail on a slow machine.

**Encoded by:** R02



## Structural Rules

Checks that apply to this anchor's files, regardless of whether it has code. Markdown formatting, naming, dispatch-table integrity, docs-vs-source sync.


### R10 — Every Markdown File Prefixed with `{NAME}`

**RULE:** Every `.md` file and subfolder inside the anchor uses the `CAE` prefix. No unprefixed names like `PRD.md`, `Backlog.md`, `Plan/`.

**Rationale:** Obsidian has a flat namespace across the vault. Unprefixed names collide with other anchors.

**Check pattern:**
- Walk the anchor tree. Any `.md` file or directory whose name doesn't start with `CAE ` or `CAE.` (other than `SKILL.md`, `CLAUDE.md`, `README.md`, `.anchor`) is a violation.

### Exceptions

_None._


### R11 — Blank Line Before Every Table

**RULE:** Every markdown table in the anchor is preceded by a blank line. Tables that come directly after a heading or paragraph without a blank line fail to render in Obsidian.

**Check pattern:**
- Grep `^\|` lines. The preceding line must be blank.

### Exceptions

_None._


### R12 — Escape Pipes in Wiki-Link Aliases Inside Tables

**RULE:** Inside a table cell, wiki-links with an alias use `\|` to escape the pipe: `[[target\|alias]]`. An unescaped `|` breaks the column.

**Check pattern:**
- Grep tables for wiki-links containing an unescaped `|` in the alias.

### Exceptions

_None._



## Code Rules

Checks that apply to source code in `Code/`. Present because CAE carries the `code` trait. Anchors without the `code` trait omit this section entirely.


### R01 — One Queue, One Clock (encodes [[#P01 — One Queue, One Clock\|P01]])

**RULE:** All task scheduling flows through `TaskScheduler.queue`. No module outside `src/execution/scheduler.rs` constructs its own priority queue, `BTreeMap<Instant, ...>`, `BinaryHeap<Task ...>`, or ad-hoc ordering of pending work.

**Check pattern:**
- Grep for `PriorityQueue`, `BinaryHeap<Task`, `BTreeMap<Instant` outside `scheduler.rs`
- Semantic: any sort-by-deadline over pending tasks

### Exceptions

_None yet._


### R02 — No `sleep()` in Production Paths (encodes [[#P01 — One Queue, One Clock\|P01]], [[#P03 — Deterministic Tests\|P03]])

**RULE:** Production code does not call `thread::sleep`, `tokio::time::sleep`, `std::thread::sleep`, or equivalent. All time coordination goes through the injected `Clock` trait.

**Check pattern:**
- Grep `thread::sleep|tokio::time::sleep|std::thread::sleep` outside `tests/` and `src/clock.rs`

### Exceptions

| ID    | File                    | Line | Grade | Summary                                   |
| ----- | ----------------------- | ---- | ----- | ----------------------------------------- |
| EX001 | `src/cli/progress.rs`   | 42   | B     | UI refresh tick, 16ms — not time-critical |

**EX001 — `src/cli/progress.rs:42`**

- **Summary:** Progress bar refresh uses `thread::sleep(Duration::from_millis(16))` in the render loop.
- **Purpose:** Human-readable animation; not coordinating with task scheduling.
- **Keep:** Yes. Test coverage for progress rendering does not depend on wall-clock time.
- **Alternative:** Could route through `Clock`, but `Clock` is scheduler-scoped and this is a cosmetic concern.
- **Gain/Loss:** Keeping saves an architectural layer; loss is a tiny, localized `sleep` call isolated to UI.


### R03 — Fail Loudly, No Silent Fallbacks (encodes [[#P02 — Fail Loudly, No Silent Fallbacks\|P02]])

**RULE:** When a task submission, worker init, or config load fails, code either returns an error that propagates to the caller or panics. It does not silently substitute a default, retry without logging, or swallow the error.

**Check pattern:**
- Grep `.unwrap_or(|_|` patterns with silent defaults
- Grep `.ok()` that discards an error without logging

### Exceptions

_None yet._


### R04 — Retries Are Declared, Not Implicit (encodes [[#P02 — Fail Loudly, No Silent Fallbacks\|P02]])

**RULE:** Retry logic lives only in `src/retry.rs`. No other module wraps a call in a `loop { match ... }` to retry failures. Tasks declare their retry policy at submission time.

**Check pattern:**
- Grep `loop { match` or `for _ in 0..` surrounding a `Result`-returning call, outside `retry.rs`

### Exceptions

_None yet._



## Format Reference

**Principle declaration:**

- **H3 heading** — `### P{NN} — Short Name`
- **Statement paragraph** — one paragraph stating the principle
- **Why:** — the rationale
- **Encoded by:** — comma-separated list of R-rule IDs that enforce this principle

**Rule declaration:**

- **H3 heading** — `### R{NN} — Short Name`, optionally followed by `(encodes P{NN})` with a wiki-link to the principle
- **RULE:** — the declarative statement; must be grep-able or describable as a pattern
- **Check pattern:** — how `/rule check` looks for violations (grep patterns, semantic cues)
- **Exceptions** — table with columns `ID | File | Line | Grade | Summary`, one row per exception
- **Per-exception block** — `EXxxx — path:line` heading followed by Summary, Purpose, Keep, Alternative, Gain/Loss

**Section ordering is fixed:** Design Principles → Structural Rules → Code Rules. `/audit rules` and `/rule check` rely on this ordering to find their scan targets.
