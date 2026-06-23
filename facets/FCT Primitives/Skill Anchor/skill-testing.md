---
description: skill-testing — facet specifying how a skill verifies its own behavior. tests/ folder split unit/ vs live/, mechanical PASS/FAIL, non-destructive.
applies-when-trait: Skill Anchor
location: ~/.claude/skills/`<skill-name>`/tests/
---

# CAB skill-testing

The skill-testing facet specifies *how a skill verifies its own behavior — a `tests/` folder under the skill directory, split `unit/` (env-free, portable) and `live/` (drives the real macOS GUI / tmux / files), reporting PASS/FAIL mechanically and never disturbing the user's real state.* What distinguishes a conformant test surface from ad-hoc scripts:

- **Two-folder split** — `unit/` for env-free checks (arg parsing, URL/string normalization, dispatch); `live/` for tests that touch the real system. The split keeps `unit/` cheap and portable; `live/` is quarantined because it can't run headless in CI.
- **Mechanical PASS/FAIL** — per-check `✓`/`✗` + final `PASS=N FAIL=M`; non-zero exit on any failure. No "eyeball the browser" steps.
- **Non-destructive** — live tests touch only resources they create (their own tabs, temp files, scratch tmux session) and clean them up. Snapshot relevant state before/after; verify net-zero.
- **No build system** — skills are scripts and markdown; tests run directly (`tests/live/<name>.sh`), not through `just` / `cargo` / `pytest`.

This is a CAB facet of the Skill trait — it applies to anchors that carry `traits: [Skill]`, and the content (the `tests/` folder) lives at the runtime location `~/.claude/skills/<skill-name>/tests/`, not under the anchor's filesystem folder.


## Layout

```
~/.claude/skills/<skill>/tests/
├── unit/      env-free checks (arg parsing, URL/string normalization, dispatch) — run anywhere
└── live/      drive the real system (browser via osascript, tmux, files) — need a Mac + GUI
```


## Conventions

- **Shell scripts** (`*.sh`) — one concern per file, self-contained and re-runnable.
- **Mechanical PASS/FAIL** — `osascript` / System Events for the browser/keyboard, tmux for sessions, file/log inspection for the verdict. Per the global CLAUDE.md "write an automated test that reports PASS/FAIL mechanically" rule.
- **Non-destructive** — never close/modify the user's real tabs, files, or sessions.


## Running

```bash
~/.claude/skills/<skill>/tests/live/<name>.sh    # one live test
~/.claude/skills/<skill>/tests/unit/<name>.sh    # one unit test
```

A per-skill or top-level aggregator (run-all) can come later; not required by the facet.


## Conformance

A skill **carries this facet** when it has a `tests/` folder with the `unit/` / `live/` split and at least one mechanical PASS/FAIL test. (Not every skill needs tests; this facet says *if/when you test a skill, this is how*.)


## Reference instance

`~/.claude/skills/ctrl/tests/live/test-surf.sh` — verifies `ctrl surf` always opens a new Chrome tab that loads, without disturbing existing tabs (before/after tab-count assertions; creates + cleans up its own sentinel and surf tabs; net-zero). Canonical example.


## Migration note (F116)

Migrated from `SKA skill-trait testing.md` per F116. Substantive content preserved; framing rewritten from "parallel-to-CAB trait" to "CAB facet of the Skill trait." Wiki-link sweep: `[[SKA skill-trait testing]]` → `[[CAB skill-testing]]`.
