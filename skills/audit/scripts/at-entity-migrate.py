#!/usr/bin/env python3
"""at-entity-migrate.py — rewrite an old-form @ person page into the settled opening
(breadcrumb → identity H1 → card), per DAS At Entity § The opening.

    at-entity-migrate.py --dry  <page.md> [...]    # report what would be written
    at-entity-migrate.py --write <page.md> [...]   # rewrite in place
    at-entity-migrate.py --dry --all               # every flat person page under AT/

What it parses from the old head (everything above the first `# ` heading):
  [[REGISTER]] / =[[REGISTER]]   → Rolodex (uppercase-only link names)
  [title](url)                   → the H1's title link (first markdown link)
  [[@Org]]                       → the H1's org (first @-link); later @-links → Personas
  #pp                            → dropped;  #Mentor → [[MENTORS]];  #Soon → [[LEGACY-SOON]]
  emails / phones / bare URLs    → Contact (phones are REPORTED, not written — they live in Contacts)
  `- Friends: [[@A]], [[@B]]`     → Friends
  other loose lines / bullets    → Context, verbatim, one line each
A page whose head has no [title](url) AND no [[@Org]] is reported UNPARSED and left alone.
Pages already carrying `| Card |` are skipped. Everything from the first `# ` heading on is kept verbatim
(an old `# Name` H1 is replaced by the identity H1; `# LOG` / `# Log` / `# INFO` are kept).
"""
import re, sys
from pathlib import Path
V = Path.home() / "ob/kmr"
AT = V / "AT"
REG = re.compile(r"=?\[\[([A-Z][A-Z0-9\-]{2,})\]\]")
MDLINK = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
ATLINK = re.compile(r"\[\[(@[^\]|]+)(?:\|[^\]]*)?\]\]")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"\(?\d{3}\)?[ -.]?\d{3}[ -.]\d{4}")
URL = re.compile(r"(?<![(\[])https?://\S+")
TAGS = {"#pp": None, "#Mentor": "[[MENTORS]]", "#Soon": "[[LEGACY-SOON]]"}

def is_person(p):
    """A flat @ page that is a PERSON: not a namesake of its own folder, and — under
    `Corp/` — only when filed inside an org's `@Org/` folder (an org page sits directly
    in `Corp/` or in a plain sub-folder such as `Corp/VC ORG/`)."""
    if not (p.name.startswith("@") and p.is_file()): return False
    if p.parent.name.startswith("@") and p.parent.name == p.stem: return False
    parts = p.relative_to(AT).parts
    if parts and parts[0] == "Corp":
        return p.parent.name.startswith("@")
    return True

def crumb(p):
    rel = p.relative_to(V).parts[:-1]
    parts = ["[[kmr]]"] + [f"[[{x}]]" for x in rel]
    return ":>> " + " → ".join(parts) + f" → [{p.stem}](hook://p/{p.stem.replace(' ', '%20')}) "

def migrate(p):
    t = p.read_text(encoding="utf-8"); lines = t.split("\n")
    fm = []
    body = lines
    if lines and lines[0].strip() == "---":
        e = lines.index("---", 1); fm = lines[:e+1]; body = lines[e+1:]
    if any(l.startswith("| Card") for l in body[:40]): return None, "already migrated"
    h = next((i for i, l in enumerate(body) if l.startswith("# ")), len(body))
    head = body[:h]; rest = body[h:]
    # drop an old `# Name` H1 (keep # LOG / # Log / # INFO etc.)
    if rest and re.match(r"^# (\[\[)?@?" + re.escape(p.stem[1:]), rest[0]):
        rest = rest[1:]
    text = "\n".join(head)
    title_link = MDLINK.search(text)
    atlinks = [m.group(1) for m in ATLINK.finditer(text)]
    if not title_link and not atlinks: return None, "UNPARSED — no [title](url) and no [[@Org]] in the head"
    regs = []
    for m in REG.finditer(text):
        if m.group(1) not in regs and m.group(1) != "AT": regs.append(m.group(1))
    for tag, repl in TAGS.items():
        if tag in text and repl and repl.strip("[]") not in regs: regs.append(repl.strip("[]"))
    org = atlinks[0] if atlinks else None
    personas = [a for a in atlinks[1:] if a != org]
    emails = sorted(set(EMAIL.findall(text)))
    phones = sorted(set(PHONE.findall(text)))
    urls = [u for u in URL.findall(text) if "linkedin" not in u.lower()]
    friends = []
    ctx = []
    for l in head:
        s = l.strip()
        if not s: continue
        if MDLINK.search(s) and (ATLINK.search(s) or REG.search(s)): continue   # the identity line
        if s.lower().startswith("- friends"): friends += ATLINK.findall(s); continue
        if EMAIL.fullmatch(s) or PHONE.fullmatch(s) or URL.fullmatch(s): continue
        if s.startswith("#pp") or s.startswith("#"): continue
        ctx.append(s.lstrip("- ").strip())
    title = title_link.group(1) if title_link else "{{title}}"
    lurl = title_link.group(2) if title_link else None
    h1 = f"# {p.stem} — **" + (f"[{title}]({lurl})" if lurl else title) + (f" at [[{org}]]" if org else "") + "**"
    contact = " · ".join([f"`{e}`" for e in emails] + ([f"[LinkedIn]({lurl})"] if lurl and "linkedin" in lurl.lower() else []) + urls) or "—"
    rows = [("Contact", contact)]
    if personas: rows.append(("Personas", " · ".join(f"[[{a}]]" for a in personas)))
    rows.append(("Rolodex", " · ".join(f"[[{r}]]" for r in regs) or "—"))
    if friends: rows.append(("Friends", " · ".join(f"[[{a}]]" for a in friends)))
    if ctx: rows.append(("Context", " · ".join(ctx)))
    card = ["| Card |  |", "| --- | --- |"] + [f"| **{k}** | {v} |" for k, v in rows]
    desc = title + (f" at {org[1:]}" if org else "")
    if not any(l.startswith("description:") for l in fm):
        fm = ["---", f'description: "{p.stem[1:]} — {desc}"', "---"]
    out = fm + ["", crumb(p), h1, ""] + card + [""] + rest
    txt = "\n".join(out)
    while "\n\n\n" in txt: txt = txt.replace("\n\n\n", "\n\n")
    note = f"phones NOT written (belong in Contacts): {', '.join(phones)}" if phones else ""
    return txt, note

def main(argv):
    mode = "--dry" if "--dry" in argv else ("--write" if "--write" in argv else None)
    if mode is None: print(__doc__); return 2
    targets = [p for p in AT.rglob("@*.md") if is_person(p)] if "--all" in argv else [Path(a) for a in argv if a.endswith(".md")]
    done = skipped = unparsed = 0
    for p in sorted(targets):
        txt, note = migrate(p)
        if txt is None:
            if note.startswith("UNPARSED"): unparsed += 1; print(f"UNPARSED  {p.relative_to(V)}")
            else: skipped += 1
            continue
        done += 1
        if mode == "--write": p.write_text(txt, encoding="utf-8")
        flag = f"   [{note}]" if note else ""
        if mode == "--dry" and "--all" not in argv:
            print(txt.split("# LOG")[0] if "# LOG" in txt else txt[:900]); print("-----")
        print(f"{'WROTE ' if mode=='--write' else 'WOULD '} {p.relative_to(V)}{flag}")
    print(f"\n{done} migratable, {skipped} already migrated, {unparsed} unparsed")
    return 0
if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
