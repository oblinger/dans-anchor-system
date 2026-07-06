---
description: "F218 propose-tier deliverable — the mined design-rules catalog, drafted as PROPOSED rulesets awaiting user upgrade. Nothing here is live: the `PROPOSED` prefix keeps every block invisible to the warden scan until upgraded."
---

# [[Warden]] · Design-Rules Catalog Proposal

The [[F218 — Design-rules catalog — ship with skills, adopt per-application|F218]] mining pass, presented as one reviewable package (per Q2: agent proposes, user reviews and upgrades — nothing is auto-created or auto-adopted). Six corpora were mined in parallel: **HA** (`prj/Hook Anchor/`), **SVP** (`SV/ww/svar-docs/sv-pipe/SVP Docs/`), **MUX** (`prj/ClaudiMux/MuxUX/`), **A2X** (`SV/ww/svar-docs/alg2-experimental/A2X/`), **SKD** (`prj/ClaudiMux/Skill Docket App/`), **SVAR** (`SV/ww/svar-docs/SVAR Design/`). A family enters this proposal only when it recurs across **≥3 projects** (or was named in the F108 commissioning message). Each block below is a draft ruleset in the exact live format — headed `PROPOSED RULESET`, which the warden scan's `# RULESET` sentinel does not match, so none of this compiles into the corpus until upgraded.

**Upgrade mechanics.** To adopt a family, say so (e.g. "upgrade R-single-source-of-truth" or "upgrade all"). The agent then: (1) strips `PROPOSED ` from the heading and moves the block to its proposed home under `library/Rulesets/`, (2) adds the catalog stub row in [[Rulesets]] and the `include::` in its umbrella ([[R-arch]] / [[R-process]] already name several of these as awaited children), (3) recompiles the warden corpus. **Adoption stays per-application**: an upgraded ruleset fires for an app only when that app's `.anchor` takes the trait — upgrade puts the rule on the shelf; each app still opts in.

**What the mining did NOT re-propose.** The live [[R-ob]] umbrella already covers three families this scan re-confirmed everywhere: state/config through the data singleton + no hardcoded config values ([[R-ob-state-mgt]], seen in HA "Oblinger's Rules" + MUX audits), no silent fallbacks + OS-bridge logging ([[R-ob-observability]], seen as HA P05/P08 + MUX no-silent-fallbacks), and the dispatcher pattern ([[R-ob-cmd-proc]], seen as MUX single-dispatcher + HA command-queue + SKD event routing). Those are catalog successes — already shipped; the recurrence evidence simply validates them.

## PROPOSED RULESET R-single-source-of-truth
description:: Every canonical datum — a config value, a state field, a type definition, a compiled binary, a spec — lives in exactly one physical location; every other reference is a pointer, include, or explicitly-labeled derived mirror. Proposed home: `Rulesets/R-arch/` (named there as an awaited child).

Recurs in 6/6 corpora — the single strongest signal in the scan. HA P04: "exists in exactly one physical location. Other references to it are symlinks, pointers, or lock-free snapshot reads. Manual duplication is forbidden" (`HA Track/HA Rules.md`). MUX: "Rust definitions … are canonical; TypeScript mirrors … are hand-maintained shadows. Keep them in sync" (`MUX Design/MUX Architecture/MUX-Data.md`). SVP: "duplicating it as a docs folder would split the source of truth" (F006). SKD: "the central registry is a cache, not a separate source of truth." SVAR: "per-subsystem PRDs link back here rather than duplicating it" (SVAR PRD). Global CLAUDE.md: "NEVER maintain multiple copies of the same code file."

### RULE R-single-source-of-truth-01 — One physical home per canonical datum (sampled)

Any canonical piece of information exists in exactly one physical location. Other references are links, includes, symlinks, or reads of the canonical copy — never a second hand-maintained instance. **Check pattern:** for a sampled datum (a type, a config default, a documented contract), search for its definition; more than one authoritative-looking definition is a violation.

### RULE R-single-source-of-truth-02 — Mirrors are labeled derived and have a sync story (sampled)

Where a mirror is genuinely required (cross-language type shadows, generated artifacts, dashboards), the mirror is explicitly labeled as derived, names its canonical source, and has a stated sync mechanism (generator, sync script, or a keep-in-sync note at both ends). An unlabeled copy is a second source of truth waiting to diverge.

### RULE R-single-source-of-truth-03 — Shared standards have one canonical home; never fork locally (stated)

When a project touches a standard shared across the vault (a doc format, an anchor convention, a ruleset), it links the canonical home rather than re-implementing or copying it locally. MUX states it directly: "there is ONE canonical home — do not fork anchor logic or docs locally."

## PROPOSED RULESET R-one-path
description:: For each operation there is exactly one current implementation path; superseded code is deleted, never parallel-maintained. Proposed home: `Rulesets/R-arch/`.

Recurs in HA + MUX + the global CLAUDE.md (no-legacy-accumulation). HA P06: "When a better approach replaces an older one, the older one is deleted entirely — not kept 'just in case,' not wrapped with a feature flag, not aliased for backward compatibility." MUX Multi-Path Audit: "`cmd_layout_load()` and `cmd_layout_apply()` are functionally identical … if a bug is fixed in one, the other will be missed."

### RULE R-one-path-01 — Exactly one current implementation path per operation (sampled)

For a sampled operation, trace how it can be invoked end-to-end. Two live code paths producing the same effect (old + new, flagged variants, aliased entry points kept for back-compat) is a violation: consolidate onto one and delete the other.

### RULE R-one-path-02 — Replaced code is deleted, not deprecated-in-place (checked)

**Check pattern:** search for `deprecated`, `legacy`, `_old`, `_v2`, `# TODO: remove`, dead feature flags. Each hit is a violation unless it carries a dated removal plan; "kept just in case" is not a justification — git history is the just-in-case.

### RULE R-one-path-03 — Near-duplicate logic consolidates behind one helper (sampled)

Two functions whose bodies differ only in a parameterizable detail merge into one shared helper. The test is the bug-fix test: if fixing a bug in one would require remembering to fix the other, they are one function written twice.

## PROPOSED RULESET R-interfaces-folder
description:: All abstract contracts live in a single `Interfaces` package per system; business code depends on interfaces, never concretes. Proposed home: `Rulesets/R-arch/` (named there as an awaited child). F108 commissioning seed.

Commissioned in F108 ("every system has a single `Interfaces/` folder") and canonical in SVP F006: "all abstract contracts (the 'what') live in a single **`Interfaces`** package; concrete instances are **never constructed directly**." The doc-side of the same instinct recurs as the human-authored layer-contract: HA `HA Design/HA Interface.md` ("What's Hidden — Callers above the HA layer do not need to know…"), SVP `SVP Interface.md` ("Public Surface / Guarantees + Non-Guarantees / Stability Tier"), MUX `MUX Interface.md`.

### RULE R-interfaces-folder-01 — One `Interfaces` package holds all abstract contracts (checked)

**Check pattern:** list the system's interface/trait/protocol definitions. Pass if they live in a single `interfaces/` package (human name `Interfaces`, lowercase directory per language convention); interface definitions scattered across module folders are violations.

### RULE R-interfaces-folder-02 — Business code depends on interfaces, not concretes (sampled)

For a sampled call site outside construction code, the referenced type is the interface, not the implementing class. Concrete types are named only in factories and the pegboard registration.

### RULE R-interfaces-folder-03 — Every code anchor carries a human-authored layer-contract doc (stated)

The anchor has a top-level `{NAME} Interface`-style doc naming the caller of record, the public surface, explicit Guarantees vs Non-Guarantees, and a What's-Hidden section listing internals callers must NOT depend on. (Complements the [[FCT API Design|R-api]] facet ruleset, which governs the doc's format; this rule requires its existence.)

## PROPOSED RULESET R-factory-pegboard
description:: Instances are created through factories registered on a per-subsystem pegboard, so the architecture's wiring is visible in one place. Proposed home: `Rulesets/R-arch/` (named there as an awaited child, "per F108"). F108 commissioning seed.

Commissioned in F108 and canonical in SVP F006: "concrete instances are **never constructed directly** — they're built by **factories**, which are registered on a **pegboard** (a per-subsystem registry) … Swapping an implementation … is a pegboard registration, not a code edit at the call site." SKD instantiates the same shape: "Sys is the pegboard — every module and subsystem hangs off it" (`SKD Track/SKD System Design.md`).

### RULE R-factory-pegboard-01 — Business code never constructs concretes directly (sampled)

Object instances are created through factory functions. **Check pattern:** for a sampled concrete class, search for direct constructor calls outside its factory and tests; each is a violation.

### RULE R-factory-pegboard-02 — Factories register on a per-subsystem pegboard (checked)

**Check pattern:** the subsystem has a central registry module where each architectural piece registers its factory; a factory reachable only by direct import from a call site is unregistered wiring.

### RULE R-factory-pegboard-03 — Swaps are registrations, not call-site edits (stated)

Substituting an implementation (real vs mock, backend A vs B) is a pegboard registration change. If a swap requires touching call sites, the wiring has leaked out of the pegboard.

## PROPOSED RULESET R-ownership
description:: Every mutable resource has exactly one owner; invariants are made true by construction rather than defended at runtime. Proposed home: `Rulesets/R-arch/`.

Recurs in MUX + HA + SKD. MUX: "Buffer Manager owns the text view; nobody else modifies it directly" (`CLAUDE.md`) and "no runtime mutex is needed, because no other path can produce a second brain" (MUX Decisions). SKD: "SKD is the sole authority for updating task status … Agents never edit the roadmap directly." HA: "every module belongs to exactly one subsystem … enforced by architect" (`HA Design/HA Architecture/HA Architecture.md`).

### RULE R-ownership-01 — One owner-writer per mutable resource (sampled)

Each mutable resource (a file, a state object, a UI region, a doc) has exactly one owning component; every other component reads through the owner or requests changes from it. **Check pattern:** for a sampled resource, search for write sites; writes outside the owner are violations.

### RULE R-ownership-02 — Structural guarantees over runtime discipline (stated)

When a property must hold ("exactly one X", "only Y touches Z"), prefer making it true by construction — a single spawner, a monopoly on the constructor, hardcoded routing — over defending it with runtime mutexes, guards, or conventions. A guard defends against a threat; a structure removes it.

### RULE R-ownership-03 — Every module belongs to exactly one subsystem (checked)

**Check pattern:** the architecture doc's subsystem→module map covers every source module exactly once; orphans and double-assignments are violations.

## PROPOSED RULESET R-design-gate
description:: Explicit user sign-off gates sit between design and dependent construction — contracts freeze before dependent code, design signs off before test construction, decisions are ratified before they are policy. Proposed home: `Rulesets/R-process/`. F108 commissioning seed ("design sign-off gate", SVP M15 canonical).

Recurs in SVP + SKD + MUX + HA. SVP M15 (canonical): "Before any test cases are constructed, all of the design documentation and the skeleton source code must be lined up and **presented to the user for approval**. This is a hard gate" (`SVP Track/SVP Roadmap/SVP Milestones.md`). SKD: "Everything gets fully specified before implementation begins" + the Sufficiency Analysis gate. MUX: decisions are "`(open)` … under design / not yet ratified" until user-`checked`. HA: the publish gate — "a fresh `/audit publish` pass MUST run and surface ZERO high-severity findings" (`HA Design/HA PRD.md`).

### RULE R-design-gate-01 — Design sign-off before test construction (stated)

A milestone gate sits between "design docs + skeleton code complete" and "test cases constructed": the package is walked through with the user as one reviewable unit, and test construction is blocked until explicit sign-off. Tests written against an unfrozen design train churn, not correctness.

### RULE R-design-gate-02 — Contracts freeze before dependent code (stated)

Shared data contracts and interfaces are agreed and stamped with an explicit stability tier ("freezes at M-n sign-off") before code that depends on them is written; until the freeze point, breaking changes are expected without notice — and after it, they are events.

### RULE R-design-gate-03 — Decisions are ratified before they are policy (stated)

A recorded design decision carries a status (`open` → user-`checked`); it is not in force as policy until ratified. Status tracks the decision itself, separate from its implementation.

### RULE R-design-gate-04 — Releases gate on a clean audit (stated)

Public releases require a fresh audit pass with zero high-severity findings, and the gate is written into the PRD itself so no release plan can omit it.

## PROPOSED RULESET R-stable-ids
description:: Numbered identifiers are permanent handles — monotonic-forever, never recycled, gap-numbered where ordered, zero-padded where sorted. Proposed home: `Rulesets/R-process/`.

Recurs in A2X + MUX + HA + SVAR + SVP (and the vault's own F-number convention). A2X: "D-numbers persist (never recycled) … X-numbers are monotonic across all task types." MUX: "D-numbers are not recycled (monotonic-forever) … The D-number is the stable handle — title text may evolve; the link stays valid." HA: "Principles: P01, P02, … never change once assigned." SVP/SVAR: "Milestones use **gap numbering** (M10, M20, M30 …) so insertions don't force renumbering … same convention as SVAR's roadmap."

### RULE R-stable-ids-01 — IDs are monotonic-forever, never recycled (checked)

Numbered entity IDs (F-, D-, Q-, X-, EX-, P-numbers) increase monotonically and are never reused, even after the entity is deleted or retired. **Check pattern:** the next-available counter only ever grows; a reused number is a violation.

### RULE R-stable-ids-02 — The number is the stable handle; titles may evolve (stated)

Links and references cite the ID, and the ID never changes once assigned — so every historical reference stays valid while the human-readable title is free to improve.

### RULE R-stable-ids-03 — Ordered sequences use gap numbering (stated)

Sequences with meaningful order (milestones) number with gaps (M10, M20, M30) so insertions (M15) never force a global renumber. Each numbered item also carries a short name usable interchangeably with its number.

### RULE R-stable-ids-04 — Zero-pad where filenames sort (checked)

Where IDs appear in filenames, pad to fixed width (F001…F999) so lexical sort equals numeric sort. **Check pattern:** `ls` the ID-bearing files; out-of-order listing reveals an unpadded ID.

## PROPOSED RULESET R-exception-discipline
description:: Accepted rule-violations are catalogued as numbered, graded exceptions with a stated justification — audits re-run mechanically and fail on ungraded regressions. Proposed home: `Rulesets/R-process/`.

Recurs in HA + MUX + the R-ob enforcement idiom. HA: "Exceptions are numbered (EX001, EX002, …) with grades and For/Against justification"; every accepted site carries an inline `EX<n>` comment. MUX: "Scanner … Exception table destructively rewritten each run" with High/Medium/Low graded findings. [[R-ob-observability]]-01 already requires it per-rule ("listed in an Exceptions table with a grade + justification") — this family generalizes the idiom so any adopted ruleset can lean on it. It is also exactly the enforcement shape Warden's audit tier automates; upgrading this family gives Warden the canonical statement of the discipline it enforces.

### RULE R-exception-discipline-01 — Accepted violations live in a numbered exception table (checked)

Each discipline's accepted deviations are enumerated in an exceptions table with globally-unique numbers (EX001…). A violation neither fixed nor listed is an open finding, not an exception.

### RULE R-exception-discipline-02 — Every exception carries a grade + justification (checked)

Each entry is graded (A–F or High/Medium/Low per the adopting project's convention) with a one-line justification for NOT taking the strict fix. Ungraded exceptions are unreviewed debt.

### RULE R-exception-discipline-03 — Audits re-run mechanically and fail on ungraded regressions (stated)

The discipline has a scanner (or Warden rule) that re-runs on demand; a new High/Medium finding since the last pass, absent a matching exception entry, fails the audit rather than silently growing the pile.

## PROPOSED RULESET R-wrapper-cli
description:: All interaction with managed infrastructure flows through the sanctioned command surface; raw primitives are forbidden, missing capability is proposed rather than worked around, and destructive commands check status first. Proposed home: `Rulesets/R-process/`.

Recurs in A2X + SKD + the global CLAUDE.md (`ctrl` / `exp` / never-raw-ssh-tmux). A2X EXP: "NEVER run … ANY raw tmux command … NEVER run raw `ssh` commands to remotes" and "If no `exp` command exists for what you need, stop and propose adding one — do not work around the system." SKD: "The cmx command surface must be complete … No escape hatches, no raw shell access for agents."

### RULE R-wrapper-cli-01 — Always through the sanctioned surface, never raw primitives (stated)

Where a project defines a wrapper CLI over managed infrastructure (tmux sessions, remotes, experiment workers), all interaction — human and agent — goes through it. Raw underlying commands are forbidden even when they would work, because they bypass the wrapper's state tracking.

### RULE R-wrapper-cli-02 — Missing capability: stop and propose, never work around (stated)

When the sanctioned surface can't do something, the move is to halt and propose adding the command — not to reach under the wrapper with raw primitives. Workarounds fork the interface and rot the wrapper's authority.

### RULE R-wrapper-cli-03 — Destructive commands check status first; setup is idempotent; force-flags are gated (stated)

Never a destructive action without a status check immediately before it; init/setup commands are safely re-runnable; `-f`/`--force` on live state requires explicit user approval.

## Borderline candidates — parked pending more recurrence

Real signals that stopped short of the ≥3-project bar or extend an existing set rather than founding a new one; future mining passes should re-test them:

- **Timing governors in config, each naming its failure mode** (HA P10) — a sharp, portable extension of [[R-ob-state-mgt]]-03; candidate `R-ob-state-mgt-04` when a second project exhibits it.
- **Write-if-changed gating on all production file writes** (HA P07/R01) — motivated by watcher cascades; portable wherever file-watchers exist.
- **Idempotent convergence, forward-only** (MUX "diffs against reality and takes the minimum actions"; SKD "No rollback — the system keeps converging forward") — two strong statements; one more instance makes it a family.
- **Test-energy budgeting: property-based + differential over hand-written examples where inputs are combinatorial** (SVP F004; A2X behavior-not-implementation) — the natural seed for the [[R-test]] placeholder's `R-property-based`.
- **Bundle self-containment** (MUX no-`~/bin`-at-runtime; global CLAUDE.md packaged-apps rule) — already enforced globally via CLAUDE.md; catalog capture would be for per-app adoption symmetry.
- **Draft-first / never present a blank page** (A2X Master Flow; SKD skeleton-first) — agent-workflow style more than application architecture; may belong beside the skills, not R-arch.

## Housekeeping recommendation

The legacy `~/.claude/skills/rule/rulesets/oblinger-rules.md` (OB-R01/02/03/05, consumed by the old `/rule create`/`/rule sync`) duplicates [[R-ob-state-mgt]]-01/02/03 and [[R-ob-observability]]-01 nearly verbatim — two sources of truth for the user's own portable rules. Recommend: retire the legacy file to a redirect at [[R-ob]] once no `/rule sync` consumer depends on it (HA's `HA Rules.md` § Inherited Rules cites it as its sync source, so HA's sync pointer moves to R-ob in the same pass). This is R-single-source-of-truth-01 applied to the catalog itself.
