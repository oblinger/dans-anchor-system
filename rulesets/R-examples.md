# RULESET R-examples
where:: `file:{anchor}/examples/**/*.md`
import:: skills/audit/scripts/audit-plan.py
description:: Examples in a published anchor are wholly invented — no content drawn from the author's vault, and no real project, person, address, or drive name.

Ruleset for the examples gallery of a published anchor — decision: [[DAS Decisions]] § D1. **The gallery is the one place where "it's a better example because it's real" is a reason to refuse, not to accept.** A published repo authored from inside a private vault has a standing gradient toward real examples, and it has been followed four separate times; these rules are the counterweight.

**Scope note.** `where::` selects `examples/**` only. A facet spec under `facets/` may *discuss* real systems in its rationale; what it may not do is ship one as a specimen. That distinction is deliberate and is why these rules are not `always`.

### RULE R-examples-01 — No real project slug appears in example prose (checked)
check:: examples_no_vault_identifiers
An example must not name a project that exists in the author's vault. The marker set is the anchor slugs of live projects plus their product names. **A mention inside a machine-generated dispatch row does not count** — the `...` catch-all enumerates whatever files are present, so a hit there is a symptom of a real file in the gallery, not of authored prose; fix the file, not the row.

### RULE R-examples-02 — No personal identifier appears anywhere under `examples/` (checked)
check:: examples_no_vault_identifiers
Real names, email addresses, absolute home paths, and employer names. This is the same class the repo's history has twice been rewritten to remove, and the gallery is where it re-enters, because worked examples get written while doing real work.

### RULE R-examples-03 — No folder is named `_NAME_` (checked)
check:: examples_no_drive_shaped_folder
Leading-and-trailing underscore is reserved to the logical-drive vocabulary, where it asserts *a complete copy of logical drive NAME*. An in-repo folder using it makes a false claim and collides with a real drive. See [[DAS Decisions]] § D2.

### RULE R-examples-04 — The marker list is a floor, not a definition (stated)
`R-examples-01` and `-02` can only catch identifiers someone thought to list, and a marker list is by construction narrower than the rule it serves. Passing them is not evidence that an example is invented; it is evidence that no *known* marker is present. The authoring discipline in [[DAS Decisions]] § D1 is what the rules approximate. Kept `stated` because a checker that scored its own coverage would be claiming exactly the completeness this rule denies.
