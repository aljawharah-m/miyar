from core.engine import analyze


def run(ar,en):
    return analyze(ar,en,use_live_sources=False,use_semantic_ai=False)


def t(z):
    return {x.get('type') for x in z['issues']}


def test_blind_an_complementizer_inside_reported_clause():
    z=run('ذكر الباحث أن الزكاة عبادة مالية','The researcher stated that Zakat is a financial act of worship.')
    assert 'condition' not in t(z)


def test_blind_in_condition_with_new_verb():
    z=run('إن ظهر الضرر توقف الفعل','If harm appears, the action stops.')
    assert z['status']=='safe'


def test_blind_wajaba_with_quantity_and_permission_flip():
    z=run('وجب دفع خمسة دنانير','He may pay five dinars.')
    assert 'modality_shift' in t(z)


def test_blind_ma_lam_new_wording_preserved():
    z=run('يبقى الحكم ما لم يتغير السبب','The ruling remains unless the cause changes.')
    assert z['status']=='safe'


def test_blind_term_definition_reversal_wudu():
    z=run('الوضوء ليس غسلا عاديا','Wudu is ordinary washing.')
    assert z['status']=='critical'


def test_blind_scope_specific_to_everyone():
    z=run('هذا الحكم خاص بالمسافر','This ruling applies to everyone.')
    assert any(x in t(z) for x in {'scope_shift','generalization','scope'})


def test_blind_same_numbers_different_targets():
    z=run('ثلاث ركعات بعد يوم واحد','one rakah after three days')
    assert 'quantity' in t(z)


def test_blind_no_false_citation_on_writer_statement():
    z=run('قال الكاتب إن الصدقة نافعة','The writer said that charity is beneficial.')
    assert z.get('recognition') is None
    assert not any(i.get('type') in {'attribution','provenance_claim_shift'} for i in z['issues'])
