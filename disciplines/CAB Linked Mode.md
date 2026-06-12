---
description: Linked Mode discipline — the pattern for an anchor whose code repository lives outside the vault. Anchor folder contains specs and dispatch pages; the code lives at a separate path declared via the `code:` key in `.anchor`.
---

# CAB Linked Mode

The pattern for an anchor whose code repository lives **outside** the vault. The anchor folder contains specs, dispatch pages, and planning content; the actual code lives at a separate filesystem path declared in `.anchor` via the `code:` key.

## What it is

A normal anchor under `~/ob/kmr/` is fully self-contained — code (if any) lives inside the anchor folder. A **Linked Mode** anchor inverts this: the anchor folder is metadata-only; code lives at an external path like `~/ob/proj/<name>/`. The skills and audits that operate on the code follow the `code:` pointer; the user reading the anchor in Obsidian sees the planning content here, but the executable bits are elsewhere.

## When to use it

- The code repo predates the anchor (long-standing project) and the user doesn't want to move it.
- The code repo is shared with collaborators who don't use the vault.
- The code repo needs its own git history independent of the vault's git.
- The code is very large (large checkouts, big build artifacts) and would clog the vault.

## How to declare it

```yaml
# .anchor
code: ~/ob/proj/<name>
```

Tools that need the code path read `.anchor`'s `code:` key. Tools that operate on docs ignore it (they walk the anchor folder normally).

## Current state

Skeleton spec — the pattern is in use (see worked examples below) but the full spec is TBD: how skills locate code, how audits report cross-boundary issues, how PR workflow handles two repos.

## Worked examples

- [[ob-utils]] anchor at `SYS/Bespoke/ob-utils/`, code at `~/ob/proj/ob-utils/` (Rust crate `rs/`, planned Python pkg `py/`).

## Related

- [[CAB Disciplines]] — parent catalog.
- [[CAB Aspects]] — Trait/Facet umbrella (Linked Mode may surface as a Trait declared in `.anchor`).

# BRIEF

- **This file is the discipline spec for Linked Mode**, not a directory of Linked-Mode anchors. Authority: defines the contract for anchors whose code lives outside the vault — the `code:` key in `.anchor`, the metadata-only anchor folder, the responsibilities split between docs and code repo.
- **NOT for per-anchor content.** Per-anchor specifics (slugs, paths, language traits, build commands) live in the anchor's own pages — never inline an anchor's particulars here. Worked examples are link-only references, not embedded detail.
- **Inclusion test for content on this page**: does it apply to *every* Linked-Mode anchor regardless of language, host, or repo layout? If yes, it belongs here. If it's specific to one anchor or one language ecosystem, it does not.
- **Naming and linking**: refer to the discipline as "Linked Mode" (two words, title case). Source anchors link to this spec via wiki-link `[[CAB Linked Mode]]`. The declaration key in `.anchor` is lowercase `code:` — do not rename to `code_path:` / `repo:` / etc. without updating every tool that reads it.
- **Load-bearing constraints**: the `code:` key is the single source of truth for where the code lives — never hard-code paths in skills or audits. The split is one-way (anchor → code via `code:`); the code repo does not need to know about the anchor.
- **Spec is skeleton-stage**: when fleshing out (skill cross-boundary semantics, audit reporting, PR workflow across two repos), update § Current state and add worked examples — do not silently delete the skeleton notice.
- **Don't restate Brief discipline rules here** — the Brief discipline lives in [[CAB Brief]]; this BRIEF section is the file-specific rule sheet only.
