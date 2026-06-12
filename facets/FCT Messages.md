---
description: Messages facet — the agent's per-anchor inbox of background-process messages that the agent reads on every pause. Distinct from `{NAME} Inbox.md` which is the user's drop-zone for raw input.
---

# CAB Messages

Spec for the **Messages facet** — the per-anchor file `{NAME} Messages.md` that holds background-process notes for the agent to read on every pause, separate from the user's raw-input `{NAME} Inbox.md`.

# BRIEF

- **This file is the facet spec, not an instance.** It defines the rules for the `{NAME} Messages.md` facet that lives in each anchor; it is not itself a messages file and never carries running-message content.
- **Scope — agent-facing only.** The Messages facet is the *agent's* inbox of background-process and out-of-band signals; the user's drop-zone for raw input is the separate `{NAME} Inbox.md` facet — do not blur the two on this page.
- **Inclusion test for this spec.** Content belongs here only when it defines how Messages files are structured, written, read, or pruned across anchors. Per-anchor message content, examples tied to a single anchor, or cross-facet workflow narrative belong in their own files or in [[CAB Base]] / a discipline page.
- **What does NOT go here.** Project-wide rules → CLAUDE.md. Markdown-rendering rules → [[R-markdown]]. Inbox-facet rules → `CAB Inbox.md`. Brief / discipline content → the relevant CAB discipline file.
- **Load-bearing distinction to preserve.** The frontmatter `description` and TLDR both call out the Messages-vs-Inbox split (agent-read background notes vs. user-dropped raw input); any future edit that loosens or removes that distinction breaks the facet's reason for existing.
- **Linking conventions.** Refer to sibling facets by their CAB filename in wiki-links (`[[FCT Inbox]]`, `[[CAB Backlog]]`); refer to per-anchor instances with the `{NAME}` placeholder (`{NAME} Messages.md`), never a concrete anchor's name.
- **Cross-references to keep in sync when this spec changes.** [[CAB Base]] dispatch tables, [[FCT All Files]] tree, and any anchor template that scaffolds a `{NAME} Messages.md` file.

