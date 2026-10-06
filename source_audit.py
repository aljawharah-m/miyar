from __future__ import annotations
import collections, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from core.engine import analyze
from core.recognition import recognize_quran, _clean_ar
from core.sources import source_route
from core.terminology import TERMS

errors=[]

# 1) Full local Quran locator integrity and exact-reference behavior.
qpath=ROOT/'data'/'quran_locator.json'
rows=json.loads(qpath.read_text(encoding='utf-8'))
if len(rows)!=6236:
    errors.append(f'Quran locator row count={len(rows)} (expected 6236)')
norm_rows=[(r,_clean_ar(r.get('text',''))) for r in rows]
unique_ok=ambiguous_ok=short_abstain=0
for r,q in norm_rows:
    out=recognize_quran(r.get('text',''),live=False)
    containing=[rr for rr,v in norm_rows if q and q in v]
    if len(containing)>1:
        if out and out.get('ambiguous'):
            ambiguous_ok+=1
        elif not out and len(q)<12:
            short_abstain+=1
        else:
            errors.append(f"Ambiguous Quran text guessed incorrectly at {r['surah']}:{r['ayah']}")
            if len(errors)>20: break
    else:
        if out and not out.get('ambiguous') and (out.get('surah'),out.get('ayah'))==(r['surah'],r['ayah']):
            unique_ok+=1
        elif not out and len(q)<12:
            short_abstain+=1
        else:
            errors.append(f"Unique Quran locator failed at {r['surah']}:{r['ayah']}")
            if len(errors)>20: break

# Known fragment that previously failed in V3.
z=analyze('وَإِنْ كُنْتُمْ جُنُبًا فَاطَّهَّرُوا','Purify yourselves.',use_live_sources=False,use_semantic_ai=False)
if not (z.get('recognition') and z['recognition']['kind']=='quran' and z['recognition']['match'].get('surah')==5 and z['recognition']['match'].get('ayah')==6):
    errors.append('Quran fragment 5:6 not recognized')
if not any(i.get('type')=='condition' for i in z.get('issues',[])) or z.get('status')!='critical':
    errors.append('Missing Quran condition was not blocked')

z=analyze('وَإِنْ كُنْتُمْ جُنُبًا فَاطَّهَّرُوا','If you are in a state of major ritual impurity, then purify yourselves.',use_live_sources=False,use_semantic_ai=False)
if z.get('status')!='safe' or z.get('issues'):
    errors.append('Correct Quran condition produced a false alert')

# 2) Terminology guard: accepted -> safe, risky -> critical, context-dependent -> review.
term_checks=0
for t in TERMS:
    ar=t['ar']
    for en in t.get('accepted',[])[:2]:
        term_checks+=1
        z=analyze(ar,en,use_live_sources=False,use_semantic_ai=False)
        if z['status']!='safe': errors.append(f"Accepted term failed: {ar} -> {en} ({z['status']})")
    for en in t.get('risky',[])[:1]:
        term_checks+=1
        z=analyze(ar,en,use_live_sources=False,use_semantic_ai=False)
        if z['status']!='critical': errors.append(f"Risky term not blocked: {ar} -> {en} ({z['status']})")
    for en in t.get('review',[])[:1]:
        term_checks+=1
        z=analyze(ar,en,use_live_sources=False,use_semantic_ai=False)
        if z['status']!='review': errors.append(f"Context term not routed to review: {ar} -> {en} ({z['status']})")


# 2b) Every terminology rule must carry an explicit external grounding manifest.
prov_path=ROOT/'data'/'terminology_provenance.json'
try:
    prov_rows=json.loads(prov_path.read_text(encoding='utf-8'))
except Exception as exc:
    prov_rows=[]
    errors.append(f'Terminology provenance manifest unreadable: {exc}')
prov_index={r.get('term'):r for r in prov_rows if r.get('term')}
for t in TERMS:
    row=prov_index.get(t['ar'])
    if not row:
        errors.append(f'Missing terminology provenance row: {t["ar"]}')
        continue
    refs=row.get('source_refs') or []
    if not refs or not any(r.get('name') for r in refs):
        errors.append(f'No external source basis for terminology rule: {t["ar"]}')
    if not any(r.get('verification_locator') for r in refs):
        errors.append(f'No verifiable source locator for terminology rule: {t["ar"]}')
    if row.get('traceability_status') != 'direct_rule_to_source_locator':
        errors.append(f'Terminology rule is not marked directly traceable: {t["ar"]}')
    if not row.get('policy_note'):
        errors.append(f'Missing policy/source distinction note: {t["ar"]}')
terminology_provenance_rows=len(prov_index)


# 2c) General linguistic-method references required by mentor guidance.
ling_path=ROOT/'data'/'linguistic_method_references.json'
try:
    ling_rows=json.loads(ling_path.read_text(encoding='utf-8'))
except Exception as exc:
    ling_rows=[]
    errors.append(f'Linguistic method references unreadable: {exc}')
required_ling={'النفي','الشرط','الاستثناء'}
supported=set()
for row in ling_rows if isinstance(ling_rows,list) else []:
    supported.update(row.get('supports') or [])
if not required_ling.issubset(supported):
    errors.append(f'Linguistic method references do not cover required core phenomena: {sorted(required_ling-supported)}')
linguistic_reference_rows=len(ling_rows)

# 3) Source router coverage. Reference-only providers are intentionally not claimed as evidence-used.
route_expectations={
    'قال الله في القرآن الكريم':['QuranEnc','Central DB / ICADB'],
    'قال رسول الله في الحديث':['HadeethEnc','Central DB / ICADB'],
    'التوحيد من مسائل العقيدة':['TerminologyEnc','الدرر السنية — العقيدة'],
    'حكم الزكاة والوضوء في الفقه':['الدرر السنية — الموسوعة الفقهية','الموسوعة الفقهية الكويتية','TerminologyEnc'],
    'مادة دعوية عامة':['Byenah','IslamHouse','IslamEnc'],
}
for text,expected in route_expectations.items():
    names=[s['name'] for s in source_route(text)['sources']]
    for name in expected:
        if name not in names:
            errors.append(f'Source router missing {name} for: {text}')

# 4) Public review UI must not pretend a real specialist workflow exists.
app=(ROOT/'app.py').read_text(encoding='utf-8')
for forbidden in ['اعتماد التنبيه','رفض التنبيه','إحالة لمختص']:
    if forbidden in app:
        errors.append(f'Public UI still contains fake human-review action: {forbidden}')
if 'تحتاج مراجعة بشرية قبل النشر' not in app:
    errors.append('Public UI missing explicit human-review state')

report={
    'quran_locator_rows':len(rows),
    'quran_unique_exact_ok':unique_ok,
    'quran_repeated_ambiguous_ok':ambiguous_ok,
    'quran_short_safe_abstentions':short_abstain,
    'terminology_checks':term_checks,
    'terminology_provenance_rows':terminology_provenance_rows,
    'linguistic_reference_rows':linguistic_reference_rows,
    'errors':errors,
    'note':'Deterministic development/source audit. Live provider connectivity is checked separately by scripts/preflight.py.'
}
(ROOT/'evaluation'/'source_audit_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
if errors:
    raise SystemExit(1)
