from core.normalization import numbers
from core.advanced_semantics import analyze_scope, analyze_term_relations, analyze_provenance, analyze_reference_conflicts
from core.rules import analyze_rules


def types(res): return {x['type'] for x in res['issues']}

def test_arabic_word_numbers_and_fractions_and_dual():
    assert '7' in numbers('سبعة أيام')
    assert '3' in numbers('ثلاث فئات')
    assert '2' in numbers('في حالتين فقط')
    assert '1/2' in numbers('نصف المقدار')
    assert '1/3' in numbers('ثلث المال')

def test_scope_generalization_and_frequency():
    r=analyze_scope('تنطبق القاعدة على بعض الناس فقط.\nقد يقع ذلك أحيانًا ولا يقع دائمًا.','The rule applies to everyone.\nThis always happens.')
    assert 'scope_shift' in types(r)
    assert 'frequency_shift' in types(r)

def test_scope_reversal_not_limited_to_only():
    r=analyze_scope('العبادة لا تقتصر على الطقوس الظاهرة.','Worship means outward rituals only.')
    assert 'scope_reversal' in types(r)

def test_term_relation_charity_zakat():
    r=analyze_term_relations('الصدقة ليست هي الزكاة.','Charity is Zakat.')
    assert 'term_relation_reversal' in types(r)

def test_provenance_claim_added():
    r=analyze_provenance('هذا النص لم يثبت أنه حديث صحيح.','This is certainly an authentic hadith.')
    assert 'provenance_claim_shift' in types(r)

def test_human_explanation_not_quran():
    r=analyze_provenance('هذا تفسير بشري وليس نصًا من القرآن.','This is a verse from the Quran.')
    assert 'sacred_text_boundary' in types(r)

def test_reference_quran_one_vs_many():
    ev=[{'segment_index':1,'status':'live_verified','evidence_type':'quran_translation','detail':'Say, He is Allah, One.'}]
    rec=[{'segment_index':1,'recognition':{'kind':'quran'}}]
    r=analyze_reference_conflicts('قل هو الله أحد.','Say: He is Allah, one among many gods.',rec,ev)
    assert 'reference_contradiction' in types(r)

def test_reference_negation_contradiction():
    ev=[{'segment_index':1,'status':'live_verified','evidence_type':'quran_translation','detail':'He neither begets nor is born.'}]
    rec=[{'segment_index':1,'recognition':{'kind':'quran'}}]
    r=analyze_reference_conflicts('لم يلد ولم يولد.','He has children and was born.',rec,ev)
    assert 'reference_contradiction' in types(r)

def test_condition_overlap_not_double_counted():
    r=analyze_rules('يجب أداء الواجب عند تحقق سببه.','The obligation must be fulfilled when its cause is established.')
    cond=[x for x in r['issues'] if x['type']=='condition']
    assert len(cond)==0

def test_correct_scope_and_numbers_stay_clean():
    from core.engine import analyze
    ar='''يجوز للمريض الفطر إذا خاف الضرر.\nلا يجوز هذا إلا عند الضرورة.\nيجب أداء الواجب عند تحقق سببه.\nعدد الأيام سبعة أيام.\nهذا الحكم خاص بالمسافر.\nقد يقع هذا أحيانًا.'''
    en='''A sick person may break the fast if harm is feared.\nThis is not permissible except in a case of necessity.\nThe obligation must be fulfilled when its cause is established.\nThe number of days is seven.\nThis ruling is specific to the traveler.\nThis may happen sometimes.'''
    r=analyze(ar,en,use_live_sources=False,use_semantic_ai=False)
    assert r['status']=='safe'
    assert not r['issues']

def test_quantity_examples_detected():
    from core.engine import analyze
    pairs=[
        ('عدد الأيام سبعة أيام.','The number of days is five.'),
        ('يستمر الحكم لمدة ثلاثة أشهر.','The ruling lasts for five months.'),
        ('يجوز هذا في حالتين فقط.','This is permissible in three cases.'),
        ('يؤخذ نصف المقدار.','The full amount is taken.'),
        ('يُخصّص ثلث المال لهذا الغرض.','Half of the money is allocated for this purpose.'),
    ]
    for ar,en in pairs:
        r=analyze(ar,en,use_live_sources=False,use_semantic_ai=False)
        assert any(i['type']=='quantity' for i in r['issues'])
