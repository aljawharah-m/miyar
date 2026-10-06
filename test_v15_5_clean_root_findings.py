import re
from pathlib import Path

from core.contextual_semantics import analyze_contextual_semantics
from core.engine import analyze, _mirror
from core.normalization import numbers
from core.sources import retrieve_reference_evidence_multi
from core.terminology import analyze_terminology


def issue_types(res):
    return [x.get('type') for x in res.get('issues', [])]


def issue_titles(res):
    return [x.get('title','') for x in res.get('issues', [])]


def test_multidigit_total_750_is_not_truncated():
    ar='دفع شخص 500 ريال ثم دفع 250 ريالًا إضافية فأصبح المجموع 750 ريالًا.'
    en='A person paid 500 SAR and later paid another 250 SAR, bringing the total to 700 SAR.'
    r=analyze_contextual_semantics(ar,en)
    x=next(i for i in r['issues'] if i['type']=='asserted_quantity_shift')
    assert x['source_span']=='750' and x['translation_span']=='700'
    assert '750' in x['explanation_ar'] and 'الأصل 00' not in x['explanation_ar']


def test_duration_30_days_is_not_truncated():
    ar='يجب الاحتفاظ بسجل القرار لمدة 30 يومًا على الأقل.'
    en='Decision logs only need to be retained for 3 days.'
    r=analyze_contextual_semantics(ar,en)
    x=next(i for i in r['issues'] if 'مدة الاحتفاظ' in i['title'])
    assert x['source_span'].startswith('30') and x['translation_span'].startswith('3')
    assert '30 يوم' in x['explanation_ar']


def test_numeric_literals_preserve_multidigit_decimal_sign_and_commas():
    vals=numbers('750 30 100 1000 10,000 -1 1.5 0.25 2.5%')
    for v in ['750','30','100','1000','10,000','1','1.5','0.25','2.5%']:
        assert v in vals


def test_date_token_does_not_create_partial_digits_in_contextual_result():
    ar='التاريخ 05/10/2026 قد يكون ملتبسًا بين تنسيقين.'
    en='The date 05/10/2026 definitely means May 10, 2026.'
    r=analyze_contextual_semantics(ar,en)
    assert 'date_ambiguity_overclaim' in issue_types(r)


def test_signed_number_relation_is_specific_root():
    r=analyze_contextual_semantics('العدد -1 يختلف عن 1.','-1 is the same as 1.')
    assert 'numeric_relation_reversal' in issue_types(r)


def test_decimal_relation_is_specific_root():
    r=analyze_contextual_semantics('الرقم 1.5 يختلف عن 15.','1.5 is equivalent to 15.')
    assert 'numeric_relation_reversal' in issue_types(r)


def test_percentage_bad_examples_do_not_replace_asserted_value():
    ar='المطلوب إخراج زكاة مقدارها 2.5 في المئة، فلا يجوز ترجمة الرقم إلى 25 في المئة أو 0.25 في المئة.'
    en='The required Zakat amount is 25 percent.'
    r=analyze_contextual_semantics(ar,en)
    x=next(i for i in r['issues'] if i['type']=='asserted_quantity_shift')
    assert x['source_span']=='2.5%' and x['translation_span']=='25%'


def test_time_period_remains_separate_from_generic_quantity():
    ar='يبدأ الموعد الساعة 9:00 صباحًا.'
    en='The appointment starts at 9:00 PM.'
    r=analyze_contextual_semantics(ar,en)
    assert 'time_period_shift' in issue_types(r)


def test_threshold_boundary_specific_root():
    ar='إذا كانت 70 في المئة بالضبط فلا يجوز افتراض أن أقل من 70 تشمل 70 نفسها.'
    en='A score of exactly 70 percent is considered below 70 percent.'
    r=analyze_contextual_semantics(ar,en)
    assert 'threshold_boundary_shift' in issue_types(r)


def test_and_or_is_specific_root():
    ar='يستطيع المتابعة إذا تحقق الشرطان أ و ب، وهذا يختلف عن أ أو ب.'
    en='The user may proceed if either condition A or condition B is fulfilled.'
    r=analyze_contextual_semantics(ar,en)
    assert 'logical_operator_shift' in issue_types(r)


def test_at_least_exactly_semantics_is_specific_root():
    ar='يجب التحقق من مصدر واحد على الأقل، ولا تعني واحدًا بالضبط ولا مصدرين على الأقل.'
    en='The user must verify at least two sources. At least one means exactly one.'
    r=analyze_contextual_semantics(ar,en)
    assert 'logical_cardinality_shift' in issue_types(r)


def test_event_order_and_causality_are_both_kept():
    ar='توضأ ثم صلى، وصلى لأنه توضأ.'
    en='He prayed and then performed Wudu. He performed Wudu because he had prayed.'
    r=analyze_contextual_semantics(ar,en)
    assert {'event_order_reversal','causality_reversal'} <= set(issue_types(r))


def test_actor_role_is_specific_root():
    ar='اتخذ المراجع القرار وليس النظام.'
    en='The system made the final decision, not the human reviewer.'
    r=analyze_contextual_semantics(ar,en)
    assert 'actor_role_inversion' in issue_types(r)


def test_source_attribution_is_specific_root():
    ar='وفقًا للمصدر الأول الحكم كذا، بينما المصدر الثاني يذكر تفصيلًا مختلفًا.'
    en='According to both sources, exactly the same ruling applies.'
    r=analyze_contextual_semantics(ar,en)
    assert 'source_attribution_collapse' in issue_types(r)


def test_pronoun_ambiguity_is_local_review_hint():
    ar='قال أحمد لخالد إنه سيعود، وقد يحتاج مرجع الضمير إلى تحليل السياق.'
    en='Ahmed told Khalid that Khalid would return.'
    r=analyze_contextual_semantics(ar,en)
    x=next(i for i in r['issues'] if i['type']=='pronoun_ambiguity')
    assert x.get('abstain_hint') is True


def test_unresolved_terminology_dictionary_miss_not_public_finding():
    z=analyze_terminology('النية تحتاج إلى فهم السياق.', 'The context must be understood.')
    assert not any(i.get('title','').startswith('مصطلح شرعي يحتاج تحققًا') for i in z['issues'])
    assert any('UNCERTAIN_TERMINOLOGY_EVIDENCE' in c.get('detail','') for c in z['checks'])


def test_meta_term_list_does_not_create_missing_term_findings():
    ar='هذه قائمة مصطلحات مثل النية والحديث والصلاة للاختبار.'
    en='This is a test list of religious terms.'
    z=analyze_terminology(ar,en)
    assert not any(i.get('translation_span')=='لا يوجد مقابل واضح' and i.get('type')=='terminology' for i in z['issues'])


def test_actual_risky_term_still_creates_public_finding():
    z=analyze_terminology('التوحيد أصل عظيم.', 'Oneness is an important principle.')
    assert any(i.get('type')=='flattening' and i.get('translation_span')=='oneness' for i in z['issues'])


def test_synthetic_test_identifier_is_not_external_recognition_candidate():
    ar='وفي مثال للاختبار بهذه الصيغة [HADITH_REF: TEST-123] أو [SOURCE_ID: ABC-001].'
    recs,ev=retrieve_reference_evidence_multi(ar,live=False)
    assert recs==[] and ev==[]


def test_explicit_reference_id_change_is_still_detected_locally():
    ar='[QURAN_REF: 2:183] [HADITH_REF: TEST-123] [SOURCE_ID: ABC-001]'
    en='[QURAN_REF: 2:185] [HADITH_REF: TEST-321] [SOURCE_ID: ABC-010]'
    r=analyze_contextual_semantics(ar,en)
    assert 'reference_identifier_changed' in issue_types(r)


def test_mirror_prefers_reference_fabrication_over_lower_impact_issue():
    issues=[
        {'type':'time_period_shift','severity':'high','confidence':.99,'source_span':'9 AM','translation_span':'9 PM','impact_ar':'time'},
        {'type':'source_fabrication_policy_shift','severity':'critical','confidence':.95,'source_span':'لا تختلق','translation_span':'insert reference','impact_ar':'source'},
    ]
    m=_mirror(issues)
    assert 'لا تختلق' in m['arabic_reader'] or 'source' in m['gap'] or 'مرجع' in (m['gap']+m['english_reader'])


def test_reference_change_suppresses_generic_quantity_in_full_engine():
    r=analyze('[QURAN_REF: 2:183]','[QURAN_REF: 2:185]',use_live_sources=False,use_semantic_ai=False)
    types=issue_types(r)
    assert 'reference_identifier_changed' in types
    assert 'quantity' not in types


def test_confidence_diagnostics_count_root_families_not_raw_signals():
    r=analyze('لا يجوز إلا في الضرورة.','It is permitted in cases of necessity.',use_live_sources=False,use_semantic_ai=False)
    c=r['diagnostics']['confidence']
    assert c['independent_evidence_count'] <= r['diagnostics']['root_issue_count']
    assert 'root-family' in c['policy']


def test_debug_trace_is_internal_diagnostics_not_public_issue_list():
    r=analyze('لا يجوز النشر.','Publication is permitted.',use_live_sources=False,use_semantic_ai=False)
    assert isinstance(r['diagnostics'].get('debug_trace'),list)
    assert all('detector' in x and 'confidence' in x for x in r['diagnostics']['debug_trace'])


def test_terminology_dedup_same_span():
    r=analyze('التوحيد ليس مجرد oneness.','Tawhid means oneness.',use_live_sources=False,use_semantic_ai=False)
    keys=[(i.get('type'),i.get('source_span'),i.get('translation_span')) for i in r['issues']]
    assert len(keys)==len(set(keys))


def test_number_roles_do_not_confuse_days_and_people_in_contextual_roots():
    ar='حضر 3 أشخاص، ويجب الاحتفاظ بالسجل 30 يومًا.'
    en='Three people attended, and the log must be retained for 3 days.'
    r=analyze_contextual_semantics(ar,en)
    x=[i for i in r['issues'] if 'مدة الاحتفاظ' in i.get('title','')]
    assert x and x[0]['source_span'].startswith('30') and x[0]['translation_span'].startswith('3')


def test_no_malformed_numeric_explanations_in_long_acceptance_pairs():
    txt=Path('evaluation/USER_LONG_STRESS_ALIGNMENT.txt').read_text(encoding='utf-8')
    ars=[]; ens=[]
    for line in txt.splitlines():
        m=re.match(r'\[\d+\] AR: (.*)',line)
        if m: ars.append(m.group(1))
        m=re.match(r'\[\d+\] EN: (.*)',line)
        if m: ens.append(m.group(1))
    assert len(ars)==len(ens)==45
    r=analyze('\n\n'.join(ars),'\n\n'.join(ens),use_live_sources=False,use_semantic_ai=False)
    explanations='\n'.join(i.get('explanation_ar','') for i in r['issues'])
    assert 'الأصل 00' not in explanations
    assert 'الأصل يطلب 0 يوم' not in explanations
    assert not any(i.get('title','').startswith('مصطلح شرعي يحتاج تحققًا') for i in r['issues'])
    assert not any(i.get('translation_span')=='لا يوجد مقابل واضح' and i.get('type')=='terminology' for i in r['issues'])


def test_long_acceptance_keeps_alignment_45_pairs():
    txt=Path('evaluation/USER_LONG_STRESS_ALIGNMENT.txt').read_text(encoding='utf-8')
    ars=[m.group(1) for m in map(lambda l: re.match(r'\[\d+\] AR: (.*)',l),txt.splitlines()) if m]
    ens=[m.group(1) for m in map(lambda l: re.match(r'\[\d+\] EN: (.*)',l),txt.splitlines()) if m]
    r=analyze('\n\n'.join(ars),'\n\n'.join(ens),use_live_sources=False,use_semantic_ai=False)
    assert r['alignment'].get('units', r['alignment'].get('pair_count'))==45
