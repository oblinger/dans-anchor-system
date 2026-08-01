---
description: "mend messages for script-owned surfaces"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [rulesets](hook://rulesets) → [M-state-ownership](hook://p/M-state-ownership) 
# M-state-ownership
Remediation messages shared by [[R-pathguard]] and [[R-state-region]] — the twin rulesets that guard the same script-owned surfaces, one by denying the edit and one by warning about it.

These messages live outside a ruleset because they span two. `R-pathguard` denies the write and `R-state-region` merely reminds, but the recovery is identical, and the many-to-one `mend::` reference is what keeps one text serving both — per [[Warden User Docs]] § Remediation messages, the `M-` prefix is the sanctioned home for a message with no single owning ruleset.

## Mend

### MEND state-owns-the-edit

This file's rows are written by `state`, not by hand. Re-issue the change through it:

```sh
state <define|set|resolve|remove> <anchor> Backlog <F<n>|T<n>|C<n>|Q<n>> [flags]
state <define|resolve|remove> <anchor> "<doc path>" <Q<n>|V<n>> [flags]
```

The verb comes first and `<anchor>` is mandatory — never inferred from where you are standing (F293). Each verb declares its own flags, so `state <verb> --help` prints that verb's and no others: `set` takes `--status` / `--horizon` / `--title` / `--next` / `--verify` / `--user`, `resolve` takes `--choice`, `define` takes `--horizon` / `--why-ask`, `remove` takes `--reason`. Use `F+` / `T+` / `Q+` to mint the next number rather than picking one.

Why the guard exists: the backlog carries an integrity stamp, the queue file is rendered from it, and both propagate into the vault-wide `Q.md`. A hand-edit desynchronizes all three, and the drift is detected on the *next* write rather than yours — so the person who has to untangle it is not you.

Two cases where `state` genuinely cannot help:

- **The row is malformed enough that `state` cannot parse it.** There is no repair verb today; the only sanctioned path is `remove` then `define`, which loses the row's sub-bullets. Read the row first and keep what you need.
- **You are editing prose that is not a row** — an intro line, a section heading. Those are yours to edit; the guard covers the row regions.

On a feature doc the guard covers `## Open Questions` and stops there. A resolved decision under the bottom `## Resolved` is yours to edit (F291): once archived it is not rendered, not counted, and gates nothing, so there is no live state left to desynchronize — and half that section is written by a path no `state` verb can address, since an F068 auto-decision was never a question. Superseded-stamps, link repairs, and hindsight added years later are legitimate edits there. Answering a *pending* question is still `state resolve <anchor> <doc> Q<n>`, which is what moves it into the archive in the first place.

For the model, read [[DAS Backlog]] and [[DAS State]].

### MEND atlas-owns-the-edit

Atlas is written by the `/atlas` skill, not by hand:

```sh
/atlas add <name>        # new entry, inserted in alphabetical position
/atlas update <name>     # refine an existing entry in place
```

The skill enforces the four disciplines a direct write silently breaks: strict alphabetical order (never categorical grouping), one paragraph per entry, routing rather than duplication, and no info the reading agent could derive itself. It also updates the per-letter jump table at the top, which a hand-edit forgets.

Before adding, check the discipline the entry is most likely to violate: if a reader gets a complete answer from the Atlas entry without following any link, the content is in the wrong place. It belongs at the target; the entry should be a paragraph and a pointer.

There is exactly one Atlas, vault-wide. Anchor-local routing belongs in that anchor's dispatch table — never a scoped parallel like `prj/Atlas.md`.

For the model, read [[Atlas]] itself.
