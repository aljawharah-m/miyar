import json
from pathlib import Path
from core.terminology import TERMS, analyze_terminology

ROOT=Path(__file__).resolve().parents[1]

def test_every_term_has_provenance_row_and_source_basis():
    rows=json.loads((ROOT/'data'/'terminology_provenance.json').read_text(encoding='utf-8'))
    idx={r['term']:r for r in rows}
    assert len(idx)==len(TERMS)
    for t in TERMS:
        row=idx[t['ar']]
        assert row['source_refs']
        assert all(r.get('name') for r in row['source_refs'])
        assert row.get('policy_note')

def test_curated_terminology_evidence_exposes_reference_basis_without_claiming_live_use():
    out=analyze_terminology('الزكاة واجبة','Charity is obligatory')
    ev=next(e for e in out['evidence'] if e['title']=='الزكاة')
    assert ev['status']=='local_curated_rule'
    assert ev.get('source_basis')
    assert 'الأساس المرجعي' in ev['detail']

def test_readme_does_not_claim_auto_apply_recheck():
    txt=(ROOT/'README.md').read_text(encoding='utf-8')
    assert 'طبّق كل التصحيحات وأعد الفحص' not in txt
    assert 'لا يوجد زر تطبيق تلقائي' in txt

def test_external_validation_is_not_fabricated():
    txt=(ROOT/'docs'/'EXTERNAL_VALIDATION_PROTOCOL.md').read_text(encoding='utf-8')
    assert 'لا تُملأ نتائج هذا الملف آليًا' in txt
