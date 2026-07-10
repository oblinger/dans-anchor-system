# RULESET R-stable-ids
include::
description:: Numbered identifiers are permanent handles — monotonic-forever, never recycled, gap-numbered where ordered, zero-padded where sorted.

Recurs in A2X + MUX + HA + SVAR + SVP (and the vault's own F-number convention). A2X: "D-numbers persist (never recycled) … X-numbers are monotonic across all task types." MUX: "D-numbers are not recycled (monotonic-forever) … The D-number is the stable handle — title text may evolve; the link stays valid." HA: "Principles: P01, P02, … never change once assigned." SVP/SVAR: "Milestones use **gap numbering** (M10, M20, M30 …) so insertions don't force renumbering … same convention as SVAR's roadmap."

### RULE R-stable-ids-01 — IDs are monotonic-forever, never recycled (checked)

Numbered entity IDs (F-, D-, Q-, X-, EX-, P-numbers) increase monotonically and are never reused, even after the entity is deleted or retired. **Check pattern:** the next-available counter only ever grows; a reused number is a violation.

### RULE R-stable-ids-02 — The number is the stable handle; titles may evolve (stated)

Links and references cite the ID, and the ID never changes once assigned — so every historical reference stays valid while the human-readable title is free to improve.

### RULE R-stable-ids-03 — Ordered sequences use gap numbering (stated)

Sequences with meaningful order (milestones) number with gaps (M10, M20, M30) so insertions (M15) never force a global renumber. Each numbered item also carries a short name usable interchangeably with its number.

### RULE R-stable-ids-04 — Zero-pad where filenames sort (checked)

Where IDs appear in filenames, pad to fixed width (F001…F999) so lexical sort equals numeric sort. **Check pattern:** `ls` the ID-bearing files; out-of-order listing reveals an unpadded ID.
