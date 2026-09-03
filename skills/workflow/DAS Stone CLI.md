---
description: "One-line-per-command reference for the `stone` script — mint, reorder, push, recall and propagate pebbles, rocks, sleepers and book entries. Kinds come from DAS Stone Kinds.json, not the script."
---

# stone — CLI reference
One line per command, as `--help` would print it. Semantics: [[DAS Stone]]. The `<kind>` form (`stone pebbles new …`) and the addressed form (`stone new Anchor.list …`, F628) are the same verbs; `Anchor` alone names the anchor's default list.

```
# mint {slug} P0001.md; the line lands atop its own control file
stone <kind> new     <anchor> --line TEXT [--body TEXT]
                              [--title T] [--date YYYY-MM-DD]
# reorder within its run
stone <kind> move    <anchor> <id> --after ID | --before ID
                                   | --to-top | --to-bottom
                                   [--owner SLUG]
# place it on another anchor's list, with a receipt (T626)
stone <kind> push    <anchor> <id> --to SLUG
# take a pushed stone back off that list
stone <kind> recall  <anchor> <id> --from SLUG
# reconcile every control file, propagate along feeds:, archive orphans
stone <kind> update  [--dry-run] [--root DIR]
# addressed form: `Lumen` = default list, `Lumen.rocks` = named one
stone new | move | push | recall  <Anchor[.list]> ...

<kind>   pebbles | rocks | sleepers | book   (DAS Stone Kinds.json)
<id>     P0001 | R0001 | S0001 | YYYY-MM-DD Title
--owner  disambiguates when two anchors share an id
--root   scan root (default $ANCHOR_VAULT_ROOT or ~/ob/kmr)
--dry-run  print every write and archive; perform none

# archive (no verb): delete the line from the stone's OWN control file,
#   then `stone <kind> update` moves the file to archive/. A line
#   deleted from any other list is re-added. Live: Tink P0020, P0021.
# conflict: one line edited in two places in the same pass is
#   CONCATENATED, never dropped (T642); clean up either copy by hand.
```

Exit non-zero on a refused mint, an ambiguous id, a `feeds:` cycle (whole pass aborts, no writes), or a missing live stone. Every write is printed. Script: `~/.claude/skills/workflow/scripts/stone`.
