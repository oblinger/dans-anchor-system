---
description: anchor-level à la carte questions (agent-owned)
---


# [[CAE]] Questions

## Open Questions

- **Q1 — Should the CAE example use Rust or Go for code samples?** — context: CAE is a reference anchor; choosing one language pins the snippets. We've been using Rust in F1; switching means a sweep.
  - (A) Stay with Rust — already started; consistent with F1.
  - (B) Switch to Go — wider audience familiarity for an example project.
  - (C) Use both — alternate per feature.
  - **Recommendation:** Lean (A). Consistency wins; no real audience driver.

- **Q2 — Should the Roadmap have explicit version markers (v1, v2, …) or just sequence?** — context: the current Roadmap uses milestone IDs but no version semantics.
  - (A) Add version markers — `v1` = MVP, `v2` = priorities + groups.
  - (B) Sequence only — milestones are just ordered.
  - **Recommendation:** Lean (B). Versions imply releases; CAE is a reference, not a shipping product.

- **Q3 — Should `CAE Questions.md` itself appear in the dispatch table on `CAE.md`?** — context: it's a new facet; needs to be wired in for navigation.
  - **Recommendation:** Strong (yes). Add it next to `CAE Triage` in the Plan dispatch row.
