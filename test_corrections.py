from core.corrections import build_high_confidence_correction
from core.engine import analyze


def test_zakat_charity_gets_actionable_correction():
    res = analyze("الزكاة واجبة", "Charity is obligatory", use_live_sources=False, use_semantic_ai=False)
    fix = build_high_confidence_correction("Charity is obligatory", res["issues"])
    assert fix is not None
    assert fix["corrected_text"] == "Zakat is obligatory"
    assert fix["changes"][0]["from"] == "charity"
    assert fix["changes"][0]["to"] == "Zakat"


def test_context_dependent_review_is_not_auto_rewritten():
    res = analyze("الربا محرم", "Interest is forbidden", use_live_sources=False, use_semantic_ai=False)
    fix = build_high_confidence_correction("Interest is forbidden", res["issues"])
    assert fix is None


def test_multiple_clear_term_fixes_can_be_applied_together():
    ar = "الزكاة واجبة. الوضوء شرط للصلاة."
    en = "Charity is obligatory. Washing is required for prayer."
    res = analyze(ar, en, use_live_sources=False, use_semantic_ai=False)
    fix = build_high_confidence_correction(en, res["issues"])
    assert fix is not None
    assert "Zakat" in fix["corrected_text"]
    assert "Wudu" in fix["corrected_text"]
    assert len(fix["changes"]) >= 2


def test_segment_scoped_fix_does_not_replace_correct_charity_in_previous_sentence():
    ar = "الصدقة مستحبة. الزكاة واجبة."
    en = "Charity is recommended. Charity is obligatory."
    res = analyze(ar, en, use_live_sources=False, use_semantic_ai=False)
    fix = build_high_confidence_correction(en, res["issues"])
    assert fix is not None
    assert fix["corrected_text"] == "Charity is recommended. Zakat is obligatory."


def test_term_fix_does_not_auto_rewrite_missing_exception():
    ar = "الزكاة واجبة ولا يجوز تركها إلا لعذر معتبر"
    en = "Charity is obligatory and it is not permissible to leave it"
    res = analyze(ar, en, use_live_sources=False, use_semantic_ai=False)
    fix = build_high_confidence_correction(en, res["issues"])
    # The sentence has another critical structural gap, so even Zakat is not presented
    # as if the whole sentence had a safe automatic rewrite.
    assert fix is None


def test_missing_necessity_exception_is_human_review_not_auto_rewrite():
    ar = "لا يجوز هذا إلا في حالة الضرورة"
    en = "This is not permissible"
    res = analyze(ar, en, use_live_sources=False, use_semantic_ai=False)
    assert build_high_confidence_correction(en, res["issues"]) is None


def test_unknown_exception_is_not_invented():
    ar = "لا يجوز هذا إلا لسبب خاص غير مذكور"
    en = "This is not permissible"
    res = analyze(ar, en, use_live_sources=False, use_semantic_ai=False)
    fix = build_high_confidence_correction(en, res["issues"])
    assert fix is None


def test_clear_number_mismatch_is_not_auto_rewritten():
    ar = "عدد الركعات هنا 3"
    en = "The number of rak'ahs here is 4"
    res = analyze(ar, en, use_live_sources=False, use_semantic_ai=False)
    assert build_high_confidence_correction(en, res["issues"]) is None


def test_common_yustahab_to_must_is_detected_but_not_auto_rewritten():
    ar = "يستحب فعل ذلك"
    en = "It must be done"
    res = analyze(ar, en, use_live_sources=False, use_semantic_ai=False)
    assert any(i.get("type") == "modality_shift" for i in res["issues"])
    assert build_high_confidence_correction(en, res["issues"]) is None


def test_correction_payload_keeps_full_unresolved_issue_context_for_human_review_ui():
    ar = "الزكاة واجبة. لا يجوز نسبة كلام إلى النبي بلا تثبت."
    en = "Charity is obligatory. This is definitely an authentic saying of the Prophet."
    res = analyze(ar, en, use_live_sources=False, use_semantic_ai=False)
    fix = build_high_confidence_correction(en, res["issues"])
    assert fix is not None
    assert fix["unresolved_issue_count"] >= 1
    assert fix["unresolved_issues"]
    assert all(isinstance(x, dict) for x in fix["unresolved_issues"])
    assert any(x.get("source_segment") for x in fix["unresolved_issues"])


def test_safe_fix_change_contains_writer_facing_sentence_context():
    ar = "الصدقة مستحبة. الزكاة واجبة."
    en = "Charity is recommended. Charity is obligatory."
    res = analyze(ar, en, use_live_sources=False, use_semantic_ai=False)
    fix = build_high_confidence_correction(en, res["issues"])
    assert fix is not None
    zakat_change = next(x for x in fix["changes"] if x["kind"] == "terminology")
    assert "الزكاة" in zakat_change.get("source_segment", "")
    assert "charity" in zakat_change.get("translation_segment", "").lower()
