# Publish — Deploy an anchor's public page to the web

Publish an anchor's web presence. Reads config from `.anchor/config.yaml` to determine method and options.

## Config

In `.anchor/config.yaml`:

```yaml
publish:
  method: gitproj           # or github-pages
  listed: false             # true = add to main projects page
  title: "The Forum"        # page title (defaults to RID)
  description: "..."        # one-line description (defaults to anchor description)
  assets:                   # files to include alongside index.html
    - "The Forum.pdf"
```

## Methods

### gitproj (default)

Publishes to `https://oblinger.github.io/gitproj/{name}/`. This is a subdirectory of the main gitproj repo — lightweight, no separate repo needed.

**Steps:**
1. Read publish config from `.anchor/config.yaml`
2. Run `/audit publish` — check for PII, credentials, sensitive paths
3. Build `index.html` from anchor description, title, and assets
4. Copy assets (PDF, images) to the publish folder
5. Push to `oblinger/gitproj` repo under `{name}/`
6. If `listed: true`, add entry to the main projects index page

**Repo location:** `~/ob/proj/gitproj/` (clone if not present)

### github-pages

Publishes to a dedicated GitHub Pages site — either `{name}.github.io` or a custom domain.

**Steps:**
1. Read publish config from `.anchor/config.yaml`
2. Run `/audit publish` — check for PII, credentials, sensitive paths
3. Create or update the repo `oblinger/{name}`
4. Build site (index.html + assets, or Jekyll/static site if configured)
5. Enable GitHub Pages on the repo
6. If custom domain, configure CNAME

## Steps (common)

1. Read `.anchor/config.yaml` — get publish method and options
2. If no publish config exists, ask the user which method to use
3. Run `/audit publish` to check for PII before publishing
4. Build the page — generate `index.html` if it doesn't exist, or use existing
5. Copy assets listed in config
6. Deploy using the configured method
7. Print the published URL
8. Add the published URL to the anchor page dispatch table — in the **External** row, add a link labeled `Published`: `[Published](https://oblinger.github.io/gitproj/{name}/)`. If no External row exists, create one.

## Page Template

For simple splash pages (most anchors), generate an `index.html`:

```html
<!DOCTYPE html>
<html>
<head>
  <title>{title}</title>
  <meta charset="utf-8">
  <style>
    body { font-family: -apple-system, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; }
    h1 { margin-bottom: 0.5em; }
    .description { font-size: 1.2em; color: #555; margin-bottom: 2em; }
    .assets a { display: block; margin: 0.5em 0; }
  </style>
</head>
<body>
  <h1>{title}</h1>
  <p class="description">{description}</p>
  <div class="assets">
    {asset links}
  </div>
</body>
</html>
```

For more complex sites, the anchor can have a `docs/` folder with custom HTML/CSS that gets published directly.
