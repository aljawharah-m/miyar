from core.engine import analyze


def r(ar,en):
    return analyze(ar,en,use_live_sources=False,use_semantic_ai=False)


def types(z):
    return [i.get('type') for i in z['issues']]


def test_laysa_feminine_negation_preserved():
    z=r('الفتوى ليست رأيًا شخصيًا','A fatwa is not a personal opinion')
    assert z['status']=='safe'
    assert not z['issues']


def test_laysa_feminine_negation_loss_is_caught():
    z=r('الفتوى ليست رأيًا شخصيًا','A fatwa is a personal opinion')
    assert z['status']=='critical'
    assert 'negation' in types(z)


def test_shart_required_for_is_not_false_obligation():
    z=r('الوضوء شرط للصلاة','Wudu is required for prayer')
    assert z['status']=='safe'
    assert not any(i.get('type') in {'obligation','modality_shift'} for i in z['issues'])


def test_word_number_mismatch_ar_en():
    z=r('عدد الركعات ثلاث','The number of rakahs is four')
    q=next(i for i in z['issues'] if i.get('type')=='quantity')
    assert q['source_span']=='3' and q['translation_span']=='4'


def test_word_number_match_ar_en():
    z=r('عدد الركعات ثلاث','The number of rakahs is three')
    assert not any(i.get('type')=='quantity' for i in z['issues'])


def test_sunnah_reductive_gloss_requires_review_even_if_sunnah_present():
    z=r('السنة هدي النبي صلى الله عليه وسلم','Sunnah is merely tradition')
    assert z['status']=='review'
    assert any(i.get('type')=='terminology' and i.get('source_span')=='السنة' for i in z['issues'])


def test_sentence_local_ruling_swap_detected_when_document_counts_match():
    z=r('هذا مستحب. وهذا واجب.','This is obligatory. This is recommended.')
    assert z['status']=='critical'
    shifts=[i for i in z['issues'] if i.get('type')=='modality_shift']
    assert shifts
    assert shifts[0].get('translation_span')=='obligatory'


def test_sentence_local_terms_cannot_mask_each_other():
    z=r('الزكاة واجبة. والصدقة مستحبة.','Charity is obligatory. Zakat is recommended.')
    assert z['status']=='critical'
    assert any(i.get('type')=='flattening' and i.get('source_span')=='الزكاة' and i.get('translation_span')=='charity' for i in z['issues'])
    assert any(i.get('type')=='flattening' and i.get('source_span')=='الصدقة' and i.get('translation_span')=='zakat' for i in z['issues'])


def test_multi_error_article_returns_distinct_findings():
    ar=('الزكاة واجبة. والصدقة مستحبة. الوضوء شرط للصلاة. '
        'لا يجوز هذا إلا للضرورة. عدد الركعات ثلاث. السنة هدي النبي صلى الله عليه وسلم.')
    en=('Charity is obligatory. Zakat is obligatory. Wudu is required for prayer. '
        'This is not permissible. The number of rakahs is four. Sunnah is merely tradition.')
    z=r(ar,en)
    assert z['status']=='critical'
    assert any(i.get('type')=='exception' for i in z['issues'])
    assert any(i.get('type')=='quantity' for i in z['issues'])
    assert any(i.get('type')=='modality_shift' for i in z['issues'])
    assert any(i.get('type')=='terminology' and i.get('source_span')=='السنة' for i in z['issues'])
    assert any(i.get('type')=='flattening' and i.get('source_span')=='الزكاة' for i in z['issues'])
    assert any(i.get('type')=='flattening' and i.get('source_span')=='الصدقة' for i in z['issues'])
    assert len(z['issues'])>=6


def test_correct_multi_term_article_stays_clean():
    ar='الزكاة واجبة. والصدقة مستحبة. الوضوء شرط للصلاة. السنة هدي النبي صلى الله عليه وسلم.'
    en='Zakat is obligatory. Charity is recommended. Wudu is required for prayer. Sunnah is the Prophetic way.'
    z=r(ar,en)
    assert z['status']=='safe'
    assert not z['issues']


def test_quran_fragment_locator_and_condition_loss():
    z=analyze("وَإِنْ كُنْتُمْ جُنُبًا فَاطَّهَّرُوا", "Purify yourselves.", use_live_sources=False, use_semantic_ai=False)
    assert z["recognition"] and z["recognition"]["kind"]=="quran"
    assert z["recognition"]["match"]["surah"]==5 and z["recognition"]["match"]["ayah"]==6
    assert z["status"]=="critical"
    assert any(i.get("type")=="condition" for i in z["issues"])


def test_quran_fragment_correct_condition_is_safe():
    z=analyze("وَإِنْ كُنْتُمْ جُنُبًا فَاطَّهَّرُوا", "If you are in a state of major ritual impurity, then purify yourselves.", use_live_sources=False, use_semantic_ai=False)
    assert z["recognition"] and z["recognition"]["kind"]=="quran"
    assert z["status"]=="safe"
    assert not z["issues"]


def test_emphatic_inna_is_not_condition():
    z=analyze("إِنَّ اللَّهَ غَفُورٌ رَحِيمٌ", "Indeed, Allah is Forgiving and Merciful.", use_live_sources=False, use_semantic_ai=False)
    assert not any(i.get("type")=="condition" for i in z["issues"])
