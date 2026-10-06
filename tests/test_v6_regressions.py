from core.engine import analyze
from core.rules import analyze_rules


def test_bila_without_is_preserved_not_added_negation():
    z=analyze_rules(
        "من قال هذا الكلام دخل الجنة بلا حساب.",
        "Whoever says this statement will enter Paradise without reckoning.",
    )
    assert not any(i.get("type") == "negation" for i in z["issues"])


def test_may_probability_is_not_permission():
    z=analyze_rules(
        "هذا نص ديني عام يحتمل أكثر من معنى حسب السياق.",
        "This religious statement may have more than one possible meaning depending on context.",
    )
    assert not any(i.get("type") == "permission" for i in z["issues"])


def test_more_than_one_possible_meaning_is_not_quantity_drift():
    z=analyze_rules(
        "هذا نص ديني عام يحتمل أكثر من معنى حسب السياق.",
        "This religious statement may have more than one possible meaning depending on context.",
    )
    assert not any(i.get("type") == "quantity" for i in z["issues"])


def test_jaza_is_permission_and_preserved_by_permissible():
    z=analyze_rules("إذا تحقق الشرط جاز الفعل.", "The action is permissible.")
    types=[i.get("type") for i in z["issues"]]
    assert "condition" in types
    assert "permission" not in types


def test_full_mixed_message_has_no_known_v5_false_positives():
    ar="""اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ.
وَإِنْ كُنْتُمْ جُنُبًا فَاطَّهَّرُوا.
إنما الأعمال بالنيات.
من قال هذا الكلام دخل الجنة بلا حساب.
الزكاة واجبة.
التوحيد أصل عظيم في الإسلام.
الشريعة تشمل الهداية والأحكام ولا تقتصر على العقوبات.
نزل الوحي على النبي.
الوضوء شرط للصلاة.
لا يجوز فعل ذلك.
لا يجوز هذا إلا في حالة الضرورة.
إذا تحقق الشرط جاز الفعل.
يجوز فعل ذلك عند الحاجة.
يجب فعل ذلك.
عدد الركعات هنا ثلاث ركعات.
الصلاة واجبة.
الصلاة واجبة على المسلم البالغ.
هذا نص ديني عام يحتمل أكثر من معنى حسب السياق."""
    en="""Allah is one god among many, the Ever-Living.
Purify yourselves.
Actions are judged by intentions.
Whoever says this statement will enter Paradise without reckoning.
Charity is obligatory.
Oneness is an important principle in Islam.
Sharia is criminal law.
The Prophet received personal inspiration.
Wudu is required for prayer.
It is permissible to do this.
This is not permissible.
The action is permissible.
It must be done when needed.
It may be done.
The number of rak'ahs here is four.
Prayer is obligatory only for scholars.
Prayer is obligatory.
This religious statement may have more than one possible meaning depending on context."""
    z=analyze(ar,en,use_live_sources=False,use_semantic_ai=False)
    # Segment 4: بلا حساب ↔ without reckoning must not be an added negation.
    assert not any(i.get("segment_index")==4 and i.get("type")=="negation" for i in z["issues"])
    # Segment 12: only the missing condition should be structural; جاز ↔ permissible is preserved.
    assert not any(i.get("segment_index")==12 and i.get("type")=="permission" for i in z["issues"])
    # Segment 18 is a natural uncertainty statement, not a ruling or a numeric claim.
    assert not any(i.get("segment_index")==18 and i.get("type") in {"permission","quantity"} for i in z["issues"])
    # Genuine numeric drift remains detected locally.
    assert any(i.get("segment_index")==15 and i.get("type")=="quantity" and i.get("source_span")=="3" and i.get("translation_span")=="4" for i in z["issues"])


def test_obligation_target_qualifier_loss_is_detected():
    z=analyze_rules("الصلاة واجبة على المسلم البالغ.", "Prayer is obligatory.")
    # structural rules alone do not own this; engine/local semantics must surface it.
    full=analyze("الصلاة واجبة على المسلم البالغ.", "Prayer is obligatory.", use_live_sources=False, use_semantic_ai=False)
    assert any(i.get("type")=="scope" and "المسلم البالغ" in str(i.get("source_span")) for i in full["issues"])


def test_prohibition_flip_is_not_double_counted_as_bare_negation():
    z=analyze("لا يجوز فعل ذلك.", "It is permissible to do this.", use_live_sources=False, use_semantic_ai=False)
    assert sum(1 for i in z["issues"] if i.get("type")=="ruling_polarity_shift") == 1
    assert not any(i.get("type")=="negation" for i in z["issues"])
