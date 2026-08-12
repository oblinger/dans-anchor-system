#!/usr/bin/env python3
"""gshare — publish a markdown file to a link-shared Google Doc, with a register and an expiry.

    gshare <path> [--days N | --forever] [--title T]   publish, or refresh an existing share
    gshare list [--all]                                print the register
    gshare clean [--dry-run]                           sweep expired rows, reconcile against Drive
    gshare rm <path | url | id>                        take one share down now
    gshare open <path | url>                           open the published doc in a browser

Every invocation sweeps expired rows before doing anything else — the expiry has to
fire when nobody is asking, so it cannot depend on an agent noticing.

The register (two markdown tables in one vault page) is the ONLY store: the Drive file
id is recovered from the URL in the Weblink cell, so there is no sidecar and no cache.

Config: ~/.config/anchor-system/gshare/config.yaml (per F080).
  drive_folder_id: <Drive folder that receives shares>   (required)
  credentials:     <OAuth client json with a drive scope> (required)
  register:        <path to the register page>            (default: {skill_data_root}/gshare/gshare register.md)
  default_days:    30

Per F325.
"""

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
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


def multipart(metadata, html):
    boundary = uuid.uuid4().hex
    body = (
        f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n"
        f"{json.dumps(metadata)}\r\n"
        f"--{boundary}\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n"
        f"{html}\r\n--{boundary}--\r\n"
    ).encode()
    return body, f"multipart/related; boundary={boundary}"


def drive_create(token, name, folder, html):
    body, ctype = multipart(
        {"name": name, "mimeType": "application/vnd.google-apps.document", "parents": [folder]}, html)
    return api(token, "POST",
               f"{UPLOAD}/files?uploadType=multipart&fields=id,name,webViewLink",
               content_type=ctype, raw=body)


def drive_update(token, file_id, name, html):
    body, ctype = multipart({"name": name}, html)
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


# ------------------------------------------------------------ markdown → HTML

WIKI_PIPED = re.compile(r"\[\[([^\[\]|]+)\|([^\[\]]+)\]\]")
WIKI_PLAIN = re.compile(r"\[\[([^\[\]|]+)\]\]")
BLOCK_ID = re.compile(r"\s+\^[A-Za-z0-9][A-Za-z0-9-]*\s*$")


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


def prepare(text):
    text = strip_frontmatter(text)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    lines = []
    for line in text.splitlines():
        if line.lstrip().startswith(":>>"):
            continue
        lines.append(BLOCK_ID.sub("", line))
    return flatten_wikilinks("\n".join(lines)).strip() + "\n"


def to_html(text):
    try:
        import markdown
    except ImportError:
        die("the `markdown` package is not installed — `pip install markdown`")
    return markdown.markdown(prepare(text), extensions=["tables", "extra", "sane_lists"])


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
    html = to_html(text)
    expires = None if args.forever else (TODAY + dt.timedelta(days=args.days or cfg["default_days"])).isoformat()

    existing = find_row(rows, str(src))
    if existing and existing.doc_id and drive_get(token, existing.doc_id):
        f = drive_update(token, existing.doc_id, name, html)
        existing.name, existing.expires = f["name"], expires
        row, verb = existing, "refreshed"
    else:
        if existing:
            rows.remove(existing)
        f = drive_create(token, name, cfg["drive_folder_id"], html)
        drive_share(token, f["id"])
        row = Row(TODAY.isoformat(), expires, f["webViewLink"], f["name"], src.resolve())
        rows.append(row)
        verb = "published"

    write_register(cfg, rows)
    print(f"gshare: {verb} {row.name}")
    print(f"  {row.url}")
    print(f"  {'never expires' if not row.expires else 'expires ' + row.expires}"
          f" · register: {cfg['register']}")
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
