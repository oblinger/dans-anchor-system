# contacts — macOS Contacts (read)

Read the local macOS **Contacts** database through one defined script, never hand-written AppleScript. No OAuth, no token: Contacts is a local TCC surface like [[io-ical|ical]] and [[io-imail|imail]], and it holds every account that syncs into this Mac — so it outranks any server-side contacts API. A future Google People API surface would be `/io gcontacts`.

**Read-only, deliberately.** Writing to a shared address book is not something an agent should do in passing; `create` and `edit` are absent by design rather than unimplemented.

## Why this exists

Agents were reaching for raw `osascript` against Contacts.app and getting it wrong — no timeout wrapper, ad-hoc output shapes, and no way to tell an empty result from a broken reader. Dan, 2026-08-29: *"we don't want agents doing osascripts raw. They end up doing them wrong… it's better to write scripts down that way. We have defined ways that we access things."* Same principle as `create` taking a JSON file in [[io-ical]].

## Commands

```bash
C="$HOME/.claude/skills/io/scripts/io-contacts"

"$C" search "Oblinger"       # one line per match:  NAME <tab> ORG
"$C" show   "Zuly"           # full record: name, org, emails, phones, born
"$C" count                   # total people in the database
"$C" list                    # everyone, one per line:  NAME <tab> ORG <tab> EMAILS <tab> PHONES
```

`list` is the whole book in one round of Apple Events — four batch reads (`name of every person`, …) joined by index, about 7 s for 2,204 people, several emails or phones joined with `; `, and any line break inside a value flattened so one record is always one line. `search` is now a filter over that same batch read rather than a per-person loop, so a broad query (`search a` → 1,561 rows) returns in the same 7 s instead of dying with AppleEvent -1712 — the failure [[WINNIE Backlog#^T015|WINNIE T015]] hit on 2026-08-30 trying to enumerate the register.

`search` and `show` both take a **name substring**, matched case-sensitively by Contacts' own `whose name contains`. `show` prints every match, blank-line separated — pass enough of the name to narrow it.

## A zero names the corpus

An empty `search` or `show` prints `no match for "X" -- searched N people` on stderr and **exits 1**. That is the point: a zero you cannot distinguish from a broken reader is not evidence of absence. `count` is the same instrument check standalone — if it prints a plausible number, the surface is alive.

## Every query carries a timeout

`with timeout of N seconds` wraps each AppleScript (default 30, override with `IO_CONTACTS_TIMEOUT`). Without one an Apple Event dies at the **120-second default and reports nothing** — which is how a mail query once looked like an empty result rather than a stall ([[io-imail]] § Performance). Contacts is small enough that this should never fire; it is there so a hang reads as a hang.

## Gotchas

- **The `organization` field is sometimes a relationship tag, not an employer.** `Charlie Oblinger` carries `Relative`. Do not read `org` as a workplace without looking.
- **Duplicates are real and common.** `Jeff Oblinger`, `Jeffery Oblinger Oblinger` and `jeff oblinger Sr` are probably one or two people. Contacts is a register in the same sense [[META Register]] means it — many writers, no owner, and drift accumulates. Deduplicate by eye, never by script.
- **Matching is case-sensitive.** `search "oblinger"` and `search "Oblinger"` return different sets; the database itself is inconsistently capitalized (`jeff oblinger Sr`).
- **The name in Contacts beats the name you were told.** Verified 2026-08-29 filing family `@entry` pages: two of three children's surnames were wrong as dictated — `Jasmine Bodenstein` (not Oblinger) and `Zuly Beltran`, where "Zuly" is the *given* name. In [[AT]] the name is the address, so a misspelling is expensive to undo. Look it up.

## Related

- [[AT]] — the vault-side people register; [[Family]] holds the family `@entry` pages.
- [[io-ical]], [[io-imail]], [[io-ihealth]] — the other local Apple surfaces, same no-expiring-auth property.
