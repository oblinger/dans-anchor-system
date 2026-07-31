#!/usr/bin/env python3
"""imgen-gen.py — generate images into the IMGEN anchor, prompt kept beside them.

The engine behind the /imgen skill (SKA F276). Backends are pluggable; `fal`
(FLUX) is the only one wired today.

Everything this writes lands in ONE place — `~/ob/kmr/Log/IMGEN/` — because a
generated image without the prompt that made it is a lucky roll nobody can
reproduce, and the only way that pairing survives is if writing the image and
recording the prompt are the same action. One sitting is a SHOOT — a numbered
folder; rolls inside it are `IMGEN<shoot>-<prompt><variant>.png`; the shoot's
own page carries every prompt, newest first, as plain copy-pasteable text.

Credentials come from the login keychain, never from a file on disk:
    security find-generic-password -s FAL_KEY -w
"""
import argparse
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
PRESET_DIR = Path.home() / ".config/anchor-system/imgen/presets"
SLUG = "IMGEN"

# `IMGEN007 — Portrait studies` — the number sorts, the title reads.
SHOOT_RE = re.compile(rf"^{SLUG}(\d{{3}})(?: — (.*))?$")
# `IMGEN007-4B.png` — shoot, prompt index, roll letter.
ROLL_RE = re.compile(rf"^{SLUG}\d{{3}}-(\d+)([A-Z])\.")

BACKENDS = {
    "fal": {
        "endpoint": "https://fal.run/fal-ai/flux/dev",
        "model": "fal-ai/flux/dev",
        "keychain": "FAL_KEY",
        "cost_per_image": 0.025,
    },
}


class ImgenError(RuntimeError):
    pass


def keychain(service):
    """Read a secret from the login keychain. Fails loudly — no fallback."""
    r = subprocess.run(["security", "find-generic-password", "-s", service, "-w"],
                       capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        raise ImgenError(
            f"no keychain entry for '{service}'. Add it with:\n"
            f"  security add-generic-password -U -a \"$USER\" -s {service} -w '<key>'")
    return r.stdout.strip()


def load_preset(name):
    f = PRESET_DIR / f"{name}.json"
    return json.loads(f.read_text()) if f.exists() else None


def save_preset(name, prompt):
    PRESET_DIR.mkdir(parents=True, exist_ok=True)
    (PRESET_DIR / f"{name}.json").write_text(
        json.dumps({"name": name, "prompt": prompt,
                    "created": dt.date.today().isoformat()}, indent=2))


# ---------------------------------------------------------------- the anchor

def shoots():
    """Every shoot folder, ascending by number. [(n, title, path), ...]"""
    if not ANCHOR.is_dir():
        return []
    out = []
    for d in ANCHOR.iterdir():
        m = SHOOT_RE.match(d.name) if d.is_dir() else None
        if m:
            out.append((int(m.group(1)), m.group(2) or "", d))
    return sorted(out)


def next_prompt_index(shoot_dir):
    """One past the highest prompt index already used in this shoot."""
    used = [int(m.group(1)) for f in shoot_dir.iterdir()
            if (m := ROLL_RE.match(f.name))]
    return max(used, default=0) + 1


def new_shoot(title):
    """Create the next shoot folder and its namesake page. Returns (n, path)."""
    n = max((b[0] for b in shoots()), default=0) + 1
    path = ANCHOR / f"{SLUG}{n:03d} — {title}"
    path.mkdir(parents=True)
    name = path.name
    (path / f"{name}.md").write_text(
        f"# {name}\n"
        f"{title}. Newest prompt first.\n\n"
        f"| -[[{name}]]- | → [[kmr]] → [[Log/Log]] → [[{SLUG}]] "
        f"→ [{name}](hook://p/{urllib.parse.quote(name)}) |\n"
        f"| --- | --- |\n"
        f"| ... |  |\n", encoding="utf-8")
    return n, path


def grid(files, width=500, across=3):
    """A borderless N-across table. The header row is left empty on purpose —
    markdown makes the first row a heading, and an image there renders as a
    column label instead of a picture."""
    rows = [files[i:i + across] for i in range(0, len(files), across)]
    cols = min(across, max(len(r) for r in rows)) if rows else 1
    out = ["| " * cols + "|", "| " + " | ".join(["---"] * cols) + " |"]
    for r in rows:
        cells = [f"![[{f.name}\\|{width}]]" for f in r] + [""] * (cols - len(r))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def _insert_before_first_group(text, block):
    """Put a prompt group above the existing ones. Newest-first is not a
    preference here — every derived view in this anchor reads top-down and
    trusts that order."""
    m = re.search(rf"^## {SLUG}\d{{3}}-\d+ ", text, re.M)
    if m:
        return text[:m.start()] + block + "\n" + text[m.start():]
    return text.rstrip("\n") + "\n\n" + block


def record_prompt(shoot_dir, shoot_n, idx, title, prompt, files, meta):
    """Write the prompt group into the shoot page, above any earlier group.

    The prompt goes LAST in the block, as a plain paragraph — no heading, no
    blockquote, no fence — so it survives a copy without anything to strip off
    it. That is the whole reason this file writes markdown at all, and it is why
    the seeds line sits above the images rather than under the prompt: nothing
    may come between the prompt and the end of its section."""
    page = shoot_dir / f"{shoot_dir.name}.md"
    block = (f"## {SLUG}{shoot_n:03d}-{idx} — {title}\n\n"
             f"*{meta}*\n\n"
             f"{grid(files)}\n\n{prompt}\n")
    page.write_text(_insert_before_first_group(page.read_text(encoding="utf-8"), block),
                    encoding="utf-8")


def add_to_gallery(shoot_dir, cover):
    """One image per shoot, newest at the top — the visual index."""
    g = ANCHOR / f"{SLUG} Gallery.md"
    if not g.exists():
        return
    entry = f"## [[{shoot_dir.name}]]\n\n![[{cover.name}|500]]\n"
    text = g.read_text(encoding="utf-8")
    m = re.search(r"^## ", text, re.M)
    g.write_text(text[:m.start()] + entry + "\n" + text[m.start():] if m
                 else text.rstrip("\n") + "\n\n" + entry, encoding="utf-8")


def add_member_row(shoot_dir):
    """Register the shoot in the anchor masthead's member zone."""
    a = ANCHOR / f"{SLUG}.md"
    if not a.exists():
        return
    text = a.read_text(encoding="utf-8")
    if shoot_dir.name in text:
        return
    marker = "| ^^^ | |\n"
    if marker in text:
        a.write_text(text.replace(marker, f"{marker}| [[{shoot_dir.name}]]  |  |\n", 1),
                     encoding="utf-8")


# ------------------------------------------------------------------ generate

def generate(spec):
    """One roll. spec = (backend, prompt, size, out_dir, stem)."""
    backend, prompt, size, out_dir, stem = spec
    cfg = BACKENDS[backend]
    body = json.dumps({"prompt": prompt, "image_size": size, "num_images": 1}).encode()
    req = urllib.request.Request(cfg["endpoint"], data=body, headers={
        "Authorization": f"Key {keychain(cfg['keychain'])}",
        "Content-Type": "application/json"})
    try:
        resp = json.load(urllib.request.urlopen(req, timeout=180))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:200]
        raise ImgenError(f"{backend} HTTP {e.code}: {detail}")
    if not resp.get("images"):
        raise ImgenError(f"{backend} returned no images: {str(resp)[:200]}")

    out = out_dir / f"{stem}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(urllib.request.urlopen(resp["images"][0]["url"], timeout=120).read())
    return out, resp.get("seed", "unknown")


def main():
    ap = argparse.ArgumentParser(
        description="Generate images into the IMGEN anchor, with the prompt recorded beside them.")
    ap.add_argument("prompt", nargs="*", help="the prompt (omit when using --preset alone)")
    ap.add_argument("-b", "--backend", default="fal", choices=sorted(BACKENDS))
    ap.add_argument("-r", "--rolls", type=int, default=1, help="images off this prompt")
    ap.add_argument("-s", "--size", default="square_hd")
    # Exactly one of these is required. There is deliberately NO default: an
    # unflagged call used to append to whatever was newest, which is silent and
    # wrong the moment the newest shoot is not the one you meant. A stateful
    # "current shoot" pointer was considered and rejected for the same reason —
    # it outlives the sitting and is shared across agents, so it reproduces the
    # silent mis-append with extra machinery to debug.
    # `-a` takes the number rather than defaulting to the newest. Two reasons:
    # an optional-argument `-a` swallows the prompt as its own value, so the
    # bare form is unusable next to a positional; and "the newest" is the same
    # implicit choice this whole flag pair exists to remove. `--list` is how you
    # find the number, and a wrong one names every shoot you do have.
    where = ap.add_mutually_exclusive_group(required=True)
    where.add_argument("-n", "--new", metavar="TITLE", default=None,
                       help="open a NEW shoot with this title")
    where.add_argument("-a", "--append", type=int, default=None, metavar="N",
                       help="append to shoot N (see --list)")
    where.add_argument("-l", "--list", action="store_true",
                       help="print the shoots and exit")
    ap.add_argument("-c", "--caption", default=None,
                    help="heading for this prompt group (defaults to the shoot title)")
    ap.add_argument("-p", "--preset", default=None, help="named preset to load")
    ap.add_argument("--save-preset", default=None, help="save this prompt as a preset")
    ap.add_argument("--confirm-over", type=float, default=1.00,
                    help="refuse a run costing more than this without --yes")
    ap.add_argument("--yes", action="store_true", help="skip the cost confirmation")
    ap.add_argument("--dry-run", action="store_true",
                    help="resolve the shoot and print what would be written; no API call")
    a = ap.parse_args()

    if a.list:
        for n, title, d in shoots():
            print(f"  {n:03d}  {title}  ({next_prompt_index(d) - 1} prompt group(s))")
        return 0

    prompt = " ".join(a.prompt).strip()
    if a.preset:
        pre = load_preset(a.preset)
        if not pre:
            raise ImgenError(f"no preset '{a.preset}' in {PRESET_DIR}")
        prompt = f"{pre['prompt']} {prompt}".strip()
    if not prompt:
        ap.error("no prompt (give one, or use --preset)")
    if a.save_preset:
        save_preset(a.save_preset, prompt)
        print(f"preset '{a.save_preset}' saved to {PRESET_DIR}")

    cost = BACKENDS[a.backend]["cost_per_image"] * a.rolls
    if cost > a.confirm_over and not a.yes:
        raise ImgenError(
            f"would cost ${cost:.2f} (> ${a.confirm_over:.2f}). Re-run with --yes.")
    if a.rolls > len(string.ascii_uppercase):
        raise ImgenError(f"at most {len(string.ascii_uppercase)} rolls off one prompt")

    # Resolve the shoot from the flag the caller was forced to pick.
    fresh = False
    if a.new:
        if a.dry_run:
            n = max((b[0] for b in shoots()), default=0) + 1
            print(f"dry-run: would open {SLUG}{n:03d} — {a.new} ← "
                  f"{SLUG}{n:03d}-1[{string.ascii_uppercase[:a.rolls]}] (${cost:.3f})")
            return 0
        shoot_n, shoot_dir = new_shoot(a.new)
        shoot_title, fresh = a.new, True
    else:
        found = shoots()
        if not found:
            raise ImgenError('nothing to append to — open one with -n "<what it is about>"')
        if a.append:
            hit = [b for b in found if b[0] == a.append]
            if not hit:
                have = ", ".join(f"{b[0]:03d} ({b[1]})" for b in found)
                raise ImgenError(f"no shoot {a.append:03d} in {ANCHOR} — have {have}")
            shoot_n, shoot_title, shoot_dir = hit[0]
        else:
            shoot_n, shoot_title, shoot_dir = found[-1]

    idx = next_prompt_index(shoot_dir)
    if a.dry_run:
        print(f"dry-run: {shoot_dir.name} ← {SLUG}{shoot_n:03d}-{idx}"
              f"[{string.ascii_uppercase[:a.rolls]}] (${cost:.3f})")
        return 0

    specs = [(a.backend, prompt, a.size, shoot_dir,
              f"{SLUG}{shoot_n:03d}-{idx}{string.ascii_uppercase[i]}")
             for i in range(a.rolls)]

    rolls, failed = [], []
    with cf.ThreadPoolExecutor(min(4, a.rolls)) as ex:
        for fut in [ex.submit(generate, s) for s in specs]:
            try:
                rolls.append(fut.result())
            except Exception as e:
                failed.append(str(e))
    rolls.sort()
    written = [p for p, _ in rolls]

    # Record only what actually landed. A half-failed run still gets its prompt
    # written, because the rolls that DID land are unreproducible without it.
    if written:
        cfg = BACKENDS[a.backend]
        seeds = ", ".join(f"{p.stem.split('-')[-1]} {s}" for p, s in rolls)
        meta = (f"{cfg['model']} · {a.size} · {dt.date.today().isoformat()} · "
                f"${cfg['cost_per_image'] * len(written):.3f} · seeds {seeds}")
        record_prompt(shoot_dir, shoot_n, idx, a.caption or shoot_title,
                      prompt, written, meta)
        if fresh:
            add_member_row(shoot_dir)
            add_to_gallery(shoot_dir, written[0])

    for p in written:
        print(f"  {p.name}")
    for f in failed:
        print(f"  FAILED: {f}", file=sys.stderr)
    print(f"{len(written)} roll(s) as {SLUG}{shoot_n:03d}-{idx}, "
          f"${BACKENDS[a.backend]['cost_per_image']*len(written):.3f} — {shoot_dir}")
    return 1 if failed else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ImgenError as e:
        print(f"imgen: {e}", file=sys.stderr)
        sys.exit(2)
