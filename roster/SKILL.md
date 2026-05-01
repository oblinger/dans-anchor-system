---
name: roster
description: >
  Show roster — concise summary of in-progress, ready, and backlog items
  for the current anchor, with a per-bucket count line at the bottom
  (one count per H2; sum equals total items in the backlog file). Icebox
  count shown separately. Use when the user says "show roster", "roster",
  "what's on the backlog", or asks for a state-of-the-work view.
tools: Read, Bash, Glob, Grep
user_invocable: true
---

# Roster — Backlog & In-Flight Summary

Render a concise view of what's currently in flight, what's ready to start, and what's deferred — drawn from the current anchor's Backlog file (and Icebox, if present).

DMUX trigger: **`show roster`** (two words). Skill name is just `roster`.

## When to Use

When the user types `roster` or `show roster`, or asks for a quick view of what's in progress, ready, or on the backlog.

## Output

Print these sections in order, **omitting any section with zero items**. Each entry shows its **F-number** so the user can refer to it unambiguously ("do F5", "tell me about F12"):

```
## Active
- **F<n> — <Item Name>** — <one-line gloss>

## Ready
- **F<n> — <Item Name>** — <one-line gloss>

## Now
- **F<n> — <Item Name>** [Status] — <one-line gloss>

## Next
- **F<n> — <Item Name>** [Status] — <one-line gloss>

## Later
- **F<n> — <Item Name>** [Status] — <one-line gloss>

---
Active: 2  Ready: 5  Now: 3  Next: 7  Later: 4  Questions: 4  Verify: 1  (Icebox: 12)
```

The **footer line always prints**, even when buckets are zero — the user sees the full picture every time. Each item appears in **exactly one bucket** (the H2 it lives under); the sum across the line equals total bullets in the backlog file. The **Icebox is counted but never listed** as a section.

The F-number is parsed from the source bullet. Source format per [[CAB Backlog]]: `- **F<n> — Item Name** [Status] — description`. If a backlog item lacks an F-number, render it as `- **F?** — <Item Name> — gloss` and flag the missing number — but don't fix it inline; that's a job for the skill that edits the backlog (`/groom` or manual repair).

## Sources

Find the current anchor by walking up from `cwd` until you hit `.anchor`. Read `{NAME} Docs/{NAME} Plan/{NAME} Backlog.md` (and `{NAME} Icebox.md` if it exists).

| Source H2 | Roster bucket | Kind |
|--|--|--|
| `## Active` | Active | workflow-state |
| `## Ready` | Ready | workflow-state |
| `## Now` | Now | horizon (per [[backlog-horizons]]) |
| `## Next` | Next | horizon |
| `## Later` | Later | horizon |
| `## Upcoming` | Now (legacy alias) | legacy — pre-horizons backlog |
| `## Done` | (not shown, not counted) | workflow-state |
| `## Legwork` | (not shown, not counted in active-work line) | category |
| Items in any H2 of Icebox file | Icebox count only | (separate file) |

**`Verify` and `Questions` are counted by bracket, not by H2.** There is no `## Verify` H2 — items in `[Verify]` state live in their horizon H2 (typically `## Now`) with the bracket. The `Verify` count in the count line is a derived statistic: scan all items across horizon H2s and count those with `[Verify]` bracket. **`Questions` works the same way**, except it excludes `## Later` items: scan `## Active`, `## Ready`, `## Now`, `## Next` for items with `[Questions]` bracket and count them. Items in `## Later` with `[Questions]` are deferred attention by definition — they're not part of the inbox. Items counted as `Verify` or `Questions` are *also* counted under their horizon H2 — see § Counts for the rule.

Missing sections / files → zero items.

## Item Format

Each source entry is an F-numbered named-list bullet:

```
- **F<n> — Item Name** [Status] — short description
```

Render the F-number and name together in bold, separated by an em-dash, exactly as in the source. Preserve the `[Status]` bracket for items in horizon H2s (Now / Next / Later) — that's where the workflow state lives. For items in workflow-state H2s (Active / Ready / Verify), the bracket is redundant and may be omitted from the rendered output to reduce noise.

Gloss the description to the first sentence or ~70 chars (whichever is shorter), suffix `…` if clipped. Preserve the source order within each bucket.

## Counts — per-bucket, no double-counting

Read the backlog file once. Compute each bucket:

**H2-based counts** (one count per H2; each item appears in exactly one of these):

- **Active** — bullets under `## Active`
- **Ready** — bullets under `## Ready`
- **Now** — bullets under `## Now` (or legacy `## Upcoming` if the anchor hasn't migrated)
- **Next** — bullets under `## Next`
- **Later** — bullets under `## Later`

**Bracket-derived counts** (items here are *also* counted under their H2 above — these are derived statistics, not partitions):

- **Questions** — items with `[Questions]` bracket across `## Active`, `## Ready`, `## Now`, `## Next` only. **`## Later` is excluded** — Later items are explicitly deferred attention; their questions don't belong in the inbox until they're promoted. Items with `[Questions]` in `## Later` are still listed under `Later`'s H2 count, just not added to `Questions`.
- **Verify** — items with `[Verify]` bracket across all horizon H2s.

**Separate file**:

- **Icebox** — bullets across all H2s in `{NAME} Icebox.md`, or `0` if the file doesn't exist.

`## Done` and `## Legwork` are excluded entirely. Done is terminal; Legwork is a category tag for autonomous agent work and is not surfaced in the roster.

**Order on the count line:** `Active`, `Ready`, `Now`, `Next`, `Later`, `Questions`, `Verify`, `(Icebox: N)`. The two bracket-derived counts (`Questions`, `Verify`) sit between the horizon counts and the separate-file Icebox tail, where the user expects to see "what's waiting on me" right before the cold-storage tail.

**Invariant:** `Active + Ready + Now + Next + Later` equals total backlog bullets (excluding Done/Legwork). `Questions` and `Verify` are bracket-derived overlays — they intentionally double-count items already accounted for under their horizon. See [[backlog-horizons]] § Roster integration.

## Failure Modes

- **No anchor found** — say "No anchor found from `<cwd>` upward." and stop.
- **No Backlog file** — say "No `{NAME} Backlog.md` at `<expected path>`." and stop.
- **Empty file** — print just the footer line, all zeros.

## Notes

- Render directly in chat; don't write to a file.
- The "Active", "Ready", and "Verify" sections are workflow states defined in [[workflow]]; the "Now / Next / Later" sections are horizons defined in [[backlog-horizons]]. Roster reads both axes from the file structure.
