from core.engine import analyze
from core import sources

AR='''1. ورد المرجع: سورة البقرة، الآية 183.\n\n2. ورد المرجع: سورة البقرة، الآية 183.\n\n3. ورد في الحديث: «إنما الأعمال بالنيات، وإنما لكل امرئ ما نوى»، والمصدر المشار إليه هو صحيح مسلم رقم 1907.'''
EN='''1. The reference is Surah Al-Baqarah, verse 183.\n\n2. The reference is Surah Al-Baqarah, verse 185.\n\n3. The hadith states: “Actions are but by intentions, and every person will have only what they intended,” and the referenced source is Sahih Muslim no. 1907.'''


def test_three_case_acceptance_has_only_changed_verse_issue_offline():
    r=analyze(AR,EN,use_live_sources=False,use_semantic_ai=False)
    assert len(r['issues'])==1
    assert r['issues'][0]['type']=='reference_identifier_changed'
    assert r['issues'][0]['issue_taxonomy']=='SOURCE_INTEGRITY'
    # local locators are not external verification
    assert r['reference_verification']['reference_verified'] is False
    assert r['reference_verification']['reference_text_retrieved'] is False


def test_explicit_quran_and_quoted_hadith_are_recognized_with_aligned_indices():
    r=analyze(AR,EN,use_live_sources=False,use_semantic_ai=False)
    recs=r['recognitions']
    assert [(x['segment_index'],x['recognition']['kind']) for x in recs]==[(1,'quran'),(2,'quran'),(3,'hadith')]
    assert recs[0]['recognition']['match']['surah']==2 and recs[0]['recognition']['match']['ayah']==183
    assert recs[2]['recognition']['match']['id']=='4560'


def test_hadith_equivalence_does_not_create_no_but_every_false_positives():
    ar='ورد في الحديث: «إنما الأعمال بالنيات، وإنما لكل امرئ ما نوى»، والمصدر المشار إليه هو صحيح مسلم رقم 1907.'
    en='The hadith states: “Actions are but by intentions, and every person will have only what they intended,” and the referenced source is Sahih Muslim no. 1907.'
    r=analyze(ar,en,use_live_sources=False,use_semantic_ai=False)
    assert r['issues']==[]


def test_live_routing_calls_quranenc_and_hadeethenc(monkeypatch):
    q_calls=[]; h_calls=[]
    def fake_q(surah,ayah,translation_key='english_saheeh'):
        q_calls.append((surah,ayah))
        return {'source':'QuranEnc','title':f'{surah}:{ayah}','detail':'reference text','reference':f'{surah}:{ayah}','url':'https://quranenc.test','status':'live_verified','evidence_type':'quran_translation','retrieved_at':'2026-10-06T00:00:00+00:00','verification':{'reference_verified':True,'source_text_retrieved':True,'user_translation_verified':False}}
    def fake_h(hid,language):
        h_calls.append((hid,language))
        return {'source':'HadeethEnc','title':f'#{hid}','detail':'hadith card','reference':hid,'url':'https://hadeethenc.test','status':'live_verified','evidence_type':'hadith_card','retrieved_at':'2026-10-06T00:00:00+00:00','verification':{'reference_verified':True,'source_text_retrieved':True,'user_translation_verified':False}}
    monkeypatch.setattr(sources,'fetch_quranenc',fake_q)
    monkeypatch.setattr(sources,'fetch_hadeethenc',fake_h)
    recs,evidence=sources.retrieve_reference_evidence_multi(AR,live=True)
    assert q_calls==[(2,183),(2,183)]
    assert ('4560','ar') in h_calls and ('4560','en') in h_calls
    assert all(x['segment_index'] in {1,2,3} for x in evidence)
    assert any(x.get('source')=='QuranEnc' and x.get('status')=='live_verified' for x in evidence)
    assert any(x.get('source')=='HadeethEnc' and x.get('status')=='live_verified' for x in evidence)


def test_failed_live_provider_never_becomes_live_verified(monkeypatch):
    def fail_q(surah,ayah,translation_key='english_saheeh'):
        return {'source':'QuranEnc','title':f'{surah}:{ayah}','detail':'failed','reference':f'{surah}:{ayah}','url':'x','status':'unavailable','evidence_type':'quran_translation','verification':{'reference_verified':False,'source_text_retrieved':False,'user_translation_verified':False}}
    monkeypatch.setattr(sources,'fetch_quranenc',fail_q)
    r=analyze('ورد المرجع: سورة البقرة، الآية 183.','The reference is Surah Al-Baqarah, verse 183.',use_live_sources=True,use_semantic_ai=False)
    assert r['reference_verification']['reference_verified'] is False
    assert r['reference_verification']['reference_text_retrieved'] is False
    assert r['status']=='review'
    assert r['abstain']['needed'] is True
