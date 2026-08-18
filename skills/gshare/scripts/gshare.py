#!/usr/bin/env python3
"""gshare — publish a markdown file to a link-shared Google Doc, with a register and an expiry.

    gshare <path> [--days N | --forever] [--title T] [--pdf]   publish, or refresh an existing share
    gshare list [--all]                                print the register
    gshare clean [--dry-run]                           sweep expired rows, reconcile against Drive
    gshare rm <path | url | id>                        take one share down now
    gshare open <path | url>                           open the published doc in a browser

Every invocation sweeps expired rows before doing anything else — the expiry has to
fire when nobody is asking, so it cannot depend on an agent noticing.

The register (two markdown tables in one vault page) is the ONLY store: the Drive file
id is recovered from the URL in the Weblink cell, so there is no sidecar and no cache.

Conversion (per F335): markdown → figure pass (Obsidian embeds resolved, mermaid →
PNG via mmdc, SVG rasterized via rsvg-convert) → pandoc DOCX → Drive import to a
native, editable Google Doc. Constructs that only render inside Obsidian (dataview,
excalidraw, note transclusions) never block the publish: each becomes a marked gap in
the published Doc and a line in the CLI report. `--pdf` publishes a PDF instead
(pandoc HTML + headless Chrome print) for docs whose value is layout.

Config: ~/.config/anchor-system/gshare/config.yaml (per F080).
  drive_folder_id: <Drive folder that receives shares>   (required)
  credentials:     <OAuth client json with a drive scope> (required)
  register:        <path to the register page>            (default: {skill_data_root}/gshare/gshare register.md)
  default_days:    30

Per F325; fidelity upgrade per F335.
"""

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import NoReturn

CONFIG_ROOT = Path(os.environ.get("ANCHOR_SYSTEM_ROOT", Path.home() / ".config/anchor-system"))
SKILL = "gshare"
DRIVE = "https://www.googleapis.com/drive/v3"
UPLOAD = "https://www.googleapis.com/upload/drive/v3"
DOC_ID_RE = re.compile(r"/(?:document|file|spreadsheets|presentation)/d/([A-Za-z0-9_-]{10,})")
TODAY = dt.date.today()
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def die(msg) -> NoReturn:
    sys.exit(f"gshare: {msg}")


# ---------------------------------------------------------------- configuration

def _yaml(path):
    if not path.is_file():
        return {}
    try:
        import yaml
    except ImportError:
        die("PyYAML is not installed, and the config is YAML — `pip install pyyaml`")
    return yaml.safe_load(path.read_text()) or {}


def config():
    """Layered read: hardcoded default < global.yaml < gshare/config.yaml < env."""
    glob = _yaml(CONFIG_ROOT / "global.yaml")
    skill_cfg = CONFIG_ROOT / SKILL / "config.yaml"
    cfg = dict(_yaml(skill_cfg))

    def get(key, default=None):
        env = os.environ.get(f"ANCHOR_SYSTEM_{SKILL.upper()}_{key.upper()}")
        if env:
            return env
        if key in cfg and cfg[key] not in (None, ""):
            return cfg[key]
        return default

    vault_root = get("vault_root", glob.get("vault_root"))
    if not vault_root:
        die(f"no vault_root — set it in {CONFIG_ROOT/'global.yaml'}")
    vault_root = Path(vault_root).expanduser().resolve()

    folder = get("drive_folder_id")
    creds = get("credentials")
    missing = [k for k, v in (("drive_folder_id", folder), ("credentials", creds)) if not v]
    if missing:
        die(f"missing required key(s) {', '.join(missing)} in {skill_cfg} — "
            f"create that file with drive_folder_id (the Drive folder that receives "
            f"shares) and credentials (an OAuth client json with a drive scope)")

    # Durable, skill-owned, in-vault data goes under skill_data_root/<skill>/ —
    # the key global.yaml already defines for exactly this, and which `dupes`
    # already occupies. NOT the Catalog: CAT's own rule 2 is "sub-catalogs
    # route, they don't warehouse", so a register of live URLs is data the
    # Catalog should point AT, never hold.
    data_root = Path(str(get("skill_data_root",
                             glob.get("skill_data_root", vault_root / "SYS/anchor-system")))).expanduser()
    register = Path(str(get("register", data_root / SKILL / f"{SKILL} register.md"))).expanduser()
    return {
        "vault_root": vault_root,
        "drive_folder_id": str(folder),
        "credentials": Path(str(creds)).expanduser(),
        "register": register,
        "default_days": int(get("default_days", 30)),
    }


# ------------------------------------------------------------------- Drive API

def access_token(creds_path):
    if not creds_path.is_file():
        die(f"no credentials at {creds_path}")
    c = json.loads(creds_path.read_text())
    body = urllib.parse.urlencode({
        "client_id": c["client_id"],
        "client_secret": c["client_secret"],
        "refresh_token": c["refresh_token"],
        "grant_type": "refresh_token",
    }).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(
                c.get("token_uri", "https://oauth2.googleapis.com/token"), data=body)) as r:
            return json.load(r)["access_token"]
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        if "invalid_grant" in detail:
            die("the refresh token has expired (Google keeps test-mode tokens for 7 days). "
                "Re-auth, then re-run:\n"
                "  python3 ~/.claude/skills/anchor/scripts/gsa-reauth.py")
        die(f"token refresh failed: {e} {detail}")


def api(token, method, url, body=None, content_type="application/json", raw=None):
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    if data is not None:
        req.add_header("Content-Type", content_type)
    try:
        with urllib.request.urlopen(req) as r:
            payload = r.read()
            return json.loads(payload) if payload else {}
    except urllib.error.HTTPError as e:
        die(f"Drive {method} {url.split('?')[0]} failed: {e.code} {e.read().decode(errors='replace')[:400]}")


def multipart(metadata, payload: bytes, payload_type: str):
    boundary = uuid.uuid4().hex
    head = (
        f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n"
        f"{json.dumps(metadata)}\r\n"
        f"--{boundary}\r\nContent-Type: {payload_type}\r\n\r\n"
    ).encode()
    tail = f"\r\n--{boundary}--\r\n".encode()
    return head + payload + tail, f"multipart/related; boundary={boundary}"


def drive_create(token, name, folder, payload, payload_type, as_gdoc):
    meta = {"name": name, "parents": [folder]}
    if as_gdoc:
        meta["mimeType"] = "application/vnd.google-apps.document"
    body, ctype = multipart(meta, payload, payload_type)
    return api(token, "POST",
               f"{UPLOAD}/files?uploadType=multipart&fields=id,name,webViewLink",
               content_type=ctype, raw=body)


def drive_update(token, file_id, name, payload, payload_type):
    body, ctype = multipart({"name": name}, payload, payload_type)
    return api(token, "PATCH",
               f"{UPLOAD}/files/{file_id}?uploadType=multipart&fields=id,name,webViewLink",
               content_type=ctype, raw=body)


def drive_share(token, file_id):
    api(token, "POST", f"{DRIVE}/files/{file_id}/permissions",
        body={"role": "reader", "type": "anyone", "allowFileDiscovery": False})


def drive_unshare(token, file_id):
    """Revoke the anyone-with-the-link permission.

    Load-bearing, and not obvious: trashing a Drive file does NOT revoke its
    link share. Measured 2026-08-12 while verifying F325, against
    `/document/d/<id>/export?format=txt` with no credentials — shared-and-live
    307, shared-and-TRASHED still 307, revoked 401. So an expiry that only
    trashed would leave every "expired" link serving the document. Revoke
    first, because that is what takes the link down; trash after, so the
    content stays recoverable.

    Probe the export endpoint, never `/edit` — a denied `/edit` returns 200
    carrying Google's "you need access" page, so it cannot tell the two apart.
    """
    perms = api(token, "GET", f"{DRIVE}/files/{file_id}/permissions?fields=permissions(id,type)")
    for perm in perms.get("permissions", []):
        if perm.get("type") == "anyone":
            api(token, "DELETE", f"{DRIVE}/files/{file_id}/permissions/{perm['id']}")


def drive_takedown(token, file_id):
    """Revoke the link, then trash. Order matters — see drive_unshare."""
    drive_unshare(token, file_id)
    api(token, "PATCH", f"{DRIVE}/files/{file_id}", body={"trashed": True})


def drive_get(token, file_id):
    """Returns the file dict, or None when it is gone or trashed."""
    url = f"{DRIVE}/files/{file_id}?fields=id,name,trashed,webViewLink"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as r:
            f = json.load(r)
    except urllib.error.HTTPError as e:
        if e.code in (404, 403):
            return None
        die(f"Drive get failed: {e.code} {e.read().decode(errors='replace')[:300]}")
    return None if f.get("trashed") else f


def drive_list(token, folder):
    q = urllib.parse.quote(f"'{folder}' in parents and trashed=false")
    out, page = [], None
    while True:
        url = f"{DRIVE}/files?q={q}&fields=nextPageToken,files(id,name,webViewLink)&pageSize=200"
        if page:
            url += f"&pageToken={page}"
        r = api(token, "GET", url)
        out.extend(r.get("files", []))
        page = r.get("nextPageToken")
        if not page:
            return out


# --------------------------------------------------- markdown → DOCX / PDF (F335)

WIKI_PIPED = re.compile(r"\[\[([^\[\]|]+)\|([^\[\]]+)\]\]")
WIKI_PLAIN = re.compile(r"\[\[([^\[\]|]+)\]\]")
BLOCK_ID = re.compile(r"\s+\^[A-Za-z0-9][A-Za-z0-9-]*\s*$")
EMBED = re.compile(r"!\[\[([^\[\]|]+?)(?:\|[^\[\]]*)?\]\]")
MD_IMG = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
FENCE = re.compile(r"^\s*(```+|~~~+)\s*(\S*)")
CALLOUT = re.compile(r"^(\s*>\s*)\[!(\w+)\][+-]?\s*(.*)$")

IMG_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"}
# Fence languages that render only inside Obsidian's plugin runtime. No external
# renderer exists for these — not DOCX, and not the PDF lane either (headless
# Chrome prints the same markdown without the plugins), which is why the answer
# is a marked gap + report, never a format switch (F335 Q1, Dan 2026-08-17).
OBSIDIAN_ONLY_FENCES = {"dataview", "dataviewjs", "query", "tasks"}


def _tool(name, hint):
    """Locate a rendering dependency. Missing tool = environment error = die
    (unlike a failing construct, which is a content gap and reports)."""
    p = shutil.which(name)
    if not p and (Path("/opt/homebrew/bin") / name).is_file():
        p = str(Path("/opt/homebrew/bin") / name)
    if not p:
        die(f"`{name}` is required for this document and is not installed — {hint}")
    return p


class Gap:
    def __init__(self, line, what, detail=""):
        self.line, self.what, self.detail = line, what, detail


def flatten_wikilinks(text):
    """A wiki-link renders as literal brackets to someone without the vault."""
    text = WIKI_PIPED.sub(lambda m: m.group(2), text)
    return WIKI_PLAIN.sub(lambda m: m.group(1).split("/")[-1].split("#")[0], text)


def strip_frontmatter(text):
    if text.startswith("---\n"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[text.find("\n", end + 1) + 1:]
    return text


def strip_vault_noise(text):
    """Frontmatter, HTML comments, `:>>` breadcrumbs, block-ids."""
    text = strip_frontmatter(text)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    lines = []
    for line in text.splitlines():
        if line.lstrip().startswith(":>>"):
            continue
        lines.append(BLOCK_ID.sub("", line))
    return "\n".join(lines)


def prepare(text):
    """Title/date extraction view of the doc — strip noise, flatten links."""
    return flatten_wikilinks(strip_vault_noise(text)).strip() + "\n"


class FigurePass:
    """Resolve every figure the doc carries into a real image file, and turn
    every construct that cannot render outside Obsidian into a marked gap.
    All images land in the workdir under space-free names so both pandoc and
    Chrome can reference them without path-quoting trouble."""

    def __init__(self, src, cfg, workdir):
        self.src, self.cfg, self.workdir = src, cfg, workdir
        self.gaps, self._index, self._n = [], None, 0

    def vault_lookup(self, basename):
        if self._index is None:
            self._index = {}
            for root, dirs, files in os.walk(self.cfg["vault_root"]):
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                for f in files:
                    self._index.setdefault(f.lower(), Path(root) / f)
        return self._index.get(basename.lower())

    def stage_image(self, path, line_no, alt=""):
        """Copy (rasterizing SVG) into the workdir; return markdown, or None on gap.

        `alt` is load-bearing and defaults to EMPTY on purpose: pandoc turns a
        lone `![text](img)` paragraph into a *captioned figure*, so passing the
        filename here would print "TINK" under every Obsidian `![[TINK.png]]`
        embed — a caption the vault reader never sees. Embeds pass nothing;
        an explicit markdown image passes the author's own alt, because there
        the caption was written deliberately.
        """
        self._n += 1
        if path.suffix.lower() == ".svg":
            out = self.workdir / f"fig-{self._n}.png"
            rsvg = _tool("rsvg-convert", "`brew install librsvg` (Docs mangles imported SVG, so gshare rasterizes it)")
            r = subprocess.run([rsvg, "-o", str(out), "--zoom", "2", str(path)],
                               capture_output=True, text=True, timeout=120)
            if r.returncode != 0 or not out.is_file():
                self.gaps.append(Gap(line_no, f"SVG `{path.name}`",
                                     f"rasterization failed: {r.stderr.strip()[:120]}"))
                return None
        else:
            out = self.workdir / f"fig-{self._n}{path.suffix.lower()}"
            shutil.copy2(path, out)
        return f"![{alt}]({out})"

    def gap_marker(self, line_no, what, detail):
        self.gaps.append(Gap(line_no, what, detail))
        return f"**[⚠ not converted: {what} — {detail}]**"

    def gap_block(self, line_no, what, detail, source_lines):
        self.gaps.append(Gap(line_no, what, detail))
        out = ["", f"> ⚠ **Not converted: {what}** — {detail} Source preserved:", ">"]
        out += [f">     {s}" for s in source_lines]
        out.append("")
        return out

    def embed_repl(self, m, line_no):
        name = m.group(1).strip()
        base = name.split("#")[0].strip()
        ext = Path(base).suffix.lower()
        if ".excalidraw" in base.lower():
            stem = base[: base.lower().index(".excalidraw")]
            for cand_ext in (".png", ".svg"):
                p = self.vault_lookup(Path(stem).name + ".excalidraw" + cand_ext) \
                    or self.vault_lookup(Path(stem).name + cand_ext)
                if p:
                    staged = self.stage_image(p, line_no)
                    if staged:
                        return staged
            return self.gap_marker(line_no, f"Excalidraw drawing `{base}`",
                                   "renders only inside Obsidian and no exported .png/.svg sits beside it — export one in Obsidian")
        if ext in IMG_EXTS:
            p = self.vault_lookup(Path(base).name)
            if not p:
                return self.gap_marker(line_no, f"image embed `{base}`", "not found anywhere in the vault")
            staged = self.stage_image(p, line_no)
            return staged if staged else f"**[⚠ not converted: `{base}`]**"
        if ext in ("", ".md"):
            return self.gap_marker(line_no, f"note transclusion `{name}`",
                                   "embedding another note renders only inside Obsidian; share that note separately or inline it")
        return self.gap_marker(line_no, f"embedded {ext} file `{base}`",
                               "a Google Doc cannot carry this file type inline")

    def md_img_repl(self, m, line_no):
        alt, ref = m.group(1), m.group(2)
        if ref.startswith(("http://", "https://", "data:")):
            return m.group(0)
        raw = urllib.parse.unquote(ref)
        p = Path(raw) if raw.startswith("/") else (self.src.parent / raw)
        if not p.is_file():
            return self.gap_marker(line_no, f"image `{ref}`", "file not found relative to the source doc")
        staged = self.stage_image(p.resolve(), line_no, alt=alt)
        return staged if staged else f"**[⚠ not converted: `{ref}`]**"

    def render_mermaid(self, source):
        mmdc = _tool("mmdc", "`npm install -g @mermaid-js/mermaid-cli`")
        self._n += 1
        mmd = self.workdir / f"mermaid-{self._n}.mmd"
        png = self.workdir / f"mermaid-{self._n}.png"
        mmd.write_text(source)
        r = subprocess.run([mmdc, "-i", str(mmd), "-o", str(png), "-b", "white",
                            "--scale", "2", "--quiet"],
                           capture_output=True, text=True, timeout=180)
        if r.returncode != 0 or not png.is_file():
            err = (r.stderr or r.stdout).strip().splitlines()
            return None, (err[-1][:160] if err else "mmdc produced no output")
        return png, None

    def run(self, text):
        lines = text.splitlines()
        out, i = [], 0
        while i < len(lines):
            line = lines[i]
            f = FENCE.match(line)
            if f:
                fence, lang = f.group(1), f.group(2).lower()
                j = i + 1
                while j < len(lines) and not lines[j].strip().startswith(fence[0] * 3):
                    j += 1
                body = lines[i + 1:j]
                if lang == "mermaid":
                    png, err = self.render_mermaid("\n".join(body) + "\n")
                    if png:
                        out += ["", f"![]({png})", ""]
                    else:
                        out += self.gap_block(i + 1, "mermaid diagram",
                                              f"mmdc failed to render it ({err}).", body)
                elif lang in OBSIDIAN_ONLY_FENCES:
                    out += self.gap_block(i + 1, f"`{lang}` block",
                                          "it renders only inside Obsidian's plugin runtime.", body)
                else:
                    out += lines[i:j + 1] if j < len(lines) else lines[i:]
                i = j + 1
                continue
            c = CALLOUT.match(line)
            if c:
                title = c.group(3).strip()
                head = c.group(2).capitalize() + (f" — {title}" if title else "")
                line = f"{c.group(1)}**{head}**"
            else:
                # MD_IMG first, EMBED second — embed replacements emit ![..](..)
                # markdown that must not be re-processed as a source image.
                n = i + 1
                line = MD_IMG.sub(lambda m: self.md_img_repl(m, n), line)
                line = EMBED.sub(lambda m: self.embed_repl(m, n), line)
            out.append(line)
            i += 1
        return "\n".join(out)


def convert(src, text, cfg, workdir, pdf=False, title=""):
    """The one conversion path: noise strip → figure pass → flatten →
    pandoc DOCX (or pandoc HTML → Chrome print for --pdf).
    Returns (payload_bytes, payload_mime, as_gdoc, gaps)."""
    pandoc = _tool("pandoc", "`brew install pandoc`")
    fp = FigurePass(src, cfg, workdir)
    md = flatten_wikilinks(fp.run(strip_vault_noise(text))).strip() + "\n"
    if not pdf:
        out = workdir / "out.docx"
        r = subprocess.run([pandoc, "-f", "gfm", "-t", "docx", "-o", str(out)],
                           input=md, text=True, capture_output=True, timeout=120)
        if r.returncode != 0:
            die(f"pandoc → docx failed: {r.stderr.strip()[:400]}")
        return out.read_bytes(), DOCX_MIME, True, fp.gaps
    # --pdf lane: pandoc HTML body, vault-ish stylesheet, headless Chrome print.
    if not Path(CHROME).is_file():
        die(f"--pdf needs Google Chrome for headless printing and {CHROME} does not exist")
    r = subprocess.run([pandoc, "-f", "gfm", "-t", "html"],
                       input=md, text=True, capture_output=True, timeout=120)
    if r.returncode != 0:
        die(f"pandoc → html failed: {r.stderr.strip()[:400]}")
    import html as _html
    html_path = workdir / "out.html"
    # .replace, not .format — the body is arbitrary document HTML and may carry braces.
    html_path.write_text(HTML_SHELL.replace("__TITLE__", _html.escape(title or src.stem))
                                   .replace("__BODY__", r.stdout))
    pdf_path = workdir / "out.pdf"
    # WAIT ON THE ARTIFACT, NOT THE PROCESS. Measured 2026-08-17 (F335): Chrome
    # 151 writes a complete PDF in about two seconds and then never exits — its
    # bundled updater keeps the process group alive, so `subprocess.run` waits
    # until the timeout even though the file has been sitting there, finished,
    # the whole time. All three headless modes behave identically, so this is
    # not a mode to flag around; the wait condition was simply wrong.
    proc = subprocess.Popen([CHROME, "--headless", "--disable-gpu",
                             "--no-first-run", "--no-default-browser-check",
                             f"--user-data-dir={workdir}/chrome-profile",
                             "--no-pdf-header-footer", "--virtual-time-budget=10000",
                             f"--print-to-pdf={pdf_path}", f"file://{html_path}"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        stable, last = 0, -1
        for _ in range(240):                       # 120 s ceiling, 0.5 s steps
            if proc.poll() is not None and pdf_path.is_file():
                break
            size = pdf_path.stat().st_size if pdf_path.is_file() else -1
            # Two consecutive equal, non-zero sizes means the write finished.
            stable = stable + 1 if size == last and size > 0 else 0
            last = size
            if stable >= 2:
                break
            time.sleep(0.5)
    finally:
        proc.kill()
        try:
            err = (proc.communicate(timeout=10)[1] or b"").decode(errors="replace")
        except subprocess.TimeoutExpired:
            err = ""
    if not pdf_path.is_file() or pdf_path.stat().st_size == 0:
        die(f"Chrome headless print produced no PDF: {err.strip()[-400:]}")
    return pdf_path.read_bytes(), "application/pdf", False, fp.gaps


HTML_SHELL = """<!doctype html><html><head><meta charset="utf-8"><title>__TITLE__</title><style>
body { font-family: -apple-system, 'Helvetica Neue', Helvetica, sans-serif; max-width: 48em;
       margin: 2em auto; padding: 0 2em; line-height: 1.55; color: #1a1a1a; }
h1, h2, h3 { line-height: 1.25; }
img { max-width: 100%; }
table { border-collapse: collapse; margin: 1em 0; }
th, td { border: 1px solid #bbb; padding: 4px 10px; text-align: left; }
code { background: #f4f4f4; padding: 1px 4px; border-radius: 3px; font-size: 0.9em; }
pre { background: #f4f4f4; padding: 10px; overflow-x: auto; border-radius: 4px; }
pre code { background: none; padding: 0; }
blockquote { border-left: 3px solid #ccc; margin-left: 0; padding-left: 1em; color: #444; }
</style></head><body>__BODY__</body></html>"""


def report_gaps(gaps):
    if not gaps:
        return
    n = len(gaps)
    print(f"  ⚠ published, but {n} construct{'s' if n > 1 else ''} could not convert:")
    for g in gaps:
        detail = f" — {g.detail}" if g.detail else ""
        print(f"    · line {g.line}: {g.what}{detail}")


DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def doc_title(path, text):
    for line in prepare(text).splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def source_date(path, text):
    m = DATE_RE.match(path.stem)
    if m:
        return m.group(1)
    head = "\n".join(text.splitlines()[:60])
    m = re.search(r"\((\d{4}-\d{2}-\d{2})\)", head)
    return m.group(1) if m else TODAY.isoformat()


def drive_name(path, text, override):
    title = override or doc_title(path, text)
    title = DATE_RE.sub("", title).replace("()", "").strip(" -—·")
    return f"{source_date(path, text)} {title}".strip()


# ---------------------------------------------------------------- the register

HEAD = """---
description: "Every document currently published out of the vault to a link-shared Google Doc — the register `gshare` keeps."
---
# gshare register
Every document currently published out of the vault as a link-shared Google Doc, and when each one comes back down.

Machine-written by `gshare` (per [[TINK325 - gshare: publish markdown to link-shared Google Docs that expire|F325]]) — **do not hand-edit below this line.** To publish, run `gshare <path>`; to take something down early, `gshare rm <path>`. Every link here is viewable by anyone holding it and is not searchable. Anything in the Drive folder that this table does not list was not put there by `gshare`, and `gshare clean` reports it rather than touching it.

"""

SPLIT_PIPE = re.compile(r"(?<!\\)\|")
MD_LINK = re.compile(r"^\[(.*)\]\((.+)\)$")


def cell_split(row):
    return [c.strip() for c in SPLIT_PIPE.split(row.strip().strip("|"))]


def page_cell(path, vault_root):
    """Full path as the target, basename as the display (Dan's rule)."""
    try:
        rel = path.resolve().relative_to(vault_root)
    except ValueError:
        return f"[{path.name}](file://{urllib.parse.quote(str(path))})"
    target = str(rel.with_suffix("")) if rel.suffix == ".md" else str(rel)
    return f"[[{target}\\|{path.stem}]]"


def parse_page_cell(cell, vault_root):
    cell = cell.strip()
    m = re.match(r"^\[\[(.+?)\]\]$", cell)
    if m:
        target = m.group(1).replace("\\|", "|").split("|")[0].strip()
        p = vault_root / target
        return p if p.suffix else p.with_suffix(".md")
    m = MD_LINK.match(cell)
    if m and m.group(2).startswith("file://"):
        return Path(urllib.parse.unquote(m.group(2)[7:]))
    return None


class Row:
    def __init__(self, added, expires, url, name, path):
        self.added, self.expires, self.url, self.name, self.path = added, expires, url, name, path

    @property
    def doc_id(self):
        m = DOC_ID_RE.search(self.url)
        return m.group(1) if m else None

    def expired(self):
        return self.expires is not None and self.expires < TODAY.isoformat()


def read_register(cfg):
    path, vault_root = cfg["register"], cfg["vault_root"]
    if not path.is_file():
        return []
    rows, section = [], None
    for line in path.read_text().splitlines():
        s = line.strip()
        if s.startswith("## "):
            section = s[3:].strip().lower()
            continue
        if not s.startswith("|") or section not in ("expiring", "permanent"):
            continue
        cells = cell_split(s)
        if not cells or cells[0].lower() in ("added", "") or set(cells[0]) <= set("-: "):
            continue
        if section == "expiring" and len(cells) >= 4:
            added, expires, link, page = cells[0], cells[1], cells[2], cells[3]
        elif section == "permanent" and len(cells) >= 3:
            added, expires, link, page = cells[0], None, cells[1], cells[2]
        else:
            continue
        m = MD_LINK.match(link)
        if not m:
            continue
        rows.append(Row(added, expires, m.group(2).strip(), m.group(1).strip(),
                        parse_page_cell(page, vault_root)))
    return rows


def write_register(cfg, rows):
    vault_root = cfg["vault_root"]
    exp = sorted([r for r in rows if r.expires], key=lambda r: (r.expires, r.name))
    perm = sorted([r for r in rows if not r.expires], key=lambda r: (r.added, r.name))
    out = [HEAD, "## Expiring\n"]
    if exp:
        out.append("| Added | Expires | Weblink | Page |\n| --- | --- | --- | --- |")
        for r in exp:
            out.append(f"| {r.added} | {r.expires} | [{r.name}]({r.url}) | "
                       f"{page_cell(r.path, vault_root) if r.path else '—'} |")
        out.append("")
    else:
        out.append("*(none)*\n")
    out.append("## Permanent\n")
    if perm:
        out.append("| Added | Weblink | Page |\n| --- | --- | --- |")
        for r in perm:
            out.append(f"| {r.added} | [{r.name}]({r.url}) | "
                       f"{page_cell(r.path, vault_root) if r.path else '—'} |")
        out.append("")
    else:
        out.append("*(none)*\n")
    cfg["register"].parent.mkdir(parents=True, exist_ok=True)
    cfg["register"].write_text("\n".join(out).rstrip() + "\n")


def find_row(rows, needle):
    """Match a row by source path, by URL, or by Drive file id."""
    m = DOC_ID_RE.search(needle)
    if m:
        for r in rows:
            if r.doc_id == m.group(1):
                return r
    p = Path(needle).expanduser()
    if p.exists():
        p = p.resolve()
        for r in rows:
            if r.path and r.path.resolve() == p:
                return r
    for r in rows:
        if r.url == needle or (r.path and r.path.name == needle):
            return r
    return None


# ----------------------------------------------------------------- the actions

def sweep(token, rows, dry_run=False, verbose=True):
    """Take down every share whose expiry has passed. Runs on every invocation."""
    live, taken = [], []
    for r in rows:
        if r.expired():
            taken.append(r)
            if not dry_run and r.doc_id:
                drive_takedown(token, r.doc_id)
        else:
            live.append(r)
    if taken and verbose:
        verb = "would expire" if dry_run else "expired"
        for r in taken:
            print(f"gshare: {verb} {r.name} (was due {r.expires})")
    return live, taken


def cmd_publish(cfg, args):
    src = Path(args.target).expanduser()
    if not src.is_file():
        die(f"no such file: {src}")
    if src.suffix.lower() not in (".md", ".markdown", ".txt"):
        die(f"{src.name} is not markdown — gshare publishes markdown, not {src.suffix or 'extensionless files'}")

    token = access_token(cfg["credentials"])
    rows, taken = sweep(token, read_register(cfg))

    text = src.read_text()
    name = drive_name(src, text, args.title)
    with tempfile.TemporaryDirectory(prefix="gshare-") as td:
        payload, ptype, as_gdoc, gaps = convert(src, text, cfg, Path(td),
                                                pdf=args.pdf, title=name)
        expires = None if args.forever else (TODAY + dt.timedelta(days=args.days or cfg["default_days"])).isoformat()

        # Decide the lane first, then act once. A registered row is refreshable
        # only when its Drive file is still live AND it is the same kind of file
        # we are about to upload: Drive cannot convert a Doc into a PDF (or back)
        # in place, so a lane switch has to take the old share down and mint a
        # fresh URL rather than silently leaving the previous format published.
        existing = find_row(rows, str(src))
        live = bool(existing and existing.doc_id and drive_get(token, existing.doc_id))
        same_lane = bool(existing and ("/document/" in existing.url) == as_gdoc)

        if existing and live and same_lane:
            f = drive_update(token, existing.doc_id, name, payload, ptype)
            existing.name, existing.expires = f["name"], expires
            row, verb = existing, "refreshed"
        else:
            if existing:
                if live:
                    drive_takedown(token, existing.doc_id)
                rows.remove(existing)
            f = drive_create(token, name, cfg["drive_folder_id"], payload, ptype, as_gdoc)
            drive_share(token, f["id"])
            row = Row(TODAY.isoformat(), expires, f["webViewLink"], f["name"], src.resolve())
            rows.append(row)
            verb = "published"

    write_register(cfg, rows)
    print(f"gshare: {verb} {row.name}{' (PDF)' if args.pdf else ''}")
    print(f"  {row.url}")
    print(f"  {'never expires' if not row.expires else 'expires ' + row.expires}"
          f" · register: {cfg['register']}")
    report_gaps(gaps)
    if taken:
        print(f"  ({len(taken)} expired share{'s' if len(taken) > 1 else ''} swept on the way in)")


def cmd_list(cfg, args):
    token = access_token(cfg["credentials"])
    rows, _ = sweep(token, read_register(cfg))
    write_register(cfg, rows)
    if not rows:
        print("gshare: nothing published")
        return
    for r in sorted(rows, key=lambda r: (r.expires or "9999", r.name)):
        when = f"until {r.expires}" if r.expires else "permanent"
        left = ""
        if r.expires:
            days = (dt.date.fromisoformat(r.expires) - TODAY).days
            left = f" ({days}d)"
        print(f"{when}{left:>7}  {r.name}")
        if args.all:
            print(f"           {r.url}")
            print(f"           {r.path}")


def cmd_clean(cfg, args):
    token = access_token(cfg["credentials"])
    rows = read_register(cfg)
    rows, taken = sweep(token, rows, dry_run=args.dry_run)

    # Reconcile — a register nobody checks against Drive invites trust it hasn't earned.
    kept, vanished = [], []
    for r in rows:
        if r.doc_id and not drive_get(token, r.doc_id):
            vanished.append(r)
        else:
            kept.append(r)
    for r in vanished:
        print(f"gshare: {'would drop' if args.dry_run else 'dropped'} {r.name} — "
              f"its Drive file is gone or trashed")

    listed = {r.doc_id for r in kept} | {r.doc_id for r in vanished}
    orphans = [f for f in drive_list(token, cfg["drive_folder_id"]) if f["id"] not in listed]
    for f in orphans:
        print(f"gshare: unregistered in the share folder (left alone): {f['name']}")

    if not args.dry_run:
        write_register(cfg, kept)
    print(f"gshare: {len(kept)} live · {len(taken)} expired · {len(vanished)} vanished · "
          f"{len(orphans)} unregistered{' (dry run — nothing written)' if args.dry_run else ''}")


def cmd_rm(cfg, args):
    token = access_token(cfg["credentials"])
    rows, _ = sweep(token, read_register(cfg))
    row = find_row(rows, args.target)
    if not row:
        die(f"no share matches {args.target!r} — `gshare list` shows what is published")
    if row.doc_id:
        drive_takedown(token, row.doc_id)
    rows.remove(row)
    write_register(cfg, rows)
    print(f"gshare: took down {row.name} (moved to the Drive trash, recoverable for 30 days)")


def cmd_open(cfg, args):
    rows = read_register(cfg)
    row = find_row(rows, args.target)
    if not row:
        die(f"no share matches {args.target!r}")
    subprocess.run(["open", row.url], check=False)


# ------------------------------------------------------------------------ main

def main():
    p = argparse.ArgumentParser(prog="gshare", description=(__doc__ or "").split("\n")[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="verb")

    q = sub.add_parser("list", help="print the register")
    q.add_argument("--all", action="store_true", help="also show URLs and source paths")

    q = sub.add_parser("clean", help="sweep expired shares and reconcile against Drive")
    q.add_argument("--dry-run", action="store_true")

    q = sub.add_parser("rm", help="take one share down now")
    q.add_argument("target")

    q = sub.add_parser("open", help="open a published doc in a browser")
    q.add_argument("target")

    q = sub.add_parser("publish", help="publish a markdown file (the default verb)")
    q.add_argument("target")
    q.add_argument("--days", type=int, help="days until it expires")
    q.add_argument("--forever", "--permanent", dest="forever", action="store_true")
    q.add_argument("--title", help="override the document title")
    q.add_argument("--pdf", action="store_true",
                   help="publish a PDF instead of an editable Google Doc (layout-first docs)")

    # `gshare <path>` with no verb means publish.
    argv = sys.argv[1:]
    if argv and argv[0] not in {"list", "clean", "rm", "open", "publish", "-h", "--help"}:
        argv = ["publish"] + argv
    args = p.parse_args(argv)
    if not args.verb:
        p.print_help()
        return

    cfg = config()
    {"publish": cmd_publish, "list": cmd_list, "clean": cmd_clean,
     "rm": cmd_rm, "open": cmd_open}[args.verb](cfg, args)


if __name__ == "__main__":
    main()
