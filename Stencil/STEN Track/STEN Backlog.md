| -[[STEN Backlog]]- | → [[DAS]] → [[STEN]] → [[STEN Track]] → [STEN Backlog](hook://p/STEN%20Backlog)  |
| --- | --- |
| ... | [[STEN Inbox]],  [[STEN Messages]],  [[STEN queries]],  [[STEN001 - The one malformed stencil in the shipped corpus is reported as a note]],   |

# Stencil Backlog
<!-- state:backlog o6 -->

Work in flight and queued for [[STEN|Stencil]] — the pattern language the anchor system is written in, one notation that both generates a document and tests whether a document fits.

## Active

## Ready
## Now
- ...

- **T001 — The one malformed stencil in the shipped corpus is reported as a note nobody reads, and nothing makes it a finding** [Ready] — → [[STEN001 - The one malformed stencil in the shipped corpus is reported as a note|T001]] — **There is no `R-sten` yet — creating it is the first half of this row, and its absence is already on the board as the C22 residual under B-QFix.** Stencil has a language spec, an engine and a restated corpus, and no ruleset, so nothing it rules can be enforced; the malformed-pattern class is simply the first rule that has a reason to exist. Create `rulesets/R-sten.md` with a `where::` over stencil-bearing files, arm it by naming it in [[R-anchor]] or [[R-doc]] (NOT [[R-facet]] — that umbrella is outside the executing closure and arms nothing, per [[Tink Backlog#^T208|TINK T208]]), and give it one checked rule for the adjacent-unbounded-variable defect. Keep `sten_match.py` as it is: raising there changes verdicts on a corpus that passes 33/33 and would fail the Computer template outright, trading a quiet defect for a loud regression in the same move, whereas a rule reports it, the template gets fixed, and the matcher never changes. Have the checker call the existing detectors rather than re-deriving the condition — a second copy of the condition is the seam that lets rule and matcher disagree. Fire-test against `_Computer {{NICKNAME}} Template.md`, and count the rest of the restated corpus in the same pass: the ruling has been in force since M2 and nobody has measured how many instances it has. ^T001

## Next

## Later

## Done

## Legwork
