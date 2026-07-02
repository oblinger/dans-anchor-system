---
description: the golden test corpus — rule × fixture × expected-verdict cases, the drift oracle for every Warden engine
---
# Warden Corpus

| -[[Warden Corpus]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[Warden]] → [Warden Corpus](hook://p/Warden%20Corpus)<br>: the golden corpus — recorded expected verdicts that pin engine behavior |
| --- | --- |

The **golden corpus** is the shared behavioral record of the rule system: each case pairs a fixture (an input document or anchor tree) with the **canonical verdicts** an engine must produce on it. Any engine that implements the adapter contract — today the shipped `audit-plan.py`, later the Python reference ([[F212 — Python reference implementation|F212]]) and Rust ([[F213 — Rust performance implementation + ms budget|F213]]) implementations — runs the same cases; the corpus is also the shared input set for the Python↔Rust differential harness. Full regime design: [[F214 — Rule-system testing regime]].

## Case anatomy

Each case is one directory under `cases/`, named `<family>-<nnn>-<slug>`:

```
cases/msg-001-wrong-h1/
  case.yaml       # id, family, mode (doc|anchor), target, provenance,
                  # engine, blessed_against (pinned at bless time)
  fixture/        # the self-contained input tree; a file named _anchor.yaml
                  # materializes as .anchor in the sandbox copy
  expected.json   # canonical verdicts: sorted [{rule, target, status}]
```

**Canonical verdicts.** Equality is over `(rule, target, status)`, sorted — the full verdict set including passes, so a rule that silently stops matching surfaces as a diff. Engine `detail` strings are informational and excluded (message wording may churn freely).

**Sandbox execution.** The runner copies `fixture/` to a temp dir and runs the engine there — the stored corpus never carries a live `.anchor` (nothing pollutes the anchor scan) and vault-level audits of the Warden anchor see fixtures only as inert files.

## Running and blessing

```
harness/run-corpus.py                # run all cases → PASS / PASS* / FAIL / STALE-DIFF
harness/run-corpus.py --case ID      # one case
harness/run-corpus.py --bless        # re-record expected.json + re-pin blessed_against
```

- **FAIL** — the rule corpus is unchanged since blessing but verdicts moved: an engine or fixture regression. Fix the regression (failing case first, then the fix).
- **STALE-DIFF** — a rule edit moved the verdicts: expected churn. Re-bless consciously; **the review gate is the `expected.json` diff in the commit**.
- **PASS\*** — verdicts unchanged but the rule corpus moved since blessing; re-bless anytime to re-pin.

`blessed_against` is a content hash over the flattened rules' verdict-bearing fields, so it moves only when a rule change could move a verdict.

## Minting cases

Two provenances, both recorded in `case.yaml`:

- **harvested** — a real vault rule plus a real (minimized) violating or compliant file; name the source rule, e.g. `harvested (R-messages-01)`.
- **synthetic** — an edge case authored for coverage: one per `when::` family, `where::` selector form, `if::` guard shape, and execution mode as those land.

Every case gets a compliant twin where practical (`query-001` fails, `query-002` passes) so both directions of drift are pinned. Coverage target at the corpus-migration milestone ([[Warden Roadmap]] M4): at least one golden per rule family and per language construct.

## Versioning against the unfrozen language

Cases today are written in the shipped RULESET format and run against the live rule corpus through the `audit-plan` adapter — the only executable semantics that exist. When the language freezes ([[Warden Roadmap]] M1) and the corpus migration lands (M4), cases are re-expressed in frozen Warden language and gain a **vendored per-case ruleset** (fully hermetic — no live-corpus coupling); `blessed_against` then pins the language version instead of the live rules. The adapter layer in `run-corpus.py` is what keeps that migration a swap, not a rewrite.
