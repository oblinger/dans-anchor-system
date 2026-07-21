---
name: aide
description: >
  Chief-of-staff work — the things you would hand to a competent assistant.
  Running the shape of a day, chasing a purchase, handling a booking, keeping
  recurring routines alive. Use with an action argument: /aide lumen (morning
  routine). Invoke when the user says "aide", "/aide {action}", or asks for
  something a chief of staff would take off their plate.
user_invocable: true
---

# Aide — Chief-of-Staff Skills
requires:: vault, anchor-cli

The home for work done **on the user's behalf** — the standing category for anything a competent chief of staff would take off their plate. Membership test: *would I hand this to an assistant?* If yes, it belongs here.

The group exists because these skills share an audience and a posture, not a mechanism. An aide skill acts for the user, reports what it did, and asks only when a real decision is theirs to make. Some run on a rhythm (a morning routine), some run on request (chase down tickets), and the category deliberately spans both — the unifying idea is *delegated personal work*, not *scheduled work*.

## Actions

| Action | File | What it does |
|---|---|---|
| `lumen` | [[aide-lumen]] | Morning routine — the day's opening sequence. |

## When to Use

- The user names an action directly: `/aide lumen`.
- The user asks for something an assistant would handle — a routine, an errand, a booking, a purchase, a recurring bit of life admin.
- **Not** for work on the user's own systems and content — that is the anchor system's job (`/groom`, `/audit`, `/atlas`). Aide acts in the world on the user's behalf; the anchor skills curate the user's materials.

## Adding an action

New actions land as `aide-{action}.md` beside this file and get a row in the Actions table above — the same shape `/io`, `/code`, and `/viz` use. Keep the action name singular and kebab-case.

**Migration candidates.** [[buy]] (find and verify where to purchase a named product) and [[cook]] (recipe-aware shopping list) are chief-of-staff work currently living as top-level skills. They belong here on the merits; folding them in is deferred because it changes live invocation paths and deserves its own change rather than riding along.

## Personas are separate

The user may put a persona in front of these skills — a named character who "is" the chief of staff. A persona is a voice and a face, defined in its own artifact; it is **not** what this group is named after and never determines membership. Personas are free to move across capabilities, and a capability must stay usable with no persona attached.
