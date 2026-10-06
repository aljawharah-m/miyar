from core.engine import analyze
from core.recognition import recognize_source, _extract_aya_rows
from core.sources import source_route
from core.semantic_ai import interpret_similarity, _chunk_text


def r(a,e): return analyze(a,e,use_live_sources=False)

# Core structure preservation
def test_exception_loss(): assert any(i["type"]=="exception" for i in r("لا يجوز هذا إلا في حالة الضرورة","This is not permissible")["issues"])
def test_exception_ok(): assert not any(i["type"]=="exception" for i in r("لا يجوز هذا إلا في حالة الضرورة","This is not permissible except in a case of necessity")["issues"])
def test_negation_loss(): assert any(i["type"]=="negation" for i in r("هذا ليس واجبا","This is obligatory")["issues"])
def test_negation_ok(): assert not any(i["type"]=="negation" for i in r("هذا ليس واجبا","This is not obligatory")["issues"])
def test_condition_loss(): assert any(i["type"]=="condition" for i in r("يجوز إذا تحقق الشرط","It is permissible")["issues"])
def test_condition_ok(): assert not any(i["type"]=="condition" for i in r("يجوز إذا تحقق الشرط","It is permissible if the condition is met")["issues"])

# Modality / ruling transitions
def test_modality_is_merged():
    z=r("يجوز فعل ذلك","It must be done")
    assert any(i["type"]=="modality_shift" for i in z["issues"])
    assert not any(i["type"] in {"permission","obligation"} for i in z["issues"])
def test_modality_reverse_is_merged(): assert any(i["type"]=="modality_shift" for i in r("يجب فعل ذلك","It may be done")["issues"])
def test_prohibition_to_permission(): assert any(i["type"]=="ruling_polarity_shift" for i in r("لا يجوز فعل ذلك","It may be done")["issues"])

# Terminology / flattening
def test_tawhid(): assert any(i["type"]=="flattening" for i in r("التوحيد أصل عظيم","Oneness is a great principle")["issues"])
def test_tawhid_accepted(): assert not any(i["type"]=="flattening" for i in r("التوحيد أصل عظيم","Tawhid is a great principle")["issues"])
def test_sharia(): assert any(i["type"]=="flattening" for i in r("الشريعة تشمل هداية وأحكاما","Sharia is criminal law")["issues"])
def test_wahy(): assert any(i["type"]=="flattening" for i in r("الوحي ما أوحاه الله إلى أنبيائه","Revelation is personal inspiration")["issues"])
def test_sunnah_flattening(): assert any(i["type"]=="flattening" for i in r("السنة هدي النبي","Sunnah is culture")["issues"])

# Numbers and list markers
def test_number(): assert any(i["type"]=="quantity" for i in r("العدد 3","The number is 4")["issues"])
def test_clean_number(): assert not any(i["type"]=="quantity" for i in r("العدد 3","The number is 3")["issues"])
def test_list_number_not_quantity(): assert not any(i["type"]=="quantity" for i in r("1. لا يجوز هذا إلا في حالة الضرورة","This is not permissible")["issues"])
def test_quantity_span():
    i=next(i for i in r("عدد الركعات هنا 3","The number of rak'ahs here is 4")["issues"] if i["type"]=="quantity")
    assert i["source_span"]=="3" and i["translation_span"]=="4"

# Scope / generalization
def test_generalization(): assert any(i["type"]=="generalization" for i in r("قد يحدث ذلك","This always happens")["issues"])
def test_narrowing(): assert any(i["type"]=="narrowing" for i in r("كل الناس","Some people")["issues"])

# Source recognition
def test_quran_text_recognition_offline():
    z=r("اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ","Allah—there is no deity except Him, the Ever-Living, the Sustainer of existence.")
    assert z["recognition"] and z["recognition"]["kind"]=="quran"
    # This exact phrase is all of 3:2 and also the opening of 2:255. Mi'yar must
    # identify Quranic text without pretending one unique reference.
    m=z["recognition"]["match"]
    assert m.get("ambiguous") is True
    refs={(x["surah"],x["ayah"]) for x in m.get("candidates",[])}
    assert (3,2) in refs and (2,255) in refs
def test_hadith_text_recognition_offline():
    z=r("إنما الأعمال بالنيات","Actions are judged by intentions")
    assert z["recognition"] and z["recognition"]["kind"]=="hadith"
    assert z["recognition"]["match"]["id"] in {"4560","66511"}
def test_quran_route_from_recognition():
    z=r("قل هو الله أحد","Say: He is Allah, One")
    assert z["source_route"]["domains"]==["quran"]
def test_hadith_route_from_recognition():
    z=r("إنما الأعمال بالنيات","Actions are judged by intentions")
    assert z["source_route"]["domains"]==["hadith"]
def test_source_route_quran_cue(): assert "quran" in source_route("قال الله في سورة البقرة")["domains"]
def test_source_route_hadith_cue(): assert "hadith" in source_route("قال النبي في الحديث")["domains"]

# Evidence / abstention / audit
def test_audit(): assert len(r("لا يجوز","This is not permissible")["audit"]["id"])==12
def test_repeatability():
    a=r("لا يجوز هذا إلا في حالة الضرورة","This is not permissible")
    b=r("لا يجوز هذا إلا في حالة الضرورة","This is not permissible")
    assert a["status"]==b["status"]
    assert [(x["type"],x["severity"]) for x in a["issues"]]==[(x["type"],x["severity"]) for x in b["issues"]]
def test_evidence_separation():
    z=r("التوحيد أصل عظيم","Oneness is a great principle")
    assert z["status"]=="critical"
    assert any(e.get("status")=="local_verified_guideline" for e in z["evidence_used"])
def test_textual_evidence_is_used(): assert any(e.get("status")=="textual_verified" for e in r("لا يجوز هذا إلا في حالة الضرورة","This is not permissible")["evidence_used"])
def test_safe_case_not_blocked(): assert r("لا يجوز هذا إلا في حالة الضرورة","This is not permissible except in a case of necessity")["status"]=="safe"
def test_critical_case_blocked(): assert r("يجوز فعل ذلك","It must be done")["status"]=="critical"
def test_evidence_tier_for_direct_rule(): assert r("يجوز فعل ذلك","It must be done")["evidence_tier"]["tier"]=="B"

# Fusion quality
def test_scope_duplicate_removed_when_exception_known():
    z=r("لا يجوز هذا إلا في حالة الضرورة","This is not permissible")
    assert any(i["type"]=="exception" for i in z["issues"])
    assert not any(i["type"]=="scope" for i in z["issues"])
def test_exclusivity_fusion():
    z=r("لا إله إلا الله","God is one among others")
    assert any(i["type"]=="exclusivity_shift" for i in z["issues"])
    assert not any(i["type"] in {"negation","exception"} for i in z["issues"])

# Parser resilience for ICADB payload variants
def test_icadb_payload_parser():
    rows=_extract_aya_rows({"results":[{"aya":255,"text":"الله لا إله إلا هو الحي القيوم"}]},2)
    assert rows==[{"surah":2,"ayah":255,"text":"الله لا إله إلا هو الحي القيوم"}]


# Semantic AI policy (pure, no model download required)
def test_semantic_ai_low_similarity_is_fail(): assert interpret_similarity(0.30)["state"]=="fail"
def test_semantic_ai_mid_similarity_is_review(): assert interpret_similarity(0.50)["state"]=="review"
def test_semantic_ai_high_similarity_is_pass(): assert interpret_similarity(0.80)["state"]=="pass"
def test_engine_survives_without_model():
    z=analyze("لا يجوز هذا إلا في حالة الضرورة","This is not permissible",use_live_sources=False,use_semantic_ai=False)
    assert z["status"]=="critical" and "semantic_ai" in z

def test_no_external_generative_layer_required_for_core():
    z=analyze("يجوز فعل ذلك","It must be done",use_live_sources=False,use_semantic_ai=False)
    assert z["status"]=="critical"
    assert any(i["type"]=="modality_shift" for i in z["issues"])
    assert not any("LLM" in c.get("check","") for c in z["checks"])

def test_low_ai_signal_does_not_inflate_gap_count(monkeypatch):
    import core.engine as eng
    fake={"available":True,"status":"review","model":"fake","similarity":0.53,"signal":{"state":"review"},"issue":None,"detail":"supporting signal"}
    monkeypatch.setattr(eng,"run_semantic_ai",lambda *a,**k: fake)
    z=eng.analyze("لا يجوز هذا إلا في حالة الضرورة","This is not permissible",use_live_sources=False,use_semantic_ai=True)
    assert z["status"]=="critical"
    assert len(z["issues"])==1
    assert z["issues"][0]["type"]=="exception"


def test_ai_only_low_similarity_requests_review_without_fake_gap(monkeypatch):
    import core.engine as eng
    fake={"available":True,"status":"fail","model":"fake","similarity":0.30,"signal":{"state":"fail"},"issue":None,"detail":"supporting signal"}
    monkeypatch.setattr(eng,"run_semantic_ai",lambda *a,**k: fake)
    z=eng.analyze("هذه معلومة عامة","Completely unrelated sentence",use_live_sources=False,use_semantic_ai=True)
    assert z["status"]=="review"
    assert z["issues"]==[]


def test_safe_exception_mirror_is_specific():
    z=r("لا يجوز هذا إلا في حالة الضرورة","This is not permissible except in a case of necessity")
    assert z["status"]=="safe"
    assert "الاستثناء" in z["meaning_mirror"]["gap"]

def test_semantic_chunking_covers_long_text():
    text=("جملة قصيرة. "*900).strip()
    chunks=_chunk_text(text,max_chars=180,max_chunks=12)
    assert len(chunks) > 12  # later passages are not silently collapsed/truncated
    assert max(len(c) for c in chunks) <= 180
    assert sum(len(c.replace(" ","")) for c in chunks) >= len(text.replace(" ",""))*0.99

def test_semantic_chunking_short_text_stays_single():
    assert _chunk_text("نص قصير") == ["نص قصير"]


def test_semantic_ai_pipeline_with_fake_model(monkeypatch):
    import numpy as np
    import core.semantic_ai as sai

    class FakeModel:
        def encode(self,texts,**kwargs):
            # Stable normalized embeddings; Arabic/English paired content gets same direction here.
            return np.tile(np.array([[1.0,0.0,0.0]],dtype=float),(len(texts),1))

    monkeypatch.setattr(sai,"_load_model",lambda model_id:(FakeModel(),None))
    z=sai.run_semantic_ai("نص عربي طويل. "*80,"English translation. "*80,enabled=True,model_id="fake")
    assert z["available"] is True
    assert z["status"]=="pass"
    assert z["similarity"] > 0.99

# Expanded terminology precision
def test_zakat_generic_charity_is_flagged():
    z=r("الزكاة واجبة","Charity is obligatory")
    i=next(i for i in z["issues"] if i.get("source_span")=="الزكاة")
    assert i["type"]=="flattening" and i["translation_span"]=="charity"
    assert z["status"]=="critical"
    assert "عبادة مالية واجبة" in i["impact_ar"]


def test_zakat_explicit_zakat_is_accepted():
    z=r("الزكاة واجبة","Zakat is obligatory")
    assert not any(i.get("source_span")=="الزكاة" for i in z["issues"])


def test_zakat_obligatory_charity_phrase_is_accepted():
    z=r("الزكاة واجبة","Obligatory charity is required")
    assert not any(i.get("source_span")=="الزكاة" and i.get("type")=="flattening" for i in z["issues"])


def test_sadaqah_is_not_zakat():
    z=r("الصدقة مستحبة","Zakat is recommended")
    assert any(i.get("source_span")=="الصدقة" and i.get("type")=="flattening" for i in z["issues"])


def test_wudu_not_generic_washing():
    z=r("الوضوء شرط للصلاة","Washing is a condition for prayer")
    assert any(i.get("source_span")=="الوضوء" and i.get("type")=="flattening" for i in z["issues"])


def test_riba_interest_routes_to_review_not_false_certainty():
    z=r("الربا محرم","Interest is forbidden")
    assert any(i.get("source_span")=="الربا" and i.get("type")=="terminology" for i in z["issues"])
    assert z["status"] in {"review","critical"}

# Long-passage and multi-issue behavior
def test_long_passage_counts_multiple_exceptions():
    z=r(
        "لا يجوز الأول إلا للضرورة. ولا يجوز الثاني إلا بإذن.",
        "The first is not permissible except in necessity. The second is not permissible."
    )
    assert any(i.get("type")=="exception" for i in z["issues"])
    ex=next(i for i in z["issues"] if i.get("type")=="exception")
    assert ex.get("segment_index")==2
    assert ex.get("source_count")==1 and ex.get("translation_count")==0


def test_long_passage_preserves_permission_and_prohibition_separately():
    z=r("لا يجوز هذا. ويجوز ذاك.","This is not permissible. That is permissible.")
    assert not any(i.get("type") in {"permission","prohibition","modality_shift","ruling_polarity_shift"} for i in z["issues"])


def test_multiple_independent_gaps_are_all_returned():
    z=r(
        "الزكاة واجبة. لا يجوز هذا إلا للضرورة. العدد 3.",
        "Charity is obligatory. This is not permissible. The number is 4."
    )
    types=[i.get("type") for i in z["issues"]]
    assert "flattening" in types
    assert "exception" in types
    assert "quantity" in types
    assert len(z["issues"]) >= 3


def test_generic_text_does_not_trigger_live_hadith_search(monkeypatch):
    import core.recognition as rec
    called=[]
    monkeypatch.setattr(rec,"_hadeeth_search_live",lambda text: called.append(text) or [])
    assert rec.recognize_hadith("هذا نص فقهي عام لا يحتوي على حديث",live=True) is None
    assert called==[]


def test_hadith_live_search_uses_bounded_cue_excerpt(monkeypatch):
    import core.recognition as rec
    called=[]
    monkeypatch.setattr(rec,"_hadeeth_search_live",lambda text: called.append(text) or [])
    text=("مقدمة طويلة "*200)+" قال النبي نص للاختبار "+("خاتمة "*200)
    rec.recognize_hadith(text,live=True)
    assert len(called)==1
    assert len(called[0]) < 700
    assert "قال النبي" in called[0]

# Multi-term precision: unrelated valid equivalents must not contaminate each other.
def test_zakat_and_sadaqah_both_correct_in_same_sentence():
    z=r("الزكاة واجبة والصدقة مستحبة","Zakat is obligatory and charity is recommended")
    assert not any(i.get("source_span") in {"الزكاة","الصدقة"} and i.get("type") in {"flattening","terminology"} for i in z["issues"])


def test_repeated_zakat_one_flattened_occurrence_is_caught():
    z=r("الزكاة واجبة. والزكاة لها مصارف محددة.","Zakat is obligatory. Charity has specified recipients.")
    assert any(i.get("source_span")=="الزكاة" and i.get("type")=="flattening" for i in z["issues"])


def test_explicit_wrong_definition_still_caught_when_term_is_preserved():
    z=r("الشريعة هداية وأحكام","Sharia is criminal law")
    assert any(i.get("source_span")=="الشريعة" and i.get("type")=="flattening" for i in z["issues"])


def test_recommended_to_obligatory_is_one_ruling_shift():
    z=r("هذا مستحب","This is obligatory")
    shifts=[i for i in z["issues"] if i.get("type")=="modality_shift"]
    assert len(shifts)==1
    assert "الاستحباب" in shifts[0]["title"] and "الإلزام" in shifts[0]["title"]
    assert not any(i.get("type") in {"recommendation","obligation"} for i in z["issues"])


def test_makruh_to_haram_is_one_ruling_shift():
    z=r("هذا مكروه","This is haram")
    shifts=[i for i in z["issues"] if i.get("type")=="modality_shift"]
    assert len(shifts)==1
    assert "الكراهة" in shifts[0]["title"] and "التحريم" in shifts[0]["title"]


def test_halal_maps_to_permissible_without_false_added_permission():
    z=r("هذا حلال","This is permissible")
    assert not any(i.get("type") in {"permission","ruling_polarity_shift"} for i in z["issues"])


def test_awrah_not_reduced_to_genitals():
    z=r("يجب ستر العورة","The genitals must be covered")
    assert any(i.get("source_span")=="العورة" and i.get("type")=="flattening" for i in z["issues"])


def test_nikah_not_reduced_to_sex():
    z=r("النكاح عقد شرعي","Sex is a religious contract")
    assert any(i.get("source_span")=="النكاح" and i.get("type")=="flattening" for i in z["issues"])


def test_long_quran_mention_does_not_trigger_full_live_index(monkeypatch):
    import core.recognition as rec
    called=[]
    monkeypatch.setattr(rec,"build_quran_index_live",lambda *a,**k: called.append(True) or [])
    text=("هذا مقال طويل عن القرآن ومناهج الترجمة. "*100)
    rec.recognize_quran(text,live=True)
    assert called==[]


def test_all_terminology_entries_accept_primary_equivalent():
    from core.terminology import TERMS, analyze_terminology
    for term in TERMS:
        accepted=term.get("accepted") or []
        assert accepted, term["ar"]
        z=analyze_terminology(term["ar"], accepted[0])
        assert not z["issues"], (term["ar"], accepted[0], z["issues"])


def test_all_risky_terminology_entries_raise_flattening():
    from core.terminology import TERMS, analyze_terminology
    for term in TERMS:
        risky=term.get("risky") or []
        if not risky:
            continue
        z=analyze_terminology(term["ar"], risky[0])
        assert any(i.get("type")=="flattening" and i.get("source_span")==term["ar"] for i in z["issues"]), (term["ar"], risky[0], z["issues"])


def test_all_context_dependent_terminology_entries_request_review():
    from core.terminology import TERMS, analyze_terminology
    for term in TERMS:
        review=term.get("review") or []
        if not review:
            continue
        z=analyze_terminology(term["ar"], review[0])
        assert any(i.get("type")=="terminology" and i.get("source_span")==term["ar"] for i in z["issues"]), (term["ar"], review[0], z["issues"])
