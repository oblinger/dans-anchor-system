---
description: "product requirements"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[skill-docs]] → [[SKL Drive]] → [[SKL Triage]] → [[SKL Triage Design]]
# Triage PRD

The current skill spec lives at [[triage/SKILL\|SKILL.md]]. User docs live at [[Q#SKL Triage|SKL Triage]].

**From:** [[F203 — Triage Skill]] · [[F205 — Triage and Q.md Format Rewrite]] · [[F204 — Triage Absorbs Groom]] (cancelled) · [[F206 — Auto-Groom on Empty Triage]] (designing)

## Overview

`/triage` surfaces the **status of an anchor** — everything waiting on the user (pending questions, items in `[Verify]`) plus what is actionable now (`[Active]`/`[Ready]`) — into one inbox so a multitasking user can decide their next move in a glance (F203). It is read-only over the work and write-only to its surfaces; it does not create feature docs, move items, or answer questions (that is `/groom`'s and the user's job). Per F075 the per-anchor `{NAME} Triage.md` retired in favor of the single vault dashboard `~/ob/kmr/Q.md`; the format/spine here is the F205 rewrite.

## Goals

- One keystroke (`"` or spoken `triage`) refreshes the anchor's section with maximum signal density.
- Strictly idempotent + destructive over agent-owned space — blow away and regenerate every run; user content is never touched.
- Stable mental map: body mirrors the backlog's horizon structure; items appear in backlog source order.

## Non-Goals

- Triage does not groom (no promoting, no parking, no answering) — it summarizes. *(F204 explored merging groom into triage; **cancelled** — the user chose to keep groom separate. F206 proposed a narrower auto-groom only on the `[G]` TAG; **still in design**, Q1–Q5 unresolved.)*
- Whole-feature verification only (no sub-item granularity in v1).

## User Stories

- As the user returning to an anchor, I read the H1 banner + TAG and immediately know whether I have work, the agent has work, both, neither, or there's grooming to do.
- As the user, I answer by reference ("F005 Q4: yes", "verified F23") and the agent maps each to the right backlog/feature-doc action.

## Key decisions

- **F-number addressing** (F203 Q4): triage addresses items by the backlog row's stable F-number; agent-raised à la carte questions use `A{n}` and live in `{NAME} Questions.md` (F205).
- **Verify-plan text comes from the backlog row** (F203 Q11): the agent that sets `[Verify]` writes what to verify + up to three wiki-links (`[[F<n> — Feature]] · [[agent-artifact]] · [[SKL X]]`); triage copies it verbatim. No `## Verify Plan` H2.
- **Verify → Done is the user-gated transition** (F203 Q12): "verified F23" moves the row to `## Done` and sets the feature-doc Status to Done.
- **Compact format** (F205): no blank lines in the body; status brackets carry counts (`[3 Questions]`, `[Verify]`, `[5 Ready]`); body links to feature docs, never inlines question text; H1 banner groups counts by pipe (user-actionable | agent-actionable | horizon) and carries an anchor **TAG** (`[U]`/`[A]`/`[U+A]`/`[G]`/`[?]`/`[]`) computed by a cascading rule.
- **Full body, never compressed** (F205 Q3): the dashboard shows each anchor's full body, or — past a size cap — just the link line; never a partial paste.
- **Compound "triage and groom"** handled at the Pilot level (natural language), not a flag.
