---
description: "durable rulings"
---
# HBR Decisions
include::

The durable rulings that shape Harbor; each is referenced by `// D0n` comments in the code.

| -[[HBR Decisions]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[HBR]] → [[HBR Design]] → [HBR Decisions](hook://p/HBR%20Decisions)<br>: durable rulings |
| --- | --- |
| Anchor | [[HBR Design]] (parent) |
| Related | [[HBR Architecture]],   |

### D01 — SQLite, not a server database (checked)

**Choice.** The catalog is a single SQLite file.

**Why.** A self-hosted household server should need no separate database process; one file also makes [[HBR Backup\|backup]] a file copy.

### D02 — Direct play first, transcode only on failure (checked)

**Choice.** The [[HBR Serve\|Serve]] pipeline streams the original bytes whenever the client supports the codec; the [[HBR Components#Serve\|Transcoder]] runs only as a fallback.

**Why.** Transcoding is the most expensive thing the server does — avoid it whenever the client can already play the file.

### D03 — Content hash is the identity (checked)

**Choice.** The [[HBR Components#Ingest\|Deduper]] folds entries by content hash, not by path or filename.

**Why.** The same rip living on two drives should be one catalog entry, regardless of where it sits on disk.
