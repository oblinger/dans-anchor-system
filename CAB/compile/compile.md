| -[[compile]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[skills]] → [compile](hook://p/compile)<br>:  |
| --- | --- |
| ~~[targets/audit-docs](hook://targets/audit-docs)~~ |  |
| ~~[targets/code-rewire](hook://targets/code-rewire)~~ |  |

# /cab compile

Generate executable checklists from CAB specs and embed them directly into skill files. Each compilation target describes which source files to read, what extras to preserve, and which skill file to update.

## Runbook

1. List all files in `~/.claude/skills/CAB/compile/targets/`
2. For each target file:
   a. Read the target (sources, extras, skill file path)
   b. Read each source file listed
   c. Read the skill file and find the `<!-- compiled:start -->` / `<!-- compiled:end -->` markers
   d. Read the existing compiled section (between the markers)
   e. Generate the checklist from the sources
   f. Append the extras
   g. Replace the content between the markers in the skill file
3. Report: "Compiled N targets"

## Target File Format

Each target in `targets/` has:

- **Skill File** — path to the skill file containing `<!-- compiled:start -->` / `<!-- compiled:end -->` markers
- **Sources** — CAB files to read for the spec (reference examples, format rules)
- **Extras** — additional rules not derivable from specs (gotchas, formatting traps)

## Compiled Section Markers

Compiled content lives inside skill files between markers:

```markdown
<!-- compiled:start source=CAB/compile/targets/code-rewire.md -->
... generated checklist ...
<!-- compiled:end -->
```

The `source=` attribute in the start marker identifies which compile target produced this section.

## Compilation Rules

- The compiled output is a **pure imperative checklist** — no prose, no examples
- Organized by file path (H2 headings), with bullet checkboxes under each
- Every item is actionable: "Has X", "Links to Y", "Contains Z"
- Extras are appended at the end under `## Universal Rules`
- Read the existing compiled section first — preserve any manually-added items marked with `# KEEP` comments

## Compile Targets

These are the skill files that contain compiled sections:

| Target | Skill File |
|--------|-----------|
| `targets/code-rewire.md` | `~/.claude/skills/rewire/SKILL.md` |
| `targets/audit-docs.md` | `~/.claude/skills/audit/audit-docs.md` |
