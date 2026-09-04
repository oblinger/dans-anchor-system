# contacts — macOS Contacts (read)

Read the local macOS **Contacts** database through one defined script, never hand-written AppleScript. No OAuth, no token: Contacts is a local TCC surface like [[io-ical|ical]] and [[io-imail|imail]], and it holds every account that syncs into this Mac — so it outranks any server-side contacts API. A future Google People API surface would be `/io gcontacts`.

**`io-contacts` itself stays read-only.** Writing to a shared address book is not something an agent should do in passing; `create` and `edit` are absent by design rather than unimplemented. **Writes live in a separate tool with a separate contract — [[io-contacts-repo]]** (§ Writes go through the repo, below).

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

`list` is the whole book in one round of Apple Events — four batch reads (`name of every person`, …) joined by index, about 7 s for 2,204 people, several emails or phones joined with `; `, and any line break inside a value flattened so one record is always one line. `search` is now a filter over that same batch read rather than a per-person loop, so a broad query (`search a` → 1,561 rows) returns in the same 7 s instead of dying with AppleEvent -1712 — the failure [[Winnie Backlog#^T015|WINNIE T015]] hit on 2026-08-30 trying to enumerate the register.

`search` and `show` both take a **name substring**, matched case-sensitively by Contacts' own `whose name contains`. `show` prints every match, blank-line separated — pass enough of the name to narrow it.

## A zero names the corpus

An empty `search` or `show` prints `no match for "X" -- searched N people` on stderr and **exits 1**. That is the point: a zero you cannot distinguish from a broken reader is not evidence of absence. `count` is the same instrument check standalone — if it prints a plausible number, the surface is alive.

## Every query carries a timeout

`with timeout of N seconds` wraps each AppleScript (default 30, override with `IO_CONTACTS_TIMEOUT`). Without one an Apple Event dies at the **120-second default and reports nothing** — which is how a mail query once looked like an empty result rather than a stall ([[io-imail]] § Performance). Contacts is small enough that this should never fire; it is there so a hang reads as a hang.

## Gotchas

- **The `organization` field is sometimes a relationship tag, not an employer.** `Charlie Oblinger` carries `Relative`. Do not read `org` as a workplace without looking.
- **Duplicates are real and common** — but the obvious-looking one is often not the duplicate. `Jeff Oblinger` and `jeff oblinger Sr` share an email *and* a phone: one person, two records. `Jeffery Oblinger Oblinger` shares neither (different email, different phone) and is **a different person** whose doubled surname is a data-entry artifact — which is exactly the record a quick pass would have merged. Contacts is a register in the same sense [[META Register]] means it — many writers, no owner, and drift accumulates. Deduplicate by eye, never by script. Measured over all 2,204 records, [[Winnie Backlog#^T015|WINNIE T015]] 2026-08-30.
- **A shared phone number usually means a shared employer, not the same person.** Of nine phone-only links in that sweep, five were switchboards: 805-542-9330 collected three unrelated SRI colleagues, 781-273-3388 two at BAE. Shared *email* is the reliable identity signal; shared phone is the sweep's main false-positive source.
- **`show` still runs a per-person Apple Event loop and hangs on a broad substring.** The batch-read rewrite landed on `list` and `search` only; `show "Oblinger"` (~20 name matches) blew past 120 s twice. Give `show` a narrow substring, or read the record off `list`.
- **Matching is case-sensitive.** `search "oblinger"` and `search "Oblinger"` return different sets; the database itself is inconsistently capitalized (`jeff oblinger Sr`).
- **The name in Contacts beats the name you were told.** Verified 2026-08-29 filing family `@entry` pages: two of three children's surnames were wrong as dictated — `Jasmine Bodenstein` (not Oblinger) and `Zuly Beltran`, where "Zuly" is the *given* name. In [[AT]] the name is the address, so a misspelling is expensive to undo. Look it up.

## Writes go through the repo, not through a prompt

`scripts/io-contacts-repo` keeps the whole address book as a git repository at `~/ob/data/contacts` — one vCard per contact named by UUID, photos as ordinary image files, an `INDEX.tsv` mapping ids back to names. Writes are a reviewed **plan file** applied between two commits.

```bash
R="$HOME/.claude/skills/io/scripts/io-contacts-repo"

"$R" status                          # repo path, record count, last commit
"$R" sync                            # dump, then commit iff something changed
"$R" apply --plan F                  # DRY by default: shows every row's effect
"$R" apply --plan F --commit         # dump+commit, apply, dump+commit
```

Plan ops: `MERGE`, `SET`, `SETEMAIL`, `DELPHONE`, `SETPHOTO`, `DELETE`.

**Dumps run in a session, on request. Nothing is scheduled, and nothing should be.** Either party may start one — Dan asks, or an agent says it wants to look at Contacts and **waits for a yes**. An agent never triggers a dump silently. Ruled by Dan 2026-09-02: *"That way I know what's happening. Otherwise, it's just gonna pop up on my screen and I'm not gonna know where it's coming from."*

**🚨 Do not rebuild the nightly launchd job.** It existed until 2026-09-02 and was deleted deliberately; `~/ob/data/contacts/RETIRED-nightly-dump.md` carries the full account. In short: an unattended job has no parent app, so macOS attributes its Contacts request to **its own binary** — and every Apple command-line tool is *one* binary hard-linked under **78 names**, so pointing launchd at `/usr/bin/python3` asks for permission as **`git`** and grants it to all 78. It also cannot be cleanly revoked, because `tccutil reset` takes a bundle ID and a bare path has none. And its first 3am firing raised a consent prompt nobody could answer, whose expiry TCC recorded as a **hard denial** that the Automation pane then refused to flip back on.

**A terminal run needs no new permission**, which is the whole reason this works: an interactive process inherits the terminal's existing grant. Only the unattended case ever needed one of its own. If unattended coverage is genuinely wanted later, wrap the script in an **app bundle** with its own bundle ID — never an interpreter.

**Why this replaced an approval prompt.** Ruled by Dan 2026-08-30: *"just make it writable and have a git log … so we don't have to worry so much about making changes."* Approval gates *intent*; the actual risk of a Contacts merge is that it is irreversible and syncs to every device. Version control makes a wrong change a `git revert` instead of a loss, and it covers the changes Dan makes on his own phone, which no approval scheme ever did. A time-boxed "writes are approved for the next hour" was considered and rejected: with ~15 concurrent sessions on this machine it grants write authority to all of them, and it approves an intention rather than an operation.

**Two commits, never one.** The *before* commit absorbs whatever drifted in since the last dump; only then does the *after* commit isolate exactly what the agent did. Squashing them leaves a diff that mixes the agent's change with a week of unrelated phone edits — and *what did the agent do* is the one question the log has to answer.

**Plans target records by ID, never by name.** On a de-duplication task the duplicate name is the thing being repaired, so matching on it is how the wrong record gets deleted. `DELETE` rows additionally carry the reviewed name and refuse if the live record no longer matches. Get ids from `vcf/` filenames or `INDEX.tsv`.

**The repo is local-only** and `init` installs a `pre-push` hook that refuses. It holds ~2,200 people's names, emails, phone numbers and addresses — overwhelmingly other people's data. Off-machine durability comes from restic, which already covers `~/ob`, so a remote would buy exposure and nothing else.

**MERGE does not carry the photo — check the survivor before you merge.** A record shows one image, so choosing between two is a judgement and the tool refuses to make it. The consequence is silent: the merged card simply keeps whichever photo the *survivor* had, **including none**, and the victim's is gone from Contacts. Found the hard way 2026-08-31 — a merge kept a 96×96 snapshot of Dan and dropped a 2160×2162 portrait. Nothing was lost only because the photo was still in the BEFORE commit, which is the recovery path: `git show <before>:photos/<uid>.jpg > out.jpg`, then a `SETPHOTO` row to put it back. Look at both images first; restore with `SETPHOTO` when the victim's is the better one.

### Two measured facts worth knowing before touching photos

- **~23% of the photos in this book cannot be read.** Contacts hands back a `PHOTO` block whose base64 decodes to the ASCII string `Unable to read recordID` — an error report shaped exactly like an image. Measured 2026-08-31: **67 of 291** contacts with a photo. A per-person re-export returns the same placeholder, so it is a condition of the address book, not a bulk-export artifact. `io-contacts-repo` checks decoded bytes against image magic numbers and lists the failures in `PHOTOS-UNREADABLE.tsv` rather than writing 23 bytes of English into a `.jpg`.
- **`SETPHOTO` must read the file `as data`, never `as picture`.** AppleScript's `as picture` coercion goes through a thumbnail representation and stores a **192×192** image whatever it was handed — a 2160×2162 portrait came back 192×192 / 5.5 KB. `read ... as data` hands Contacts the file's own bytes and the full image survives. Measured 2026-08-31 on Dan's card, both directions.
- **Photos dominate an export and must not go inline.** 200 cards export to 3.0 MB of which **96% is base64 photo** from 23 contacts. Stored as separate image files it is ~22 MB once, because git re-stores a photo only when the image changes; inline it would be ~33 MB *every dump*, undeltable and uncompressible.

## Related

- [[AT]] — the vault-side people register; [[Family]] holds the family `@entry` pages.
- [[io-ical]], [[io-imail]], [[io-ihealth]] — the other local Apple surfaces, same no-expiring-auth property.
