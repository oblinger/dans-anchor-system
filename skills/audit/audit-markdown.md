---
name: audit-markdown
description: Markdown hygiene rule runner. Checks touched (or all) markdown files against a rules library — bundled rules read-only, user-added rules in ~/.config/ob-skills/audit-markdown/rules/. Per F081 v1 minimal — no MCP, no Stop-hook auto-register yet, manually invokable.
---

# /audit markdown

Check markdown files against a library of hygiene rules. Each rule lives as a markdown file with embedded Python — rules-as-markdown means the rule's intent doc and its implementation live together in one file.

## When to use

- After editing one or more markdown files, to verify hygiene.
- Before committing a doc-heavy change.
- As a periodic sweep (`--all`) to catch drift across the vault.
- As a Stop hook (v2 — auto-register not yet wired; users currently invoke manually).

## CLI

```bash
# Check specific files
python3 ~/.claude/skills/audit/scripts/audit-markdown.py file1.md file2.md

# Scan the whole vault (vault_root from F080 global config)
python3 ~/.claude/skills/audit/scripts/audit-markdown.py --all

# Scan a subtree
python3 ~/.claude/skills/audit/scripts/audit-markdown.py --all "/path/to/dir"

# List loaded rules (what's active right now)
python3 ~/.claude/skills/audit/scripts/audit-markdown.py --list-rules
```

Exit code: `0` if no findings, `1` if any errors (severity = `error`), `2` on usage error.

## Rule architecture

Two locations, in load order (later overrides earlier on name collision):

1. **Bundled rules** — `skills/audit/rules-markdown/*.md` (read-only, ships with the skill).
2. **User-space rules** — `~/.config/ob-skills/audit-markdown/rules/*.md` (per F080 namespace; user-added).

Each rule is one `.md` file with this shape:

```markdown
---
name: my-rule-name
severity: warning   # or "error"
---

# My rule name

Prose explaining what this rule checks and why it matters. This part is for humans
reading the rule library; the agent doesn't act on it.

​```python
# The compile step extracts the first ```python``` block in the file
# and exec's it in a namespace with `Path`, `re`, `sys` already imported.
# Define a `check(file_path: Path) -> list[dict]` function. Each dict is
# {"line": <1-indexed>, "message": <str>, "severity": <optional override>}.

def check(file_path):
    findings = []
    # ... scan file_path, append findings ...
    return findings
​```
```

The compile step (in `audit-markdown.py`):
1. Read the `.md` file.
2. Parse YAML frontmatter for `name:` + `severity:` (defaults: file stem, `warning`).
3. Extract the first ` ```python ... ``` ` fenced code block.
4. `exec()` the block into a namespace pre-populated with `Path`, `re`, `sys`.
5. Pull `check` out of the namespace; expect callable.

If a rule file lacks the python block or `check` function, the loader prints a warning and skips it — the rest of the rules still load.

**Security note:** rules are `exec()`'d Python. Bundled rules ship with the skill (trusted). User-space rules are added intentionally by the user (trusted by definition — same trust level as installing a Python package). Do not load rules from third-party sources without inspection.

## Starter rules (bundled with the skill)

| Rule | Severity | Checks |
|---|---|---|
| `trailing-whitespace` | warning | No trailing spaces / tabs on any line. |
| `final-newline` | warning | File ends with exactly one `\n`. |
| `heading-spacing` | warning | ATX headings have blank line both before and after (except line-1 / immediately-post-frontmatter). |

## Adding a user rule

```bash
# Create your rule
mkdir -p ~/.config/ob-skills/audit-markdown/rules
cat > ~/.config/ob-skills/audit-markdown/rules/no-wiki-bare.md <<'EOF'
---
name: no-wiki-bare
severity: warning
---

# No bare wiki-link references to features

When linking to a feature doc by F-number, prefer the explicit form
`[[F<n> — Title]]` over `[[F<n>]]` so the displayed text carries the title.

​```python
import re
BARE_F = re.compile(r"\[\[F\d+\]\]")

def check(file_path):
    findings = []
    try:
        text = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return findings
    for i, line in enumerate(text.splitlines(), start=1):
        if BARE_F.search(line):
            findings.append({"line": i, "message": "bare [[F<n>]] — use [[F<n> — Title]]"})
    return findings
​```
EOF

# Verify
python3 ~/.claude/skills/audit/scripts/audit-markdown.py --list-rules
```

## Output format

```
audit-markdown: scanned <N> files; <K> findings (<E> errors, <W> warnings) from <R> rules
  [warning] trailing-whitespace path/to/file.md:42 — trailing whitespace (3 chars)
  [warning] final-newline       path/to/file.md:120 — file does not end with newline
  [error]   no-wiki-bare        path/to/file.md:15 — bare [[F<n>]] — use [[F<n> — Title]]
```

## What's NOT in v1 (deferred to follow-on work)

Per F081 spec § 11 + Resolved Qs — explicit scope decisions for v1:

- **No MCP server.** Each invocation is a one-shot Python run; no long-lived process. Per F081 Q1.
- **No PostToolUse hook.** Runs at end-of-turn (Stop hook) when wired, not on every tool. Per F081 Q3.
- **Stop hook auto-registration via `init.sh`** — deferred. Users currently invoke manually or wire the hook via `/update-config`. Per F081 Q4 (yes-eventually).
- **Backfill mode** (`--backfill` flag that re-runs all rules on the whole vault at install time, useful for catching pre-existing drift) — deferred. Use `--all` manually for now. Per F081 Q5 (yes-eventually).
- **Refactor to share infrastructure with `/audit q`** — deferred to v2 (per F081 Q7).

These are tracked as follow-on backlog items rather than blocking v1.

## Cross-references

- [[F081 — audit markdown — markdown hygiene via MCP server]] — full design + open-q resolutions.
- [[F076 — audit q — Q.md constraint validator with mechanical-fix mode]] — sibling auditor with a similar bundled-vs-user-space pattern; v2 refactor will share infrastructure.
- [[F080 — Skill config — unified namespace YAML]] — user-rule location depends on the F080 namespace; `vault_root` is read from F080 config.
- [[CAB Markdown Formatting]] — the rules library should grow to cover most of CAB's markdown conventions.
