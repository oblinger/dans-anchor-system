---
name: dupes
description: Vault hygiene — scan for duplicate filenames; emit a confidence-ranked natural-language edit list; user instructs verbally, agent executes
user_invocable: true
---

# Dupes

`/dupes` — vault-level skill that scans for duplicate `.md` filenames using `ha --dump --format=collisions`, filters out expected duplicates via an allowlist, and emits a natural-language edit list (`E1..EN`) grouped by confidence. The user reviews and replies in free-form natural language; the agent (Claude) executes the selected edits using normal capabilities.

**No formal parser, no action enum, no script layer.** The skill's contract is the list it emits.

Feature design: [[F069 — Dupes skill (vault hygiene)]].

## When to use

When the user says `/dupes` — they want a sweep of duplicate filenames across the vault, with proposed fixes. Useful for catching misplaced files, accidental copies, partial moves, and other "data got mixed up" symptoms. **Detect-and-fix**, not detect-only — the user can already run `ha --dump --format=collisions` directly if they just want the list.

## Trigger

Slash-only: `/dupes <args>`. Not a DMUX prefix-trigger (`dupes` is too common a noun).

Args:
- (none) — scan the full vault (kmr root).
- `<path>` — restrict to a subtree.
- `--dry` — emit the edit list but refuse to execute even on user instruction.

## Runbook

### 1. Run HA collision detection

```bash
ha --dump --format=collisions --verbose
```

Returns every `.md` basename appearing in ≥2 locations across the vault, case-insensitively grouped, with full path lists per group (per HA F062, shipped 2026-05-14). If a `<path>` arg was supplied, post-filter to groups where ≥2 paths are under that subtree.

### 2. Read the allowlist + decisions

Look up both paths via the `ob-skills` omnibus helper (per [[F072 — Skills config file (~_.claude_skills.md)]]):

```bash
OBSKILLS=~/.claude/skills/ob-skills/scripts/ob-skills
ALLOWLIST="$("$OBSKILLS" config skill_data.per_skill.dupes.allowlist --default ~/ob/kmr/SYS/ob-skills/dupes/expected.md)"
DECISIONS="$("$OBSKILLS" config skill_data.per_skill.dupes.decisions --default ~/ob/kmr/SYS/ob-skills/dupes/decisions.md)"
```

Then read both files:

- **`$ALLOWLIST`** — bulleted filename patterns (basename-level allowlist; case-insensitive; `*` glob supported).
- **`$DECISIONS`** — per-group reviewed decisions (specific path sets, not basenames). Each H2 section is one decision; the `paths::` block under each H2 lists the exact sorted-absolute-path tuple that was reviewed-OK. Per [[F073 — Dupes per-group decisions (reviewed-and-OK without allowlisting the basename)]].

The helper falls back to the `--default` value if `~/.claude/ob-skills.md` doesn't exist or the key isn't set. Skills never fail for missing config.

For each collision group, do a **three-way classification check** in this order:

1. **Allowlist match** (basename matches `expected.md` pattern) → group is EXPECTED-BY-NAME. Excluded from edit generation; counted in the summary.
2. **Decision match** (sorted absolute path tuple matches a `decisions.md` H2's `paths::` block exactly) → group is REVIEWED. Excluded from edit generation; counted separately in the summary with the decision date.
3. **No match either way** → group is SUSPICIOUS. Proceed.

The two suppressions are conceptually distinct: allowlist suppresses the **name** anywhere it appears; per-group decisions suppress the **specific path set**. If a reviewed group's paths change (file added, removed, or renamed), the path-tuple no longer matches and the group re-surfaces — that's the intended "re-review on change" behavior.

### 3. Generate edits per suspicious group

For each suspicious group, do all five steps. Content reading is **mandatory**, not optional — path-based heuristics alone are not enough to make a defensible recommendation.

1. **Stat** each file (size, mtime).
2. **Read** each file in full.
3. **Characterize the relationship** between the files using the standardized vocabulary below — emit one **Content** line summarizing what we see.
4. **Apply heuristics** → confidence band + proposed action(s), anchored on the Content characterization.
5. **Assign** monotonic `E<n>` number.

E-numbering is monotonic across the three confidence bands (High first, then Medium, then Low).

### Content characterization vocabulary

Pick the most accurate phrase; paraphrase when none quite fit. The phrase precedes the recommendation in the output so the user can sanity-check the recommendation against what the agent saw.

| Phrase | When it applies |
|---|---|
| **Byte-identical** | All files in the group hash to the same bytes (case-insensitive file-hash match). |
| **One is empty (0 bytes)** | One file has zero content; others have content. |
| **One is a stub** | One file has only a breadcrumb/header (no real body); others have content. Detection: `< 100` bytes or content matches `^:>>` breadcrumb pattern with nothing else. |
| **Largely identical, minor divergence** | Files share `>~90%` of content; a few lines differ. Detection: line-overlap ratio. |
| **Largely overlapping with unique sections** | Files share substantial content but each has meaningfully unique sections. |
| **One looks like a later version** | One is a strict (or near-strict) superset of the other — same H1, more entries, more recent dates, more paragraphs. |
| **Different sections, partially overlapping** | Meaningfully different content with some shared material. |
| **Different content, same name (coincidental)** | Only the filename is shared; content is unrelated. |

### Confidence heuristics — anchored on Content

Content reading sharpens the bands. Path patterns inform but don't dominate.

| Band | Content signal | Default action |
|---|---|---|
| **High** | Byte-identical, or one is empty/stub | Delete the non-canonical copy. Canonical = most-likely-active (shortest path; not under `Closet/`/`Yore/`/`Archive/`). |
| **High** | Archive copy + identical/stub active | Delete the active; archive is canonical-historical. |
| **High** | Different content, same name (coincidental) + paths in genuinely different anchors with no signal of accident | **Leave alone — coincidental name collision.** (Leave-alone is valid at High confidence when the content evidence is unambiguous.) |
| **Medium** | One looks like a later version | Delete older / archive copy. Alt: rename to disambiguate (`<name>-old.md`). |
| **Medium** | Largely identical, minor divergence | Carefully merge into canonical; or delete one if the divergence is trivial. |
| **Low** | Largely overlapping with unique sections | Multi-option: carefully merge, keep-one + delete-other, rename, leave alone. |
| **Low** | Different sections, partially overlapping | Multi-option with leave-alone as default. |

Be conservative — when in doubt, downgrade. **Leave-alone is always available** as an option at any confidence level.

### Scaling — subagent dispatch for large N

For small scans (`N ≤ 10` suspicious groups), the main agent reads files inline.

For larger scans, **dispatch comparison subagents** so the main context stays clean and the work parallelizes. Each subagent takes a batch of `~5–10` groups and returns one structured record per group:

```
Group: <name> ×<count>
Paths: <path1>, <path2>, ...
Content: <one of the standardized phrases>
Confidence: High | Medium | Low
Recommendation: <natural-language action description>
Options: [<alt 1>, <alt 2>, ...]   (Low confidence only)
```

The main agent collects subagent results, sorts by confidence-band-then-group-size, assigns monotonic E-numbers across the full set, and renders the report (§ 4).

**Subagents handle volume; backlog handles user parking.** If the user wants to defer a specific group for later, that's a backlog candidate. The backlog is NOT a volume-relief valve — using it that way turns it into a junk drawer.

### Action vocabulary — plain English

- **Delete `<path>`** — mechanical filesystem op.
- **Move `<old-path>` to `<new-path>`** — mechanical.
- **Rename `<old-path>` to `<new-basename>`** — mechanical, same directory.
- **Carefully merge `<a>` and `<b>` — \<inline rules\>** — **agentic** (semantic merge; see § Merge guidance).
- **Leave alone — \<one-line reason\>** — explicit no-op.

### 4. Emit the edit list

Each edit uses a **nested structure**: bullet for the group + sub-bullets for **Content** (characterization), **Recommendation** (default action), and **Alt** (when applicable). This puts the content evidence right next to the recommendation so the user can sanity-check at a glance.

```markdown
## Edits (proposed) — N total

### High confidence (M edits)
- **E1** — `empty.md` ×2
  - **Content:** one is empty (0 bytes); the other has content.
  - **Recommendation:** Delete `/path/to/empty.md`. Canonical: `/active/path/empty.md`.
- **E2** — `stale.md` ×2
  - **Content:** byte-identical.
  - **Recommendation:** Delete `/Closet/stale.md`; archive is canonical-historical, but `/Topic/stale.md` is the active copy.
- **E3** — `MyNotes.md` ×2
  - **Content:** different content, same name (coincidental — distinct anchors).
  - **Recommendation:** Leave alone — no signal of accident.

### Medium confidence (K edits)
- **E15** — `notes.md` ×2
  - **Content:** one looks like a later version (10 more entries, latest `2026-02-14`).
  - **Recommendation:** Delete the older copy `/old-path/notes.md`; keep `/new-path/notes.md`.
  - **Alt:** rename old to `notes-2025.md` to keep the historical snapshot.

### Low confidence (J edits) — pick an option
- **E25** — `config.md` ×2
  - **Content:** largely overlapping with unique sections (both have distinct content blocks).
  - Options:
    - A) Keep `/anchor-a/config.md`, delete `/anchor-b/config.md`
    - B) Keep `/anchor-b/config.md`, delete `/anchor-a/config.md`
    - C) Rename `/anchor-a/config.md` to `config-anchor-a.md` (disambiguate)
    - D) Carefully merge — combine unique sections, keep at `/anchor-a/config.md`, delete `/anchor-b/config.md`
    - E) Leave alone

## Expected — filtered out

### Allowlist hits (basename, N groups)
- `SKILL.md` ×46
- `README.md` ×12

### Reviewed-group decisions (per-group, K groups) — see ~/ob/kmr/SYS/ob-skills/dupes/decisions.md
- `code-review.md` ×2 (decided 2026-05-15)
- `RASA.md` ×2 (decided 2026-05-15)
- …
```

Within each confidence band, sort by group size ascending (smallest groups first — accidents are usually 2-copy).

### 5. Wait for user instruction (no parser, just listen)

After printing the list, stop. The user replies in free-form natural language. Read it, identify which edits to execute (and how, for Low-confidence options), and act.

Common patterns to handle:

- *"do all high"* / *"execute all high confidence"* → every High-confidence edit's default action.
- *"E1, E3, E5"* / *"do E1 through E10"* → those edits.
- *"all high but skip E5"* → all High except E5.
- *"E12 option C"* / *"on E12 go with C"* → execute E12 using option C (override default).
- *"E20 leave alone, E25 option D"* → mixed.
- *"X is also expected"* → append `X` to `expected.md`, re-run from § 2.
- *"reviewed E<n>"* / *"mark E<n> reviewed-OK"* → append a new H2 to `decisions.md` capturing E<n>'s sorted path tuple + `verdict:: leave-alone` (and any free-form note the user provided). Future scans suppress this exact group. Per [[F073]].
- *"unmark <H2 title>"* / *"forget reviewed group <name>"* → remove the H2 from `decisions.md`. The group will re-surface on next scan.
- *"cancel"* / *"actually no, none of those"* → exit without changes.

If a user instruction is genuinely ambiguous, ask. Otherwise just act — per [[F068 — Assume-and-announce discipline (Drive mode)]], strong hypothesis + reversibility means execute, not ask.

### 6. Execute selected edits sequentially

For each selected edit:

- **Delete** → `rm <path>`.
- **Move** → `mv <old> <new>`.
- **Rename** → `mv <old-dir>/<old-name> <old-dir>/<new-name>`.
- **Carefully merge** → see § Merge guidance below.
- **Leave alone** → no-op.

Report per-edit outcome:
- `E1: deleted /path/X`
- `E5: skipped per instruction`
- `E12: merged /a + /b → /canonical, deleted /b`

Errors are reported per-edit, not bulk-abort the run.

### --dry flag

If `--dry` was passed: emit the edit list, then refuse to execute even on user instruction. Respond to execute requests with *"Dry run — no edits will be applied. Re-invoke without `--dry` to enable execution."*

## Merge guidance — executing "carefully merge"

When executing a `Carefully merge <a> and <b>` action:

1. **Read both files in full.**
2. **Choose the canonical path** — usually named in the action description. If unspecified, prefer the one NOT under `Closet/`/`Yore/`/`Archive/`; ties broken by shorter absolute path.
3. **Combine content** per the inline rules in the action description. Default rules:
   - **Dated entries** (H2/H3 with `YYYY-MM-DD`): merge in reverse-chronological order; dedupe identical entries.
   - **Sectioned by topic** (H2 sub-sections): combine sections; dedupe duplicates within each; keep the longer / more-detailed version.
   - **Redundant prose**: keep longer version verbatim; append unique paragraphs from shorter under `## Merged from <other-path>`.
   - **Default**: canonical content first; append unique content from other under `## Merged from <other-path>`.
4. **Write the merged content** to the canonical path.
5. **Delete the merged-from path.**
6. **Report**: `E<n>: merged <a> + <b> → <canonical>; deleted <b>`.

Action-description inline rules override the defaults — e.g., *"Carefully merge `/a.md` and `/b.md` — `/b.md` is older notes, append its bullets to bottom of `/a.md`, delete `/b.md`."*

## Out of scope (v1)

- **Auto-execute without user nod** — no `--yes` flag.
- **Cross-reference scanning** — which files link to which via `[[wiki-links]]`. Defer.
- **Non-`.md` files** — limited to what HA emits.
- **Inline content-diff display** — skill states "files differ" but doesn't render diffs.
- **Vault-level backlog** — findings stay conversational, not persisted.

## Implementation notes

- `ha --dump --format=collisions --verbose` is the underlying call. Output format depends on what HA shipped; parse accordingly.
- The allowlist is the only persistent state the skill maintains; everything else is computed per-run.
- Idempotence: re-running after edits should NOT re-list resolved groups (HA re-scans reflect filesystem state).
- **Allowlist vs leave-alone** — different mechanisms:
  - Allowlist = "never propose anything for these filenames" (suppression, doesn't appear in edits).
  - Leave-alone action = "surfaced edit explicitly tagged reviewed and kept" (visible acknowledgment).
