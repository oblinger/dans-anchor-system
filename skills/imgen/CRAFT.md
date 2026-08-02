# imgen craft — what the models actually do

Companion to [SKILL.md](SKILL.md). That file is mechanical: verbs, flags, where output lands. **This one is earned experience** — the things a generative image model reliably gets wrong, and what actually moves it.

Everything here was paid for in real rolls. Each entry names the failure, the fix, and the roll it came from, so a claim can be checked rather than taken on faith.

## The one rule under all the others

**The model renders nouns, not prohibitions.** Every finding below is a special case of this. *"No smile at all"* leaves the smile untouched; *"the mouth closed in a flat straight line, corners level"* removes it. *"A few strands of grey"* is ignored; *"hollows under the cheekbones, deep creases from nose to mouth"* ages a face. *"Not overweight"* renders a belly; *"a waist clearly narrower than the shoulders"* does not.

When a prompt fails, the first question is not *how do I say it more firmly* — it is **what is the thing I want, described as a thing that is there.**

## Faces

**A text prompt does not control face, age, or affect.** One batch off a single prompt routinely spans ~30 years of apparent age and the full range from near-tears to drill-sergeant. The keeper is a lucky draw, not a specification. Two consequences: shoot **6+ per batch** when a face matters, and once a face is chosen, **never try to reproduce it by prompting** — start from the keeper and `edit` / `inpaint`, which hold identity. *(IMGEN005 Vector; IMGEN006 Batch 1 gave three distinct women off one wording.)*

**Age undershoots badly, and worst on women.** Asking for "mid forties" lands at late thirties. **Ask for a decade older than you want** and let it undershoot into range. Structural cues carry it — crow's feet, jawline, nasolabial creases, hollows.

**Expression is the least reliable thing in the frame.** It varies more between variants of one prompt than any other attribute, and it is what most often decides a portrait. Budget shots for it.

## Composition

**A gesture must agree with the gaze.** Pointing at something while looking at the camera reads as staged no matter how well it renders — nobody points at what they are not looking at. Either the eyes follow the hand, or there is no hand. *(IMGEN006 Batch 2: six competent images, all subtly wrong for this one reason.)*

**A secondary element loses to a dominant one** unless it is named **early** in the prompt and given a size word. A corkboard listed after a wall of monitors renders as almost nothing; the same board named first and called *large* fills a third of the frame. *(IMGEN006 Batches 1→2.)*

**A dark scene comes out too dark to read.** Atmosphere words ("late at night", "lit by screens") are enough on their own; the face additionally needs to be called **well exposed and clearly readable**, or every variant is silhouette.

**Rendered text is always noise.** Screens, signage, documents and handwriting come back text-shaped and meaningless. Compose so that *density* rather than legibility carries the meaning, and never spend rolls trying to fix it.

**Poses default to symmetric and centered.** Left to itself the model squares the subject to camera and plants them dead-center. Asymmetry has to be asked for by name — *turned three-quarters, one shoulder forward, weight shifting* — and even then it lands in maybe one variant of six.

**Some poses do not render at all.** *"Mid handoff"* reliably comes back as *"holding a box"*: arms stay tucked against the body however clearly the extension is described. When a pose keeps collapsing to its static neighbour, stop paying for variants and change the staging. *(IMGEN007, both batches.)*

## Style

**A style transfer imports the style's own priors, and words do not override them.** Converting a photo to anime resets age to young and affect to pleasant no matter how the prompt argues — the source face plus the style prior outvote the description every time. Pushing from "mid fifties" to "in her sixties" across two batches moved almost nothing; roughly one variant in six breaks through, so it is a lottery rather than a wall. *(IMGEN006 Batches 4–6.)*

**The subject can fight the style, and usually wins.** A large muscular man drags the render toward heavy-outlined Western comic art; asking explicitly for thin-line anime barely moves it. Style words are weak whenever the subject has a strong stylistic association of its own. *(IMGEN007.)*

When a restyled age, expression or look actually matters: **mask the face and `inpaint` it** — fill redraws what is inside the mask instead of politely declining — or generate fresh in the target style rather than converting into it.

## Editing an image you already have

**`edit` (Kontext) is strong on scene, weak on anatomy.** It weights identity preservation heavily and will quietly decline to alter a face. Two rounds on one nose produced no usable change; that is the signal to switch to `inpaint`. *(IMGEN002.)*

**A big mask is the tool for re-posing.** To move a limb, mask it **entirely** — fingertip to shoulder — plus wherever it is going, and keep the face outside. Everything inside is regenerated, so props and screens caught in the mask will differ between variants; keep out of the mask whatever must survive. *(IMGEN006 Batch 3 moved both arms onto a keyboard in one pass, six variants, every one the same woman.)*

**The mask bounds what is achievable, and no wording escapes it.** Asking for a change that would need pixels outside the mask fails however it is phrased. *"Make it pinch"* failed repeatedly because the thumb tip would have to leave the circle; *"bring the knuckle in"* worked, because it asked for a change within the allowed region. **When an instruction keeps failing, check the geometry before rewriting the sentence.** *(IMGEN002 Batches 17–21.)*

**When two passes miss in opposite directions, blend instead of re-rolling.** An inpaint result is a composite of its source, so the two are pixel-identical outside the mask — compositing between them through the same mask moves *only* that region, along exactly the axis that was overshot. Free, deterministic, dial-able, and it beats paying for another guess. *(IMGEN002 Batch 15.)*

## Reviewing

**Show one sheet, not N windows.** A batch is judged by comparison, and separate `open` calls give overlapping windows in arbitrary order. Every multi-image run writes a labelled contact sheet; open that.

**Never describe an image the user has not been seen.** Look at what was actually produced before saying anything about it.

**Calibrate against the person, not the picture.** The user's read on faces is finer-grained than the agent's, and reporting confidently in either direction — "these came out great", "these all have problems" — has been wrong about equally often. State what is observably there, name the defects that are mechanical (a hand, a duplicated limb, an exposure), and let taste be theirs.
