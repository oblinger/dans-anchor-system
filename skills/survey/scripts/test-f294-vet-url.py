#!/usr/bin/env python3
"""F294 layers 0-2 — extraction, verdict classes, label matching.

Offline by construction. Layer 1 is exercised against a stubbed opener rather
than the live web, because a test that needs the network tells you about the
network. The one thing that MUST be checked against reality — that the ten
fabricated Apple Podcasts IDs come back DEAD while real ones come back alive —
is a corpus run, not a unit test, and lives in the feature doc's criteria.

The bias throughout: a false alarm is worse than a miss. A tool that cries wolf
is dismissed inside a week, so `BLOCKED` must never read as a finding and the
paren regression must never come back.

    python3 test-f294-vet-url.py
"""
import importlib.util
import io
import sys
import urllib.error
from pathlib import Path

HERE = Path(__file__).parent
_spec = importlib.util.spec_from_file_location("vu", HERE / "vet_url.py")
vu = importlib.util.module_from_spec(_spec)
sys.modules["vu"] = vu
_spec.loader.exec_module(vu)

results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"\n          got  {got!r}\n          want {want!r}"))


print("Layer 0 — extraction, where a false alarm is born")


def urls(text):
    return [l.url for l in vu.extract(text)]


def test_the_paren_regression():
    """The bug that motivated layer 0 having its own tests: a prototype reported
    Wikipedia's `Sleep_with_Me_(podcast)` as dead because the regex ate the
    closing paren, producing a 404 on a page that is perfectly alive."""
    check("a balanced paren inside the path survives the markdown wrapper",
          urls("see [Sleep With Me](https://en.wikipedia.org/wiki/Sleep_with_Me_(podcast))"),
          ["https://en.wikipedia.org/wiki/Sleep_with_Me_(podcast)"])
    check("...and bare, with a sentence period after it",
          urls("read https://en.wikipedia.org/wiki/Sleep_with_Me_(podcast)."),
          ["https://en.wikipedia.org/wiki/Sleep_with_Me_(podcast)"])
    check("a genuinely unmatched trailing paren is still dropped",
          urls("(see https://example.com/a)"), ["https://example.com/a"])


def test_every_markdown_form_is_reached():
    doc = ("inline [Alpha](https://a.example.com/one)\n"
           "autolink <https://b.example.com/two>\n"
           "bare https://c.example.com/three\n"
           "ref [Delta][d]\n\n"
           "[d]: https://d.example.com/four\n")
    check("inline, autolink, bare and reference-style all extract",
          urls(doc), ["https://a.example.com/one", "https://b.example.com/two",
                      "https://c.example.com/three", "https://d.example.com/four"])
    got = vu.extract(doc)
    check("...and the link text rides along for layer 2",
          [l.text for l in got if l.text], ["Alpha", "Delta"])
    # The reference link is cited on line 4 and defined on line 6; both are
    # places a reader would go to fix it, so both are kept.
    check("...with the line number, so a report can point at the citation",
          [l.lines for l in got], [[1], [2], [3], [4, 6]])


def test_what_must_never_be_fetched():
    doc = ("[[Some Wiki Link]] and [note](hook://p/Thing) and "
           "[mail](mailto:x@y.com) and [local](http://localhost:8080/x) and "
           "[lan](http://192.168.1.5/status) and [f](file:///tmp/x.html)\n"
           "[real](https://example.com/ok)")
    check("wiki-links, hook/mailto/file schemes, localhost and RFC-1918 are skipped",
          urls(doc), ["https://example.com/ok"])


def test_a_url_in_a_fence_is_an_example_not_a_citation():
    doc = ("```bash\ncurl https://fake.example.com/not-a-citation\n```\n"
           "real one: https://example.com/yes")
    check("fenced code is not scanned", urls(doc), ["https://example.com/yes"])


def test_the_same_url_twice_is_one_finding_on_two_lines():
    doc = "[a](https://example.com/x)\nand again [b](https://example.com/x)"
    got = vu.extract(doc)
    check("deduped to one entry", len(got), 1)
    check("...retaining every line it appeared on", got[0].lines, [1, 2])


print("\nLayer 1 — 'could not determine' must not read as 'dead'")


class _Resp:
    def __init__(self, body="", url="https://example.com/x", status=200):
        self._b = body.encode(); self._u = url; self.status = status
        self.headers = type("H", (), {"get_content_charset": lambda s: "utf-8"})()

    def read(self, n=None): return self._b
    def geturl(self): return self._u
    def __enter__(self): return self
    def __exit__(self, *a): return False


def _stub(resp=None, exc=None):
    def opener(req, timeout=None):
        if exc is not None:
            raise exc
        return resp
    vu.urllib.request.urlopen = opener


_real_urlopen = vu.urllib.request.urlopen


def verdict_for(url="https://example.com/x", text="", **kw):
    _stub(**kw)
    try:
        return vu.fetch(vu.Link(url=url, text=text))
    finally:
        vu.urllib.request.urlopen = _real_urlopen


def test_a_bot_wall_is_never_a_finding():
    """Two of the 46 URLs in the corpus behind this feature were live pages
    behind bot walls. A tool that reported those as dead would be ignored inside
    a week — and this is also the rule that makes escalation unnecessary, since
    'could not determine' is an acceptable terminal answer."""
    for code in (401, 403, 429, 999):
        v = verdict_for(exc=urllib.error.HTTPError(
            "https://example.com/x", code, "no", {}, io.BytesIO(b"")))
        check(f"HTTP {code} is BLOCKED", v.status, "BLOCKED")
        check(f"...and HTTP {code} is not reportable to Dan", v.reportable, False)


def test_the_verdicts_that_do_report():
    v = verdict_for(exc=urllib.error.HTTPError(
        "https://example.com/x", 404, "nf", {}, io.BytesIO(b"")))
    check("404 is DEAD", (v.status, v.reportable), ("DEAD", True))
    v = verdict_for(exc=urllib.error.HTTPError(
        "https://example.com/x", 410, "gone", {}, io.BytesIO(b"")))
    check("410 is GONE", (v.status, v.reportable), ("GONE", True))
    v = verdict_for(exc=urllib.error.HTTPError(
        "https://example.com/x", 503, "err", {}, io.BytesIO(b"")))
    check("5xx is SERVER-ERR and not reportable — retry later, not a dead link",
          (v.status, v.reportable), ("SERVER-ERR", False))


def test_a_200_that_means_not_found():
    """The case a status code cannot catch: a site that serves its 404 page with
    a 200. Common enough on CMS-backed sites that ignoring it would leave a hole
    exactly where fabricated URLs land."""
    v = verdict_for(resp=_Resp("<title>Page Not Found</title><p>sorry</p>"))
    check("a not-found title under HTTP 200 is SOFT-404", v.status, "SOFT-404")
    check("...and it is reportable", v.reportable, True)
    v = verdict_for(resp=_Resp("<title>The Sleep Podcast</title>"))
    check("a normal page is OK", v.status, "OK")


def test_only_redirects_that_lose_the_target_are_reported():
    v = verdict_for(url="https://site.example.com/podcast/deep/thing",
                    resp=_Resp("<title>Home</title>", url="https://site.example.com/"))
    check("a deep path landing on the site root is REDIR-HOME", v.status, "REDIR-HOME")
    v = verdict_for(url="https://old.example.com/x",
                    resp=_Resp("<title>New</title>", url="https://other.example.net/x"))
    check("crossing domains is REDIR-OFFSITE", v.status, "REDIR-OFFSITE")
    v = verdict_for(url="http://www.example.com/x",
                    resp=_Resp("<title>Fine</title>", url="https://example.com/x/"))
    check("http→https + www + trailing slash is NOT a finding", v.status, "OK")


print("\nLayer 2 — the check that catches a fabrication which happens to resolve")


def test_why_layer_2_exists():
    """Layer 1 caught the ten fabricated Apple IDs by luck — all ten happened not
    to resolve. An invented ID that lands on a *different real podcast* returns
    200 and passes reachability cleanly, and the citation is then confidently,
    silently wrong. That is the more dangerous case, and only label matching
    sees it."""
    check("a link labelled one show pointing at another does not match",
          vu.label_matches("Sleep With Me", "Crime Junkie — True Crime Podcast"),
          False)
    check("...while the right target does",
          vu.label_matches("Sleep With Me", "Sleep With Me Podcast on Apple Podcasts"),
          True)


def test_label_matching_is_deliberately_generous():
    """A page title routinely differs from a show's common name. This check is
    tuned to catch 'points somewhere else entirely', not to police wording — a
    strict version would produce exactly the false alarms that kill trust."""
    # A title that is nothing but boilerplate ("Listen on Apple Podcasts")
    # tokenizes to nothing once the stop list is applied, which means there is no
    # signal either way. That must read as "no finding", not as a mismatch — the
    # tool's whole credibility rests on never manufacturing an alarm out of an
    # absence of evidence.
    check("a title made only of boilerplate yields no signal, so no finding",
          vu.label_matches("Nothing Much Happens", "Listen on Apple Podcasts"), True)
    check("one meaningful shared token is enough",
          vu.label_matches("the Nothing Much Happens show",
                           "Nothing Much Happens: bedtime stories"), True)
    check("an unlabelled link cannot mismatch", vu.label_matches("", "Anything"), True)
    check("...and neither can a titleless page",
          vu.label_matches("Some Show", ""), True)


def test_mismatch_only_applies_to_an_otherwise_healthy_page():
    """A dead link must report as dead, not as a label problem — the verdict has
    to name the fault the user can act on."""
    _stub(resp=_Resp("<title>Crime Junkie</title>"))
    try:
        out = vu.vet([vu.Link(url="https://example.com/x", text="Sleep With Me")])
    finally:
        vu.urllib.request.urlopen = _real_urlopen
    check("a 200 whose title contradicts the label is MISMATCH", out[0].status, "MISMATCH")
    check("...and the detail shows both sides so the fix is obvious",
          "Sleep With Me" in out[0].detail and "Crime Junkie" in out[0].detail, True)


def test_the_report_separates_findings_from_unknowns():
    """The undetermined block is not a list of problems, and saying so in the
    output is what stops a reader treating BLOCKED as a defect."""
    vs = [vu.Verdict(vu.Link(url="https://a/x", lines=[3]), "DEAD", "HTTP 404", 404),
          vu.Verdict(vu.Link(url="https://b/y", lines=[9]), "BLOCKED", "HTTP 403", 403),
          vu.Verdict(vu.Link(url="https://c/z", lines=[1]), "OK", "", 200)]
    text = vu.report(vs, doc="survey.md")
    check("the count names reportable and undetermined separately",
          "1 reportable, 1 undetermined" in text, True)
    check("...the finding carries its line number", "[DEAD]:3" in text, True)
    check("...and the unknown block says outright it is not a finding",
          "NOT a finding" in text, True)


test_the_paren_regression()
test_every_markdown_form_is_reached()
test_what_must_never_be_fetched()
test_a_url_in_a_fence_is_an_example_not_a_citation()
test_the_same_url_twice_is_one_finding_on_two_lines()
test_a_bot_wall_is_never_a_finding()
test_the_verdicts_that_do_report()
test_a_200_that_means_not_found()
test_only_redirects_that_lose_the_target_are_reported()
test_why_layer_2_exists()
test_label_matching_is_deliberately_generous()
test_mismatch_only_applies_to_an_otherwise_healthy_page()
test_the_report_separates_findings_from_unknowns()

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
