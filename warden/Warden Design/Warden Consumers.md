---
description: "Proposed inventory of the consumers the Warden hook substrate must serve — each defined, with the substrate demands it implies and a confidence grade. Parley input for F131 Q4."
---
/comp:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[Warden]] → [[Warden Design]] → [Warden Consumers](hook://p/Warden%20Consumers)

# Warden Consumers
The inventory of things that consume agent moments through the Warden substrate — what each is, which moments it binds, and what it demands of the engine. Drafted 2026-07-01 as the starting material for the [[F131 — Hooks — fast inner-loop check substrate (path-rule alerts first)|F131]] Q4 parley; **confirmed by the user the same day** (F131 Q4 resolution): the confident set is the starting set — the substrate is designed against it — extended by the rules-corpus scan in § The rules corpus below.

**Why this doc exists.** The substrate (binary structure, config format, action vocabulary, matching) must be designed against the full range of consumers, not just the first one — otherwise path-rule-specific assumptions get baked in. Every consumer below reduces to the same skeleton: *bind moments (F209 taxonomy) → match/guard (F210 conjunction; F131 unification bindings) → act (steer / deny / fix / record)*. What varies is which moments, how expensive the guard is, and which action.

## Confident — exist today as bespoke hooks or ratified designs; they WILL ride the substrate

- **path-rule alerts** — deny/warn when Edit/Write touches a state-managed region (backlog rows, queries.md, TOC tables). The F131 motivator. Moments: `tool:pre:Edit/Write`. Demands: path-pattern unification with variable bindings; sub-ms match; veto action.
- **doc-audit on write** — run the rule engine against a written markdown file; auto-fix mechanical findings, steer the rest into context. Exists as `audit-on-write.sh` (F177); M4 migrates it onto the compiler. Moments: `write:markdown`. Demands: full ruleset evaluation, fix-capable actions, per-file scoping.
- **advice injectors** — classify a known failure signature in a tool result and inject the matching fix into the next turn. Exists as the F181 webfetch-authwall hook; the pattern generalizes (Bash 999, gh auth, MCP token expiry). Moments: `tool:post:<tool>`. Demands: cheap classifier guards; steer (additionalContext) action; one-bundle-per-failure-mode packaging.
- **command guard** — veto dangerous shell commands before they run (`bash-guard.sh` today; the `tool:pre` deny semantics were ratified in [[F210 — Conjunction binding + indexing|F210]] § Resolved). Moments: `tool:pre:Bash`. Demands: veto with reason; the `aow-safety` floor; near-zero latency.
- **maintain triggers** — keep derived files in sync with their sources (`maintain-hook.sh` today: mtime triggers + `:pr`/`:commit`/`:daily` events). Moments: `tool:post:Read`, `git:*`, timers. Demands: event moments beyond tool calls; run-a-recipe action.
- **agent-state sensing** — the [[F216 — Agent-state model — sensing what the agent is doing|F216]] classifier consuming the moment ledger to maintain `agent.state` / `agent.skill`. Moments: all (it IS the ledger's standing consumer). Demands: ordered, timestamped moment stream; session registry.
- **queue hygiene autofire** — audit-q's banner refresh + stale-bracket detection fired on backlog/queries writes rather than manual runs (an M4 migration target). Moments: `write:markdown` scoped to Track files. Demands: same as doc-audit, narrower scope.

## Uncertain — plausible; shape or value needs the parley

- **conversation-content gating** — rules on what the agent said/didn't say ([[F217 — Conversation-content gating — rules on what was said|F217]], designed): the `turn` view + `ask_oracle` tier. Uncertain only in its live-path shape (F217 Q1) — the substrate hooks are clear.
- **secret detection** — deny tool calls that would expose keys/tokens (post-read redaction? pre-send scan?). Valuable, but overlaps command guard, and detection quality/false-positive cost is unproven for vault workflows.
- **trigger-discipline integration** — wiring F091-style compact/markdown-write triggers through the substrate instead of bespoke hook scripts. Almost certainly right eventually (it's M4's spirit); uncertain whether F091's surface survives as its own consumer or dissolves into doc-audit + maintain.
- **file-size sanity** — warn before enormous Reads. Trivial to build; unclear it earns a rule (the harness already truncates; marginal value).
- **observability / replay log** — record every moment durably for debugging and audit trails. The ledger half-exists (F216 ring buffer); uncertain whether durable full-history is wanted (cost, privacy) or the bounded ring suffices.

## Listed but probably shouldn't be substrate consumers

- **anchor-invariant validation** — slug uniqueness, `.anchor` structure, dispatch coverage. Belongs to periodic `/audit structure` sweeps; firing it per-moment buys little and costs much (vault-wide checks don't scope to a single write).
- **spec-conformance checks (Q-format / ask-format)** — not a separate consumer; these are just rulesets the **doc-audit on write** consumer evaluates. Listing them separately double-counts.
- **session-state dashboard** — a UI that *reads* what agent-state sensing maintains; it consumes the ledger's output, not moments, so it sits above the substrate, not on it.

## The rules corpus — the workload behind doc-audit (Q4 extension, scanned 2026-07-01)

Per the user's Q4 ruling, the consumer inventory is extended by what the vault actually carries in Decisions and Rulesets:

- **115 `# RULESET` blocks ≈ 482 rules** — 254 `checked` / 109 `stated` / 82 `sampled` / 3 `tracked` — in ob-skills facets (~49 files), `library/Rulesets/` (~44), disciplines, and examples; every block scoped by `where::` (always / file / anchor / sentinel kinds, `{ANCHOR}`/`{NAME}` pattern variables).
- **22 live `## Decisions` surfaces** vault-wide — documentation only per the [[FCT Decisions]] doctrine (Warden never computes against decisions); they place no demand on the engine beyond confirming rulesets as the sole computable surface.

Consequences for the substrate: applicable-ruleset resolution must be an **indexed table probe** (compile the corpus, keyed by source mtimes — the `/distill` direction), not a per-moment scan; the **kind split is structural** — checked rules are engine-evaluable, stated/sampled can only be *steered* into agent context as reminders, tracked feed the ledger; and covering the confident seven + most of this corpus is the ratified "really good starting set." Full design: [[F131 — Hooks — fast inner-loop check substrate (path-rule alerts first)|F131]] § Substrate scope.

## What the inventory implies for the substrate (pre-parley read)

The confident seven already exercise the full action vocabulary (veto / steer / fix / record / run-recipe), both `pre` and `post` phases, path unification with bindings, event moments beyond tool calls, and one standing stream consumer. If the substrate serves those seven cleanly, everything in the uncertain bucket is a configuration, not a redesign — which is the answer F131 Q4 wants: the inventory is closed enough to unblock the substrate design.
