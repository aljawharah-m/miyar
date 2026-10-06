from core.normalization import numbers
from core.rules import analyze_rules
from core.advanced_semantics import analyze_provenance, analyze_reference_conflicts


def _types(r):
    return {i.get('type') for i in r.get('issues', [])}


def _ref(ar, en, detail, kind='quran'):
    rec=[{'segment_index':1,'recognition':{'kind':kind}}]
    ev=[{'segment_index':1,'status':'live_verified','evidence_type':'quran_translation' if kind=='quran' else 'hadith_translation','language':'en','detail':detail}]
    return analyze_reference_conflicts(ar,en,rec,ev)


def test_neither_nor_preserves_two_arabic_negations():
    r=analyze_rules('لَمْ يَلِدْ وَلَمْ يُولَدْ.','He neither begets nor is born.')
    assert not any(i.get('type')=='negation' for i in r['issues'])


def test_is_but_preserves_arabic_exclusivity():
    r=analyze_rules('وَمَا مُحَمَّدٌ إِلَّا رَسُولٌ.','Muhammad is but a messenger.')
    assert not any(i.get('type')=='exception' for i in r['issues'])


def test_should_not_preserves_prohibition():
    r=analyze_rules('لا يجوز نسبة كلام إلى النبي بلا تثبت.','Statements should not be attributed to the Prophet without verification.')
    assert not any(i.get('type') in {'negation','prohibition'} for i in r['issues'])


def test_negated_authentic_hadith_is_not_positive_provenance_claim():
    r=analyze_provenance('هذا النص لم يثبت أنه حديث صحيح.','This text has not been established here as an authentic hadith.')
    assert not r['issues']


def test_one_third_is_single_quantity():
    assert numbers('One third of the money is allocated for this purpose.') == ['1/3']
    r=analyze_rules('يُخصّص ثلث المال لهذا الغرض.','One third of the money is allocated for this purpose.')
    assert not any(i.get('type')=='quantity' for i in r['issues'])


def test_reference_not_but_and_is_but_are_equivalent():
    r=_ref('وَمَا مُحَمَّدٌ إِلَّا رَسُولٌ.','Muhammad is but a messenger.','Muhammad is not but a messenger. Other messengers have passed on before him.')
    assert not r['issues']


def test_reference_alignment_uses_matching_clause_not_rest_of_full_verse():
    detail=('O you who have believed, when you rise to prayer, wash your faces. '
            'And if you are in a state of janabah, then purify yourselves. '
            'But if you are ill and do not find water, then seek clean earth.')
    r=_ref('وَإِنْ كُنْتُمْ جُنُبًا فَاطَّهَّرُوا.','If you are in a state of janabah, then purify yourselves.',detail)
    assert not r['issues']


def test_reference_real_negation_contradiction_still_caught():
    r=_ref('لَمْ يَلِدْ وَلَمْ يُولَدْ.','He has children and was born.','He neither begets nor is born.')
    assert 'reference_contradiction' in _types(r)


def test_reference_one_among_many_still_caught():
    r=_ref('قُلْ هُوَ اللَّهُ أَحَدٌ.','Say: He is Allah, one among many gods.','Say, He is Allah, One.')
    assert 'reference_contradiction' in _types(r)
