---
description: "What V2 audit is — a rule-driven checker/corrector for vault artifacts, run explicitly and online, across a four-level automation scale that never deletes content."
---

# Audit PRD

Audit checks the user's artifacts against the rules that govern their structure — sourced from the facet and discipline specs — and corrects the violations it finds, both on explicit command and online as files are written.

## Overview

A **facet/discipline** specifies how a kind of artifact should be structured; embedded in each spec is a **ruleset** (`R-<name>` — see [[FCT Ruleset]]) whose rules carry a `check::` (how to detect a violation) and, increasingly, a `fix::` (how to repair it). Audit is the engine that **resolves** which rules apply to a given target (via each rule's `where::` selector), **runs** the mechanical ones by script and **judges** the rest by agent, then **fixes** what it safely can. It unifies today's piecemeal sub-audits (`structure`, `anchor`, `doc`, `dispatch`, `rules`, `q`, `markdown`, `architecture`, …) under one rule-processing pipeline.

It serves both the user — who runs `/audit` to bring an anchor into conformance — and the agent, who gets continuous in-the-moment correction from the online hooks while editing, so artifacts converge toward their specs without anyone having to remember every rule. The design record lives in [[Audit Features]]; the load-bearing pieces are the engine ([[F001 — Rule-driven audit engine — resolve, run, judge|F001]]), fix-by-default + automation levels ([[F002 — Audit fix-by-default + Python rule functions|F002]]), and the online write-path ([[F003 — On-write rule hook + test workflow|F003]], [[F004 — Audit-on-write hook — closed-off E2E slice|F004]], [[F005 — Doc audit-on-write — vault-wide rollout + safety guard|F005]]).

## Design Workflow

| Phase | Doc |
|---|---|
| Requirements (this doc) | [[Audit PRD]] |
| User stories | [[Audit Stories]] |
| Interaction surface | [[Audit UX Design]] |
| System design | [[Audit Architecture]] |
| Milestones | [[Audit Roadmap]] |

## Goals

- **One rule-processing engine** behind every audit surface — resolve → run → judge → fix, sharing a single rule corpus and `where::` selector vocabulary.
- **Fix by default** at the explicit surface; `dry` is the report-only opt-out.
- **Always-on online correction** via read/write hooks, at a conservative level that never touches structure.
- **A four-level automation scale** (Informational / Online / Standard / Aggressive) that a future per-anchor setting pins.
- **Never delete content** — every fix is content-preserving, enforced mechanically.
- **Preserve the existing sub-audits** while the engine unifies them over time.

## Non-Goals

- **Authoring or curating rules** — that is the `/rule` skill's domain. Audit only *consumes* rulesets (`[[F002 — Audit fix-by-default + Python rule functions|F002]]` covers how rules carry checks/fixes; cross-project curation is out of scope here).
- **Deleting flagged-for-removal content automatically** — audit marks; a separate explicit sweep removes.
- **Aggressive refactoring by default** — the Aggressive level is opt-in only.
- **Renaming the `/audit` verb** — it is wired into ~14 sub-actions and many docs; the default simply fixes.

## User Stories

Full set in [[Audit Stories]]. In brief:

- **As the agent editing a file**, I want the safest mechanical defects auto-fixed and the subjective ones flagged the moment I write, so I self-correct in the loop without being asked.
- **As the user**, I want `/audit <anchor>` to bring it into conformance — fixing what is safe, reporting the rest — in one pass.
- **As the user**, I want audit to never silently delete my content — when a rule says something should go, mark it and let me decide; a separate command sweeps the marks.
- **As the user**, I want an opt-in aggressive pass that will restructure and consolidate when I ask for it.

## Two trigger modes

- **Explicit** — `/audit [sub] [target] [dry]`. A thorough on-demand pass over an anchor or document. Runs at the **Standard** level by default.
- **Online** — `PostToolUse` hooks on read/write fire the distilled rule corpus against the just-touched file every time, with no user ask. Runs at the **Online** level. This is the always-on guardrail; `/audit` is the thorough backstop. The two share one rule corpus and one `where::` vocabulary.

## Automation scale (four levels, conservative → aggressive)

Audit's fixing aggressiveness is a **level**. Eventually each anchor is pinned to its level; for v1 the levels are a designed ladder with Online and Standard active.

| Level | Posture | What it changes | Where it's the default |
|---|---|---|---|
| **Informational** | flag only — zero edits | nothing; reports + inline annotations only | `dry`; any report-only pass |
| **Online** | always-on, safest mechanical only | corrupting-character fixes — stray angle brackets, trailing whitespace, pipe-escapes, table blank lines; **never structure** | the read/write hooks (no user ask) |
| **Standard** | thorough explicit pass | all `fix::` mechanical repairs **+ bounded-judgment fixes** incl. structural correctness (a misplaced story, a broken dispatch row); flags the radical/ambiguous | explicit `/audit` |
| **Aggressive** | opt-in deep pass | + structural refactors — restructure, reorder, consolidate | opt-in only |

**Why Online sits below Standard.** The online hooks fire automatically, without the user asking, so they must be *more* conservative than an explicit pass. Pulling stray angle brackets out of a document the agent just wrote is appropriate to do silently; relocating a mis-filed story or rewriting a dispatch table is not — that is the user's `/audit` to invoke. Online touches only what is unambiguously safe and rendering-corrupting.

## Never-delete invariant

Audit **never deletes content** at any level. It may move, rewrite, or condense; it must not remove a whole chunk (a section, paragraph, list, or worked example). When a rule implies content should go, audit wraps it in an **inline informational callout** (`> [!info] Recommend deleting — <why>`) and leaves it in place for the user to act on. Removing those marks is a **separate explicit operation** ("sweep deletion marks"), never bundled into a normal audit. Mechanically, the `aow-safety.py` guard ([[F005 — Doc audit-on-write — vault-wide rollout + safety guard|F005]]) enforces that every fix preserves the document's alphanumeric sequence as a subsequence — any fix that would drop a letter or digit is reverted and downgraded to a flag.

## Success criteria

**Tier:** 1 (agent-immediate)

**What done looks like.** `/audit <anchor>` resolves its facets' rules, runs+judges+fixes at Standard, and reports a per-rule pass/fail/N-A summary; `/audit <anchor> dry` reports without writing. An online write to a vault `.md` auto-applies the Online-level fixes and flags the rest, sub-second, never deleting content. The four-level scale and the never-delete invariant hold uniformly across the engine and both trigger modes.

**How it will be verified.** Per the engine and on-write feature docs: break a mechanical rule in a scratch copy of [[HBR]] → `/audit` repairs it and the re-run is green; `dry` writes nothing; an online write surfaces the Online fixes only; the safety guard reverts any alphanumeric-dropping fix to a flag.
