---
description: Common Anchor Example — the canonical anchor itself. Reference only, not invoked directly. Skills (rewire, audit, create, CAB) point at specific files here when they need to show what a correctly-structured anchor looks like.
---

# CAE — Common Anchor Example

CAE **is** a fully-wired anchor in canonical form. It exists so that other skills and humans have a single concrete reference to look at when the question is "what should this file look like?"

CAB prose (`skills/CAB/cab-facets/*.md`) describes *what each piece is* and *why*. CAE shows *exactly what the files look like* when the spec is applied. Two sources, one for reasoning, one for shape.

**CAE is reference material, not executable.** There is no runbook. Do not invoke `/cae`.

## Structure

```
CAE/                                        ← anchor root (slug: CAE, trait: code)
├── SKILL.md                                this file
├── .anchor                                 anchor config (flat YAML)
├── CAE.md                                  anchor page with dispatch table
├── CLAUDE.md                               agent configuration
└── CAE Docs/
    ├── CAE Docs.md                         top-level dispatch
    ├── CAE Plan/
    │   ├── CAE Plan.md                     plan dispatch
    │   ├── CAE PRD.md                      product requirements
    │   ├── CAE System Design.md            architecture + design principles
    │   ├── CAE Roadmap.md                  milestones
    │   ├── CAE Backlog.md                  deferred work
    │   ├── CAE Inbox.md                    raw input drop zone
    │   ├── CAE Triage.md                   triage inbox (agent-owned)
    │   └── CAE Rules.md                    project rules and exceptions
    ├── CAE User/
    │   ├── CAE User.md                     user dispatch
    │   └── CAE User Guide.md               end-user documentation
    └── CAE Dev/
        ├── CAE Dev.md                      dev dispatch
        ├── CAE Files.md                    source file tree
        ├── CAE Architecture.md             system-level design
        └── CAE Scheduler.md                module doc (canonical format)
```

## How other skills reference CAE

When a skill needs to show the correct shape of a file, it links to the specific CAE file:

```markdown
For the anchor page format, see `~/.claude/skills/CAE/CAE.md`.
For the Plan dispatch format, see `~/.claude/skills/CAE/CAE Docs/CAE Plan/CAE Plan.md`.
For a module doc in canonical form, see `~/.claude/skills/CAE/CAE Docs/CAE Dev/CAE Scheduler.md`.
```

Link to the **specific file** that demonstrates the piece — not the whole tree.

## About the content

CAE demonstrates a `code`-trait anchor. The fictional project is a simple CLI scheduler — enough domain to give the PRD, System Design, and module docs realistic content. The *structure* is what matters; the scheduler narrative is just illustrative.

## Variations not shown here

CAE shows the common case: folder name matches slug, `code` trait, inline mode. Other variations documented in CAB but not demonstrated in CAE:

- **Folder name differs from slug** — marker-file redirect pattern, see [[CAB Folder]]
- **Linked-mode code repo** — `code:` key points outside the anchor folder, see [[Code Anchor]]
- **Other traits** — `simple`, `topic`, `paper`, `skill`; see [[CAB Traits]]
