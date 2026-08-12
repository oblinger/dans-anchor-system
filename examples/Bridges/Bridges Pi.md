---
description: "the always-on Raspberry Pi — cron + watchers"
---
:>> [[DAS]] → [[examples]] → [BRDG](hook://BRDG) → [Bridges Pi](hook://p/Bridges%20Pi)
# Bridges Pi
The heartbeat. It is small enough to be uninteresting and reliable enough to be the thing that notices when something else stopped, which is the whole reason it exists.

| Property | This machine |
|---|---|
| **Role** | cron, watchers, uptime checks |
| **Reachable** | always, by design |
| **Holds** | the watcher logs |
| **Rebuild cost** | twenty minutes from an image |

Listed by hand on [[Bridges]] rather than swept in by its catch-all — four machines is a small enough set that naming each one costs nothing and says more than a sorted list would.
