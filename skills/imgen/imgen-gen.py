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
    "flux-dev":     {"endpoint": "https://fal.run/fal-ai/flux/dev",         "cost": 0.025},
    "flux-kontext": {"endpoint": "https://fal.run/fal-ai/flux-kontext/dev", "cost": 0.040},
}
# The verb the user types → the model that runs it. The H4 command records both,
# e.g. `create flux-dev` / `edit flux-kontext 6E`.
VERB_MODEL = {"create": "flux-dev", "edit": "flux-kontext"}
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

def format_command(verb, image=None):
    """`create flux-dev` / `edit flux-kontext 6E`."""
    model = VERB_MODEL[verb]
    return f"{verb} {model}" + (f" {image}" if image else "")


def parse_command(cmd):
    """`edit flux-kontext 6E` → (verb, model, image|None)."""
    parts = cmd.split()
    if not parts or parts[0] not in VERB_MODEL:
        raise ImgenError(f"unknown command '{cmd}' — verb must be one of {sorted(VERB_MODEL)}")
    verb = parts[0]
    model = parts[1] if len(parts) > 1 else VERB_MODEL[verb]
    image = parts[2] if len(parts) > 2 else None
    if model not in BACKENDS:
        raise ImgenError(f"unknown model '{model}' in command '{cmd}'")
    return verb, model, image


# --------------------------------------------------------------------- the page

def _quote(name):
    return urllib.parse.quote(name)


def new_roll(title, prompt):
    """Create the next roll folder + its page (breadcrumb head + a Next render). Returns (n, path)."""
    n = max((b[0] for b in rolls()), default=0) + 1
    path = ANCHOR / f"{SLUG}{n:03d} — {title}"
    path.mkdir(parents=True)
    name = path.name
    # A roll page is a regular file, not an anchor page — so its head is a `:>>`
    # breadcrumb, not a dispatch table (only anchor pages get tables).
    head = (f":>> [[kmr]] → [[Log/Log]] → [[{SLUG}]] → [{name}](hook://p/{_quote(name)}) \n"
            f"# {name}\n"
            f"{title}. Newest render on top.\n\n"
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
        anchor = _section_span(text, r"^## Pick[ \t]*$")
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


def format_meta(model, size, date, cost, n, seeds):
    """The italic provenance line that closes a batch block."""
    listed = ", ".join(f"{n}{v} {seeds[v]}" for v in sorted(seeds) if seeds[v])
    parts = [model, size, date, f"${cost:.3f}"] + ([f"seeds {listed}"] if listed else [])
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


# ------------------------------------------------------------------ pick / index

PICK_BLOCK_RE = re.compile(r"^## Pick\b.*?(?=^## |\Z)", re.M | re.S)


def set_pick(roll_dir, image_name, width=2000):
    """Lift the chosen image to a `## Pick` block at the very top (above Next render)."""
    page = roll_page(roll_dir)
    text = PICK_BLOCK_RE.sub("", page.read_text(encoding="utf-8"))
    text = re.sub(r"\n{3,}", "\n\n", text)
    block = f"## Pick\n\n![[{image_name}|{width}]]\n\n"
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


# ----------------------------------------------------------------------- run it

def _do_render(roll_dir, roll_n, count, size, confirm_over, yes, dry):
    """Shared by `render` and `edit`: execute the Next render `count` times."""
    command, prompt = read_next(roll_dir)
    verb, model, image = parse_command(command)
    if not prompt.strip():
        raise ImgenError("Next render has an empty prompt — set one with `update` or a prompt arg")
    source = resolve_image(roll_dir, image) if verb == "edit" else None

    cost = BACKENDS[model]["cost"] * count
    if cost > confirm_over and not yes:
        raise ImgenError(f"would cost ${cost:.2f} (> ${confirm_over:.2f}). Re-run with --yes.")

    # Append to the newest batch iff it ran the exact same command+prompt; else new batch.
    nb = newest_batch(roll_dir)
    if nb and nb[1] == command and nb[2] == prompt:
        batch = nb[0]
        start = len(batch_variants(roll_dir, batch))
    else:
        batch = next_batch_index(roll_dir)
        start = 0
    if start + count > len(string.ascii_uppercase):
        raise ImgenError(f"batch {batch} would exceed 26 images")
    variants = [string.ascii_uppercase[start + i] for i in range(count)]

    if dry:
        where = "append to" if start else "new"
        print(f"dry-run: {command!r} × {count} → {where} Batch {batch} "
              f"({SLUG}{roll_n:03d}-{batch}[{''.join(variants)}]) (${cost:.3f})")
        return []

    specs = {v: (model, prompt, size, source,
                 roll_dir / f"{SLUG}{roll_n:03d}-{batch}{v}.png") for v in variants}
    date, seeds = read_batch_meta(roll_dir, batch)      # carry forward an append's earlier seeds
    written, failed = [], []
    with cf.ThreadPoolExecutor(min(4, count)) as ex:
        futs = {ex.submit(generate, *s): v for v, s in specs.items()}
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
        # An edit inherits its source's dimensions, so record the source instead of a size.
        meta = format_meta(model, size if source is None else f"source {source.stem}",
                           date or dt.date.today().isoformat(),
                           BACKENDS[model]["cost"] * len(all_imgs), batch, seeds)
        write_batch(roll_dir, batch, command, prompt, all_imgs, meta)
        if not (ANCHOR / f"{SLUG} Gallery.md").read_text(encoding="utf-8").count(roll_dir.name):
            add_to_gallery(roll_dir, written[0])
    for p in sorted(written):
        print(f"  {p.name}")
    for f in failed:
        print(f"  FAILED: {f}", file=sys.stderr)
    print(f"{len(written)} image(s) → Batch {batch} of {roll_dir.name}, "
          f"${BACKENDS[model]['cost']*len(written):.3f}")
    return written


# -------------------------------------------------------------------- the verbs

def cmd_new(a):
    n, path = new_roll(a.roll, " ".join(a.prompt).strip())
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
