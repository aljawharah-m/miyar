from pathlib import Path
from core.engine import analyze


def test_mixed_reference_root_is_not_collapsed_to_synthetic():
    ar='وفي هذا المثال [QURAN_REF: 2:183] و [HADITH_REF: TEST-123] و [SOURCE_ID: ABC-001].'
    en='[QURAN_REF: 2:185] [HADITH_REF: TEST-321] [SOURCE_ID: ABC-010]'
    r=analyze(ar,en,use_live_sources=False,use_semantic_ai=False)
    root=next(x for x in r['issues'] if x.get('type')=='reference_identifier_changed')
    assert root['reference_state']=='mixed'
    states={x['kind']:x['reference_state'] for x in root['sub_evidence']}
    assert states['QURAN_REF']=='changed'
    assert states['HADITH_REF']=='synthetic'
    assert states['SOURCE_ID']=='synthetic'


def test_all_synthetic_reference_root_stays_synthetic_and_nonreligious():
    ar='[HADITH_REF: TEST-123] [SOURCE_ID: ABC-001]'
    en='[HADITH_REF: TEST-321] [SOURCE_ID: ABC-010]'
    r=analyze(ar,en,use_live_sources=False,use_semantic_ai=False)
    root=next(x for x in r['issues'] if x.get('type')=='reference_identifier_changed')
    assert root['reference_state']=='synthetic'
    assert root['religious_impact']=='none'


def test_public_ui_does_not_use_success_checkmark_for_detected_terminology_gap():
    app=Path('app.py').read_text(encoding='utf-8')
    assert '⚠ فحص المصطلحات' not in app  # icon is dynamic, not hardcoded HTML
    assert 'term_icon="⚠"' in app
    assert 'arabic_gap_count_phrase(len(term_issues))' in app


def test_public_ui_separates_internal_reference_match_from_live_verification():
    app=Path('app.py').read_text(encoding='utf-8')
    assert 'مطابقة المرجع داخل النص' in app
    assert 'التحقق الخارجي الحي' in app
    assert 'لم يكتمل تحقق خارجي حي يمكن الاعتماد عليه في هذا الفحص' in app


def test_public_ui_explains_taxonomy_is_not_religious_impact():
    app=Path('app.py').read_text(encoding='utf-8')
    assert 'نوع الخطأ يصف طبيعة الخلل' in app
    assert 'ذات أثر ديني مباشر' in app


def test_public_ui_translation_status_is_result_not_evaluation_process():
    app=Path('app.py').read_text(encoding='utf-8')
    assert 'سلامة انتقال الترجمة' in app
    assert 'arabic_gap_count_phrase(len(ordered_issues))' in app
