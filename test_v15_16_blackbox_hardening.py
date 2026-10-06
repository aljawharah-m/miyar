from core.engine import analyze


def run(ar,en):
    return analyze(ar,en,use_live_sources=False,use_semantic_ai=False)

def titles(r): return [x.get('title','') for x in r['issues']]
def types(r): return {x.get('type') for x in r['issues']}
def tax(r): return {x.get('issue_taxonomy') for x in r['issues']}


def test_thousands_format_equivalent():
    assert run('بلغ العدد 10000.','The count was 10,000.')['issues']==[]

def test_negative_pronoun_ahad_not_numeric():
    assert run('لم يحضر أحد.','No one attended.')['issues']==[]

def test_likul_every_is_preserved():
    assert run('لكل موظف حساب واحد.','Every employee has one account.')['issues']==[]

def test_not_permitted_is_valid_prohibition_rendering():
    assert run('لا يجوز الدخول دون تصريح.','Entry is not permitted without authorization.')['issues']==[]

def test_quran_surah_name_change_same_ayah_is_reference_drift():
    r=run('ورد المرجع: سورة البقرة، الآية 183.','The reference is Surah An-Nisa, verse 183.')
    assert 'SOURCE_INTEGRITY' in tax(r)
    assert any('السورة' in x for x in titles(r))

def test_numeric_quran_locator_change_is_reference_not_quantity():
    r=run('ورد المرجع القرآني 2:183.','The Quran reference is 4:183.')
    assert 'SOURCE_INTEGRITY' in tax(r)
    assert not any(x.get('type')=='quantity' for x in r['issues'])

def test_hadith_number_change_is_reference_integrity():
    r=run('ورد في الحديث والمصدر صحيح مسلم رقم 1907.','The hadith source is Sahih Muslim no. 1908.')
    assert 'SOURCE_INTEGRITY' in tax(r)

def test_quran_to_prophet_attribution_swap():
    r=run('قال الله تعالى: «لا إكراه في الدين».','The Prophet Muhammad said: “There is no compulsion in religion.”')
    assert 'SOURCE_INTEGRITY' in tax(r)

def test_prophet_to_quran_attribution_swap():
    r=run('قال رسول الله صلى الله عليه وسلم: «إنما الأعمال بالنيات».','The Qur’an states: “Actions are by intentions.”')
    assert 'SOURCE_INTEGRITY' in tax(r)

def test_insufficient_evidence_paraphrase_is_safe():
    assert run('الأدلة غير كافية للجزم.','The evidence is insufficient for certainty.')['issues']==[]

def test_insufficient_evidence_to_certainty_is_epistemic():
    r=run('الأدلة غير كافية للجزم.','The evidence proves the claim conclusively.')
    assert 'EPISTEMIC' in tax(r)

def test_ma_lam_to_even_if_reverses_condition():
    r=run('يستمر الإجراء ما لم يظهر خطأ.','The process continues even if an error appears.')
    assert any(x.get('type')=='condition_gate_shift' for x in r['issues'])

def test_recommended_to_forbidden_is_one_religious_ruling_root():
    r=run('هذا الفعل مستحب.','This action is forbidden.')
    assert len(r['issues'])==1
    assert r['issues'][0]['issue_taxonomy']=='RELIGIOUS_SEMANTIC'
    assert r['issues'][0]['religious_impact']=='high'

def test_disliked_to_obligatory_is_one_religious_ruling_root():
    r=run('هذا الفعل مكروه.','This action is obligatory.')
    assert len(r['issues'])==1
    assert r['issues'][0]['issue_taxonomy']=='RELIGIOUS_SEMANTIC'

def test_rabb_al_alamin_all_worlds_not_generalization():
    assert run('«الحمد لله رب العالمين».','“All praise is for Allah, Lord of all worlds.”')['issues']==[]

def test_as_samad_dependency_is_detected():
    r=run('«الله الصمد».','“Allah depends on His creation.”')
    assert len(r['issues'])==1
    assert r['issues'][0]['issue_taxonomy']=='RELIGIOUS_SEMANTIC'
    assert r['issues'][0]['religious_impact']=='high'

def test_din_nasiha_negation_detected():
    r=run('قال رسول الله صلى الله عليه وسلم: «الدين النصيحة».','The Prophet Muhammad said: “Religion has nothing to do with sincere advice.”')
    assert r['issues'] and r['issues'][0]['religious_impact']=='high'

def test_source_fabrication_variant_is_reference_root():
    r=run('إذا تعذر التحقق فلا يجوز اختلاق مرجع.','If verification fails, a substitute religious reference can be supplied.')
    assert len(r['issues'])==1
    assert r['issues'][0]['issue_taxonomy']=='SOURCE_INTEGRITY'

def test_target_haram_addition_has_high_religious_impact():
    r=run('النص يحتاج إلى مراجعة.','The text states that the act is haram.')
    assert r['issues'] and r['issues'][0]['religious_impact']=='high'

def test_consensus_addition_is_single_root():
    r=run('ذكر النص رأيًا واحدًا.','All scholars unanimously agree with this religious ruling.')
    assert len(r['issues'])==1
    assert r['issues'][0]['type']=='unsupported_addition_policy_shift'
