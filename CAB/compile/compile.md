# /cab compile

Generate executable checklists from CAB specs. Each compilation target describes which source files to read and what extras to preserve. The output is a `.compiled.md` file that agents execute mechanically.

## Steps

1. List all files in `~/.claude/skills/CAB/compile/targets/`
2. For each target file:
   a. Read the target (sources, extras, output path)
   b. Read each source file listed
   c. Read the existing compiled output (if it exists)
   d. Generate the checklist from the sources
   e. Append the extras
   f. Write to the output path
3. Report: "Compiled N targets"

## Target File Format

Each target in `targets/` has:

- **Output** — path to the compiled checklist
- **Sources** — CAB files to read for the spec (reference examples, format rules)
- **Extras** — additional rules not derivable from specs (gotchas, formatting traps)

## Compilation Rules

- The compiled output is a **pure imperative checklist** — no prose, no examples
- Organized by file path (H2 headings), with bullet checkboxes under each
- Every item is actionable: "Has X", "Links to Y", "Contains Z"
- Extras are appended at the end under `## Universal Rules`
- If a compiled file already exists, read it first — preserve any manually-added items marked with `# KEEP` comments
