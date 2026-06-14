---
description: "Mortgage loan application moving across Applicant, Loan Officer, Underwriting, and Funding swimlanes from submission to disbursement"
---
# 12 — Swimlane process

**Diagram kind:** Swimlane process (cross-functional flowchart).
**Layout challenge:** actors as lanes × ordered process steps with cross-lane hand-offs — a 2-D grid where each node belongs to exactly one lane (its actor) and edges must read left-to-right (or top-to-bottom) in process order while frequently crossing lane boundaries; the engine must keep lanes contiguous, preserve step order within a lane, and route cross-lane hand-offs without tangling.
**Domain:** A residential mortgage loan application flowing from the borrower's submission through loan-officer intake, underwriting review (with a possible rework loop), and final funding disbursement.

## Nodes
- N1 — Submit application — [start] (lane: Applicant)
- N2 — Upload income & asset documents — [step] (lane: Applicant)
- N3 — Resubmit corrected documents — [step] (lane: Applicant)
- N4 — Receive & log application — [step] (lane: Loan Officer)
- N5 — Verify document completeness — [decision] (lane: Loan Officer)
- N6 — Request missing items — [step] (lane: Loan Officer)
- N7 — Order credit report & appraisal — [step] (lane: Loan Officer)
- N8 — Assess creditworthiness — [step] (lane: Underwriting)
- N9 — Underwriting decision — [decision] (lane: Underwriting)
- N10 — Issue conditional approval — [step] (lane: Underwriting)
- N11 — Decline application — [end] (lane: Underwriting)
- N12 — Prepare closing package — [step] (lane: Funding)
- N13 — Disburse loan funds — [step] (lane: Funding)
- N14 — Notify borrower of funding — [end] (lane: Funding)

## Edges
- N1 → N4 : "application submitted" [solid]
- N2 → N4 : "documents attached" [solid]
- N4 → N5 : "logged" [solid]
- N5 → N6 : "incomplete" [solid]
- N5 → N7 : "complete" [solid]
- N6 → N3 : "missing items requested" [dashed]
- N3 → N4 : "corrected documents" [solid]
- N7 → N8 : "file ready for review" [solid]
- N8 → N9 : "assessment done" [solid]
- N9 → N10 : "approved" [solid]
- N9 → N11 : "rejected" [solid]
- N9 → N6 : "needs more info" [dashed]
- N10 → N12 : "conditional approval" [solid]
- N12 → N13 : "package signed" [solid]
- N13 → N14 : "funds released" [solid]

## Groups / lanes / cardinality
- Four swimlanes (one per actor), each containing exactly the nodes listed: **Applicant** = {N1, N2, N3}; **Loan Officer** = {N4, N5, N6, N7}; **Underwriting** = {N8, N9, N10, N11}; **Funding** = {N12, N13, N14}.
- Two start nodes feed intake (N1 application, N2 documents). Three terminal nodes: N11 (declined), N14 (funded). 
- Two cross-lane rework loops route backward: N6 → N3 (Loan Officer back to Applicant) and N9 → N6 (Underwriting back to Loan Officer); these are the dashed edges. All forward hand-offs are solid.
- Every edge except the two intra-Applicant→Loan-Officer feeds and the two backward loops crosses a lane boundary; N1→N4, N2→N4, N3→N4, N7→N8, N10→N12 are the forward cross-lane hand-offs.

## Acceptance
- Fidelity: the render contains exactly these 14 nodes and 15 edges (count + labels match); none added or dropped.
- Legibility: text ≥ ~18px at page-width embed; aspect ~0.6–1.6; no overlaps; per [[R-diagram]].
