from core.engine import analyze


def types(ar, en):
    return [x.get('type') for x in analyze(ar, en, use_live_sources=False, use_semantic_ai=False)['issues']]


def result(ar, en):
    return analyze(ar, en, use_live_sources=False, use_semantic_ai=False)


def test_discourse_if_said_is_not_reported_as_condition_when_meaning_is_preserved():
    assert 'condition' not in types('وإذا قيل إن زيدًا حضر فالمقصود مجرد مثال لغوي.', 'If it is said that Zayd attended, this is only a linguistic example.')


def test_discourse_if_mentioned_is_not_a_fake_condition():
    assert 'condition' not in types('وإذا ورد في النص اسم خالد فهو مثال في العبارة.', 'When the name Khalid appears in the text, it is an example in the sentence.')


def test_real_condition_removal_gets_root_condition_gate():
    ts=types('لا يُقبل الطلب إلا بشرط تحقق الهوية.', 'The request is accepted regardless of whether identity is verified.')
    assert 'condition_gate_shift' in ts


def test_exclusivity_is_one_root_not_bare_negation_and_exception():
    ts=types('لا يكتمل الإجراء إلا بعد التحقق من المصدر.', 'The procedure is complete before source verification.')
    assert 'exclusivity_shift' in ts
    assert 'negation' not in ts and 'exception' not in ts


def test_ruling_degree_is_claim_linked():
    ts=types('إذا قيل إن الفعل مستحب فلا ينبغي نقله على أنه واجب.', 'A recommended action may be described as mandatory.')
    assert 'ruling_degree_shift' in ts
    assert 'condition' not in ts


def test_lexical_one_of_does_not_create_quantity_bug():
    ts=types('هذا واحد من المبادئ الأساسية.', 'This is one of the basic principles.')
    assert 'quantity' not in ts


def test_asserted_number_ignores_bad_example_numbers():
    ts=types('المطلوب زكاة مقدارها 2.5 في المئة، ولا يجوز ترجمتها إلى 25 في المئة أو 0.25 في المئة.', 'The required Zakat amount is 25 percent.')
    assert 'asserted_quantity_shift' in ts


def test_reference_identifier_has_dedicated_root_not_quantity():
    ts=types('[QURAN_REF: 2:183]', '[QURAN_REF: 2:185]')
    assert 'reference_identifier_changed' in ts
    assert 'quantity' not in ts


def test_citation_locator_change_is_detected():
    ts=types('المرجع سورة البقرة، الآية 183.', 'The reference may be changed to Surah Al-Baqarah verse 185.')
    assert 'reference_identifier_changed' in ts


def test_scope_generalization_root():
    ts=types('لا يجوز تحويل بعض الناس إلى جميع الناس، أو غالبًا إلى دائمًا.', 'Some people can be translated as all people, and usually as always.')
    assert any(x in ts for x in ('quantifier_scope_reversal','scope_reversal','frequency_shift'))


def test_uncertainty_to_certainty_root():
    assert 'uncertainty_to_certainty' in types('النتيجة محتملة وليست مؤكدة.', 'The conclusion is definitely correct.')


def test_comparison_direction_root_suppresses_condition_noise():
    ts=types('فإذا كانت نسبة الخطأ في النظام أ أقل من النظام ب فلا يجوز قلبها.', 'System A has a higher error rate than System B.')
    assert 'comparison_direction_reversal' in ts
    assert 'condition' not in ts


def test_event_order_and_causality_have_specific_roots():
    ts=types('توضأ ثم صلى، وصلى لأنه توضأ.', 'He prayed and then performed Wudu. He performed Wudu because he had prayed.')
    assert 'event_order_reversal' in ts and 'causality_reversal' in ts


def test_unit_mismatch_not_generic_number_mismatch():
    ts=types('يجب المحافظة على الوحدات، فـ 5 دقائق ليست 5 ساعات.', 'Five minutes may be translated as five hours.')
    assert 'unit_mismatch' in ts
    assert 'quantity' not in ts


def test_actor_role_inversion_has_specific_root():
    ts=types('اتخذ المراجع القرار وليس النظام.', 'The system made the decision, not the reviewer.')
    assert 'actor_role_inversion' in ts


def test_source_attribution_collapse_has_specific_root():
    ts=types('وفقًا للمصدر الأول الحكم كذا، بينما المصدر الثاني يذكر تفصيلًا مختلفًا.', 'According to both sources, exactly the same ruling applies.')
    assert 'source_attribution_collapse' in ts


def test_pronoun_ambiguity_is_local_review_not_global_downgrade_when_critical_exists():
    r=result('قال أحمد لخالد إنه سيعود، والضمير غير واضح. ولا يجوز تحويل الممنوع إلى مباح.', 'Ahmed told Khalid that Khalid would return. The prohibited act is permissible.')
    assert 'pronoun_ambiguity' in [x['type'] for x in r['issues']]
    assert r['status']=='critical'


def test_and_or_logic_root():
    assert 'logical_operator_shift' in types('يجوز المتابعة إذا تحقق الشرطان أ و ب.', 'The user may proceed if A or B is fulfilled.')


def test_at_least_cardinality_root():
    assert 'logical_cardinality_shift' in types('يجب التحقق من مصدر واحد على الأقل من مصدرين.', 'The user must verify at least two sources.')


def test_only_scope_is_contextual_not_presence_count():
    ts=types('المقصود الاختبار التقني فقط.', 'The text is intended only for technical testing.')
    assert 'scope_omission' not in ts


def test_bad_examples_do_not_become_asserted_values_when_translation_preserves_rule():
    ts=types('القيمة الصحيحة 2.5، ولا تحولها إلى 25 أو 0.25.', 'The correct value is 2.5; do not change it to 25 or 0.25.')
    assert 'quantity' not in ts and 'asserted_quantity_shift' not in ts


def test_reference_fabrication_policy_root():
    assert 'source_fabrication_policy_shift' in types('إذا تعذر التحقق من المرجع فيجب التصريح بعدم القدرة على التحقق بدل اختلاق مصدر.', 'If the reference cannot be verified, an alternative reliable-looking reference may be inserted.')


def test_epistemic_overclaim_root():
    assert 'epistemic_overclaim' in types('لم يُكتشف خطأ لا تعني لا يوجد خطأ.', 'No error was detected means there is definitely no error.')


def test_safe_paraphrase_not_rejected():
    r=result('بدأ الاجتماع في التاسعة صباحًا.', 'The meeting started at 9 AM.')
    assert r['status']=='safe'


def test_disclaimer_boundary_root():
    assert 'disclaimer_boundary_shift' in types('هذا للاختبار التقني فقط، ولا يُعد فتوى شرعية.', 'This may be treated as a complete religious ruling.')


def test_diagnostics_separate_raw_signals_from_root_issues():
    r=result('لا يكتمل الإجراء إلا بعد التحقق من المصدر.', 'The procedure is complete before verification.')
    d=r['diagnostics']
    assert d['raw_signal_count'] >= d['root_issue_count']
    assert d['suppressed_signal_count'] == d['raw_signal_count']-d['root_issue_count']


def test_unseen_discourse_frame_does_not_overfit_if_clause():
    ts=types('وإذا افترضنا في المثال أن خالد وصل فهذه مقدمة للمثال لا شرط للحكم.', 'Suppose in the example that Khalid arrived; this frames the example and is not a condition of the ruling.')
    assert 'condition' not in ts
