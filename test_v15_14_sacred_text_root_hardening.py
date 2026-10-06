import core.engine as eng
from core.engine import analyze

AR_NAT='''1. «قل هو الله أحد».\n\n2. «قل هو الله أحد».\n\n3. «شهر رمضان الذي أنزل فيه القرآن».\n\n4. «شهر رمضان الذي أنزل فيه القرآن».\n\n5. قال رسول الله صلى الله عليه وسلم: «إنما الأعمال بالنيات، وإنما لكل امرئ ما نوى».\n\n6. قال رسول الله صلى الله عليه وسلم: «إنما الأعمال بالنيات، وإنما لكل امرئ ما نوى».\n\n7. قال رسول الله صلى الله عليه وسلم: «من كان يؤمن بالله واليوم الآخر فليقل خيرًا أو ليصمت».\n\n8. قال رسول الله صلى الله عليه وسلم: «من كان يؤمن بالله واليوم الآخر فليقل خيرًا أو ليصمت».\n\n9. «لا إكراه في الدين».\n\n10. «لا إكراه في الدين».\n\n11. «إن الله مع الصابرين».\n\n12. «إن الله مع الصابرين».'''
EN_NAT='''1. “Say: He is Allah, the One.”\n\n2. “Say: Allah is one of several gods.”\n\n3. “The month of Ramadan is the month in which the Qur’an was revealed.”\n\n4. “The Qur’an was not revealed in Ramadan.”\n\n5. The Prophet Muhammad said: “Actions are but by intentions, and every person will have only what they intended.”\n\n6. The Prophet Muhammad said: “Intentions do not affect actions.”\n\n7. The Prophet Muhammad said: “Whoever believes in Allah and the Last Day should say what is good or remain silent.”\n\n8. The Prophet Muhammad said: “Whoever believes in Allah and the Last Day must always speak.”\n\n9. “There is no compulsion in religion.”\n\n10. “People must be forced into religion.”\n\n11. “Indeed, Allah is with the patient.”\n\n12. “Allah is not with the patient.”'''


def _fake_refs(ar, live=True):
    # Enough authoritative English evidence to exercise the source-grounded path.
    refs={
      1:('quran','Say: He is Allah, the One.'),2:('quran','Say: He is Allah, the One.'),
      3:('quran','The month of Ramadan in which the Quran was revealed.'),4:('quran','The month of Ramadan in which the Quran was revealed.'),
      5:('hadith','Actions are but by intentions, and every person will have only what they intended.'),6:('hadith','Actions are but by intentions, and every person will have only what they intended.'),
      7:('hadith','Whoever believes in Allah and the Last Day should say what is good or remain silent.'),8:('hadith','Whoever believes in Allah and the Last Day should say what is good or remain silent.'),
      9:('quran','There is no compulsion in religion.'),10:('quran','There is no compulsion in religion.'),
      11:('quran','Indeed, Allah is with the patient.'),12:('quran','Indeed, Allah is with the patient.'),
    }
    recs=[]; ev=[]
    for idx,(kind,detail) in refs.items():
        match={'score':1.0,'method':'test'}
        if kind=='quran': match.update({'surah':1,'ayah':idx})
        else: match.update({'id':str(idx)})
        recs.append({'segment_index':idx,'text':'x','recognition':{'kind':kind,'confidence':'high','match':match}})
        ev.append({'source':'QuranEnc' if kind=='quran' else 'HadeethEnc','segment_index':idx,'status':'live_verified','detail':detail,'evidence_type':'quran_translation' if kind=='quran' else 'hadith_translation','language':'en','verification':{'reference_verified':True,'source_text_retrieved':True,'user_translation_verified':False}})
    return recs,ev


def test_natural_quran_hadith_acceptance_with_authoritative_refs(monkeypatch):
    monkeypatch.setattr(eng,'retrieve_reference_evidence_multi',_fake_refs)
    r=analyze(AR_NAT,EN_NAT,use_live_sources=True,use_semantic_ai=False)
    assert len(r['issues'])==6, [(x.get('segment_index'),x.get('type'),x.get('title')) for x in r['issues']]
    assert {x['segment_index'] for x in r['issues']}=={2,4,6,8,10,12}
    assert all(x['religious_impact']=='high' for x in r['issues'])
    assert not ({1,3,5,7,9,11} & {x['segment_index'] for x in r['issues']})


def test_generic_surah_reference_is_reference_not_quantity():
    r=analyze('ورد في سورة الإخلاص، الآية 1: «قل هو الله أحد».','Surah Al-Ikhlas, verse 2 states: “Say: He is Allah, the One.”',use_live_sources=False,use_semantic_ai=False)
    assert len(r['issues'])==1
    assert r['issues'][0]['issue_taxonomy']=='SOURCE_INTEGRITY'
    assert r['issues'][0]['type']=='reference_identifier_changed'


def test_hadith_source_fabrication_root():
    ar='إذا تعذر التحقق من الحديث في المصدر المشار إليه فيجب التصريح بعدم القدرة على التحقق وعدم اختلاق مصدر بديل.'
    en='If the hadith cannot be verified in the referenced source, another reliable-looking hadith source may be inserted.'
    r=analyze(ar,en,use_live_sources=False,use_semantic_ai=False)
    assert len(r['issues'])==1
    assert r['issues'][0]['type']=='source_fabrication_policy_shift'
    assert r['issues'][0]['issue_taxonomy']=='SOURCE_INTEGRITY'
    assert r['issues'][0]['religious_impact']=='high'


def test_recognized_quran_generic_negation_has_high_religious_impact():
    r=analyze('«إن الله مع الصابرين».','“Allah is not with the patient.”',use_live_sources=False,use_semantic_ai=False)
    assert len(r['issues'])==1
    assert r['issues'][0]['religious_impact']=='high'
    assert r['issues'][0].get('recognized_source_kind')=='quran'
