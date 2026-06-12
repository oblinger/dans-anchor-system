---
name: devops
description: Run long-horizon operational work — remote builds, deployments, test-machine drives, multi-agent orchestration, permission/keychain dances — under a mandatory heartbeat discipline. Every heartbeat ends with one ALL-CAPS state banner (WAITING ON USER / WAITING ON COMPLETION / WORKING) so the user can glance at the window and instantly tell whether they are the thing being blocked on. Covers heartbeat cadence, real-time watchers, lockup recovery, and bringing test-machine fixes back to the source of truth.
---

# DevOps

Operational work runs on a clock the user cannot see — a build takes eight minutes, a remote agent goes quiet, a keychain dialog sits unclicked on another machine's screen. The single failure mode that wastes the most user time is **the user not realizing they are the blocker.** DevOps mode fixes that with one rule: while operational work is in flight, a heartbeat fires on a cadence, and its **last line is always an ALL-CAPS state banner** naming exactly what is being waited on. The user glances at the window and knows in one second whether to act.

This skill is the methodology for that work — the heartbeat being the load-bearing part, the rest being the practices that make long unattended drives safe.

## When you are in DevOps mode

Any time you are driving work that (a) takes long enough that you'll report status more than once, AND (b) has waiting states the user can't see — a remote build, a deploy, a test-machine drive, a forge, a multi-agent orchestration, a permission/keychain sequence on another machine. The moment you start such work, you are in DevOps mode and the heartbeat discipline below is in force until the work lands or the user stops it.

## The heartbeat — the core rule

While DevOps work is in flight, keep a recurring heartbeat alive (via ScheduleWakeup). Every heartbeat does three things, in order:

1. **Observe.** Capture the real state — the remote pane, the build process list, the artifact on disk. Observe the ground truth, not your memory of it.
2. **Report.** Tell the user, in 2–4 lines, what is happening and what you are doing.
3. **Banner.** End with exactly one ALL-CAPS state line — the last thing the user sees.

### The state banner (mandatory last line)

The final line of every heartbeat — and of every DevOps status message, heartbeat or not — is one of:

- **WAITING ON USER — {specific action}** — you cannot proceed until the user does a named thing. Be specific and actionable: name the machine, the dialog, the click. *"WAITING ON USER — click Allow on the keychain dialog on haorui's screen"* not *"WAITING ON USER — permissions."*
- **WAITING ON COMPLETION — {what, with ETA if known}** — a process or event you do not control must finish. *"WAITING ON COMPLETION — forge release build on haorui, ~4 min left"*.
- **WORKING — {what you are actively doing}** — you are mid-task, no one is blocked on anyone. *"WORKING — pulling the arch fix back to production and committing"*.

Rules for the banner:
- **It is the LAST line.** Nothing after it. The user's eye lands at the bottom of the window; that is where the state must be.
- **ALL CAPS for the banner keyword.** WAITING ON USER / WAITING ON COMPLETION / WORKING. The caps are the visual signal that this is the state line, not prose.
- **One banner, not several.** If multiple things are true, lead with the one that needs the user. WAITING ON USER always wins over WAITING ON COMPLETION — if the user is blocking anything, that is the banner.
- **Never silently wait on the user.** The entire point: a WAITING ON USER state that is not bannered is the bug this skill exists to kill. If you find yourself idle because the user hasn't done something, that fact must already be the last line of your most recent message.

### Heartbeat cadence

Variable, matched to the event horizon — tighter when something is actively progressing and worth watching, longer when waiting on something slow.

- **Floor: ~30 minutes** (1800s). Do not heartbeat more often than that; more is noise. (Established by the user 2026-06-12; adjustable per user.)
- **Active watching** (a build/test progressing in minutes, a drive with frequent state changes): ~30 min.
- **Slow wait** (a long compile, a queue, an overnight job): stretch toward 60 min (3000–3600s).
- **Real-time events do not wait for the heartbeat.** Use watchers (next section) for anything you need to react to promptly. The heartbeat is the "don't lose track / keep the user oriented" backstop, not the primary event channel.

Cache-window note: ScheduleWakeup past 300s pays a prompt-cache miss. Since the floor is already 30 min, every heartbeat pays it — fine, that's the deliberate trade for not over-pinging. Don't pick values just under 300s thinking you're saving cache; the floor governs.

## Watchers — real-time events, not the heartbeat

For anything you must react to quickly (a build finishing, a blocker appearing), arm a Monitor watcher. The heartbeat is too coarse for this.

- **Key watchers on ground truth, not pane text.** The best signal is an artifact: `ls /Applications/Foo.app`, a process count, an exit file. Pane-text greps false-fire on the agent's own prose ("I'll report the build status then" matched a "build status" grep all session). When you must grep a pane, exclude the narration phrases.
- **Cover failure, not just success.** A watcher that greps only the success marker stays silent through a crash. Include the error/hang signatures you'd act on.
- **Stop stale watchers.** When a watcher's premise is gone (the build it watched finished), TaskStop it — a watcher re-emitting a dead event is noise that buries real signal.
- **One concern per watcher.** Don't overload; a focused watcher is easy to reason about and easy to retire.

## Seeing the remote screen (screen capture)

You can visually inspect a remote Mac's screen — essential for GUI verification, TCC-prompt detection, and subjective checks — but only from the right session context.

- **Direct SSH cannot capture the screen.** `ssh host screencapture …` fails with *"could not create image from display"* — the SSH session is not in the user's GUI/Aqua login session and has no window-server access. This is a session-context limit, not a permission you can grant.
- **Capture from inside the Terminal-launched tmux session.** That session IS in the GUI/Aqua context. Run it detached so you don't disturb the user's view, then pull the file back:
  - `tmux new-window -t <sess> -d -n cap 'screencapture -x /tmp/cap.png'`
  - `scp host:/tmp/cap.png /tmp/cap.png` — then Read the PNG (the Read tool renders images visually).
- **Verify it's real content, not black.** A valid full-screen capture is multi-MB; a Screen-Recording-denied capture is a small near-black image (desktop picture only). If you get black, the tmux/Terminal context needs Screen Recording granted (System Settings → Privacy → Screen Recording → the Terminal app that launched tmux).
- **Use it to close the observation loop on GUI work.** Don't depend on a flaky remote agent's prose for "did the window appear / is the prompt up / does it look right" — screencap + Read is ground truth. This is the visual half of the watcher discipline.

## Remote-agent and remote-machine practice

- **Drive remote agents via tmux send-keys + capture-pane.** Send the text literally, then send Enter. A second bare Enter is often needed to submit. Capture the pane to observe; never assume an instruction landed — verify.
- **Observe the process, not just the UI.** A TUI pane can show a stale frame. `ps -o pid,stat,%cpu,etime` tells you the truth: `S+` at ~0% CPU is idle/sleeping; a frozen timer with the process alive but ignoring input is a hang.
- **Match the model to the work.** The machine doing the heavy debugging gets the strongest model; the orchestrating side can run lighter. Flip at phase boundaries (build → debug).
- **Disruptive testing goes to the test machine, never production.** Live GUI tests, synthetic clicks, process kills, permission resets — these steal focus and restart processes. Pin them to a dedicated test box; keep the user's primary surface quiet.

## Lockup recovery

When a remote agent or process hangs (frozen frame, ignores input, alive but not progressing):

1. **Capture state first — never blind-kill.** Grab the process state (`ps stat/cpu/etime`), the pane, the logs, the artifact state. The postmortem needs this.
2. **Then restart to unblock immediately.** Kill the hung process (TERM, then KILL if needed), relaunch fresh, re-brief it from the durable artifacts (feature docs, roadmap, the work already committed). Don't make the user wait on a corpse.
3. **A fresh agent at low context often beats reviving a wedged one near its context limit.** The work that matters should already be captured (committed, on disk); a clean relaunch is cheap.

## Source-of-truth discipline

Fixes made on a test machine are not done until they are back in the source of truth.

- **Review before pulling back.** A fix made to get a build working on machine X may be an X-only hack. Read the diff: is it portable (good — bring it back) or environment-specific (gate it or rework it)? Arch conditionals, derived paths, and capability probes are usually portable; hardcoded machine paths are not.
- **Commit in the canonical repo, not the throwaway tree.** The test-machine working tree is disposable. Apply the reviewed fix to the real source and commit there; let the test machine re-sync.
- **Don't lose incidental improvements.** Build-recipe fixes, helper scripts, and config the remote agent authored to get unblocked are real work — pull them back too.

## Permission / keychain gates

These are almost always WAITING ON USER and are the highest-value thing to banner clearly.

- **Name the exact click.** Which machine's screen, which dialog title, what button. "Always Allow on the codesign keychain dialog on haorui" — not "grant permissions."
- **Do the non-interactive prep first, then gate.** Stage everything that doesn't need the user (build, install, layout, dry-run) so the human step is a single clean action, not a series of interruptions.
- **TCC first-launch is human-only.** Accessibility / Screen Recording / Microphone grants on first launch need a person at the machine. Surface them as WAITING ON USER with the specific permissions and bundle.
- **Coordinate timing.** Confirm the user is at the machine's screen before triggering a launch that will throw prompts; otherwise the prompts sit unanswered and you've burned a cycle.

## Anti-patterns

- **Silent wait on the user.** Idle because the user hasn't acted, with no WAITING ON USER banner in your last message. This is the cardinal sin.
- **Heartbeat without a banner.** A status report whose last line is prose, not a state banner. The user has to read the whole thing to learn they're blocked.
- **Pane-text watchers that false-fire.** Grepping the agent's narration instead of ground-truth artifacts.
- **Polling instead of watching.** Burning turns re-capturing a pane when a Monitor watcher or a ScheduleWakeup heartbeat would do it for you.
- **Leaving fixes on the test machine.** Green build on the test box, nothing committed to the source of truth.
- **Blind-killing a hang.** Restarting without capturing state first — the next hang is now undebuggable.

## Related

- [[bridge]] — the control / sync / claude mechanisms DevOps work runs over.
- [[crank]] — autonomous-progress loop; DevOps is its operational sibling (crank drives the backlog; DevOps drives the machines).
- [[verification]] — tier discipline for what "done" means on a verify item.

---

_v1 draft 2026-06-12 — authored mid-drive (Muxbridge test-machine bring-up). Heartbeat + state-banner rule is the settled core; the methodology sections are seeded from that session and will be refined with the user._
