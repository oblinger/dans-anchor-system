"""R-markdown-17 — a fenced line wider than FENCE_MAX_WIDTH is a finding;
prose lines are free; ~~~ fences and an unclosed fence count; markers are
skipped. Also pins the shared `fence_overwidth_lines` the R-fence-guard deny
bodies call, so the audit and the refusal read the same width."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"


def _ap():
    spec = importlib.util.spec_from_file_location("audit_plan_fw", SCRIPTS / "audit-plan.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["audit_plan_fw"] = mod
    spec.loader.exec_module(mod)
    return mod


def _doc(tmp: Path, body: str) -> Path:
    p = tmp / "X.md"
    p.write_text(body, encoding="utf-8")
    return p


def test_width_constant_is_72():
    assert _ap().FENCE_MAX_WIDTH == 72


def test_fits_passes_and_prose_is_free(tmp_path):
    ap = _ap()
    ok = "x" * 72
    p = _doc(tmp_path, "# T\n" + "p" * 300 + "\n\n```\n" + ok + "\n```\n")
    assert ap.chk_md_fence_width(p, tmp_path, None)[0] == "pass"
    assert ap.fence_overwidth_lines(p.read_text()) == []


def test_73_fails_with_line_and_length(tmp_path):
    ap = _ap()
    p = _doc(tmp_path, "# T\n\n```text\nshort\n" + "y" * 73 + "\n```\n")
    verdict, detail = ap.chk_md_fence_width(p, tmp_path, None)
    assert verdict == "fail" and "line(s) 5" in detail and "73" in detail
    assert ap.fence_overwidth_lines(p.read_text()) == [(5, 73, "y" * 73)]


def test_tilde_fence_and_unclosed_fence_count(tmp_path):
    ap = _ap()
    p = _doc(tmp_path, "~~~\n" + "z" * 80 + "\n~~~\n")
    assert ap.chk_md_fence_width(p, tmp_path, None)[0] == "fail"
    q = _doc(tmp_path, "```\n" + "w" * 80 + "\n")
    assert ap.chk_md_fence_width(q, tmp_path, None)[0] == "fail"


def test_marker_line_with_long_info_string_is_skipped(tmp_path):
    ap = _ap()
    p = _doc(tmp_path, "```" + "i" * 90 + "\nok\n```\n")
    assert ap.chk_md_fence_width(p, tmp_path, None)[0] == "pass"


def test_registered_under_check_name():
    ap = _ap()
    assert ap.CHECKERS["md_fence_width"] is ap.chk_md_fence_width
