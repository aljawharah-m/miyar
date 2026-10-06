from core.engine import analyze


def _issues(ar, en):
    return analyze(ar, en, use_live_sources=False, use_semantic_ai=False)["issues"]


def test_ikhlas_one_among_several_is_caught_without_live_provider():
    issues=_issues('«قل هو الله أحد».','“Say: Allah is one among several gods.”')
    assert len(issues)==1
    assert issues[0]['type']=='sacred_semantic_reversal'
    assert issues[0]['issue_taxonomy']=='RELIGIOUS_SEMANTIC'
    assert issues[0]['religious_impact']=='high'


def test_correct_ikhlas_paraphrase_stays_clean():
    assert _issues('«قل هو الله أحد».','“Say: He is Allah, the One.”') == []


def test_explicit_hadith_context_fuses_must_always_speak_to_one_root():
    issues=_issues('قال رسول الله صلى الله عليه وسلم: «فليقل خيرًا أو ليصمت».',
                   'The Prophet Muhammad said: “He must always speak.”')
    assert len(issues)==1
    assert issues[0]['type']=='sacred_semantic_reversal'
    assert issues[0]['religious_impact']=='high'


def test_hadith_source_fabrication_variant_is_reference_root():
    issues=_issues('إذا لم يمكن التحقق من مصدر الحديث فلا يُختلق مصدر بديل.',
                   'If the hadith source cannot be verified, a plausible alternative source may be inserted.')
    assert len(issues)==1
    assert issues[0]['type']=='source_fabrication_policy_shift'
    assert issues[0]['issue_taxonomy']=='SOURCE_INTEGRITY'
    assert issues[0]['religious_impact']=='high'


def test_safe_hadith_source_abstention_variant_stays_clean():
    assert _issues('إذا لم يمكن التحقق من مصدر الحديث فلا يُختلق مصدر بديل.',
                   'If the hadith source cannot be verified, no alternative source should be fabricated.') == []
