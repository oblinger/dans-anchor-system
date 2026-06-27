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
├── CAE Design/                             design docs (PRD, Architecture, Decisions)
│   ├── CAE Design.md                       design dispatch
│   ├── CAE PRD.md                          product requirements
│   ├── CAE Architecture.md                 system-level architecture
│   ├── CAE Decisions.md                    principles + rules (audit-tiered)
│   └── CAE System Design.md                (legacy — folding into Architecture per F113)
├── CAE Track/                              tracking docs (was {NAME} Docs/{NAME} Plan/ pre-2026-06-08)
│   ├── CAE Track.md                        track dispatch
│   ├── CAE Roadmap.md                      milestones
│   ├── CAE Backlog.md                      deferred work
│   ├── CAE Inbox.md                        raw input drop zone
│   └── CAE Triage.md                       triage inbox (agent-owned)
├── CAE User Docs/                          end-user docs (was CAE User/ pre-2026-06-08)
│   ├── CAE User Docs.md                    user-docs dispatch
│   └── CAE Guide.md                        end-user guide
└── CAE Dev Docs/                           developer docs (was CAE Dev/ pre-2026-06-08)
    ├── CAE Dev Docs.md                     dev-docs dispatch
    ├── CAE Files.md                        source file tree
    └── CAE Scheduler.md                    module doc (canonical format; subsystem of Architecture)
```

## How other skills reference CAE

When a skill needs to show the correct shape of a file, it links to the specific CAE file:

```markdown
For the anchor page format, see `~/.claude/skills/CAE/CAE.md`.
For the Track dispatch format, see `~/.claude/skills/CAE/CAE Track/CAE Track.md`.
For the Architecture format, see `~/.claude/skills/CAE/CAE Design/CAE Architecture.md`.
For a module doc in canonical form, see `~/.claude/skills/CAE/CAE Dev Docs/CAE Scheduler.md`.
```

Link to the **specific file** that demonstrates the piece — not the whole tree.

## About the content

CAE demonstrates a `code`-trait anchor. The fictional project is a simple CLI scheduler — enough domain to give the PRD, System Design, and module docs realistic content. The *structure* is what matters; the scheduler narrative is just illustrative.

## Variations not shown here

CAE shows the common case: folder name matches slug, `code` trait, inline mode. Other variations documented in CAB but not demonstrated in CAE:

- **Folder name differs from slug** — marker-file redirect pattern, see [[CAB Folder]]
- **Linked-mode code repo** — `code:` key points outside the anchor folder, see [[Code Anchor]]
- **Other traits** — `simple`, `topic`, `paper`; see [[TRT]]
- **Skill trait** — `skill`-trait anchor (SKILL.md at the root, no code repo, user docs in the parallel SKL tree); see [[CSE]] (Common Skill Example)
