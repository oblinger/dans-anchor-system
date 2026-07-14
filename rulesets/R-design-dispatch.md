# RULESET R-design-dispatch
include::
where:: `file: **/{{slug}} Design.md`
description:: Rules every `{slug} Design.md` dispatch page must satisfy — location, H1 form, dispatch-table structure, and required-document coverage for Code anchors.

### RULE R-design-dispatch-01 — File lives inside `{slug} Design/` (checked)
The dispatch page `{slug} Design.md` must reside at `{slug} Design/{slug} Design.md` — inside the root-level `{slug} Design/` folder.
**Check pattern:** the file's parent directory name matches `{slug} Design`.
**Why:** the location is the facet's contract; a misplaced dispatch page is invisible to anchor-page resolution and breaks folder-relative linking. (sampled)

### RULE R-design-dispatch-02 — H1 is `# {slug} Design` (checked)
The file's H1 reads exactly `# {slug} Design` where `{slug}` is the anchor's root ID.
**Check pattern:** H1 matches `^# \S+ Design$`.
**Why:** the H1 is used as the anchor-page title in dispatch tables; a wrong H1 surfaces the wrong name everywhere it appears. (checked)

-[[{slug} Design]]-` form (checked)
-[[{slug} Design]]-` in column 1 and the `><br>: design — …` description in column 2.
**Check pattern:** first table row starts with `| -[[` and ends with a `><br>:` description.
**Why:** the strikethrough self-link form is the DAS Anchor Page standard for dispatch tables; deviating breaks the consistent navigation pattern across all anchors. (sampled)

### RULE R-design-dispatch-04 — Interface entry present for Code anchors (sampled)
Anchors that carry the Code trait MUST include a `{slug} Interface.md` row in the dispatch table (per F094 Q3=A — Interface is a system contract, not an end-user doc).
**Check pattern:** for anchors with `traits: [code]` or equivalent, the dispatch table contains a row linking `{slug} Interface`.
**Why:** Interface is required for Code anchors; omitting it leaves callers without the public-API contract the Design folder exists to surface. (sampled)
