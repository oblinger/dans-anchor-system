---
name: cook
description: Recipe-aware shopping/staging list from Paprika
user_invocable: true
---

# Cook

`/cook <recipe>` (or `/cook <recipe> and <recipe> and …`) — pull ingredients from the user's Paprika library, classify against `~/ob/kmr/Topic/Food/Food Categories.md`, and print **Repurchase / Verify / Downstairs / Remaining** lists so the user knows what to buy, what to double-check, what to grab from the basement, and what's already on hand.

Feature design: [[F066 — Cook skill]].

## When to use

When the user says `cook` followed by one or more recipe names. Answers "what do I need to do shopping for, what do I need to grab from downstairs, and what do I already have, before I start cooking?"

## Trigger

Slash-only: `/cook <args>`. Not a DMUX prefix-trigger — `cook` is a common English word and would over-trigger.

Args: one or more recipe names joined by the literal token ` and ` (case-insensitive, surrounding whitespace trimmed).

Examples:
- `/cook chili`
- `/cook chili and stew`
- `/cook spinach soup and chicken adobo and quinoa peppers`

## Runbook

### 1. Parse recipe names

Split args on the literal ` and ` (case-insensitive, trim whitespace around each piece). Each piece is one recipe-name query.

### 2. Resolve each name against Paprika

For each piece, run:

```bash
paprika "<name>"
```

`paprika` is the CLI at `~/.claude/skills/cook/scripts/paprika.py`, wired onto the user's `$PATH`. Default output is JSON: a list of matches with `name, source, source_url, rating, ingredients, directions, uid`.

Branch on results:

- **0 matches** — surface to user: *"No Paprika recipe matches 'X' — check spelling, or skip?"* Wait for direction; do not silently drop.
- **1 match** — auto-accept silently.
- **Unique high-rated match** (≥2 matches, but exactly ONE has the maximum rating AND that rating is ≥4 stars) — **auto-accept silently**. The user's starred favorites are signal-rich; a ≥4★ recipe always wins over unrated or lower-rated candidates. Surface the chosen name (with ★ rating) in the recipe-confirmation header so the user can catch wrong picks if any.
- **Strong but inexact match** (user query is a unique case-insensitive substring of one match's name, AND no ≥4★ match exists) — soft-confirm: *"I assume you meant: <full name>. Let me know if I'm wrong."* Proceed unless objection.
- **≥2 matches with no clear winner** — list candidates `1)..N)` with rating/source, ask user to pick. (When listing, include `★N` for rated recipes; helps the user spot their starred favorite at a glance.)

### 3. Read Food Categories file

Read `~/ob/kmr/Topic/Food/Food Categories.md`. Parse H2 sections — each H2 is a category, body bullets are the ingredients in it. Build an in-memory map: `ingredient_lower → category_name`.

If the file doesn't exist, create it with the default skeleton (Spices, Staples, Downstairs, Freezer, Produce (Standing), Verify, Uncategorized — all empty) before proceeding. First-run output will be all Repurchase candidates.

### 4. Classify each ingredient

Collect all ingredients across all resolved recipes. Aggregate when names match (case-insensitive). For each unique ingredient:

| Found in Food Categories under | → Output block |
|---|---|
| not present in file | **Repurchase** |
| `## Verify` H2 | **Verify** (almost-always-on-hand but worth a quick check — produce that turns over, garlic, etc.) |
| `## Downstairs` H2 | **Downstairs** (must be physically retrieved from basement storage) |
| any other H2 (Spices, Staples, Freezer, …) | **Remaining**, sub-grouped by that H2 |

**Quantities:** keep them on Repurchase, Verify, and Downstairs (user needs them for shopping / checking / grabbing). Drop them in Remaining (user has the item; how much is irrelevant). When aggregating across recipes, sum compatible units and concatenate incompatible ones (`Onions: 2 medium [Chili] + 1 cup chopped [Stew]`).

### 5. Print output

Four blocks, in this order. Print headings even if empty (use `_None._` body):

```markdown
## Repurchase
- 4 large bell peppers
- 2 onions
- 1 jalapeño
- 1 bunch cilantro

## Verify
- 2 garlic cloves
- 2 medium carrots

## Downstairs
- 1 can diced tomatoes (28 oz)
- 4 cups chicken broth

## Remaining
- **Spices:** cumin, oregano, paprika
- **Staples:** olive oil, flour, rice
- **Produce (Standing):** ginger
- **Freezer:** frozen corn
```

In **Remaining**: one line per H2 category that has ingredients in this session, bold category name, colon, comma-separated ingredient list. Omit categories with no hits. Order categories as they appear in `Food Categories.md`.

### 6. Surface "expect on-hand" candidates — ONE batch per session

After the four blocks, scan the **Repurchase** list for items that match the "suspect on-hand" heuristic (below). For each match, propose a category. **Batch ALL candidates into ONE prompt — do not surface across multiple rounds.** Especially for spices: the user wants single-question-then-add-all UX, not round-by-round nagging.

```
I'm assuming you have these on-hand. Which categories?

- ground cumin       → Spices
- smoked paprika     → Spices
- ground coriander   → Spices
- ground turmeric    → Spices
- liquid smoke       → Spices
- nutritional yeast  → Spices
- garlic cloves      → Verify
- ginger             → Produce (Standing)

Reply "yes" to add all as proposed, or correct any (e.g. "ginger is in Verify").
```

If user replies `yes` → for each proposed item, append under its proposed H2 in `~/ob/kmr/Topic/Food/Food Categories.md` (alphabetical order within the section). Re-classify and reprint the four blocks (those items now fall out of Repurchase).

If user replies with corrections → apply each correction (move to specified H2). Items not mentioned in the user's reply remain in Repurchase for this session and are NOT added to the file.

If user replies `no` (or no response) → do nothing. Items stay in Repurchase.

Skip step 6 entirely if no Repurchase items match the heuristic.

### 7. Push to Apple Reminders — condensed format, one section per reminder

After the four blocks are finalized (post step 6 corrections), push the lists to a new Apple Reminders list. **Condensed format**: one reminder per section (or per Remaining sub-category), with the items packed into the reminder's `body` (notes) field. Goal: ~5–7 reminders total, not one per item — the one-per-item version was unreadable on iPhone.

**List name:** `Cook YYYY-MM-DD HH:MM` using local time. Each `/cook` invocation creates a fresh list; old lists accumulate until the user clears them out.

**Contents (in order):**

1. **Header reminder** — name: `Recipes for:`. Body: each recipe descriptive title on its own line (strip Paprika sort prefixes, e.g. `+QUINOA peppers - Mexican Quinoa Stuffed Peppers` → `Mexican Quinoa Stuffed Peppers`). Same line-per-item shape as Repurchase/Verify/Downstairs.
2. **Repurchase reminder** — name: `Repurchase`. Body: items one-per-line (literal newlines inside the AppleScript string). Line-per-item makes each shopping target individually scannable.
3. **Verify reminder** — name: `Verify`. Body: items one-per-line.
4. **Downstairs reminder** — name: `Downstairs`. Body: items one-per-line.
5. **Remaining reminders** — one per sub-category that has items this session. Name: the sub-category H2 name (`Spices`, `Staples`, `Produce (Standing)`, etc.). Body: comma-separated items, no quantities (matches the on-screen Remaining format from § 5 — those items are reference, not action targets, so dense is fine).

Repurchase / Verify / Downstairs use newlines because they're action-oriented (shopping list, retrieval list); each line being its own visual unit helps. Remaining sub-categories use commas because they're reference; pack tight.

**AppleScript invocation pattern:**
```bash
LIST_NAME="Cook $(date '+%Y-%m-%d %H:%M')"
osascript <<EOF
tell application "Reminders"
    set newList to make new list with properties {name:"$LIST_NAME"}
    tell newList
        make new reminder with properties {name:"Recipes for:", body:"<title 1>
<title 2>"}
        make new reminder with properties {name:"Repurchase", body:"<item 1>
<item 2>
..."}
        make new reminder with properties {name:"Verify", body:"<item 1>
<item 2>"}
        make new reminder with properties {name:"Downstairs", body:"<item 1>
<item 2>"}
        make new reminder with properties {name:"Spices", body:"<a>, <b>, <c>"}
        make new reminder with properties {name:"Staples", body:"<a>, <b>"}
        # ... one per Remaining sub-category that has items
    end tell
end tell
EOF
```

Literal newlines inside AppleScript double-quoted strings work natively (no `\n` escape needed) when passed via bash heredoc.

**First-run permission:** macOS prompts for Reminders access the first time AppleScript touches the app from a given parent process. User grants once via System Settings → Privacy & Security → Reminders; subsequent runs are silent. If permission doesn't persist across runs (parent-process bundle instability), package this step as a standalone `.app` bundle for stable permission identity.

After pushing, print a one-line confirmation: `Pushed to Reminders: Cook YYYY-MM-DD HH:MM (N reminders).`

## Suspect-on-hand heuristic

**Be aggressive on spices.** The user has noted: "Generally I have spices on hand. Ask me about Spices to verify once and put them in the list." Better to over-propose Spices and let the user correct than to under-propose and leave them in Repurchase repeatedly.

Mark a Repurchase ingredient as suspect-on-hand if it matches any:

- **Spices** (aggressive):
  - Starts with `ground ` → propose **Spices**
  - Ends in `powder`, `seeds`, `leaves`, `flakes`, `paste`, `extract`, or `essence` → propose **Spices**
  - Contains `yeast` (e.g. nutritional yeast) → propose **Spices**
  - `liquid smoke`, `bay leaves`, vanilla, etc. — flavor-extras → propose **Spices**
  - Common named spices: paprika (any kind), cumin, coriander, turmeric, oregano, basil, thyme, rosemary, sage, cinnamon, cardamom, cloves, nutmeg, allspice, cayenne, ginger powder, garlic powder, onion powder, mustard powder, dill, parsley (dried), tarragon, marjoram, fennel seed, anise, paprika, sumac, za'atar → propose **Spices**
- **Staples**:
  - Is one of: salt, pepper, sugar (any kind), flour (any kind), oil (any kind), vinegar (any kind), rice, pasta, baking soda, baking powder, baker's yeast → propose **Staples**
  - Common condiments: ketchup, mayo/mayonnaise, mustard (any kind), soy sauce, hot sauce, worcestershire, sriracha → propose **Staples**
  - Bottled juice (lemon juice, lime juice, vinegars) → propose **Staples**
- **Freezer**:
  - Starts with `frozen ` → propose **Freezer**
- **Verify** (turnover produce / aromatics the user usually keeps but worth checking):
  - garlic, ginger (fresh), carrots, lemons (fresh, whole), limes (fresh, whole), onions (yellow/red as standing) — when in doubt, propose **Verify**

Anything else stays in Repurchase. The user's `Food Categories.md` is the ground truth; the heuristic only fires for items NOT yet in the file.

## Out of scope (v1)

- **Quantity scaling / "double batch"** — v1 reports ingredients per the Paprika recipe as written.
- **Quantity-aware Repurchase** — the file says "I have some" but not "how much"; the user judges sufficiency.
- **Recipe-to-meal-plan integration** — adjacent skill space; defer.

## Implementation notes

- Read Paprika data via the `paprika` CLI — do NOT shell out to SQLite directly. The CLI is the contract.
- Ingredient matching is case-insensitive on lookup but preserves original casing on output.
- File appends to `Food Categories.md` preserve alphabetical order within the target H2.
- If multiple ingredients map to the same category in the suspect-on-hand block, batch them; one append, one re-classify pass.
