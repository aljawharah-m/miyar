from pathlib import Path
import re
from core.engine import analyze, _mirror, _span_overlap


def types(r):
    return [x.get('type') for x in r.get('issues', [])]


def codes(r):
    return [x.get('root_code') or x.get('type') for x in r.get('issues', [])]


def test_numeric_date_paragraph_suppresses_generic_uncertainty_but_keeps_specific_roots():
    ar=('وفي الاختبارات الرقمية، العدد 0 لا يعني عدم وجود قيمة دائمًا، والعدد -1 يختلف عن 1، '
        'والرقم 1.5 يختلف عن 15، والتاريخ 05/10/2026 قد يكون ملتبسًا بين الخامس من أكتوبر '
        'والعاشر من مايو بحسب التنسيق، لذلك يجب الحفاظ على الصيغة أو توضيحها')
    en=('The number 0 always means that no value exists. -1 is the same as 1, and 1.5 is equivalent to 15. '
        'The date 05/10/2026 definitely means May 10, 2026.')
    r=analyze(ar,en,use_live_sources=False,use_semantic_ai=False)
    assert 'uncertainty_to_certainty' not in types(r)
    assert {'SIGNED_NUMBER_CONTRADICTION','DECIMAL_VALUE_CORRUPTION','DATE_AMBIGUITY_COLLAPSE'} <= set(codes(r))
    u=next(x for x in r['diagnostics']['debug_trace'] if x['type']=='uncertainty_to_certainty')
    assert u['suppressed_by']=='date_ambiguity_overclaim'
    assert u['merged_into']=='date_ambiguity_overclaim'


def test_true_semantic_uncertainty_is_not_suppressed():
    r=analyze('قد يكون هذا الرأي صحيحًا لكنه غير مؤكد.','This opinion is definitely correct.',use_live_sources=False,use_semantic_ai=False)
    assert 'uncertainty_to_certainty' in types(r)
    u=next(x for x in r['issues'] if x['type']=='uncertainty_to_certainty')
    assert u.get('root_code') in {None,'uncertainty_to_certainty'}


def test_backward_compatible_public_types_have_specific_root_codes():
    r=analyze('العدد -1 يختلف عن 1 والرقم 1.5 يختلف عن 15.','-1 is the same as 1 and 1.5 is equivalent to 15.',use_live_sources=False,use_semantic_ai=False)
    nums=[x for x in r['issues'] if x['type']=='numeric_relation_reversal']
    assert {x.get('root_code') for x in nums}=={'SIGNED_NUMBER_CONTRADICTION','DECIMAL_VALUE_CORRUPTION'}


def test_same_paragraph_independent_numeric_roots_are_not_merged():
    r=analyze('العدد -1 يختلف عن 1 والرقم 1.5 يختلف عن 15.','-1 is the same as 1 and 1.5 is equivalent to 15.',use_live_sources=False,use_semantic_ai=False)
    assert sum(x.get('type')=='numeric_relation_reversal' for x in r['issues'])==2


def test_event_order_and_causality_remain_two_roots_after_dedup():
    r=analyze('توضأ ثم صلى، وصلى لأنه توضأ.','He prayed and then performed Wudu. He performed Wudu because he had prayed.',use_live_sources=False,use_semantic_ai=False)
    assert {'event_order_reversal','causality_reversal'} <= set(types(r))


def test_three_ruling_shifts_remain_three_roots():
    ar=('إذا قيل إن فعلًا ما جائز فلا يصح نقله بما يفيد أنه واجب، وإذا قيل إنه مستحب فلا ينبغي '
        'ترجمته بما يفيد الإلزام، وإذا ورد أن أمرًا محرم فلا يجوز تخفيف العبارة إلى أنه غير مفضل فقط')
    en=('If an action is permissible, it may be translated as obligatory. A recommended action may be described '
        'as mandatory, while something prohibited can be translated as merely not preferred.')
    r=analyze(ar,en,use_live_sources=False,use_semantic_ai=False)
    roots=[x for x in r['issues'] if x.get('type')=='ruling_degree_shift']
    assert len(roots)>=3


def test_span_overlap_requires_actual_spans_not_just_same_paragraph():
    assert _span_overlap('-1 ≠ 1','1.5 ≠ 15') < .72
    assert _span_overlap('05/10/2026 ملتبس','05/10/2026 ملتبس بحسب التنسيق') >= .72


def test_mirror_uses_public_roots_only_not_suppressed_trace():
    ar='التاريخ 05/10/2026 قد يكون ملتبسًا بين تنسيقين.'
    en='The date 05/10/2026 definitely means May 10, 2026.'
    r=analyze(ar,en,use_live_sources=False,use_semantic_ai=False)
    assert 'uncertainty_to_certainty' not in types(r)
    assert '05/10/2026' in (r['meaning_mirror']['arabic_reader']+r['meaning_mirror']['english_reader']+r['meaning_mirror']['gap'])


def test_root_ranking_still_prefers_reference_fabrication_in_long_stress():
    txt=Path('evaluation/USER_LONG_STRESS_ALIGNMENT.txt').read_text(encoding='utf-8')
    ars=[m.group(1) for m in map(lambda l: re.match(r'\[\d+\] AR: (.*)',l),txt.splitlines()) if m]
    ens=[m.group(1) for m in map(lambda l: re.match(r'\[\d+\] EN: (.*)',l),txt.splitlines()) if m]
    r=analyze('\n\n'.join(ars),'\n\n'.join(ens),use_live_sources=False,use_semantic_ai=False)
    mirror=' '.join(r['meaning_mirror'].values())
    assert 'مرجع' in mirror or 'التحقق' in mirror


def test_long_stress_has_no_terminology_fallback_noise_and_no_malformed_numbers():
    txt=Path('evaluation/USER_LONG_STRESS_ALIGNMENT.txt').read_text(encoding='utf-8')
    ars=[m.group(1) for m in map(lambda l: re.match(r'\[\d+\] AR: (.*)',l),txt.splitlines()) if m]
    ens=[m.group(1) for m in map(lambda l: re.match(r'\[\d+\] EN: (.*)',l),txt.splitlines()) if m]
    r=analyze('\n\n'.join(ars),'\n\n'.join(ens),use_live_sources=False,use_semantic_ai=False)
    text='\n'.join((x.get('title','')+' '+x.get('explanation_ar','')) for x in r['issues'])
    assert 'مصطلح شرعي يحتاج تحققًا' not in text
    assert 'الأصل 00' not in text and not re.search(r'(?<!\d)0 يومًا على الأقل', text)


def test_repeated_analysis_is_stable_in_root_order_and_mirror():
    ar='قد يكون هذا الرأي صحيحًا. والعدد -1 يختلف عن 1.'
    en='This opinion is definitely correct. -1 is the same as 1.'
    a=analyze(ar,en,use_live_sources=False,use_semantic_ai=False)
    b=analyze(ar,en,use_live_sources=False,use_semantic_ai=False)
    ka=[(x.get('type'),x.get('root_code'),x.get('source_span'),x.get('translation_span')) for x in a['issues']]
    kb=[(x.get('type'),x.get('root_code'),x.get('source_span'),x.get('translation_span')) for x in b['issues']]
    assert ka==kb
    assert a['meaning_mirror']==b['meaning_mirror']


def test_debug_trace_exposes_semantic_family_and_suppression_fields():
    r=analyze('التاريخ 05/10/2026 قد يكون ملتبسًا.','The date 05/10/2026 definitely means May 10, 2026.',use_live_sources=False,use_semantic_ai=False)
    assert all('semantic_family' in x and 'suppressed_by' in x and 'merged_into' in x for x in r['diagnostics']['debug_trace'])
