#!/usr/bin/env python3
"""vet_url — validate URLs before they reach Dan (F294, layers 0-4).

An agent cannot tell an ID it *read* from an ID it *generated*; that information
does not exist at generation time. On 2026-08-01 ten Apple Podcasts links were
shipped in a survey with invented digits in an otherwise perfect URL shape, and
every one looked legitimate. Only a fetch settles it, so this is a tool rather
than a rule.

Layers 0-2 are on by default; 3 and 4 are opt-in:

  0  extraction   — markdown links, autolinks, bare URLs, reference style
  1  reachability — nine verdicts, because "could not determine" must be
                    distinguishable from "dead"
  2  label match  — link text vs the page's own title; the check that catches an
                    invented ID which happens to land on a REAL page
  3  --expect     — assert the page actually says what is about to be claimed
                    about it
  4  --deep       — registry probes (Apple / DOI / arXiv / PubMed), fragment
                    checks, and a Wayback fallback on anything dead

Layer 4 is the strongest check and the reason `--deep` exists. Layer 1 caught the
ten fabrications by luck — all ten happened not to resolve. An invented ID
landing on a different real podcast returns 200 and passes reachability cleanly,
producing a citation that is confidently and silently wrong. `itunes.apple.com/
lookup?id=<N>` answers that directly: `resultCount: 0` for an invented ID, and
the canonical name for a real one, which is a far stronger label check than a
page title.

Every probe is plain tier-1 HTTP. No browser is ever launched — see the feature
doc's escalation etiquette: `BLOCKED` is an acceptable terminal answer, which is
what removes any pressure to reach for Dan's screen.

    vet_url <url>...
    vet_url --doc <file.md> --deep
    vet_url --expect "Get it on Google Play" <url>
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
from typing import Optional
from urllib.parse import quote, unquote, urlsplit

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

REPORTABLE = ("DEAD", "GONE", "SOFT-404", "REDIR-HOME", "REDIR-OFFSITE", "MISMATCH",
              "EXPECT-FAIL", "NO-ANCHOR")
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
    # Kept so layers 3-4 can interrogate the page without a second request. Never
    # serialized — `--json` emits verdicts, not page dumps.
    body: str = ""
    fragment_ok: Optional[bool] = None
    evidence: str = ""
    registry_name: str = ""

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


# Hosts whose entire job is to hand you off somewhere else. Reporting a DOI for
# crossing domains would flag every correctly-working DOI in the vault — the
# textbook false alarm this tool cannot afford.
REDIRECTORS = ("doi.org", "dx.doi.org", "hdl.handle.net", "n2t.net",
               "purl.org", "w3id.org")


def _classify_redirect(orig: str, final: str) -> tuple:
    """A redirect is only interesting when it loses the target.

    A deep path landing on the site root almost always means the thing was
    removed and the server papered over it; crossing domains means rot or a sold
    domain. Everything else (http→https, trailing slash, www, and any resolver
    doing exactly what it exists to do) is noise."""
    o, f = urlsplit(orig), urlsplit(final)
    ohost = o.netloc.lower().removeprefix("www.")
    fhost = f.netloc.lower().removeprefix("www.")
    if ohost != fhost:
        if ohost in REDIRECTORS:
            return "", ""
        return "REDIR-OFFSITE", f"{ohost} → {fhost}"
    opath = o.path.rstrip("/")
    fpath = f.path.rstrip("/")
    if opath and len(opath) > 1 and not fpath:
        return "REDIR-HOME", f"{opath} → site root"
    return "", ""


_ID_ATTR = re.compile(r"""\s(?:id|name)=["']([^"']+)["']""")


def _fragment_state(url: str, body: str):
    """Whether a `#fragment` deep-link actually lands somewhere, or None when the
    question cannot be asked honestly.

    None is returned for a page that renders *no* ids at all — an SPA shell builds
    its anchors client-side, so absence there is evidence of how the page is
    rendered, not of a broken link. Reporting those would be exactly the false
    alarm that gets the tool ignored."""
    frag = urlsplit(url).fragment
    if not frag or frag.startswith(":~:"):  # `#:~:text=` is a text fragment, not an anchor
        return None
    ids = set(_ID_ATTR.findall(body))
    if not ids:
        return None
    return unquote(frag) in ids or frag in ids


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
    frag = _fragment_state(link.url, body)
    if _SOFT404.search(title) or _SOFT404.search(_strip_html(body[:4000])):
        return Verdict(link, "SOFT-404", f"HTTP 200 but the page says not-found "
                                         f"— title {title!r}", code, title, final,
                       body, frag)
    st, why = _classify_redirect(link.url, final)
    if st:
        return Verdict(link, st, why, code, title, final, body, frag)
    return Verdict(link, "OK", "", code, title, final, body, frag)


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


# ---- layer 3: --expect --------------------------------------------------------
#
# The URL that started this was perfectly alive. What was invented was the *claim
# about it* — "there is a Get it on Google Play badge near the top" — relayed from
# a summarizer that described an element which was not visibly there. So the
# answer here is deliberately three-valued rather than yes/no: text, markup, or
# absent. A string that appears only in an `alt=` or a `content=` attribute IS on
# the page and is NOT necessarily on the screen, and that distinction is exactly
# the one that cost Dan three round-trips.

def expectation(body: str, expect: str):
    """Where `expect` appears on the page: 'text', 'markup', or None."""
    want = re.sub(r"\s+", " ", expect).strip().lower()
    if not want:
        return None
    if want in re.sub(r"\s+", " ", _strip_html(body)).lower():
        return "text"
    if want in re.sub(r"\s+", " ", html.unescape(body)).lower():
        return "markup"
    return None


# ---- layer 4: --deep, registry probes -----------------------------------------
#
# A URL carrying a machine-checkable ID can be settled against the registry that
# issues those IDs, which is both more authoritative than fetching the page and a
# silent way around a bot wall. The Apple probe is the one that matters: it would
# have caught all ten fabrications instantly, including the dangerous variant
# where an invented ID lands on a real but different show.

_APPLE = re.compile(r"^https?://(podcasts|apps|music|itunes)\.apple\.com/.*?/id(\d+)", re.I)
_DOI = re.compile(r"^https?://(?:dx\.)?doi\.org/(10\.\d{4,9}/\S+)", re.I)
_ARXIV = re.compile(r"^https?://arxiv\.org/(?:abs|pdf)/([0-9]{4}\.[0-9]{4,5}|[a-z-]+(?:\.[A-Z]{2})?/[0-9]{7})", re.I)
_PUBMED = re.compile(r"^https?://pubmed\.ncbi\.nlm\.nih\.gov/(\d{5,9})", re.I)


@dataclass
class Probe:
    registry: str
    # True = the registry has this ID, False = it does not, None = could not ask.
    # None is a first-class answer for the same reason BLOCKED is.
    found: Optional[bool]
    name: str = ""
    detail: str = ""


def _get(url: str, timeout=TIMEOUT) -> str:
    """Body of a registry call, including on an error status.

    A 404 body is not noise here — the DOI Handle API answers "no such handle"
    with `responseCode: 100` *and* HTTP 404, so discarding error bodies throws
    away the very answer being asked for."""
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept": "application/json,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read(300_000).decode(
                r.headers.get_content_charset() or "utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        try:
            return e.read(300_000).decode("utf-8", errors="replace")
        except Exception:
            return ""
    except Exception:
        return ""


def _get_json(url: str, timeout=TIMEOUT):
    raw = _get(url, timeout)
    try:
        return json.loads(raw) if raw else None
    except json.JSONDecodeError:
        return None


# A single numeric namespace serves podcasts, apps and songs, so "the ID exists"
# is NOT the question — "the ID is the kind of thing this URL claims" is. Found
# the hard way: the fabricated podcast id1509001470 resolves with resultCount 1,
# to a Russian children's choir recording. An existence-only probe would have
# cleared that URL.
_APPLE_KIND = {
    "podcasts": ("podcast",),
    "apps": ("software", "mac-software", "software-bundle", "ios-software"),
}


def _probe_apple(host: str, pid: str) -> Probe:
    """`resultCount: 0` is a definitive 'no such ID'; a hit is only useful once
    its product type is checked against what the URL claims. A match also hands
    back the canonical name, which beats a page title as a label check."""
    api = f"https://itunes.apple.com/lookup?id={pid}"
    data = _get_json(api)
    if data is None or "resultCount" not in data:
        return Probe("apple", None, detail=f"{api} unreachable")
    if not data["resultCount"]:
        return Probe("apple", False,
                     detail=f"itunes lookup id={pid} → resultCount 0 — no such Apple ID")
    r = (data.get("results") or [{}])[0]
    name = r.get("collectionName") or r.get("trackName") or ""
    actual = (r.get("kind") or r.get("wrapperType") or "?").lower()
    want = _APPLE_KIND.get(host.lower())
    if want and actual not in want:
        return Probe("apple", False,
                     detail=f"itunes lookup id={pid} → a {actual} ({name!r}), "
                            f"not a {host.rstrip('s')} — the ID exists but is not "
                            "what this URL claims")
    return Probe("apple", True, name, f"itunes lookup id={pid} → {actual} {name!r}")


def _probe_doi(doi: str) -> Probe:
    """The Handle API, not Crossref: it is authoritative for *every* DOI, where
    Crossref only knows the ones it registered. The trade is that it answers
    existence without a title."""
    api = f"https://doi.org/api/handles/{quote(doi, safe='/')}"
    data = _get_json(api)
    if data is None or "responseCode" not in data:
        return Probe("doi", None, detail=f"{api} unreachable")
    rc = data["responseCode"]
    if rc == 1:
        return Probe("doi", True, detail=f"handle API → registered ({doi})")
    if rc in (100, 200):  # 100 handle not found, 200 values not found
        return Probe("doi", False, detail=f"handle API → no such DOI ({doi})")
    return Probe("doi", None, detail=f"handle API → responseCode {rc}")


def _probe_arxiv(aid: str) -> Probe:
    body = _get(f"http://export.arxiv.org/api/query?id_list={quote(aid)}")
    if not body:
        return Probe("arxiv", None, detail="arxiv API unreachable")
    titles = [_strip_html(t) for t in re.findall(r"<title>(.*?)</title>", body, re.S)]
    entry = titles[1] if len(titles) > 1 else ""
    if not entry or entry.lower() == "error":
        return Probe("arxiv", False, detail=f"arxiv API → no such ID ({aid})")
    return Probe("arxiv", True, entry, f"arxiv API {aid} → {entry!r}")


def _probe_pubmed(pmid: str) -> Probe:
    data = _get_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                     f"?db=pubmed&id={pmid}&retmode=json")
    rec = ((data or {}).get("result") or {}).get(pmid)
    if rec is None:
        return Probe("pubmed", None, detail="eutils unreachable")
    if rec.get("error"):
        return Probe("pubmed", False, detail=f"eutils → no such PMID ({pmid})")
    title = rec.get("title", "")
    return Probe("pubmed", True, title, f"eutils {pmid} → {title!r}")


def registry_probe(url: str):
    """The probe for this URL's registry, or None if it carries no known ID."""
    for rx, fn in ((_APPLE, _probe_apple), (_DOI, _probe_doi),
                   (_ARXIV, _probe_arxiv), (_PUBMED, _probe_pubmed)):
        m = rx.match(url)
        if m:
            return fn(*m.groups())
    return None


def wayback(url: str) -> str:
    """Last snapshot date for a dead URL, so a citation can be repointed rather
    than silently dropped."""
    data = _get_json("https://archive.org/wayback/available?url=" + quote(url, safe=""))
    snap = ((data or {}).get("archived_snapshots") or {}).get("closest") or {}
    ts = snap.get("timestamp", "")
    if not snap.get("available") or len(ts) < 8:
        return ""
    return f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}"


def deepen(v: Verdict) -> Verdict:
    """Apply layer 4 to one already-fetched verdict.

    A probe outranks the page fetch in both directions: it can condemn a URL the
    page served happily, and it can clear one the page refused to serve at all."""
    p = registry_probe(v.link.url)
    if p is not None:
        v.evidence = p.detail
        if p.found is False:
            v.status, v.detail = "DEAD", p.detail
        elif p.found is True:
            if p.name:
                v.title = v.title or p.name
                v.registry_name = p.name
            if v.status in ("BLOCKED", "SERVER-ERR", "TIMEOUT"):
                # The API sidestep doing its job: an answer without a browser.
                v.status = "OK"
                v.detail = f"resolved via registry despite HTTP {v.http or '—'} — {p.detail}"
    if v.status in ("DEAD", "GONE"):
        when = wayback(v.link.url)
        if when:
            v.detail = f"{v.detail}; last archived {when} (repointable via web.archive.org)"
    return v


def vet(links, workers=WORKERS, check_labels=True, deep=False, expect=None) -> list:
    out = []
    n = min(workers, max(len(links), 1))
    with cf.ThreadPoolExecutor(max_workers=n) as ex:
        out = list(ex.map(fetch, links))
        if deep:
            out = list(ex.map(deepen, out))

    for v in out:
        # A registry's canonical name is a far stronger label check than a page
        # title, so it wins when layer 4 supplied one.
        against = v.registry_name or v.title
        if (check_labels and v.status == "OK" and v.link.text
                and against and not label_matches(v.link.text, against)):
            v.status = "MISMATCH"
            v.detail = f"link says {v.link.text!r}, target says {against!r}"
        if deep and v.status == "OK" and v.fragment_ok is False:
            v.status = "NO-ANCHOR"
            v.detail = (f"page is fine but #{urlsplit(v.link.url).fragment} "
                        "is not an anchor in it")
        # Last, so it annotates a stronger finding rather than masking it. Skipped
        # when there is no body — a page that did not load cannot be asserted about.
        if expect and v.body:
            where = expectation(v.body, expect)
            if where is None:
                note = f"page does not contain {expect!r}"
                v.status, v.detail = (("EXPECT-FAIL", note) if v.status == "OK"
                                      else (v.status, f"{v.detail}; {note}"))
            elif where == "markup":
                note = (f"{expect!r} appears only in markup (an alt/meta attribute) "
                        "— it is on the page but not necessarily on the screen")
                v.status, v.detail = (("EXPECT-MARKUP", note) if v.status == "OK"
                                      else (v.status, f"{v.detail}; {note}"))
        v.body = ""
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
        lines.append("  — undetermined and caveats (NOT a finding) —")
        for v in unknown:
            lines.append(f"  [{v.status}] {v.link.url}  {v.detail}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="vet_url", description=(__doc__ or "").split("\n")[0])
    ap.add_argument("urls", nargs="*")
    ap.add_argument("--doc", help="extract and vet every URL in this file")
    ap.add_argument("--extract-only", action="store_true",
                    help="layer 0 only — print what would be fetched")
    ap.add_argument("--no-labels", action="store_true", help="skip layer 2")
    ap.add_argument("--expect", metavar="TEXT",
                    help="layer 3 — assert the page actually says TEXT")
    ap.add_argument("--deep", action="store_true",
                    help="layer 4 — registry probes, fragment checks, Wayback "
                         "fallback. Tier-1 HTTP only; never launches a browser")
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

    verdicts = vet(links, workers=a.workers, check_labels=not a.no_labels,
                   deep=a.deep, expect=a.expect)
    if a.json:
        print(json.dumps([{"url": v.link.url, "text": v.link.text,
                           "lines": v.link.lines, "status": v.status,
                           "http": v.http, "detail": v.detail, "title": v.title,
                           "registry": v.evidence, "registry_name": v.registry_name,
                           "reportable": v.reportable} for v in verdicts], indent=1))
    else:
        print(report(verdicts, a.doc))
    return 1 if any(v.reportable for v in verdicts) else 0


if __name__ == "__main__":
    raise SystemExit(main())
