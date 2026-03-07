# CAB Parts

An anchor is a folder that:
1. Contains a **marker file** — a markdown file with the same name as the folder
2. Contains a **primary anchor page** — the main content/overview page
3. Is registered with **HookAnchor** so it can be accessed by name from anywhere
4. Optionally has a **TLC** (short uppercase code) as its identifier

All parts are optional except the anchor folder and marker file.

- [[CAB Folder]] — the folder itself, with a marker file matching its name
- [[CAB Page]] — heading, `desc::` property, and link table
- [[CAB Naming]] — TLC vs full name, `{NAME}` prefix for all files
- [[CAB Docs]] — planning docs and published docs
- [[CAB Inbox]] — raw input drop zone for processing
- [[CAB PRD]] — product requirements document
- [[CAB Open Questions]] — unresolved questions with options and decisions
- [[CAB UX Design]] — user-facing interface specification
- [[CAB System Design]] — technical architecture and component design
- [[CAB Design Discussions]] — extended design reasoning and trade-off analysis
- [[CAB Backlog]] — low-priority ideas and deferred work
- [[CAB Features]] — individual feature descriptions in their own subfolder
- [[CAB Roadmap]] — milestone-based execution plan with checkbox tracking
- [[CAB Files]] — single-page codebase file tree with descriptions
- [[CAB Cards]] — optional cheat sheets and spaced repetition flashcards for the topic
- [[CAB Module Doc]] — module documentation for source code groupings
- [[CAB Code Repository]] — optional code repository linked via `Code` symlink, with sync-push
- [[CAB Claude]] — optional Claude Code configuration file
- [[CAB Documentation Site]] — published docs setup with MkDocs
- [[CAB Skill]] — omnibus Claude Code skill with actions, reference data, and scripts
- [[CAB Types]] — Simple, Public Repo, Private Repo, Paper


See [[CAB All Files]] for a visual overview of the full structure.
