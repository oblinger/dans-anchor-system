---
name: buy
description: >
  Given a known product (model + identifier), find verified buy locations across major retailers,
  drive a real browser via ctrl (NOT WebFetch / curl / Playwright — they're all bot-blocked by
  every major retailer's bot-wall), confirm each landing page is a real product page for the
  exact model the user wants, capture current price + buy-button presence + stock + promos,
  and recommend the best place to purchase with confidence. Retries per retailer when the first
  candidate URL is invalid; keeps the best verified page per company. Use when the user names a
  specific product to purchase: "what's the best price on the {X}", "where should I buy {X}",
  "buy {X}". Sibling of /find (identifies products) / /profile (profiles them) / /survey
  (compares them). v1: skeleton — fleshed-out section is § Page-validity verification and
  § Per-retailer retry loop; everything else is the obvious shape.
tools: Read, Write, Edit, Bash, WebSearch
user_invocable: true
---

# Buy — Best Price + Verified Buy Location
requires:: vault, external:ctrl
subsystem:: [[DAS Search Design]] — the Search group's subsystem profile

Skill spec for `/buy <product>` — walks major retailers for a known product, verifies real product pages via real-Safari fetching, and recommends the best place to purchase with stock + price + seller captured.

`/buy <product>` walks the major retailers selling a known product, drives **real Safari** via `ctrl jpage` to bypass bot-walls, verifies each landing page is actually a product page for the requested model, and recommends where to purchase.

**Critical constraint — fetch wall** (this is the lesson the v0 attempt of this skill paid for):

> WebFetch, curl, Playwright headless, and `ctrl jjpage` are ALL bot-blocked by Dell, Amazon, Best Buy, Walmart, Adorama, B&H, Abt, CDW, Provantage. The only fetcher that works is **real Safari driven via `ctrl jpage`** — it uses the user's actual browser session with cookies + JavaScript, and retailers serve it like a normal user. Do not propose any other fetcher; do not "fall back" to WebFetch when ctrl seems slow. Slow but working beats fast but blocked.

## Where this runs — haorui, not the laptop

**All purchasing happens on haorui.** That machine holds the logged-in retailer sessions (Amazon as "Daniel"); the laptop does not. Connect first, then drive `ctrl` over there:

```bash
~/.claude/skills/bridge/bridge tmux haorui
tmux send-keys -t bridge-haorui '<cmd>' Enter
tmux capture-pane -t bridge-haorui -p
```

**The division of labor is fixed: the agent researches and stages; the user buys.** Never place an order, never complete a checkout. The deliverable is a set of verified product tabs open on haorui, each sitting on a live Add-to-Cart button, so the user can walk them in one pass and decide.

### Delivery — stage tabs, don't just report

`ctrl tab <url>` opens a candidate without stealing focus, so a whole finalist set can be staged in order. Do that for **every** finalist, not only the winner — the user's rhythm is to go through the tabs and pick, and a recommendation they can't click is friction. Order the tabs to match the comparison table in chat, then `screencapture -x` to confirm they actually landed before reporting done.

### Gotchas (paid for on the first live run, 2026-07-24)

- **Safari needs `AllowJavaScriptFromAppleEvents`** or every `ctrl jpage` errors out. One-time fix, already applied to haorui: `defaults write com.apple.Safari AllowJavaScriptFromAppleEvents -bool true` plus `IncludeDevelopMenu`, then restart Safari.
- **`ctrl jpage`'s extractor silently drops Amazon order-card and product content** — it returned 10 nav blocks from a page listing 81 orders. Get real content via `osascript` → `do JavaScript "document.body.innerText"`, or ship a JS file and run it. **Escaping inline JS through `tmux send-keys` mangles it — `scp` the script instead.**
- **Amazon order-search ignores `&startIndex=`** — pages 2+ silently re-render page 1. Verify pagination advanced before claiming you read the full history.
- **A screengrab of haorui's screen is ground truth.** When extraction looks empty or wrong, look at the actual page before concluding anything about it.

## When to Use

- User says: *"where should I buy {X}"*, *"best price for {X}"*, *"buy {X}"*, *"check prices on {X}"*.
- User has already identified the specific product (model number, full name). For "which monitor should I buy" → `/survey` first.
- Slash-only — "buy" is too common a word to be a DMUX prefix-trigger.

## Required input

A specific product the user wants to purchase. Must include enough to disambiguate:

- Brand + model number (best): *"Dell U3225QE"*
- Brand + full product name: *"Dell UltraSharp 32 4K Thunderbolt Hub Monitor"*
- Bare model number if globally unique: *"U3225QE"*

If the user names something ambiguous (*"a Dell monitor"*), one inline question: *"Which model?"* — then proceed.

## Per-retailer candidate list (v1 default)

Walk these retailers in order. The list is the v1 default for US consumer electronics; refine per-category in future versions.

```
dell        — direct manufacturer
amazon      — marketplace + Amazon direct
bestbuy     — big-box retail
newegg      — electronics-focused, has 3P sellers
bh          — B&H Photo (NYC; specialist)
adorama     — competitor to B&H; often runs sales
walmart     — big-box + marketplace
costco      — members-only; sometimes lowest with longer return window
microcenter — physical stores; sometimes in-store-only deals
abt         — Midwest specialist, white-glove
cdw         — business reseller
provantage  — business reseller
ebay        — used / open-box (only if user opts in)
```

Per-category overrides (future): groceries, books, software, furniture, automotive, etc.

## Runbook

### 1. Resolve product identity

Confirm the model number + canonical name. If the user gave only a model number, do a quick `WebSearch` for `"<model>"` to confirm the brand + full name. Surface the canonical identifier in chat and ask the user to confirm — one terse line.

```
Resolved: Dell UltraSharp 32 4K Thunderbolt Hub Monitor — U3225QE. Right product? (y/n)
```

### 2. Discover candidate URLs per retailer

For each retailer in the v1 list, build candidate URLs in priority order:

1. **Search-result hit** — `WebSearch` for `<product> site:<retailer-domain>`. The first product-page hit is candidate #1.
2. **Retailer-internal search URL** — fall back: `https://<retailer-domain>/search?q=<model>` (or the retailer's known search URL pattern). The search-results page is candidate #2.
3. **Web search for "buy {product} at {retailer}"** — candidate #3 when both above fail.

Each retailer gets at most 3 candidate URLs to try, in priority order.

### 3. Verify each candidate IS a product page (CORE LOOP — load-bearing)

For each candidate URL, drive Safari via `ctrl jpage` and inspect the result. Skip any other fetcher.

```bash
ctrl jpage "<candidate-url>" --output /tmp/buy/<retailer>.json
```

Then run **page-validity verification**:

#### Page-validity ladder

A candidate is **VALID** (is a real product page for the requested model) iff:

- **Title test:** title contains the product identifier (`<model-number>` or a distinctive multi-word fragment of the canonical name), AND
- **Not a bot-wall:** title is NOT one of `Access Denied`, `Just a moment...`, `Robot or human?`, `Pardon Our Interruption`, `Are you a robot?`, `Checking your browser`, OR a generic 4xx page, AND
- **Not a category/search page:** title or H1 contains the product identifier specifically, not just the brand name; presence of a price, an "Add to Cart" / "Buy Now" / "Add to Bag" button, or a SKU code in the page body increases confidence.

A candidate is **INVALID** if:

- **404 / not found** — title `Page Not Found`, `404`, or HTTP 404 (visible in jpage output).
- **Wrong product** — title contains a different model number (e.g., `U3223QE` not `U3225QE`).
- **Search-results page** — title is `Search results for "..."` or contains `<N> results found`; body has multiple distinct product cards instead of one.
- **Cart / checkout / home** — title is `Shopping Cart`, `Checkout`, `Sign In`, the retailer's homepage.
- **Bot-wall page** — title matches the not-a-bot-wall blocklist above.

A candidate is **BLOCKED** (different from INVALID) when:

- Title is bot-wall content (`Access Denied`, `Just a moment...`, etc.) — the URL probably points at the right product but Safari got a challenge response. **Treat the same as INVALID for retry purposes** — try the next candidate — but mark the retailer's final status as `BLOCKED` not `NOT_FOUND` if all candidates hit bot-walls. Bot-walls usually indicate the URL is right but the fetcher couldn't pass; the user can click the tab manually.

#### Per-retailer retry loop

For each retailer, walk candidates in priority order. On the first VALID candidate, capture and stop. Pseudo:

```
for retailer in RETAILERS:
    state = NOT_TRIED
    best  = None
    for candidate in candidates(retailer):
        result = ctrl_jpage(candidate)
        verdict = validity(result)
        if verdict == VALID:
            best  = capture(result)
            state = VERIFIED
            break
        elif verdict == BLOCKED:
            state = BLOCKED  # but keep trying — next candidate might pass
        elif verdict == INVALID:
            state = NOT_FOUND
            continue
    record(retailer, state, best)
```

Order matters: VALID wins over BLOCKED wins over NOT_FOUND. Once a retailer has a VALID candidate, you're done with that retailer — do not check other candidates from the same company even if they might be cheaper (that's a per-page concern, handled in step 4).

#### Best option per company

If a retailer has multiple product pages for the same model (e.g., Walmart often has the single unit, a 2-pack bundle, a docking-station bundle), the **first** VALID hit from step 2's priority order wins — by construction it's the highest-relevance search result, usually the canonical single-unit listing. If the captured page turns out to be a bundle and the user wants the single unit, surface this in chat and offer to retry that retailer with a more specific search.

If a single retailer page shows multiple sellers (Amazon, Newegg often do), capture the **cheapest seller with the buy button enabled** as the retailer's best price. Note the seller in the recommendation.

### 4. Capture per VALID page

From the jpage JSON, extract:

- **Price** — first `$NNN.NN` pattern near "price" / "sale" / current-price-class keywords.
- **Regular price** (if present) — strikethrough or `was:` price for sale comparison.
- **Buy button** — text contains `Add to Cart`, `Buy Now`, `Add to Bag`, `Place in Cart`, `Buy It Now`, or similar; verify the button is not `Notify Me`, `Out of Stock`, `Pre-order`, `See Similar`.
- **Stock** — text contains `In Stock` / `Limited` / `Out of Stock` / `Backorder` / `Pre-order` / `Ships in N days`.
- **Seller** — for marketplaces, who's actually selling (Amazon direct, Newegg direct, 3P seller name + rating).
- **Promos** — coupons, rebates, financing, free shipping, member discounts.
- **Shipping** — free vs $X, estimated arrival.

Store as a JSON record per retailer.

### 5. Recommend

Sort verified retailers by **effective total cost** (price + shipping − discounts), with tiebreakers:

1. Lowest effective cost wins.
2. Tiebreak: first-party (manufacturer/retailer direct) > 3P with high rating > 3P with mid rating.
3. Tiebreak: in-stock > limited > backorder.
4. Tiebreak: return policy length (longer wins).

#### Consumables rank by cost per unit, not lowest ticket

**For anything bought by the serving** — tea, coffee, razors, supplements, paper goods — "lowest effective cost" is the wrong sort key, and pack sizes make ticket price actively misleading. First ask which regime applies:

- **Unvalidated** (never bought it, might not like it) → cheapest *small* quantity to trial. Breadth of variety is a plus here.
- **Validated** (established that they like it) → largest sensible pack, sorted by **$/unit**. This is a restock; unit economics is the only axis that matters.

Always show a **$/unit column** so the comparison is legible either way. Watch for per-count math that counts non-comparable items — a 48-bag tea pack bundled with 20 honey sticks reports $0.39/count but is $0.55 per actual tea bag.

Missing this cost a wrong recommendation on 2026-07-24: ranked a 44-flavor sampler over the 88-count on lowest ticket + widest discovery, when the product was already validated and $/bag was the real criterion.

#### Screen on hard constraints BEFORE ranking on unit cost

A dietary or physical constraint — decaf, gluten-free, unscented, no salt added, a size that has to fit — is a **filter applied to the candidate set first**, never a tiebreaker inside the ranking. Establish the constraint set for the category before pricing anything, then rank only the survivors by $/unit. A perfect unit price on a product the user can't actually consume is a total loss, not a near miss.

**On variety and assortment packs, verify the contents, not the title.** Marketing copy names the count and the vibe, not the constraint — "44 unique flavours" concealed that the pack was mostly caffeinated. Open the flavor list or the ingredient panel and confirm every item clears the filter, or state plainly that the composition couldn't be verified.

Cost a second wrong recommendation on the *same product line*: the 2026-07-24 Twinings 88-count won on $/bag and turned out to be predominantly caffeinated for a user who drinks decaf. The 2026-08-01 replacement run screened to decaf first, then ranked — and the winner was deliberately **not** the cheapest per bag.

#### One unvalidated item at a time

On an unvalidated consumable, recommend **a single pack and stop** — don't stage a companion buy, a bulk tier, or a second flavor in the same order. Bulk pricing and "while we're here" bundles are only earned *after* a verdict. Until then every extra unit rides on the same unverified assumption, so one wrong assumption spoils the whole order instead of one pack of it.

This compounds with the constraint filter above: the 2026-07-24 tea order bought three products at once on the untested premise that caffeine didn't matter, and all three landed wrong together. The follow-up bought exactly one pack, explicitly holding the re-buy until the user has tried it.

Say the holding pattern out loud in the recommendation — *"one pack now; tell me the verdict and I'll size the restock"* — so the user knows the small order is a deliberate probe rather than an oversight.

Surface a table to the user:

```
Verified  |  Retailer  |  Price (effective)  |  Buy  |  Stock  |  Seller
-----------|----------|--------------------|-------|---------|--------
VERIFIED   | Adorama  | $749.00            | ✓    | In stock| Adorama direct
VERIFIED   | Newegg   | $788.00            | ✓    | In stock| Technology Traders (3P, 4.3★)
VERIFIED   | Best Buy | $949.99            | ✓    | In stock| Best Buy direct
VERIFIED   | Dell.com | $1,029.99          | ✓    | Limited | Dell direct
BLOCKED    | B&H      | could not verify   | ?    | ?       | (Cloudflare blocked Safari extraction; click tab to see)
NOT_FOUND  | Costco   | not stocked         | —     | —       | —
```

Plus a one-line recommendation: *"Adorama at $749.00 — biggest sale (33% off list), shipping free. If Adorama feels sketchy for this much, Newegg via Technology Traders at $788 is the safe pick — verified 3P seller with 4.3★, free 30-day returns."*

### 6. Stage every finalist as a tab on haorui

Not just the winner — the whole shortlist, in the same order as the comparison table, so the user can go through them in one pass:

```bash
for A in {asin-or-url-list}; do ctrl tab "{url}"; sleep 2; done
screencapture -x /tmp/buy/tabs.png    # then scp back and LOOK at it
```

Confirm the tabs actually landed before reporting done. **Stop here — the user clicks Add to Cart and completes the purchase.**

### 7. Log the outcome

Once the user reports what they bought, record it: a dated entry in [[BUY Log]], a **Done** line in [[BUY Purchasing]], and — for consumables — the $/unit reference on the category page (e.g. [[BUY Tea]]) so the next run starts from real numbers instead of re-deriving them.

## When NOT to use this skill

- **Identifying a product** — use `/find`.
- **Profiling a product** — use `/profile`.
- **Comparing alternatives** — use `/survey`.
- **Subscription / SaaS / digital goods** — out of scope for v1.
- **Used / open-box hunting** — only if user opts in (eBay candidate triggered explicitly).

## Anti-patterns

- **Don't use WebFetch / curl / Playwright headless / `ctrl jjpage`.** They are bot-blocked everywhere. Real Safari via `ctrl jpage` only. Repeated for emphasis because every fast iteration of this skill will be tempted to "just try curl first" — it does not work.
- **Don't parallelize `ctrl jpage` calls.** Safari has one active tab; parallel calls collide. Sequential, ~2-second sleep between, accept the wall-clock cost.
- **Don't trust search-result snippets for final prices.** They lag the live page. Search gets you to candidate URLs; ctrl jpage gives you the price.
- **Don't skip the page-validity check.** A captured "price" from a search-results page or a bundle listing is worse than no price at all — it's a wrong-confidence trap.
- **Don't include a retailer in the final table without `VERIFIED` or `BLOCKED` status.** Anything else is hallucination by another name.
- **Don't recommend before all retailers have been walked.** Half-complete recommendations cost the user money.

## Output

- A per-retailer summary table (markdown, in chat).
- A JSON record per session at `~/ob/kmr/Log/BUY/<YYYY-MM-DD> — <product-slug>.json` capturing all verified prices, sellers, stock, promos — historical record for re-checks.
- A `ctrl surf` on the winner.

## Related

- Sibling external-entity skills: [[find]], [[profile]], [[survey]].
- Browser-driving tool: [[ctrl]] (`ctrl jpage` is the only fetcher in this skill).
- Future: per-category overrides (groceries → different retailer list), price-history tracking, watchlist / drop-alert mode.

## Known limitations (v1 skeleton)

- US-only retailer list; international shoppers get wrong defaults.
- No automatic coupon-stacking; promos are reported, not applied.
- No member-price detection for Costco / Sam's Club / Amazon Prime — the skill sees the public price.
- Sequential ctrl jpage is slow (~30-60s for 10 retailers); future: smarter retailer pruning based on category.
- No price-history / "is this actually a deal?" check; future: store historical captures in `~/ob/kmr/Log/BUY/` and compare across runs.
