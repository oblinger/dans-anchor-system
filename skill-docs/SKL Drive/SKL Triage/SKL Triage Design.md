---
description: "design surface for `/triage`"
---
# SKL Triage Design

| -[[SKL Triage Design]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[SKL Drive]] → [[SKL Triage]] → [SKL Triage Design](hook://p/SKL%20Triage%20Design)<br>: design surface for `/triage` |
| --- | --- |
| --- | |

## 2026-06-23 — body source, banner counts, and the self-grooming sweep

Three corrections landed together after the Q.md body went untrustworthy.

**1. Body source: backlog rows, not the queries paste.** The F176 migration (ask → query) repointed the Q.md H1 *link* to `{NAME} queries.md` — correct. But the renderer over-reached and began *pasting the entire queries page as the Q.md section body*, skipping the backlog rows. Since the H1 banner counts the backlog, an anchor with no open user-questions showed a real count (`Ready 4`) above an empty body (`Nothing pending in scope`). Fix: the body is rendered from the backlog H2s again (per `[[FCT Triage]]` § Body H2s); the queries page is reached via the H1 link, never pasted. `read_queries_body` removed from `triage-section.py`.

**2. Banner counts: the merged headline numbers were under-counting.** `derive_banner` computed `active_n` and `verify_n` but never folded them into the displayed headline, and `[Agreed]` (the feature-lifecycle synonym for Ready) was uncounted. So `Ready` showed only bare `[Ready]` rows. Fix: headline `Ready` = `[Active]` + `[Ready]` + `[Agreed]`; headline `Questions` = pending `Q<n>` + `[Verify]` rows — matching the 2026-05-24 two-merged-groups design.

**3. Self-grooming sweep (the cheap groom subset, baked into the render).** Problem: triage sometimes showed/carried stale state because the backlog hadn't been groomed. **Why not run a full `/groom` before every triage?** Measured cost on the live vault: triage render `triage-section.py` ≈ **0.8s/anchor**; the `audit-q --fix` verify pass triage already runs ≈ **14s** (whole Q.md) / **~3s** (one anchor); a single `state task update` ≈ **3.8s** (its internal audit-q dominates). A *full* groom isn't a fixed number — it's agent reasoning over the whole backlog (promotion decisions, question-parking), i.e. tens of seconds to minutes **plus tokens** — far too expensive to gate every triage. **Key insight:** the staleness that erodes trust is almost always the *script-decidable* subset of `/groom` § 2a (date/placement facts, no judgment) — not un-promoted items. So `triage-section.py` runs just that subset, in place, before the render: (a) `[Done]` rows in a live H2 → relocated to `## Done`; (b) `[Verify-by <date>]` past date → auto-`[Done]` + relocated. **Measured added cost: ~1s**, and conditional (a clean backlog is a no-op). Everything judgment-heavy (`[Watching Nd]` body-date expiry, blocker-resolved, `[Ready]` hedging, lazy states, bracket/H2 mismatch, promotion, question-parking) stays in explicit `/groom`. Renderer spec: `[[SKA triage]]` § 5a. On first run it caught 7 stale `[Done]` rows hiding in MUX's `## Later`.
