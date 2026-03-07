# Planning Workflow

The full planning flow from idea to implementation-ready roadmap. Execute these steps in order for new systems; revisit selectively during `/dev replan`.

**Planning Pipeline**
1. [[#1. PRD|PRD]]
2. [[#2. UX Design|UX Design]]
3. [[#3. System Design|System Design]]
4. [[#4. Files + Module Docs|Files + Module Docs]]
5. [[#5. Roadmap|Roadmap]]
6. [[#6. Document|Document]]

✦ [[#Open Questions]] — parallel to the pipeline, not a step in it
✦ [[#Planning Backlog]] — autonomous work the agent can do without user input
✦ [[#Planning Levels]] — light, standard, or deep. Standard is the default.
✦ [[#Planning Modes]] — interactive (default), complete (autonomous), or exhaustive (full cleanup)

## Planning Pipeline Steps

### 1. PRD

Capture what the system is, what it does, and why. Create [[CAB PRD|{NAME} PRD.md]] following that spec.

- **Overview** — what it does and why it needs to exist (two sentences)
- **Goals** — concrete, verifiable outcomes; explicit non-goals
- **User Stories** — numbered (US-1, US-2, ...), each with enough detail that a worker could build against it
- **Design Constraints** — numbered (DC-1, DC-2, ...), each with rule AND reasoning
- **Prior Art** — existing tools, patterns, codebases to draw from or avoid

**Fleshing out guidance:**
- Can you explain what this does and why in two sentences? If not, Overview isn't clear.
- What's the smallest version that would be useful? Start there.
- For every goal, ask: what would I cut with half the time? That reveals core vs. nice-to-have.
- Have you covered every role that interacts with the system — not just primary users?
- Could a worker read each story and start building without coming back to ask? If not, add detail.
- Do stories cover the full lifecycle — setup, daily use, error recovery, maintenance?
- For each constraint, have you explained reasoning, not just the rule?

### 2. UX Design

Design the user-facing experience. Create [[CAB UX Design|{NAME} UX Design.md]] following that spec.

- Screens and navigation flows
- Interaction model (keyboard, text/voice, mouse tiers)
- Commands, menus, and shortcuts
- System concepts — the shared vocabulary for users, agents, and docs
- Mockups (ASCII or linked)

Specification only — current design, not history. Rationale belongs in [[CAB Design Discussions|Design Discussions]].

### 3. System Design

Design the technical architecture. Create [[CAB System Design|{NAME} System Design.md]] following that spec.

- Component boundaries and data flow
- Module decomposition with responsibilities
- APIs and protocols
- Data models and storage
- Infrastructure decisions
- Monitoring, failure handling, and configuration tiers
- Key design decisions with rationale in a Decisions section

Specification only — current design, not history.

### 4. Files + Module Docs

Build the file tree and module docs together — they reference each other.

**Files document:** List every file with one-line descriptions. Create [[CAB Files|{NAME} Files.md]] following that spec.

**IMPORTANT:** The Files page is a monospace page (`cssclasses: monospace`), NOT a code block. Read the [[CAB Files]] spec before creating or updating — it defines the exact format: frontmatter, box-drawing tree, aligned descriptions, and wiki-links to module docs.

**Module docs:** For each module in the Files doc, create a [[CAB Module Doc|module doc]] following that spec. Module docs live under `{NAME} Dev/` in a subfolder structure mirroring the source tree (see [[CAB Module Doc]] for location rules and format). Link each module doc from the Files tree using `→ [[doc name]]` on the directory or file line.

Read the [[CAB Module Doc]] spec before writing — it defines the structured format: breadcrumb, brief, properties table, methods table, discussion, method details, protocol, see also.

**Planning vs implemented:** During planning, module docs describe the *proposed* API. Mark every property, method, class, and struct description with **(proposed)** inline to indicate the code does not yet reflect this. As implementation proceeds, remove **(proposed)** from each item once it matches the code. This makes module docs the living spec — during planning they show what will be built, during execution they converge toward what exists.

**Module doc structure for planning:**
- **Module summary table** — if the module contains more than 3 classes/structs, start with a table listing all types in the module (name + one-line description). This orients readers before the detailed sections.
- **Per-class sections** — each class/struct gets: brief description, properties table, methods table
- **Module-level functions** — listed after the class sections
- The informal prose from Plan/ module descriptions provides the content; the Dev/ module docs give it structured form

### 5. Roadmap

Build the ordered implementation plan. Create [[CAB Roadmap|{NAME} Roadmap.md]] following that spec.

- Break work into milestones ordered by dependency (foundational first)
- Each milestone has clear acceptance criteria
- Identify which milestones can be parallelized
- The roadmap is the work queue for `/dev execute`

#### Roadmap Validation

After writing or updating the roadmap, validate it:

1. **Check task order** — are tasks in logical order? Do prerequisites come first? Are there dependency conflicts that should reorder items?
2. **Check for missing work** — scan Notes, Todo, and Backlog documents for work discussed but not reflected in the roadmap. Add any missing items.
3. **Surface open questions** — check `{NAME} Backlog.md`, `{NAME} Open Questions.md`, and other docs for unresolved questions. Each should either block a milestone or be deferred.
4. **Run validation script** — if `roadmap_check.py` is available:
   ```bash
   python ~/ob/kmr/prj/personal-curation/roadmap_check.py "{NAME} Roadmap.md"
   ```
   Fix any reported errors (missing checkboxes, deferred items without references, invalid format).

### 6. Document

Create the documentation dispatch tree — placeholder pages that link the anchor's top-level folder file down through every documentation page. The goal: starting from `{NAME}.md` or `{NAME} Docs.md`, a reader can reach any markdown file by following links.

**Dispatch tree structure:**
1. **Docs dispatch page** (`{NAME} Docs.md`) — links to all doc areas: Plan, Dev, User, Design
2. **Dev dispatch page** (`{NAME} Dev.md` inside the Dev folder) — links to all module aggregator pages
3. **Module aggregator pages** (e.g., `{NAME} App.md`) — links to individual class/struct docs
4. **Individual docs** — leaf pages with breadcrumb back to their aggregator

**Breadcrumbs:** Every page below the dispatch level starts with a breadcrumb line: ` [[parent page]] → This Page`. This creates upward navigation.

**Verification:** Walk the link tree from the anchor page. Every `.md` file in the Docs folder should be reachable. If a page is unreachable, either add a link from its parent or create a missing dispatch page.

**Timing:** Run this step after the Roadmap (or after implementation if docs were created during execution). The Document step ensures the full tree is navigable — it catches orphaned pages that were created during implementation but never linked.


## Open Questions

Questions live in [[CAB Open Questions|{NAME} Open Questions.md]], organized by urgency level.

### Capturing

As the agent works through the pipeline, it captures questions into the Open Questions file and tags each by urgency:
- **Urgent** — ready to plan now and many downstream decisions depend on the answer
- **Soon** — will become urgent as the pipeline advances
- **Deferred** — safe to decide later; no near-term downstream impact

### Raising Urgent Questions

When an urgent question accumulates, the agent opens the Open Questions file and presents the top question explicitly to the user — stating the alternatives, what depends on the answer, and what to consider. Discussion proceeds immediately.

Occasionally the agent should mention the count of **soon** questions available, especially once the count exceeds five or so, to let the user know batch resolution is available.

### Batch Resolution

The user initiates batch question-answering when ready. The agent opens the Open Questions file and presents questions one at a time with alternatives and trade-offs. After each answer, the agent cascades the decision back into the affected pipeline documents.

### Recording Discussions

When a question or batch of questions involves notable back-and-forth — exploring trade-offs, comparing approaches, or changing direction — create a new dated section in [[CAB Design Discussions|{NAME} Design Discussions.md]] to document the reasoning. The design docs themselves stay specification-only; the discussion log captures the "why."


## Planning Backlog

Planning backlog items live in the **Legwork** section of the project's `{NAME} Backlog.md`. These are tasks the agent can work through mostly autonomously — if a task needs user input, it belongs in Open Questions instead.

During implementation, legwork items are pulled as Priority 1 Tier 2 work in `/dev execute`. During planning, they are worked after the pipeline steps complete.

### What qualifies

Work that advances the planning documents without requiring user approval for each step:

- Fleshing out incomplete sections in pipeline documents
- Running consistency passes and fixing contradictions
- Writing or updating module descriptions
- Running tests or validation scripts (including tests that involve the user, as long as they're non-destructive)
- Updating test code to match design changes
- Researching prior art or technical feasibility

### What does NOT qualify

- Changing core application code
- Making architectural decisions that haven't been discussed
- Anything dangerous or irreversible
- Work that requires a design choice — that's an Open Question

### When to work the backlog

The agent completes all primary planning pipeline work first. Once the pipeline steps are done and no urgent open questions remain, the agent works through backlog items before declaring planning complete. Backlog items discovered during the pipeline are captured immediately but executed later.




## Planning Levels

Three levels control the depth of each pipeline step. Standard is the default; the user can request light or deep at any time.

### Light

Abbreviated pass through each step. Produce short-form versions of each document — enough to establish direction, not enough for a worker to build from. Useful for early exploration or small features.

- PRD: overview + goals only, skip user stories and constraints
- UX: key screens or commands only, skip detailed flows
- System Design: component list and data flow only, skip detailed APIs
- Files/Modules: flat file list with one-line descriptions, skip module docs
- Roadmap: ordered task list without formal milestones or acceptance criteria

### Standard

The default. Work through each step fully, filling in all sections in order. Each document should be complete enough that a worker could build from it without blocking questions.

### Deep

Each step is completed with explicit verification of completeness and cross-document consistency. After finishing each step:

- Verify every section in the document is populated — no placeholders or TBDs left
- Cross-check against earlier documents for terminology consistency and contradictions
- Confirm all open questions surfaced by this step are captured and tagged
- Run the consistency pass (PRD stories traced through UX and System Design) before advancing


## Planning Modes
Two modes control how the agent interacts with the user during planning. Interactive is the default.

### Interactive Mode
The default. The agent works through the pipeline step by step, explaining what it's doing, raising urgent questions immediately, and pausing for input at natural decision points. Use this when the user is at the console and wants to collaborate on the design.

### Complete Mode
The agent makes maximum autonomous progress without pausing for input. Useful when the user is stepping away and wants the planning to advance as far as possible.

In complete mode:
- Tag all questions as **Deferred** instead of raising them — capture them in Open Questions for later
- Work through every pipeline step that doesn't require a user decision
- Run consistency passes and fix what you can
- Work through the entire planning backlog
- Stop only when no further progress is possible without user input

The agent exits complete mode when it runs out of autonomous work. On the next interaction, it reports what was accomplished, what questions accumulated, and where the pipeline stands.

The user can switch modes at any time — say "complete planning" to enter complete mode, or just resume interactive conversation to return to interactive mode.

### Exhaustive Mode

Everything in complete mode, plus additional passes that go beyond forward planning into cleanup, legacy removal, and pre-speccing. Use when the user wants the planning phase to be truly finished — no loose ends, no deferred housekeeping.

In exhaustive mode, after completing all complete-mode work:

- **Legacy scan** — search for old patterns, deprecated formats, and superseded approaches. For non-user-facing internals, make the changes to migrate to current patterns. For user-facing capabilities, raise an Open Question about when to drop legacy support (this may be answered in the PRD or by the user).
- **Re-document** — verify all documentation is complete, consistent, and linked properly. Every doc matches its CAB part spec. Cross-references are valid. The dispatch tree is navigable from the anchor page to every document. Nothing is stale or orphaned.
- **Worker spec pass** — write implementation specs for every roadmap item whose dependencies are already clear. Some items depend on earlier implementation and can't be fully specced yet — skip those. The goal is to pre-spec as many milestones as possible so workers can be dispatched immediately when execution begins.
- **Final consistency sweep** — one last pass across all documents checking for contradictions, terminology drift, and gaps introduced by the exhaustive work itself.




After steps 1–3, run consistency checks:

- Trace every PRD user story through UX Design and System Design — is every capability designed and architecturally supported?
- Check terminology — same words for same concepts across all documents?
- Check for contradictions — does any document promise something another can't deliver?
- Are all open questions captured? Are any blocking?

Multiple passes are normal. Each pass tightens the design.

**Cascade rule:** Updating any document may invalidate others. When a decision changes the UX, check System Design. When a constraint changes in the PRD, check both UX and System Design.

## Sufficiency Check

Before moving to implementation, verify:

- Could a worker start building from these documents without blocking questions?
- Do goals, stories, and constraints tell a consistent story?
- Is there a clear first milestone?
- Open questions are empty or all remaining are TBD/deferred
- User has reviewed and approved the design

## Completion

The planning phase is complete when:
1. All 6 pipeline steps are complete and documents are internally consistent
2. Open questions are resolved or deferred
3. User has approved the design (file tree, module specs, API overviews, mockups)
4. The roadmap has a clear first milestone ready for implementation
5. The documentation dispatch tree is navigable from the anchor page to every doc

Transition to `/dev execute` when the roadmap is ready.
