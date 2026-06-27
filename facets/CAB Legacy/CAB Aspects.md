---
description: "Aspects, Traits, and Facets — the unified anchor-property model"
---

# CAB Aspects

The unified anchor-property model: an Aspect is any named property an anchor carries, split into broad **Traits** (declared paradigms) and narrow **Facets** (file-based features), each carrying Constraints and Expected Usage.

## At a glance

An **Aspect** is any named property an anchor carries. Aspects come in two sub-categories, distinguished by *what they describe*:

- **Trait** — a **broad paradigm / intended usage** of the anchor, independent of any specific file or folder. Declared explicitly in the anchor's `traits:` list. Examples: `Code` (this is a code project), `Publishable` (this anchor is intended for the public website), `Skill` (this anchor is a Claude skill).
- **Facet** — a **narrow, specific aspect** of the anchor, almost always tied to one or more files. Defined by its spec under `CAB/CAB Facets/<Name>.md`; detection is whatever the spec says (usually file-existence). Examples: `Backlog` (a `<NAME> Backlog.md` file), `Architecture`, `Website Subfolder` (the specific folder to deploy).

Use **"Aspect"** only when discussing the umbrella; default to **"Trait"** or **"Facet"** when the specific sub-category is known. (User framing 2026-05-25: *"a facet is really just an aspect of an anchor."*)

```
       Aspect (umbrella)
       ├── Trait   ← broad paradigm; declared in `traits:`
       └── Facet   ← narrow file-based aspect; spec-defined detection
```

Both Traits and Facets carry **Constraints** (rules about legal usage — including mutual exclusion) and **Expected Usage** (positive guidelines for typical use). Both sections are part of every Aspect's spec.

---

## Trait — broad paradigm; intended usage

A **Trait** declares a *paradigm* the author intends for the anchor — a way of using it, independent of any specific files or formats. "This is a code project." "This anchor publishes to the web." "This is a Claude skill." Traits live in the anchor's `.anchor` `traits:` list because the author's intent is what defines them; the system doesn't infer paradigms from files.

- **Where declared.** `traits: [Code, Publishable]` in the anchor's `.anchor` frontmatter. The anchor page's dispatch table may render the Traits row for human readability, but the `.anchor` field is canonical.
- **Detection.** Read `traits:`. Done — no file walks, no inference.
- **Cardinality.** Inherently many — one anchor can carry multiple Traits (e.g., `Code + Skill`), subject to per-Trait Constraints (see below).
- **Spec doc.** `ob-skills/traits/<Trait Name>.md`, with required sections covering: (a) what paradigm this Trait names, (b) what shape the anchor takes when it carries this Trait, (c) **Constraints**, (d) **Expected Usage**, (e) which skills/audits attach.
- **Examples (current set, F090-pending expansion):** identity traits `Code`, `Topic`, `Skill`, `Paper`, `Simple`; capability trait `Track` (drive-loop / backlog lifecycle — see [[Track]]). New Traits anticipated: `Publishable`.

**Why Traits are declared (not detected).** A Trait is *what the author intends the anchor to be*, not what the files happen to look like. Implicit detection would let the system disagree with the author's intent; the explicit `traits:` field eliminates that. Two anchors with identical file shapes can carry different Traits because the author meant different things.

---

## Facet — narrow aspect; usually file-based

A **Facet** describes a *specific structural feature* of the anchor — almost always tied to one or more files. "This anchor has a Backlog (`<NAME> Backlog.md`)." "This anchor has an Architecture folder." "This anchor has a website subfolder for GitHub deployment."

- **Spec doc.** `CAB/CAB Facets/<Facet Name>.md`. The spec is authoritative for **six** things (the four mechanics + Constraints + Expected Usage):
  1. **Detection mechanism** — how the system decides whether this Facet is present on an anchor. Default: file-existence (most Facets work this way). Override: anything else (e.g., a `Composability` Facet might check capability requirements rather than files).
  2. **Cardinality** — `one` (one Backlog per anchor) or `many` (many Feature docs per anchor); the spec declares.
  3. **Format constraints** — filename pattern, frontmatter shape, body section requirements, naming rules.
  4. **Behavior** — which skills and audits act on this Facet.
  5. **Constraints** — rules about legal usage (see § Constraints below).
  6. **Expected Usage** — positive guidelines for typical use (see § Expected Usage below).
- **Examples (current set, ~30):** Backlog, Architecture, Interface, Rules, Module Doc, PRD, Roadmap, Triage, Questions, Features.

**Why most Facets are file-detected (but the spec wins).** A narrow structural feature usually leaves a file or folder fingerprint — the easy detection rule is "look for the file." The spec defaults to that. Exceptions exist (file-less Facets like Composability), and the spec mechanism is general enough to handle them.

---

## Constraints (every Aspect spec)

A **Constraint** is a rule about *legal usage* — what's forbidden, what's required, what's mutually exclusive. Both Trait specs and Facet specs include a Constraints section.

> [!important] Governing principle — compose by default; exclude only on *logical* incompatibility
> Traits are **freely mixable by default.** A mutual-exclusion constraint is declared **only when two traits are logically incompatible** — i.e. they make contradictory claims about the *same underlying thing*. The clean examples: the git-aspect traits `Commit` / `Push` / `PR` / `NoGit` are all answers to one question (how this anchor's git boundary is handled), so at most one can hold; the cadence traits `Drive` / `Lean` likewise. The identity traits (`Code` / `Topic` / `Paper` / `Simple`) exclude because they make contradictory structural claims (repo vs no-repo, docs vs no-docs). **Absent such a logical conflict, a trait composes with everything** — do not add exclusions for tidiness or "it'd be weird." Weird-but-coherent combinations are allowed; only contradictions are forbidden. (Per user direction 2026-06-11; e.g. [[Collection]] composes with any identity trait because nothing about enumerating members contradicts being Code / Topic / Skill.)

Common Constraint shapes:

- **Mutual exclusion: at most one.** *"At most one of {`Code`, `Topic`, `Paper`, `Simple`} per anchor."* — the anchor's "what is this thing" Trait is single-valued.
- **Mutual exclusion: exactly one.** *"Exactly one Backlog per anchor."* — cardinality `one` enforced.
- **Co-requirement.** *"The `Publishable` Trait requires the `Website Subfolder` Facet."* — declaring one mandates the other.
- **Exclusion.** *"The `Simple` Trait excludes all other Traits."* — simple anchors don't compose.
- **Format invariant.** *"The Backlog Facet requires source-order preservation."* — operational rule on the Facet's content.

Constraints are *enforceable* — audits read them and validate. (`/audit aspects` is the proposed home; tracks under F090's Phase 6.)

## Expected Usage (every Aspect spec)

An **Expected Usage** guideline is *what's recommended* — typical patterns, common compositions, ergonomics — without being a hard rule. Both Trait specs and Facet specs include an Expected Usage section.

Common Expected-Usage shapes:

- **Common combinations.** *"`Code` is commonly combined with `Skill` for runtime skill anchors."*
- **Typical scale.** *"Most anchors with the `Backlog` Facet have between 5 and 50 active rows."*
- **Naming conventions.** *"Feature docs typically use `F<NNN> — <Title>.md`; deviations have surfaced in audits."*
- **Skill pairings.** *"The `Architecture` Facet is typically populated by `/architect`; manual edits are valid but discouraged."*

Expected Usage is *guidance*, not enforcement. Audits may surface deviations as warnings (not errors) but don't block.

---

## Trait vs Facet — sharper distinction

Both are Aspects, but they describe different things:

| | Trait | Facet |
|---|---|---|
| **What it describes** | Broad paradigm / intended usage of the anchor | Narrow specific aspect, usually tied to file(s) |
| **Spec lives** | `ob-skills/traits/<Name>.md` | `CAB/CAB Facets/<Name>.md` |
| **How presence is determined** | Read the `traits:` list (one rule) | Whatever the Facet's spec says (usually file-existence) |
| **Author intent vs system inference** | Author-declared intent | System-detected feature |
| **Typical examples** | `Code`, `Skill`, `Publishable`, `Paper` | `Backlog`, `Architecture`, `Interface`, `Website Subfolder` |
| **Constraints + Expected Usage sections** | Required | Required |

**The clarifying example pair (user 2026-05-25):**
- *"This anchor is a Code anchor"* → Trait. Not tied to a specific file; declares a paradigm (this is a code project).
- *"This anchor has a website subfolder to deploy to GitHub"* → Facet. Narrow, file-based (the specific folder).
- *"This anchor is Publishable"* → Trait. Intent: "publish to the web." May co-require certain Facets (the website subfolder) by Constraint.

---

## Spec-doc structure (Trait and Facet, same shape)

Every Aspect spec doc — Trait or Facet — has the same shape:

- **Frontmatter** — YAML with a one-line `description:`.
- **`# <Aspect Name>`** — the H1, the Aspect's name.
- **`## What it is`** — paragraph naming what paradigm (Trait) or narrow aspect (Facet) this names.
- **`## How it's detected`** — for a Trait, "name appears in the anchor's `traits:` list"; for a Facet, the detection mechanism owned by this spec (usually file-existence; can be other).
- **`## Format`** — for Facets, filename patterns, frontmatter shape, body requirements; for Traits, structural expectations on the anchor as a whole.
- **`## Constraints`** — mutual exclusion, co-requirements, exclusions, format invariants (see § Constraints above for shapes).
- **`## Expected Usage`** — common combinations, typical scales, naming conventions, skill pairings (see § Expected Usage above for shapes).
- **`## Triggers`** — optional; only when the Aspect declares behavioral triggers. Holds `### compact` (terse prose the agent reads at POST-COMPACT when this Aspect is active on the cwd anchor) and `### markdown-write` (terse prose the agent reads when a `.md` file is modified in the cwd anchor's tree).
- **`## Skills and audits that attach`** — the skills and audits bound to this Aspect.

When a new Trait or Facet is added, its spec doc must fill all six required sections (What / How detected / Format / Constraints / Expected Usage / Skills and audits). The `## Triggers` section is optional — present only when the Aspect declares behavioral triggers.

## Triggers (F091 discipline)

An **Aspect can declare behavioral triggers** — events that, when they fire on an anchor carrying this Aspect, cause the agent to surface or apply specific behavior. See [[F091 — Trigger discipline]] for the full design. The shape in brief:

- **`## Triggers` H2 in the body — sole declaration site.** Per F091 Q1 revision 2026-06-06: triggers are declared **only** in the body, with H3 sub-sections per trigger type (`### compact`, `### markdown-write`). Each H3 contains the prose the agent reads at trigger time. No frontmatter `triggers:` list. Rationale: every trigger needs natural-text behavior content (the H3 body), so the body H2 is mandatory regardless; a frontmatter list would duplicate the H3 names without enabling any consumer the body grep can't enable. Less tooling, less duplication, single source of truth.
- **v1 trigger types:** `compact` (fires at POST-COMPACT reload), `markdown-write` (fires when a `.md` file is modified — wiring deferred to v2; the v1 ship is the declaration discipline).
- **Resolution mechanism:** anchor-resident, lazy lookup. Each trigger event reads the cwd anchor's `.anchor` `traits:` list, walks those Trait specs, and looks for the relevant `## Triggers § <type>` H3 in the body. If present, that Aspect declares that trigger; the H3 body IS the behavior. No central registry; no install step.
- **Composition:** when multiple declared Aspects share a trigger type, their `## Triggers § <type>` text concatenates in declared-traits-list order. Each Aspect keeps its trigger prose terse.

Existing examples: [[Commit]], [[Push]], [[PR]], [[NoGit]] all declare a `compact` trigger that surfaces their Git-aspect rules into OPERATING_CONSTANTS at POST-COMPACT.

---

## Asymmetry — Traits vs Facets, one sentence

When code or prose asks *"does this anchor have Aspect X?"*: if X is a **Trait**, the answer is a one-line lookup in `traits:`; if X is a **Facet**, the answer is whatever X's spec evaluates to (a file-existence check by default, something else if the spec overrides).

---

## Anti-patterns to avoid

- **Calling a narrow file-based aspect a Trait.** If it's about a specific file or folder, it's a Facet. Traits describe paradigms.
- **Calling a broad paradigm a Facet.** "This is a Code anchor" isn't a Facet; it's an intent declaration → Trait.
- **Hard-coding file-existence as the detection rule for all Facets.** The Facet spec is authoritative; bypass at your peril.
- **Saying "Trait" when you mean "any Aspect."** Use "Aspect" for the umbrella; "Trait" specifically for the declared-paradigm kind.
- **Declaring a Trait in the anchor doc body instead of in `.anchor`.** The `.anchor` field is canonical.
- **Omitting Constraints or Expected Usage from a new Trait/Facet spec.** Both sections are required — they're how the system knows what's enforceable and what's recommended.

---

## Composability matrix — Trait × Trait

The matrix below names the legal compositions of declared Traits. Per-spec Constraints (per § Constraints above) handle cardinality and format invariants; this central matrix handles Trait-vs-Trait composability so readers don't have to walk every Trait spec to learn the legal combinations.

|  | Simple | Topic | Code | Paper | Skill | Track | Commit | Push | PR | NoGit | Drive | Lean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Simple** | — | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ |
| **Topic** | ✗ | — | ✗ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ |
| **Code** | ✗ | ✗ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| **Paper** | ✗ | ✓ | ✓ | — | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Skill** | ✗ | ✗ | ✓ | ✗ | — | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| **Track** | ✗ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Commit** | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | — | ✗ | ✗ | ✗ | ✓ | ✓ |
| **Push** | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ | — | ✗ | ✗ | ✓ | ✓ |
| **PR** | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | — | ✗ | ✓ | ✓ |
| **NoGit** | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | — | ✓ | ✓ |
| **Drive** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✗ |
| **Lean** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | — |

**Legend:** ✓ = legal composition; ✗ = illegal (audits flag); — = same Trait (composition with self is meaningless).

**Reading guide:**
- **Simple** is exclusive — a Simple anchor carries only the Simple Trait. It's the "just a folder with a marker, nothing else" shape. (Simple + NoGit is the trivial exception — most Simple anchors are non-git by nature.)
- **Topic + Paper** are compatible — a research-area anchor (Topic) can co-carry the Paper Trait if it's authored as iteratively-revised content.
- **Code + Skill** is the common skill-anchor combination — a runtime Claude skill IS a code project; both apply.
- **Code + Paper** is legal — a research artifact can include code.
- **Topic excludes Code, Skill** — Topics are evergreen knowledge, not repo-backed projects.
- **Skill excludes Topic, Paper** — Skills are runtime, not knowledge content.
- **Track** is a *capability* trait (not an identity), so it layers onto any identity trait **except Simple** — `Code + Track` (tracked code project), `Skill + Track` (e.g. [[SKA]]), `Paper + Track`, `Topic + Track`, or `Track` alone (a non-code ops/wiring effort with a backlog). It co-requires the Backlog facet. See [[Track]].
- **Git-aspect traits (Commit / Push / PR / NoGit) are mutually exclusive** — exactly one per anchor (per F077 v2 design). The four together exhaust the Git-aspect dimension, escalating: **Commit** (commits, never pushes, never asks) → **Push** (commits AND pushes, never asks) → **PR** (commits on branch + review-gated PRs) → and **NoGit** (no repo at all). See [[Commit]] / [[Push]] / [[PR]] / [[NoGit]].
- **Commit, Push, and PR require Code** — they shape how a repo is managed; an anchor without a repo can't take any of them. `Commit + Code` (default for SKA, kmr-internal code), `Push + Code` (continuously-published branch, e.g. [[HA]]), `PR + Code` (production code with PR-gated git).
- **NoGit excludes Code (and Skill)** — declaring "no repo" on an anchor that HAS a repo is a contradiction. `NoGit + Topic` (knowledge area without per-anchor git), `NoGit + Simple` (minimal folder marker), `NoGit + Paper` (writing project versioned by the document not git).
- **All three Git-aspect traits compose with Track** — whether an anchor is `Tracked` (has a backlog + drive loop) is orthogonal to its git posture.
- **Cadence traits (Drive / Lean) are mutually exclusive** — exactly one per anchor at a time. **Drive is the default** — anchors that don't declare either run in Drive. `Lean` is the cautious / fortify-the-foundation posture; per-turn invocation uses `/fortify`, declarative per-anchor activation uses `Lean` in `traits:`.
- **Cadence traits compose with everything else** — they're orthogonal to identity, capability, and Git-aspect. `Drive + Code + Track + Commit` (the canonical "code project with backlog and standard everything"); `Lean + Code + Track + PR` ("production code being fortified").

New Traits introduced later (e.g., `Publishable`) extend the matrix with new rows + columns. The Trait spec doc declares its compatibilities; this matrix is the rendered view. Audits read either source.

The matrix is **enforceable** — `/audit aspects` (proposed; tracks under F090 Phase 6) walks every anchor, checks the declared `traits:` list against this matrix, and surfaces violations as backlog rows.

## Migration history

The Aspect / Trait / Facet model lands as part of [[F090 — Retire CAB Types, unify under Traits, Facets-as-Traits-by-file-existence]]. Pre-F090, CAB had three terms — Types, Traits (near-synonym for Types), Facets — with overlapping semantics. F090:

- **Retires** "Type" terminology entirely.
- **Keeps** "Trait" and "Facet" as sibling sub-categories, with sharpened semantics (broad paradigm vs narrow file-based aspect).
- **Introduces** "Aspect" as the umbrella.
- **Mandates** Constraints + Expected Usage sections on every Trait and Facet spec.
- **Ships** the central composability matrix above (per F090 Q3 = (A)).

# BRIEF

- **This is the umbrella spec for the Aspect / Trait / Facet vocabulary** — the authoritative definition of what those three words mean, how they relate, and what every Trait/Facet spec must contain. Per-Trait and per-Facet specs live under `ob-skills/traits/<Name>.md` and `CAB/CAB Facets/<Name>.md`; this file is the model they all conform to.
- **Do NOT inline per-Trait or per-Facet content here.** "What the Code trait means," "what the Backlog facet requires" — those belong in their own spec files. This page only carries the shared model (the six required sections, the Trait-vs-Facet distinction, the composability matrix).
- **The inclusion test for content here:** does it apply to *every* Trait spec and *every* Facet spec equally? If yes (e.g., "every spec needs Constraints + Expected Usage"), it belongs here. If it's about one specific Aspect, it belongs in that Aspect's spec.
- **The composability matrix is the single source of truth for legal Trait-vs-Trait combinations.** When a new Trait ships, add a row + column here AND mirror in the Trait's spec. Do not let the matrix drift from per-spec declarations — audits read both and flag divergence.
- **Load-bearing for /audit aspects (F090 Phase 6).** The six required sections (What / Detection / Format / Constraints / Expected Usage / Skills) and the matrix are what the audit walks. Renaming sections or dropping required content breaks the audit; coordinate with F090 before restructuring.
- **The Triggers section is F091's home in this spec.** When the trigger-discipline shape evolves (v2 wiring for `markdown-write`, new trigger types), update § Triggers here AND the matching declarations in individual Aspect specs ([[Commit]], [[Push]], [[PR]], [[NoGit]], etc.).
- **Pre-F090 vocabulary ("Type", "Trait" as Type-synonym) is retired.** Don't reintroduce "Type" terminology; if you find it lingering elsewhere in the vault, route through F090's migration backlog rather than spot-fixing here.
