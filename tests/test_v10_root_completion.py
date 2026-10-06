from core.normalization import numbers
from core.rules import analyze_rules
from core.recognition import recognize_hadith
from core.engine import analyze


def _types(result):
    return {i.get('type') for i in result.get('issues', [])}


def test_arabic_quantities_are_general_not_context_specific():
    assert numbers('يُعطى المال لثلاث فئات محددة') == ['3']
    assert numbers('عدد الأيام سبعة أيام') == ['7']
    assert '2' in numbers('يجوز هذا في حالتين فقط')


def test_fraction_to_full_is_compared_as_half_to_one():
    r = analyze_rules('يؤخذ نصف المقدار.', 'The full amount is taken.')
    qty = [i for i in r['issues'] if i.get('type') == 'quantity']
    assert qty
    assert qty[0]['source_span'] == '1/2'
    assert qty[0]['translation_span'] == '1'


def test_fraction_to_fraction_still_works():
    r = analyze_rules('يُخصّص ثلث المال لهذا الغرض.', 'Half of the money is allocated for this purpose.')
    qty = [i for i in r['issues'] if i.get('type') == 'quantity']
    assert qty
    assert qty[0]['source_span'] == '1/3'
    assert qty[0]['translation_span'] == '1/2'


def test_clean_conditions_are_not_false_positives():
    ar = '''يجوز للمريض الفطر إذا خاف الضرر.\nلا يجوز هذا إلا عند الضرورة.\nإذا تحقق الشرط جاز الفعل.\nيجب أداء الواجب عند تحقق سببه.'''
    en = '''A sick person may break the fast if harm is feared.\nThis is not permissible except in a case of necessity.\nIf the condition is met, the action is permissible.\nThe obligation must be fulfilled when its cause is established.'''
    r = analyze(ar, en, use_live_sources=False, use_semantic_ai=False)
    assert r['status'] == 'safe'
    assert not r['issues']


def test_hadith_aldeen_alnaseeha_has_local_locator():
    m = recognize_hadith('الدين النصيحة', live=False)
    assert m is not None
    assert m['id'] == '4309'
    assert m['score'] >= .99


def test_clean_reference_free_block_stays_safe():
    ar='''الزكاة واجبة.\nالصدقة مستحبة.\nالوضوء شرط للصلاة.\nالتوحيد أصل عظيم في الإسلام.\nنزل الوحي على النبي.\nالشريعة تشمل الهداية والأحكام.\nالفتوى جواب شرعي يصدر عن مؤهل.\nالسنة من هدي النبي.\nيجوز للمريض الفطر إذا خاف الضرر.\nلا يجوز هذا إلا عند الضرورة.\nإذا تحقق الشرط جاز الفعل.\nيجب أداء الواجب عند تحقق سببه.\nعدد الأيام سبعة أيام.\nهذا الحكم خاص بالمسافر.\nقد يقع هذا أحيانًا.'''
    en='''Zakat is obligatory.\nCharity is recommended.\nWudu is required for prayer.\nTawhid is an important principle in Islam.\nRevelation was sent to the Prophet.\nSharia includes guidance and rulings.\nA fatwa is a religious answer issued by a qualified person.\nSunnah is part of the guidance of the Prophet.\nA sick person may break the fast if harm is feared.\nThis is not permissible except in a case of necessity.\nIf the condition is met, the action is permissible.\nThe obligation must be fulfilled when its cause is established.\nThe number of days is seven.\nThis ruling is specific to the traveler.\nThis may happen sometimes.'''
    r = analyze(ar, en, use_live_sources=False, use_semantic_ai=False)
    assert r['status'] == 'safe'
    assert not r['issues']
