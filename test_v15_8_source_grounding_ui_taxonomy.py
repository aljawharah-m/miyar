from core.engine import analyze
from core import engine, sources


def test_ruling_and_terminology_have_distinct_subtypes_and_reasons():
    r=analyze('إذا قيل إن فعلًا ما جائز فلا يصح نقله بما يفيد أنه واجب.','If an action is permissible, it may be translated as obligatory.',use_live_sources=False,use_semantic_ai=False)
    roots=[x for x in r['issues'] if x.get('type')=='ruling_degree_shift']
    assert roots and roots[0]['issue_subtype']=='RULING_TRANSFER_DRIFT'
    assert roots[0]['religious_impact']=='high'
    assert 'ينقل درجة الحكم' in roots[0]['religious_impact_reason']

    r=analyze('التوحيد','oneness',use_live_sources=False,use_semantic_ai=False)
    roots=[x for x in r['issues'] if x.get('issue_taxonomy')=='RELIGIOUS_SEMANTIC']
    assert roots and roots[0]['issue_subtype']=='RELIGIOUS_TERMINOLOGY_DRIFT'
    assert 'مصطلح إسلامي' in roots[0]['religious_impact_reason']


def test_general_numeric_has_no_direct_religious_impact():
    r=analyze('أصبح المجموع 750 ريالًا.','The total became 700 SAR.',use_live_sources=False,use_semantic_ai=False)
    nums=[x for x in r['issues'] if x.get('issue_taxonomy')=='LOGIC_NUMERIC']
    if nums:
        assert nums[0]['religious_impact']=='none'


def test_zakat_numeric_can_keep_numeric_taxonomy_with_high_religious_impact():
    r=analyze('مقدار الزكاة المطلوب 2.5 في المئة ولا يجوز نقله إلى 25 في المئة.','The required Zakat amount is 25 percent.',use_live_sources=False,use_semantic_ai=False)
    nums=[x for x in r['issues'] if x.get('issue_taxonomy')=='LOGIC_NUMERIC']
    if nums:
        assert any(x['religious_impact']=='high' for x in nums)


def test_taxonomy_breakdown_matches_public_issue_count():
    r=analyze('إذا قيل إن فعلًا ما جائز فلا يصح نقله بما يفيد أنه واجب.','If an action is permissible, it may be translated as obligatory.',use_live_sources=False,use_semantic_ai=False)
    b=r['diagnostics']['taxonomy_breakdown']
    assert sum(x['count'] for x in b.values())==len(r['issues'])


def test_public_issue_has_evidence_provenance_contract():
    r=analyze('إذا قيل إن فعلًا ما جائز فلا يصح نقله بما يفيد أنه واجب.','If an action is permissible, it may be translated as obligatory.',use_live_sources=False,use_semantic_ai=False)
    assert r['issues']
    p=r['issues'][0]['evidence_provenance']
    assert p['detector']
    assert p['aligned_pair'] is not None
    assert p['timestamp']
    assert 'confidence' in p and 'suppression_history' in p


def test_reference_identifier_trace_keeps_independent_sub_evidence():
    ar='وفي هذا المثال التجريبي [QURAN_REF: 2:183] أو [HADITH_REF: TEST-123] أو [SOURCE_ID: ABC-001] فلا يجوز تغييرها.'
    en='[QURAN_REF: 2:185] [HADITH_REF: TEST-321] [SOURCE_ID: ABC-010] All identifiers may be changed.'
    r=analyze(ar,en,use_live_sources=False,use_semantic_ai=False)
    roots=[x for x in r['issues'] if x.get('type')=='reference_identifier_changed']
    assert roots and len(roots[0].get('sub_evidence',[]))==3
    states={x['kind']:x['reference_state'] for x in roots[0]['sub_evidence']}
    assert states['HADITH_REF']=='synthetic' and states['SOURCE_ID']=='synthetic'
    assert states['QURAN_REF']=='changed'


def test_synthetic_ids_external_calls_zero(monkeypatch):
    calls=[]
    monkeypatch.setattr(sources,'recognize_source',lambda *a,**k: calls.append(1) or None)
    rec,evidence=sources.retrieve_reference_evidence_multi('مثال تجريبي [HADITH_REF: TEST-123] و [SOURCE_ID: ABC-001].',live=True)
    assert calls==[] and rec==[] and evidence==[]


def test_live_source_failure_abstains_instead_of_fabricating(monkeypatch):
    recognition={'kind':'quran','match':{'surah':2,'ayah':183,'score':1.0}}
    monkeypatch.setattr(engine,'retrieve_reference_evidence_multi',lambda ar,live=True: ([{'segment_index':1,'text':ar,'recognition':recognition}],[{'source':'QuranEnc','status':'unavailable','segment_index':1,'detail':'failed','verification':{'reference_verified':False,'source_text_retrieved':False,'user_translation_verified':False}}]))
    r=engine.analyze('نص قرآني معروف','A translated verse',use_live_sources=True,use_semantic_ai=False)
    assert r['status']=='review'
    assert r['abstain']['needed'] is True


def test_recommended_source_never_becomes_used_evidence_without_retrieval():
    r=analyze('مسألة فقهية عامة','A general fiqh statement',use_live_sources=False,use_semantic_ai=False)
    assert all(x.get('status')!='recommended' for x in r['evidence_used'])
    assert any(x.get('status')=='recommended' for x in r['suggested_sources'])


def test_synthetic_reference_finding_is_not_marked_as_religious_source():
    ar='وفي هذا المثال التجريبي [QURAN_REF: 2:183] و [HADITH_REF: TEST-123] و [SOURCE_ID: ABC-001] فلا يجوز تغييرها.'
    en='[QURAN_REF: 2:185] [HADITH_REF: TEST-321] [SOURCE_ID: ABC-010]'
    r=analyze(ar,en,use_live_sources=False,use_semantic_ai=False)
    root=next(x for x in r['issues'] if x.get('type')=='reference_identifier_changed')
    assert root['reference_state']=='mixed'
    assert root['religious_impact']=='high'
    states={x['kind']:x['reference_state'] for x in root['sub_evidence']}
    assert states['QURAN_REF']=='changed'
    assert states['HADITH_REF']=='synthetic' and states['SOURCE_ID']=='synthetic'


def test_conflicting_source_evidence_forces_human_review(monkeypatch):
    recognition={'kind':'quran','match':{'surah':2,'ayah':183,'score':1.0}}
    evidence=[{'source':'QuranEnc','status':'conflicting','segment_index':1,'detail':'conflicting provider evidence','verification':{'reference_verified':True,'source_text_retrieved':True,'user_translation_verified':False,'conflict':True}}]
    monkeypatch.setattr(engine,'retrieve_reference_evidence_multi',lambda ar,live=True: ([{'segment_index':1,'text':ar,'recognition':recognition}],evidence))
    r=engine.analyze('نص قرآني','A translation',use_live_sources=True,use_semantic_ai=False)
    assert r['status']=='review'
    assert r['reference_verification']['source_conflict'] is True
    assert 'تعارضت أدلة المصادر' in r['decision_reason']


def test_public_ui_contains_taxonomy_impact_and_verification_labels():
    from pathlib import Path
    app=Path('app.py').read_text(encoding='utf-8')
    for marker in ['الأثر الديني:', 'ما الذي تحقق منه مِعيار؟', 'المرجع: تم التحقق', 'الترجمة: قيد التقييم', 'صحة الحكم الشرعي الأصلي']:
        assert marker in app
