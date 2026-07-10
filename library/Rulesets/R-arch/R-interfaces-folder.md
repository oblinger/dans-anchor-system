# RULESET R-interfaces-folder
include::
description:: All abstract contracts live in a single `Interfaces` package per system; business code depends on interfaces, never concretes.

Commissioned in F108 ("every system has a single `Interfaces/` folder") and canonical in SVP F006: "all abstract contracts (the 'what') live in a single **`Interfaces`** package; concrete instances are **never constructed directly**." The doc-side of the same instinct recurs as the human-authored layer-contract: HA `HA Design/HA Interface.md` ("What's Hidden — Callers above the HA layer do not need to know…"), SVP `SVP Interface.md` ("Public Surface / Guarantees + Non-Guarantees / Stability Tier"), MUX `MUX Interface.md`.

### RULE R-interfaces-folder-01 — One `Interfaces` package holds all abstract contracts (checked)

**Check pattern:** list the system's interface/trait/protocol definitions. Pass if they live in a single `interfaces/` package (human name `Interfaces`, lowercase directory per language convention); interface definitions scattered across module folders are violations.

### RULE R-interfaces-folder-02 — Business code depends on interfaces, not concretes (sampled)

For a sampled call site outside construction code, the referenced type is the interface, not the implementing class. Concrete types are named only in factories and the pegboard registration.

### RULE R-interfaces-folder-03 — Every code anchor carries a human-authored layer-contract doc (stated)

The anchor has a top-level `{slug} Interface`-style doc naming the caller of record, the public surface, explicit Guarantees vs Non-Guarantees, and a What's-Hidden section listing internals callers must NOT depend on. (Complements the [[FCT API Design|R-api]] facet ruleset, which governs the doc's format; this rule requires its existence.)
