---
description: "F222 — Doc-fire on write — run an anchor's doc-audit rules live on a markdown edit and steer, gated by an opt-in trait"
---

# [[Warden]] · F222 — Doc-fire on write

## Summary

Roadmap item 7 ([[Warden Roadmap]] § Live push). Wire the **doc-fire (audit-on-write) path into the live `write:markdown` moment**: when an agent writes a markdown file in an opted-in anchor, Warden runs that anchor's doc-audit rules on the written file and **steers** the agent with what is non-canonical — the `/audit doc <file>` pass, triggered automatically by the edit instead of by an explicit command. The doc-fire executor already exists and is verdict-identical to `audit-plan` ([[F212 — Python reference implementation|F212]] `warden_docfire.fire_audit`); this feature is the **dispatcher wiring + the opt-in trait gate**. It is the bridge to the real payoff (item 8): the markdown-discipline / progressive-disclosure layout rules firing live so Warden keeps documents in canonical form as they are written.

User directive 2026-07-02: *"go ahead and do your doc fire on write."*

## Success Criteria

**Tier:** 3 (live-environment behavior — user-observable)
**Blocks next:** [[Warden Roadmap]] item 8 (markdown-discipline stress-test rules fire through this path)

**What done looks like.** In an anchor whose `.anchor` declares the `audit-on-write` trait, a `Write`/`Edit` of a `.md` file makes the live hook run the doc-audit rules on that file and emit a steer naming each failing rule + detail; a clean file emits nothing. An anchor *without* the trait is unaffected (inert-by-default). `warden off` silences it like everything else.

**How it will be verified.** A unit test drives `dispatch()` with a PostToolUse:Write payload against a fixture anchor (trait on → steer with the failure; trait off → silent), and a live proof writes a deliberately non-canonical markdown file in the Warden anchor and reads the steer back through the real dispatcher.

## Design

- **Opt-in trait `audit-on-write`.** The gate is a plain capability trait in the anchor's `.anchor` `traits:` — not a ruleset-keying trait. The dispatcher checks `"audit-on-write" in anchor_traits`; only then does a markdown write trigger the audit. Inert-by-default (no anchor pays until it opts in), matching Warden's whole posture.
- **Wiring point — after the moment loop in `dispatch()`.** When the event is a `write:<kind>` markdown moment and the anchor opts in, call `warden_docfire.fire_audit(written_file, "doc")`, keep the `status != pass` verdicts, and turn them into one steer (`[warden audit-on-write] {file} has N issue(s): · {rule}: {detail} …`). Passes are silent. Reuses the same executor the golden corpus and `/audit` use — no parallel checker code.
- **Fail-safe + isolated.** The call sits inside the dispatcher's existing catch-all (a doc-fire bug can never break the write) and only runs for opted-in anchors on markdown writes, so the added cold cost (loading `warden_docfire` + `audit-plan`) is paid only where asked.
- **Re-evaluation is bounded, not yet economized.** `PostToolUse:Write` fires once per Write/Edit (not per keystroke), so v1 runs the file's doc-audit on each write. The heavier significant-edit gate ([[F215 — Re-evaluation economy — the significant-edit gate|F215]]) — skip when the edit can't have changed a verdict — is the future optimization, not a v1 blocker.
- **Steer only on `fail`, never on `error`.** A doc-audit verdict is `pass` / `fail` / `error`. Audit-on-write steers **only on `fail`** (a real content violation the writer can fix). An `error` — an unimplemented or broken checker — is a *rule-infrastructure* gap, not the doc-writer's problem; surfacing it on every write would be pure noise (a blast-radius scan of the Warden docs found the failures were almost all `error`/`unknown checker`, only one real `fail`). Errors still surface to the rule author through `/audit`; they never steer the writer.
- **Steer, never block.** Consistent with the pilot: audit-on-write emits `additionalContext`, never a `deny`. Blocking doc rules are out of scope here.

## Status

**Built + LIVE 2026-07-02.** The dispatcher (`warden_hook.dispatch`) now runs `audit_on_write()` after the moment loop when the anchor declares the `audit-on-write` trait and a markdown file was written: it fires `warden_docfire.fire_audit(file, "doc")` and steers each `fail` verdict (`[warden audit-on-write] {file} has N issue(s) to fix: · {rule}: {detail}`). Proven end-to-end through the **real dispatcher**: a violating markdown write in a trait-on anchor emits the steer naming `R-messages-01`, a trait-off anchor is silent, a clean file is silent, and `warden off` silences it. `test_warden_hook.test_audit_on_write` covers trait-on/off + clean-file.

**Adopted on the Warden anchor** (`warden/.anchor` `traits: [… audit-on-write]`) — the roadmap's adopt-first step, proven live against the real anchor. A blast-radius scan first confirmed it is non-noisy: with `fail`-only steering, **0 of 38 real Warden docs** would steer on write (the doc corpus is clean; the earlier apparent failures were all `error`/unimplemented-checker, now correctly excluded). No recompile needed — the gate reads `.anchor` live.

Ready for item 8 ([[Warden Roadmap]]): the markdown-discipline / progressive-disclosure layout rules now have a live path to fire on write.

## Open questions

1. **Scope of the audit per write** — v1 audits the single written file (`mode=doc`). Should a write ever trigger an anchor-level (`mode=anchor`) pass (e.g., a new file that changes anchor structure)? Deferred until the layout rules (item 8) show whether file-level is enough.
