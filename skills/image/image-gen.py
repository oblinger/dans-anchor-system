#!/usr/bin/env python3
"""image-gen.py — generate images from a prompt, with a sidecar and a cost line.

The engine behind the /image skill (SKA F276). Backends are pluggable; `fal`
(FLUX) is the only one wired today. Every image written gets a sidecar carrying
the prompt, model, seed, date, and cost — without it a good result is a lucky
roll that can never be reproduced.

Credentials come from the login keychain, never from a file on disk:
    security find-generic-password -s FAL_KEY -w
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

PRESET_DIR = Path.home() / ".config/anchor-system/image/presets"
DEFAULT_OUT = Path.home() / "ob/data/MyDesk"

BACKENDS = {
    "fal": {
        "endpoint": "https://fal.run/fal-ai/flux/dev",
        "model": "fal-ai/flux/dev",
        "keychain": "FAL_KEY",
        "cost_per_image": 0.025,
    },
}


class ImageGenError(RuntimeError):
    pass


def keychain(service):
    """Read a secret from the login keychain. Fails loudly — no fallback."""
    r = subprocess.run(["security", "find-generic-password", "-s", service, "-w"],
                       capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        raise ImageGenError(
            f"no keychain entry for '{service}'. Add it with:\n"
            f"  security add-generic-password -U -a \"$USER\" -s {service} -w '<key>'")
    return r.stdout.strip()


def load_preset(name):
    """Return a preset's locked prompt, or None if no such preset."""
    f = PRESET_DIR / f"{name}.json"
    if not f.exists():
        return None
    return json.loads(f.read_text())


def save_preset(name, prompt):
    PRESET_DIR.mkdir(parents=True, exist_ok=True)
    (PRESET_DIR / f"{name}.json").write_text(
        json.dumps({"name": name, "prompt": prompt,
                    "created": dt.date.today().isoformat()}, indent=2))


def slug(s, n=40):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:n] or "image"


def generate(spec):
    """One image. spec = (backend, prompt, size, out_dir, label, idx)."""
    backend, prompt, size, out_dir, label, idx = spec
    cfg = BACKENDS[backend]
    body = json.dumps({"prompt": prompt, "image_size": size, "num_images": 1}).encode()
    req = urllib.request.Request(cfg["endpoint"], data=body, headers={
        "Authorization": f"Key {keychain(cfg['keychain'])}",
        "Content-Type": "application/json"})
    try:
        resp = json.load(urllib.request.urlopen(req, timeout=180))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:200]
        raise ImageGenError(f"{backend} HTTP {e.code}: {detail}")
    if not resp.get("images"):
        raise ImageGenError(f"{backend} returned no images: {str(resp)[:200]}")

    img = resp["images"][0]
    seed = resp.get("seed", "unknown")
    stem = f"{label} {idx:02d}" if idx else label
    out = out_dir / f"{stem}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(urllib.request.urlopen(img["url"], timeout=120).read())

    # The sidecar IS the source for a generated image — same basename, always.
    out.with_suffix(".prompt.md").write_text(
        f"# {stem}\n\n"
        f"- **Generated:** {dt.datetime.now().isoformat(timespec='seconds')}\n"
        f"- **Backend:** {backend}\n"
        f"- **Model:** {cfg['model']}\n"
        f"- **Seed:** {seed}\n"
        f"- **Size:** {size}\n"
        f"- **Cost:** ${cfg['cost_per_image']:.3f}\n\n"
        f"## Prompt\n\n{prompt}\n")
    return out


def main():
    ap = argparse.ArgumentParser(description="Generate images with a sidecar and a cost line.")
    ap.add_argument("prompt", nargs="*", help="the prompt (omit when using --preset alone)")
    ap.add_argument("-b", "--backend", default="fal", choices=sorted(BACKENDS))
    ap.add_argument("-n", "--count", type=int, default=1, help="how many images")
    ap.add_argument("-s", "--size", default="square_hd")
    ap.add_argument("-o", "--out", type=Path, default=None, help="output dir")
    ap.add_argument("-l", "--label", default=None, help="basename for the files")
    ap.add_argument("-p", "--preset", default=None, help="named preset to load")
    ap.add_argument("--save-preset", default=None, help="save this prompt as a preset")
    ap.add_argument("--confirm-over", type=float, default=1.00,
                    help="refuse a batch costing more than this without --yes")
    ap.add_argument("--yes", action="store_true", help="skip the cost confirmation")
    a = ap.parse_args()

    prompt = " ".join(a.prompt).strip()
    if a.preset:
        pre = load_preset(a.preset)
        if not pre:
            raise ImageGenError(f"no preset '{a.preset}' in {PRESET_DIR}")
        prompt = f"{pre['prompt']} {prompt}".strip()
        a.label = a.label or a.preset.capitalize()
    if not prompt:
        ap.error("no prompt (give one, or use --preset)")
    if a.save_preset:
        save_preset(a.save_preset, prompt)
        print(f"preset '{a.save_preset}' saved to {PRESET_DIR}")

    cost = BACKENDS[a.backend]["cost_per_image"] * a.count
    if cost > a.confirm_over and not a.yes:
        raise ImageGenError(
            f"batch would cost ${cost:.2f} (> ${a.confirm_over:.2f}). Re-run with --yes.")

    out_dir = a.out or (DEFAULT_OUT / (a.label or slug(prompt)))
    label = a.label or slug(prompt)
    specs = [(a.backend, prompt, a.size, out_dir, label, i if a.count > 1 else 0)
             for i in range(1, a.count + 1)]

    written, failed = [], []
    with cf.ThreadPoolExecutor(min(4, a.count)) as ex:
        for fut in [ex.submit(generate, s) for s in specs]:
            try:
                written.append(fut.result())
            except Exception as e:
                failed.append(str(e))

    for p in written:
        print(f"  {p}")
    for f in failed:
        print(f"  FAILED: {f}", file=sys.stderr)
    print(f"{len(written)} image(s), ${BACKENDS[a.backend]['cost_per_image']*len(written):.3f} "
          f"— {out_dir}")
    return 1 if failed else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ImageGenError as e:
        print(f"image-gen: {e}", file=sys.stderr)
        sys.exit(2)
