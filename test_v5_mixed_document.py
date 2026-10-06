from core.engine import analyze
from core.corrections import build_high_confidence_correction

AR = """اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ.
وَإِنْ كُنْتُمْ جُنُبًا فَاطَّهَّرُوا.
إنما الأعمال بالنيات.
الزكاة واجبة.
يجوز فعل ذلك عند الحاجة.
لا يجوز هذا إلا في حالة الضرورة.
الوضوء شرط للصلاة.
الشريعة تشمل هداية وأحكامًا ولا تقتصر على العقوبات.
التوحيد أصل عظيم في الإسلام.
عدد الركعات هنا ثلاث ركعات."""

EN = """Allah is one god among many, the Ever-Living.
Purify yourselves.
Actions are judged by intentions.
Charity is obligatory.
It must be done when needed.
This is not permissible.
Wudu is required for prayer.
Sharia is criminal law.
Tawhid means oneness.
The number of rak'ahs here is four."""


def result():
    return analyze(AR, EN, use_live_sources=False, use_semantic_ai=False)


def test_mixed_document_recognizes_each_scriptural_segment():
    z=result()
    found=[(x["segment_index"],x["recognition"]["kind"]) for x in z["recognitions"]]
    assert (1,"quran") in found
    assert (2,"quran") in found
    assert (3,"hadith") in found


def test_mixed_document_quran_ambiguity_is_not_guessed():
    z=result()
    first=next(x for x in z["recognitions"] if x["segment_index"]==1)["recognition"]
    assert first["match"].get("ambiguous") is True
    refs={(x["surah"],x["ayah"]) for x in first["match"].get("candidates",[])}
    assert (2,255) in refs and (3,2) in refs


def test_mixed_document_issues_are_sentence_local():
    z=result()
    assert any(i.get("segment_index")==2 and i.get("type")=="condition" for i in z["issues"])
    assert any(i.get("segment_index")==5 and i.get("type")=="modality_shift" for i in z["issues"])
    assert any(i.get("segment_index")==6 and i.get("type")=="exception" for i in z["issues"])
    assert any(i.get("segment_index")==10 and i.get("type")=="quantity" and i.get("source_span")=="3" and i.get("translation_span")=="4" for i in z["issues"])
    assert not any(i.get("type")=="quantity" and "1، 4" in str(i.get("translation_span")) for i in z["issues"])


def test_accepted_wudu_sentence_does_not_false_positive():
    z=result()
    assert not any(i.get("segment_index")==7 for i in z["issues"])


def test_safe_correction_never_creates_identity_nonsense_or_broken_modal():
    z=result()
    fix=build_high_confidence_correction(EN,z["issues"])
    assert fix is not None
    low=fix["corrected_text"].lower()
    assert "zakat is obligatory" in low
    # V15.2 suggests only atomic terminology substitutions; structural/ruling
    # rewrites remain human-review tasks.
    assert "it must be done when needed" in low
    assert "not permissible except in a case of necessity" not in low
    assert "sharia is sharia" not in low
    assert "tawhid means tawhid" not in low
    assert "it permissible be done" not in low


def test_source_route_contains_mixed_domains():
    z=result()
    assert "quran" in z["source_route"]["domains"]
    assert "hadith" in z["source_route"]["domains"]
    assert "fiqh" in z["source_route"]["domains"]
    assert "terminology" in z["source_route"]["domains"]
