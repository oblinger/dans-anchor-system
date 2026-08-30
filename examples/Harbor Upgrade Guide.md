---
description: "made-up table-of-contents heart — a long procedure whose only above-the-fold substance is its own map"
---
:>> [[DAS]] → [[FEX]] → [Harbor Upgrade Guide](hook://p/Harbor%20Upgrade%20Guide) 
# Harbor Upgrade Guide
The operator's procedure for moving a Harbor deployment from one release to the next — eight steps, in the order they must run, with what each one is protecting against.

| Table of Contents |  |
|---|---|
| **[[#1. Read the release note]]** |  |
| **[[#2. Snapshot the index]]** |  |
| **[[#3. Drain the replay queue]]** |  |
| **[[#4. Rotate certificates early]]** |  |
| **[[#5. Upgrade the binary]]** |  |
| **[[#6. Warm the caches]]** |  |
| **[[#7. Verify the latency budget]]** |  |
| **[[#8. Roll back, if you must]]** |  |
| **[[#Why this page is an example]]** |  |

## 1. Read the release note
Every release under [[Harbor Releases]] opens with its deprecations, and the deprecations are the part of the note that an upgrade actually consumes. Read the note for the release you are moving *to*, and if the upgrade skips a release, read every note in between as well: 3.9 → 4.1 removed the legacy auth path that 4.0's note announced and 4.1's note assumes you already know about, so an operator who read only the 4.1 note found the auth path gone with no warning they had seen.

Three things to extract before going further. **The deprecations** — anything your tenants still use is a blocker, not a note. **The index format** — a release that changes it (4.0 did) makes step 2 mandatory rather than merely prudent. **The minimum previous release** — 4.2 refuses to start on an index written by anything before 4.0, and the refusal names the version, which is helpful only if you are reading the log rather than the dashboard.

Write the answers into the change ticket. The point of the ticket is not approval; it is that the person doing step 8 at three in the morning can see what the person doing step 1 knew.

## 2. Snapshot the index
Run [[Harbor Runbook Rebuild Index]] § Snapshot before anything else changes. The index format changed in 4.0 and the rewrite is one-way — a 4.x index will not load on a 3.x binary, so the snapshot is the only road back past step 8, and a snapshot taken after the binary has started is a snapshot of the new format, which is worthless for rollback.

The snapshot takes between four and forty minutes depending on tenant count, and it holds a read lock on the index for the duration. On a standard-tier depot that is invisible; on an enterprise depot with a dozen [[Harbor Tenancy Model|pools]] it shows up as a latency bump on the auth-lookup hop, so do it inside the window, not before it. Verify the snapshot by size against the previous one — a snapshot that is a tenth the size of last month's is a snapshot of an empty index, which the tool does not consider an error.

Keep two. The previous release's snapshot is also the only thing that can rescue you if this release's snapshot turns out to be corrupt, which has happened once and was discovered during a rollback.

## 3. Drain the replay queue
Run [[Harbor Runbook Replay Queue]] to zero before the binary stops. Anything still queued when the old binary exits is replayed against the new binary with the old payload shape, which 4.2 rejects loudly and 4.1 accepted silently — and the second is worse, because a silently mis-shaped payload lands in the index and is not found until a tenant asks why their attachment is blank.

Draining means *zero*, not *low*. The queue drains in the order items were enqueued, so the last item is the oldest failure, and old failures are disproportionately the ones with the unusual payload shapes. Watch the queue depth on the console rather than trusting the runbook's exit code: the runbook exits when it has *submitted* every item, and submission is not completion.

If the queue will not drain — an item that fails on every replay — do not proceed. Move the item to the dead-letter store, note its id in the ticket, and continue. An item that fails on the old binary will not succeed on the new one, and a stuck queue is the most common reason an upgrade window is missed.

## 4. Rotate certificates early
If [[Harbor Runbook Cert Expiry]] shows anything under thirty days, rotate now rather than after. The new binary re-validates the whole chain on first start, and a certificate that was tolerated by a long-running 3.x process — one that validated it eleven months ago and never looked again — is refused by a fresh 4.x process that looks today.

This is the step most often skipped, because thirty days feels like plenty. It is not, for one reason: the rotation itself takes a restart, and if you discover the expiry during step 5 you will be restarting twice inside a window sized for once. Rotating in step 4 costs one restart of the old binary, which you were about to stop anyway.

Tenants who front through [[Harbor Integration Cloudflare|Cloudflare]] have a second chain to check, the one Cloudflare presents to Harbor rather than the one Harbor presents to the world. It is not in the cert-expiry runbook's default scope; pass `--upstream` to include it.

## 5. Upgrade the binary
Per depot, standard tier first. An enterprise depot is upgraded only after one standard depot has served a full hour of real traffic on the new build — the [[Harbor Tenancy Model|tenancy model]] keeps their pools apart, so a bad build on a standard depot cannot reach an enterprise tenant, and the hour is what turns the standard depot into a canary rather than a gamble.

The upgrade itself is a stop, a binary swap, and a start. The start is the slow part: the new binary reads the whole index on first run to rewrite it into its own format, and on a large depot that is the forty minutes from step 2 all over again. Nothing serves during the rewrite. Size the window accordingly, and do not be tempted to start two depots at once to save time — they share nothing except the operator's attention, and the operator's attention is what runs out.

After the start, confirm the version in the log before touching the console. The console caches the version string and has shown the old version for up to ten minutes after a successful upgrade; the log line is written by the running process and cannot be stale.

## 6. Warm the caches
Run [[Harbor Runbook Cache Warm]] on every upgraded depot before opening traffic to it. A cold auth cache after upgrade is indistinguishable from an [[Harbor Runbook Auth Storm|auth storm]] on the dashboards — the same spike in lookup latency, the same climb in Okta calls — and it has paged the on-call twice for nothing, once at a time that turned a routine upgrade into a postmortem.

Warming pulls the last twenty-four hours of distinct tenant ids from the access log and issues one lookup each, which takes about a minute per thousand tenants. It needs the depot to be *started* but not yet *serving*, which is the state the binary is in between step 5's start and the moment you open the load balancer. Do not open the load balancer first.

Check the hit rate on the console before opening traffic: anything above 90% means the warm ran; anything near zero means it ran against the wrong depot, which the runbook allows because it takes a hostname and does not check that the hostname is the one you meant.

## 7. Verify the latency budget
Compare each hop against [[Harbor Latency Budget]] for one hour of real traffic after the load balancer opens. The comparison is per hop, not total: a total under 160 ms can hide a payload-assembly hop over its 60 ms budget if the auth hop happens to be under its own, and the over-budget hop is the one that will breach next week when traffic is not flattered by the post-upgrade lull.

A hop over budget after an upgrade is an S3 in [[Harbor Runbooks]]' scale — not an incident, but not done either. File it before closing the ticket, and name the hop. The one hop that reliably moves on upgrade is payload assembly, because the [[Harbor Integration S3|S3]] client is the piece most releases touch; if it is the only one over, that is expected and the ticket says so.

The hour is a floor. On a Sunday it should be four, because Sunday traffic does not exercise the enterprise pools.

## 8. Roll back, if you must
Stop the binary, restore the step-2 snapshot, start the previous build. There is no in-place downgrade and there never will be — the index rewrite in step 5 is one-way by design — so the snapshot is the whole rollback story, which is why step 2 is not optional and why it is verified by size rather than trusted.

Decide to roll back on evidence, not on nerves. The evidence that justifies it: the version in the log is wrong (the swap did not take), the cache warm cannot reach 90% (the index rewrite is incomplete), or a hop is over budget by more than half (the build is slower, not merely different). Everything else is an S2 or S3 to be worked on the new build, because a rollback re-runs the forty-minute rewrite in the other direction and puts you back at step 5 with less window than you had.

Write down why. The postmortem for a rollback is short and mandatory, and its first line is which of the three pieces of evidence you saw.

## Why this page is an example
The page is long and the reader's first need is *where is the step I am on*, so the table of contents is the heart — it orients rather than carries, and it is regenerated from the headings (`md-toc.py`) rather than written, which is why nothing about it is authored by hand and why it appears only once the page crosses the length floor that makes a map worth having. Specified at [[DAS heart]] § Table of contents.
