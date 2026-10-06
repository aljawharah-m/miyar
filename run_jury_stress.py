import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from core.engine import analyze

CASES=[
('safe_exception','لا يجوز هذا إلا في حالة الضرورة','This is not permissible except in a case of necessity','safe',None),
('lost_exception','لا يجوز هذا إلا في حالة الضرورة','This is not permissible','critical','exception'),
('safe_laysa','الفتوى ليست رأيًا شخصيًا','A fatwa is not a personal opinion','safe',None),
('lost_laysa','الفتوى ليست رأيًا شخصيًا','A fatwa is a personal opinion','critical','negation'),
('safe_condition_required','الوضوء شرط للصلاة','Wudu is required for prayer','safe',None),
('permission_to_obligation','يجوز فعل ذلك','It must be done','critical','modality_shift'),
('obligation_to_permission','يجب فعل ذلك','It may be done','critical','modality_shift'),
('recommendation_to_obligation','هذا مستحب','This is obligatory','critical','modality_shift'),
('makruh_to_haram','هذا مكروه','This is haram','critical','modality_shift'),
('number_word_safe','عدد الركعات ثلاث','The number of rakahs is three','safe',None),
('number_word_shift','عدد الركعات ثلاث','The number of rakahs is four','critical','quantity'),
('zakat_safe','الزكاة واجبة','Zakat is obligatory','safe',None),
('zakat_flattened','الزكاة واجبة','Charity is obligatory','critical','flattening'),
('sadaqah_safe','الصدقة مستحبة','Charity is recommended','safe',None),
('sadaqah_as_zakat','الصدقة مستحبة','Zakat is recommended','critical','flattening'),
('wudu_safe','الوضوء طهارة مخصوصة','Wudu is a specific ritual ablution','safe',None),
('wudu_flattened','الوضوء طهارة مخصوصة','Washing is simple cleaning','critical','flattening'),
('tawhid_safe','التوحيد أصل عظيم','Tawhid is a great principle','safe',None),
('tawhid_flattened','التوحيد أصل عظيم','Oneness is a great principle','critical','flattening'),
('sharia_safe','الشريعة هداية وأحكام','Sharia includes guidance and rulings','safe',None),
('sharia_flattened','الشريعة هداية وأحكام','Sharia is criminal law','critical','flattening'),
('wahy_safe','الوحي من الله إلى أنبيائه','Revelation is from God to His prophets','safe',None),
('wahy_flattened','الوحي من الله إلى أنبيائه','Personal inspiration comes to prophets','critical','flattening'),
('sunnah_safe','السنة هدي النبي','Sunnah is the Prophetic way','safe',None),
('sunnah_reductive','السنة هدي النبي','Sunnah is merely tradition','review','terminology'),
('riba_context','الربا محرم','Interest is forbidden','review','terminology'),
('hijab_context','الحجاب واجب','The headscarf is obligatory','review','terminology'),
('sentence_ruling_swap','هذا مستحب. وهذا واجب.','This is obligatory. This is recommended.','critical','modality_shift'),
('sentence_ruling_safe','هذا مستحب. وهذا واجب.','This is recommended. This is obligatory.','safe',None),
('sentence_term_swap','الزكاة واجبة. والصدقة مستحبة.','Charity is obligatory. Zakat is recommended.','critical','flattening'),
('sentence_term_safe','الزكاة واجبة. والصدقة مستحبة.','Zakat is obligatory. Charity is recommended.','safe',None),
('two_exceptions_one_lost','لا يجوز الأول إلا للضرورة. ولا يجوز الثاني إلا بإذن.','The first is not permissible except in necessity. The second is not permissible.','critical','exception'),
('two_exceptions_safe','لا يجوز الأول إلا للضرورة. ولا يجوز الثاني إلا بإذن.','The first is not permissible except in necessity. The second is not permissible except with permission.','safe',None),
('later_term_flattened','الزكاة واجبة. والزكاة لها مصارف محددة.','Zakat is obligatory. Charity has specified recipients.','critical','flattening'),
('may_possibility','قد يحدث هذا','This may happen','safe',None),
('scope_loss','يجوز هذا في بعض الحالات','This is permissible in all cases','review','generalization'),
('prohibition_permission','لا يجوز فعل ذلك','It may be done','critical','ruling_polarity_shift'),
]

results=[]; passed=0
for cid,ar,en,expected_status,expected_type in CASES:
    z=analyze(ar,en,use_live_sources=False,use_semantic_ai=False)
    ts={i.get('type') for i in z['issues']}
    ok=z['status']==expected_status and (expected_type is None or expected_type in ts)
    results.append({'id':cid,'ok':ok,'expected_status':expected_status,'actual_status':z['status'],'expected_type':expected_type,'actual_types':sorted(t for t in ts if t)})
    passed+=int(ok)
report={
    'n':len(CASES),'passed':passed,'failed':len(CASES)-passed,'pass_rate':passed/len(CASES),
    'cases':results,
    'label':'JURY-ORIENTED SYNTHETIC STRESS SET — DEVELOPMENT EVIDENCE ONLY',
    'note':'Designed to exercise critical constraints, terminology precision, false-positive control, sentence-local alignment, and abstention/review behavior. Not independent field validation.'
}
print(json.dumps(report,ensure_ascii=False,indent=2))
(ROOT/'evaluation'/'jury_stress_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
if passed!=len(CASES): raise SystemExit(1)
