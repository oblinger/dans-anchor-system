# Release

Orchestrate the release phase — changelog, version bump, packaging, publishing, and final ship.

## Pipeline

| Step | Action | File | What it does |
|------|--------|------|-------------|
| 1 | Changelog | [[code-changelog]] | Generate changelog from merged milestones |
| 2 | Version | [[code-version]] | Bump version numbers (semver) |
| 3 | Package | [[code-package]] | Build distributable artifacts |
| 4 | Publish | [[code-publish]] | Publish to website or registry |
| 5 | Ship | [[code-ship]] | Final gate: tag, push, announce |

## Dispatch

On `/code release`: execute each step in order. Each step file defines its own workflow. Steps 1-4 are currently TBD stubs except for Publish, which is fully implemented.
