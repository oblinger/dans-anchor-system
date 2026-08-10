---
description: "made-up list-spine exemplar — one machine-written row per hop"
---

| -[[Harbor Hops]]- | : made-up list-spine exemplar — one machine-written row per hop<br>→ [[DAS]] → [[examples]] → [Harbor Hops](hook://p/Harbor%20Hops)  |
| --- | --- |
| Related | [[FEX Spine Examples]],  [[Harbor Latency Budget]],  [[DAS spine]],   |
| --- | |
| [[Auth Lookup]]  | resolves the caller identity, cache-backed; 25 ms |
| [[Egress]]  | writes the response to the wire; 20 ms since pooling landed |
| [[Payload Assembly]]  | builds the response body; 60 ms, the largest slice |
| [[Route Resolve]]  | maps the request to a backend; 15 ms |
| [[TLS Handshake]]  | negotiates the connection; 40 ms of the budget |

# Harbor Hops
Every hop a Harbor request passes through — one page per hop, in the order they run.

> [!info] Canonical list spine
> A hub that ends in `---`, so **the machine writes one row per child, alphabetically, each carrying that child's own description**. Nothing below the marker is hand-written.
> - **This is what `---` means and `...` does not.** A `...` page collapses every unlisted child into one compact row; `---` gives each child a line of its own with room for a sentence. That per-child sentence is the whole reason to choose it.
> - **The rows above the marker are the author's**, the rows below are the machine's. `Related` is pinned by hand; the five hops are enumerated by HookAnchor from this folder.
> - **It is a classic dispatcher** — the anchor page of its own folder (`Harbor Hops/Harbor Hops.md` with a `.anchor` beside it), dispatching the children it actually contains. That is the normal case, and it is what makes the enumeration below trustworthy: the machine is reading this folder, not a list someone maintained.
> - **No heart.** A pure index's spine is its content — there is nothing to put between the H1 and the table because the table is above the H1. Compare [[Devtools]], which carries both.
>
> The live counterpart is [[Disk]]: two curated rows, then `---`, then ~25 machine-written drive rows, several with real descriptions.
