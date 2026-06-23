---
description: "product requirements — focus-free voice dictation hub for macOS"
---
# DMUX PRD
What DictaMUX is and what its first version must deliver.

| Outline                         |                                              |
| ------------------------------- | -------------------------------------------- |
| [[#Overview\|Overview]]         | what DictaMUX is + the combined-project vision |
| [[#Goals\|Goals]]               | what v1 must deliver                          |
| [[#Non-Goals\|Non-Goals]]       | what v1 defers                               |
| [[DMUX PRD#User Stories\|DMUX Stories]] | ten user stories (inline; US-DMUX-1..10) |
| [[#See also\|See also]]         | sibling design docs                          |

## Overview

DictaMUX is a macOS native Swift app that acts as a voice dictation hub, solving Apple Dictation's critical limitation: focus must remain in the active window while dictating. DictaMUX holds dictation focus in a dedicated Edit Pane while letting users work across tmux sessions and other applications, then sends dictated text to targets without requiring focus change.

The app supports three speech engines — Apple Dictation (high-quality focus-based transcription), SpeechAnalyzer (macOS 26+ focus-free transcription), and SFSpeechRecognizer (background command recognition) — providing a three-level voice command system: standby wake words, active commands, and in-transcript dictation commands, alongside a full numpad keyboard interface.

DictaMUX will evolve into a combined codebase with MuxUX, producing three build targets from one repository: DictaMUX standalone (this app), MuxUX standalone (the Tauri terminal GUI), and a merged DictaMUX-combined app embedding both. The combined project inherits the DictaMUX name; the transition is gated on verifying Apple Dictation works in a Tauri webview context before committing to the merged architecture.

## Design Workflow

| Step | Document | Purpose |
|------|----------|---------|
| 1 | [[DMUX PRD]] | Clarify requirements and scope |
| 2 | [[DMUX UX Design]] | Edit Pane, voice command surface, numpad interface |
| 3 | [[DMUX Architecture]] | Speech engines, target delivery, buffer/state model |
| 4 | [[DMUX Testing]] | Testing strategy + proposed-tests overview |
| 5 | [[DMUX Decisions]] | Load-bearing decisions citing rules |
| 6 | [[DMUX Track]] | Roadmap + features implementing the user stories |

## Goals

1. **Dictation without focus loss** — Users dictate into DictaMUX's Edit Pane while working in other apps; text is sent to targets via `CGEvent.postToPid()` without switching focus.
2. **Voice-controlled workflow** — Wake DictaMUX with voice from any app ("ignite"), send text to targets ("transmit"/"dispatch"), manage buffers ("stash"/"grab"), all hands-free.
3. **Buffer management** — Stack of 5 buffers for curating text before sending; stash, grab, swap operations queue multiple thoughts.
4. **Multiple target apps** — Auto-detect target from focus transitions, lock to a specific app, or always dispatch to tmux.
5. **Companion terminal window** — Dock below a MuxUX (or iTerm2) terminal window, appearing as a unified two-pane application.
6. **Persistent state** — Buffers, history, and configuration survive across sessions.
7. **Focus-free dictation** — SpeechAnalyzer engine (macOS 26+) enables continuous transcription without DictaMUX holding focus.
8. **Visual target feedback** — Green glow border overlay on the target app's window during dictation.
9. **Passthrough commands** — Always-on voice triggers that immediately send mapped text + Enter to the target app, in every mode.
10. **Scratch pad (Bench)** — Ordered list of text entries for collecting notes alongside the main buffer workflow.

## Non-Goals

- **Cross-platform** — macOS only; Apple Dictation and SFSpeechRecognizer are macOS-native.
- **Terminal emulator replacement** — DictaMUX manages dictation, not terminal emulation (companion window pattern).
- **Rich text editing** — Plain text only; no formatting, no markdown rendering.
- **AI transcription** — Uses Apple's built-in engines exclusively; no Whisper, no cloud APIs.
- **Direct mouse interaction with targets** — Mouse clicks via `postToPid` don't work (tested); voice commands are the path.

## User Stories

### US-DMUX-1 — Quick dictation into current app
As a **user**, I want to wake DictaMUX and dictate straight into the app I'm in, so that I can send text without changing focus. User is in Mail composing an email, says "ignite" — DictaMUX activates, Mail becomes the target. User dictates, says "transmit" — text is sent to Mail at cursor position. DictaMUX returns to Listening mode.

### US-DMUX-2 — Extended work with locked target
As a **user**, I want to lock a target app so I can reference other windows mid-dictation, so that my text always lands in the right place. User opens Obsidian, says "ignite", locks the target. They switch to browser for reference, say "ignite" again — target stays Obsidian (locked). Dictate, transmit, switch apps, repeat.

### US-DMUX-3 — Buffer stack workflow
As a **user**, I want to stash partial thoughts and pull them back later, so that I can curate multiple dictations before sending. User dictates a command, realizes tmux isn't ready, says "stash" — text pushed to Stack 1, buffer clears. Dictates another thought, stashes it. Later says "grab two" to pull the original, "dispatch" to send to tmux.

### US-DMUX-4 — Recovery from history
As a **user**, I want to recover previously sent text, so that I can reuse or repair a buffer I cleared. User opens history (Cmd+H / "history"), scrolls to the entry, clicks it — text copied to current buffer. Edits if needed, transmits to a new target.

### US-DMUX-5 — Hands-free tmux dictation loop
As a **user coding with an agent**, I want a keyboard-free dictate-and-send loop into tmux, so that I can prompt continuously while coding. User presses Numpad Enter to start dictating, speaks a prompt, presses Numpad . — dictation stops, text goes to tmux with a newline, buffer clears. Repeat.

### US-DMUX-6 — Voice wake from anywhere
As a **user deep in another app**, I want to start dictation by voice alone, so that I never touch the keyboard to activate DictaMUX. User says "ignite" — DictaMUX acquires focus, starts dictation, captures the previous app as target. User dictates, sends, continues working.

### US-DMUX-7 — Standalone use without MuxUX
As a **user without MuxUX running**, I want DictaMUX to work alone, so that the dictation hub is useful on its own. DictaMUX works as a floating edit window with buffer stack, history, and keyboard/voice commands. Can send to any app via "transmit" or any tmux session via "dispatch".

### US-DMUX-8 — Focus-free dictation with SpeechAnalyzer
As a **user**, I want to dictate without DictaMUX taking focus, so that I keep working in my current app while speaking. User says "fuse" from any app — DictaMUX starts SpeechAnalyzer transcription, no focus change. Text accumulates in the Edit Pane; "fire" sends and continues, "transmit" sends and stops. The green glow overlay confirms the target.

### US-DMUX-9 — Passthrough command to agent
As a **user**, I want a voice trigger that fires a slash command instantly, so that I can drive my agent mid-dictation. User says "forge" — DictaMUX immediately sends "/dev forge" + Enter to the target without interrupting dictation state. The passthrough fires in any mode.

### US-DMUX-10 — Bench for collecting notes
As a **user**, I want a side list for saved thoughts, so that I can collect notes without disturbing the main buffer. User says "bench" — current buffer is added as a numbered entry to the bench list. Later "show bench" lists entries, "full bench" loads them all into the buffer for sending.

## See also

- [[DMUX UX Design]] — Edit Pane and voice command surface
- [[DMUX Architecture]] — speech engines, target delivery, state model
- [[DMUX Decisions]] — load-bearing choices (native Swift, three engines, no focus-steal, companion window, YAML config, persistent state)
