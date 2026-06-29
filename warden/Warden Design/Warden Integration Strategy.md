---
description: "what to adopt vs. build (prior art) + the dependency/repository policy"
---

# Warden Integration Strategy

How the rule system relates to the prior art mapped in [[Warden Survey]], and the policy for *depending* on anything external. Driving constraints: the [[Warden PRD]] goals (state-once declarative rules, **performance** — instruments nearly every action, **simple to load and use**) and the standing principles **single source of truth**, **no fallback logic**, and **a packaged app must not reach outside its bundle at runtime**.

## Where we sit in the landscape

The survey scores every candidate on four legs — **(a)** path match · **(b)** content validation · **(c)** corrective message to the agent · **(d)** block. Mapped onto our architecture ([[Warden Architecture]]):

| Survey layer | Closest prior art | Our subsystem | Verdict |
|---|---|---|---|
| Interception (a/c/d) | **Claude Code hooks** (native) | the **hook subsystem** (§6) | **Already ours** — same mechanism; we sit on it. |
| Declarative rule-file UX | **Hookify** (official, ~90%) | **[[FCT Ruleset]]** + [[Warden Events]] | **We exceed it** — rulesets, `include::` composition, tiers, the moment taxonomy, the `when ∧ where ∧ if` conjunction. Hookify is one-regex-per-condition on the *edit text*; we validate the *whole resulting file*. |
| Content engine (b) | **Vale** (markdown), **Semgrep** (code) | the `check::` primitive library + the audit engine (§7b) | **Mixed** — our primitives cover the common cases; Vale/Semgrep are richer for their niches. Integration seam, not a rebuild. |
| The under-served **gap** | *(nobody ships it turnkey)* | the **audit engine** (Resolve→Run→Judge) | **This is our core IP.** Whole-file validation against a multi-rule format spec, per-violation messages — the survey's headline finding is that this is exactly what's missing off-the-shelf. Build it; that's the point. |

**Conclusion:** our design is aimed squarely at the confirmed gap, on top of the confirmed-standard plumbing. We are not reinventing the interception layer (it's native) and not reinventing rich rule files (we already exceed Hookify). The novel, build-it-ourselves core is the moment taxonomy + the whole-file rule engine + the compiler/installer.

## What the survey resolves

- **Rules can block, not just steer** (freeze Q1). Native `PreToolUse` returns `permissionDecision: "deny"` with a reason fed back to the agent; `PostToolUse` returns `{decision: "block", reason}`. So a `tool:pre` rule *may* veto an action, gated by the `aow-safety` floor. → folds into [[F210 — Conjunction binding + indexing|F210]].
- **Implementation caveat:** prefer **JSON `deny`/`block` output over bare exit-code-2** (survey notes Claude Code bug #24327 — exit-2 sometimes halts instead of feeding the message back). → a note for [[F211 — Rule compiler and installer|F211]] and the hook subsystem.
- **Validation of the whole approach:** arXiv 2606.13174 ("compiling user corrections into runtime enforcement") is our compiler/installer + steer model as a research result; AGENTS.md #179 is the standards direction heading our way. We are early on a real curve, not off in the weeds.

## Integration posture per layer

1. **Interception → rely on Claude Code hooks natively, behind a thin adapter.** Non-negotiable and already done. The one design move: keep the hook contract behind a small adapter interface so a future harness (Codex/Cursor hooks mirror the same allow/deny/modify shape) is an *adapter swap*, not a rewrite. Not a dependency — it's the runtime we live in.

2. **Rule-file UX → stay independent; offer interop, not dependency.** Our format is a richer superset of Hookify's. Borrow its author-facing *ergonomics* (a one-line English rule that compiles to the full form is worth having) but own the format end to end. Optionally ship a **Hookify-import** so existing Hookify rules migrate in. We do not depend on the Hookify plugin.

3. **Content engine → self-contained primitives by default; external checkers as opt-in adapters.** Our `check::` library is the default and covers the regex/frontmatter/structural cases natively (and must, for the hot path — see below). Vale and Semgrep are excellent but are **optional, adapter-isolated backends** (`check:: vale:<rule>`, `check:: semgrep:<rule>`) that **fail loud** if a rule invokes a tool that isn't installed — never a silent skip, never required by any core ruleset. A clean install runs the whole core with none of them present.

## Dependency & repository policy

The user's question — vendor a copy / depend on a repo / mirror our own clone / don't depend at all — has one governing answer:

> **Self-contained core; optional, adapter-isolated, fail-loud edges; no hard external-repo dependencies.** A clean clone of this repo must build and run the full core with **zero external repos and zero external binaries**. Anything external is an opt-in capability at the edge, never a load-bearing core dependency.

Per external thing:

| External thing | Kind | Binding | Rationale |
|---|---|---|---|
| **Claude Code hooks** | platform runtime contract | **Native**, behind a thin adapter | It's the substrate, not a dependency (like the OS). Adapter buys future-harness portability. |
| **Hookify / cchook formats** | prior-art convention | **Independent + optional import** | Our format is a superset; learn the UX, don't bind to their plugin. |
| **Vale / Semgrep / ast-grep** | optional checker binaries | **Detect-if-present adapter; fail loud if a rule needs an absent tool; never required by core** | Keeps the core zero-dep + simple to load; honors no-fallback. |
| **The whole-file format engine** | the gap | **Build it — our core** | Confirmed under-served; it's the reason the system exists. |

Mapped to the four options the user named:

- **(d) Don't depend — the default for the core.** The rule language, taxonomy, compiler/installer, default checker library, and the Python + Rust implementations are all ours and self-contained.
- **(b) Depend on an external repo — avoid.** A build-time dependency on someone else's repo taxes every clone and risks drift; acceptable *only* at the optional edge, and even there prefer "detect an installed binary" over "build-depend on their source."
- **(a) Vendor a copy — only for tiny, stable, license-clean snippets**, never a whole engine (vendoring Vale/Semgrep bloats the repo and forks a stale copy — violates single-source-of-truth and "simple to load").
- **(c) Mirror our own clone — only as resilience for a *critical* upstream at risk of disappearing.** We have no such critical upstream (every external is optional), so: no mirrors.

### Why the performance architecture already forces this

The implicit hot path (Rust, per-moment ms budget — [[Warden PRD]] § Performance) **cannot afford to spawn an external process** (Vale/Semgrep startup alone blows a `tool:pre` budget). So external checkers are *intrinsically* confined to the **explicit / on-demand audit path**, and the implicit path is *necessarily* self-contained native code. The performance constraint and the dependency policy reinforce each other: the thing that must be fast must also be self-contained — which is also the thing that makes the repo simple to load.

## Adoption & standards alignment

Does aligning with Vale/Semgrep win adopters? Three points:

1. **Network effects for an agent-time system are at the *agent-rules* layer, not at Vale/Semgrep.** Claude Code hooks, AGENTS.md, and the forming "full-file-schema" direction the survey flagged (AGENTS.md #179) are the standard adopters will already have. Vale (prose-lint) and Semgrep (code-SAST) are mature, niche tools whose audiences only partly overlap ours. Aligning early with — and influencing — the agent-rules standard is the real network-effect play; "be consistent with Vale" is a *feature*, not a standards strategy.

2. **The adoption lever from Vale/Semgrep is consuming their rule *corpora*, not mimicking their syntax.** An importer that lets an adopter bring an existing Vale style (or Opengrep ruleset) and get *agent-time* enforcement for free is a real on-ramp. Keep it an on-ramp: import/translate into our richer format; never contort ours to look like theirs.

3. **Vale-first, Opengrep-over-Semgrep.** The vault is markdown → Vale's domain *is* ours and it is cleanly MIT. Semgrep is code-SAST (peripheral here) and now legally messier (below) → if code-scanning ever matters, target Opengrep (LGPL), not Semgrep.

Caveat: every integration fights "simple to load" and couples us to someone else's roadmap and licensing drift. Semgrep is the live cautionary tale (§ Licensing). So integrations stay **optional, separately-packaged edge adapters** — preserving the simple core while offering the on-ramp.

## Can our language be an extension of Vale's?

Two senses — the answer differs by which:

**Surface syntax (host Vale's YAML rule files verbatim): no.** That splits our surface into two grammars, makes Vale's schema a permanent input contract (couples us to their roadmap — the Semgrep risk), and abandons our markdown-native format + `include::` composition + the moment taxonomy. Violates single-source-of-truth and simple-to-load.

**Capability model (express everything Vale can, and more): yes — this is the target.** Vale's design is `extends:` a **check-type** — a small set of parameterized content-check primitives. That is *exactly* our `check::`-a-primitive design; the two independently arrived at the same architecture. So we spec **our `check::` vocabulary as a superset of Vale's check-type taxonomy**:

| Vale | Ours | Native or adapter |
|---|---|---|
| path glob (`.vale.ini [*.md]`) | `where::` file glob | native |
| `scope:` heading / sentence / paragraph / code / raw | `where::` extended with in-file **region scopes** | native for heading/code; prose scopes need a segmenter |
| `extends:` existence · substitution · occurrence · repetition · consistency · conditional · capitalization | `check::` regex primitives | **native** |
| `extends:` spelling · metric · sequence(POS) · script | `check::` … | **opt-in Vale adapter** (Hunspell / readability / NLP / Tengo — not reimplemented) |
| `message:` (+ `%s`) | rule message / steer + interpolation | native (add interpolation) |
| `level:` suggestion / warning / error | a **severity** field — *distinct from our verification `tier`* | add field |
| `link:` · `limit:` | link · per-file cap | add fields |

So: **our language is a superset of Vale's *capability*, not a host for its *syntax*.** A Vale rule maps 1:1 into ours, so the integration is (1) a **Vale importer** (trivial given the mapping) + (2) an **opt-in Vale execution adapter** for the NLP / spelling / script / metric check-types we don't reimplement (confined to the explicit audit path — they're slow anyway; consistent with D3). The regex/structural subset runs natively on the hot path.

Two genuine additions Vale forces into our format: an in-file **scope/region** dimension on `where::`, and a **severity** axis separate from `tier`. Both are clean extensions (downstream touches to [[FCT Ruleset]] + the `check::` primitive library).

## Licensing — can we vendor?

| Component | License | Vendorable? |
|---|---|---|
| **Vale** engine | MIT | **Yes** — retain LICENSE + attribution; cleanest to vendor. |
| Vale **styles** (Microsoft/Google/write-good) | per-style (mostly MIT/CC) | Mostly yes — check each style. |
| **Semgrep** engine (CE/OSS) | LGPL-2.1 | Yes, with **LGPL obligations** — trivially satisfied when invoked as a subprocess; redistributing the binary requires shipping the license + permitting relink/modify; avoid static-embedding without LGPL compliance. |
| **Semgrep-maintained rules** (registry) | **Semgrep Rules License v1.0** (Dec 2024) — internal / non-competing / non-SaaS only | **No** — not freely redistributable. This relicensing triggered the Opengrep fork. |
| **Opengrep** (Semgrep fork, Jan 2025) | LGPL-2.1 | Yes — the open substitute for Semgrep-style scanning + free rules. |
| **ast-grep** | MIT | Yes. |

**Bottom line:** vendoring the *engines* is permitted (Vale MIT; Semgrep/Opengrep LGPL with obligations); vendoring **Semgrep's rule registry is not**. The Semgrep episode is itself the argument for our policy — external rule corpora can be relicensed out from under you — so **own our rule corpus, keep external tools as optional detect-if-present adapters, and prefer MIT/LGPL engines (Vale, Opengrep, ast-grep) if we ever bundle anything.** (Sources: InfoQ/Semgrep/Opengrep 2025; vale.sh.)

## Decisions

- **D1 — Self-contained core, zero hard external-repo dependencies.** A clean clone runs the full core with no external repos/binaries.
- **D2 — Claude Code hooks are the interception substrate, used natively behind a thin portability adapter** (not vendored, not a repo dependency).
- **D3 — External checkers (Vale/Semgrep) are optional, adapter-isolated, fail-loud, confined to the explicit audit path; no core ruleset may require one.**
- **D4 — Prior-art rule formats (Hookify) are interop targets, not dependencies;** an import path is a nice-to-have, our format stays the superset source of truth.
- **D5 — Rules may block** (`tool:pre` deny / `tool:post` block) **via JSON hook output, gated by the `aow-safety` floor;** never via exit-code-2.
- **D6 — Adoption alignment targets the agent-rules standards layer** (hooks, AGENTS.md), not Vale/Semgrep *consistency*. Their value is realized via opt-in **rule-corpus importers** (an on-ramp), Vale-first, Opengrep-over-Semgrep.
- **D7 — Vendoring posture.** Engines are legally vendorable (Vale MIT; Semgrep/Opengrep LGPL with obligations) but **Semgrep's registry rules are not**. Default remains detect-if-present, no vendoring (D1/D3); if we ever bundle, prefer MIT/LGPL engines and never Semgrep's restricted rules.
- **D8 — Our language is a superset of Vale's *capability*, not a host for its *syntax*.** Spec the `check::` primitive vocabulary as a superset of Vale's check-type taxonomy; add an in-file `scope`/region dimension to `where::`, a `severity` axis (distinct from `tier`), message interpolation, and `link`. Integration = a Vale **importer** (1:1 mapping) + an **opt-in execution adapter** for the NLP/spelling/script/metric check-types (native for the regex/structural subset). We do **not** accept Vale's YAML as a surface dialect. Downstream: [[FCT Ruleset]] (severity + scope), [[F211 — Rule compiler and installer]] (the adapter).

## Open questions

1. **How thin is the harness adapter?** Minimal (Claude-Code-only now, refactor later) vs. a clean interface from day one. Leaning: a single narrow adapter module now, Claude-Code-only behind it.
2. **Do we ship the Hookify-import in v1** or defer? (Defer unless there's a real corpus of Hookify rules to migrate.)
3. **Vale specifically** — is there enough markdown-rule value to build the Vale adapter early, or do our native primitives + the agent-judgment path cover the markdown cases well enough that Vale waits? (Leaning: native primitives first; Vale adapter only if a real rule needs lookaround-class regex we won't reimplement.)

## See also

- [[Warden Survey]] — the prior-art survey this strategy responds to.
- [[Warden Architecture]] — the subsystems referenced here.
- [[Warden PRD]] — the goals (simple-to-load, performance) that drive the policy.
- [[F210 — Conjunction binding + indexing]] · [[F211 — Rule compiler and installer]] · [[F213 — Rust performance implementation + ms budget]] — where these decisions land.
