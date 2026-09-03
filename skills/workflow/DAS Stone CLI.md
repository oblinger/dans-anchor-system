---
description: "One-line-per-command reference for the `stone` script — mint, reorder, push, recall and propagate stones, addressed by list as `Slug[.list]`."
---

# stone — CLI reference
One line per command, as `--help` would print it. Semantics: [[DAS Stone]]. A stone is addressed by its LIST: the slug alone is the anchor's default list (`pebbles` vault-wide, `_:` in global.yaml), `Tink.rocks` a named one. Lists are declared under `stones:` in the anchor's `.anchor`. The older `stone <kind> <verb> <anchor> …` form still parses until the kind table retires (F628 step 4).

```text
stone new <list> --line TEXT [--body TEXT]    # mint {slug} P0001.md
          [--title T] [--date YYYY-MM-DD]
stone move <list> <id> --owner SLUG |         # reorder within its run
          --after ID | --before ID |
          --to-top | --to-bottom |
          --dest <list>                       # to another list

stone push <list> <id> --to SLUG              # place it on another
                                              #   anchor's list (T626)
stone recall <list> <id> --from SLUG          # take a pushed stone back
stone update [--dry-run] [--root DIR]         # reconcile every list,
                                              #   propagate feeds:,
                                              #   archive orphans

<list>     a slug, or slug.list: Tink = its default list (pebbles),
           Tink.rocks = a named one; lists are declared under stones:
           in the anchor's .anchor
<id>       P0001 | R0001 | S0001 | YYYY-MM-DD Title
--owner    disambiguates when two anchors share an id
--root     scan root (default $ANCHOR_VAULT_ROOT or ~/ob/kmr)
--dry-run  print every write and archive; perform none
--title, --date   dated lists only (book): member title, creation date

# legacy: stone <kind> <verb> <anchor> ...  kind = pebbles | rocks |
#   sleepers | book; same verbs; retires with the kind table.
# archive (no verb): delete the line from the stone's OWN control file,
#   then `stone update` moves the file to archive/. A line deleted from
#   any other list is re-added. Live: Tink P0020, P0021.
# conflict: one line edited in two places in the same pass is
#   CONCATENATED, never dropped (T642); clean up either copy by hand.
```

Exit non-zero on a refused mint, an ambiguous id, a `feeds:` cycle (whole pass aborts, no writes), or a missing live stone. Every write is printed. Script: `~/.claude/skills/workflow/scripts/stone`.

## Proposed — T653, not yet built

```text
stone move <list> <id> --dest <list>        # relocate: new number on
          [--after ID | --before ID |       #   the target, links follow
          --to-top | --to-bottom] [--force] #   (anchor update), old
                                            #   number retired by a
                                            #   tombstone in archive/
stone share <list> <id> --with SLUG         # second appearance on
                                            #   SLUG's list (was push)
stone share <list> <id> --recall SLUG       # take it back (was recall)
stone archive <list> <id> [--force]         # drop the line, move the
                                            #   file to archive/
--root     removed everywhere; tests set ANCHOR_VAULT_ROOT
--force    proceed on a shared-out stone; withdraws its appearances
```

Design and Dan's reasoning: [[Tink653 - stone verbs move gains --dest, share replaces push recall, archive is a|T653]].
