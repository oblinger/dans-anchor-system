# /audit surfaced

Verify every agent recipe's `surfaced::` determination still resolves. Per [[AREC]] § The fourth discipline, every recipe under `~/ob/kmr/SYS/Agent/Agent Recipes/` carries a `surfaced::` line declaring the mechanism that puts it in front of an agent when it's needed. **The claim is a citation, and citations rot** — a memory gets renamed, a CLAUDE.md line gets reworded, and the recipe goes on asserting a mechanism that no longer exists, silently, with nothing to notice.

**Reports findings only.** Fix work goes into a backlog entry; no recipe file is modified. A stale `surfaced::` line needs a human call (was the memory renamed, or genuinely deleted? did the recipe move area and now want `in-area` instead?) that the checker cannot safely make.

## Two checkable forms

Of the four forms [[AREC]] names, only two are mechanically checkable:

| Form | Check |
|---|---|
| `` memory — `<slug>` `` | A file `` <slug>.md `` must exist under `~/.claude/projects/-Users-oblinger-ob-kmr/memory/`. Hyphens/underscores in the slug are interchangeable — both are tried. |
| `` CLAUDE.md — <desc> `` | At least one backtick- or quote-enclosed literal excerpt inside `<desc>` must appear verbatim in `~/.claude/CLAUDE.md`. |

`in-area` (no mechanism — reachability comes from being in the area already) and `` skill — <name> `` / `` facet — <name> `` (resolved by the skill/facet loading machinery) are counted but not validated — there's nothing filesystem-checkable to verify for them here.

## Runbook

```bash
python3 ~/.claude/skills/audit/scripts/audit-surfaced.py            # full scan, text
python3 ~/.claude/skills/audit/scripts/audit-surfaced.py --json     # machine-readable
```

**Exit code:** `1` if any `broken` finding, else `0`. `unverifiable` (a `CLAUDE.md —` description with no literal excerpt to check at all) and `unparseable` (a `surfaced::` line matching none of the four known forms) are reported but don't fail the exit code — both need a human read to resolve, not a retry.

## Interpreting the report

- **Broken** — the declared mechanism no longer resolves: a `memory —` slug with no matching file, or a `CLAUDE.md —` description whose every literal excerpt has vanished from the global instructions. File a backlog row; the fix is either re-pointing `surfaced::` at what actually carries the fact now, or restoring the missing mechanism.
- **Unverifiable** — a `CLAUDE.md —` line describes the target in prose with no literal excerpt (e.g. *"the yore trigger row"* with nothing quoted). Not a failure — the recipe may still be perfectly reachable — but the claim can't be machine-checked as written. Consider tightening the description to quote the actual text.
- **Unparseable** — a `surfaced::` value that doesn't match `in-area`, `memory — `, `CLAUDE.md — `, `skill — `, or `facet — `. Likely a typo or a new form [[AREC]] hasn't documented yet.

## When to use

- **Vault sweep** — periodic whole-estate hygiene; nobody's single change triggers this, which is why it lives in the `sweep` moment rather than a per-anchor one.
- After a memory-store reorganization or a CLAUDE.md edit, to catch any recipe whose citation just broke.

## Cross-references

- [[audit/SKILL|/audit]] — parent skill; this is the `sweep` moment's recipe-citation check.
- [[AREC]] § The fourth discipline — the doctrine this audit verifies against.
