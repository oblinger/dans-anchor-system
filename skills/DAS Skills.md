---
description: "Skills — the `/`-invocable runbooks"
---

# DAS Skills
The catalog of skills — the `/`-invocable runbooks — organized by the nine subsystems in [[DAS]] order.

![[F143-1-top-level.svg|2400]]
*Dan's Anchor System — the kinds of system parts: **Skills** (verbs) create **Facets** (nouns); **Disciplines** (adjectives) modify both; **Rulesets** constrain all three.*



| -[[DAS Skills]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [SKL](hook://SKL) → [DAS Skills](hook://p/DAS%20Skills)<br>: Skills — the `/`-invocable runbooks |
| --- | --- |
| Related | [[DAS Facets\|Facets]],  [[DAS Disciplines\|Disciplines]],  [[DAS Traits\|Traits]],  [[DAS Examples\|Examples]],  [[DAS Rulesets\|Rulesets]],  [[DAS\|dans-anchor-system]],   |
|  |  |
|  | **SKILL GROUPS** — organized by the nine subsystems, in [[DAS]] order |
| [[DAS Anchor Design\|Anchor]]+ | [[DAS Anchor Toolkit\|Anchor Toolkit]],  [[DAS Create\|Create]],  [[DAS Migrate\|Migrate]],  [[DAS Move\|Move]],  [[DAS Publish\|Publish]],  [[DAS Streams\|Streams]],  [[DAS Yore\|Yore]],   |
| [[DAS Hygiene Design\|Hygiene]]+ | [[DAS Audit\|Audit]],  [[DAS Dupes\|Dupes]],  [[DAS Maintain\|Maintain]],  [[DAS Rewire\|Rewire]],  [[DAS Slug Scan\|Slug Scan]],  [[DAS Tidy\|Tidy]],  [[rule/SKILL\|Rule]],   |
| [[DAS Tracking Design\|Tracking]]+ | [[DAS Backlog\|Backlog]],  [[DAS workflow\|Workflow]],  [[DAS Messages\|Messages]],  [[DAS Ask\|Ask]],  [[DAS Groom\|Groom]],   |
| [[DAS Design Design\|Design]]+ | [[DAS Plan\|Plan]],  [[DAS Architect\|Architect]],  [[DAS Parley\|Parley]],   |
| [[DAS Code Design\|Code]]+ | [[DAS Code Skill\|Code]],  [[DAS Fix\|Fix]],  [[DAS Pilot Flow\|Pilot Flow]],  [[DAS PR Flow\|PR Flow]],  [[cleanup/SKILL\|Cleanup]],  [[module-doc/SKILL\|Module Doc]],  [[devops/SKILL\|Devops]],   |
| [[DAS Doc Design\|Doc]]+ | [[DAS MD\|MD]],  [[DAS Viz\|Viz]],  [[DAS IO\|IO]],  [[redline/SKILL\|Redline]],   |
| [[DAS Search Design\|Search]]+ | [[DAS Find\|Find]],  [[DAS Profile\|Profile]],  [[DAS Survey\|Survey]],  [[DAS Purchase\|Buy]],  [[DAS Book\|Book]],  [[DAS Corp\|Corp]],  [[DAS Person\|Person]],  [[DAS Product\|Product]],  [[DAS Software\|Software]],  [[DAS Meta Survey\|Meta Survey]],  [[DAS Research\|Research]],  [[DAS Research Skill\|Research Skill]],  [[DAS Search Overview\|Search Overview]],   |
| [[DAS Drive Design\|Drive]]+ | [[DAS Crank\|Crank]],  [[DAS Mint\|Mint]],  [[DAS Feature\|Feature]],  [[DAS Finalize\|Finalize]],  [[DAS Land\|Land]],  [[DAS Fortify\|Fortify]],  [[change/SKILL\|Change]],   |
| [[DAS Utility Design\|Utility]]+ | [[DAS Ctrl\|Ctrl]],  [[bridge/SKILL\|Bridge]],  [[DAS Exp\|Exp]],  [[screen/SKILL\|Screen]],  [[get-user-auth/SKILL\|Get User Auth]],  [[vox/SKILL\|Vox]],  [[muse/SKILL\|Muse]],  [[DAS Snip\|Snip]],  [[DAS Cook\|Cook]],  [[atlas/SKILL\|Atlas]],   |
| --- | |
| [[anchor/SKILL]] | Anchor operations — both a single anchor and the anchor system's machinery. Actions: /anchor scan (discover anchors), /anchor config (manage .anchor), /anchor status (activity tracking), /anchor docs-audit (docs vs source), /anchor install (one-time per-machine wiring of the CLI tools). Use when the user says: "scan for anchors", "anchor config", "install the anchor tools". |
| [[anchor-install]] | Install CAB command-line tools — make stat, cab-config, cab-scan, cab-audit available from any shell. Run once per machine. |
| [[anchor-system/SKILL]] | Internal helper — reads + writes the unified `~/.config/anchor-system/` namespace (per F080) for skill configuration, runtime state, and accumulated data. Not user-invocable; consumed by other skills via the `anchor-system config` / `anchor-system path` CLI. |
| [[Architect]] | SKA skill anchor for `/architect` |
| [[ask/SKILL]] | The system for NOT asking the user questions piecemeal. Prime directive: ELIMINATE every question the agent can (auto-resolve reversible/soon-visible guesses, run checks itself, decide low-stakes/visible calls, infer from the codebase), then CONSOLIDATE the irreducible residue into one self-documenting, counted, one-shot-answerable pile in the anchor's `{slug} queries.md` (sections Agent Resolutions / Verifications / Immediate Questions / Questions). The doc is the always-current STORE of open questions — write every question there the moment it is raised; chat is at most a VIEW, never carrying a question the doc lacks (the user runs many agents; chat scrolls away). Glance the doc and trim answered items. Use when the user runs /ask or an agent has a decision to route. Per F169 + [[Query PRD]]. |
| [[Audit]] | SKA skill anchor for `/audit` |
| [[brief-template]] |  |
| [[buy/SKILL]] | Given a known product (model + identifier), find verified buy locations across major retailers, drive a real browser via ctrl (NOT WebFetch / curl / Playwright — they're all bot-blocked by every major retailer's bot-wall), confirm each landing page is a real product page for the exact model the user wants, capture current price + buy-button presence + stock + promos, and recommend the best place to purchase with confidence. Retries per retailer when the first candidate URL is invalid; keeps the best verified page per company. Use when the user names a specific product to purchase: "what's the best price on the <X>", "where should I buy <X>", "buy <X>". Sibling of /find (identifies products) / /profile (profiles them) / /survey (compares them). v1: skeleton — fleshed-out section is § Page-validity verification and § Per-retailer retry loop; everything else is the obvious shape. |
| [[cab-migrate]] |  |
| [[code/SKILL]] | Development workflow skill — planning, architecture, implementation, testing, release, and orchestration. Use with an action argument: /code plan, /code architect, /code mint, /code test, /code release, etc. Key sub-skills: /code delegate (parallel work dispatch — "delegate this", "fan out"), /code spike (aggressive root cause — "spike that bug"), /code bugfix (red-green bug response), /code forge (rebuild+restart), /code rewire (structural repair), /code replan (requirements changed), /code ask-questions (resolve pending decisions), /code research (investigate landscape). When the user says "new feature", "spike that bug", "fix this bug", "forge it", "rewire this", invoke the corresponding /code action. |
| [[code-anchor]] |  |
| [[code-arch-audit]] |  |
| [[code-ask-questions]] |  |
| [[code-bugfix]] |  |
| [[code-changelog]] |  |
| [[code-code]] |  |
| [[code-delegate]] |  |
| [[code-execute]] |  |
| [[code-forge]] |  |
| [[code-ios]] |  |
| [[code-mac-gui]] | Drive a native macOS app via click/type/screenshot to reproduce bugs, verify behavior, and debug the UI. Use when user says: "mac gui", "debug the app", "eyeball it", "run it and see what happens", "test the UI", "click through", or references visual/UI issues (modal, button, screen, layout, window) in a Mac app. |
| [[code-merge]] |  |
| [[code-mint]] |  |
| [[code-modules]] |  |
| [[code-package]] |  |
| [[code-plan-audit]] |  |
| [[code-pr-flow]] |  |
| [[code-publish]] |  |
| [[code-release]] |  |
| [[code-replan]] |  |
| [[code-research]] |  |
| [[code/code-review]] |  |
| [[code-rewire]] |  |
| [[code-rewire.compiled]] |  |
| [[code-setup]] |  |
| [[code-ship]] |  |
| [[code-spec]] |  |
| [[code-spike]] |  |
| [[code-system-design]] |  |
| [[code-test]] |  |
| [[code-test-external]] |  |
| [[code-test-plan]] |  |
| [[code-test-quality]] |  |
| [[code-test-scaffolds]] |  |
| [[code-testing]] |  |
| [[code-verify]] |  |
| [[code-version]] |  |
| [[code-workers]] |  |
| [[code-worktrees]] |  |
| [[cook/SKILL]] | Recipe-aware shopping/staging list from Paprika |
| [[ctrl/SKILL]] | Local environment control — browser automation, persistent shell sessions, and system interaction. Subcommands: box, outbox, surf, search, navigate, shell. Most subcommands are mapped to trigger words in CLAUDE.md. |
| [[dupes/SKILL]] | Vault hygiene — scan for duplicate filenames; emit a confidence-ranked natural-language edit list; user instructs verbally, agent executes |
| [[excalidraw-examples]] |  |
| [[docs/EXP]] | 2026 Vast ML Testing — ML experiment suites (distillation, interpretability, LLM probing) run on vast.ai GPUs |
| [[EXP Backlog]] |  |
| [[docs/EXP Experiment Flow]] |  |
| [[docs/EXP Experiment Template]] |  |
| [[docs/EXP Master Flow]] |  |
| [[EXP Messages]] | agent inbox — system messages for this anchor; cleared on every pause. See [[DAS Messages]]. |
| [[docs/EXP Orchestrator Flow]] |  |
| [[exp/SKILL]] | Remote-experimentation toolkit — runs ML workloads on ephemeral GPU instances (vast.ai) via SSH + rsync + watcher daemon. Multi-remote, with named workers and a zap dispatch pattern. |
| [[docs/EXP Worker Instructions]] |  |
| [[docs/EXP Write Up Template]] |  |
| [[fix/SKILL]] | Fix common environment problems — permissions, auth, session config, workarounds. Use when the user says: "fix permissions", "fix auth", "reauth google", "fix the session", "clean up", "something's broken", "fix claude". |
| [[fix-claude-permissions]] |  |
| [[fix-claude-session]] |  |
| [[fix-google-reauth]] |  |
| [[fix-mac-finder-dotfiles]] |  |
| [[fix-mac-key-repeat]] |  |
| [[fix-mac-mail-delete-to-archive]] |  |
| [[fix-mac-sudo-nopassword]] |  |
| [[fix-mac-unsigned-apps]] |  |
| [[fix-obsidian-python-comments]] |  |
| [[google-sheets]] |  |
| [[google-slides]] |  |
| [[imgen/SKILL]] | Generated imagery — roll an image from a prompt into the [[IMGEN]] anchor, which keeps the prompt beside it. Sessions are numbered batches; `-t "{topic}"` opens a new one, no flag appends to the latest, `--dry-run` shows where a roll will land. Use when the user says "/imgen" or "really imgen". Authored diagrams are /viz. |
| [[io/SKILL]] | External system I/O — read from and write to external applications and services. Google Workspace: Sheets, Slides, Drive, Docs. Email via Apple Mail. Use when the user says: "put this in sheets", "read the spreadsheet", "update the slides", "upload to drive", "read my email", "search mail for", "find that email from". Subcommands: /io gsheet, /io gslide, /io gdoc, /io gdrive, /io email, /io notion. |
| [[io-email]] |  |
| [[io-email-access]] |  |
| [[io-excel]] |  |
| [[io-gdoc]] |  |
| [[io-gdrive]] |  |
| [[io-gsheet]] |  |
| [[io-gslide]] |  |
| [[io-notion]] |  |
| [[maintain/SKILL]] |  |
| [[md/SKILL]] | Markdown utility verbs — produce or maintain markdown artifacts: /md file-tree (format file trees), /md toc (regenerate tables of contents), /md dispatch-table (build dispatch pages), /md cards (build cheat / summary / detail cards), /md track-changes (inline diff HTML for edits). Bare /md glances the [[DAS markdown]] discipline rules. The format-rule content moved to [[DAS markdown]] 2026-06-10 — this skill keeps utility verbs only. |
| [[md-cards]] |  |
| [[md-dispatch-table]] |  |
| [[md-file-tree]] |  |
| [[md-toc]] |  |
| [[md-track-changes]] |  |
| [[migrate/SKILL]] | Change an anchor in place — slug, traits, structure, naming (relocation is /move's job), organization. Use when the user says: "migrate this", "rename the slug", "change the type", "move this project", "restructure this", "convert to code project", "reorganize", "rename", "change". |
| [[move/SKILL]] |  |
| [[MUSE]] | Voice-memo ingestion + review-and-do pipeline |
| [[parley/SKILL]] | Structured discussion — talk through a topic, capture decisions, track next steps. Use when the user says: "parley", "let's discuss", "let's talk about", "I want to think through", "let's figure out", "discuss this". |
| [[pilot-flow/SKILL]] |  |
| [[pr-flow/SKILL]] |  |
| [[publish/SKILL]] |  |
| [[rewire]] |  |
| [[SKILL-retired]] | > |
| [[slug-scan/SKILL]] |  |
| [[snip/SKILL]] | Capture rough text drops and iteratively refine them. Use when the user says `/snip <text>` (or the word "snip" gets auto-prefixed as `/snip` by the dictation pipeline). Three modes: (1) `/snip <text>` with no revise marker drops a new dated H2 entry with two versions stacked newest-on-top: `### version 1` (AI refinement) above `### version 0` (raw verbatim). (2) `/snip revise <instructions>` — or any args containing `snip <punct/ws> revise` somewhere — takes the current top version of the top entry, applies the instructions, and prepends the result as the next version. (3) Bare `/snip` re-refines the top version with a generic clean pass, prepending the next version. In every case the new top version is pbcopy'd to clipboard and the file is glanced. |
| [[status-doc-template]] |  |
| [[streams/SKILL]] | Content stream definitions — Stub skill — runbook to come. Manages content stream definitions for anchors. |
| [[template.docx]] |  |
| [[tidy/SKILL]] |  |
| [[viz/SKILL]] | Visual drafting — produce visual artifacts (charts, diagrams, mockups, slides). Use with an action argument: /viz excalidraw, /viz matplot. Triggered when user says "draw", "diagram", "mockup", "chart this", "plot data", "timeline chart", "excalidraw", or asks to create/update/export a visual artifact. |
| [[viz-d2]] |  |
| [[viz-diagram]] | Stated intent for `{base}.svg`. Maintained alongside the SVG by `/viz diagram`; rewritten as the user clarifies (never appended). |
| [[viz-docx]] |  |
| [[viz-dot]] |  |
| [[viz-excalidraw]] |  |
| [[viz-matplot]] |  |
| [[viz-mermaid]] |  |
| [[viz-pdf]] |  |
| [[viz-pptx]] |  |
| [[viz-svg]] |  |
