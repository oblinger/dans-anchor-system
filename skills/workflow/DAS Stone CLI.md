---
description: "One-line-per-command reference for the `stone` script — mint, reorder, push, recall and propagate pebbles, rocks, sleepers and book entries. Kinds come from DAS Stone Kinds.json, not the script."
---

# stone — CLI reference
One line per command, as `--help` would print it. Semantics: [[DAS Stone]]. The `<kind>` form (`stone pebbles new …`) and the addressed form (`stone new Anchor.list …`, F628) are the same verbs; `Anchor` alone names the anchor's default list.

```
stone <kind> new     <anchor> --line TEXT [--body TEXT] [--title T] [--date YYYY-MM-DD]   # mint {slug} P0001.md, line goes to the top of its own control file
stone <kind> move    <anchor> <id> (--after ID | --before ID | --to-top | --to-bottom) [--owner SLUG]   # reorder within its run
stone <kind> push    <anchor> <id> --to SLUG                 # place it on another anchor's list, with a receipt (T626)
stone <kind> recall  <anchor> <id> --from SLUG               # take a pushed stone back off that list
stone <kind> update  [--dry-run] [--root DIR]                # reconcile every control file and propagate along feeds:; archives orphans
stone new | move | push | recall  <Anchor[.list]> …          # addressed form: `Lumen` = default list, `Lumen.rocks` = the named one

<kind>  pebbles | rocks | sleepers | book        # from DAS Stone Kinds.json; `stone <kind> --help` lists its verbs
<id>    P0001 | R0001 | S0001 | YYYY-MM-DD Title # the stone's number; `--owner` disambiguates when two anchors share one
--root  scan root (default $ANCHOR_VAULT_ROOT or ~/ob/kmr); `update --dry-run` prints every write and archive and performs none

# archive (no verb) : delete the stone's line from ITS OWN control file, then `stone <kind> update` moves the file to archive/.
#                     A line deleted from any other list is silently re-added. Live example: Tink Pebbles/archive/Tink P0020.md.
# conflict          : two projections of one line edited in the same pass are CONCATENATED, never dropped (T642); clean up either copy by hand.
```

Exit non-zero on a refused mint, an ambiguous id, a `feeds:` cycle (whole pass aborts, no writes), or a missing live stone. Every write is printed. Script: `~/.claude/skills/workflow/scripts/stone`.
