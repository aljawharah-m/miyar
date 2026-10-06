from core.engine import analyze
from core.corrections import build_high_confidence_correction


def r(ar,en):
    return analyze(ar,en,use_live_sources=False,use_semantic_ai=False)


def test_dedupe_is_segment_local_for_repeated_modality_shift():
    z=r("يجوز فعل ذلك. يجوز للمسافر الفطر إذا شق عليه الصوم.",
        "It must be done. A traveler must break the fast.")
    shifts=[i for i in z["issues"] if i.get("type")=="modality_shift"]
    assert {i.get("segment_index") for i in shifts} == {1,2}
    assert any(i.get("segment_index")==2 and i.get("type")=="condition" for i in z["issues"])


def test_fasting_is_preserved_by_break_the_fast_context():
    z=r("يجوز للمسافر الفطر إذا شق عليه الصوم.","A traveler may break the fast if fasting is difficult for him.")
    assert not any(i.get("source_span")=="الصيام" and i.get("type")=="terminology" for i in z["issues"])


def test_only_for_is_scope_addition_not_generalization():
    z=r("الصلاة واجبة.","Prayer is obligatory only for scholars.")
    assert any(i.get("type")=="scope_addition" for i in z["issues"])
    assert not any(i.get("type")=="generalization" for i in z["issues"])


def test_zakat_second_charity_occurrence_is_bound_and_corrected():
    ar="الصدقة مستحبة والزكاة واجبة."
    en="Charity is recommended and charity is obligatory."
    z=r(ar,en)
    issue=next(i for i in z["issues"] if i.get("source_span")=="الزكاة" and i.get("type")=="flattening")
    assert issue.get("translation_occurrence_index")==2
    fix=build_high_confidence_correction(en,z["issues"])
    assert fix is not None
    assert fix["corrected_text"] == "Charity is recommended and Zakat is obligatory."


def test_qayyum_omission_is_detected():
    z=r("اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ.","Allah is one god among many, the Ever-Living.")
    assert any(i.get("source_span")=="القيوم" and i.get("type")=="omission" for i in z["issues"])


def test_qayyum_preserved_passes_term_guard():
    z=r("اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ.","Allah—there is no deity except Him, the Ever-Living, the Sustainer of all existence.")
    assert not any(i.get("source_span")=="القيوم" and i.get("type") in {"omission","terminology","flattening"} for i in z["issues"])
