---
description: "The rules-as-markdown hygiene library + loader/runner. Shipped (v1 core)."
---

# [[Audit]] · F008 — audit markdown — markdown hygiene rule library

## Summary

A new `/audit markdown` sub-skill that runs a Python script at end-of-turn (Stop hook) to check touched markdown files against a library of rules.

**Rules-as-markdown architecture.** Each rule is an H2 section in a markdown file: an English description above + a Python function (same name as the H2 slug) below. A compile step extracts the Python from all rule files into a runnable module. The skill ships with a bundled rule library (read-only, under the ob-skills repo); users can add custom rules in `~/.config/ob-skills/audit-markdown/rules/` per F080's unified namespace. Configuration (also per F080) selects which rules are active.

**v1 stack — deliberately minimal.** No MCP server, no PostToolUse hook, no agent involvement. Stop hook → Python script → reads compiled rules → scans `git diff --name-only` of markdown files → prints findings. Agent sees findings in the next turn and corrects naturally. Performance optimizations (MCP, monitoring) deferred until measurement justifies.

**Initial bundled rule library** (Q2-b leaning): description-chars (the seed problem), frontmatter-YAML validity, missing-H1, dangling wiki-link resolution.

**Distribution** (Q4-a leaning): `obskills-init.sh` extends to merge the Stop hook entry into `~/.claude/settings.json` and seed `~/.config/ob-skills/audit-markdown/config.yaml` with default rule selection.

**One-shot backfill** (Q5-yes leaning): `audit markdown --backfill` scans the whole vault using the same compiled rules, providing immediate value over the existing markdown corpus.

## Design

### Architecture

```
skills/audit/
├── audit-markdown.md                          # skill runbook (sub-skill of /audit)
├── scripts/
│   ├── audit-markdown.py                      # entry point — invoked by Stop hook
│   └── compile-rules.py                       # rule-extractor (v1 helper; refactor into /cab compile later)
└── checks/
    └── rules/                                 # BUNDLED rule library (ships with skill)
        ├── description_chars.md
        ├── frontmatter_yaml.md
        ├── missing_h1.md
        └── wiki_links.md

~/.config/ob-skills/audit-markdown/            # per F080 unified namespace
├── config.yaml                                # rule selection (which rules active)
├── rules/                                     # USER-ADDED rules (mutable)
│   └── my_custom_rule.md
└── compiled/
    └── rules.py                               # compile output: bundled ∪ user rules
```

### Rule file format

Each rule is an H2 in a markdown file. The H2 slug (kebab → snake_case) is the Python function name. The English content explains the rule for human readers; the fenced ```python``` block implements it.

```markdown
## description_chars

The frontmatter `description:` field must parse cleanly under standard YAML.
Agents often write wiki-links and backticks here that break YAML escaping;
this rule catches that and suggests either character-escape or switching to
block-literal `description: |` form.

```python
def description_chars(path: Path, frontmatter: dict, body: str) -> list[Finding]:
    desc = frontmatter.get("description", "")
    # detection logic returns a Finding with suggested_fix
    ...
```
```

**Multiple rules per file** are allowed — one H2 per rule, any number of H2s per file. Useful for grouping related rules (e.g. all frontmatter rules in `frontmatter_rules.md`).

### Compile step

`compile-rules.py` walks `skills/audit/checks/rules/*.md` (bundled) and `~/.config/ob-skills/audit-markdown/rules/*.md` (user), extracts each ` ```python ... ``` ` block under each H2, and concatenates into `~/.config/ob-skills/audit-markdown/compiled/rules.py`. The compiled module imports a uniform `Finding` dataclass + helper utilities from a base module, then defines one function per H2.

Compile invocations:
- **On install** — `obskills-init.sh` runs it once after writing the config.
- **On user edit** — user runs `audit-markdown compile` (manual; v1 doesn't auto-watch).
- **On runtime mismatch** — if `audit-markdown.py` sees the source files newer than the compiled output, it auto-recompiles before running.

v1 implements compile inside `skills/audit/`. v2 may refactor to `/cab compile` as a new target type — same verb, generalized infrastructure (per Q7).

### Runtime — Stop hook flow

```bash
# ~/.claude/settings.json — hooks entry (added by obskills-init.sh)
"Stop": {
  "command": "python3 ~/.claude/skills/audit/scripts/audit-markdown.py"
}
```

`audit-markdown.py` flow:

1. Read `~/.config/ob-skills/audit-markdown/config.yaml` to learn which rules are active.
2. Check if compiled output is stale relative to source files; if so, recompile.
3. Import compiled `rules.py`.
4. `git diff --name-only --diff-filter=AM HEAD` → list of touched files (extension filter to `*.md`).
5. For each file: parse frontmatter + body; for each active rule: call the function with `(path, frontmatter, body)`; collect findings.
6. If findings exist: print to stdout in agent-readable format (file:line — message — suggested fix).
7. Exit. (The Stop hook's stdout is captured by Claude Code and surfaced to the agent in the next turn.)

Total per-turn cost: ~50-150ms cold (Python startup + module import + N file reads). For sessions touching <10 markdown files, that's invisible against agent thinking time. If this ever becomes a hot path, promote to MCP per the deferred Q1.

### Configuration (per F080)

```yaml
# ~/.config/ob-skills/audit-markdown/config.yaml
rules:
  description_chars: enabled
  frontmatter_yaml: enabled
  missing_h1: enabled
  wiki_links: enabled
  # user-added rules listed here too
  my_custom_rule: enabled

# optional thresholds
severity_threshold: warning   # show warnings + errors; suppress info
backfill_concurrency: 4
```

YAML throughout (per F080). Round-trips cleanly via `ruamel.yaml`. User edits the file directly; no `audit-markdown config` CLI needed in v1.

### Distribution (per SKA Deployment Arch)

`scripts/obskills-init.sh` extends to:

1. Symlink `skills/audit/` (existing curated-skills behavior).
2. Run `audit-markdown compile` to produce initial `~/.config/ob-skills/audit-markdown/compiled/rules.py`.
3. Write seed `~/.config/ob-skills/audit-markdown/config.yaml` with all bundled rules enabled (only if file doesn't exist — don't overwrite a user's customization on re-run).
4. Merge Stop hook entry into `~/.claude/settings.json` via small Python merger (idempotent; preserves existing hooks).
5. Print "vault hygiene enabled — N bundled rules active" confirmation.

Merger respects existing entries — re-running init.sh is safe.

### Out of scope (v1 — explicit deferrals)

- **MCP server** (Q1). Stop hook + Python script is the v1 stack. Promote to MCP only if measurement shows hot-path cost matters.
- **PostToolUse hook** (Q3). The per-edit hook is deferred; end-of-turn batch is sufficient for v1.
- **Auto-compile-on-rule-file-change** — runtime auto-recompile (stale-check) handles this passably; filesystem-watch deferred.
- **Cross-vault rules** — single-vault assumption matches current usage.
- **Rule-authoring UI** — no `audit-markdown add-rule` CLI in v1; user creates rule files by hand using a documented template.
- **Generalizing to `/cab compile`** (Q7). Refactor in v2.

## Status

**Done 2026-05-24** — v1 minimal core shipped in commit `b539df3`:
- `skills/audit/scripts/audit-markdown.py` (240-line script): rules-as-markdown loader + runner, F080-aware `vault_root` resolution, CLI with file args / `--all [dir]` / `--list-rules`, bundled-vs-user-space override on name collision.
- `skills/audit/rules-markdown/`: 3 starter rules (`trailing-whitespace`, `final-newline`, `heading-spacing` with frontmatter-aware blank-line check).
- `skills/audit/audit-markdown.md`: skill runbook with rule architecture spec + user-rule add example.
- `skills/audit/SKILL.md` Actions table: `/audit markdown` row added.
- End-to-end verified: 766 SKA-subtree files scanned, 821 findings detected (legacy heading-spacing drift). Bundled rule library loads, dotted-key user override path works, `--list-rules` enumerates correctly.

**Follow-on work deferred** (in scope of F081 spec, not v1 minimal):
- **Stop hook auto-registration** (Q4 (a)) — needs `obskills-init.sh` to merge the Stop-hook entry into `~/.claude/settings.json`. Until then, users invoke manually.
- **`--backfill` mode** (Q5) — vault-wide scan at install time. `--all <dir>` already does this manually; the install-time variant is the missing piece.
- **MCP server form** (Q1 (b)/(c) deferred) — in-session live checking via MCP. Promote if measurement justifies; v1 doesn't.
- **Refactor to share infra with `/audit q`** (Q7 (a) v2) — both auditors have similar bundled-vs-user-space + rule-library patterns; common foundation is a v2 refactor opportunity.

These tracked inline on the F081 backlog Done row for now; promote to discrete B-rows if they remain dormant > 30 days.

All 7 Qs were resolved 2026-05-24 (Q1 per-session no MCP, Q2 (b) small varied set, Q3 Stop-hook only, Q4 (a) auto-register via init.sh, Q5 yes ship backfill, Q6 (a) bundled + user-space split, Q7 (b) parallel in v1 / (a) refactor in v2).

## Resolved

- **Q1 — Singleton-across-sessions vs per-session MCP server.** — **Resolution: simplest thing — per-session, no MCP server in v1.** v1 ships **no MCP server at all** — just a Python script invoked by the Stop hook. Promotion to MCP/singleton happens later if measurement demands. Incorporated into Design § Architecture.
- **Q2 — Initial bundled rule library for v1.** — **Resolution: (b) description-chars + small varied set** — also frontmatter-YAML validity, missing-H1, dangling wiki-link resolution. 3-4 rules of varied shape exercises the extension mechanism within ≈the same effort as (a)-minimal. Incorporated into Design § Initial bundled rule library.
- **Q3 — How is the server invoked — hook, agent-discretion, or both?** — **Resolution: Stop hook only, Python script (no agent involvement).** Drops PostToolUse from v1; end-of-turn batch is sufficient. Incorporated into Design § Runtime.
- **Q4 — Team-install path — how does this dovetail with F080 + SKA Deployment Arch?** — **Resolution: (a) Auto-register via `obskills-init.sh`** — init.sh installs the skill, adds the Stop hook entry to `~/.claude/settings.json` (merged, idempotent), and seeds `~/.config/ob-skills/audit-markdown/config.yaml` (per F080 unified namespace) with default rule selection. Turnkey for team-mates. Incorporated into Design § Install.
- **Q5 — One-shot backfill scan as v1 deliverable?** — **Resolution: yes** — ship `audit markdown --backfill` in v1. Backfill gives immediate value over the existing vault that accumulated under the old regime. Same compiled-rule module; just runs across all files. Cheap to add. Incorporated into Design § Backfill.
- **Q6 — Where do rule files live (both bundled and user-added)?** — **Resolution: (a) Bundled in `skills/audit/checks/rules/*.md`; user-added in `~/.config/ob-skills/audit-markdown/rules/*.md`** — read-only bundled + mutable user-space is the standard CLI convention. Compile step reads both directories. User disables bundled rules via config selection. Incorporated into Design § Rule file locations.
- **Q7 — Compile mechanism: reuse `/cab compile` or add a parallel mechanism?** — **Resolution: (b) parallel mechanism in v1, (a) refactor target for v2.** v1: implement rule extraction as a private helper inside `audit-markdown` to ship fast. v2: refactor into a `/cab compile` target once the rule shape stabilizes. Document the v2 intent in the skill runbook. Incorporated into Design § Compile.
