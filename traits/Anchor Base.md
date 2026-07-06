---
description: Anchor Base Trait — the implicit trait EVERY anchor carries by construction (engine key `anchor-base`). Never declared in `.anchor`; its members are the exhaustive always-on set the system applies everywhere.
---

# Anchor Base

The Anchor Base trait (engine key **`anchor-base`**) is what every anchor is, before it declares anything: the implicit, applied-by-construction trait that carries the system's always-on behavior. This page exists so the user can see in one place exactly what the system does everywhere — a first-class documented object like every other trait (per F229 A′, 2026-07-06; the concept dates to the 2026-07-02 activation decision, formerly the internal literal `_base`).

## What it is

**Every anchor carries `anchor-base` — automatically, unconditionally, and without declaring it.** Both Warden dispatchers append it to an anchor's trait list at fire time, and the compiler stamps it into the IR's declared-traits snapshot, so "a trait-less anchor obeys nothing" is impossible by construction ([[Warden Semantics]] § Activation).

Its **members** — additional traits every anchor carries through it — are compiled policy: `warden_compile.ANCHOR_BASE_TRAITS` stamps them into the IR as `base_traits`, and both dispatchers expand an anchor's *effective* traits from that one compiled source. This page and that constant are kept in sync — the constant implements, this page documents.

## Current members

- **`audit-on-write`** — every anchored markdown file is doc-audited on write through the Warden dispatcher: mechanical fails with a `fix::` are repaired in place (never-delete floor), the rest are steered. Adopted into the base 2026-07-06 (F229 Q1 = A′), replacing the retired vault-wide `audit-on-write.sh` hook with coverage preserved.

Rules keyed directly by `anchor-base` (a `RULESET R-anchor-base`) would also fire everywhere; none exist yet.

## The rules

1. **Never declare it.** `anchor-base` (or a member it already carries) in a `.anchor` `traits:` list is redundant at best and misleading at worst — `warden compile` warns when it finds one.
2. **Scope = every anchor, and via the vault-root anchor, effectively the whole vault.** The vault root (`~/ob/kmr/.anchor`) is a first-class anchor, so every un-anchored vault path resolves to it and inherits the base behavior. Traits do **not** cascade into nested anchors — the everywhere-guarantee comes from this trait, not from the root anchor; the root anchor only catches otherwise-unowned territory.
3. **No opt-out (yet).** Base membership is mandatory everywhere; `warden off` is the global kill. A per-anchor negation mechanism (e.g. a `-trait` form) is future work, to be built when a real anchor first needs out.
4. **Membership changes are user decisions.** Adding a trait to the base applies behavior to everything the user owns — the same adoption doctrine as any trait (nothing is auto-adopted), decided at the F229-Q1 class of review, then recorded here and in `ANCHOR_BASE_TRAITS`.

## How it's detected

It isn't declared, so there is nothing to detect: `warden_fire.read_anchor_traits` appends `anchor-base` to every anchor's list, and `warden_fire.effective_traits` (mirrored in the Rust hook) adds the members from `ir.base_traits`.
