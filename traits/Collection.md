# Collection

The **Collection** trait — an anchor whose page **enumerates a collection of members**: an anchor that exists *to be* the set of its children, where the children are an expected, **usually one** kind of thing (projects, dated entries, entities, drives). Declared by `Collection` in the anchor's `.anchor` `traits:` key.

Follows [[CAB Base]] with these deltas. Sibling identity traits: [[Topic Anchor]], [[Code Anchor]], [[Paper Anchor]], [[Simple Anchor]], [[Skill Anchor]].

## When to Use

When an anchor's reason for being is *the collection itself* — its page is dominated by an enumeration of like members, and "add a member" = "add one more of the same kind." Examples: [[Bespoke]] (code subprojects), [[Log]] (dated data-lists), [[AT]] (entity pages), [[Disk]] (drives), [[prj]] (personal projects).

Contrast with [[Topic Anchor]]: a Topic is a **heterogeneous routing hub** *about a subject* (mixed children — docs, sub-topics, varied sub-anchors); a Collection is a **homogeneous enumeration** *of like members*. A Topic deepens (more sub-structure); a Collection widens (more members). When in doubt: if adding content means "one more of the same," it's a Collection; if it means "another facet of the topic," it's a Topic.

## Deltas from Base

- **Member zone in the dispatch table.** A Collection's [[DSC Dispatch Table]] carries a **Member zone** below the Masthead — the members rendered as a **member list** (flat) or **member groups** (categorized), and **manual / auto / hybrid** (auto-listed below `---` / `...`, or hand-ordered, or pinned-plus-auto). Which layout is the [[progressive-disclosure]] List / Grouped choice; the compact→grouped graduation by member count is [[granularity]]. *(Full structure: [[F155 — Dispatch-table structure spec + CAE worked examples|F155]].)*
- **Datedness is orthogonal.** Members may be dated (Log — a dated-entry stream) or not (Bespoke — undated projects). This is the `dated?` dimension of [[file-association]] riding on top of the trait; the Collection trait itself doesn't care.
- **Members carry an expected member type.** The anchor's children conform to a known shape (all projects, all entities, all `Disk <name>.md` pages). Adding a member = creating one more file/sub-anchor of that shape.

## Composability

**Capability trait** (a structural shape layered on an identity), cardinality **at most one**. **Composes freely** — with [[Topic Anchor]] (a routing hub whose children happen to be homogeneous), [[Simple Anchor]] (a bare folder whose page is a member list), [[Skill Anchor]] (a skill group enumerating its skills, e.g. [[SKL]]), or any other identity. **No exclusions** — per [[CAB Aspects]] § Governing principle (compose by default; exclude only on logical incompatibility), nothing about *enumerating members* contradicts any identity, so Collection mixes with all of them. Most Collections are also Topic or Simple, but that's a tendency, not a constraint.

## Details — on "homogeneous"

The headline says "usually one homogeneous type," and that is **spiritually correct** but not strict. A Collection *can* hold members of several kinds — in that case the member type is simply a **union** of those kinds. The load-bearing point is not strict homogeneity; it is that **there is an expected member type at all** — the anchor enumerates members drawn from a known (possibly union) type, rather than holding arbitrary heterogeneous content. So read "Collection" as *an enumerated collection of members of an expected type*, where that type is usually singular and occasionally a union.

## Example

[[Disk]] — a Collection of drive pages:

```
Disks/
├── .anchor                  (traits: Collection, Simple)
├── Disk.md                  anchor page — Masthead + member list of drives
├── Disk BEAST.md            member
├── Disk BIG BLUE.md         member
└── Disk COPPER.md           member
```

The anchor page's Member zone enumerates `Disk *.md`; the singular `Disk` prefix is the member-type signature (the [[file-association]] naming convention).

## Audit

Type-specific structure checks for Collection anchors.

### Expected
- The anchor page carries a **Member zone** (member list or member groups) below the Masthead.
- Members share an expected naming shape (the member-type signature).
- If dated, members follow the [[dated-entry-stream]] conventions (ISO-prefixed, newest-first).

## Anchor-page examples

This trait underlies the three Container shapes in the [[FCT Anchor Page]] kinds catalog, each with its own worked example: [[HBR Components]] (grouped), [[Espresso]] (list), [[HBR Log]] (chronological).

## Related

- [[DSC Dispatch Table]] — the Masthead + Member-zone structure a Collection's page uses.
- [[progressive-disclosure]] — member list vs member groups (List / Grouped).
- [[file-association]] — dated-or-not + member placement/naming.
- [[granularity]] — when a member list graduates compact → grouped.
- [[F152 — Set Anchor trait — homogeneous-collection anchor kind; dispatch-organization via existing disciplines|F152]] — the design feature; "Set Anchor" was the working name, renamed **Collection** 2026-06-11 (set is too math-technical; list collides with the dispatch List pattern).
