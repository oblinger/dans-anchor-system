# RULESET R-examples
include::
where:: `file:{anchor}/examples/**/*.md`
import:: skills/audit/scripts/audit-plan.py
description:: Examples in a published anchor are wholly invented — no content drawn from the author's vault, and no real project, person, address, or drive name.

Ruleset for the examples gallery of a published anchor — decision: [[DAS Decisions]] § D1. **The gallery is the one place where "it's a better example because it's real" is a reason to refuse, not to accept.** A published repo authored from inside a private vault has a standing gradient toward real examples, and it has been followed four separate times; these rules are the counterweight.

**Scope note.** `where::` selects `examples/**` only. A facet spec under `facets/` may *discuss* real systems in its rationale; what it may not do is ship one as a specimen. That distinction is deliberate and is why these rules are not `always`.

### RULE R-examples-01 — No real project slug appears in example prose (checked)
check:: examples_no_vault_identifiers
An example must not name a project that exists in the author's vault. The marker set is the anchor slugs of live projects plus their product names. **A mention inside a machine-generated dispatch row does not count** — the `...` catch-all enumerates whatever files are present, so a hit there is a symptom of a real file in the gallery, not of authored prose; fix the file, not the row.

**Check pattern:** no line under `examples/` carries a marker from the live-project set, **excluding markdown table rows** (an electric-zone row is machine-written and cannot be edited; the offending file trips these rules on its own content instead). Bounded by `R-examples-04`: passing means no *known* marker is present, not that the example is invented.

### RULE R-examples-02 — No personal identifier appears anywhere under `examples/` (checked)
check:: examples_no_vault_identifiers
Real names, email addresses, absolute home paths, and employer names. This is the same class the repo's history has twice been rewritten to remove, and the gallery is where it re-enters, because worked examples get written while doing real work.

**Check pattern:** same scan and same table-row exclusion as `-01`, over the personal-identifier marker set rather than the project one. Same `R-examples-04` bound.

### RULE R-examples-03 — No folder is named `_NAME_` (checked)
check:: examples_no_drive_shaped_folder
Leading-and-trailing underscore is reserved to the logical-drive vocabulary, where it asserts *a complete copy of logical drive NAME*. An in-repo folder using it makes a false claim and collides with a real drive. See [[DAS Decisions]] § D2.

**Check pattern:** no *folder* on the file's path below the anchor root both starts and ends with `_` (and is longer than two characters). The file's own basename is out of scope — this is a claim folder names make, not filenames.

### RULE R-examples-04 — The marker list is a floor, not a definition (stated)
`R-examples-01` and `-02` can only catch identifiers someone thought to list, and a marker list is by construction narrower than the rule it serves. Passing them is not evidence that an example is invented; it is evidence that no *known* marker is present. The authoring discipline in [[DAS Decisions]] § D1 is what the rules approximate. Kept `stated` because a checker that scored its own coverage would be claiming exactly the completeness this rule denies.
