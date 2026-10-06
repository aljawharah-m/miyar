from core.engine import analyze


def test_target_side_explicit_religious_addition_has_direct_religious_impact():
    ar = "ولا يجوز للنظام إضافة نصائح أو أحكام أو استنتاجات لم ترد في الأصل حتى لو بدت منطقية، فالإضافة غير المدعومة قد تكون أخطر من الترجمة الحرفية الناقصة"
    en = "The translator may add reasonable religious conclusions even if they do not appear in the source text."
    result = analyze(ar, en)
    roots = result.get('issues', [])
    hit = [x for x in roots if x.get('type') == 'unsupported_addition_policy_shift']
    assert hit, roots
    assert hit[0]['religious_impact'] == 'high'
    assert 'أضافت استنتاجًا دينيًا صريحًا' in hit[0]['religious_impact_reason']


def test_general_unsupported_addition_without_religious_target_stays_nonreligious():
    ar = "لا يجوز إضافة استنتاجات لم ترد في الأصل"
    en = "The translator may add reasonable conclusions that do not appear in the source."
    result = analyze(ar, en)
    roots = result.get('issues', [])
    hit = [x for x in roots if x.get('type') == 'unsupported_addition_policy_shift']
    if hit:
        assert hit[0]['religious_impact'] == 'none'
