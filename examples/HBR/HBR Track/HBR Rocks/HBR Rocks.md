---
description: "*Control* — the ranked list"
---

| -[[HBR Rocks]]- | → [[DAS]] → [[FEX]] → [[HBR\|HARBOR]] → [[HBR Track\|HARBOR TRACK]] → [HBR Rocks](hook://p/HBR%20Rocks)  |
| --- | --- |
| [[HBR Rocks]]  | *Control* — the ranked list |
| Related | [[DAS Stone]],  [[DAS Rocks]],  [[HBR Roadmap]],  [[HBR Backlog]],   |
| ... | [[HBR R0001]],  [[HBR R0002]],  [[HBR R0003]],   |

# HBR Rocks
The big chunks Harbor is trying to move — one file each. The **ranking** lives next door in [[HBR Rocks]]; this folder just holds the rocks.

✂ ──── example notes ──── ✂

Nothing below this line is part of the example. Above it is a stone-group folder page that could sit in a real anchor unchanged; below it is commentary about why the group looks the way it does.

- **The list moved out of this page, and that is the whole shape of [[DAS Stone]].** This folder page used to carry the ranked tiers itself. It cannot any more: an anchor page is machine-maintained at the top and the ranking is the one thing that must stay hand-arranged, so the two are now separate files — the rocks here, the arrangement in [[HBR Rocks]]. `R-stone-01` puts the group at `{slug} Track/{slug} {Kind}s/`; the control file sits beside it in Track.
- **Stones are numbered, not abbreviated.** `HBR R0001`, not `HBR HR` — `R-stone-02`, monotonic forever and never recycled. The abbreviation used to carry the meaning, which made a rename touch every line that referenced it; now **the expansion is simply the file's H1** (*Historical retrospective*), and the number is an opaque handle that nothing has to keep in sync.
- **The control line is one string doing two jobs.** `[[HBR R0001|HBR:]] gather stats` renders as `HBR: gather stats` for a human and resolves to the stone for the machine. Because the display half carries the *source* anchor, that exact line can be pasted into a downstream anchor's control file and still reads correctly *and* still points home — which is why propagation is line-copying rather than rendering, and why a downstream file stays hand-editable.
- **The words after the colon are a slice, not the rock.** "Gather stats" is not the historical retrospective; it is the piece of it in flight this week. That string lives in the stone's own `line::` key, so every copy of it anywhere in the feed graph is rendered from one place.
- **Two groups, and no sequence inside either.** `ACTIVE` and `SOON` say how committed Harbor is, not what order things happen in. Ordering belongs to [[HBR Roadmap]]; the moment tier lines grow dates and dependency arrows, the anchor has quietly acquired a second roadmap.
- **[[HBR R0003]] is deliberately uncommitted.** Real, named, worth doing, and nobody has promised it — exactly what a rock list exists to hold and what neither a roadmap milestone nor a backlog row can express.
- **Position is the data.** Which tier a line sits under, what order it is in, and whether it is above or below the self-section marker `-HBR-` (which is what publishes it downstream) are all expressed by *arranging* rather than by fields. That is why the stone files carry so few keys — see [[DAS Stone Keys]] § the arrangement test.

-[[HBR Rocks|HBR]]-
ACTIVE
[[HBR R0001|-]] gather stats
[[HBR R0002|-]] settle the codec matrix
SOON
[[HBR R0003|-]] pick a metrics backend
