# Publish

Publish a project to the personal website (oblinger.github.io). Creates a project page with splash content, optional documentation, downloads, and repo links. The page is built locally within the project anchor, then copied to the website repo and pushed.


## Website Infrastructure
- **Site**: https://oblinger.github.io/
- **Repo**: `/Users/oblinger/ob/proj/oblinger.github.io`
- **Engine**: Jekyll with `jekyll-theme-cayman`
- **Projects hub**: `projects.markdown` (permalink `/gitproj/`)
- **Project pages live in**: `gitproj/{ProjectName}/`
- **Deployment**: push to GitHub → GitHub Pages auto-builds


## Questions to Resolve

Before building, gather answers to these questions. The user may provide some upfront; ask for the rest interactively.

### Identity
- **PROJECT NAME** — Display name for the project page title
- **SLUG** — URL-safe directory name (e.g., `HookAnchor`, `AlienBiology`). Default: project name with no spaces
- **ONE-LINER** — Single sentence description (used in Jekyll `description:` front matter and the projects hub)

### Content
- **SPLASH TEXT** — What goes on the main page? Options:
  - Write new content (agent drafts based on existing README/docs)
  - Adapt existing README.md from the repo
  - User provides text
- **DOCUMENTATION** — Should docs be published? Options:
  - None — splash page only
  - Markdown docs — `.md` files with cayman layout, built by Jekyll
  - Pre-built HTML — generated docs (MkDocs, Sphinx, Quarto, etc.) copied as-is
  - PDF documents — papers/whitepapers served as downloads
- **SCREENSHOTS/IMAGES** — Any images to include on the splash page?

### Links
- **REPO LINK** — Link to the source repository? If yes, provide the GitHub URL
- **DOWNLOAD** — Offer a downloadable artifact (binary, installer, zip)? If yes, where is it built or stored?
- **EXTERNAL LINKS** — Any other links to include (demo, video, related projects)?

### Navigation
- **PROJECTS HUB** — Add a link from the projects page (`/gitproj/`)? (Default: yes)
- **CUSTOM PERMALINK** — Use a custom URL path? (Default: `/gitproj/{SLUG}/`)

### Legal
- **LICENSE** — What license to publish under? Options:
  - All rights reserved (default — no LICENSE file, copyright notice on page)
  - MIT License
  - Apache 2.0
  - Other (specify)
- If a LICENSE file already exists in the repo, use that. Otherwise ask.

### Build Integration
- **AUTO-DEPLOY** — Should the project's justfile get a `docs-deploy` recipe that copies to the website repo, commits, and pushes? (Default: yes if justfile exists)
- **GENERATED DOCS** — If docs are generated (MkDocs, Sphinx, etc.), what build command produces them?


## Workflow

### 1. Gather Information
Read the project's existing materials (README, docs, CLAUDE.md) to pre-fill answers. Present the questions above, filling in what you can infer. Ask the user to confirm or override.

### 2. Build Locally
Create a `website/` directory inside the project anchor (vault side, not repo side) containing:

```
website/
├── index.md              # Splash page with Jekyll front matter
├── [additional .md]      # Documentation pages (if any)
├── [assets/]             # Images, PDFs (if any)
└── deploy.sh             # Script to copy to website repo and push
```

**Jekyll front matter** for each `.md` file:
```yaml
---
layout: cayman
title: {PROJECT NAME}
description: {ONE-LINER}
permalink: /gitproj/{SLUG}/
---
```

### 3. Review
Show the user the generated splash page content. Iterate until approved.

### 4. Deploy
Run the deploy script or equivalent:
1. Copy `website/` contents to `oblinger.github.io/gitproj/{SLUG}/`
2. If PROJECTS HUB = yes, add a link to `projects.markdown`
3. `cd` to website repo, `git add`, `git commit`, `git push`
4. Report the live URL: `https://oblinger.github.io/gitproj/{SLUG}/`

### 5. Integrate (optional)
If AUTO-DEPLOY = yes, add a `docs-deploy` recipe to the project's justfile:
```just
website_repo := "/Users/oblinger/ob/proj/oblinger.github.io"

# Deploy project page to personal website
publish:
    @echo "Deploying to website repo..."
    cp -r website/* {{website_repo}}/gitproj/{SLUG}/
    cd {{website_repo}} && git add gitproj/{SLUG} && git commit -m "Update {PROJECT NAME} page" && git push
    @echo "✓ Deployed to https://oblinger.github.io/gitproj/{SLUG}/"
```


## Existing Project Patterns

Reference these when building pages — match the style and conventions:

| Project | Type | Pattern |
|---------|------|---------|
| HookAnchor | Pre-built HTML | `index.html` redirect → `README.html` + 5 doc pages + custom CSS |
| AlienBiology | Markdown + PDFs | `.md` with cayman layout, PDFs alongside |
| DeliberativeCoherence | Quarto + Markdown | `.md` splash + `.qmd` rendered to HTML |
| ASIO | Topic collection | Index `.md` linking to 30+ individual `.md` files |
| abio-docs | Generated docs | MkDocs output, whole directory replaced on deploy |
