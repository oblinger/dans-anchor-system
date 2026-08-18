# RULESET R-stone
include::
import:: skills/audit/scripts/audit-plan.py
where:: `file:{anchor}/**/* Rocks/**, {anchor}/**/* Pebbles/**, !**/DAS *.md`
exclusion-note:: `!**/DAS *.md` exempts the facet-spec catalog (a `DAS <Name>.md` is the SPEC for the facet, not an instance; specs are governed by [[R-facet-spec]]). The vault-wide `LST/Rocks/` is **not** an instance — its folder is not `{slug} Rocks`, so the `* Rocks/` shape does not match it. **This glob is the one place a kind is named**: the checkers read every other per-kind fact from `DAS Stone Kinds.json`, so declaring a third kind means adding its folder shape to this line and nothing else.
description:: Structural rules for a stone group — folder location and naming, the control file, the header-by-link-target rule, stone numbering, and the key block's position.

Ruleset for the Stone facet — spec: [[DAS Stone]]. Adopted 2026-08-11 via **[[R-anchor]]'s `include::`** — the umbrella `/audit anchor` actually resolves, and the one that made these rules run. ([[R-facet]] names it too, for catalog completeness; that umbrella is outside the `R-doc`/`R-anchor` closure, so an include there arms nothing on its own.) Generalises [[R-rocks]] across kinds: where that ruleset governs `* Rocks/` alone, these rules govern any configured kind, and the four checked ones were verified by a malformed fixture rather than by the clean corpus.

**Overlap with [[R-rocks]] is real and deliberate for now.** `R-stone-01` subsumes `R-rocks-01` (folder name) and `R-rocks-02` (under Track) for the rock kind, so a malformed rock group would draw a finding from each. No live group is malformed, so the duplication currently costs nothing; consolidating means retiring two `R-rocks` rules, which touches the tier annotations that have already folded a checker onto the wrong rule twice in this exact ruleset. It is filed as its own step rather than done in passing.

### RULE R-stone-01 — The group lives at `{slug} Track/{slug} {Kind}s/`, control file beside it (checked)
check:: stone_group_located

A stone group is a folder under the anchor's Track facet, named by its kind's `folder` template for the owning anchor's slug, with that kind's **control file** beside it in the same Track folder. Not under Design, not at the anchor root.

**Check pattern:** the folder's basename equals `folder.format(slug=…)`; its parent is `{slug} Track`; the file `{slug} {ControlWord}.md` exists in that parent.

**An anchor page is not required, and this rule used to say it was.** The clause was inherited from `R-rocks-01`, which does mandate a `{slug} Rocks.md` folder-note. Corrected 2026-08-11 against the mechanism rather than against taste: `cmd_new` in `stone` creates the group folder with `mkdir` and writes exactly two things, the stone file and the control file — it has never minted an anchor page or a `.anchor`. The corpus agrees and splits cleanly by provenance: all four **rock** groups carry a page (they predate the facet and inherit the Rocks shape), and all four **pebble** groups, every one of them minted by `stone`, carry none. Enforcing the clause would have declared four conformant groups defective on the strength of a copied sentence.

### RULE R-stone-02 — One file per stone, numbered and never recycled (checked)
check:: stone_members_numbered

`{slug} {PREFIX}{NNNN}`, monotonic forever. A recycled number silently re-points stale cross-anchor references, and a copied control line is indistinguishable from a fresh one, so nothing could detect it.

**Check pattern:** every `*.md` directly in the group folder, other than the group's own anchor page, has a stem matching `^{slug} {PREFIX}\d{digits}$`. The match is exact and never a `{slug} {PREFIX}*` glob — for the rock kind the prefix is `R`, so that glob matches `HBR Rocks.md` inside `HBR Rocks/` for every rock group that exists.

**Only half of this rule is checkable, and the checker says so in its own finding.** Non-recycling is a claim about history; a snapshot of a directory cannot evidence it. What a file can evidence is the shape, and the shape is what makes the history claim enforceable by the mint.

### RULE R-stone-03 — The prefix is not derived from the kind's name (stated)
Renaming a kind must not rename its stones. The prefix is an opaque identifier whose only job is uniqueness within the anchor; deriving it from the kind makes a rename touch every stone file and every control line that references one, including copies already propagated into other anchors.

### RULE R-stone-04 — A header is identified by its link target (checked)
check:: stone_header_by_target

A line is a header when its **first** link targets a control file — never by how it renders. The first-link restriction keeps a stone whose `line::` mentions a control file from being read as one.

**Check pattern:** over the control file, classify each line by its first link's target — a `… {ControlWord}` target is a header, a `{slug} {PREFIX}{NNNN}` target is a stone, anything else is neither — then assert the link's *display* agrees, in both directions. A header line renders per the kind's `header_line` template (`-[[X Pebble|X]]-`, dashes OUTSIDE the link); a line wearing that wrap without targeting a control file fails, and so does a line that targets one but renders as something else; the same pair for `{slug}:` and stones. (History: the dashes originally sat INSIDE the display (`[[X Pebble|-X-]]`) because a bare `-[[X Pebble|X]]-` line was HookAnchor's electric identity-row grammar — the first 2026-08-17 attempt to move them outside got every control file's list wiped by ELECTRIC rebuilds. Later that day HookAnchor f180d008c retired the bare dash form — the bare initiator is now `= = [[Name]] = =` and the dash form matches only as a table row's first cell — so the dashes-outside form is the standard.) Lines with no leading link (a tier label like `UNCOMMITTED`, or prose) are neither, by design, and are not judged.

**Why the check is about agreement rather than about rendering.** The mechanism resolves identity from the target and would be unaffected by a mismatched display. The reader would not: a control file is *scanned*, not resolved, so a line that looks like a header while pointing at a stone misleads exactly the audience the hand-arranged ordering exists for. The rule protects the human half of a mechanism that is already safe.

### RULE R-stone-05 — Control-file names are reserved against stone names (stated)
The mint refuses any stone whose filename would equal a control file's. `{slug} {1–2 letters}` is not an empty namespace, so without this the scheme can silently overwrite a stone.

### RULE R-stone-06 — Keys sit at the top, above the prose (checked)
check:: stone_keys_above_prose

`key:: value` lines precede the body. See [[DAS Stone Keys]] for the vocabulary and for why frontmatter was rejected.

**Check pattern:** in each stone file, walk from the first line after any frontmatter block and record where the body begins — the first non-blank line that is not a `key:: value`. A key line below that point fails, naming both line numbers. Frontmatter is skipped rather than counted as prose: [[DAS Stone Keys]] rejects frontmatter as the key vehicle, which is a different rule's business, and conflating the two here would report the wrong defect.
