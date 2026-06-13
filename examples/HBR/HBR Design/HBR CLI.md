---
description: "command-line surface"
---
# HBR CLI
The `harbor` command — how the owner runs the server.

| -[[HBR CLI]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[OBSK]] → [[HBR]] → [[HBR Design]] → [HBR CLI](hook://p/HBR%20CLI)<br>: command-line surface |
| --- | --- |
| Anchor | [[HBR Design]] (parent) |
| Related | [[HBR API Design]],  [[HBR UX Design]],   |

```
harbor scan [PATH]   # walk a watched root, ingest new media into the catalog
harbor serve         # start the HTTP server (browse + stream)
harbor backup        # snapshot the catalog + harbor.toml to the backup dir
harbor status        # print catalog size, last scan time, and cache hit-rate
```

Every subcommand reads `harbor.toml` for the watched roots, catalog path, and listen address. Subcommands never prompt; they exit non-zero on any error.
