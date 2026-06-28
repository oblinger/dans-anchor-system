---
description: "prior-art survey of existing rule/hook systems + recommended adaptation"
---
# Warden Survey

→ **[[#Recommended Adaptation for the Anchor System|Recommended adaptation for the anchor system]]**
## Overview

Survey of existing systems that do — or come close to — the target pattern: an agent is about to write a file → a rule matches on the file **path** → the rule checks the **content** against a regular expression / format spec → on mismatch a corrective **message** is sent back to the agent so it self-fixes → optionally the write is **blocked**. Scored on four legs throughout: **(a)** path/glob match · **(b)** regex/content validation · **(c)** corrective message fed back to the agent · **(d)** block.

## Headline finding

The pattern **already exists off-the-shelf in skeletal form**, and the closest match is a first-party Anthropic plugin (**Hookify**), built on **Claude Code hooks**. The intercept-and-feedback *plumbing* is solved and standardized. The genuinely under-served leg — and the load-bearing novelty of the anchor rule system — is **whole-resulting-file validation against a rich multi-rule format spec** (not just a single regex on the inserted diff), with a corrective message keyed to each specific violation. No tool ships that as a turnkey declarative engine.

A distinction to design around: the existing declarative tools match on the **edit text being written** (`new_text`/`old_text`) plus the path — *not* a re-read of the **whole resulting file** against a format spec. "Validate the entire resulting file and feed the error back" is the part still assembled by hand (a `PostToolUse` validator script).

## The qualitative landscape (meta-survey)

Five qualitatively distinct places such a system could live, each surveyed below:

1. **Agent-harness–native mechanisms** — hooks/rules built into coding agents. *Closest to the exact pattern.*
2. **LLM guardrail frameworks** — validate model output against rules, with a re-ask loop.
3. **File/doc linting & policy-as-code** — mature regex/format enforcement on files.
4. **Commercial agent governance / control planes** — enterprise policy products.
5. **DIY / open-source community** — people building exactly this on top of hooks.

## Ranked: closest to the exact pattern

### Tier 1 — The native primitive + its declarative wrappers (this *is* the system)

- **Claude Code hooks — the exact mechanism, native.** `PreToolUse` matches the Write/Edit tool; the hook script inspects `tool_input.file_path` + content; returns `permissionDecision: "deny"` with a `permissionDecisionReason` fed back to the agent (which retries), and blocks even under `--dangerously-skip-permissions`. `PostToolUse` validates-after-write → `{decision:"block", reason:...}` to drive the fix loop. Every leg (a/b/c/d). Caveat: prefer JSON `deny`/`block` output over bare exit-code-2 (bug #24327 — exit-2 sometimes halts instead of feeding back).
- **Hookify (official Anthropic plugin) — ~90% of the pattern, declarative. ★ clone-this-first.** `/plugin install hookify`, then `/hookify "<rule in English>"`. Rules are markdown-with-YAML at `.claude/hookify.{rule}.local.md`: `field: file_path` + `operator: regex_match` for the path; `field: new_text`/`old_text`/`content` + `regex_match`/`contains`/`not_contains`/`starts_with`/`ends_with` for content; `action: block|warn`; the markdown body is the message shown to the agent. Multi-condition (AND). Limitation = exactly the gap: matches the inserted text, not a re-read of the whole file; one regex per condition, not a format spec.
- **cchook (YAML) + cchooks (Python SDK) — the DIY building blocks.** `cchook` (syou6162): declarative YAML conditions (`file_extension`, `prompt_regex`) + actions (`exit_status: 2`, `output`). `cchooks` (GowayLee, ~131★): imperative Python SDK to hand-build the pattern with arbitrary logic. [`disler/claude-code-hooks-mastery`](https://github.com/disler/claude-code-hooks-mastery) (~3.8k★): canonical reference showing the lint→feedback→self-fix loop end to end.

### Tier 2 — The content-check engine (the "regex matches the document" half — commoditized)

- **Vale — closest conceptual ancestor for prose/markdown. ★** A Vale rule = path-glob (`.vale.ini` `[*.md]` sections) + in-file `scope:` (headings vs code) + regex (Go superset *with* lookaround) + a custom `message:` with `%s` interpolation + `level:` + `link:`. That is the target design *minus the agent loop*; people already pipe its JSON output into `PostToolUse` hooks. For a markdown vault, this is the engine to adopt rather than reinvent.
- **Semgrep — the closest *complete* system, but code-only.** Per-path rules (`paths:`), AST + `pattern-regex` content checks, interpolated `message:`, deterministic `fix:`, and a shipped **official MCP server** that lets the agent write-a-rule → scan → read-message → fix in a loop. Living proof the full idea works for code. `ast-grep` is the lighter local equivalent.
- **Frontmatter/schema + policy-as-code.** For structured metadata: `remark-lint-frontmatter-schema` (JSON Schema `pattern` on frontmatter); a `validate-md` skill does true whole-file frontmatter-vs-`schema.yaml` validation (but on-demand, not in the write loop). For rich cross-field invariants: Conftest/OPA Rego, CUE. `pre-commit` (regex `files:` + `pygrep` regex content + block) is the same shape but commit-grained.

### Tier 3 — Commercial productization of the hook primitive

- **Endor Labs Agent Governance** — productized hooks: allow / **deny-with-reason** / **modify**, agent self-corrects same turn. Closest commercial match (security-leaning). **Arnica** injects policy at generation time across Claude/Cursor/Copilot/Gemini. **Qodo** (June 2026) auto-*mines* conventions from codebase + PR history into enforceable rules — closest to the format/convention spirit, but PR/review grain. **OpenAI Codex hooks** mirror Claude's allow/deny/modify. None ship "path-regex → whole-file-format → corrective message" turnkey for general conventions.

### Tier 4 — Adjacent, looks similar, isn't (advisory, not enforcing)

Cursor `.mdc` rules, Windsurf, Continue, Copilot `applyTo`, Aider CONVENTIONS.md, AGENTS.md, `ruler`, `agent-rules` — these do path/glob matching **only to select which prompt text to inject**. No content validation, no deterministic message, no block; compliance is probabilistic and decays over a long session. The LLM-guardrail frameworks (Guardrails AI, NeMo, Instructor, LangGraph middleware) validate **model-output blobs** with a re-ask loop but have **no concept of file path** — the path only emerges if the file-write is a tool whose args you intercept.

## Summary table

| System | (a) path | (b) content regex | (c) feedback to agent | (d) block | Full pattern? |
|---|---|---|---|---|---|
| **Claude Code hooks** | ✓ | ✓ (your script) | ✓ (reason) | ✓ | **YES — native, exact** |
| **Hookify** (official) | ✓ | ✓ (on `new_text`) | ✓ (rule body) | ✓ | **~90% — declarative; no whole-file** |
| cchook / cchooks / mastery | ✓ | ✓ | ✓ | ✓ | YES — DIY building blocks |
| **Vale** | ✓ | ✓ (regex+lookaround) | ✓ (`message:`+link) | via hook | content-engine ★ (no native loop) |
| **Semgrep** / ast-grep | ✓ | ✓ (AST+regex) | ✓ (`message:`) +fix | via MCP | complete — but code-only |
| frontmatter-schema / OPA / pre-commit | ✓ | ✓ | ✓ | ✓ (commit) | content-engine (not edit-grained) |
| Endor / Arnica / Qodo | ✓ | partial | ✓ | ✓ | commercial; security/PR grain |
| Cursor/Windsurf/Copilot/Continue rules | ✓ | ✗ | ✗ | ✗ | advisory only |
| Guardrails AI / NeMo / LangGraph | ✗ (no path) | ✓ | ✓ (re-ask) | ✓ | output-blob, not file-edit |

## Three signals worth tracking

- **[arXiv 2606.13174](https://arxiv.org/abs/2606.13174)** — *"Getting Better at Working With You: Compiling User Corrections into Runtime Enforcement for Coding Agents"*: compiles user corrections into verifiers that intercept on failure and "report the rule violation and evidence to the agent, compelling it to revise until compliant." The target design as a research paper.
- **[AGENTS.md proposal #179](https://github.com/agentsmd/agents.md/issues/179)** — explicitly contemplates "regex-validated structures or full file schemas" with violation feedback. The standards direction is heading toward this but hasn't shipped it — worth influencing.
- **[Microsoft Agent Governance Toolkit](https://opensource.microsoft.com/blog/2026/04/02/introducing-the-agent-governance-toolkit-open-source-runtime-security-for-ai-agents/)** (Apr 2026) — generic intercept-every-action policy engine (YAML/Rego/Cedar), but security/OWASP-framed and block-oriented, not format-convention.

## Recommended Adaptation for the Anchor System

Keep it to three picks. Each names a primary and, where it's a close call, the alternative to keep in view.

1. **Interception layer → Claude Code hooks (`PreToolUse` deny + `PostToolUse` block).** This is non-negotiable: it's the only native mechanism that intercepts the agent's own Write/Edit and feeds a message back. Don't rebuild the plumbing. *No real alternative* — MCP-gateway interceptors achieve the same semantics but only over MCP tools, not native edits, so they'd require routing all file writes through an MCP filesystem tool.

2. **Rule-file UX → model after Hookify's declarative rule format.** Markdown+YAML rule files (`file_path` regex + content operators + a message body + block/warn) are the right author-facing shape and it's first-party. *I recommend Hookify's format, but it could also be `cchook`'s YAML schema* if the anchor system wants to live outside the Anthropic plugin mechanism and own the engine end to end — same expressiveness, fully self-contained.

3. **Content engine → Vale for the markdown/prose format rules.** The vault is markdown; Vale's rule = path-glob + regex + interpolated message + severity is a near-exact import of what's needed, and it wires cleanly into a `PostToolUse` hook. *I recommend Vale for the expressible-as-regex rules, but it could also be a custom `PostToolUse` validator script* for the cases Vale/Hookify can't express — namely whole-resulting-file validation against a multi-rule format spec. That last piece is the genuine gap; budget to build it rather than expecting an off-the-shelf engine.

**One-line build path:** Hookify-style declarative rule files → dispatched by a `PostToolUse` hook → Vale for regex-expressible markdown rules, a small custom validator for whole-file format specs → corrective message returned via `reason`/`additionalContext` so the agent self-fixes. Study [`disler/claude-code-hooks-mastery`](https://github.com/disler/claude-code-hooks-mastery) for the reference loop.

## Sources

- Claude Code hooks: https://code.claude.com/docs/en/hooks · https://code.claude.com/docs/en/hooks-guide
- Hookify (official plugins): https://github.com/anthropics/claude-plugins-official
- cchook: https://github.com/syou6162/cchook · cchooks SDK: https://github.com/GowayLee/cchooks · mastery: https://github.com/disler/claude-code-hooks-mastery
- Vale: https://vale.sh/docs/styles · https://vale.sh/docs/guides/regex
- Semgrep MCP: https://github.com/semgrep/mcp · autofix: https://semgrep.dev/docs/writing-rules/autofix · ast-grep: https://ast-grep.github.io/reference/yaml.html
- remark-lint-frontmatter-schema: https://github.com/JulianCataldo/remark-lint-frontmatter-schema · Conftest: https://github.com/open-policy-agent/conftest · pre-commit: https://pre-commit.com/
- Endor Labs: https://www.endorlabs.com/learn/introducing-agent-governance-using-hooks-to-bring-visibility-to-ai-coding-agents · Arnica: https://www.arnica.io/solutions/agentic-rules-enforcer · Qodo: https://www.helpnetsecurity.com/2026/06/24/qodo-ai-generated-code-governance/ · Codex hooks: https://developers.openai.com/codex/hooks
- arXiv 2606.13174: https://arxiv.org/abs/2606.13174 · AGENTS.md #179: https://github.com/agentsmd/agents.md/issues/179 · MS Agent Governance Toolkit: https://opensource.microsoft.com/blog/2026/04/02/introducing-the-agent-governance-toolkit-open-source-runtime-security-for-ai-agents/
