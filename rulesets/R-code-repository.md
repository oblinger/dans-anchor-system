# RULESET R-code-repository
include::
where:: `file:{anchor}/.anchor`
description:: how an anchor declares & resolves its associated code repository

What `/audit` checks on a `code`-trait anchor's repository association. Format of this set: [[DAS Ruleset]].

### RULE R-code-repository-01 — A `code`-trait anchor declares `code:` in `.anchor` (checked)
check:: anchor_has code

An anchor with the `code` trait carries a `code:` key in its `.anchor`; its presence *is* the declaration that code belongs to this anchor.

**Check pattern:** if `traits` contains `code`, assert a non-empty `code:` key in `.anchor`.

**Why:** the `code:` key is the single source of truth — there is no `code` symlink and no path-convention fallback.

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
