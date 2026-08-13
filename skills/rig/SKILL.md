---
name: rig
description: >
  Cloud machine lifecycle — create, start, stop and destroy GPU/CPU boxes, and publish
  each one as an ssh alias. Verbs: up, down, rm, ls, ip, ssh. GCP today; adapter seam
  for more. Reach for it when work needs a machine that does not exist yet.
user_invocable: false
---

# RIG — Cloud Machine Lifecycle
requires:: external:gcloud
subsystem:: [[DAS Utility Design]] — the Utility group's subsystem profile

`rig` makes a cloud machine exist and be reachable. It does not drive the machine and it does not run work on it — those belong to [[bridge]] and to whatever experiment framework the project uses. rig is a CLI tool, not a slash-command skill; the user invokes it directly as `rig <verb>`, and skills call it when they need a box.

Full user documentation: `docs/RIG.md` — written free of vault conventions so it can be published outside this repo.

## When to reach for it

| Situation | Tool |
| --- | --- |
| The machine does not exist yet | **`rig up`** |
| The machine exists; you want a shell, a session, an agent on it | [[bridge]] |
| The machine exists and is provisioned; you want a structured experiment run | the project's experiment framework (e.g. `svx`) |

The boundary is about failure domains, not tidiness. rig holds cloud credentials, quota, zones and **billing**; a mistake there costs money and leaves orphans, where a mistake in the others costs a retry.

## The verbs

```sh
rig up <name>      # create if absent, start if stopped, no-op if running (idempotent)
rig down <name>    # stop — disk survives, compute billing stops
rig rm <name>      # destroy — requires --yes
rig ls             # every machine in the account, with state and burn rate
rig ip <name>      # bare IP on stdout, for $(rig ip <name>)
rig ssh <name>     # refresh the alias and connect
```

`up` and `down` are power; `up` and `rm` are existence. **`down` is not `rm`** — a stopped machine still bills for its disk, and a destroyed one takes your work with it. Both are right sometimes; the wrong one is expensive in opposite directions.

## Two things an agent must get right

**1. Use your own slug as the name prefix.** The namespace is global and flat, so `dev` means one machine everywhere. The convention is `<agent>.<name>` — `a2x.dev`, `tink.build`. Pass `--agent <slug>`, or export `RIG_AGENT`; rig prefixes a bare name for you when it knows your slug, and warns when it does not. Two agents that both want a "dev" box collide unless this is honoured.

**2. Bring it down when you are finished.** *Nothing expires.* There is no lease, no timeout, no automatic teardown — a GPU box left running bills continuously (order of several hundred dollars a month for one mid-range GPU), and you will not have a session tomorrow in which to notice. Treat `rig down` as part of finishing the work, not as cleanup to get to later. Auto-teardown is designed but unbuilt — [[TINK P0005]].

Before starting and after finishing, `rig ls` is the check: it lists **everything in the account**, including machines rig did not create, and prints the running burn rate. That is deliberate — the machine costing you money is the one nobody remembers making.

## What it gives the rest of the system

**An ssh alias.** After `rig up <name>`, `ssh <name>` works. rig maintains a delimited block in `~/.ssh/config` and rewrites the stanza on every `up`, which is also how it repairs the ephemeral-IP problem — cloud machines almost always return on a new address after a stop/start, and anything holding the old one silently points at nothing.

Because the output is an ordinary ssh host, every downstream tool composes without knowing rig exists.

## Contents

- **`scripts/rig`** — the CLI (put on `$PATH`). Python 3, stdlib plus PyYAML for config.
- **`docs/RIG.md`** — user documentation and the architecture rationale; publication-safe.
- **`~/.config/rig/config.yaml`** — per-backend defaults (project, zones, size, disk, user, key).

## Backends

Adapters register with `@backend("<name>")` and implement `up` / `down` / `rm` / `ls` / `ip` / `ssh_target`; `--cloud` selects one. **`gcp` is the only one implemented** — Azure is expected, and the seam exists now because a second backend is far cheaper to add than to retrofit. Name mapping is the adapter's problem: GCE forbids dots, so `a2x.dev` becomes instance `a2x-dev` with the true name in metadata.

Keep adapters thin. They encode *your* choices — image family, key, which zones to try — not an abstraction over clouds.

## Gotchas

- **rig's ssh key must have no passphrase.** rig authenticates non-interactively. A passphrase-protected key fails as `Permission denied (publickey)` — identical to having no key at all, because ssh offers the key and then cannot sign with it. Diagnose with `ssh-keygen -y -f <key>`: if it prompts, that is the cause.
- **GPU stockouts are routine.** `up` retries across the configured zones; the cloud names which zones have capacity only after the request fails.
- **A cloud's word for "stopped" may read like "destroyed."** GCE reports a stopped instance as `TERMINATED`. It still exists, and `rig up` starts it again.
