---
description: agent inbox — system messages for this anchor; cleared on every pause. See [[CAB Messages]].
---

# CAB Messages

Agent inbox for the CAB anchor — a transient log of system events (hook edits, audit pings, automation notices) that the agent reads at session start and clears on every pause.

[2026-06-07 11:09:01] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-07 11:33:13] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-07 11:35:25] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-07 12:30:53] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-07 13:16:41] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-07 13:17:48] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-07 13:19:38] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-07 13:21:01] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-07 13:21:44] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-07 13:23:03] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-07 13:23:11] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-07 13:24:49] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-07 13:24:53] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-07 13:27:48] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-07 13:55:33] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-07 13:56:57] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-07 13:57:01] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-07 14:50:46] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-07 14:52:29] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-07 14:52:32] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-07 14:54:06] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-07 14:55:00] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-07 16:40:40] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-07 16:41:39] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-07 16:43:36] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-11 12:26:23] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited

# BRIEF

- **This is an agent inbox, not a durable doc.** The body is a transient append-only log of system events for the CAB anchor; do NOT treat it as content to curate or preserve.
- **Cleared on every pause.** Entries below the H1 are wiped at session boundaries; nothing here is load-bearing across sessions — if something matters long-term, it belongs in the backlog, a feature doc, or a Decisions/Rules file, NOT here.
- **Inclusion test for a line entry:** machine-written `[timestamp] [LEVEL] <event>` lines emitted by hooks/automation for this anchor only. No hand-authored prose, no cross-anchor messages (each anchor has its own `<NAME> Messages.md`).
- **Do not pile content here:** discussion, notes-to-self, design fragments, TODOs, multi-anchor system events — all belong elsewhere. The inbox is one anchor, one log, machine-emitted only.
- **Format is strict:** `[YYYY-MM-DD HH:MM:SS] [LEVEL] <message>`, one event per line, append-only, newest at the bottom. Don't reformat, sort, or coalesce — downstream readers parse the literal shape.
- **Load-bearing structure:** the H1 `# CAB Messages`, the TLDR sentence under it, and this `# BRIEF` section are the only persistent zones. Clearing logic preserves the H1+TLDR and this BRIEF — never delete or rename them, or the inbox loses its anchor.
[2026-06-11 12:27:06] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-13 14:43:21] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-23 16:22:28] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-23 16:22:51] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-23 18:25:07] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-23 18:25:47] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-27 11:10:52] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-27 11:14:59] [INFO] backlog at SYS/Bespoke/Skill Agent/CAB/CAB Track/CAB Backlog.md was edited
[2026-06-27 16:09:21] [INFO] backlog at SYS/Bespoke/Skill Agent/ob-skills/facets/CAB Legacy/CAB Track/CAB Backlog.md was edited
