from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "app.py"

def test_arabic_gap_count_helper_present_and_used():
    app = APP.read_text(encoding="utf-8")
    assert "def arabic_gap_count_phrase" in app
    assert "3 <= n <= 10" in app
    assert "arabic_gap_count_phrase(len(ref_issues))" in app
    assert "arabic_gap_count_phrase(len(term_issues))" in app
    assert "arabic_gap_count_phrase(len(ruling_issues))" in app
    assert "arabic_gap_count_phrase(len(ordered_issues))" in app

def test_taxonomy_summary_uses_feminine_category_labels():
    app = APP.read_text(encoding="utf-8")
    for label in ("دلالية دينية", "دلالية عامة", "منطقية/رقمية", "مرجعية", "معرفية"):
        assert label in app
    assert "taxonomy_summary_label(key)" in app

def test_live_reference_status_is_not_overstated():
    app = APP.read_text(encoding="utf-8")
    assert "لم يكتمل تحقق خارجي حي يمكن الاعتماد عليه في هذا الفحص" in app
    assert "لم يتم اعتماد تحقق خارجي حي مكتمل في هذا الفحص" not in app
