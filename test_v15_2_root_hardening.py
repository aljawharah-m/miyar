from core.engine import analyze
from core.corrections import build_high_confidence_correction


def run(ar,en):
    return analyze(ar,en,use_live_sources=False,use_semantic_ai=False)


def types(z):
    return {i.get('type') for i in z['issues']}


def test_an_masdariyya_is_not_condition():
    z=run('أن يتوضأ المسلم خير له','For the Muslim to perform Wudu is better for him.')
    assert 'condition' not in types(z)


def test_in_conditional_is_condition_and_preserved():
    z=run('إن يتوضأ المسلم صحت صلاته','If the Muslim performs Wudu, his prayer is valid.')
    assert z['status']=='safe'


def test_wajaba_to_may_is_modality_shift():
    z=run('وجب عليه الصيام','He may fast.')
    assert 'modality_shift' in types(z)


def test_ma_lam_missing_is_condition_loss():
    z=run('يجوز هذا ما لم يترتب عليه ضرر','This is permissible.')
    assert 'condition' in types(z)


def test_ma_lam_to_unless_is_safe():
    z=run('يجوز هذا ما لم يترتب عليه ضرر','This is permissible unless it causes harm.')
    assert z['status']=='safe'


def test_quantity_binding_catches_swapped_numbers_with_same_bag():
    z=run('خمس صلوات بعد مرور حول واحد','one prayer after five lunar years')
    assert 'quantity' in types(z)


def test_quantity_binding_accepts_correct_local_numbers():
    z=run('خمس صلوات بعد مرور حول واحد','five prayers after one lunar year')
    assert z['status']=='safe'


def test_ordinary_washing_not_ritual_ghusl_term():
    z=run('غسل اليدين مطلوب','Washing the hands is required.')
    assert z['status']=='safe'
    assert not any(i.get('source_span')=='الغسل' for i in z['issues'])


def test_vocalized_ghusl_is_ritual_term():
    z=run('الغُسل واجب في هذه الحالة','Ghusl is obligatory in this case.')
    assert z['status']=='safe'


def test_negation_polarity_flip_laysa_to_positive():
    z=run('ليست الزكاة صدقة تطوع','Zakat is voluntary charity.')
    assert 'negation' in types(z)


def test_prohibition_permission_flip():
    z=run('لا يجوز فعل ذلك','It is permissible to do that.')
    assert 'ruling_polarity_shift' in types(z)


def test_unequal_sentence_counts_still_keep_local_checks():
    ar='الزكاة واجبة. لا يجوز هذا إلا للضرورة.'
    en='Zakat is obligatory; this is not permissible except in necessity.'
    z=run(ar,en)
    assert z['status']=='safe'
    assert z['alignment']['mode'] in {'monotonic_grouped_ar','monotonic_grouped_en','sentence_1to1'}


def test_atomic_term_fix_only():
    z=run('الزكاة واجبة','Charity is obligatory')
    fix=build_high_confidence_correction('Charity is obligatory',z['issues'])
    assert fix and fix['corrected_text']=='Zakat is obligatory'
    assert {c['kind'] for c in fix['changes']}=={'terminology'}


def test_structural_gap_is_never_auto_rewritten():
    z=run('لا يجوز هذا إلا للضرورة','This is not permissible')
    assert build_high_confidence_correction('This is not permissible',z['issues']) is None


def test_modality_gap_is_never_auto_rewritten():
    z=run('يستحب فعل ذلك','It must be done')
    assert build_high_confidence_correction('It must be done',z['issues']) is None


def test_long_alignment_recovers_after_extra_english_sentence():
    ar = 'الزكاة واجبة. لا يجوز هذا إلا للضرورة. يجب الاحتفاظ بالسجل ثلاثين يوما. التوحيد أصل مهم.'
    en = 'Zakat is obligatory. This is not permissible except in necessity. This sentence is an unsupported addition. The log must be retained for thirty days. Tawhid is an important principle.'
    z = run(ar, en)
    # The inserted sentence must not shift the later pairs and create fake terminology/ruling errors.
    assert not any(i.get('source_segment','').startswith('يجب الاحتفاظ') and 'Tawhid' in i.get('translation_segment','') for i in z['issues'])
    assert not any(i.get('source_segment','').startswith('التوحيد') and 'log' in i.get('translation_segment','').lower() for i in z['issues'])


def test_long_alignment_recovers_after_missing_english_sentence():
    ar = 'الزكاة واجبة. هذا سطر تم حذفه من الترجمة. يجب الاحتفاظ بالسجل ثلاثين يوما. التوحيد أصل مهم.'
    en = 'Zakat is obligatory. The log must be retained for thirty days. Tawhid is an important principle.'
    z = run(ar, en)
    assert not any(i.get('source_segment','').startswith('يجب الاحتفاظ') and 'Tawhid' in i.get('translation_segment','') for i in z['issues'])
    assert not any(i.get('source_segment','').startswith('التوحيد') and 'log' in i.get('translation_segment','').lower() for i in z['issues'])


def test_equal_counts_can_use_local_merge_split_without_global_shift():
    ar = 'الزكاة واجبة؛ ولا يجوز هذا إلا للضرورة. يجب الاحتفاظ بالسجل ثلاثين يوما. التوحيد أصل مهم.'
    en = 'Zakat is obligatory. This is not permissible except in necessity; the log must be retained for thirty days. Tawhid is an important principle.'
    z = run(ar, en)
    assert not any(i.get('source_segment','').startswith('التوحيد') and 'log' in i.get('translation_segment','').lower() for i in z['issues'])


def test_ala_complementizer_is_not_exception():
    z=run('ينبغي ألا يحول النص الاحتمال إلى يقين','The text should not turn possibility into certainty.')
    assert 'exception' not in types(z)


def test_discourse_if_said_is_not_semantic_condition():
    z=run('إذا قيل إن الزكاة واجبة فالمقصود شرح المثال','When saying that Zakat is obligatory, this is only explaining the example.')
    assert not any(i.get('type')=='condition' and i.get('source_span') in {'إذا','اذا'} for i in z['issues'])


def test_one_of_principles_is_not_invented_quantity():
    z=run('من أصول الاعتقاد التوحيد','One of the principles of belief is Tawhid.')
    assert 'quantity' not in types(z)


def test_no_one_is_not_numeric_one():
    z=run('لا أحد قدم أكثر من ثلاثة ملفات','No one submitted more than three files.')
    assert 'quantity' not in types(z)


def test_in_after_reporting_verb_is_not_condition():
    z=run('قيل إن الزكاة عبادة مالية','It was said that Zakat is a financial act of worship.')
    assert 'condition' not in types(z)


def test_structured_reference_packet_does_not_shift_later_paragraphs():
    ar='''الزكاة واجبة\n\nوفي حالة وجود مرجع مكتوب بهذه الصيغة\n[QURAN_REF: 2:183]\nأو\n[HADITH_REF: TEST-123]\nأو\n[SOURCE_ID: ABC-001]\nفلا يجوز تغيير المعرف\n\nوقال أحمد لخالد إنه سيعود بعد المراجعة\n\nوقيل لفاطمة إن عليها مراجعة ملفها'''
    en='''Zakat is obligatory.\n\n[QURAN_REF: 2:185]\n\n[HADITH_REF: TEST-321]\n\n[SOURCE_ID: ABC-010]\n\nAll identifiers above were changed.\n\nAhmed told Khalid that he would return after the review.\n\nFatimah was told to review her file.'''
    z=run(ar,en)
    assert z['alignment']['mode']=='hierarchical_paragraph_1to1'
    assert z['alignment']['units']==4
    assert not any(i.get('source_segment','').startswith('وقال أحمد') and 'Fatimah' in i.get('translation_segment','') for i in z['issues'])
    assert not any(i.get('source_segment','').startswith('وقيل لفاطمة') and 'Ahmed' in i.get('translation_segment','') for i in z['issues'])
