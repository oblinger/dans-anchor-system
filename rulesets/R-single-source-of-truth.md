# RULESET R-single-source-of-truth
include::
description:: Every canonical datum — a config value, a state field, a type definition, a compiled binary, a spec — lives in exactly one physical location; every other reference is a pointer, include, or explicitly-labeled derived mirror.

Recurs in 6/6 corpora — the single strongest signal in the scan. HA P04: "exists in exactly one physical location. Other references to it are symlinks, pointers, or lock-free snapshot reads. Manual duplication is forbidden" (`HA Track/HA Rules.md`). MUX: "Rust definitions … are canonical; TypeScript mirrors … are hand-maintained shadows. Keep them in sync" (`MUX Design/MUX Architecture/MUX-Data.md`). SVP: "duplicating it as a docs folder would split the source of truth" (F006). SKD: "the central registry is a cache, not a separate source of truth." SVAR: "per-subsystem PRDs link back here rather than duplicating it" (SVAR PRD). Global CLAUDE.md: "NEVER maintain multiple copies of the same code file."

### RULE R-single-source-of-truth-01 — One physical home per canonical datum (sampled)

Any canonical piece of information exists in exactly one physical location. Other references are links, includes, symlinks, or reads of the canonical copy — never a second hand-maintained instance. **Check pattern:** for a sampled datum (a type, a config default, a documented contract), search for its definition; more than one authoritative-looking definition is a violation.

### RULE R-single-source-of-truth-02 — Mirrors are labeled derived and have a sync story (sampled)

Where a mirror is genuinely required (cross-language type shadows, generated artifacts, dashboards), the mirror is explicitly labeled as derived, names its canonical source, and has a stated sync mechanism (generator, sync script, or a keep-in-sync note at both ends). An unlabeled copy is a second source of truth waiting to diverge.

### RULE R-single-source-of-truth-03 — Shared standards have one canonical home; never fork locally (stated)

When a project touches a standard shared across the vault (a doc format, an anchor convention, a ruleset), it links the canonical home rather than re-implementing or copying it locally. MUX states it directly: "there is ONE canonical home — do not fork anchor logic or docs locally."
