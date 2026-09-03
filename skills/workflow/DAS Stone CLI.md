---
description: "One-line-per-command reference for the `stone` script — mint, reorder, push, recall and propagate stones, addressed by list as `Slug[.list]`."
---

# stone — CLI reference
One line per command, as `--help` would print it. Semantics: [[DAS Stone]]. A stone is addressed by its LIST: the slug alone is the anchor's default list (`pebbles` vault-wide, `_:` in global.yaml), `Tink.rocks` a named one. Lists are declared under `stones:` in the anchor's `.anchor`. The older `stone <kind> <verb> <anchor> …` form still parses until the kind table retires (F628 step 4).

```text
stone new <list> --line TEXT [--body TEXT]    # mint {slug} P0001.md
          [--title T] [--date YYYY-MM-DD] [--after REF]
stone move <list> <id> --owner SLUG |         # reorder within its run
          --after REF | --before REF |
          --to-top | --to-bottom
          --dest <list>                       # move to new list
stone share <list> <id> --with <list>         # also appear on <list>
stone share <list> <id> --recall <list>       # stop appearing there
stone archive <list> <id>                     # retire to archive/
stone update [--dry-run]                      # reconcile + propagate

<list>  slug or slug.list
<id>    P0001 | R0001 | S0001 | YYYY-MM-DD Title
REF     an <id>, or a label line's exact text (CYCLE 27:)
```

Semantics and the T653 design (relocation, tombstones, share, archive): [[DAS Stone]], [[Tink653 - stone verbs move gains --dest, share replaces push recall, archive is a|T653]].
