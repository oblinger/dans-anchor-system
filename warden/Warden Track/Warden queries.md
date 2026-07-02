---
description: Warden queries — mechanically rendered from the backlog by triage (Verifications / Ready+Next / Questions). Do not hand-edit; edit the backlog rows.
---

# [U+A]  [[Warden|Warden]]  -  Ready 2    Questions 8   |   Now 4    Next 1    Later 5    Verify 0    Icebox 0

## Ready
- [[F217 — Conversation-content gating — rules on what was said]] — **Next:** Design the bounded lazy `turn` view + the mechanical/ask_oracle gating, building on [[F216 — Agent-state model — sensing what the agent is doing|F216]]'s classifier + environment contract.
- [[F211 — Rule compiler and installer]] — **Next:** After the M0 language freeze ([[F209 — Unified trigger taxonomy + when language|F209]]/[[F210 — Conjunction binding + indexing|F210]] answers), design the compile→install→fire contract + skeleton;...
## Questions
- [[F214 — Rule-system testing regime]] **(1Q)** — designed; design landed 2026-07-01: five layers with concrete contracts; golden corpus live at [[Warden Corpus]] (runner + 4 seed goldens against the shipped...
- [[F216 — Agent-state model — sensing what the agent is doing]] **(2Q)** — designed; design complete 2026-07-01: closed five-state taxonomy, signal inventory, mechanical classifier (pending-question predicate + debounce invariants),...
- [[F209 — Unified trigger taxonomy + when language]] **(3Q)** — · finalize the trigger taxonomy: phase default for bare moments, `git:*` first-class vs derived, `skill:pre/post` emission point....
- [[F210 — Conjunction binding + indexing]] **(2Q)** — · pin the `if::` guard vocabulary (fixed vs registry) and whether `where::` precedence resolves before index choice; then the language freezes.
