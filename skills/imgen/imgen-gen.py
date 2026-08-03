#!/usr/bin/env python3
"""imgen-gen.py — generate & edit images into the IMGEN anchor, prompt kept beside them.

The engine behind the /imgen skill (SKA F276). A sitting is a ROLL — a numbered
folder `IMGEN<nnn> — <title>/` whose namesake page carries everything; individual
pictures inside it are IMAGES, `IMGEN<nnn>-<batch><variant>.png`.

The page is stateful. Under the H1 it holds, in order:
    ## Pick            the chosen image, shown large   (optional, set by `pick`)
    ## Next render     the ONE pending operation: an `#### <command>` H4 + a prompt
    ## Batch N …        past renders, newest first: H2 title → images → #### command → prompt

`render` executes the Next render. The command sticks (after any run, Next render
is whatever just ran), so bare `render` repeats it; a fresh prompt resets it to a
`create`. If the Next render still matches the newest batch, `render` APPENDS to
that batch instead of starting a new one — "more of the same" stays one section.

Backends are pluggable; `flux-dev` (text→image) and `flux-kontext` (instruction
edit) are wired. Credentials come from the login keychain, never a file on disk:
    security find-generic-password -s FAL_KEY -w
"""
import argparse
import base64
import concurrent.futures as cf
import datetime as dt
import json
import re
import string
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ANCHOR = Path.home() / "ob/kmr/Log/IMGEN"
SLUG = "IMGEN"

ROLL_RE = re.compile(rf"^{SLUG}(\d{{3}})(?: — (.*))?$")     # a roll folder
IMAGE_RE = re.compile(rf"^{SLUG}\d{{3}}-(\d+)([A-Z])\.")    # an image file: batch, variant

BACKENDS = {
    "flux-dev":     {"endpoint": "https://fal.run/fal-ai/flux/dev",           "cost": 0.025},
    "flux-kontext": {"endpoint": "https://fal.run/fal-ai/flux-kontext/dev",   "cost": 0.040},
    "flux-fill":    {"endpoint": "https://fal.run/fal-ai/flux-pro/v1/fill",   "cost": 0.050},
}
# The verb the user types → the model that runs it. The H4 command records both,
# e.g. `create flux-dev` / `edit flux-kontext 6E` / `inpaint flux-fill 1A [nose]`.
VERB_MODEL = {"create": "flux-dev", "edit": "flux-kontext", "inpaint": "flux-fill"}
# Fill works best near 1MP; a 500² source starves it. Masks scale with the image.
FILL_SIZE = 1024
KEYCHAIN = "FAL_KEY"


class ImgenError(RuntimeError):
    pass


def keychain(service=KEYCHAIN):
    """Read a secret from the login keychain. Fails loudly — no fallback."""
    r = subprocess.run(["security", "find-generic-password", "-s", service, "-w"],
                       capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        raise ImgenError(
            f"no keychain entry for '{service}'. Add it with:\n"
            f"  security add-generic-password -U -a \"$USER\" -s {service} -w '<key>'")
    return r.stdout.strip()


# ---------------------------------------------------------------- rolls / images

def rolls():
    """Every roll folder, ascending by number. [(n, title, path), ...]"""
    if not ANCHOR.is_dir():
        return []
    out = []
    for d in ANCHOR.iterdir():
        m = ROLL_RE.match(d.name) if d.is_dir() else None
        if m:
            out.append((int(m.group(1)), m.group(2) or "", d))
    return sorted(out)


def find_roll(arg):
    """Resolve a roll by number ('4' / '004') or by name substring. → (n, title, path)."""
    found = rolls()
    if not found:
        raise ImgenError('no rolls yet — open one with `imgen new "<title>"`')
    s = str(arg).strip()
    if s.isdigit():
        hit = [b for b in found if b[0] == int(s)]
    else:
        low = s.lower()
        hit = [b for b in found if low in f"{SLUG}{b[0]:03d} — {b[1]}".lower()]
    if len(hit) == 1:
        return hit[0]
    have = ", ".join(f"{b[0]:03d} ({b[1]})" for b in found)
    if not hit:
        raise ImgenError(f"no roll matching '{arg}' — have: {have}")
    raise ImgenError(f"'{arg}' matches several rolls — be specific. Have: {have}")


def roll_page(roll_dir):
    return roll_dir / f"{roll_dir.name}.md"


def batch_variants(roll_dir, n):
    """Variant letters already present in batch n, sorted."""
    out = []
    for f in roll_dir.iterdir():
        m = IMAGE_RE.match(f.name)
        if m and int(m.group(1)) == n:
            out.append(m.group(2))
    return sorted(out)


def next_batch_index(roll_dir):
    used = [int(m.group(1)) for f in roll_dir.iterdir()
            if (m := IMAGE_RE.match(f.name))]
    return max(used, default=0) + 1


def resolve_image(roll_dir, image):
    """Turn a loose image ref ('6E', 'IMGEN004-6E', '...png') into an existing Path."""
    name = image.strip()
    if name.lower().endswith(".png"):
        name = name[:-4]
    if not name.startswith(SLUG):
        m = ROLL_RE.match(roll_dir.name)
        prefix = f"{SLUG}{m.group(1)}" if m else roll_dir.name.split(" ")[0]
        name = f"{prefix}-{name}"
    p = roll_dir / f"{name}.png"
    if not p.exists():
        raise ImgenError(f"no image {p.name} in {roll_dir.name}")
    return p


# ------------------------------------------------------------------ command (H4)

def format_command(verb, image=None, region=None):
    """`create flux-dev` / `edit flux-kontext 6E` / `inpaint flux-fill 1A [nose]`."""
    model = VERB_MODEL[verb]
    return (f"{verb} {model}" + (f" {image}" if image else "")
            + (f" [{region}]" if region else ""))


def parse_command(cmd):
    """`inpaint flux-fill 1A [nose]` → (verb, model, image|None, region|None)."""
    rm = re.search(r"\[([^\]]+)\]\s*$", cmd)
    region = rm.group(1) if rm else None
    parts = (cmd[:rm.start()] if rm else cmd).split()
    if not parts or parts[0] not in VERB_MODEL:
        raise ImgenError(f"unknown command '{cmd}' — verb must be one of {sorted(VERB_MODEL)}")
    verb = parts[0]
    model = parts[1] if len(parts) > 1 else VERB_MODEL[verb]
    image = parts[2] if len(parts) > 2 else None
    if model not in BACKENDS:
        raise ImgenError(f"unknown model '{model}' in command '{cmd}'")
    if verb == "inpaint" and not region:
        raise ImgenError(f"'{cmd}' needs a mask region, e.g. `inpaint flux-fill 1A [nose]`")
    return verb, model, image, region


# --------------------------------------------------------------------- the page

def _quote(name):
    """Percent-encode for a hook:// link, leaving the em-dash literal — that is what
    every existing breadcrumb in the anchor uses. `quote(safe=…)` cannot express this:
    it silently drops non-ASCII characters from `safe`, so the em-dash is restored after."""
    return urllib.parse.quote(name).replace("%E2%80%94", "—")


def new_roll(title, prompt, about=None):
    """Create the next roll folder + its page (breadcrumb head + a Next render). Returns (n, path)."""
    n = max((b[0] for b in rolls()), default=0) + 1
    path = ANCHOR / f"{SLUG}{n:03d} — {title}"
    path.mkdir(parents=True)
    name = path.name
    # A roll page is a regular file, not an anchor page — so its head is a `:>>`
    # breadcrumb, not a dispatch table (only anchor pages get tables).
    #
    # The line under the H1 says what this sitting is ABOUT — who the subject is,
    # what was being explored. It is not a place for navigation meta ("newest
    # first"): the page's ordering is the anchor's convention, not this roll's news.
    head = (f":>> [[kmr]] → [[Log/Log]] → [[{SLUG}]] → [{name}](hook://p/{_quote(name)}) \n"
            f"# {name}\n"
            f"{about or (title + '.')}\n\n"
            f"## Next render\n\n#### {format_command('create')}\n{prompt}\n")
    roll_page(path).write_text(head, encoding="utf-8")
    return n, path


def grid(images, width=500, across=3):
    """A borderless N-across table. The header row is left empty on purpose —
    markdown makes the first row a heading, and an image there renders as a
    column label instead of a picture."""
    rows = [images[i:i + across] for i in range(0, len(images), across)]
    cols = min(across, max((len(r) for r in rows), default=1)) if rows else 1
    out = ["| " * cols + "|", "| " + " | ".join(["---"] * cols) + " |"]
    for r in rows:
        cells = [f"![[{f.name}\\|{width}]]" for f in r] + [""] * (cols - len(r))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def _section_span(text, heading_re):
    """(start, stop) of a `## …` section: from its heading to the next `## `, or EOF.
    Returns None if the heading is absent."""
    m = re.search(heading_re, text, re.M)
    if not m:
        return None
    nxt = re.search(r"^## ", text[m.end():], re.M)
    return m.start(), (m.end() + nxt.start() if nxt else len(text))


def read_next(roll_dir):
    """Parse the `## Next render` block → (command, prompt)."""
    text = roll_page(roll_dir).read_text(encoding="utf-8")
    span = _section_span(text, r"^## Next render[ \t]*$")
    if not span:
        raise ImgenError(f"{roll_dir.name} has no '## Next render' block "
                         f"(old-format roll? migrate it first)")
    block = text[span[0]:span[1]]
    cm = re.search(r"^####[ \t]+(.*)$", block, re.M)
    if not cm:
        raise ImgenError(f"{roll_dir.name} Next render has no '#### <command>' line")
    return cm.group(1).strip(), block[cm.end():].strip("\n")


def write_next(roll_dir, command, prompt):
    """Replace (or insert) the `## Next render` block."""
    page = roll_page(roll_dir)
    text = page.read_text(encoding="utf-8")
    block = f"## Next render\n\n#### {command}\n{prompt}\n"
    span = _section_span(text, r"^## Next render[ \t]*$")
    if span:
        new = text[:span[0]] + block + ("\n" + text[span[1]:] if span[1] < len(text) else "")
    else:
        # Insert after a Pick block if present, else after the H1 header, before batches.
        anchor = _section_span(text, r"^## Pick\b.*$")
        first_h2 = re.search(r"^## ", text, re.M)
        pos = anchor[1] if anchor else (first_h2.start() if first_h2 else len(text))
        new = text[:pos].rstrip("\n") + "\n\n" + block + ("\n" + text[pos:] if pos < len(text) else "")
    page.write_text(re.sub(r"\n{3,}", "\n\n", new), encoding="utf-8")


def newest_batch(roll_dir):
    """The top-most `## Batch N` section → (n, command, prompt) or None."""
    text = roll_page(roll_dir).read_text(encoding="utf-8")
    m = re.search(r"^## Batch (\d+)\b.*$", text, re.M)
    if not m:
        return None
    n = int(m.group(1))
    body = text[m.end():]
    end = re.search(r"^## ", body, re.M)
    block = body[:end.start()] if end else body
    cm = re.search(r"^####[ \t]+(.*)$", block, re.M)
    command = cm.group(1).strip() if cm else ""
    prompt = strip_meta(block[cm.end():]) if cm else ""
    return n, command, prompt


def strip_meta(block):
    """Drop a batch's trailing italic provenance line, leaving just the prompt.

    Load-bearing: `render` decides append-vs-new-batch by comparing this prompt
    against the Next render's, so a meta line left attached here would make every
    repeat look like a different prompt and open a new batch each time."""
    lines = block.strip("\n").split("\n")
    while lines and not lines[-1].strip():
        lines.pop()
    if lines and re.fullmatch(r"\*.*\*", lines[-1].strip()):
        lines.pop()
    return "\n".join(lines).strip("\n")


SPEND_RE = re.compile(r"^\*\*Spent so far:\*\*.*$", re.M)


def update_spend(roll_dir):
    """Recompute the roll's cumulative cost and park it under the summary line.

    Derived, never accumulated: every batch's provenance line carries its own
    dollar figure, so the total is re-summed from the page each time. That way a
    deleted or rewritten batch can never leave the total silently wrong."""
    page = roll_page(roll_dir)
    text = page.read_text(encoding="utf-8")
    # Count a dollar figure only on a provenance line — one that also names a model
    # or a seed. Older rolls wrote provenance as plain prose rather than the italic
    # line, so keying on `*…*` alone silently under-reports them as $0.000.
    # Sum EXACTLY: per-batch figures are rounded to the penny for readability, and
    # summing those rounded values drifts (a 1-image flux-dev batch is 2.5¢, which
    # no whole-cent display can hold). So price each batch from its model and its
    # image count, and fall back to the printed figure only when that is unknown.
    total = 0.0
    for m in re.finditer(r"^## Batch \d+\b.*$", text, re.M):
        nxt = re.search(r"^## ", text[m.end():], re.M)
        block = text[m.start():m.end() + nxt.start()] if nxt else text[m.start():]
        model = next((k for k in BACKENDS if k in block), None)
        if model is None and "fal-ai/flux/dev" in block:
            model = "flux-dev"
        # A mask preview is embedded in the batch but costs nothing — never bill it.
        shots = len([e for e in re.findall(r"!\[\[([^\]|]*?\.(?:png|jpg))", block, re.I)
                     if "-preview." not in e])
        if model and shots:
            total += BACKENDS[model]["cost"] * shots
        else:                                   # local blends, or a batch with no model
            c, d = re.search(r"(\d+)¢", block), re.search(r"\$([0-9]+\.[0-9]+)", block)
            total += int(c.group(1)) / 100 if c else float(d.group(1)) if d else 0.0
    line = f"**Spent so far:** ${total:.2f}"
    if SPEND_RE.search(text):
        text = SPEND_RE.sub(line, text, count=1)
    else:                                   # insert just above the first H2
        m = re.search(r"^## ", text, re.M)
        pos = m.start() if m else len(text)
        text = text[:pos].rstrip("\n") + f"\n\n{line}\n\n" + text[pos:]
    page.write_text(re.sub(r"\n{3,}", "\n\n", text), encoding="utf-8")
    return total


def read_batch_meta(roll_dir, n):
    """Recover a past batch's provenance line → (date|None, {variant: seed}).

    Seeds are what make a batch re-rollable, so an append must carry forward the
    ones already recorded rather than overwrite them with only the new images'."""
    text = roll_page(roll_dir).read_text(encoding="utf-8")
    span = _section_span(text, rf"^## Batch {n}\b.*$")
    if not span:
        return None, {}
    block = text[span[0]:span[1]]
    dm = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", block)
    seeds = dict(re.findall(rf"\b{n}([A-Z])\s+(\d+)", block))
    return (dm.group(1) if dm else None), seeds


def cents(cost):
    """Per-batch money reads in whole cents — a batch is pennies, and `$0.040`
    is harder to scan than `4¢`. The roll total stays in dollars."""
    return f"{int(cost * 100 + 0.5)}¢"      # half-up; round() would send 2.5¢ down to 2¢


def format_meta(model, size, date, cost, n, seeds):
    """The italic provenance line that closes a batch block."""
    listed = ", ".join(f"{n}{v} {seeds[v]}" for v in sorted(seeds) if seeds[v])
    parts = [model, size, date, cents(cost)] + ([f"seeds {listed}"] if listed else [])
    return "*" + " · ".join(parts) + "*"


def write_batch(roll_dir, n, command, prompt, images, meta=None):
    """Create or replace the `## Batch n` section (title → images → #### command → prompt → meta)."""
    page = roll_page(roll_dir)
    text = page.read_text(encoding="utf-8")
    span = _section_span(text, rf"^## Batch {n}\b.*$")
    # Rewriting a batch must not cost it its identity: a heading subtitle ("the
    # keeper") and any commentary written above the grid are hand-authored and
    # unrecoverable, so carry them across rather than regenerating a bare heading.
    heading, lead = f"## Batch {n}", ""
    if span:
        old = text[span[0]:span[1]]
        heading = old.split("\n", 1)[0].rstrip()
        body = old.split("\n", 1)[1] if "\n" in old else ""
        gm = re.search(r"^\|", body, re.M)
        lead = body[:gm.start()].strip("\n") if gm else ""
    block = (f"{heading}\n\n" + (f"{lead}\n\n" if lead else "")
             + f"{grid(images)}\n\n#### {command}\n{prompt}\n"
             + (f"\n{meta}\n" if meta else ""))
    if span:                                   # replace in place (append case)
        new = text[:span[0]] + block + ("\n" + text[span[1]:] if span[1] < len(text) else "")
    else:                                      # insert just below the Next render block
        nr = _section_span(text, r"^## Next render[ \t]*$")
        pos = nr[1] if nr else len(text)
        new = text[:pos].rstrip("\n") + "\n\n" + block + ("\n" + text[pos:] if pos < len(text) else "")
    page.write_text(re.sub(r"\n{3,}", "\n\n", new), encoding="utf-8")
    update_spend(roll_dir)


# ------------------------------------------------------------------ pick / index

PICK_BLOCK_RE = re.compile(r"^## Pick\b.*?(?=^## |\Z)", re.M | re.S)


def set_pick(roll_dir, image_name, width=2000):
    """Lift the chosen image to a `## Pick` block at the very top (above Next render)."""
    page = roll_page(roll_dir)
    text = PICK_BLOCK_RE.sub("", page.read_text(encoding="utf-8"))
    text = re.sub(r"\n{3,}", "\n\n", text)
    # The heading names the pick, so the page says which image won without the
    # reader having to decode the embed's filename.
    m = IMAGE_RE.match(image_name)
    block = (f"## Pick" + (f" — {m.group(1)}{m.group(2)}" if m else "")
             + f"\n\n![[{image_name}|{width}]]\n\n")
    m = re.search(r"^## ", text, re.M)
    text = (text[:m.start()] + block + text[m.start():] if m
            else text.rstrip("\n") + "\n\n" + block)
    page.write_text(text, encoding="utf-8")


def set_gallery_cover(roll_name, cover_name, width=500):
    g = ANCHOR / f"{SLUG} Gallery.md"
    if not g.exists():
        return
    text = g.read_text(encoding="utf-8")
    h2 = re.search(rf"^## \[\[{re.escape(roll_name)}\]\].*$", text, re.M)
    if not h2:
        return
    head, tail = text[:h2.end()], text[h2.end():]
    tail, k = re.subn(r"!\[\[[^\]]*\]\]", f"![[{cover_name}|{width}]]", tail, count=1)
    if k:
        g.write_text(head + tail, encoding="utf-8")


def add_to_gallery(roll_dir, cover):
    g = ANCHOR / f"{SLUG} Gallery.md"
    if not g.exists() or f"[[{roll_dir.name}]]" in g.read_text(encoding="utf-8"):
        return
    entry = f"## [[{roll_dir.name}]]\n\n![[{cover.name}|500]]\n"
    text = g.read_text(encoding="utf-8")
    m = re.search(r"^## ", text, re.M)
    g.write_text(text[:m.start()] + entry + "\n" + text[m.start():] if m
                 else text.rstrip("\n") + "\n\n" + entry, encoding="utf-8")


def add_member_row(roll_dir):
    a = ANCHOR / f"{SLUG}.md"
    if not a.exists():
        return
    text = a.read_text(encoding="utf-8")
    if roll_dir.name in text:
        return
    marker = "| ^^^ | |\n"
    if marker in text:
        a.write_text(text.replace(marker, f"{marker}| [[{roll_dir.name}]]  |  |\n", 1),
                     encoding="utf-8")


# ------------------------------------------------------------------ generate one

def _data_uri(path):
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


# ------------------------------------------------------------------- masking

def mask_path(roll_dir, stem, region):
    return roll_dir / f"{stem}-{region}-mask.png"


def find_mask(roll_dir, region):
    """The newest `{SLUG}{nnn}-{batch}-{region}-mask.png` in the roll, or None.

    A mask is named for the batch it FEEDS, not the image it was traced from, so
    it sorts beside the work it produced rather than beside its source."""
    pat = re.compile(rf"^{SLUG}\d{{3}}-(\d+)-{re.escape(region)}-mask\.png$")
    found = [(int(m.group(1)), p) for p in roll_dir.iterdir()
             if (m := pat.match(p.name))]
    return max(found)[1] if found else None


def build_mask(src, region, ellipse, size, stem):
    """Write `<image>-<region>-mask.png` at `size`², plus a review preview.

    The preview is the ORIGINAL image with a pure-green outline drawn on it —
    one picture, not a before/after pair. A separate black-and-white mask is
    unreadable to a human: you cannot map its coordinates onto the photo by eye,
    which is exactly the review the mask exists to enable."""
    from PIL import Image, ImageDraw, ImageFilter
    lanczos = Image.Resampling.LANCZOS
    im = Image.open(src).convert("RGB")
    k = size / im.width
    cx, cy, rx, ry = (round(v * k) for v in ellipse)

    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=255)
    mp = mask_path(src.parent, stem, region)
    mask.convert("RGB").save(mp)

    edge = (mask.filter(ImageFilter.FIND_EDGES)
                .point(lambda v: 255 if v > 40 else 0)
                .filter(ImageFilter.MaxFilter(5)))          # thicken so it reads
    prev = im.resize((size, size), lanczos)
    prev.paste(Image.new("RGB", (size, size), (0, 255, 0)), mask=edge)
    pp = src.parent / f"{stem}-{region}-preview.png"
    prev.save(pp)
    return mp, pp


def inpaint(model, prompt, source, mask, out, size=FILL_SIZE):
    """Fill inside `mask` only. Returns (path, seed).

    FLUX Fill is NOT pixel-preserving — it re-renders the whole frame and may
    even hand back a different resolution. So its output is composited back into
    the source through the (feathered) mask: outside the mask the result is
    byte-for-byte the source, which is what makes a mask mean what it says."""
    from PIL import Image, ImageFilter
    lanczos = Image.Resampling.LANCZOS
    big = Image.open(source).convert("RGB").resize((size, size), lanczos)
    tmp = source.parent / f".{source.stem}-up.png"
    big.save(tmp)
    try:
        cfg = BACKENDS[model]
        payload = {"prompt": prompt, "image_url": _data_uri(tmp),
                   "mask_url": _data_uri(mask)}
        req = urllib.request.Request(cfg["endpoint"], data=json.dumps(payload).encode(),
                                     headers={"Authorization": f"Key {keychain()}",
                                              "Content-Type": "application/json"})
        try:
            resp = json.load(urllib.request.urlopen(req, timeout=180))
        except urllib.error.HTTPError as e:
            raise ImgenError(f"{model} HTTP {e.code}: {e.read().decode('utf-8','replace')[:200]}")
        if not resp.get("images"):
            raise ImgenError(f"{model} returned no images: {str(resp)[:200]}")
        raw = source.parent / f".{source.stem}-raw.png"
        raw.write_bytes(urllib.request.urlopen(resp["images"][0]["url"], timeout=120).read())
        filled = Image.open(raw).convert("RGB").resize((size, size), lanczos)
        m = Image.open(mask).convert("L").resize((size, size), lanczos)
        Image.composite(filled, big, m.filter(ImageFilter.GaussianBlur(6))).save(out)
        raw.unlink(missing_ok=True)
        return out, resp.get("seed")
    finally:
        tmp.unlink(missing_ok=True)


def generate(model, prompt, size, source, out):
    """One image → (path, seed). `source` is a Path for edit models, else None (text→image)."""
    cfg = BACKENDS[model]
    payload = {"prompt": prompt, "num_images": 1}
    if source is None:
        payload["image_size"] = size
    else:
        payload["image_url"] = _data_uri(source)
    req = urllib.request.Request(cfg["endpoint"], data=json.dumps(payload).encode(),
                                 headers={"Authorization": f"Key {keychain()}",
                                          "Content-Type": "application/json"})
    try:
        resp = json.load(urllib.request.urlopen(req, timeout=180))
    except urllib.error.HTTPError as e:
        raise ImgenError(f"{model} HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:200]}")
    if not resp.get("images"):
        raise ImgenError(f"{model} returned no images: {str(resp)[:200]}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(urllib.request.urlopen(resp["images"][0]["url"], timeout=120).read())
    return out, resp.get("seed")


def contact_sheet(paths, out, cols=3, cell=560):
    """Composite a whole batch into ONE labelled image.

    A shoot is judged by comparing its variants, so it wants a single window —
    six `open` calls give six overlapping windows in arbitrary order and no way
    to see them side by side. Each cell is captioned with its variant id
    (`1A`, `1B`, …) so the sheet can be pointed at directly.

    Free, and deliberately NOT embedded in the roll page: the page already
    carries the images themselves, and a sheet there would double every batch.
    The `-sheet` suffix cannot match `IMAGE_RE`, so it is never counted as a
    render or picked up as a variant.
    """
    from PIL import Image, ImageDraw, ImageFont
    rows = -(-len(paths) // cols)
    pad, bar = 8, 34
    sheet = Image.new("RGB", (cols * (cell + pad) + pad,
                              rows * (cell + bar + pad) + pad), (24, 24, 26))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/SFNSMono.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
    for i, p in enumerate(paths):
        x = pad + (i % cols) * (cell + pad)
        y = pad + (i // cols) * (cell + bar + pad)
        im = Image.open(p).convert("RGB")
        im.thumbnail((cell, cell), Image.Resampling.LANCZOS)
        sheet.paste(im, (x + (cell - im.width) // 2, y))
        draw.text((x + 4, y + cell + 6), re.sub(rf"^{SLUG}\d{{3}}-", "", p.stem),
                  font=font, fill=(210, 210, 214))
    sheet.save(out)
    return out


# ----------------------------------------------------------------------- run it

def _do_render(roll_dir, roll_n, count, size, confirm_over, yes, dry):
    """Shared by `render` and `edit`: execute the Next render `count` times."""
    command, prompt = read_next(roll_dir)
    verb, model, image, region = parse_command(command)
    if not prompt.strip():
        raise ImgenError("Next render has an empty prompt — set one with `update` or a prompt arg")
    source = resolve_image(roll_dir, image) if verb in ("edit", "inpaint") else None
    mask = None
    if verb == "inpaint":
        mask = find_mask(roll_dir, region)
        if mask is None:
            raise ImgenError(f"no '{region}' mask in {roll_dir.name} — build it first with "
                             f"`imgen mask {roll_n} {image} {region} --ellipse cx,cy,rx,ry`")

    cost = BACKENDS[model]["cost"] * count
    if cost > confirm_over and not yes:
        raise ImgenError(f"would cost ${cost:.2f} (> ${confirm_over:.2f}). Re-run with --yes.")

    # Append to the newest batch iff it ran the exact same command+prompt; else new batch.
    nb = newest_batch(roll_dir)
    if nb and nb[1] == command and nb[2] == prompt:
        batch = nb[0]
        used = set(batch_variants(roll_dir, batch))
    else:
        batch = next_batch_index(roll_dir)
        used = set()
    # Take the next FREE letters, not the next `len(used)` of them. A batch whose
    # letters have gaps — some renders failed, one was deleted — is otherwise handed
    # variants that already exist, and the re-run silently overwrites them.
    free = [c for c in string.ascii_uppercase if c not in used]
    if count > len(free):
        raise ImgenError(f"batch {batch} would exceed 26 images")
    variants = free[:count]

    if dry:
        where = "append to" if used else "new"
        print(f"dry-run: {command!r} × {count} → {where} Batch {batch} "
              f"({SLUG}{roll_n:03d}-{batch}[{''.join(variants)}]) ({cents(cost)})")
        return []

    def one(v):
        out = roll_dir / f"{SLUG}{roll_n:03d}-{batch}{v}.png"
        if verb == "inpaint":
            return inpaint(model, prompt, source, mask, out)
        return generate(model, prompt, size, source, out)

    specs = {v: (v,) for v in variants}
    date, seeds = read_batch_meta(roll_dir, batch)      # carry forward an append's earlier seeds
    written, failed, sheet = [], [], None
    with cf.ThreadPoolExecutor(min(4, count)) as ex:
        futs = {ex.submit(one, *s): v for v, s in specs.items()}
        for fut in futs:
            try:
                path, seed = fut.result()
                written.append(path)
                seeds[futs[fut]] = seed
            except Exception as e:
                failed.append(str(e))
    if written:
        all_imgs = sorted((roll_dir / f"{SLUG}{roll_n:03d}-{batch}{v}.png"
                           for v in batch_variants(roll_dir, batch)),
                          key=lambda p: p.name)
        # An inpaint batch leads with its mask preview, so the region that was
        # repainted is visible in the record beside what it produced — you can
        # judge the mask and the result in one glance, without opening files.
        shots = len(all_imgs)                      # paid renders, before the free preview
        if mask is not None:
            preview = mask.with_name(mask.name.replace("-mask.png", "-preview.png"))
            if preview.exists():
                all_imgs = [preview] + all_imgs
        # An edit inherits its source's dimensions, so record the source instead of a size.
        detail = (size if source is None else
                  f"{source.stem} · mask {mask.name}" if mask else f"source {source.stem}")
        meta = format_meta(model, detail,
                           date or dt.date.today().isoformat(),
                           BACKENDS[model]["cost"] * shots, batch, seeds)
        write_batch(roll_dir, batch, command, prompt, all_imgs, meta)
        if not (ANCHOR / f"{SLUG} Gallery.md").read_text(encoding="utf-8").count(roll_dir.name):
            add_to_gallery(roll_dir, written[0])
        if len(all_imgs) > 1:
            sheet = contact_sheet(all_imgs,
                                  roll_dir / f"{SLUG}{roll_n:03d}-{batch}-sheet.png")
    for p in sorted(written):
        print(f"  {p.name}")
    for f in failed:
        print(f"  FAILED: {f}", file=sys.stderr)
    if sheet:
        print(f"  review → {sheet}")
    print(f"{len(written)} image(s) → Batch {batch} of {roll_dir.name}, "
          f"{cents(BACKENDS[model]['cost']*len(written))} "
          f"(roll total ${update_spend(roll_dir):.2f})")
    return written


# -------------------------------------------------------------------- the verbs

def cmd_new(a):
    n, path = new_roll(a.roll, " ".join(a.prompt).strip(), a.about)
    add_member_row(path)
    print(f"created {path.name} — check its Next render, then `imgen render {n}`")
    return 0


def cmd_get(a):
    _, _, d = find_roll(a.roll)
    command, prompt = read_next(d)
    print(f"command: {command}")
    print(f"prompt:\n{prompt}")
    return 0


def cmd_update(a):
    _, _, d = find_roll(a.roll)
    command, prompt = read_next(d)
    if a.command is None and a.prompt is None:
        raise ImgenError("nothing to update — give --command and/or --prompt")
    if a.command is not None:
        parse_command(a.command)               # validate
        command = a.command.strip()
    if a.prompt is not None:
        prompt = a.prompt
    write_next(d, command, prompt)
    print(f"Next render is now: {command}")
    return 0


def cmd_render(a):
    n, _, d = find_roll(a.roll)
    prompt = " ".join(a.prompt).strip()
    if prompt:                                 # a prompt resets Next render to a fresh create
        write_next(d, format_command("create"), prompt)
    _do_render(d, n, a.count, a.size, a.confirm_over, a.yes, a.dry_run)
    return 0


def cmd_edit(a):
    n, _, d = find_roll(a.roll)
    resolve_image(d, a.image)                   # fail early if the image is missing
    write_next(d, format_command("edit", a.image), " ".join(a.instruction).strip())
    _do_render(d, n, a.count, a.size, a.confirm_over, a.yes, a.dry_run)
    return 0


def cmd_mask(a):
    """Author a mask and render its green-outline preview. No API call, no cost."""
    _, _, d = find_roll(a.roll)
    src = resolve_image(d, a.image)
    try:
        cx, cy, rx, ry = (int(v) for v in a.ellipse.split(","))
    except ValueError:
        raise ImgenError("--ellipse wants cx,cy,rx,ry in the source image's own pixels")
    n, _, _ = find_roll(a.roll)
    stem = f"{SLUG}{n:03d}-{next_batch_index(d)}"      # named for the batch it will feed
    mp, pp = build_mask(src, a.region, (cx, cy, rx, ry), a.size_px, stem)
    print(f"  {mp.name}\n  {pp.name}   <- review this one (green outline on the image)")
    return 0


def cmd_inpaint(a):
    n, _, d = find_roll(a.roll)
    src = resolve_image(d, a.image)
    if a.ellipse:
        build_mask(src, a.region, tuple(int(v) for v in a.ellipse.split(",")),
                   a.size_px, f"{SLUG}{n:03d}-{next_batch_index(d)}")
    write_next(d, format_command("inpaint", a.image, a.region), " ".join(a.instruction).strip())
    _do_render(d, n, a.count, a.size, a.confirm_over, a.yes, a.dry_run)
    return 0


def cmd_pick(a):
    _, _, d = find_roll(a.roll)
    img = resolve_image(d, a.image)
    set_pick(d, img.name)
    set_gallery_cover(d.name, img.name)
    print(f"pick: {img.stem} → top of {d.name} + gallery cover")
    return 0


def cmd_list(a):
    if a.roll:
        _, _, d = find_roll(a.roll)
        for f in sorted(p.name for p in d.iterdir() if IMAGE_RE.match(p.name)):
            print(f"  {f}")
    else:
        for n, title, d in rolls():
            nb = newest_batch(d)
            tail = f"— latest Batch {nb[0]}" if nb else "— empty"
            print(f"  {n:03d}  {title}  {tail}")
    return 0


def main():
    ap = argparse.ArgumentParser(prog="imgen",
                                 description="Generate & edit images into the IMGEN anchor.")
    sub = ap.add_subparsers(dest="verb", required=True)

    def spend_opts(p):
        p.add_argument("-n", "--count", type=int, default=1, help="how many images (default 1)")
        p.add_argument("-s", "--size", default="square_hd")
        p.add_argument("--confirm-over", type=float, default=1.00)
        p.add_argument("--yes", action="store_true")
        p.add_argument("--dry-run", action="store_true")

    p = sub.add_parser("new", help="create a new roll")
    p.add_argument("roll"); p.add_argument("prompt", nargs="*")
    p.add_argument("--about", default=None,
                   help="the line under the H1: what this sitting is about (default '<title>.')")
    p.set_defaults(fn=cmd_new)

    p = sub.add_parser("get", help="print the Next render block")
    p.add_argument("roll"); p.set_defaults(fn=cmd_get)

    p = sub.add_parser("update", help="rewrite the Next render (no render)")
    p.add_argument("roll")
    p.add_argument("--command", default=None)
    p.add_argument("--prompt", default=None)
    p.set_defaults(fn=cmd_update)

    p = sub.add_parser("render", help="run the Next render N times")
    p.add_argument("roll"); p.add_argument("prompt", nargs="*"); spend_opts(p)
    p.set_defaults(fn=cmd_render)

    p = sub.add_parser("edit", help="instruction-edit an image → new batch")
    p.add_argument("roll"); p.add_argument("image"); p.add_argument("instruction", nargs="+")
    spend_opts(p)
    p.set_defaults(fn=cmd_edit)

    p = sub.add_parser("mask", help="author a mask + green-outline preview (free)")
    p.add_argument("roll"); p.add_argument("image"); p.add_argument("region")
    p.add_argument("--ellipse", required=True, metavar="cx,cy,rx,ry")
    p.add_argument("--size-px", type=int, default=FILL_SIZE)
    p.set_defaults(fn=cmd_mask)

    p = sub.add_parser("inpaint", help="repaint inside a mask (flux-fill)")
    p.add_argument("roll"); p.add_argument("image"); p.add_argument("region")
    p.add_argument("instruction", nargs="+")
    p.add_argument("--ellipse", default=None, metavar="cx,cy,rx,ry",
                   help="(re)build the mask first; omit to reuse the existing one")
    p.add_argument("--size-px", type=int, default=FILL_SIZE)
    spend_opts(p)
    p.set_defaults(fn=cmd_inpaint)

    p = sub.add_parser("pick", help="mark an image as the roll's pick")
    p.add_argument("roll"); p.add_argument("image"); p.set_defaults(fn=cmd_pick)

    p = sub.add_parser("list", help="list rolls, or images in a roll")
    p.add_argument("roll", nargs="?"); p.set_defaults(fn=cmd_list)

    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ImgenError as e:
        print(f"imgen: {e}", file=sys.stderr)
        sys.exit(2)
