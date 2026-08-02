#!/usr/bin/env python3
"""F294 layers 0-5 — extraction, verdicts, label matching, assertions, registry
probes, and the Stop hook.

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
import json
import pathlib
import tempfile
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


print("\nLayer 3 — the claim about the page, not just the page")


def test_the_claim_that_cost_three_round_trips():
    """A badge whose text lives only in `alt=` IS on the page and is NOT
    necessarily on the screen — mySleepButton's Play badge collapses behind a
    hamburger on tablet. A yes/no answer here would have been wrong in the
    direction that wasted Dan's time, so the check is three-valued."""
    page = ('<p>Fall asleep faster.</p>'
            '<a href="/play"><img alt="Get it on Google Play" src="b.png"></a>')
    check("a string present only in an attribute reports as markup, not text",
          vu.expectation(page, "Get it on Google Play"), "markup")
    check("a string in the visible copy reports as text",
          vu.expectation(page, "fall asleep faster"), "text")
    check("a string that is simply absent reports as absent",
          vu.expectation(page, "Nintendo Switch edition"), None)
    check("...and whitespace/case differences do not manufacture an absence",
          vu.expectation("<p>Get it   on\nGoogle  Play</p>", "get it on google play"),
          "text")


def test_expect_annotates_a_stronger_finding_rather_than_masking_it():
    _stub(resp=_Resp("<title>Crime Junkie</title><p>true crime</p>"))
    try:
        out = vu.vet([vu.Link(url="https://example.com/x", text="Sleep With Me")],
                     expect="lullaby")
    finally:
        vu.urllib.request.urlopen = _real_urlopen
    check("the label mismatch survives — it is the more actionable fault",
          out[0].status, "MISMATCH")
    check("...and the failed expectation is appended, not substituted",
          "does not contain 'lullaby'" in out[0].detail, True)


def test_a_page_that_never_loaded_cannot_be_asserted_about():
    v = verdict_for(exc=urllib.error.HTTPError(
        "https://example.com/x", 404, "nf", {}, io.BytesIO(b"")))
    check("no body means no expectation check — the verdict stays DEAD",
          (v.status, v.body), ("DEAD", ""))


print("\nLayer 4 — the registry probe, which is why --deep exists")

_real_get = vu._get

APPLE_PODCAST = ('{"resultCount":1,"results":[{"wrapperType":"track",'
                 '"kind":"podcast","collectionName":"Nothing Much Happens"}]}')
APPLE_SONG = ('{"resultCount":1,"results":[{"wrapperType":"track","kind":"song",'
              '"collectionName":"\\u041a\\u0440\\u0438\\u0432\\u0438\\u0446\\u043a\\u0438\\u0439"}]}')
APPLE_NONE = '{"resultCount":0,"results":[]}'


def _stub_get(mapping):
    """Route registry calls by URL substring; anything unmatched returns ''
    (the unreachable case), so a test can only pass by naming its own traffic."""
    def fake(url, timeout=None):
        for frag, body in mapping.items():
            if frag in url:
                return body
        return ""
    vu._get = fake


def probe(url, mapping):
    _stub_get(mapping)
    try:
        return vu.registry_probe(url)
    finally:
        vu._get = _real_get


def test_an_id_that_exists_is_not_the_question():
    """Found live, and the reason this test exists: the fabricated podcast ID
    1509001470 resolves with resultCount 1 — to a Russian children's choir
    recording. Apple runs ONE numeric namespace across podcasts, apps and songs,
    so an existence-only probe would have cleared a fabricated podcast URL on the
    strength of an unrelated song."""
    p = probe("https://podcasts.apple.com/us/podcast/sleep-with-me/id1509001470",
              {"itunes.apple.com/lookup": APPLE_SONG})
    check("a song ID behind a /podcast/ URL is NOT found", p.found, False)
    check("...and the evidence names what the ID actually is",
          "a song" in p.detail and "not what this URL claims" in p.detail, True)
    p = probe("https://podcasts.apple.com/us/podcast/nothing-much/id1487513861",
              {"itunes.apple.com/lookup": APPLE_PODCAST})
    check("the same ID shape with kind=podcast is found", p.found, True)
    check("...and hands back the canonical name for layer 2",
          p.name, "Nothing Much Happens")


def test_the_verdict_the_ten_fabrications_would_have_got():
    p = probe("https://podcasts.apple.com/us/podcast/x/id1268371860",
              {"itunes.apple.com/lookup": APPLE_NONE})
    check("resultCount 0 is a definitive no-such-ID", p.found, False)
    check("...naming the lookup, per success criterion 4",
          "resultCount 0" in p.detail and "1268371860" in p.detail, True)


def test_each_registry_answers_for_its_own_ids():
    p = probe("https://doi.org/10.1038/nature14539",
              {"doi.org/api/handles": '{"responseCode":1,"handle":"10.1038/n"}'})
    check("DOI responseCode 1 is registered", (p.registry, p.found), ("doi", True))
    # The Handle API answers "no such handle" with responseCode 100 *and* HTTP
    # 404. `_get` must read error bodies or this verdict is silently lost —
    # which is exactly what happened on the first live run.
    p = probe("https://doi.org/10.1038/nature99999",
              {"doi.org/api/handles": '{"responseCode":100,"handle":"x"}'})
    check("DOI responseCode 100 is no-such-DOI", p.found, False)
    p = probe("https://arxiv.org/abs/2401.99999",
              {"export.arxiv.org": "<feed><title>ArXiv Query</title>"
                                   "<entry><title>Error</title></entry></feed>"})
    check("arXiv's Error entry is no-such-ID", (p.registry, p.found), ("arxiv", False))
    p = probe("https://arxiv.org/abs/1706.03762",
              {"export.arxiv.org": "<feed><title>ArXiv Query</title>"
                                   "<entry><title>Attention Is All You Need</title></entry></feed>"})
    check("...and a real one carries its title", p.name, "Attention Is All You Need")
    p = probe("https://pubmed.ncbi.nlm.nih.gov/28978842/",
              {"esummary.fcgi": '{"result":{"28978842":{"title":"Sleep and memory"}}}'})
    check("PubMed answers for a PMID", (p.registry, p.name), ("pubmed", "Sleep and memory"))
    check("a URL carrying no registry ID gets no probe",
          probe("https://example.com/blog/post", {}), None)


def test_an_unreachable_registry_is_undetermined_not_a_verdict():
    """The same discipline as BLOCKED: 'could not ask' must never masquerade as
    'the answer is no', or the tool invents dead links during a network blip."""
    p = probe("https://podcasts.apple.com/us/podcast/x/id123456789", {})
    check("no response from the lookup yields found=None", p.found, None)


def test_deepen_can_condemn_and_can_clear():
    v = vu.Verdict(vu.Link(url="https://podcasts.apple.com/us/podcast/x/id1268371860"),
                   "OK", "", 200, "Some Page")
    _stub_get({"itunes.apple.com/lookup": APPLE_NONE, "archive.org": "{}"})
    try:
        vu.deepen(v)
    finally:
        vu._get = _real_get
    check("a page that served happily is condemned by the registry", v.status, "DEAD")

    v = vu.Verdict(vu.Link(url="https://podcasts.apple.com/us/podcast/x/id1487513861"),
                   "BLOCKED", "HTTP 403", 403)
    _stub_get({"itunes.apple.com/lookup": APPLE_PODCAST})
    try:
        vu.deepen(v)
    finally:
        vu._get = _real_get
    check("...and a bot wall is cleared by it, with no browser involved",
          v.status, "OK")
    check("...the API sidestep saying so in the detail",
          "resolved via registry" in v.detail, True)


def test_a_dead_link_is_offered_its_last_snapshot():
    """Reporting a dead citation without its archive date makes the user redo the
    lookup by hand; the point is a repointable link, not a red mark."""
    v = vu.Verdict(vu.Link(url="https://old.example.com/x"), "DEAD", "HTTP 404", 404)
    _stub_get({"archive.org/wayback": '{"archived_snapshots":{"closest":'
                                      '{"available":true,"timestamp":"20190412034500"}}}'})
    try:
        vu.deepen(v)
    finally:
        vu._get = _real_get
    check("the snapshot date is appended", "last archived 2019-04-12" in v.detail, True)

    v = vu.Verdict(vu.Link(url="https://old.example.com/y"), "DEAD", "HTTP 404", 404)
    _stub_get({"archive.org/wayback": '{"archived_snapshots":{}}'})
    try:
        vu.deepen(v)
    finally:
        vu._get = _real_get
    check("...and nothing is invented when there is no snapshot", v.detail, "HTTP 404")


def test_a_resolver_doing_its_job_is_not_link_rot():
    """A DOI exists to hand you off to a publisher. Flagging that as
    REDIR-OFFSITE would fire on every correctly-working DOI in the vault."""
    check("doi.org → nature.com is not a finding",
          vu._classify_redirect("https://doi.org/10.1038/nature14539",
                                "https://www.nature.com/articles/nature14539"), ("", ""))
    check("...while an ordinary site crossing domains still is",
          vu._classify_redirect("https://old.example.com/x",
                                "https://other.example.net/x")[0], "REDIR-OFFSITE")


print("\nLayer 4 — fragments, where the SPA guard prevents a false alarm")


def test_a_fragment_is_only_judged_when_the_page_renders_anchors():
    page = '<h2 id="Format_and_structure">F</h2><h2 id="References">R</h2>'
    check("a fragment matching no id on an id-rendering page is absent",
          vu._fragment_state("https://x/y#Format", page), False)
    check("...and one that matches is present",
          vu._fragment_state("https://x/y#References", page), True)
    check("a percent-encoded fragment is decoded before comparing",
          vu._fragment_state("https://x/y#Format%5Fand%5Fstructure",
                             '<h2 id="Format_and_structure">F</h2>'), True)
    # The guard that keeps this check honest: a page carrying no ids at all is an
    # SPA shell building its anchors client-side, so absence proves nothing.
    check("a page with no ids at all yields no verdict, not a failure",
          vu._fragment_state("https://x/y#anything", "<div><p>hi</p></div>"), None)
    check("a URL with no fragment is not asked about",
          vu._fragment_state("https://x/y", page), None)
    check("a #:~:text= scroll-to-text fragment is not an anchor claim",
          vu._fragment_state("https://x/y#:~:text=hello", page), None)


def test_no_anchor_is_a_deep_only_verdict():
    _stub(resp=_Resp('<title>T</title><h2 id="Real">R</h2>',
                     url="https://example.com/p#Missing"))
    try:
        shallow = vu.vet([vu.Link(url="https://example.com/p#Missing")])
        deep = vu.vet([vu.Link(url="https://example.com/p#Missing")], deep=True)
    finally:
        vu.urllib.request.urlopen = _real_urlopen
    check("the default pass does not report anchors", shallow[0].status, "OK")
    check("--deep does", deep[0].status, "NO-ANCHOR")


def test_the_canonical_name_outranks_the_page_title():
    """The registry knows what the target IS; a page <title> is marketing. When
    both are available the registry wins the layer-2 comparison."""
    _stub(resp=_Resp("<title>Podcasts on Apple Podcasts</title>",
                     url="https://podcasts.apple.com/us/podcast/x/id777"))
    _stub_get({"itunes.apple.com/lookup": APPLE_PODCAST})
    try:
        out = vu.vet([vu.Link(url="https://podcasts.apple.com/us/podcast/x/id777",
                              text="Sleep With Me")], deep=True)
    finally:
        vu.urllib.request.urlopen = _real_urlopen
        vu._get = _real_get
    check("a link labelled 'Sleep With Me' pointing at 'Nothing Much Happens' "
          "is caught by the registry name", out[0].status, "MISMATCH")
    check("...and the detail quotes the registry, not the boilerplate title",
          "Nothing Much Happens" in out[0].detail, True)


def test_the_body_never_escapes_the_verdict():
    """Pages are held only long enough for layers 3-4 to read them. Leaving them
    on the verdict would put 200 KB of HTML into every --json report."""
    _stub(resp=_Resp("<title>T</title>" + "<p>x</p>" * 500))
    try:
        out = vu.vet([vu.Link(url="https://example.com/x")])
    finally:
        vu.urllib.request.urlopen = _real_urlopen
    check("the body is cleared before the verdict is returned", out[0].body, "")


print("\nLayer 5 — the Stop hook, which must never trap a session")

vu.HOOK_DIR = pathlib.Path(tempfile.mkdtemp(prefix="vet-url-test-"))
NOW = 1_800_000_000


def _transcript(*user_texts):
    p = vu.HOOK_DIR / "t.jsonl"
    p.write_text("".join(
        json.dumps({"type": "user", "message": {"content": t}}) + "\n"
        for t in user_texts), encoding="utf-8")
    return str(p)


def hook_for(msg, resp=None, exc=None, session="s1", transcript="", active=False):
    _stub(resp=resp, exc=exc)
    try:
        return vu.hook({"last_assistant_message": msg, "session_id": session,
                        "transcript_path": transcript,
                        "stop_hook_active": active}, NOW)
    finally:
        vu.urllib.request.urlopen = _real_urlopen


def test_a_turn_with_no_urls_does_no_work():
    """Nearly every turn. It must cost nothing, so the check has to end before
    any I/O — no transcript read, no cache read, no fetch."""
    _stub(exc=AssertionError("a URL-free turn must never reach the network"))
    try:
        out = vu.hook({"last_assistant_message": "Done — 37 suites green.",
                       "session_id": "s0"}, NOW)
    finally:
        vu.urllib.request.urlopen = _real_urlopen
    check("no URLs means allow, untouched", out, {})


def test_a_dead_citation_forces_a_correction():
    out = hook_for("See [the show](https://example.com/gone)",
                   exc=urllib.error.HTTPError("https://example.com/gone", 404,
                                              "nf", {}, io.BytesIO(b"")),
                   session="dead1")
    check("a 404 blocks the stop", out.get("decision"), "block")
    check("...naming the URL so the correction can be specific",
          "https://example.com/gone" in out.get("reason", ""), True)
    check("...and telling the agent not to simply re-assert it",
          "do not re-assert" in out.get("reason", ""), True)


def test_what_must_never_block_a_conversation():
    """A bot wall says nothing about existence, and a label mismatch is fuzzy.
    Either one blocking chat is the false alarm that gets the hook turned off —
    so the hook fires only on unambiguous non-resolution."""
    out = hook_for("[a](https://example.com/walled)",
                   exc=urllib.error.HTTPError("https://example.com/walled", 403,
                                              "no", {}, io.BytesIO(b"")),
                   session="blk1")
    check("BLOCKED does not block", out, {})
    out = hook_for("[Sleep With Me](https://example.com/other)",
                   resp=_Resp("<title>Crime Junkie</title>",
                              url="https://example.com/other"), session="mis1")
    check("MISMATCH does not block chat either", out, {})
    out = hook_for("[fine](https://example.com/ok)",
                   resp=_Resp("<title>All good</title>",
                              url="https://example.com/ok"), session="ok1")
    check("a healthy link is silent", out, {})


def test_one_correction_per_url_set_no_loop():
    """A blocking Stop hook can re-fire on its own continuation. Keyed on the URL
    set rather than the turn, so the guard holds regardless of what loop
    protection the runtime supplies."""
    args = dict(exc=urllib.error.HTTPError("https://example.com/x", 404, "nf",
                                           {}, io.BytesIO(b"")), session="loop1")
    first = hook_for("[a](https://example.com/x)", **args)
    second = hook_for("[a](https://example.com/x)", **args)
    check("the first report blocks", first.get("decision"), "block")
    check("the identical set does not block twice", second, {})
    check("the runtime's own loop flag is honoured too",
          hook_for("[a](https://example.com/y)", active=True, session="loop2",
                   exc=args["exc"]), {})


def test_a_url_dan_supplied_is_not_corrected_at_him():
    t = _transcript("have a look at https://example.com/dans-link please")
    out = hook_for("Sure — https://example.com/dans-link is the one you sent.",
                   exc=urllib.error.HTTPError("https://example.com/dans-link", 404,
                                              "nf", {}, io.BytesIO(b"")),
                   session="own1", transcript=t)
    check("quoting back a link Dan supplied is not a finding", out, {})


def test_the_hook_fails_open_on_anything_unexpected():
    """The whole point of a Stop hook is that it runs unattended on every turn.
    Trapping a session is a worse outcome than missing a dead link."""
    check("unparseable stdin allows the stop", vu.hook_main("not json at all"), 0)
    check("empty stdin allows the stop", vu.hook_main(""), 0)


def test_the_cache_spends_one_fetch_per_url_per_hour():
    calls = []

    def counting(req, timeout=None):
        calls.append(req.full_url)
        return _Resp("<title>Fine</title>", url="https://example.com/cached")

    vu.urllib.request.urlopen = counting
    try:
        vu.hook({"last_assistant_message": "[a](https://example.com/cached)",
                 "session_id": "c1"}, NOW)
        vu.hook({"last_assistant_message": "again [b](https://example.com/cached) "
                                           "and [c](https://example.com/cached2)",
                 "session_id": "c2"}, NOW + 5)
    finally:
        vu.urllib.request.urlopen = _real_urlopen
    check("the repeated URL is fetched once across turns",
          calls.count("https://example.com/cached"), 1)


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
test_a_turn_with_no_urls_does_no_work()
test_a_dead_citation_forces_a_correction()
test_what_must_never_block_a_conversation()
test_one_correction_per_url_set_no_loop()
test_a_url_dan_supplied_is_not_corrected_at_him()
test_the_hook_fails_open_on_anything_unexpected()
test_the_cache_spends_one_fetch_per_url_per_hour()
test_the_claim_that_cost_three_round_trips()
test_expect_annotates_a_stronger_finding_rather_than_masking_it()
test_a_page_that_never_loaded_cannot_be_asserted_about()
test_an_id_that_exists_is_not_the_question()
test_the_verdict_the_ten_fabrications_would_have_got()
test_each_registry_answers_for_its_own_ids()
test_an_unreachable_registry_is_undetermined_not_a_verdict()
test_deepen_can_condemn_and_can_clear()
test_a_dead_link_is_offered_its_last_snapshot()
test_a_resolver_doing_its_job_is_not_link_rot()
test_a_fragment_is_only_judged_when_the_page_renders_anchors()
test_no_anchor_is_a_deep_only_verdict()
test_the_canonical_name_outranks_the_page_title()
test_the_body_never_escapes_the_verdict()

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
