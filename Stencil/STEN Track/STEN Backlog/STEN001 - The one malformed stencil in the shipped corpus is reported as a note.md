---
description: "Routed from [[Tink Backlog#^T210|TINK T210]], Scout's prior-art survey ([[2026-08-11 Stencil-like languages — one shape that generates and validates]]) finding 3."
---

# [[STEN]] · T001 — The one malformed stencil in the shipped corpus is reported as a note nobody reads, and nothing makes it a finding
Routed from [[Tink Backlog#^T210|TINK T210]], Scout's prior-art survey ([[2026-08-11 Stencil-like languages — one shape that generates and validates]]) finding 3.

next:: **There is no `R-sten` yet — creating it is the first half of this row, and its absence is already on the board as the C22 residual under B-QFix.** Stencil has a language spec, an engine and a restated corpus, and no ruleset, so nothing it rules can be enforced; the malformed-pattern class is simply the first rule that has a reason to exist. Create `rulesets/R-sten.md` with a `where::` over stencil-bearing files, arm it by naming it in [[R-anchor]] or [[R-doc]] (NOT [[R-facet]] — that umbrella is outside the executing closure and arms nothing, per [[Tink Backlog#^T208|TINK T208]]), and give it one checked rule for the adjacent-unbounded-variable defect. Keep `sten_match.py` as it is: raising there changes verdicts on a corpus that passes 33/33 and would fail the Computer template outright, trading a quiet defect for a loud regression in the same move, whereas a rule reports it, the template gets fixed, and the matcher never changes. Have the checker call the existing detectors rather than re-deriving the condition — a second copy of the condition is the seam that lets rule and matcher disagree. Fire-test against `_Computer {{NICKNAME}} Template.md`, and count the rest of the restated corpus in the same pass: the ruling has been in force since M2 and nobody has measured how many instances it has.

## Summary

Routed from [[Tink Backlog#^T210|TINK T210]], Scout's prior-art survey ([[2026-08-11 Stencil-like languages — one shape that generates and validates]]) finding 3. [[STEN Language]] § Variable extent already rules that two unbounded variables adjacent with no literal between them is **malformed** — a checkable defect, not a construct — and names the live instance: `SYS/SYS Catalog/Computer/_Computer {{NICKNAME}} Template.md`, the line `- **My nickname / short reference:** {{NICKNAME}}{{, phonetic hint if non-obvious — delete otherwise}}`. `sten_match.py` detects it in two places (`parse_stencil` line ~151, `_match_body`'s `settle` line ~325) and both **append a note and carry on**, binding all but the last hole to the empty string. So the ruling exists, the detector exists, and the defect has sat in a shipped template through M3 and M5 regardless, because a note is not a verdict and no surface reads it. `syntax-rules` is the contrast the survey draws: it makes the analogous case (a duplicate pattern variable) a **hard error** at macro-definition time, so the malformed pattern cannot reach a matcher at all.

## Status

**Ready** — minted from the backlog row by `state` on 2026-08-28 (F614: every task has its doc; the row is its pointer).
