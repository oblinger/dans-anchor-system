---
description: anchor-base — the implicit trait EVERY anchor carries by construction (engine key `anchor-base`). Never declared in `.anchor`; its members are the exhaustive always-on set the system applies everywhere.
---

# anchor-base

The **`anchor-base`** trait (the implicit base every anchor carries) is what every anchor is, before it declares anything: the implicit, applied-by-construction trait that carries the system's always-on behavior. This page exists so the user can see in one place exactly what the system does everywhere — a first-class documented object like every other trait (per F229 A′, 2026-07-06; the concept dates to the 2026-07-02 activation decision, formerly the internal literal `_base`).

## What it is

**Every anchor carries `anchor-base` — automatically, unconditionally, and without declaring it.** Both Warden dispatchers append it to an anchor's trait list at fire time, and the compiler stamps it into the IR's declared-traits snapshot, so "a trait-less anchor obeys nothing" is impossible by construction ([[Warden Semantics]] § Activation).

Its **members** — additional traits every anchor carries through it — are compiled policy: `warden_compile.ANCHOR_BASE_TRAITS` stamps them into the IR as `base_traits`, and both dispatchers expand an anchor's *effective* traits from that one compiled source. This page and that constant are kept in sync — the constant implements, this page documents.

## Current members

- **`audit-on-write`** — every anchored markdown file is doc-audited on write through the Warden dispatcher: mechanical fails with a `fix::` are repaired in place (never-delete floor), the rest are steered. Adopted into the base 2026-07-06 (F229 Q1 = A′), replacing the retired vault-wide `audit-on-write.sh` hook with coverage preserved.
- **`ob-remote-ops`** — remote-ops hygiene ([[R-ob-remote-ops]]): one-shot SSH remote-control (`ssh <host> '<cmd>'`) is denied at `tool:pre:Bash` with a redirect to the `bridge` skill's persistent-tmux control plane; bare attaches, `scp`/`rsync`, and in-bridge `tmux` commands pass. Adopted into the base 2026-07-06 (F183 — the commissioning specified a globally-firing deny, previously the would-be `bash-guard.sh` branch).
- **`state-region`** — the F236 advisory ([[R-state-region]]): an agent Edit/Write touching `## Open Questions` / `## Resolved` / `## Status` on an existing doc carrying labeled items gets the use-`state` reminder at `tool:pre:*`; the edit stands (advisory, per F236 Q3). Doc creation exempt. Adopted into the base 2026-07-13 (F236 M3 — the ratified design specifies vault-wide firing on any doc `state` can address).
- **`ios`** — Apple-platform guardrails ([[R-ios]]): ad-hoc code signing is denied at `tool:pre:Bash`/`tool:pre:Edit` (TCC grants reset every rebuild — sign with the user's Apple Developer account), and GUI-affecting test runs (`xcodebuild test`, simulator boots) get a steer to a `/bridge` agent on a remote machine. Every rule self-gates on Xcode tooling evidence, so non-Apple work never fires it. Adopted into the base 2026-07-13 (F237, user-directed).
- **`code-mirror`** — Two-Way Doc Mirror wrong-side-edit protection ([[R-code-mirror]]): an agent Edit/Write on the repo-side copy of a mirrored doc route is denied at `tool:pre:*` with a redirect to the vault original. Routes come from the `mirror-routes.json` index `code sync` regenerates. Self-gates on the route index, so anchors with no mirror routes never fire it.
- **`pathguard`** — veto-path protection for script-owned surfaces ([[R-pathguard]]): the agent's Edit/Write on `* Backlog.md` / `* queries.md`, a feature doc's `## Open Questions` / `## Resolved` region, or `Atlas/Atlas.md` is **denied** at `tool:pre:*` and redirected to the owning tool (`state` / queries-render / `/atlas`). The hard-DENY twin of the soft `state-region` advisory above — same surfaces, but blocked rather than reminded. `state`'s own writes are subprocess file I/O, not tool calls, so they pass; only an agent's direct Edit/Write is caught. Adopted into the base 2026-07-18 (F264, user-directed — closing the hole where the advisory reminded but the edit still landed).

Rules keyed directly by `anchor-base` (a `RULESET R-anchor-base`) would also fire everywhere; none exist yet.

## The rules

1. **Never declare it.** `anchor-base` (or a member it already carries) in a `.anchor` `traits:` list is redundant at best and misleading at worst — `warden compile` warns when it finds one.
2. **Scope = every anchor, and via the vault-root anchor, effectively the whole vault.** The vault root (`~/ob/kmr/.anchor`) is a first-class anchor, so every un-anchored vault path resolves to it and inherits the base behavior. Traits do **not** cascade into nested anchors — the everywhere-guarantee comes from this trait, not from the root anchor; the root anchor only catches otherwise-unowned territory.
3. **No opt-out (yet).** Base membership is mandatory everywhere; `warden off` is the global kill. A per-anchor negation mechanism (e.g. a `-trait` form) is future work, to be built when a real anchor first needs out.
4. **Membership changes are user decisions.** Adding a trait to the base applies behavior to everything the user owns — the same adoption doctrine as any trait (nothing is auto-adopted), decided at the F229-Q1 class of review, then recorded here and in `ANCHOR_BASE_TRAITS`.

## How it's detected

It isn't declared, so there is nothing to detect: `warden_fire.read_anchor_traits` appends `anchor-base` to every anchor's list, and `warden_fire.effective_traits` (mirrored in the Rust hook) adds the members from `ir.base_traits`.
