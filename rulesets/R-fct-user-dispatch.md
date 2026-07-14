# RULESET R-fct-user-dispatch
include::
where:: `file: **/{slug} User Docs/{slug} User Docs.md`
description:: Rules every `{slug} User Docs.md` dispatch page must satisfy — the file must exist in the right location, open with the right dispatch-table header, and contain only user-task-shaped documentation (not system-spec docs).

### RULE R-fct-user-dispatch-01 — file lives at the correct path (checked)
The dispatch page is at `{slug} User Docs/{slug} User Docs.md` — a root-level folder.
**Check pattern:** path matches `{slug} User Docs/{slug} User Docs.md`.
**Why:** the folder context supplies the "User Docs" qualifier; a misfiled page is invisible to dispatch resolution.

### RULE R-fct-user-dispatch-02 — dispatch table top-left cell is the self-link (checked)
-[[{slug} User Docs]]-` in the left cell and a brief description beginning with `>` or `+>` in the right cell.
**Check pattern:** first table row matches `-\[\[.+ User Docs\]\]-` in cell 1 and starts with `>` or `+>` in cell 2.
**Why:** the self-link is what makes the dispatch table navigable; wrong or absent cell breaks the anchor-page contract per F060.

### RULE R-fct-user-dispatch-03 — contains only user-task documentation (sampled)
Every body row links a doc that describes a *user task* (Guide, Installation, CLI, FAQ, Cards) — not a system-spec doc (Interface, Architecture, UX Design, Data Model, Principles), which belong in [[DAS Design Dispatch|Design]] per F094.
**Check pattern:** body rows do not link `{slug} Interface.md`, `{slug} Architecture.md`, `{slug} Data Model.md`, `{slug} Principles.md`, or `{slug} UX Design.md`.
**Why:** scope leakage lets Design docs accumulate here; the F094 boundary is load-bearing for `/audit docs`.

### RULE R-fct-user-dispatch-04 — primary guide uses bare filename (stated)
The primary user-facing guide is `{slug} Guide.md`, not `{slug} User Guide.md`. The folder context already supplies "user-facing."
**Check pattern:** no file named `{slug} User Guide.md` is linked as the primary row (legacy files may exist pending forward-migration).
**Why:** the filename convention prevents "User User Guide" redundancy and is the canonical form going forward.
