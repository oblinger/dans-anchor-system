# EXP Experiment Template

One page per run, named for its folder, beside its script and its outputs. The write-up sits on top; the execution record follows. The design half is written before dispatch and frozen there; the run half is appended after. This is also the "results template" yoke's writeup gate refers to.

The `run::` execution contract lives in the sibling `{run} Setup.md`. **Nothing on the page links outside its own folder** — the folder has to survive being zipped and read months later out of context.

Everything from here to the scissors is the template, as live markdown. `{{curly braces}}` mark what you supply.

---

# {{Run name}} Writeup

**Question:** {{one line}}

## Potential Approaches

**{{the primary choice}}**
1. **{{option}}** — {{what it does, and what it tests}}
2. **{{option}}** — {{what it does, and what it tests}}

**{{a second, orthogonal choice}}**
1. **{{option}}** — {{what it does, and what it costs}}
2. **{{option}}** — {{what it does, and what it costs}}

**Chosen: {{n · n · …}}** — {{why, and why not the others}}

{{Any choice that decides whether the whole run means anything gets a paragraph here.}}

## Expectations

1. {{outcome}} → {{what it would mean}}
2. {{outcome}} → {{what it would mean}}
3. {{outcome}} → {{what it would mean}}
- {{rider}} → {{what it would mean}}

**Expected: {{n}}**, because {{mechanism}}

**Would change my mind:** {{the observation}}

## Result

{{The claim, in bold, one sentence with the number in it. Then the figure, and one line saying what to look at.}}

## The but

{{The limitation, before a reader has to ask.}}

---

# {{Run name}} Experiment

## Answer criterion

{{The form the answer must take.}}

## Controls

- {{control}} — rules out {{what}}
- **Instrument check** — {{what proves the manipulation fired}}

## Timebox

{{Budget, and what gets cut if it is blown.}}

## Threats

{{What would make the result meaningless whichever way it comes out.}}

---

## Environment

## What Ran

## Findings

## Verdict

## Next

## Assets

---

# ✂ Filling it in

## The two blocks

**Potential Approaches** and **Expectations** share one form: mutually-exclusive options, numbered, then a committed choice with the reasoning under it.

**Numbered items are mutually exclusive** — exactly one gets built, or exactly one comes true. Forcing candidates into a numbered list is what surfaces the option you had not considered; a list of two obviously-incomplete alternatives reads as obviously incomplete.

**Approaches usually need several lists, not one.** A design is a technique choice *plus* orthogonal ones — where the behaviour is measured, how deep, how much, which positions. Each is its own question, gets its own bold header, and gets its own numbered options. Flattening them into a row of dots under one list is how a design decision gets defaulted instead of made.

**Expectations need one list**, of outcomes, plus dotted riders that can accompany any of them.

**Each option needs enough words to stand on its own.** A bare *"Rank 1"* is a note to yourself, not a design — someone who was not in the conversation has to be able to read it. What belongs under **Chosen:** / **Expected:** is the reasoning *for the choice*; what each option means stays with the option.

**None of this notation belongs in the document.** A reader does not need to be told what a numbered list means.

### An expectation block, worked

The numbered outcomes have to cover the space, **including the boring one and the broken one**. A list that omits *"nothing happened and the instrument was fine"* and *"nothing happened because the instrument never fired"* cannot tell those apart when the number comes back zero.

Live example, from a rank-1 ablation of a truth direction in a 24-layer model:

1. Damage at L10 → the probe and the answer are one computation, found eight layers before it surfaces.
2. Damage at L18 but not L10 → the model carries a readable representation for eight layers without committing to use it.
3. No damage anywhere, instrument check fires → the fact is redundant or distributed; rank-1 removal does not disturb it.
4. No damage anywhere, instrument check silent → not a result. Plumbing.
- The topic control hurts as much as the truth direction → whatever moved was not about truth.
- Steering moves the answer where ablation does not → influence without necessity.
- The direct-effect cosine is near zero → any effect is indirect. Expected, and not evidence against.

**Expected: 3**, because the lens shows the answer gap flat below +1.3 through L17 and then jumping to +8.3 in one block. Almost nothing about the answer is in the residual before L18, so a direction read at L10 that fed the answer should have left an accumulating trace, and there is none. The probe meanwhile stays at 0.84 through L24 — signal present at many depths at once is the profile that shrugs off one rank-1 removal.

**Would change my mind:** a drop at L18 that clears the topic control. That is outcome 2, and it is falsifiable on this rig inside the timebox.

Note what the block does. Each numbered outcome names a *reading*, not just a number — so the run cannot come back and be argued about. The riders attach to any outcome and each would change what it means. The commitment is one line with a mechanism behind it: **the *because* is what gets graded, and being right is not.**

Freeze it at dispatch. Editing it after results is the most visible way to lose a reader's trust.

### Who writes the approach, and what the agent does with it

**The approach is the researcher's, in the researcher's words.** It is the part of the run that carries their judgement, so it is the part that has to be captured rather than composed. Take it down as dictated. Tidying the wording is fine; substituting your own framing for theirs is not, even when yours is tighter.

**Then critique it — that is the job, and it is not optional.** After the approach has been stated, say plainly whether you would have done something different:

- If a genuinely better approach is indicated, say so, say why, and say what it would cost. Do not soften it into a question.
- If the difference is in the noise and what was proposed is reasonable, **accept it and move on.** Manufacturing an objection to look thorough wastes the researcher's attention and teaches them to ignore the next one.
- If the approach is not well formed — a step missing, a control that would not rule out what it claims, a term used two ways — say that too. That is a correction, not a critique.

The order matters. Critique **after** the approach is stated, never during, or the approach on the page ends up being a negotiated compromise rather than a record of what the researcher actually thought.

**Where the researcher has already written structure into the page, extend it — never replace it.** That includes whitespace: if they wrote no blank line between a heading and its list, do not add one. A structure being edited is a structure being communicated.

**Write the choice in words, never as an index tuple.** `Chosen: 1 · 1 · 4 · 1 · 1` is compact and unreadable — nobody decodes five indices against five lists. Name what was chosen in a sentence or two, in the same order the questions appear.

### A potential-approaches block, worked

**A design is rarely one choice.** It is usually a technique choice plus several orthogonal ones — where the behaviour is measured, how deep the intervention goes, how much is removed, which positions are touched. Each of those is its own mutually-exclusive question and each deserves its own short list, because burying them as a flat row of dots is how a design decision gets defaulted instead of made.

Give every question a bold header and number its options. **Each option needs enough words to be understood by someone who was not in the conversation** — a bare *"Rank 1"* is a note to yourself, not a design.

Live example, from a rank-1 ablation of a truth direction in a 24-layer model:

**What we do to the direction**
1. **Ablation** — project the direction out of the residual stream and see whether the model still states the fact. Tests whether it is *needed*.
2. **Steering** — add α·v̂ at a range of strengths and see whether the answer moves with dose. Tests whether it has *influence*.
3. **Directed patching** — copy across only the v̂ component from another item, leaving everything else alone. Tests whether that one coordinate carries the fact.

**What behaviour we score**
1. **A full statement** — the exact position the direction was fitted at.
2. **A completion prompt** — the natural behavioural setting, one token before the direction was learned.

**How deep we intervene**
1. **One layer at a time, all of them** — gives a curve, but the model may rebuild the direction at the next layer, so a null is ambiguous.
2. **Only the two named depths** — cheap, but no curve and no room to be surprised.
3. **Every layer at once** — closes the rebuild escape; says nothing about where.
4. **Both 1 and 3.**

**How much of the direction we remove**
1. **Rank 1** — the probe direction alone: one line in activation space.
2. **Rank k** — the top k directions of its subspace. Matters because if the property is carried by a plane rather than a line, removing the line leaves it intact and the null is false.

**Chosen: 1 · 1 · 4 · 1.** Ablation first because necessity is the claim being made. The second choice is the one that decides whether the run means anything: score the prompt instead of the statement and a null is fully explained by the direction not transferring across positions — a fact about the setup, not about the model.

Three things to copy from this. **Options that are known-weak are still chosen and said so** — rank 1 is the setting most likely to manufacture a false null, and it goes in Threats rather than being quietly upgraded. **The choice that could invalidate everything gets its own paragraph** below the lists, not a clause inside one. And **do not list a straw option to look thorough** — "do nothing" is not a candidate approach, and putting it on the list only makes a reader wonder what they missed.

**The measurement must be independent of the manipulation.** Reading a probe after intervening on the direction that probe reads is circular, and the circularity does not show up in the numbers.

## Controls

Each control rules out a specific alternative explanation, and if you cannot name that alternative in one line, it is not a control.

**Random baselines are usually the weak version.** In a thousand dimensions a random vector is nearly orthogonal to everything, so beating it is close to free. The sharp control is a *different meaningful* quantity built by the identical pipeline — same construction, same norm, a property you are not claiming.

**The instrument check is separate and mandatory.** A manipulation that changed nothing and one that never fired produce identical numbers.

## Timebox

State the budget out loud when the run starts. When it is blown, say so and name the choice — extend, cut, or move on. A run that quietly keeps going is the failure this section exists to prevent.

## Threats

What would make the result meaningless **whichever way it comes out**. Confounds, and seams — a quantity derived in one setting and applied in another, a direction fitted at one token position and used at a different one. A threat named beforehand reads as judgement; the same threat named afterwards reads as an excuse.

## Result and Findings

**Result** is the headline and the one figure. **Findings** below is the full evidence. The duplication is deliberate: the top is what gets quoted, the bottom is what gets audited.

Lead each finding with the claim and follow with the number. A point estimate with no spread reads as not knowing what was measured.

## Verdict

Met or not met, against the answer criterion — not against whether the result was pleasing. Then say which numbered outcome came true and whether the expectation's reasoning survived even where its number did not.

**A negative result gets the full treatment** and says what it licenses: a fact surviving an intervention means redundancy, not irrelevance.

## Why the write-up is on top

A run is read far more often than it is executed, almost always by someone deciding whether to trust it. Leading with question, candidates, expectation and result means the first screen answers *what did this settle and how much should I believe it*. Everything below the rule is for auditing.
