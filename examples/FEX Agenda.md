---
description: "strategy for Harbor — why the scheduler exists, what winning looks like, and the approach we are betting on"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[examples]] → [FEX Agenda](hook://p/FEX%20Agenda)
# FEX Agenda
The strategic frame for [[HBR|Harbor]] — why this activity exists, what winning looks like, and the approach we are betting on. Worked example for [[DAS Agenda]].

_Example only — this is a reference artifact for the [[HBR]] example world, not a live strategy._

## Purpose

Harbor exists because small engineering teams keep rebuilding the same thing: a way to run recurring jobs that is more accountable than `cron` and less operational overhead than Airflow. The teams we have in mind run five to fifty scheduled jobs, have no dedicated platform engineer, and currently discover failures when someone notices a missing report.

Harbor serves the engineer who owns those jobs. Not the platform team that would run a scheduler as a service, and not the analyst who wants a visual DAG builder — those are adjacent products with different buyers.

## Success — what "won" looks like

Twelve months from GA:

- Three teams outside our own company run Harbor in production on jobs they would be paged for.
- A new user gets from `install` to a scheduled, retrying, notifying job in under ten minutes without reading more than the quickstart.
- Job failures reach a human through a configured channel within one minute, in every case, without the user having built the notification path themselves.
- We have turned down at least one feature request that would have pulled us toward the platform-team buyer, and can point to the Constraints section as why.

The last one is a success criterion, not a joke: an unfocused scheduler is the failure mode the market is already full of.

## Approach

**CLI-first, single-host, notification-complete.**

We win by being the tool an engineer can adopt alone, on a machine they already have, in an afternoon. Three commitments follow from that:

1. **The CLI is the product**, not a client for a server. Configuration is a file in the user's repo; state is on disk. There is nothing to operate.
2. **Reliability features ship before capability features.** Retry with backoff, failure notification, and durable job history come before task groups, priorities, or a plugin system. A scheduler that runs exotic topologies unreliably is worth less than one that runs simple jobs you can trust.
3. **Adoption is bottom-up.** We optimize the first ten minutes, not the enterprise evaluation. Distribution is via engineers telling other engineers, which means the quickstart and the failure messages are marketing surfaces.

The bet: reliability plus zero operational overhead beats capability for this buyer, and the buyer is large enough. If that is wrong, we will see it as steady adoption that stalls at hobby use.

## Constraints

- **Single-host through v2.** Multi-host coordination is parked ([[FEX Icebox]]); it changes the state model and the operational story simultaneously, which is the change we are least able to absorb.
- **No hosted service.** We are not taking on running other people's jobs. This removes an obvious revenue path, and we accept that.
- **Two engineers, part-time, through GA.** Anything that needs a dedicated frontend or a dedicated ops person is out of scope by construction.
- **Python 3.11+, no compiled extensions.** Install must be `pip install` on a stock machine; this rules out some performance work we would otherwise want.
- **We do not chase the platform-team buyer.** Multi-tenancy, quotas, and RBAC are the shape of that product; each is individually reasonable and collectively a different company.

## Cadence

**Quarterly, joint.** The user and the agent re-read this Agenda together at the start of each quarter, before the Roadmap's next milestone block is planned. The agent additionally flags it during any `/design` pass that would change the § Constraints — a constraint being relaxed is a strategy change, not a scope change, and it gets ratified here first.

## Open Questions

- **Q1** — Does "notification-complete" include an inbound status endpoint (something external can poll), or only outbound delivery? Outbound-only is simpler and matches the single-host constraint; inbound is what a monitoring integration would ask for. Deferred until a real integration request arrives.

## History

- **2026-04-21** — Added the "turned down a platform-team feature" success criterion after the multi-tenant request in [[FEX Icebox]] surfaced how attractive that direction looks in the moment.
- **2026-03-02** — Chose CLI-first over a server-plus-client architecture. The deciding argument was the ten-minute adoption target, which a server model cannot hit.
- **2026-02-14** — First draft. Purpose and buyer definition ratified; Approach was one paragraph and unnamed at this point.
