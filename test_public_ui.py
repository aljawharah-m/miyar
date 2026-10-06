from pathlib import Path

APP=(Path(__file__).resolve().parents[1]/"app.py").read_text(encoding="utf-8")


def test_no_gendered_public_prompts():
    for bad in ["الصقي", "اكتبي", "جربي", "أدخلي"]:
        assert bad not in APP


def test_no_public_technical_copy_leaks():
    for bad in [
        '"sentence-transformers/',
        '"تعليل LLM',
        '"OpenAI',
        '"يعمل التحليل محليًا',
        '"الطبقات المستخدمة',
        '"فحص محلي مكتمل',
        '"جاهزة مبدئيًا للنشر',
    ]:
        assert bad not in APP


def test_empty_inputs_are_disabled():
    assert "disabled=not ready" in APP


def test_neutral_placeholders():
    assert 'placeholder="النص العربي هنا"' in APP
    assert 'placeholder="الترجمة هنا"' in APP


def test_public_safe_gate_is_scoped():
    assert 'return "لا يظهر مانع دلالي"' in APP
    assert "لا يثبت صحة المحتوى الشرعي الأصلي" in APP


def test_safe_result_hides_human_review_controls():
    assert 'if res["status"] == "review":' in APP
    assert 'اعتماد التنبيه' not in APP
    assert 'رفض التنبيه' not in APP
    assert 'إحالة لمختص' not in APP


def test_public_app_disables_external_generative_decision_layer():
    assert 'res = analyze(ar, en, use_live_sources=True, use_semantic_ai=True)' in APP
    assert "OPENAI_API_KEY" not in APP


def test_user_controlled_html_is_escaped():
    assert "def esc(value):" in APP
    assert "{esc(ar_piece)}" in APP
    assert "{esc(en_piece)}" in APP


def test_public_ui_supports_long_passages():
    assert "max_chars=12000" in APP
    assert "حتى 12,000 حرف" in APP


def test_public_ui_keeps_all_detected_issues_accessible_without_clutter():
    assert 'with st.expander(f"الفجوات المكتشفة ({len(ordered_issues)})")' in APP
    assert "for issue in ordered_issues:" in APP
    assert "من دون الاعتماد على رقم المقطع" in APP


def test_public_ui_knows_curated_terminology_layer():
    assert '"curated_terminology_rule": "قاعدة مصطلحية محافظة"' in APP


def test_actionable_correction_flow_is_public_and_safe():
    assert "build_high_confidence_correction" in APP
    assert "تصحيحات آمنة مقترحة" in APP
    assert "أما البقية فلا يعيد صياغتها آليًا حتى لا يغيّر المعنى" in APP
    assert "طبّق التصحيح الآمن وأعد الفحص" not in APP
    assert "طبّق التصحيحات الآمنة وأعد الفحص" not in APP
    assert "miyar_auto_run" not in APP


def test_ai_similarity_is_not_in_primary_result_strip():
    assert "التقارب الدلالي العام:" in APP
    assert "عرض تفاصيل الفحص" in APP
    assert "التحليل الدلالي بالذكاء الاصطناعي" not in APP


def test_hero_is_short_and_value_first():
    assert "سلامة الصياغة لا تعني سلامة المعنى" in APP
    assert "قد تبدو الترجمة صحيحة وواضحة" in APP
    assert "تصحيح آمن" in APP


def test_public_ui_uses_collapsed_gap_and_review_sections():
    assert "الفجوات المكتشفة" in APP
    assert "تصحيحات آمنة مقترحة" in APP
    assert "طبّق التصحيحات الآمنة وأعد الفحص" not in APP
    assert "فجوات تحتاج مراجعة بشرية" in APP


def test_public_ui_explains_product_and_remaining_review_work():
    assert "مِعيار يراجع ترجمة موجودة قبل نشرها" in APP
    assert "تصحيح آمن" in APP
    assert "تحتاج مراجعة بشرية" in APP
    assert "لا يوجد تصحيح آلي محدد" in APP


def test_public_ui_names_repeated_quran_locations():
    assert "quran_ref_label" in APP
    assert "ورد النص في أكثر من موضع قرآني" in APP


def test_public_ui_does_not_expose_internal_check_count_as_gap_count():
    assert "فحوص تحتاج انتباه" not in APP
    assert "فحصًا دون تنبيه" not in APP


def test_public_ui_does_not_overclaim_local_terminology_evidence():
    assert "قاعدة مصطلحية موثقة داخل مِعيار" not in APP
    assert "فحصًا دون تنبيه" not in APP
    assert "التفاصيل متاحة عند الحاجة، من دون مزاحمة النتيجة الأساسية." not in APP


def test_public_ui_makes_reference_check_self_explanatory_and_collapsed():
    assert 'with st.expander("التحقق من الترجمة بالمراجع الموثوقة")' in APP
    assert "إذا تعرّف مِعيار على آية أو حديث" in APP
    assert "الترجمة المرجعية الموثوقة" in APP
    assert "ماذا استفاد مِعيار من المرجع؟" in APP


def test_public_ui_collapses_evidence_and_moves_route_to_technical_details():
    assert 'with st.expander("كيف وصل مِعيار إلى هذا القرار؟")' in APP
    assert "ملخص الدليل" in APP
    assert "المسار المرجعي الداخلي" in APP
    assert '<div class="section-head">المسار المرجعي</div>' not in APP


def test_public_issue_titles_strip_segment_numbers_and_show_text_context():
    assert "_public_issue_title" in APP
    assert "source_segment" in APP
    assert "translation_segment" in APP
    assert r"المقطع\s*\d+" in APP


def test_result_summary_has_no_redundant_helper_sentence():
    assert "التفاصيل الكاملة متاحة عند الحاجة بدون إغراق صفحة المراجعة." not in APP


def test_safe_corrections_show_full_before_and_after_context():
    assert "الموضع في الأصل" in APP
    assert "<span>قبل</span>" in APP
    assert "<span>بعد</span>" in APP
    assert "←" not in APP
