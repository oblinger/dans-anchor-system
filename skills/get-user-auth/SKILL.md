---
name: get-user-auth
description: >
  USE WHEN A PASSWORD OR INTERACTIVE AUTH IS NEEDED FROM THE USER — keychain
  password, sudo, login/unlock, code-signing key authorization, a 2FA tap, a
  GUI permission/trust dialog, or any credential the agent cannot supply itself.
  The preferred pattern: trigger the auth prompt **in the user's GUI session**
  (so it actually appears on their screen), immediately **screen-grab to verify**
  the right window is up in the right place, surface a **bold USER ACTION
  callout** that names the exact window title and steps, then **poll every ~60s**
  while **re-printing the callout each cycle** so it never scrolls off — resuming
  the moment the user has done it. Especially required when driving a remote/GUI
  machine over ssh, where the agent cannot type the password itself.
user_invocable: true
---

# get-user-auth — get a password / interactive auth from the user, the right way

When you need a credential or interactive authorization that **only the user can
provide** — a keychain/login password, `sudo`, a code-signing key authorization,
a GUI "Always Trust" / permission dialog, a 2FA tap — do **not** just print
"please run X and type your password." Drive it: put the prompt on the user's
screen, verify it landed, tell them exactly what to do in an unmissable callout,
and watch for completion so you continue the instant they're done.

## The hard constraint that motivates this skill

**Processes you launch over ssh are session-isolated from the target machine's
GUI (Aqua) session.** They **cannot** present GUI dialogs on the console,
**cannot** `screencapture` the console (TCC-blocked → `could not create image
from display`), and **cannot** reach the GUI session's unlocked keychain
(`codesign` over ssh fails `errSecInternalComponent`). So you can never "just
pop the dialog" or "just screen-grab" from an ssh shell. The fix is to launch
**inside the user's GUI session** via `open` (`open -a Terminal <script>.command`,
`open -a "<App>"`, `open <file>`), which LaunchServices runs in the logged-in
console session where dialogs render and the keychain is reachable.

(See `[[project_muxux_haorui_obutils_pathdep]]` for the concrete haorui case
this skill was distilled from.)

## Runbook

### 1. Pop the prompt in the user's GUI session

Build a tiny self-describing script and open it in the user's GUI session — do
**not** run the auth-needing command directly over ssh.

```bash
# On the target machine, write a .command script with on-screen guidance:
cat > /tmp/<task>.command <<'SCRIPT'
#!/bin/bash
clear
echo "============================================================"
echo "  <TASK NAME>"
echo "  <NAME> — type your <which> password at the prompt below."
echo "  (It will NOT echo as you type. Then press Return.)"
echo "============================================================"
<the command that needs auth>      # e.g. security set-key-partition-list …
echo "rc=$?  — you can close this window."
SCRIPT
chmod +x /tmp/<task>.command
open -a Terminal /tmp/<task>.command   # ← runs in the GUI session; prompt appears on screen
```

For a pure GUI app step (e.g. Keychain Access trust), `open -a "<App>"` instead,
and name the exact navigation in the callout (step 3).

Pick a script filename / window content that is **identifiable on a screen-grab**
(a distinctive banner line) so step 2 can verify it.

### 2. Screen-grab to VERIFY the window is up and in the right place

**Immediately** after `open`, capture the target's screen and look at it
yourself — confirm the intended window/app is frontmost and in the correct pane,
before you tell the user to act.

```bash
ssh <host> 'screencapture -x -t jpg /tmp/auth-verify.jpg'   # local machine: screencapture works directly
scp <host>:/tmp/auth-verify.jpg <scratchpad>/auth-verify.jpg
# then Read the image and confirm the right window/title/pane is showing.
```

- **If the grab succeeds:** Read it, confirm the prompt window is present and
  focused. If it's missing/behind/in the wrong pane, fix (re-`open`, raise it,
  point the user at the right one) BEFORE asking them to act.
- **If the grab is blocked** (`could not create image from display` — the ssh/TCC
  isolation above): say so honestly, and fall back to a **process-liveness /
  state probe** as your verification (e.g. `pgrep -fl <cmd>` to confirm it's
  waiting on input, or read the script's tee-log). Never claim a window is on
  screen if you couldn't verify it — ask the user to confirm it appeared.
- **The grab is authoritative for "is the window there," the completion signal is
  authoritative for "did they finish."** A fast user can answer before your grab
  fires — so a grab that shows *no* dialog does **not** mean it failed: check the
  process/output first (`button returned:OK`, rc=0, state changed). Only if the
  process is still **alive** AND the grab shows no dialog is it likely hidden
  behind another window — then raise it (`open` again / AppleScript activate)
  before pointing the user at it.
- **Privacy: the grab captures the user's WHOLE screen** (private messages, mail,
  calendars, anything open). Use it **only** to confirm the target window/pane —
  do not read, quote, or surface unrelated on-screen content, and **delete the
  grab** as soon as you've verified. Treat it like a credential: minimal,
  single-purpose, discarded.

### 3. Surface a bold USER ACTION callout — name the window + the steps

On your side, emit one unmissable callout. It MUST:
- Lead with **USER ACTION** in bold (a 🔔 helps).
- **Name the exact window/app title** the user should look at (the menu/title
  bar text) so they pick the right one among open windows.
- Give the **precise steps** (what to type / click), and that the password won't
  echo.
- Name the **machine** ("on haorui's screen") when it's not the local one.

```
🔔 **USER ACTION** — on **<machine>**'s screen

A Terminal window titled **"<exact title>"** is open and waiting.
→ Type your **<which>** password and press **Return** (it won't show characters).

Tell me "done" when you've entered it.
```

### 4. Wait — poll ~every 60s AND re-print the callout each cycle

Watch for completion so you resume the moment the user finishes — but keep the
instruction visible the whole time (chat scrolls; the ask must not vanish off the
top).

- **Poll about once a minute** (60s; not faster — it just spams) for a concrete
  completion signal: the auth process exited 0, the script's tee-log shows
  success, or the state you needed changed (`codesign` probe now passes, the
  mount appeared, etc.). Use a background poll loop or `ScheduleWakeup`.
- **On every poll cycle, RE-PRINT the USER ACTION callout** (verbatim, step 3) so
  it stays pinned at the bottom of the conversation and never scrolls off.
- Also accept an explicit "done" from the user as the signal (don't force them to
  wait for your poll).
- **Verify, don't trust, the "done."** When the signal fires (or the user says
  done), re-run the concrete probe to confirm the auth actually took before
  continuing — the user may have typed the wrong password or hit Cancel.

### 5. Continue

Once verified, proceed with the work that needed the auth, and tell the user it
went through. If it did **not** take (wrong password / cancelled), re-surface the
callout (step 3) and loop — don't silently move on.

## Anti-patterns

- ❌ Printing "run this and type your password" and moving on (no GUI pop, no
  verify, no wait) — the user loses the instruction and you don't know when
  they're done.
- ❌ Trying to `screencapture` or present a dialog over ssh and reporting failure
  as if the user's machine is broken — it's session isolation; use `open`.
- ❌ Claiming "the password prompt is on your screen" without having verified it
  (grab or liveness probe) — confirm or say you couldn't.
- ❌ Polling every few seconds (spam) or never (you stall). ~60s, re-printing the
  ask each time.
- ❌ Asking for the password in chat. A credential in chat is compromised — see
  `[[feedback_credential_in_chat_rotate]]`. Always route it through the user's
  own GUI prompt; never have them paste it to you.
