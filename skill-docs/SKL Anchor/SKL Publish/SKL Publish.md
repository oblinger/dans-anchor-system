---
description: "`/publish` deploys an anchor's public page to the web."
---
# /Publish
`/publish` deploys an anchor's public page to the web. It reads the publish config from the anchor's `.anchor` file to decide which method to use — **gitproj** (the default; publishes to `https://oblinger.github.io/gitproj/{name}/` as a subdirectory of your main gitproj repo, no separate repo needed) or **github-pages** (dedicated repo at `oblinger/{name}`, optionally with a custom domain). Use it when you say "publish this," "deploy the page," or "push to web."

| -[[SKL Publish]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[SKL Anchor]] → [SKL Publish](hook://p/SKL%20Publish)<br>: the `/publish` skill |
| --- | --- |
| Related | [[skills/publish/SKILL.md\|SKILL]],   |
| [[SKL Publish Design\|Design]] |  |

Before deploying, the skill runs `/audit publish` to sweep for PII, credentials, and sensitive paths. Then it builds `index.html` from your anchor's title, description, and assets list (PDFs, images), copies the assets, pushes to the configured remote, and adds a `Published` link in the anchor page's dispatch table's External row so you can find the live URL later. For simple splash pages it auto-generates the HTML; for complex sites you can keep a `docs/` folder of custom HTML/CSS and publish that directly.
