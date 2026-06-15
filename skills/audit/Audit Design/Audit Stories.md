---
description: "User stories for V2 audit — online auto-fix, the explicit Standard pass, annotate-don't-delete + sweep, and the opt-in aggressive pass."
---

# Audit Stories

The four stories that drive the design. Each names the trigger mode and automation level it exercises (see [[Audit PRD]] § Automation scale).

## US-AUDIT-1 — Online auto-fix while editing

**As the agent** writing a vault document, **I want** the safest mechanical defects fixed and the subjective ones flagged the instant I save, **so that** I correct in the loop without the user ever asking.

- *Trigger:* online (read/write hook). *Level:* Online.
- On a `Write`/`Edit`, the distilled rule corpus runs against the just-touched file. Rendering-corrupting defects (stray angle brackets, trailing whitespace, pipe-escapes, table blank lines) are auto-fixed in place; subjective findings are surfaced as a short agent message. Structure is never touched. Sub-second, every write.
- Realized by [[F003 — On-write rule hook + test workflow|F003]] / [[F004 — Audit-on-write hook — closed-off E2E slice|F004]] / [[F005 — Doc audit-on-write — vault-wide rollout + safety guard|F005]].

## US-AUDIT-2 — The explicit Standard pass

**As the user**, **I want** `/audit <anchor>` to bring it into conformance in one pass — fixing what is safe, reporting the rest — **so that** the anchor converges on its specs without me hand-applying each repair.

- *Trigger:* explicit `/audit`. *Level:* Standard.
- The engine resolves the anchor's facets → their rulesets → binds each rule to a target → runs mechanical `checked` rules by script, judges `stated`/`sampled` by agent, applies every `fix::` whose `check::` failed **plus bounded-judgment fixes** (a mis-filed story, a broken dispatch row), and re-runs to convergence. Radical or ambiguous findings are reported, not forced. `dry` makes it report-only.
- Realized by [[F001 — Rule-driven audit engine — resolve, run, judge|F001]] + [[F002 — Audit fix-by-default + Python rule functions|F002]].

## US-AUDIT-3 — Annotate, don't delete; sweep on demand

**As the user**, **I want** audit to never silently delete my content — when a rule says something should go, mark it and let me decide — **so that** I keep control of every removal, with a one-command sweep when I'm ready.

- *Trigger:* explicit `/audit` marks; explicit `/audit sweep` removes. *Level:* Standard to mark; the sweep is its own operation.
- A rule whose violation implies removal does not delete. It wraps the content in `> [!info] Recommend deleting — <why>` and leaves it. The marks accumulate until the user runs the separate sweep, which removes all marked blocks at once. The `aow-safety.py` alphanumeric-subsequence guard mechanically guarantees no fix ever drops a letter or digit.

## US-AUDIT-4 — Opt-in aggressive refactor

**As the user**, **I want** an aggressive pass that will restructure, reorder, and consolidate when I explicitly ask, **so that** a drifted anchor can be brought fully into shape in one deliberate sweep.

- *Trigger:* explicit, opt-in. *Level:* Aggressive.
- Everything Standard does, plus structural refactors the conservative levels withhold. Never the default — the user names it. (Per-anchor level pinning is the path to making this routine for scratch anchors and forbidden for careful ones.)
