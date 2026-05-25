# /Tidy

`/tidy` validates an anchor's folder structure against its CAB type spec and fixes the structural issues it finds — naming compliance (every file and folder prefixed with `{NAME}`), broken links from the anchor page, roadmap-vs-detail separation, slug index entries, marker file consistency, and CLAUDE.md headers. Use it when you say "tidy this," "fix the structure," or "validate the anchor."

The skill walks the type-specific spec from `CAB Types/`, runs the checklist top to bottom (naming → links → roadmap content → slug → file structure → CLAUDE.md), and reports what was fixed plus anything that needs your manual attention. It's the "make this conform to the blueprint" pass — narrower than `/audit` (which reports without fixing), narrower than `/rewire` (which is the structural-repair workhorse), but broader than `/lint` (which is detect-only static analysis).
