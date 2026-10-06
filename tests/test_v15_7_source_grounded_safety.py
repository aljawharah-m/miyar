from core.engine import analyze
from core import sources


def test_quranenc_metadata_preserves_version_when_upstream_provides_it(monkeypatch):
    class R:
        ok=True; status_code=200
        def raise_for_status(self): pass
        def json(self):
            if 'translations/list' in self.url:
                return [{'key':'english_saheeh','language_iso_code':'en','version':'1.2.3','last_update':'2026-01-01','title':'English Saheeh'}]
            return {'translation':'Reference translation'}
    def fake_get(url,timeout=None):
        r=R(); r.url=url; return r
    sources.fetch_quranenc_translation_metadata.cache_clear()
    monkeypatch.setattr(sources.requests,'get',fake_get)
    ev=sources.fetch_quranenc(2,183,'english_saheeh')
    assert ev['source_version']=='1.2.3'
    assert ev['translation_key']=='english_saheeh'
    assert ev['retrieved_at']
    assert ev['verification']['reference_verified'] is True
    assert ev['verification']['user_translation_verified'] is False


def test_hadeethenc_does_not_invent_version(monkeypatch):
    class R:
        def raise_for_status(self): pass
        def json(self): return {'hadeeth':'Hadith text','grade':'Sahih','reference':'Bukhari'}
    monkeypatch.setattr(sources.requests,'get',lambda *a,**k:R())
    ev=sources.fetch_hadeethenc('123','en')
    assert ev['source_version'] is None
    assert ev['retrieved_at']
    assert ev['verification']['reference_verified'] is True
    assert ev['verification']['user_translation_verified'] is False


def test_synthetic_ids_are_not_sent_to_external_recognition(monkeypatch):
    called=[]
    monkeypatch.setattr(sources,'recognize_source',lambda text,live=True: called.append(text) or None)
    text='وفي هذا المثال التجريبي [HADITH_REF: TEST-123] و [SOURCE_ID: ABC-001] بهذه الصيغة.'
    recs, evidence=sources.retrieve_reference_evidence_multi(text,live=True)
    assert called==[]
    assert recs==[] and evidence==[]


def test_recommended_sources_are_not_used_evidence_without_retrieval():
    r=analyze('هذا حكم فقهي تجريبي.','This is an experimental legal statement.',use_live_sources=False,use_semantic_ai=False)
    used={x.get('source') for x in r['evidence_used']}
    suggested={x.get('source') for x in r['suggested_sources']}
    assert 'الدرر السنية — الموسوعة الفقهية' not in used
    assert 'الموسوعة الفقهية الكويتية' not in used
    assert suggested


def test_every_public_issue_has_taxonomy_and_religious_impact():
    r=analyze('هذا الفعل جائز ولا يصح نقله بما يفيد أنه واجب.','This action is mandatory.',use_live_sources=False,use_semantic_ai=False)
    assert r['issues']
    for x in r['issues']:
        assert x['issue_taxonomy'] in {'RELIGIOUS_SEMANTIC','GENERAL_SEMANTIC','LOGIC_NUMERIC','SOURCE_INTEGRITY','EPISTEMIC'}
        assert x['religious_impact'] in {'none','medium','high'}
        assert x['boundary_note_ar']


def test_ruling_transfer_is_religious_semantic_not_fatwa_validation():
    r=analyze('إذا قيل إن فعلًا ما جائز فلا يصح نقله بما يفيد أنه واجب.','If an action is permissible, it may be translated as obligatory.',use_live_sources=False,use_semantic_ai=False)
    roots=[x for x in r['issues'] if x.get('type')=='ruling_degree_shift']
    assert roots
    assert roots[0]['issue_taxonomy']=='RELIGIOUS_SEMANTIC'
    assert roots[0]['religious_impact']=='high'
    assert 'ليس بإصدار حكم شرعي جديد' in roots[0]['boundary_note_ar']


def test_logic_numeric_can_have_religious_impact_without_becoming_religious_taxonomy():
    r=analyze('في الحكم الشرعي يشترط تحقق الشرطين أ و ب معًا.','For the religious ruling, condition A or condition B is enough.',use_live_sources=False,use_semantic_ai=False)
    roots=[x for x in r['issues'] if x.get('type') in {'logical_operator_shift','condition_gate_shift'}]
    if roots:
        assert roots[0]['issue_taxonomy'] in {'LOGIC_NUMERIC','GENERAL_SEMANTIC'}
        assert roots[0]['religious_impact'] in {'medium','high'}


def test_reference_verification_is_distinct_from_user_translation_verification():
    r=analyze('نص عام','General text',use_live_sources=False,use_semantic_ai=False)
    assert r['reference_verification']['user_translation_verified'] is False
    assert 'لا يعني' in r['reference_verification']['note_ar']
