# Rules — Audit Code Against Project Rules

Check the codebase for rule violations. **Reports findings only.** Fix work goes into a backlog entry; no code or rule files are modified.

## Workflow

### 1. Detect rules file

Run `cab-config get rules` to locate the project's rules file. If no rules file exists, report `rules: no rules configured — skip` and stop. (Do not write a backlog entry; nothing to audit.)

### 2. Run rule check in report-only mode

Invoke `/rule check --all --report-only` (or whatever flag prevents `/rule check` from posting to stat or auto-grading). The goal is to surface every violation without side-effecting the rules file or the project.

If `/rule check` cannot run in report-only mode in the current implementation, capture its stdout findings and roll back any stat post it makes — this audit owns the entry, not the rule-check skill.

### 3. Build the findings table

| # | Rule | Location | Severity |
|---|------|----------|----------|
| 1 | NoSilentFallbacks | src/lib.rs:42 | high |
| 2 | NamingConvention | src/util.rs:18 | low |
| … | … | … | … |

Print the table to the console. **If `dry` substring is in args**, stop here — print "dry-run — no backlog entry written."

### 4. Write the backlog entry

Locate `{NAME} Docs/{NAME} Plan/{NAME} Backlog.md`. Read it, find the lowest unused B-number (per [[CAB Backlog]] § Format), and append a new bullet under `## Upcoming`:

```
- **B<n> — Rules audit: <N> violations (<YYYY-MM-DD>)** — work surfaced by `/audit rules`. Sub-bullets are candidate splits if this needs to be broken up.
  - <Rule>: <file:line> — <severity>
  - …
```

Group sub-bullets by severity (high → medium → low), then by rule name, then by file path. Keep each sub-bullet to one line.

If there are zero violations, do **not** write an entry.

### 5. Report

Print a one-line summary:
- With findings: `rules: N violations → B<n>`
- Clean: `rules: clean — no entry written`
- Dry: `rules: N violations (dry-run, no entry written)`

The orchestrator (or single-skill caller) will roll this up into the final stat post.
