---
description: "CLI reference for the `state` script — canonical state editor for everything below the anchor level (backlog rows + feature-doc Open Questions). Verb-first, anchor-flag with cwd-walkup, slug-as-alias hybrid. F129 (shipped 2026-06-07)."
---

# state — canonical state editor (CLI reference)

> **STATUS:** Canonical. Shipped 2026-06-07 via F129. Legacy `backlog-edit.py` ships alongside for the migration window — both scripts share helpers and the same state file; new code should prefer `state`.

## NAME

`state` — canonical state editor for backlog rows AND feature-doc Open Questions

## SYNOPSIS

```
state task create  [-a ANCHOR] --status S --title T [--horizon H] [--body B]
state task update  [-a ANCHOR] ROW-ID [--status S] [--horizon H] [--title T] [--body B]
state task delete  [-a ANCHOR] ROW-ID

state q    add     [-a ANCHOR] ROW-ID [--slug NAME] [BODY-source]
state q    answer  [-a ANCHOR] ROW-ID (-n N | --slug NAME) --choice OPT [BODY-source]
state q    remove  [-a ANCHOR] ROW-ID (-n N | --slug NAME) [--reason TEXT]
state q    rewrite [-a ANCHOR] ROW-ID (-n N | --slug NAME) [--slug NEW]      [BODY-source]
```

## ANCHOR RESOLUTION

`-a ANCHOR` (long form: `--anchor`) is OPTIONAL on every verb. Resolved in this order:

1. `-a PATH` — path to an anchor folder (the directory containing `.anchor`).
2. `-a SLUG` — slug name; script looks up via `ha --dump`. Errors if non-unique across the vault.
3. Flag absent — script walks cwd UP looking for `.anchor`; uses that folder.

Errors if all three modes fail (flag absent AND no `.anchor` ancestor of cwd).

## TASK SUBCOMMANDS

```
state task create   create a new row (mints Fnew or Bnew F-number).
                    --status S    required.  bracket text (Designing, Ready, …).
                    --title  T    required.  row title.
                    --horizon H   optional.  Now|Next|Later|Active|Ready|Verify|Done. defaults to Now.
                    --body   B    optional.  row body (wiki-links, dates, descriptions).
                    --kind   K    optional.  F (default) or B for backlog item.
                                  NOTE: does NOT create the feature doc file. /feature does that.
                                  Orphan rows (no doc) surface as audit-q findings — by design.

state task update   modify properties of an existing row.
                    ROW-ID        required positional.  F<NNN> or B<id>.
                    --status S    optional.  new bracket text.
                    --horizon H   optional.  new horizon (moves the row between H2 sections).
                    --title  T    optional.  new title.
                    --body   B    optional.  new body.
                                  At least one of --status/--horizon/--title/--body required.

state task delete   remove a row entirely. Rare — normally use `update --status Done`.
                    ROW-ID        required positional.
```

## Q (QUESTION) SUBCOMMANDS

```
state q add        add a new Q to the feature doc's `## Open Questions`.
                   ROW-ID        required positional (the row whose doc holds Qs).
                   --slug NAME   optional.  attach a semantic slug at creation.
                                 Block-ID always uses the Q-number (`^F128-Q5`);
                                 slug is metadata stamped in the bullet for cross-ref.
                   <BODY>        required.  via stdin / -m / --from-file (see § BODY SOURCE).
                                 Auto-mints the next Q-number per ask-format.

state q answer     move an Open Question to `## Resolved` as a `### Q<n> — Title` H3.
                   ROW-ID        required positional.
                   -n N          identify Q by number.    EITHER -n OR --slug.
                   --slug NAME   identify Q by slug.
                   --choice OPT  required.  the chosen option label, e.g. '(A)'.
                                            written into `**Choice:** OPT` in the H3.
                   <BODY>        optional.  resolution body via stdin/-m/--from-file.
                                            blockquoted original Q context is appended automatically.

state q remove     soft-delete a Q (preserves audit trail in `### Removed` H3).
                   ROW-ID        required positional.
                   -n N          identify Q by number.    EITHER -n OR --slug.
                   --slug NAME   identify Q by slug.
                   --reason TEXT optional.  short reason stamped in the H3 title.
                                            Q-number stays consumed forever; never reused.

state q rewrite    overwrite a Q's body. `rewrite` IS the explicit intent — no --force flag.
                   ROW-ID        required positional.
                   -n N          identify Q by number.    EITHER -n OR --slug.
                   --slug NAME   identify Q by slug.    (the existing slug)
                   --slug NEW    rename the Q's slug.   (same flag; second occurrence = new value)
                                 To attach a slug to a Q that didn't have one: just pass --slug NEW.
                   <BODY>        required.  new body via stdin/-m/--from-file.
```

## BODY SOURCE

Pick ONE. Priority order if multiple given:

```
-m TEXT          inline (short one-liners; shell-quoted).
--from-file P    read from file (long Qs / multi-paragraph bodies).
<stdin>          default when neither -m nor --from-file given. Heredoc-friendly.
```

## POST-CONDITIONS (Q-mode)

Every `state q` invocation runs the following post-condition. (The `{ANCHOR} queries.md` page is built on demand by `/query`'s determination logic — there is no separate render step.)

```
1. audit-q.py --scope q --dry — lenient warn. errors print to stderr; don't unwind the Q-edit.
                                cross-anchor errors never block a local Q-edit.
```

## EXAMPLES

```
# task: mint a new Designing feature, default horizon Now
state task create --status Designing --title "Sparse-checkout docs migration"

# task: cross-anchor mint (explicit slug)
state task create --anchor MUX --status Designing --title "Dmux ghost-panel bug"

# task: promote to Ready
state task update F099 --status Ready

# task: move horizon AND change body
state task update F099 --horizon Later --body "→ [[F099 — sparse-checkout]] — deferred to v2"

# task: rare delete (typo at mint)
state task delete F999

# q: add (stdin, numeric-only)
echo '**Q5 — short** — body.' | state q add F091

# q: add with slug at creation
echo '**Q5 — body** — ...' | state q add F091 --slug trigger-mechanism

# q: answer by number OR slug
echo 'team picked A' | state q answer F091 -n 5            --choice '(A)'
echo 'team picked A' | state q answer F091 --slug trigger  --choice '(A)'

# q: attach slug to existing Q (rewrite without changing body — pass --slug NEW)
state q rewrite F091 -n 5 --slug trigger-mechanism -m "**Q5 — trigger mechanism** — (body unchanged)"

# q: remove with audit trail
state q remove F091 -n 5 --reason 'obsoleted by F128'

# q: full rewrite of body
echo '**Q5 — rewritten** — fresh body.' | state q rewrite F091 -n 5
```

## DESIGN NOTES

**Why `state` and not `status` or `backlog-edit`.** `status` reads as "show me the status" (every actual invocation MUTATES); `backlog-edit` was the F128-era name when scope was just rows. `state` is honest about scope and direction.

**Why `task` and not `row`.** Agents and humans both think in "tasks," not "markdown rows." The conflict with the existing `task` skill (which manages shell-execution tasks) is contained by the `state task` namespacing.

**Why verb-first.** Surface is going to grow (`state doc`, `state messages`, `state verify` already feel inevitable). Verb-first keeps every command at the same grammatical shape.

**Why anchor is optional with cwd-walkup.** Agents almost always know their anchor implicitly via cwd. Path-based anchor lookup handles the non-unique-slug case across projects. Slug is still accepted for compactness when uniqueness holds.

**Why no `--force` on rewrite.** The verb name *is* the explicit intent declaration. `--force` was solving "did you mean to do this?" for a verb whose name literally means "yes, overwrite." Drop it. The Recommendation-presence gate from F128 is also dropped — the verb is enough.

**Why `answer` and not `resolve`.** Friendlier; matches how users say it. Section header stays `## Resolved` (state); verb is `answer` (action) — same ticket-system convention.

**Why this script doesn't create the feature doc file.** Separation of concerns: `state task create` mints the ROW; `/feature` owns the doc. Orphan rows (row exists, doc doesn't) surface as audit-q findings — by design. Trying to bundle would duplicate `/feature`'s shape conventions (frontmatter, Open Questions block, Status block, glance discipline) into the script and create a drift surface.

## IMPLEMENTATION STATUS

- **Shipped (F129, 2026-06-07):** `~/.claude/skills/workflow/scripts/state` is canonical. Verb-first restructure (`task create|update|delete` + `q add|answer|remove|rewrite`); `-a/--anchor` (path|slug|cwd-walkup); no `--force` on rewrite; `--slug` hybrid. Caller doc-sweep across `/feature`, `/query`, `/groom`, `/triage`, `/crank`, `/mint`, `/finalize`, `/rewire`, `/audit` SKILL.md files is incremental — both scripts coexist.
- **Legacy:** `~/.claude/skills/workflow/scripts/backlog-edit.py` ships the F128-era positional CLI + `-Q add|resolve|remove|rewrite` flag-mode. `state` delegates to its helpers via importlib — single source of truth at the helper level; both scripts share the same state.json file used by `/audit integrity`.

## RELATED

- [[DSC ask-format]] — Q-format spec the script enforces.
- [[F127 — Always-render ask report — ask invariant render + audit + glance before dialogue|F127]] — the render-audit-glance invariant `state q` post-conditions implement.
- [[F128 — Status script as source-of-truth for Q-management — extend backlog-edit.py|F128]] — the predecessor shipped 2026-06-07 (Q-management arrived under the old CLI shape).
- [[SKL Workflow]] — user-voice discipline page.
