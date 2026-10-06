from core.alignment import aligned_pairs
from core.engine import analyze
import core.recognition as recognition


def run(ar,en):
    return analyze(ar,en,use_live_sources=False,use_semantic_ai=False)


def test_single_arabic_unit_split_english_has_no_empty_alignment_pair():
    ar='قال رسول الله صلى الله عليه وسلم: «بلغوا عني ولو آية، وحدثوا عن بني إسرائيل ولا حرج، ومن كذب علي متعمدًا فليتبوأ مقعده من النار».'
    en='Convey from me, even if one verse. Narrate from the Children of Israel, and there is no harm; whoever deliberately lies about me, let him take his seat in Hellfire.'
    pairs, mode=aligned_pairs(ar,en)
    assert len(pairs)==1
    assert pairs[0][1].strip()
    assert pairs[0][2].strip()
    assert mode=='single_ar_grouped_en'


def test_short_quran_quote_is_recognized_inside_natural_wrapper():
    r=recognition.recognize_quran('قال الله تعالى: «الم»',live=False)
    assert r is not None
    assert any((int(x.get('surah',0)),int(x.get('ayah',0)))==(2,1) for x in ([r] if not r.get('ambiguous') else r.get('candidates',[])))


def test_embedded_quran_text_is_safe_ambiguous_not_overclaimed():
    r=recognition.recognize_quran('«الله لا إله إلا هو الحي القيوم»',live=False)
    assert r is not None
    assert r.get('ambiguous') is True
    locs={(int(x['surah']),int(x['ayah'])) for x in r.get('candidates',[])}
    assert (3,2) in locs and (2,255) in locs


def test_hadeeth_search_considers_relevant_result_after_rank_15(monkeypatch):
    target='قال رسول الله صلى الله عليه وسلم: «هلك المتنطعون» قالها ثلاثا.'
    rows=[]
    for i in range(20):
        rows.append({'id':str(9000+i),'hadith_text':f'نص مختلف تماما للاختبار رقم {i} ولا يطابق الحديث','title':'غير مطابق'})
    rows.append({'id':'3420','hadith_text':target,'title':'هلك المتنطعون'})
    monkeypatch.setattr(recognition,'_hadeeth_search_live',lambda text: rows)
    r=recognition.recognize_hadith(target,live=True)
    assert r is not None
    assert r.get('id')=='3420'
    assert r.get('method')=='hadeethenc_search'


def test_no_god_but_allah_equivalence_is_safe():
    ar='قال رسول الله صلى الله عليه وسلم: «من قال لا إله إلا الله دخل الجنة».'
    en='The Prophet said: “Whoever says there is no god but Allah will enter Paradise.”'
    assert run(ar,en)['issues']==[]


def test_none_of_you_believes_equivalence_is_safe():
    ar='قال رسول الله صلى الله عليه وسلم: «لا يؤمن أحدكم حتى يحب لأخيه ما يحب لنفسه».'
    en='The Prophet said: “None of you truly believes until he loves for his brother what he loves for himself.”'
    assert run(ar,en)['issues']==[]
