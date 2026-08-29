# RULESET R-stone
include::
import:: skills/audit/scripts/audit-plan.py
where:: `file:{anchor}/**/* Rocks/**, {anchor}/**/* Pebbles/**, {anchor}/**/* Sleepers/**, {anchor}/**/* Book/**, !**/DAS *.md`
exclusion-note:: `!**/DAS *.md` exempts the facet-spec catalog (a `DAS <Name>.md` is the SPEC for the facet, not an instance; specs are governed by [[R-facet-spec]]). The vault-wide `LST/Rocks/` is **not** an instance — its folder is not `{slug} Rocks`, so the `* Rocks/` shape does not match it. **This glob is the one place a kind is named**: the checkers read every other per-kind fact from the kind table in [[DAS Stone]], so declaring a new kind means adding its folder shape to this line and nothing else. **And it is a step that has already been missed** — `sleeper` shipped as a kind and its `* Sleepers/` shape was never added here, so `SV Sleepers` went unaudited from the day it was created until 2026-08-28, when `book` was added and the gap was noticed beside it. Selecting a non-instance is harmless (`_stone_gate` passes it as *"not a Stone-facet instance"*, which is what keeps `Interviewing Book` and `LST/Rocks/` out of scope); **failing to select an instance is the silent half**, and it is the one to check when adding a kind.
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

**A kind may instead declare date-named members, and the shape is declared in the kind table rather than assumed.** The table's `stone file` row IS the member-naming declaration — `{slug} P0001` means numbered, `YYYY-MM-DD {Title}` means dated. There is no separate `member::` key, because a per-kind fact belongs in the table whose columns are the kinds; carrying it anywhere else would encode "which kind" twice in two notations. Ruled by Dan, 2026-08-28, for the book and traffic kinds, whose members are chronological registers whose readability is the point — renumbering `2026-08-10 Ode via Will Hsia` to `SONAR B0003` would destroy exactly what the list is for.

**A dated name's date is the CREATION date, and is never the ordering key.** Dan, 2026-08-28: *"the only viable date is really gonna be the creation date, and that's not really the date that it gets sorted by. The date that it gets sorted by is gonna be the date of something happening."* Ordering lives in the control file, which since the same day may be machine-generated from any key at all — so the sort key never has to appear in a filename, and a stone's name never has to change when what it waits on moves. This satisfies the rule's actual intent: a date-stamped title is unique, monotonic and non-recycling, which is all three things the numbering was protecting.

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

### RULE R-stone-07 — The group is linked from `{slug} Track.md` (checked)
check:: stone_dispatch_linked

`{slug} Track.md` carries a row linking the group — **either its control file** (`[[{slug} Pebble]]`, `[[{slug} Rock]]`) **or its folder** (`[[{slug} Pebbles]]`, `[[{slug} Rocks]]`, `[[{slug} Book]]`).

**Check pattern:** grep the anchor's Track dispatch page for a wiki-link to either target, accepting the pipe-escaped `[[X\|alias]]` form a dispatch cell uses, and a `#heading` or `/subpath` reference. Judged **once per group**, on the group's spokesfile — its first member — never once per member.

**Both targets count, and the control file is the one that usually does.** `R-rocks-08` named the folder alone, because that is what a rock group's Track page happens to link. Measured vault-wide 2026-08-28, every other kind links the **control file** instead — `[[TINK Pebble]]`, singular — which is the better target anyway, since the control file is what a reader opens and the folder is storage. Porting the folder-only predicate unchanged fired on **21 of 32 live groups**: a rule measuring a convention rather than a defect. Accepting either drops it to **6**, and all six are genuine — their Track pages mention neither.

**Why:** the group folder is elective, so nothing else guarantees it is reachable. An unlinked group is invisible twice over — to a person navigating the anchor, and to the catch-all of every page above it, since the catch-all deliberately omits any child the page already links and so has nothing to say about one nobody links at all.

**Ported from [[R-rocks]]-08 on 2026-08-28 ([[TINK Backlog#^T603|T603]]), and it had a live victim — [[SV]], which fires on all three of its groups.** `R-stone` generalised six of `R-rocks`' thirteen rules and stopped, leaving seven rock-only — so `sleeper`, `pebble` and `book` groups went unchecked on reachability. `SV Sleepers` was unreachable by navigation and nothing said so, **while the rocks half of the identical defect fired in the same sweep on the same anchor.** Two groups, one rule, one silence: that asymmetry is what makes this the first of the seven to port rather than the easiest.

Six remain rock-only and are the rest of [[TINK Backlog#^T603|T603]]: `R-rocks-03` (cardinality 0-or-1 per anchor, which [[DAS Stone]] states and no checker enforces for any kind), `R-rocks-05`/`-06` (every member on a control line; no control line pointing at a missing stone — an orphaned stone file is invisible in every kind today), and `R-rocks-09`…`-11`.

### RULE R-stone-08 — Every member is named in the control file (checked)
check:: stone_member_ranked

Every stone file in the group folder is the target of some wiki-link in the control file. Emitted as a **warning**, not an error.

**Check pattern:** collect member basenames; collect every wiki-link target in the control file; assert each member is among them. Judged **once per group**, on the spokesfile. Membership is read by **stem**, never through the number regex — so a dated member (`book`) is seen exactly as a numbered one is.

**Why:** a stone nobody has ranked is a real state and a transient one — the file lands first, the line follows — so this is cleanup pressure, not a gate. But it is the only pressure there is: a member the control file does not name is reachable from nothing a person reads. Until this port every non-rock kind had no such check at all, which is the data-loss shape rather than the navigation one.

**Ported from [[R-rocks]]-05 on 2026-08-28 ([[TINK Backlog#^T603|T603]] leg 2).** Measured across all 32 live groups first: zero unranked members, in every kind. So the evidence for this rule is its fixture — `test_stone_ranking_rules_fire_beside_a_clean_twin`, an unranked member beside a fully-ranked twin — and not the green sweep, which cannot distinguish a working rule from one that never ran.

### RULE R-stone-09 — No dead lines in the control file (checked)
check:: stone_control_links_resolve

Every control-file line ranking one of **this group's** stones — a line whose leading link begins `{slug} ` — resolves to a file that exists.

**Check pattern:** for each line opening with a wiki-link, take that leading link's target; skip a **header** (a target ending in a control-file word, R-stone-04) and skip a line naming **another anchor's** stone (which under [[DAS feed]] is what a propagated line is, and which no local resolver can see); otherwise assert `{target}.md` exists in the group folder or resolves nearby. Leading link only: a promotion marker, a feed annotation and plain commentary all carry links that point outside the anchor. Judged **once per group**, on the spokesfile.

**Why:** the control file is the surface people read and cite from; a link that goes nowhere makes it untrustworthy at exactly the moment someone is trying to act on it. R-rocks-06 records the vault-wide [[Rocks]] page carrying five such rows for months — and that rule judged nothing at all between the Stone migration and 2026-08-11, because it kept reading the folder-note after the ranking had moved. This port reads the control file only, since under [[DAS Stone]] that is where the ranking is and there is no migration to straddle.

**Ported from [[R-rocks]]-06 on 2026-08-28 ([[TINK Backlog#^T603|T603]] leg 2).** Measured first: zero dead lines across 32 live groups, `SONAR Book`'s eleven dated members included. Evidence is the paired fixture, same as R-stone-08.
