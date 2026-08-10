---
description: "Skills — the `/`-invocable runbooks"
---

# DAS Skills
The catalog of skills — the `/`-invocable runbooks — organized by the nine subsystems in [[DAS]] order.

![[F143-1-top-level.svg|2400]]
*Dan's Anchor System — the kinds of system parts: **Skills** (verbs) create **Facets** (nouns); **Disciplines** (adjectives) modify both; **Rulesets** constrain all three.*



| -[[DAS Skills]]- | : Skills — the `/`-invocable runbooks<br>→ [[DAS]] → [[SKL]] → [DAS Skills](hook://p/DAS%20Skills)  |
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
| [[anchor/SKILL]]  | Anchor operations — both a single anchor and the anchor system's machinery. Actions: /anchor scan (discover anchors), /anchor config (manage .anchor), /anchor status (activity tracking), /anchor docs-audit (docs vs source), /anchor install (one-time per-machine wiring of the CLI tools). Use when the user says: "scan for anchors", "anchor config", "install the anchor tools". |
| [[anchor-install]]  | Install CAB command-line tools — make stat, cab-config, cab-scan, cab-audit available from any shell. Run once per machine. |
| [[anchor-system/SKILL]]  | Internal helper — reads + writes the unified `~/.config/anchor-system/` namespace (per F080) for skill configuration, runtime state, and accumulated data. Not user-invocable; consumed by other skills via the `anchor-system config` / `anchor-system path` CLI. |
| [[Architect]]  | SKA skill anchor for `/architect` |
| [[ask/SKILL]]  | The system for NOT asking the user questions piecemeal. Prime directive: ELIMINATE every question the agent can (auto-resolve reversible/soon-visible guesses, run checks itself, decide low-stakes/visible calls, infer from the codebase), then CONSOLIDATE the irreducible residue into one self-documenting, counted, one-shot-answerable pile in the anchor's `{slug} queries.md` (sections Agent Resolutions / Verifications / Immediate Questions / Questions). The doc is the always-current STORE of open questions — write every question there the moment it is raised; chat is at most a VIEW, never carrying a question the doc lacks (the user runs many agents; chat scrolls away). Glance the doc and trim answered items. Use when the user runs /ask or an agent has a decision to route. Per F169 + [[Query PRD]]. |
| [[Audit]]  | SKA skill anchor for `/audit` |
| [[brief-template]]  |  |
| [[buy/SKILL]]  | Given a known product (model + identifier), find verified buy locations across major retailers, drive a real browser via ctrl (NOT WebFetch / curl / Playwright — they're all bot-blocked by every major retailer's bot-wall), confirm each landing page is a real product page for the exact model the user wants, capture current price + buy-button presence + stock + promos, and recommend the best place to purchase with confidence. Retries per retailer when the first candidate URL is invalid; keeps the best verified page per company. Use when the user names a specific product to purchase: "what's the best price on the {X}", "where should I buy {X}", "buy {X}". Sibling of /find (identifies products) / /profile (profiles them) / /survey (compares them). v1: skeleton — fleshed-out section is § Page-validity verification and § Per-retailer retry loop; everything else is the obvious shape. |
| [[cab-migrate]]  |  |
| [[code/SKILL]]  | Development workflow skill — planning, architecture, implementation, testing, release, and orchestration. Use with an action argument: /code plan, /code architect, /code mint, /code test, /code release, etc. Key sub-skills: /code delegate (parallel work dispatch — "delegate this", "fan out"), /code spike (aggressive root cause — "spike that bug"), /code bugfix (red-green bug response), /code forge (rebuild+restart), /code rewire (structural repair), /code replan (requirements changed), /code ask-questions (resolve pending decisions), /code research (investigate landscape). When the user says "new feature", "spike that bug", "fix this bug", "forge it", "rewire this", invoke the corresponding /code action. |
| [[code-anchor]]  |  |
| [[code-arch-audit]]  |  |
| [[code-ask-questions]]  |  |
| [[code-bugfix]]  |  |
| [[code-changelog]]  |  |
| [[code-code]]  |  |
| [[code-delegate]]  |  |
| [[code-execute]]  |  |
| [[code-forge]]  |  |
| [[code-ios]]  |  |
| [[code-mac-gui]]  | Drive a native macOS app via click/type/screenshot to reproduce bugs, verify behavior, and debug the UI. Use when user says: "mac gui", "debug the app", "eyeball it", "run it and see what happens", "test the UI", "click through", or references visual/UI issues (modal, button, screen, layout, window) in a Mac app. |
| [[code-merge]]  |  |
| [[code-mint]]  |  |
| [[code-modules]]  |  |
| [[code-package]]  |  |
| [[code-plan-audit]]  |  |
| [[code-pr-flow]]  |  |
| [[code-publish]]  |  |
| [[code-release]]  |  |
| [[code-replan]]  |  |
| [[code-research]]  |  |
| [[code/code-review]]  |  |
| [[code-rewire]]  |  |
| [[code-rewire.compiled]]  |  |
| [[code-setup]]  |  |
| [[code-ship]]  |  |
| [[code-spec]]  |  |
| [[code-spike]]  |  |
| [[code-system-design]]  |  |
| [[code-test]]  |  |
| [[code-test-external]]  |  |
| [[code-test-plan]]  |  |
| [[code-test-quality]]  |  |
| [[code-test-scaffolds]]  |  |
| [[code-testing]]  |  |
| [[code-verify]]  |  |
| [[code-version]]  |  |
| [[code-workers]]  |  |
| [[code-worktrees]]  |  |
| [[cook/SKILL]]  | Recipe-aware shopping/staging list from Paprika |
| [[CRAFT]]  |  |
| [[ctrl/SKILL]]  | Local environment control — browser automation, persistent shell sessions, and system interaction. Subcommands: box, outbox, surf, search, navigate, shell. Most subcommands are mapped to trigger words in CLAUDE.md. |
| [[daybreak/SKILL]]  | Morning routine — the day's opening sequence. Run each morning to set up what the day looks like. Use when the user says "daybreak", "/daybreak", or asks to start the day. |
| [[disk/SKILL]]  | Reconcile a mirror drive (10T / 8T / BLACK) against its catalog, in both directions, plus two capacity questions. Use when the user says "check the drive for stray files", "does the drive match the catalog", "is there anything unexpected on 8T", "will BLACK still hold the master if we resync", "what would a refresh actually copy/delete", "reconcile 10T against the catalog". Not a hash checker — pairs with the existing three-drive SHA-256 verify system, doesn't replace it. |
| [[Drawing Wisdom]]  | Accumulated judgment about drawing pictures — when a figure earns its place, what makes one readable, and the mistakes that keep recurring. The companion to the `viz` skill's mechanical instruction. |
| [[dupes/SKILL]]  | Vault hygiene — scan for duplicate filenames; emit a confidence-ranked natural-language edit list; user instructs verbally, agent executes |
| [[excalidraw-examples]]  |  |
| [[docs/EXP]]  | **Remote compute** — ephemeral GPU instances via SSH + rsync + watcher (not yet under the SKA prefix). |
| [[EXP Backlog]]  |  |
| [[docs/EXP Experiment Flow]]  |  |
| [[docs/EXP Experiment Template]]  |  |
| [[docs/EXP Master Flow]]  |  |
| [[EXP Messages]]  | agent inbox — background-process messages for this anchor; append-only. See [[DAS Messages]]. |
| [[docs/EXP Orchestrator Flow]]  |  |
| [[exp/SKILL]]  | Remote-experimentation toolkit — runs ML workloads on ephemeral GPU instances (vast.ai) via SSH + rsync + watcher daemon. Multi-remote, with named workers and a zap dispatch pattern. |
| [[docs/EXP Worker Instructions]]  |  |
| [[docs/EXP Write Up Template]]  |  |
| [[fix/SKILL]]  | Fix common environment problems — permissions, auth, session config, workarounds. Use when the user says: "fix permissions", "fix auth", "reauth google", "fix the session", "clean up", "something's broken", "fix claude". |
| [[fix-claude-permissions]]  |  |
| [[fix-claude-session]]  |  |
| [[fix-google-reauth]]  |  |
| [[fix-mac-finder-dotfiles]]  |  |
| [[fix-mac-key-repeat]]  |  |
| [[fix-mac-mail-delete-to-archive]]  |  |
| [[fix-mac-sudo-nopassword]]  |  |
| [[fix-mac-unsigned-apps]]  |  |
| [[fix-obsidian-python-comments]]  |  |
| [[google-sheets]]  |  |
| [[google-slides]]  |  |
| [[imgen/SKILL]]  | Generate and edit images into the IMGEN anchor — each sitting is a numbered roll whose page carries one pending "Next render" plus every batch it has already produced, prompt recorded beside the images it made. Text-to-image (flux-dev) and instruction editing (flux-kontext) are wired; visible per-call cost; a pick pins the keeper. Use when the user says "/imgen", "really imgen", or asks for a picture to be generated or edited. Not for authored diagrams — that is /viz. |
| [[inbox/SKILL]]  | Drains the current anchor's [[DAS Inbox]] — reads every PENDING entry (raw input dropped in by another agent or the user via `state drop`), integrates each one into the right planning surface (Backlog, PRD, Roadmap, Discussion, or handled in place), and marks it processed with the sanctioned status tag (`DONE` or `MOVED → {destination}`) via `state inbox-tag`. Never hand-edits the Inbox markdown directly. Use when the user says "/inbox", "drain the inbox", "check the inbox", "process the inbox", or when the status banner shows `Inbox N` with N > 0. T131 leg 3 — the drain half of the agent-inbox pattern (leg 1: `state drop`; leg 2: the `Inbox N` banner signal). |
| [[io/SKILL]]  | External system I/O — read from and write to external applications and services. Google Workspace: Sheets, Slides, Drive, Docs. Apple: Mail, Calendar, Health. Use when the user says: "put this in sheets", "read the spreadsheet", "update the slides", "upload to drive", "read my email", "search mail for", "find that email from", "what's on my calendar", "read my calendar", "what do I have today", "pull my health data", "what's my sleep/heart rate", "check my apple health". Subcommands: /io gsheet, /io gslide, /io gdoc, /io gdrive, /io imail, /io ical, /io ihealth, /io notion. |
| [[io-excel]]  |  |
| [[io-gdoc]]  |  |
| [[io-gdrive]]  |  |
| [[io-gsheet]]  |  |
| [[io-gslide]]  |  |
| [[io-ical]]  |  |
| [[io-ical-access]]  |  |
| [[io-ihealth]]  |  |
| [[io-imail]]  |  |
| [[io-imail-access]]  |  |
| [[io-notion]]  |  |
| [[maintain/SKILL]]  |  |
| [[md/SKILL]]  | Markdown utility verbs — produce or maintain markdown artifacts: /md file-tree (format file trees), /md toc (regenerate tables of contents), /md dispatch-table (build dispatch pages), /md cards (build cheat / summary / detail cards), /md track-changes (inline diff HTML for edits). Bare /md glances the [[DAS markdown]] discipline rules. The format-rule content moved to [[DAS markdown]] 2026-06-10 — this skill keeps utility verbs only. |
| [[md-cards]]  |  |
| [[md-dispatch-table]]  |  |
| [[md-file-tree]]  |  |
| [[md-toc]]  |  |
| [[md-track-changes]]  |  |
| [[migrate/SKILL]]  | Change an anchor in place — slug, traits, structure, naming (relocation is /move's job), organization. Use when the user says: "migrate this", "rename the slug", "change the type", "move this project", "restructure this", "convert to code project", "reorganize", "rename", "change". |
| [[move/SKILL]]  |  |
| [[MUSE]]  | Voice-memo ingestion + review-and-do pipeline |
| [[parley/SKILL]]  | Structured discussion — talk through a topic, capture decisions, track next steps. Use when the user says: "parley", "let's discuss", "let's talk about", "I want to think through", "let's figure out", "discuss this". |
| [[pilot-flow/SKILL]]  |  |
| [[pr-flow/SKILL]]  |  |
| [[publish/SKILL]]  |  |
| [[rewire]]  |  |
| [[SKA Bridge Testing]]  | SKA Bridge Testing — strategy + proposed-tests overview |
| [[SKILL-retired]]  | > |
| [[SKL]]  | the skills pillar — every Claude Code skill, one folder per skill with a SKILL.md entry point |
| [[slug-scan/SKILL]]  |  |
| [[snip/SKILL]]  | Capture rough text drops and iteratively refine them. Use when the user says `/snip <text>` (or the word "snip" gets auto-prefixed as `/snip` by the dictation pipeline). Three modes: (1) `/snip <text>` with no revise marker drops a new dated H2 entry with two versions stacked newest-on-top: `### version 1` (AI refinement) above `### version 0` (raw verbatim). (2) `/snip revise <instructions>` — or any args containing `snip <punct/ws> revise` somewhere — takes the current top version of the top entry, applies the instructions, and prepends the result as the next version. (3) Bare `/snip` re-refines the top version with a generic clean pass, prepending the next version. In every case the new top version is pbcopy'd to clipboard and the file is glanced. |
| [[status-doc-template]]  |  |
| [[streams/SKILL]]  | Content stream definitions — Stub skill — runbook to come. Manages content stream definitions for anchors. |
| [[template.docx]]  |  |
| [[tidy/SKILL]]  |  |
| [[viz/SKILL]]  | Visual drafting — produce visual artifacts (charts, diagrams, mockups, slides). Use with an action argument: /viz excalidraw, /viz matplot. Triggered when user says "draw", "diagram", "mockup", "chart this", "plot data", "timeline chart", "excalidraw", or asks to create/update/export a visual artifact. |
| [[viz-d2]]  |  |
| [[viz-diagram]]  | Stated intent for `{base}.svg`. Maintained alongside the SVG by `/viz diagram`; rewritten as the user clarifies (never appended). |
| [[viz-docx]]  |  |
| [[viz-dot]]  |  |
| [[viz-excalidraw]]  |  |
| [[viz-matplot]]  |  |
| [[viz-mermaid]]  |  |
| [[viz-pdf]]  |  |
| [[viz-pptx]]  |  |
| [[viz-svg]]  |  |
| [[io-calendar]]  |  |
| [[io-calendar-access]]  |  |
| [[io-email]]  |  |
| [[io-email-access]]  |  |
