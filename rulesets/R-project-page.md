# RULESET R-project-page
include::
where:: `file: **/website/index.md`
description:: Rules every Project Page instance must satisfy — presence of a `website/` folder, the Jekyll cayman front matter, and the deploy script.

### RULE R-project-page-01 — `website/` folder present (checked)
The anchor contains a `website/` subdirectory with at minimum an `index.md` and a `deploy.sh`.
**Check pattern:** `website/index.md` and `website/deploy.sh` exist inside the anchor folder.
**Tier:** checked
**Why:** the `website/` folder is how the project page is detected; missing it means the facet is absent, not malformed.

### RULE R-project-page-02 — Jekyll cayman front matter (checked)
`website/index.md` opens with YAML frontmatter including `layout: cayman`, a non-empty `title:`, a non-empty `description:`, and a `permalink: /gitproj/{slug}/`.
**Check pattern:** frontmatter block contains `layout: cayman`, `title:`, `description:`, and `permalink:` matching `/gitproj/`.
**Tier:** checked
**Why:** the cayman layout and permalink are what Jekyll needs to render and route the page; missing fields produce a broken or invisible page.

### RULE R-project-page-03 — Dispatch-table Related row carries the published URLs (sampled)
The anchor's dispatch table (root `{slug}.md`) includes a `Related` row carrying both the GitHub repo link and the project page URL `https://oblinger.github.io/gitproj/{slug}/` (repo/site links live in Related, not a separate External row).
**Check pattern:** the anchor page has a `| Related |` row containing `oblinger.github.io/gitproj/`.
**Tier:** sampled
**Why:** the Related row is how readers discover the published page; without it the deployment is silent to navigators.

### RULE R-project-page-04 — Permalink and dispatch-table URL stay in sync (stated)
The `permalink:` value in `website/index.md` frontmatter and the URL in the anchor's `Related` dispatch row must use the same `{slug}` — they cannot drift.
**Check pattern:** extract `{slug}` from frontmatter `permalink:`; verify the same path appears in the `Related` row.
**Tier:** stated
**Why:** mismatched slugs cause the dispatch row to link a 404; the projects hub `/gitproj/` lists all pages by permalink.
