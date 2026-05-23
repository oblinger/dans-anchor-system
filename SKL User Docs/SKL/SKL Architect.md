# /Architect

`/architect` creates and maintains the top-level architecture document for an anchor — the system-level view that decomposes your project into **subsystems**, each with its own dispatch table, summary table, optional figure, and list of modules. The architecture lives at `{NAME} Docs/{NAME} User/{NAME} Architecture/`, and every module doc carries a back-link row pointing up to its subsystem. Reach for it when you say "build the architecture," "update the architecture," or "refresh the system diagram."

The skill reads your module docs as ground truth (and warns you if they're stale compared to the actual source) rather than re-reading every source file — it operates one layer *above* module docs. It's conservative by design: it'll propose new subsystems, flag orphan modules, and reconcile broken cross-links, but it won't wipe prose you wrote. Substantive changes surface as questions; trivial fixes happen silently.
