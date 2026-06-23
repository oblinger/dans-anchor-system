---
description: "durable rulings for Mini"
---
# Mini Decisions
include::

The durable rulings that shape Mini. Each is a D-record with a one-line rationale.

### D01 — Plain-text store, no database (checked)

**Choice.** Mini keeps its data in a single newline-delimited text file, not a database.

**Why.** Zero setup is the whole point of Mini; a file the user can open in any editor beats a process they have to run.
