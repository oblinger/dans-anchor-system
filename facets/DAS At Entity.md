---
description: "the `@`-prefixed page for an entity you correspond with — identity line, LOG, and the two dated folders Drafted/ and Meet/"
group: file, folder
---

| -[[DAS At Entity]]- | → [[DAS]] → [[FCT]] → [DAS At Entity](hook://p/DAS%20At%20Entity)  |
| --- | --- |
| Related | [[DAS Log]],  [[DAS WP]],  [[DAS stream]],  [[DAS Folder]],  [[DAS file-association]],  [[DAS Template Files]],   |
| Examples | [[FEX At Entity\|worked instance — folder form, Drafted + Meet]],  [[@David Chee\|live instance — mail-shaped LOG]],   |
| Template | [[_@{{PERSON_NAME}} Template\|_@{{PERSON_NAME}} Template]] — the person form; copied on mint |
| Rules | [[R-at-entity]],  [[R-stream]],   |

# DAS At Entity
The `@`-prefixed page for an entity you correspond with — one identity line, an optional INFO block, a dated `# LOG`, and two dated folders: `Drafted/` for correspondence composed here and `Meet/` for synchronous meetings.

**TLDR** — An **at entity** is anything that can hold an opinion, make a decision, and be written to: a person, a company, or a standing group. Its page is `@{Name}.md`, promoted to `@{Name}/` holding a namesake `@{Name}.md` the moment it acquires attachments or either dated folder. Three containers, one test each: **did I draft something for them** → `Drafted/`; **was it a synchronous meeting** → `Meet/`; **everything else** → `# LOG`. `Drafted/` names *provenance*, not state, so a sent message stays there; the vault is never a mail archive, because the ground truth of what was sent is the mail account. **Cardinality: many per anchor.**

# What an at entity is
The `@` sigil marks an **entity** — something with agency, which is what separates it from a topic page. The test is whether the thing can *hold an opinion, make a decision, and be corresponded with*. Three kinds qualify:

- **A person** — the common case, and the one the [[_@{{PERSON_NAME}} Template|person template]] scaffolds.
- **An organization** — `@Anthropic`, `@Alta Vista`. Corporations decide and correspond, so they are entities in exactly the same sense.
- **A standing group** — a management team, a computer-vision team, a recurring committee. This is the deliberate stretch of the word, and it exists to give recurring meetings a home: a meeting has N attendees and cannot live in one attendee's page without arbitrarily electing one of them.

**The `@` is what makes it an entity, so a standing group carries it too.** A group folder named without the sigil is still being *used* as an entity — it hosts `Meet/`, it accumulates correspondence — while being invisible to every glob and every check that enumerates entities. That second, unmarked class is the cost, and it buys nothing. (Recorded as this spec's call, not Dan's: he left it open on 2026-08-20 — *"I didn't use the @ character with those… I could use the @ character, but I think I could also just use that Meet subfolder with an arbitrary folder that is serving as an entity in that sense."* Ratifying or overturning it is § Unsettled item 3.)

# Detection, cardinality, forms
**Detection** is the leading `@` on the file or folder name. **Cardinality is many per anchor** — 655 `@*.md` pages and 51 `@` folders live under `AT/`, `SV/` and `Topic/` as of 2026-08-20, which is the second reason this is a facet rather than a template: nothing ties an at entity to the [[AT]] folder any more, so a shape that lived in one folder's template could not reach the ones outside it.

**Two forms, and the promotion between them is one-way.**

- **Flat** — `@{Name}.md`. The starting form and still the overwhelming majority (~604 of 655).
- **Folder** — `@{Name}/` containing a namesake `@{Name}.md` plus whatever it has acquired: `Drafted/`, `Meet/`, attachments, sub-anchors. Per [[DAS file-association]] the namesake file keeps the folder's exact name, so every existing `[[@{Name}]]` link survives the promotion untouched.

**Promotion happens on first use, never in advance.** A `Drafted/` folder appears only for entities actually drafted to — on today's corpus that is order ten or twenty, not 655 — which is why the ~92%-flat ratio is not an argument against the folders. Nothing is pre-created.

# The routing rule — three containers, three tests
This is the load-bearing part of the facet, because it is paid on every new note. Apply in order; the first that matches wins.

- **Was something *drafted* here for this entity?** → `Drafted/`. A drafting session — the inbound message, the reasoning, the revisions, the final text — is **one document**, not N dated log entries.
- **Was it a *synchronous* exchange with this entity?** → `Meet/`. In person, phone, video; the channel is irrelevant.
- **Otherwise** → `# LOG`. The running state of the relationship.

The tests are mutually exclusive by construction: a drafted message is asynchronous and a meeting is not drafted. A meeting whose *preparation* was drafted still files under `Meet/` — see § Meet.

# Drafted
`@{Name}/Drafted/YYYY-MM-DD — {thread topic}.md`, one file per drafting **thread**. The document's internal format is [[AT Mail]] — four H3 blocks (draft, in-response-to, reasoning, previous versions) inside a dated H2, newest H2 on top. This spec places the file; `AT Mail` shapes its contents, and neither restates the other.

**The name is `Drafted`, not `Drafts`, and the difference is the whole point.** It names **provenance** — *this was composed here* — rather than **state**. A sent message therefore still belongs; under a state name every sent item would read as misfiled the moment it went out.

**The vault is not a mail archive.** The ground truth of what was actually sent is the mail account itself, and most correspondence never appears here at all. `Drafted/` holds *drafting sessions* — which is what scopes the folder, and what removes any obligation to be complete. A received message that was never drafted against does not belong in `Drafted/` merely because it is email.

**The date is the date the thread opened, and the file is never renamed as it grows.** A thread that runs for months keeps its original name; renaming would break every link into it, and the sort order it buys is not worth that. Where only the month or year is known, [[DAS stream]]'s coarser forms apply (`YYYY-MM — {topic}.md`).

**Both folders' documents carry a one-line orientation under the H1** — what the thread or meeting is and where it stands. It is what makes a folder of twenty files scannable without opening any of them, and it is what [[R-spine]]-02 asks of every document anyway.

## Merging — the answer to document bloat, and it is not settled
A heavily-corresponded entity accumulates many small documents, and the intended remedy is **merging the tail of the folder** into one larger document per period rather than pruning it. The proposal on the table, stated so it can be argued with:

A merged file is `YYYY — {Name} drafted.md`. Each **thread** becomes an H2, each **exchange** an H3, each of the four AT-Mail blocks an H4 — a uniform demote-by-one that a script can apply and reverse. The merge is append-only and runs on the tail (threads with no activity in the period), never on a live thread.

**This is a proposal, not a rule.** It is § Unsettled item 1, and Dan has said he will settle the format with [[SONAR|Sonar]] directly.

# Meet
`@{Name}/Meet/YYYY-MM-DD — {topic}.md`, one file per meeting.

**A meeting is a synchronous entity-to-entity event.** That is the whole boundary, and it is what makes this container crisp where a "notes" folder would not be. In person, phone call, video call — the channel does not matter. Everything attached to that event belongs to it: the **preparation** written beforehand, the **contemporaneous** notes, and the **after-notes** written up later all live in the one meeting document.

**File under the meeting's main entity.** A meeting with several people is filed under the one whose meeting it is — the person who called it, or the standing group that owns the recurrence. In practice this is answerable; when it genuinely is not, the meeting wants a standing-group entity of its own rather than an arbitrary election among attendees.

**Three time-slices, one document.** The suggested skeleton — `## Prepared — {date}`, `## Notes — during`, `## After — {date}` — keeps the three in the order they were written, which is the order that shows what the meeting *changed*. Reading a prep block that asked the wrong question against an after block that names the right one is most of the value; splitting them across files destroys it. The H2s are a suggestion; the one-document rule is not.

# What stays in LOG — most of it
`# LOG` is not a residue after the two folders are carved out; it remains the largest of the three. Measured across the 261 at entities carrying a `# LOG`, over 244 dated events (2026-08-20):

| Kind of event | Count | Share | Destination |
|---|---|---|---|
| Relationship / status note | 134 | 54% | stays in `# LOG` |
| Meeting or call | 56 | 22% | `Meet/` |
| Correspondence | 29 | 11% | `Drafted/` *(only the part actually drafted)* |
| Untitled | 17 | 6% | stays in `# LOG` |
| Intro / referral | 8 | 3% | stays in `# LOG` |

So roughly **60%+ of the existing corpus stays where it is** — *"maybe work for Sports Visio"*, *"asked me to join his fractional CFO pool"*, *"trying to cancel service"*, *"behavioral AI role"*. Those are the running state of a relationship, and they are the majority rather than the odds and ends. **Do not plan a migration that assumes LOG empties out.**

The corollary for the migration: the selection rule is *"was this a drafting session?"*, which is strictly narrower than *"is this about email."* A received denial, a forwarded reply, a note recording that a message arrived — none were drafted, so under a provenance name none of them move.

# Entry shape
The parts of the namesake page, top to bottom:

- **H1 identity line** — a self-link plus up to three more pieces on one line: the title (hyperlinked to a profile where one exists), the `@`-entry for the employing organization, and the rolodex group links. Spelled out in [[_@{{PERSON_NAME}} Template]].
- **`# INFO`** — optional; present only when there is data beyond the identity line (phone, email, address, handles). No table when there is nothing extra.
- **`# LOG`** — dated events, **newest first**. An ordinary event is `### YYYY-MM-DD  {title}`. An event that drafts a message is an **H2**, because it carries H3 blocks inside it — measured 2026-08-20, 159 plain H3 events against 85 mail-shaped H2s. Once `Drafted/` is in use, new drafting sessions go to the folder and this H2 form is what the migration retires.
- **`Drafted/`**, **`Meet/`** — folder form only, created on first use.


## The opening — breadcrumb, identity H1, card (2026-08-29)
Settled on [[@Henna Dattani]] with Dan, then applied to ten more entries the same day. A flat entity page opens with a **breadcrumb** (it is a leaf — no dispatch table, and never a `...`, which would enumerate the parent folder's children), then an **H1 that carries the identity line** — the base name, an em-dash, and the role linked to LinkedIn with the organization as its `@` link:

`# @Henna Dattani — **[Alignment TPM](https://linkedin…) at [[@Anthropic]]**`

Directly under it sits the **card**, the page's heart ([[DAS heart]] § Fact card). It is a two-column table headed `| Card |  |`; every row is a fact about *this* person. The rows, **in this order**:

| Row | Holds | Present when |
|---|---|---|
| **Contact** | the **channels to reach them** — email · [LinkedIn](…) · [X](…) · a **standing** meeting room, labelled (a personal Meet/Zoom code reused across calls; a one-off invite link is not contact). **Phone numbers live in macOS Contacts, not here** — they drift; write one only when the person has no contact card at all | **always**, even empty — an empty Contact is a to-do |
| **Personas** | **who they are elsewhere** — two kinds, mixed in one cell: their other `@` affiliations (ex-employers, boards, groups they belong to, each an `@` link), and their **presence pages**, each a bare-name link with a fixed label so a reader knows what to look for: **Website** (a personal site), **Wikipedia**, **DBLP**, **Scholar** (Google Scholar), **GitHub**, **OpenReview**, **ORCID**, and an employer profile page named for the employer (*MSR page*). A single paper or post is not a persona — it goes in **Known for** or the body. Their job title lives in the H1, not here | only when there is one |
| **Rolodex** | which of Dan's registers they belong in — [[BOD]], [[MENTORS]], [[FAANG]], [[ADVISORS]] … — each linked. Replaces the old `#mentor` / `#bod`-style tags; no `#pp` (every `@` person page is a person) | **always**, even empty — an empty Rolodex is a question: *should they be in one?* |
| **Friends** | the people they know that Dan also knows, each an `@` link | only when there is one |
| **Active** | **links only, one per activity** — to the activity's own page: an application under Sonar's [[Apply]] (aliased to the application's name, `[[ATI\|2026-04-14 Anthropic Alignment TPM]]`, never a bare slug), an engagement page, a stone. No prose, no funnel page — if the application page does not exist yet, that is the thing to create (with Sonar), not a reason to link something else. **Bidirectional by rule:** the activity page links the person, the person's card links the activity, because Dan reaches an activity *through* the person as often as the other way | only while something is active |
| **Historical** | the same links once the activity is over — the loop that ended, the engagement that closed. A link moves from Active to Historical; it is never deleted. Links only, as above | only when there is one |
| **Context** | how Dan knows this person and why they are in the list — the intro, the relationship, the standing arrangement. **Last, because it is the long one**: every row above is a bare fact and stays at the top | only when there is something to say |
| *then* | **Known for** (the work itself — papers, books, systems, each linked) · Trajectory · Education · Public work · Relatives · Notes … as known, in any order | as known |

**Live:** [[@Henna Dattani]] (the specimen), [[@Will Hsia]] and [[@Nick Allen]] (an **Active** application), [[@Carlos Jimenez]] and [[@Mojmir Stehlik]] (a **Historical** loop), [[@Rafah Hosn]] and [[@Praveen Paritosh]] (Rolodex-heavy mentors), [[@David Chee]] (a standing Meet room in Contact). **Made-up:** [[@Marguerite Vale]]. The `# LOG` follows the card as before; the one-liner slot under the H1 is not used — the H1 *is* the identity line.

**Who writes these.** [[SONAR]] mints entries for the people the job search touches; the personnel agent to come ([[WINNIE]]) owns the register as a whole and the pass that brings the ~650 existing entries into this shape. Both read this table, not Henna's page, for what goes in each row.

# Site-specific extensions
A vault may specialize this facet for its own user in that vault's agent-conventions page, in a section keyed to this facet's exact name. Nothing here assumes one exists; when it does, it refines this spec and never overrides a declared pointer. In this vault that page is [[Agent Conventions]], and the `@`-entry corpus lives under [[AT]] with the person shape in [[_@{{PERSON_NAME}} Template]] and the drafted-message shape in [[AT Mail]].

# Unsettled — what Dan and Sonar settle next
Recorded so the next agent does not mistake an open question for a ruling, and so the settling has a list:

1. **The merge format** (§ Merging) — the demote-by-one proposal above is unratified. Dan, 2026-08-20: *"I think I'll probably work with Sonar directly on that format."*
2. **Whether the person shape stays a template or becomes part of this facet.** Today [[_@{{PERSON_NAME}} Template]] holds the identity-line and LOG shape and this facet points at it. That split is deliberate for now and expected to collapse once [[STEN|Stencil]] can express both.
3. **Whether a standing group carries the `@` sigil.** § What an at entity is takes the position that it does; Dan left it open.
4. **Whether `Meet/` generalizes beyond at entities.** A project meeting with no single owning entity has nowhere to go under this facet.
5. **Folder-form entities collide with the spine rules, and the migration will multiply it.** Measured 2026-08-20: a flat `@{Name}.md` audits clean, but a folder-form namesake is treated as an **anchor entry page** and trips `R-spine-02` (no orientation line under the H1) and `R-spine-09` (no breadcrumb or dispatch identity row above it) — reproduced on the live [[@Avid Boustani]] and on [[FEX At Entity|the worked instance]]. The at-entity H1 *is* an identity line, which is the shape those rules are asking for and cannot recognise. Promoting ten or twenty entities to folder form turns one latent collision into twenty findings, so this wants deciding **before** the sweep, not during it: either the entity page adopts a spine, or `R-spine` learns that an `@` identity line is one.

# See also
- [[AT Mail]] — the format *inside* a `Drafted/` document; this facet places the file, `AT Mail` shapes it
- [[DAS Log]] — the anchor-level sibling; an at entity's `# LOG` is the same idea scoped to one entity
- [[DAS WP]] — the other dated-folder facet; WP holds polished documents, `Drafted/` holds messages
- [[DAS stream]] — owns the `YYYY-MM-DD — {topic}` entry-filename pattern both folders use
- [[DAS file-association]] — owns the namesake-file rule that makes flat→folder promotion link-safe

# BRIEF

*(Maintainer note — cautions for whoever edits this facet spec. The normative spec is the body above; the ruleset is [[R-at-entity]]; the worked instance is [[FEX At Entity]].)*

- **This ruleset is deliberately NOT armed.** [[R-at-entity]] is not named in [[R-anchor]]'s `include::`, so it enters no plan and fires on nothing. That is intentional while §Unsettled is open — arming it would hand a 655-page corpus a wall of findings for a shape its owner has not ratified. **It also means a green audit says nothing about at-entity conformance**, which is the [[DAS Facet]] § vacuous-zero failure exactly. When the shape settles, arm it by naming it in `R-anchor`, and *measure the blast radius in the same pass* rather than after.
- **The message format is not this facet's to state.** [[AT Mail]] carries it as prose, under a standing instruction not to hand-write a ruleset for it because [[STEN|Stencil]] is meant to own the generate-and-check pair. `R-at-entity` therefore covers **placement and structure only** — where an entity lives, when it promotes to folder form, which container an entry belongs in — and never the four blocks. Keep that line; crossing it recreates the two-copies drift both documents exist to avoid.
- **The migration is Sonar's, not this spec's.** Converting the live corpus is tracked as a [[SONAR|Sonar]] pebble. Do not sweep at entities from here; a spec change lands here, the corpus moves there.
- **Don't relax the routing rule into a preference.** § The routing rule is three exclusive tests in order, and it is the only thing standing between three containers and three-way ambiguity on every new note. If a case genuinely does not fit, that is evidence about the containers, not license for a fourth "it depends."
