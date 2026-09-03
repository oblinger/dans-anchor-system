# rig

**`rig` brings cloud machines up and down. That is all it does.**

| Table of Contents |  |
|---|---|
| **[[#Synopsis]]** |  |
| **[[#What rig is not]]** |  |
| **[[#Two states, not one]]** |  |
| **[[#One namespace]]** |  |
| **[[#The integration contract: an ssh alias]]** |  |
|    [[#How a connection tool consumes this]] |  |
| **[[#Backends]]** |  |
| **[[#`ls` shows everything]]** |  |
| **[[#Configuration]]** |  |
| **[[#Ownership and expiry — ruled 2026-09-03, not yet built]]** |  |
|    [[#The gap this closes]] |  |

It exists because every other tool in the chain assumes the machine already exists. Connection tools take a host you can already reach; experiment frameworks take a remote you have already registered. Something has to make the box first, and until now that something was a human at a cloud console.

## Synopsis

```
rig [--cloud BACKEND] [--agent SLUG] COMMAND [ARGS]

  up    NAME  create if absent, start if stopped, no-op if running
  down  NAME  stop it; disk survives, compute billing stops
  rm    NAME  destroy it, disk and all (--yes required, no undo)
  ls          every machine on every cloud, state and burn rate
  ip    NAME  print the address on stdout, nothing else
  ssh   NAME  refresh the alias and connect (extra args go to ssh)
  reap        stop rig-managed machines that are up but idle
  renew NAME  push the lease out again (default lease_hours)
  gc          destroy owned rigs stopped > frozen_days (asks; --yes)
  keep  NAME  exempt a stopped rig from gc (--days N, default 14)
  name  NAME  print the canonical <prefix><agent>-<local> name

  up    --size TYPE  --zone ZONE  --disk GB  --image FAMILY
  up    --lease HOURS (default 8, <24)  --forever (no lease, loud)
  reap  --idle MIN (default 60)  --load N  --dry-run
  gc    --days N  --yes  --dry-run
  --cloud picks a backend (azure | gcp); default from config
              ls/reap walk every cloud in `clouds:`
  --agent also reads $RIG_AGENT, $BRIDGE_AGENT, or config agent:

  NAME is <prefix><agent>-<local>: lowercase, hyphens, no dots
  (do-a2x-dev; config REQUIRES prefix:, has lease_hours, frozen_days)
  Config: ~/.config/rig/config.yaml
  Exit 0 on success; nonzero with one line on stderr otherwise
```

In use, the point is that the second line needs nothing from the first:

```sh
rig up a2x-dev          # ensure it exists and is running
ssh a2x-dev             # …reachable, because rig wrote the alias
```

## What rig is not

The boundary is deliberate and worth stating, because the temptation to widen it is constant.

| Job | Owner |
| --- | --- |
| Make a machine exist and be reachable | **rig** |
| Drive a machine you already have — shells, sessions, agents | your connection tool |
| Run structured work on it — tasks, experiments, results | your experiment framework |
| Configure what's *installed* on it | your provisioner |

rig deals in cloud credentials, quotas, zones, images, and **billing**. That is a different failure domain from everything else on that list: a failed connection costs a retry, while a failed or forgotten machine costs money and leaves orphans. Keeping it in its own tool keeps that risk in one place.

## Two states, not one

A machine has two independent properties, and conflating them is the most common way to lose money or work:

|  | exists | running |
| --- | --- | --- |
| `up` | creates if absent | starts if stopped |
| `down` | keeps it | stops it |
| `rm` | destroys it | — |

**`down` is not `rm`.** A stopped machine costs nothing for compute but keeps billing for its disk — on a 500 GB volume that is real money for something nobody is using. A destroyed machine costs nothing and takes your work with it. Both are legitimate; picking the wrong one is expensive in opposite directions. `rm` therefore requires `--yes`, and `up` never destroys anything.

Note that clouds use confusing words here. GCE reports a *stopped* instance as `TERMINATED`, which reads like it was destroyed. It was not — `rig up` will start it again.

**`up` is idempotent.** Create if absent, start if stopped, no-op if already running. You do not have to know which case you are in, which is the point: the same command is correct on the first day and every day after.

## One namespace

**Rig names are global and flat.** There is no project, folder, or scope — `dev` means one machine, everywhere, forever. This is a deliberate simplification: a flat namespace needs no resolution rules, and a name that appears in a log or a script means exactly one thing.

Flat namespaces collide, so the convention is a prefix:

```
<agent>-<name>          a2x-dev     tink-build     lumen-scratch
```

**The separator is a hyphen, and that is load-bearing.** The whole point of the namespace is that *one name means one machine in every tool*, and a dot cannot survive the chain:

| Consumer | A dotted name becomes | A hyphenated name becomes |
| --- | --- | --- |
| the cloud (GCE instance name) | rejected — dots are illegal | `a2x-dev` |
| ssh (`Host` alias) | `a2x.dev` | `a2x-dev` |
| tmux (session name) | **silently rewritten to `a2x_dev`** | `a2x-dev` |

tmux's rewrite is the dangerous one because it is silent and undocumented: the session is created, under a different name, and tmux's prefix matching then lets a lookup for `bridge-a2x` quietly land inside `bridge-a2x_dev`. Two tools disagree about what the machine is called while both appear to work. `rig` rejects dotted names outright and tells you the hyphenated form.

**The prefix is whoever owns the machine** — typically the agent that created it. Two agents that both want a `dev` box get `a2x-dev` and `tink-dev` and never collide. Set it with `--agent`, `$RIG_AGENT`, or `agent:` in the config; if the name you pass is not already prefixed and an agent is known, rig prefixes it for you.

This works anywhere there is a notion of a named agent. It does not require any particular knowledge-management system, project layout, or directory convention — just that the humans and agents sharing a cloud account have agreed on their own names.

A name without a prefix is legal, and rig warns. The warning is the whole enforcement mechanism; this is a convention, not a schema.

**Ruled 2026-09-03, ahead of the agent prefix: an owner prefix from config.** Every rig name becomes `<prefix><agent>-<local>` — `do-svp-h100` for Dan — with `prefix:` required in the config. Unlike the agent convention this one *is* a schema: it is how `ls`, `reap` and `gc` know which machines are rig's. See § Ownership and expiry.

## The integration contract: an ssh alias

**rig's output is an ssh alias.** This is the single design decision that makes it compose.

When `rig up` finishes, `ssh <rig-name>` works. rig maintains a block in `~/.ssh/config` delimited by `>>> rig managed block` / `<<< rig managed block` comment markers, and rewrites the stanza inside it on every `up`:

```
Host a2x-dev
    HostName 35.190.146.166
    User oblinger
    IdentityFile ~/.ssh/gcp_sv_dev
```

Because every downstream tool already accepts a host, none of them needs to know rig exists. Your connection tool, your experiment framework, and plain `ssh` all address `a2x-dev` and all keep working.

This also solves a bug that bites everyone eventually: **cloud addresses are not stable.** Stop a machine and start it again and it *may* come back on a different address — sometimes it reclaims the same one, which is worse than always changing, because it means the breakage is intermittent and you will not have built the habit of expecting it. Anything holding the old IP then points at nothing, or eventually at somebody else's machine. Since `up` rewrites the alias every time, the indirection is repaired whenever it breaks, without anyone having to notice.

For the same reason, `down` and `rm` **remove** the alias. A destroyed rig whose `Host` entry survives is a live trap: the cloud recycles that address, so the alias does not fail — it connects to a stranger. This is not hypothetical; it was observed within minutes of destroying a test rig, when the next machine started came up on the dead rig's exact address.

### How a connection tool consumes this

The alias is the entire handoff. A connection tool is handed the rig's name and needs nothing else:

```sh
rig up a2x-dev              # machine exists; alias published
bridge tmux a2x-dev         # tmux both sides, named bridge-a2x-dev
```

One name — `a2x-dev` — is the cloud instance, the ssh alias, and (prefixed) the tmux session on both ends. Nothing has to be looked up or translated, and there is no second identifier to keep in sync.

Two things the connection tool must honour, both learned by breaking them:

- **The alias wins over any host-shortname convention.** A tool that expands a bare name to `<name>.local` for Bonjour will turn a working alias into an unresolvable mDNS lookup. Ask `ssh -G <name>` before guessing.
- **The alias declares the login user; use it.** A cloud VM's account is rarely the laptop user's name. Assuming `$USER@host` is a same-person-both-ends assumption that holds between two of your own Macs and nowhere else.

**A tool that writes its own ssh config cannot consume the alias — feed it `rig ip`.** Some tools generate a private ssh config and connect with `ssh -F`. Pointing such a tool at the alias produces `HostName a2x-dev`, and `HostName` must be a resolvable address: ssh does **not** re-resolve it as another alias, and the private config cannot see `~/.ssh/config`. The symptom is `Could not resolve hostname a2x-dev` from a name that `ssh a2x-dev` connects to happily.

For those, hand over the address instead of the name:

```sh
svx remote add a2x --host "$(whoami)@$(rig ip a2x-dev)"
```

The cost is that such a tool now holds an **address**, not a name, so it goes stale exactly when the alias would have been repaired — after a `down`/`up`. Re-run its registration after restarting the rig, or give the machine a static address if that becomes tiresome.

For the cases that want a raw address, `rig ip <name>` prints the IP on stdout and nothing else, so it composes:

```sh
ssh root@$(rig ip a2x-dev)
curl http://$(rig ip a2x-dev):8080/health
```

## Backends

A backend is an adapter. It translates rig's verbs into one cloud's API and, crucially, **maps rig names to whatever that cloud will accept**.

That mapping is the adapter's problem, not the user's. Because rig names are already hyphenated, the GCE mapping is currently the identity — but the authoritative rig name is also stored in instance metadata, so the mapping stays exact regardless, and any legacy dotted name still recorded from before the hyphen rule resolves correctly. A different cloud with different rules solves it differently; nothing above this layer changes.

The contract each adapter implements:

| Method | Returns |
| --- | --- |
| `up(name, opts)` | create-or-start |
| `down(name)` / `rm(name)` | stop / destroy |
| `ls()` | every machine, with state, size, GPU, address |
| `ip(name)` | address or nothing |
| `ssh_target(name)` | user, host, key |

Adapters register themselves with a `@backend("name")` decorator, and `--cloud` selects one. Two exist: `gcp` and `azure` (added 2026-09-02, the day Dan ruled SportsVisio work moves to Azure). `ls` and `reap` walk every cloud in the config's `clouds:` list, because the machine you forgot is on the cloud you stopped thinking about; the other verbs locate a rig by name across those clouds and fall back to the default backend, so `rig down a2x-dev` needs no `--cloud` even when the default has moved.

**Azure specifics the adapter absorbs.** Every rig gets its own resource group, `rig-<name>`: `az vm delete` removes the VM and leaves NIC, public IP, NSG and the OS disk behind — the disk still billing — and there is no flag that reliably takes all of them, so `rm` is `az group delete` on that group and has nothing to forget. `down` is `deallocate`, never `stop`: a stopped-but-allocated Azure VM keeps billing for compute, which is the Azure spelling of the down/rm trap. A VM found in somebody else's group (the AI backend's sandbox, say) is never group-deleted. Login is `az login --use-device-code` (a plain `az login` opens the personal browser). GPU quota for the SV subscription is centralus only; `az vm list-usage -l centralus` is the reflex when an allocation fails.

**Adapters should stay thin.** Cloud CLIs are already good; an adapter is a place to encode *your* decisions — which image, which key, which zones to try — not an abstraction layer that hides the cloud. Where a cloud's behaviour is genuinely surprising, the adapter absorbs it: the GCE adapter retries across zones on a capacity stockout, because GPU stockouts are routine and the error names the zones that do have capacity.

## `ls` shows everything

`rig ls` lists every machine in the account, not only the ones rig created. Unmanaged machines appear in parentheses under their native names.

This is on purpose. The point of the listing is to notice what is costing money, and a machine you forgot is exactly the machine rig did not create. The footer estimates the burn rate of everything currently running:

```
running burn ≈ $1.00/hr  (≈ $720/mo if left up)
```

Prices are rough and hard-coded per machine type. They are for noticing, not for accounting.

## Configuration

`~/.config/rig/config.yaml` holds defaults so the common case is a bare command:

```yaml
backend: azure
clouds: [azure, gcp]      # what ls / reap walk
agent: a2x
azure:
  subscription: <id>
  location: centralus
  size: Standard_NC40ads_H100_v5
  disk: 500
  image: microsoft-dsvm:ubuntu-hpc:2404:latest
  user: oblinger
  key: ~/.ssh/azure_sv
gcp:
  project: my-project
  zones: [us-east1-b, us-east1-c, us-east1-d]
  size: g2-standard-12
  disk: 500
  user: dano
  key: ~/.ssh/gcp_sv_dev
```

Everything is overridable per invocation (`--size`, `--zone`, `--disk`, `--image`, `--cloud`).

**A note on keys.** rig authenticates non-interactively, so its key must have no passphrase. This is worth stating because a passphrase-protected key fails in a maximally confusing way: ssh offers the key, cannot sign with it, and the server reports `Permission denied (publickey)` — indistinguishable from having no key at all. If you are debugging that error, run `ssh-keygen -y -f <key>`; if it asks for a passphrase, that is your answer.

## Ownership and expiry — ruled 2026-09-03, not yet built

Dan, 2026-09-03, after an H100 billed five idle hours: *"rig should, by default, have a prefix that's in the configuration of rig, and each user can set what their prefix is. That way rig can have commands that just know which things were created by it… by default, when you rig up a machine, it puts the watcher out there."* Four parts:

1. **Owner prefix, required in config.** `~/.config/rig/config.yaml` has `prefix:` (Dan's is `do-`); rig refuses to run without it — no default, no derivation from `$USER`, because a guessed prefix would make `gc` offer to destroy whatever the guess matched. Every rig it creates is named `<prefix><agent>-<local>` (`do-svp-h100`; `rig name h100` prints the canonical form for scripts), on Azure in resource group `rig-<that name>`, tagged `rig-name` as before. **The prefix is how rig knows what is its own to destroy**: `gc` and the frozen nag act only on rig-tagged boxes carrying the configured prefix; `reap` (stop, reversible) still covers any rig-tagged box; everything untagged is listed in parentheses and never touched. Boxes that predate the rule (`a2x-dev`) are still found by the name they carry — `rig up a2x-dev` restarts it rather than making `do-a2x-dev` — but are never `gc`'d, since the prefix is the only evidence of whose they are.
2. **The lease lives on the cloud, set by `rig up` by default.** As built 2026-09-03: on Azure the lease is the VM's own **auto-shutdown schedule** (`az vm auto-shutdown`, a DevTestLab schedule in the rig's group that *deallocates* at a UTC time of day) — it fires with the laptop shut and the session gone, and a Contributor can set it. Default `lease_hours: 8` (config), `--lease H` per rig, `--forever` opts out and says so; `rig renew <name> [--hours H]` pushes it; `rig ls` shows it in a LEASE column, where **`NONE` on a running rig is the line to act on**. Ceiling is 24 h because the schedule is daily. *Down, never rm.* **Not built, and why:** the on-box idle watcher the ruling asked for needs the VM to hold a role that can stop it — a role *assignment*, which Contributor cannot create (checked: Dan is Contributor on `sv-startups-01`). Until someone with Owner grants a self-stop role, idle detection stays with the hourly laptop reaper; the lease covers the walked-away case on its own. GCP has no lease at all (instance schedules need IAM the project does not grant, and SV compute left GCP) — `up --cloud gcp` prints `NO LEASE` and means it.
3. **Zombie sweep for the frozen ones.** A deallocated box still bills its disk (500 GB StandardSSD ≈ $40/month), so stopped-and-forgotten is the slow leak. `up`, `down`, `rm` and `ls` print one nag line when a prefix-owned box has been stopped more than `frozen_days` (3): `rig: 1 frozen rig(s) stopped > 3d, disks billing: do-svp-h100 (9d) — rig gc to destroy, rig keep NAME to exempt`. `rig gc` lists them and asks at a terminal; with no terminal it refuses unless `--yes`, so an agent has to mean it — nothing destroys on its own. `rig keep <name> --days N` (default 14) tags the rig exempt; `rig gc --dry-run` just lists. Stop time comes from the cloud (Azure instance view, GCE `lastStopTimestamp`); a rig whose stop time cannot be read is treated as frozen, not as fresh.
4. **The laptop reaper stays as the second layer**, walking every cloud hourly, for the box whose watcher failed to install or whose identity lost its role.

What this still does not catch: a box nobody created through rig. The nag counts unmanaged running boxes in its burn line (as `ls` does) and leaves them alone.

### The gap this closes

**A rig stays up until someone takes it down.** There is no timeout, no lease, and no automatic teardown. A GPU machine left running bills continuously — for a single mid-range GPU box, on the order of several hundred dollars a month — and the agent that created it will not have a session tomorrow in which to remember.

Until that is built, `rig ls` and its burn line are the only safety net, and they only work if somebody looks. Treat `rig down` as part of finishing, not as cleanup you will get to later.

**The hourly reaper is a backstop, and it was dead for its whole life until 2026-09-03.** `com.oblinger.rig-reap` (launchd, `rig reap --idle 60`, log `~/.config/rig/reap.log`) had exited 1 on all 460 runs since install: launchd's PATH resolved `python3` to `/usr/bin/python3`, which has no PyYAML, and `rig` dies on that before it lists anything. Nobody read the log; the H100 rig `svp-h100` billed five idle hours that night. Fixed by putting the conda interpreter's bin first in the plist's `EnvironmentVariables:PATH`; the next run logged `rig: nothing running` with exit 0. Two lessons: a launchd job's exit status is in `launchctl list`, and a backstop nobody has seen fire is not yet a backstop — kick it once (`launchctl kickstart -k gui/$UID/com.oblinger.rig-reap`) and read the log. Durable on-box expiry is [[Tink P0005]].
