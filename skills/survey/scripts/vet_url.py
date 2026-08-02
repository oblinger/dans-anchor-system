#!/usr/bin/env python3
"""vet_url — validate URLs before they reach Dan (F294, layers 0-2).

An agent cannot tell an ID it *read* from an ID it *generated*; that information
does not exist at generation time. On 2026-08-01 ten Apple Podcasts links were
shipped in a survey with invented digits in an otherwise perfect URL shape, and
every one looked legitimate. Only a fetch settles it, so this is a tool rather
than a rule.

Three layers, all on by default:

  0  extraction   — markdown links, autolinks, bare URLs, reference style
  1  reachability — nine verdicts, because "could not determine" must be
                    distinguishable from "dead"
  2  label match  — link text vs the page's own title; the check that catches an
                    invented ID which happens to land on a REAL page

Layer 2 is the important one. Layer 1 caught the ten fabrications by luck — all
ten happened not to resolve. An invented ID landing on a different real podcast
returns 200 and passes reachability cleanly, producing a citation that is
confidently and silently wrong.

    vet_url <url>...
    vet_url --doc <file.md>
    vet_url --doc <file.md> --json
"""
import argparse
import concurrent.futures as cf
import html
import json
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

TIMEOUT = 12
WORKERS = 16
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")

# ---- layer 0: extraction ------------------------------------------------------
#
# Extraction bugs produce false alarms, and a tool that cries wolf is dismissed
# inside a week — the same failure mode as an over-firing alert. The prototype
# that motivated this flagged Wikipedia's `Sleep_with_Me_(podcast)` as dead purely
# because its regex ate the closing paren.

SKIP_SCHEMES = ("file:", "hook:", "mailto:", "obsidian:", "tel:", "data:",
                "javascript:", "ftp:")
PRIVATE_HOST = re.compile(
    r"^(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|\[::1\])",
    re.I)

_INLINE = re.compile(r"\[(?P<text>[^\]]*)\]\(\s*(?P<url>[^\s()]*(?:\([^\s()]*\)[^\s()]*)*)"
                     r"(?:\s+[\"'][^\"']*[\"'])?\s*\)")
_AUTOLINK = re.compile(r"<(?P<url>[a-zA-Z][a-zA-Z0-9+.-]*://[^>\s]+)>")
# `[ \t]` not `\s` for the indent — `\s` matches the preceding newline, so the
# match starts on the blank line above and the report cites the wrong line.
_REF_DEF = re.compile(r"^[ \t]{0,3}\[(?P<ref>[^\]]+)\]:[ \t]*(?P<url>\S+)", re.M)
_REF_USE = re.compile(r"\[(?P<text>[^\]]*)\]\[(?P<ref>[^\]]*)\]")
# `)` is allowed through here and settled by `_balance_parens` — excluding it
# outright is exactly how the `Sleep_with_Me_(podcast)` regression happened.
_BARE = re.compile(r"(?<![(<\[\"'=])\bhttps?://[^\s<>\"'`\]]+")
_WIKI = re.compile(r"\[\[[^\]]*\]\]")
_FENCE = re.compile(r"^```.*?^```", re.M | re.S)


@dataclass
class Link:
    url: str
    text: str = ""
    lines: list = field(default_factory=list)


def _balance_parens(url: str) -> str:
    """Give back a trailing `)` that belongs to the URL.

    `(https://en.wikipedia.org/wiki/Sleep_with_Me_(podcast))` — the last paren
    closes the markdown wrapper, the one before it belongs to the path. Walk from
    the right and drop only the parens that are genuinely unmatched."""
    while url.endswith(")") and url.count(")") > url.count("("):
        url = url[:-1]
    return url


def _clean(url: str) -> str:
    url = _balance_parens(url.strip())
    # Sentence punctuation clings to a bare URL. A trailing slash or a path
    # segment ending in a dot is legitimate, so only strip what cannot be path.
    while url and url[-1] in ".,;:!?'\"":
        url = url[:-1]
    return _balance_parens(url)


def _wanted(url: str) -> bool:
    low = url.lower()
    if any(low.startswith(s) for s in SKIP_SCHEMES):
        return False
    if not low.startswith(("http://", "https://")):
        return False
    return not PRIVATE_HOST.match(urlsplit(url).netloc)


def extract(text: str) -> list:
    """Every http(s) URL in `text`, deduped, each carrying its link text and the
    lines it appeared on. Wiki-links and fenced code are removed first — a URL
    inside a fence is an example, not a citation."""
    text = _FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    text = _WIKI.sub("", text)
    lines = text.split("\n")

    def line_of(pos):
        return text.count("\n", 0, pos) + 1

    found = {}

    def add(url, txt, pos):
        url = _clean(url)
        if not _wanted(url):
            return
        e = found.setdefault(url, Link(url=url, text=txt.strip()))
        if txt.strip() and not e.text:
            e.text = txt.strip()
        ln = line_of(pos)
        if ln not in e.lines:
            e.lines.append(ln)

    refs = {m.group("ref").lower(): m.group("url") for m in _REF_DEF.finditer(text)}
    for m in _INLINE.finditer(text):
        add(m.group("url"), m.group("text"), m.start())
    for m in _AUTOLINK.finditer(text):
        add(m.group("url"), "", m.start())
    for m in _REF_USE.finditer(text):
        ref = (m.group("ref") or m.group("text")).lower()
        if ref in refs:
            add(refs[ref], m.group("text"), m.start())
    for m in _REF_DEF.finditer(text):
        add(m.group("url"), "", m.start())
    for m in _BARE.finditer(text):
        add(m.group(0), "", m.start())

    for e in found.values():
        e.lines.sort()
    return sorted(found.values(), key=lambda e: (e.lines[:1] or [0], e.url))


# ---- layer 1: reachability ----------------------------------------------------
#
# BLOCKED is a SUCCESS, not a failure. Two of the 46 URLs in the corpus that
# produced this feature were live pages behind bot walls (Liebert 403, Star
# Tribune 429). Reporting "could not determine" for those is the honest answer,
# and it is what removes any pressure to escalate into Dan's browser.

REPORTABLE = ("DEAD", "GONE", "SOFT-404", "REDIR-HOME", "REDIR-OFFSITE", "MISMATCH")
_SOFT404 = re.compile(
    r"\b(page not found|not found|no longer available|doesn'?t exist|"
    r"does not exist|410 gone|404 error|removed or renamed)\b", re.I)
_TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
_H1 = re.compile(r"<h1[^>]*>(.*?)</h1>", re.I | re.S)
_OG = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)',
                 re.I)
_TAG = re.compile(r"<[^>]+>")


@dataclass
class Verdict:
    link: Link
    status: str
    detail: str = ""
    http: int = 0
    title: str = ""
    final_url: str = ""

    @property
    def reportable(self):
        return self.status in REPORTABLE


def _strip_html(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(_TAG.sub(" ", s))).strip()


def _page_title(body: str) -> str:
    for rx in (_OG, _TITLE, _H1):
        m = rx.search(body)
        if m:
            t = _strip_html(m.group(1))
            if t:
                return t
    return ""


def _classify_redirect(orig: str, final: str) -> tuple:
    """A redirect is only interesting when it loses the target.

    A deep path landing on the site root almost always means the thing was
    removed and the server papered over it; crossing domains means rot or a sold
    domain. Everything else (http→https, trailing slash, www) is noise."""
    o, f = urlsplit(orig), urlsplit(final)
    ohost = o.netloc.lower().removeprefix("www.")
    fhost = f.netloc.lower().removeprefix("www.")
    if ohost != fhost:
        return "REDIR-OFFSITE", f"{ohost} → {fhost}"
    opath = o.path.rstrip("/")
    fpath = f.path.rstrip("/")
    if opath and len(opath) > 1 and not fpath:
        return "REDIR-HOME", f"{opath} → site root"
    return "", ""


def fetch(link: Link, timeout=TIMEOUT) -> Verdict:
    req = urllib.request.Request(link.url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read(200_000).decode(r.headers.get_content_charset() or "utf-8",
                                          errors="replace")
            final, code = r.geturl(), r.status
    except urllib.error.HTTPError as e:
        code = e.code
        if code in (401, 403, 429, 999):
            return Verdict(link, "BLOCKED", f"HTTP {code} — bot wall, says nothing "
                                            "about whether the page exists", code)
        if code == 410:
            return Verdict(link, "GONE", "HTTP 410", code)
        if code >= 500:
            return Verdict(link, "SERVER-ERR", f"HTTP {code}", code)
        return Verdict(link, "DEAD", f"HTTP {code}", code)
    except urllib.error.URLError as e:
        reason = str(getattr(e, "reason", e))
        low = reason.lower()
        if "timed out" in low or "timeout" in low:
            return Verdict(link, "TIMEOUT", reason)
        if "name or service" in low or "nodename" in low or "getaddrinfo" in low:
            return Verdict(link, "DNS-FAIL", reason)
        if "certificate" in low or "ssl" in low:
            return Verdict(link, "TLS-FAIL", reason)
        return Verdict(link, "TIMEOUT", reason)
    except (TimeoutError, OSError) as e:
        return Verdict(link, "TIMEOUT", str(e))
    except UnicodeDecodeError as e:
        return Verdict(link, "OK", f"non-text body ({e.reason})", 200)

    title = _page_title(body)
    if _SOFT404.search(title) or _SOFT404.search(_strip_html(body[:4000])):
        return Verdict(link, "SOFT-404", f"HTTP 200 but the page says not-found "
                                         f"— title {title!r}", code, title, final)
    st, why = _classify_redirect(link.url, final)
    if st:
        return Verdict(link, st, why, code, title, final)
    return Verdict(link, "OK", "", code, title, final)


# ---- layer 2: label / target match --------------------------------------------

_STOP = {"the", "a", "an", "and", "or", "of", "for", "with", "to", "in", "on",
         "at", "by", "from", "podcast", "podcasts", "show", "official", "site",
         "home", "page", "app", "apps", "com", "org", "net", "www", "apple",
         "google", "play", "store", "listen", "episode", "episodes", "free"}


def _tokens(s: str) -> set:
    return {w for w in re.findall(r"[a-z0-9]+", s.lower())
            if len(w) > 2 and w not in _STOP}


def label_matches(text: str, title: str) -> bool:
    """Does the link text share any meaningful token with the page's own title?

    Deliberately generous. A show's page title routinely differs from its common
    name, so this is tuned to catch "this link goes somewhere else entirely",
    not to police wording."""
    lt, tt = _tokens(text), _tokens(title)
    if not lt or not tt:
        return True
    return bool(lt & tt)


def vet(links, workers=WORKERS, check_labels=True) -> list:
    out = []
    with cf.ThreadPoolExecutor(max_workers=min(workers, max(len(links), 1))) as ex:
        for v in ex.map(fetch, links):
            if (check_labels and v.status == "OK" and v.link.text
                    and v.title and not label_matches(v.link.text, v.title)):
                v.status = "MISMATCH"
                v.detail = f"link says {v.link.text!r}, page says {v.title!r}"
            out.append(v)
    return sorted(out, key=lambda v: (v.link.lines[:1] or [0], v.link.url))


# ---- reporting ----------------------------------------------------------------

def report(verdicts, doc=None) -> str:
    bad = [v for v in verdicts if v.reportable]
    unknown = [v for v in verdicts if not v.reportable and v.status != "OK"]
    lines = []
    where = f" in {doc}" if doc else ""
    lines.append(f"vet_url: {len(verdicts)} URL(s){where} — "
                 f"{len(bad)} reportable, {len(unknown)} undetermined")
    for v in bad:
        loc = f":{v.link.lines[0]}" if v.link.lines else ""
        lines.append(f"  [{v.status}]{loc} {v.link.url}")
        if v.detail:
            lines.append(f"      {v.detail}")
    if unknown:
        lines.append("  — undetermined (NOT a finding; the page may well be fine) —")
        for v in unknown:
            lines.append(f"  [{v.status}] {v.link.url}  {v.detail}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="vet_url", description=__doc__.split("\n")[0])
    ap.add_argument("urls", nargs="*")
    ap.add_argument("--doc", help="extract and vet every URL in this file")
    ap.add_argument("--extract-only", action="store_true",
                    help="layer 0 only — print what would be fetched")
    ap.add_argument("--no-labels", action="store_true", help="skip layer 2")
    ap.add_argument("--workers", type=int, default=WORKERS)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    if a.doc:
        p = Path(a.doc)
        if not p.is_file():
            print(f"vet_url: no such file: {a.doc}", file=sys.stderr)
            return 2
        links = extract(p.read_text(encoding="utf-8", errors="replace"))
    elif a.urls:
        links = [Link(url=_clean(u)) for u in a.urls if _wanted(_clean(u))]
    else:
        links = extract(sys.stdin.read())

    if a.extract_only:
        if a.json:
            print(json.dumps([{"url": l.url, "text": l.text, "lines": l.lines}
                              for l in links], indent=1))
        else:
            for l in links:
                print(f"{','.join(map(str, l.lines)) or '-'}\t{l.url}\t{l.text}")
        return 0

    if not links:
        if not a.json:
            print("vet_url: no URLs found")
        else:
            print("[]")
        return 0

    verdicts = vet(links, workers=a.workers, check_labels=not a.no_labels)
    if a.json:
        print(json.dumps([{"url": v.link.url, "text": v.link.text,
                           "lines": v.link.lines, "status": v.status,
                           "http": v.http, "detail": v.detail, "title": v.title,
                           "reportable": v.reportable} for v in verdicts], indent=1))
    else:
        print(report(verdicts, a.doc))
    return 1 if any(v.reportable for v in verdicts) else 0


if __name__ == "__main__":
    raise SystemExit(main())
