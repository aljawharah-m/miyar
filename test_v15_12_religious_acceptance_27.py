from core.engine import analyze


def run(a,e):
    return analyze(a,e,use_live_sources=False,use_semantic_ai=False)


def types(r):
    return {i.get('type') for i in r['issues']}


def test_direct_ruling_transfers():
    cases=[
        ('يذكر النص أن هذا الفعل جائز.','The text states that this action is obligatory.'),
        ('يذكر النص أن هذا الفعل مستحب.','The text states that this action is mandatory.'),
        ('يذكر النص أن هذا الفعل محرم.','The text states that this action is merely not preferred.'),
    ]
    for a,e in cases:
        r=run(a,e)
        assert 'modality_shift' in types(r)
        issue=next(i for i in r['issues'] if i['type']=='modality_shift')
        assert issue['issue_taxonomy']=='RELIGIOUS_SEMANTIC'
        assert issue['religious_impact']=='high'


def test_direct_ruling_preserved_is_safe():
    assert run('يذكر النص أن هذا الفعل مستحب.','The text states that this action is recommended.')['issues']==[]


def test_tawhid_definition_flattening_and_safe_tawhid():
    bad=run('التوحيد مصطلح شرعي له دلالة محددة في السياق الإسلامي.','Tawhid simply means general oneness.')
    assert 'flattening' in types(bad)
    good=run('من أصول الاعتقاد الإسلامي التوحيد.','Tawhid is one of the foundations of Islamic belief.')
    assert good['issues']==[]


def test_reference_locator_and_source_fabrication():
    changed=run('ورد المرجع: سورة البقرة، الآية 183.','The reference is Surah Al-Baqarah, verse 185.')
    x=next(i for i in changed['issues'] if i['type']=='reference_identifier_changed')
    assert x['issue_taxonomy']=='SOURCE_INTEGRITY' and x['religious_impact']=='high'
    same=run('ورد المرجع: سورة البقرة، الآية 183.','The reference is Surah Al-Baqarah, verse 183.')
    assert not any(i['type']=='reference_identifier_changed' for i in same['issues'])
    fab=run('إذا تعذر التحقق من المرجع فيجب التصريح بعدم القدرة على التحقق، ولا يجوز اختلاق مرجع بديل.','If the reference cannot be verified, another reliable-looking religious reference may be inserted.')
    assert 'source_fabrication_policy_shift' in types(fab)


def test_synthetic_identifier_and_authenticity_claim():
    changed=run('[HADITH_REF: TEST-123] معرّف تجريبي مخصص للاختبار.','[HADITH_REF: TEST-321] is a test identifier.')
    x=next(i for i in changed['issues'] if i['type']=='reference_identifier_changed')
    assert x['religious_impact']=='none'
    fake=run('[HADITH_REF: TEST-123] معرّف تجريبي للاختبار وليس حديثًا موثقًا.','[HADITH_REF: TEST-123] is a verified authentic Hadith source.')
    assert 'provenance_claim_shift' in types(fake)


def test_target_side_religious_additions():
    consensus=run('ذكر النص هذا الرأي دون أن يدعي وجود إجماع عليه.','All scholars unanimously agree with this opinion and there is no disagreement.')
    x=next(i for i in consensus['issues'] if i['type']=='unsupported_addition_policy_shift')
    assert x['religious_impact']=='high'
    rel=run('لا يجوز إضافة استنتاجات لم يذكرها النص الأصلي.','The translator may add reasonable religious conclusions even if they do not appear in the source text.')
    x=next(i for i in rel['issues'] if i['type']=='unsupported_addition_policy_shift')
    assert x['religious_impact']=='high'


def test_generic_forbidden_addition_not_automatically_religious():
    r=run('يذكر النص أن هذا الأمر يحتاج إلى مراجعة.','The text states that this is absolutely forbidden.')
    x=next(i for i in r['issues'] if i['type']=='unsupported_addition_policy_shift')
    assert x['religious_impact']=='none'


def test_condition_numeric_epistemic_and_abstention():
    cond=run('يذكر النص أن قبول العمل مرتبط بتحقق الشرط المذكور.','The action is accepted whether or not the stated condition is fulfilled.')
    assert 'condition_gate_shift' in types(cond)
    zakat=run('يذكر النص مقدارًا قدره 2.5 في المئة في سياق الزكاة.','The text states that the Zakat amount is 25 percent.')
    x=next(i for i in zakat['issues'] if i['type']=='asserted_quantity_shift')
    assert x['issue_taxonomy']=='LOGIC_NUMERIC' and x['religious_impact']=='high'
    general=run('بلغ المجموع 750 ريالًا.','The total was 700 SAR.')
    x=next(i for i in general['issues'] if i['type']=='quantity')
    assert x['issue_taxonomy']=='LOGIC_NUMERIC' and x['religious_impact']=='none'
    epi=run('الأدلة المتاحة لا تكفي للجزم بصحة الادعاء.','The available evidence proves the claim with certainty.')
    assert 'uncertainty_to_certainty' in types(epi)
    abst=run('إذا تعارضت المصادر أو لم يتضح السياق فيجب طلب مراجعة بشرية وعدم إصدار قرار نهائي.','If the sources conflict or the context is unclear, the system should still issue a definitive answer.')
    assert 'abstention_policy_shift' in types(abst)


def test_order_causality_and_safe_paraphrase():
    assert 'event_order_reversal' in types(run('توضأ الشخص ثم صلى.','The person prayed and then performed Wudu.'))
    assert 'causality_reversal' in types(run('يقول النص إنه صلى لأنه توضأ.','The text says he performed Wudu because he prayed.'))
    assert run('توضأ أحمد قبل أن يصلي.','Before praying, Ahmad performed Wudu.')['issues']==[]


def test_numbered_safe_case_does_not_create_quantity_false_positive():
    r=run('26. من أصول الاعتقاد الإسلامي التوحيد.','26. Tawhid is one of the foundations of Islamic belief.')
    assert not any(i.get('type')=='quantity' for i in r['issues'])
    assert r['issues']==[]


def test_exclusivity_case_is_one_clean_root():
    r=run('لا يجوز هذا الفعل إلا في حالة الضرورة.','This action is permitted in cases of necessity.')
    assert len(r['issues'])==1
    assert r['issues'][0]['type']=='ruling_polarity_shift'
