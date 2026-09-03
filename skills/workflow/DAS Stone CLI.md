---
description: "One-line-per-command reference for the `stone` script — mint, reorder, push, recall and propagate stones, addressed by list as `Slug[.list]`."
---

# stone — CLI reference
One line per command, as `--help` would print it. Semantics: [[DAS Stone]]. A stone is addressed by its LIST, `Slug[.list]`: the slug alone is the anchor's default list (`pebbles` vault-wide, `_:` in global.yaml), `Tink.rocks` a named one. Lists are declared under `stones:` in the anchor's `.anchor`. The older `stone <kind> <verb> <anchor> …` form still parses until the kind table retires (F628 step 4).

```
# mint {slug} P0001.md; the line lands atop the list's control file
stone new     <Slug[.list]> --line TEXT [--body TEXT]
                            [--title T] [--date YYYY-MM-DD]
# reorder within its run
stone move    <Slug[.list]> <id> --after ID | --before ID
                                 | --to-top | --to-bottom
                                 [--owner SLUG]
# place it on another anchor's list, with a receipt (T626)
stone push    <Slug[.list]> <id> --to SLUG
# take a pushed stone back off that list
stone recall  <Slug[.list]> <id> --from SLUG
# reconcile every declared list, propagate along feeds:, archive orphans
stone update  [--dry-run] [--root DIR]

<Slug[.list]>  Tink = its default list (pebbles); Tink.rocks = named
<id>           P0001 | R0001 | S0001 | YYYY-MM-DD Title
--owner        disambiguates when two anchors share an id
--root         scan root (default $ANCHOR_VAULT_ROOT or ~/ob/kmr)
--dry-run      print every write and archive; perform none
--title/--date dated lists only (book): member title, creation date

# legacy: stone <kind> <verb> <anchor> ...  kind = pebbles | rocks |
#   sleepers | book; same verbs; retires with the kind table.
# archive (no verb): delete the line from the stone's OWN control file,
#   then `stone update` moves the file to archive/. A line deleted from
#   any other list is re-added. Live: Tink P0020, P0021.
# conflict: one line edited in two places in the same pass is
#   CONCATENATED, never dropped (T642); clean up either copy by hand.
```

Exit non-zero on a refused mint, an ambiguous id, a `feeds:` cycle (whole pass aborts, no writes), or a missing live stone. Every write is printed. Script: `~/.claude/skills/workflow/scripts/stone`.
