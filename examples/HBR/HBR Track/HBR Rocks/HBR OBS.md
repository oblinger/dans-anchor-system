---
description: "observability — make Harbor's behaviour visible while it runs, not only after it breaks"
---
# HBR OBS
Observability — make Harbor's behaviour visible while it is running, rather than reconstructable afterwards from logs.

## What

Harbor is diagnosed by reading logs after something has already gone wrong. OBS is the chunk that changes that: metrics for ingest throughput, transcode queue depth and playback errors, emitted continuously, with somewhere to look at them.

Done looks like a dashboard that answers "is Harbor healthy right now?" without anyone opening a log file.

## Why now

It is not committed, and this section says why honestly: nothing is currently blocked on it. It is on the list because the retrospective ([[HBR HR]]) is being made expensive by exactly the absence it would fix, and because every month it is deferred adds another month of history that has to be reconstructed rather than read.

That is the shape of an uncommitted rock — a real argument, no promise. It stays here, visible, until it earns a group above it or gets dropped on purpose.

## Shape

- **Pick a metrics backend** — the decision that gates everything else. Not started.
- **Instrument the three surfaces** — [[HBR Ingest]], transcode, serve.
- **A dashboard worth opening** — the part that decides whether any of this gets used.

## Status

**2026-08-06** — named, argued, not committed. No work has started and none is scheduled.
