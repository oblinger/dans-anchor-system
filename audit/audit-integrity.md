# /audit integrity

Detect backlog edits that bypassed [[workflow/scripts/backlog-edit|backlog-edit.py]]. Cross-references each anchor's `<NAME> Backlog.md` mtime against the last-script-run timestamp in `~/.config/ob-skills/backlog-edit/state.json`. Any backlog whose mtime is newer than the script's last recorded run for that anchor is a **bypass** — either an agent edited the file directly (a discipline failure) or the user edited it (in Obsidian, etc.).

The audit does **not** distinguish agent-bypass from user-direct-edit. Both look identical at the filesystem level. The report flags both; the user filters mentally by familiarity with their own activity.

## Mechanism

`backlog-edit.py` writes one entry per anchor to `~/.config/ob-skills/backlog-edit/state.json` on every invocation:

```json
{
  "anchors": {
    "SKA": {
      "last_run": "2026-06-02T18:52:56+00:00",
      "row_id": "F095",
      "verb": "added",
      "horizon": "Now",
      "status": "Designing"
    },
    "MUX": { ... }
  }
}
```

`/audit integrity` reads this file and compares each entry's `last_run` to the corresponding backlog file's `stat().st_mtime`. Three outcomes:

| Status | Condition | Meaning |
|---|---|---|
| `clean` | `backlog_mtime <= last_run + tolerance` | The script's recorded write is the most recent change. Discipline held. |
| `bypass` | `backlog_mtime > last_run + tolerance` | Something edited the backlog after the script's last run. **Could be an agent direct-edit (failure) OR a legitimate user direct-edit.** |
| `unknown` | No state entry for this anchor | The script has never been invoked on this anchor. All observed edits are direct. Usually means a fresh install OR an anchor whose entire history predates the retrofit. |

Default tolerance: **5 seconds** — handles filesystem timestamp resolution + the script's own internal delay between mutating the file and writing state.

## Runbook

```bash
~/.claude/skills/audit/scripts/audit-integrity.py            # full vault scan
~/.claude/skills/audit/scripts/audit-integrity.py --anchor SKA  # one anchor
~/.claude/skills/audit/scripts/audit-integrity.py --json     # machine-readable
~/.claude/skills/audit/scripts/audit-integrity.py --tolerance 60  # widen the grace window
```

**Exit code:** `0` when no bypass found, `1` when ≥1 bypass found. Useful for hooks / CI / scheduled checks.

## Interpreting the report

- **bypass section** is the actionable one. For each entry:
  1. Did **you** edit that backlog in the last day? (Obsidian, terminal editor, etc.) If yes — fine, dismiss.
  2. If no — an agent ran a direct `Edit`/`Write` against the file. The retrofit prose said not to, but skill drift happens. Track down which skill did it (cross-reference the timeline against your recent slash-command history) and tighten the retrofit.

- **unknown section** is mostly noise — it lists every anchor whose backlog file exists but has never been touched by `backlog-edit.py`. Expected immediately after the retrofit landed; expected to shrink over time as anchors get exercised.

- **clean section count** is the positive signal. As skills are exercised and the discipline holds, `clean` grows and `unknown` shrinks.

## When to use

- **Manually**, after a workflow-heavy session where agents touched many backlogs — quick check that the retrofit held.
- **Scheduled**, e.g. once a day via `cron` or a Stop hook — surfaces drift quickly.
- **As a CI check** on the skills repo before publishing — catches a retrofit regression before it ships.

## False positives

The user's own edits show up as bypasses. This is a fundamental limit of the mechanism; the audit cannot read minds. Two mitigations:

1. **Don't edit backlogs directly in Obsidian.** Use `backlog-edit.py` from terminal if you want a row update tracked. (Not always practical — sometimes you just want to fix a typo.)
2. **Mental filter.** The bypass report is small enough to scan. You know what you edited; everything else is real drift to chase.

## Composition

Calls into [[workflow/scripts/backlog-edit|backlog-edit.py]]'s state file. Per the script-vs-skill split, this skill is **report-only** — it does not modify any backlog. The state file is read-only from this skill's perspective.

## Cross-references

- [[audit/SKILL|/audit]] — parent skill; this is one sub-action.
- [[workflow/SKILL|workflow/SKILL.md]] § Mutation API — the discipline this audit verifies.
- [[workflow/scripts/backlog-edit|backlog-edit.py]] — the mutation tool whose state this audit reads.
