# RULESET R-code-repository
include::
import:: skills/audit/scripts/audit-plan.py
where:: `anchor`
description:: how an anchor declares & resolves its associated code repository

What `/audit` checks on a `code`-trait anchor's repository association. Format of this set: [[DAS Ruleset]].

> **Armed 2026-08-11 ([[TINK Backlog#^T212|T212]]) — the first of the forty, and it needed two repairs before arming meant anything.**
>
> **The selector could not match, at all.** It read `where:: file:{anchor}/.anchor`, and in anchor mode `enumerate_scope` builds its scope from `target.rglob("*.md")` — markdown only. `_match_file_glob` then selects *from that list*, so a `file:` selector naming any non-`.md` path resolves to the empty set, the ruleset drops out of `plan["groupings"]` entirely, and nothing reports that it did. Arming the set while it read that way would have added a row to the plan and changed no verdict. The `.anchor` file is reachable only through `where:: anchor`, whose synthetic target is the anchor root — which is what both of this set's checkers actually read (neither looks at `target`). Repaired to `anchor` here; **19 rules across 5 sets carry the unmatchable form** (this set, [[R-dot-anchor]], [[R-fct-folder]], [[R-feed]], and `R-doc-facet`'s `doc-region`, which is not a selector kind at all), the other four being outside the closure and so invisible until they are armed.
>
> **Its `(checked)` rule was the unconditional form of a conditional claim.** `-01` read `check:: anchor_has code`, which asserts a `code:` key on **every** anchor, while the rule's own check pattern says *if `traits` contains `code`*. Measured across the vault 2026-08-11: of **1,395** `.anchor` files, **27** declare the `code` trait, **24** of those carry the key, so the honest finding is **3**. The rule as wired reported **1,371** — 99.8% of them anchors that were never claiming to hold code. `-02` already encodes the conditional correctly (`not a code anchor` → pass), so `-01` was demoted rather than re-wired: the assertion it wanted already exists, once, in the rule beside it.
>
> Armed in [[R-anchor]] with `-02` as its one mechanical rule. It finds all three real cases — `SV/ww/Auto SV`, `SYS/Bespoke/ob-app`, and DAS's own [[HBR]] example anchor.

### RULE R-code-repository-01 — A `code`-trait anchor declares `code:` in `.anchor` (stated)

An anchor with the `code` trait carries a `code:` key in its `.anchor`; its presence *is* the declaration that code belongs to this anchor.

**Why:** the `code:` key is the single source of truth — there is no `code` symlink and no path-convention fallback.

**Demoted from `(checked)` 2026-08-11 ([[TINK Backlog#^T212|T212]]) — the checker asserted the claim's unconditional form.** `check:: anchor_has code` demands the key of every anchor, not of code-trait anchors; the measurement is in the set's header. The conditional assertion lives in `-02`, whose checker returns `pass` with *not a code anchor* the moment the trait is absent. Re-wiring `-01` would have meant a second checker computing the same verdict, so this rule keeps the declaration and `-02` keeps the enforcement.

### RULE R-code-repository-02 — No implicit fallback when `code:` is absent (checked)
check:: no_git_probe_fallback

A `code`-trait anchor with no `code:` key is an error — scripts must fail, never probe for `.git/` at the anchor root or look up a legacy `code` symlink.

**Check pattern:** resolver errors (does not silently locate a repo) when the trait is present but `code:` is missing.

**Why:** silent fallbacks hide misconfiguration; the spec forbids them generally.

### RULE R-code-repository-03 — Relative `code:` resolves against the anchor root (stated)

An absolute `code:` value is used as-is; a relative value resolves against the **anchor root** (the folder holding `.anchor`), not the caller's cwd; `code: .` is inline mode (repo == anchor root, `.git/` beside `.anchor`).

### RULE R-code-repository-04 — Doc mirroring is declared via `mirror:` in `.anchor` (stated)

Each route carries `here:` (anchor-root-relative) + `there:` (absolute path) + optional `direction:` (`two-way` default | `push` | `pull`). `mirror:` is independent of `code:` — it syncs two local folders; `there:` is never resolved against the code checkout.

**Why:** association ("where is the code") and sync ("what mirrors where") are different layers; coupling them was the old spec's hidden dependency.

### RULE R-code-repository-05 — The there side is never an authoring surface (stated)

Backward transport happens only for changes that arrived via git commits; uncommitted there-side edits are quarantined and flagged. The sync stamps there-side copies read-only.

**Why:** the here side is where user and agents co-author; silent backward flow would collide with live edits.
