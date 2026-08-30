#!/usr/bin/env python3
"""at-entity-migrate.py — rewrite an old-form @ person page into the settled opening
(breadcrumb → identity H1 → card), per DAS At Entity § The opening.

    at-entity-migrate.py --dry  <page.md> [...]    # report what would be written
    at-entity-migrate.py --write <page.md> [...]   # rewrite in place
    at-entity-migrate.py --dry --all               # every flat person page under AT/
    at-entity-migrate.py --write --all --from-git  # re-run from each page's git HEAD text (redo a bad pass)

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
PHONE = re.compile(r"\(?\d{3}\)?[ \-–—.]?\d{3}[ \-–—.]\d{4}")
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

def migrate(p, text=None):
    """Lossless by construction: the identity line is DECOMPOSED into the H1 and card rows
    (every link, register and tag lands somewhere); every other head line is kept VERBATIM
    below the card; the body from the first heading on is untouched byte for byte."""
    t = text if text is not None else p.read_text(encoding="utf-8"); lines = t.split("\n")
    fm = []; body = lines
    if lines and lines[0].strip() == "---":
        e = lines.index("---", 1); fm = lines[:e+1]; body = lines[e+1:]
    if any(l.startswith("| Card") for l in body[:40]): return None, "already migrated"
    # head = lines before the first heading of ANY level. An old template H1
    # (`# [[@Name]]  [title](url) [[@Org]]`) is part of the identity, not the body.
    h = next((i for i, l in enumerate(body) if re.match(r"^#{1,6} ", l)), len(body))
    head = body[:h]; rest = body[h:]
    if rest and re.match(r"^# (\[\[)?@?" + re.escape(p.stem[1:]) + r"(\]\])?", rest[0]) and ("](" in rest[0] or "[[" in rest[0]):
        head = head + [rest[0]]; rest = rest[1:]
    elif rest and re.match(r"^# (\[\[)?@?" + re.escape(p.stem[1:]) + r"(\]\])?\s*$", rest[0]):
        rest = rest[1:]                       # a bare old `# Name` H1 is replaced by the identity H1
    text = "\n".join(head)
    if any(l.startswith(":>>") or l.startswith("| ") for l in head):
        return None, "UNPARSED — the page already carries a spine or a table in its head; migrate by hand"
    if "[[_Org]]" in text: return None, "UNPARSED — marked as an org (`[[_Org]]`), not a person"
    mdlinks = MDLINK.findall(text)
    atlinks = []
    for m in ATLINK.finditer(text):
        if m.group(1) not in atlinks: atlinks.append(m.group(1))
    if not mdlinks and not atlinks: return None, "UNPARSED — no [title](url) and no [[@Org]] in the head"
    li = [(a, u) for a, u in mdlinks if "linkedin" in u.lower()]
    if not li and not atlinks: return None, "UNPARSED — the only link is not LinkedIn and there is no [[@Org]]; probably not a person page"
    title, lurl = (li[0] if li else (mdlinks[0] if mdlinks else (None, None)))
    junk = None
    if lurl and "/mynetwork/" in lurl: junk = lurl; lurl = None
    other_md = [(a, u) for a, u in mdlinks if u != (li[0][1] if li else (mdlinks[0][1] if mdlinks else None))]
    org = atlinks[0] if atlinks else None
    personas = [a for a in atlinks[1:]]
    regs = []
    for m in re.finditer(r"=?\[\[([^\]|@][^\]|]*)(?:\|[^\]]*)?\]\]", text):
        name = m.group(1)
        if name not in regs: regs.append(name)
    for tag in set(re.findall(r"(?<!\S)#(\w+)", text)):
        if tag == "pp": continue
        r = {"Mentor": "MENTORS", "Soon": "LEGACY-SOON"}.get(tag, f"LEGACY-{tag.upper()}")
        if r not in regs: regs.append(r)
    emails = []
    for m in EMAIL.finditer(text):
        if m.group(0) not in emails: emails.append(m.group(0))
    friends = []; kept = []
    def is_identity(s):
        return bool(MDLINK.search(s) and (ATLINK.search(s) or re.search(r"\[\[[^\]]+\]\]", s) or re.search(r"(?<!\S)#\w+", s))) or (ATLINK.search(s) and not re.search(r"[a-z]{4,} [a-z]{3,}", re.sub(r"\[\[[^\]]*\]\]|\[[^\]]*\]\([^)]*\)", "", s)))
    for l in head:
        s = l.strip()
        if not s: continue
        if is_identity(s): continue
        if s.lower().startswith("- friends"):
            friends += [a for a in ATLINK.findall(s)]; continue
        if EMAIL.fullmatch(s): continue          # represented in Contact
        if re.fullmatch(r"#\w+(\s+#\w+)*", s): continue   # tags — represented in Rolodex
        kept.append(l)                            # everything else: verbatim, below the card
    ident = (f"[{title}]({lurl})" if (title and lurl) else (title or "")) + ((" at " if title else "") + f"[[{org}]]" if org else "")
    h1 = f"# {p.stem} — **{ident}**"
    contact = " · ".join([f"`{e}`" for e in emails] + ([f"[LinkedIn]({lurl})"] if lurl and "linkedin" in lurl.lower() else [])) or "—"
    rows = [("Contact", contact)]
    pers = [f"[[{a}]]" for a in personas] + [f"[{a}]({u})" for a, u in other_md]
    if pers: rows.append(("Personas", " · ".join(pers)))
    rows.append(("Rolodex", " · ".join(f"[[{r}]]" for r in regs) or "—"))
    if friends: rows.append(("Friends", " · ".join(f"[[{a}]]" for a in friends)))
    card = ["| Card |  |", "| --- | --- |"] + [f"| **{k}** | {v} |" for k, v in rows]
    desc = (title or "") + (f" at {org[1:]}" if org else "")
    if not any(l.startswith("description:") for l in fm):
        fm = ["---", f'description: "{p.stem[1:]} — {desc}"', "---"]
    if junk: kept.append(f"*(old LinkedIn link, not a profile: {junk})*")
    out = fm + ["", crumb(p), h1, ""] + card + [""] + (kept + [""] if kept else []) + rest
    phones = PHONE.findall(text)
    note = f"phone in head, kept verbatim below the card: {', '.join(phones)}" if phones else ""
    return "\n".join(out), note


def main(argv):
    mode = "--dry" if "--dry" in argv else ("--write" if "--write" in argv else None)
    if mode is None: print(__doc__); return 2
    targets = [p for p in AT.rglob("@*.md") if is_person(p)] if "--all" in argv else [Path(a) for a in argv if a.endswith(".md")]
    done = skipped = unparsed = 0
    import subprocess
    for p in sorted(targets):
        base = None
        if "--from-git" in argv:
            r = subprocess.run(["git", "-C", str(V), "show", f"HEAD:{p.relative_to(V)}"], capture_output=True, text=True)
            if r.returncode != 0: print(f"NO-BASE   {p.relative_to(V)}"); continue
            base = r.stdout
        txt, note = migrate(p, base)
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
