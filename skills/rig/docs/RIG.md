# rig

**`rig` brings cloud machines up and down. That is all it does.**

It exists because every other tool in the chain assumes the machine already exists. Connection tools take a host you can already reach; experiment frameworks take a remote you have already registered. Something has to make the box first, and until now that something was a human at a cloud console.

## Synopsis

```
rig [--cloud BACKEND] [--agent SLUG] COMMAND [ARGS]

  up    NAME  create if absent, start if stopped, no-op if running
  down  NAME  stop it; disk survives, compute billing stops
  rm    NAME  destroy it, disk and all (--yes required, no undo)
  ls          every machine in the account, state and burn rate
  ip    NAME  print the address on stdout, nothing else
  ssh   NAME  refresh the alias and connect (extra args go to ssh)
  reap        stop rig-managed machines that are up but idle

  up    --size TYPE  --zone ZONE  --disk GB  --image FAMILY
  reap  --idle MIN (default 60)  --load N  --dry-run
  --cloud defaults to gcp, the only backend implemented
  --agent also reads $RIG_AGENT, $BRIDGE_AGENT, or config agent:

  NAME is <agent>-<local>: lowercase, hyphens, no dots (a2x-dev)
  Config: ~/.config/rig/config.yaml
  Exit 0 on success; nonzero with one line on stderr otherwise
```

In use, the point is that the second line needs nothing from the first:

```sh
rig up a2x-dev          # ensure it exists and is running
ssh a2x-dev             # …and it's reachable, because rig wrote the alias
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
bridge tmux a2x-dev         # tmux session on both sides, named bridge-a2x-dev
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

Adapters register themselves with a `@backend("name")` decorator, and `--cloud` selects one. Today only `gcp` is implemented. Azure is expected next, which is why the seam exists now rather than later — a second backend is much cheaper to add than to retrofit.

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
backend: gcp
agent: a2x
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

## Known gap: nothing expires

**A rig stays up until someone takes it down.** There is no timeout, no lease, and no automatic teardown. A GPU machine left running bills continuously — for a single mid-range GPU box, on the order of several hundred dollars a month — and the agent that created it will not have a session tomorrow in which to remember.

Until that is built, `rig ls` and its burn line are the only safety net, and they only work if somebody looks. Treat `rig down` as part of finishing, not as cleanup you will get to later.
