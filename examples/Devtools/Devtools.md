---
description: example grouped-dispatch collection (> 15 members)
---

| -[[Devtools]]- | : example grouped-dispatch collection (> 15 members)<br>→ [[DAS]] → [[FEX]] → [Devtools](hook://p/Devtools)  |
| --- | --- |
| Related | [[Bridges]] (flat variant),  [[DAS Dispatch Table]],  [[DAS progressive-disclosure]],  [[FEX]], |
| [[Devtools Build\|Build]]+ | [[Devtools Compile\|Compile]],  [[Devtools Bundle\|Bundle]],  [[Devtools Watch\|Watch]],  [[Devtools Cache\|Cache]],   |
| [[Devtools Test\|Test]]+ | [[Devtools Unit\|Unit]],  [[Devtools E2E\|E2E]],  [[Devtools Coverage\|Coverage]],  [[Devtools Fuzz\|Fuzz]],   |
| [[Devtools Ship\|Ship]]+ | [[Devtools Release\|Release]],  [[Devtools Sign\|Sign]],  [[Devtools Publish\|Publish]],  [[Devtools Rollback\|Rollback]],   |
| [[Devtools Observe\|Observe]]+ | [[Devtools Logs\|Logs]],  [[Devtools Metrics\|Metrics]],  [[Devtools Trace\|Trace]],  [[Devtools Alert\|Alert]],   |
| ... |  |

# Devtools
The team's development tooling — a collection big enough to group.

| Stage | What it does | Gate it enforces | Typical wall-clock |
|---|---|---|---|
| **Build** | Compile, bundle, watch, cache | Nothing ships that does not compile clean | 40 s cold, 3 s warm |
| **Test** | Unit, E2E, coverage, fuzz | Coverage may not fall below the previous release | 6 min |
| **Ship** | Release, sign, publish, rollback | Every artifact signed; rollback proven before publish | 90 s |
| **Observe** | Logs, metrics, trace, alert | An alert exists for every gate above | continuous |

The four stages are a pipeline, not a menu — **Observe is what makes the other three trustworthy**, because a gate nobody watches is a gate that quietly stops firing. That is why it is a peer stage rather than a footnote under Ship.


> [!note] Canonical two-level spine
> A hub whose group rows are **themselves pages**, each with its own spine and its own children. That is the "two-level" part — this page is one node in a tree of containers, not a flat list wearing headings.
> - **Each group-row label is a link** (`[[Devtools Build|Build]]`) *down* to that group's own page. The members beside it are a hand-pinned **preview**; the full list lives on the group's page.
> - **`+` marks the label as an expandable container**, not a leaf. That marker is what separates this shape from a [[Harbor Runbooks|grouped spine]], where the labels are plain text and every child is already in this folder.
> - **It still ends in a catchall**, so a child that has not earned a stage yet lands in `...` rather than vanishing.
>
> **The heart here is the pipeline table, not the masthead.** The masthead routes you to four other pages; the heart says what this page is *about*. Both are tables, and telling them apart is the thing this example exists to teach. Only 13 pages vault-wide are two-level; it is the rarest hub shape and the one that earns its keep only past ~15 children.
